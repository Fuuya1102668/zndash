import calendar
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import feedparser
import httpx
import trafilatura

from .config import (
    NEWS_FETCH_CONCURRENCY,
    NEWS_FEEDS,
    RAINFALL_APP_ID,
    RAINFALL_COORDINATES,
    RAINFALL_URL,
    WEATHER_FORECAST_URL,
)


class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            self.parts.append(data)


def _plain_text(content):
    parser = _HTMLTextExtractor()
    parser.feed(content or "")
    return " ".join(" ".join(parser.parts).split())


def _parse_forecast(forecast):
    if not forecast:
        return None

    temperature = forecast.get("temperature") or {}
    chance_of_rain = forecast.get("chanceOfRain") or {}
    rain_values = []
    for period in ("T00_06", "T06_12", "T12_18", "T18_24"):
        value = chance_of_rain.get(period)
        if value and value != "--":
            try:
                rain_values.append(int(value.replace("%", "")))
            except ValueError:
                continue

    def temperature_value(bound):
        value = (temperature.get(bound) or {}).get("celsius")
        return value if value not in (None, "", "--") else "未発表"

    return {
        "telop": forecast.get("telop", "--"),
        "max": temperature_value("max"),
        "min": temperature_value("min"),
        "rain": sum(rain_values) // len(rain_values) if rain_values else 0,
    }


def format_temperature(value):
    return f"{value}℃" if value not in (None, "", "--", "未発表") else "未発表"


async def fetch_weather_forecast():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(WEATHER_FORECAST_URL)
            response.raise_for_status()
            data = response.json()
        forecasts = data.get("forecasts", [])
        if len(forecasts) < 2:
            return None
        return {
            "description": data.get("description", {}).get("bodyText", ""),
            "today": _parse_forecast(forecasts[0]),
            "tomorrow": _parse_forecast(forecasts[1]),
        }
    except (httpx.HTTPError, ValueError, KeyError) as error:
        print(f"天気予報の取得に失敗しました: {error}")
        return None


async def fetch_rainfall_data():
    if not RAINFALL_APP_ID:
        print("降水量を取得するには YAHOO_WEATHER_APP_ID を設定してください")
        return [], []

    params = {
        "coordinates": RAINFALL_COORDINATES,
        "appid": RAINFALL_APP_ID,
        "interval": 5,
        "past": 0,
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(RAINFALL_URL, params=params)
            response.raise_for_status()

        namespace = {"ns": "http://olp.yahooapis.jp/ydf/1.0"}
        root = ET.fromstring(response.text)
        labels, values = [], []
        for weather in root.findall(".//ns:Weather", namespace):
            date_node = weather.find("ns:Date", namespace)
            rain_node = weather.find("ns:Rainfall", namespace)
            if date_node is None or rain_node is None or not date_node.text or not rain_node.text:
                continue
            labels.append(f"{date_node.text[-4:-2]}:{date_node.text[-2:]}")
            values.append(float(rain_node.text))
        return labels, values
    except (httpx.HTTPError, ET.ParseError, ValueError) as error:
        print(f"降水量の取得に失敗しました: {error}")
        return [], []


def _parse_feed(feed_content):
    feed = feedparser.parse(feed_content)
    articles = []
    for entry in feed.entries[:3]:
        content = getattr(entry, "summary", "") or getattr(entry, "description", "")
        if not content and getattr(entry, "content", None):
            content = entry.content[0].get("value", "")
        articles.append({
            "title": getattr(entry, "title", "タイトルなし"),
            "link": getattr(entry, "link", ""),
            "description": _plain_text(content),
        })
    return articles


async def fetch_news(source_key):
    url = NEWS_FEEDS.get(source_key)
    if not url:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
        return _parse_feed(response.text)
    except (httpx.HTTPError, ValueError) as error:
        print(f"{source_key} のニュース取得に失敗しました: {error}")
        return []


def _parse_recent_feed(feed_content, cutoff, now):
    feed = feedparser.parse(feed_content)
    articles = []
    for entry in feed.entries:
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if not published:
            continue
        published_at = datetime.fromtimestamp(calendar.timegm(published), timezone.utc)
        if published_at < cutoff or published_at > now + timedelta(minutes=5):
            continue

        content = entry.get("summary", "") or entry.get("description", "")
        if not content and entry.get("content"):
            content = entry.content[0].get("value", "")
        articles.append({
            "title": _plain_text(entry.get("title") or "タイトルなし"),
            "link": entry.get("link") or "",
            "description": _plain_text(content),
            "published_at": published_at,
        })
    return articles


async def fetch_recent_news(source_key, hours=24):
    """Fetch timestamped entries still present in a feed within the time window."""
    url = NEWS_FEEDS.get(source_key)
    if not url:
        return []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            response.raise_for_status()
        return _parse_recent_feed(response.text, cutoff, now)
    except (httpx.HTTPError, ValueError) as error:
        print(f"{source_key} の直近ニュース取得に失敗しました: {error}")
        return []


async def fetch_article_text(client, article):
    """Fetch full article text, falling back to the RSS excerpt when unavailable."""
    fallback = (article.get("description") or "").strip()
    url = article.get("link", "")
    if not url:
        return fallback, "rss_fallback"

    try:
        allowed_domains = article.get("allowed_domains", ())
        for _ in range(5):
            parts = urlsplit(url)
            hostname = (parts.hostname or "").lower()
            if parts.scheme != "https" or not any(
                hostname == domain or hostname.endswith(f".{domain}")
                for domain in allowed_domains
            ):
                return fallback, "rss_fallback"
            response = await client.get(url, follow_redirects=False)
            if response.is_redirect:
                redirect = response.headers.get("location")
                if not redirect:
                    return fallback, "rss_fallback"
                url = urljoin(url, redirect)
                continue
            response.raise_for_status()
            break
        else:
            return fallback, "rss_fallback"
        if len(response.content) > 8_000_000:
            return fallback, "rss_fallback"
        response.raise_for_status()
        extracted = await asyncio.to_thread(
            trafilatura.extract,
            response.text,
            output_format="txt",
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        text = "\n\n".join(line.strip() for line in (extracted or "").splitlines() if line.strip())
        if len(text) >= 350:
            return text, "full"
        if len(fallback) > len(text):
            return fallback, "rss_fallback"
        if text:
            return text, "full"
        return fallback, "rss_fallback"
    except (httpx.HTTPError, ValueError) as error:
        print(f"記事本文を取得できませんでした: {error}")
        return fallback, "rss_fallback"
    except Exception as error:
        print(f"記事本文の抽出に失敗しました: {type(error).__name__}")
        return fallback, "rss_fallback"


async def fetch_article_bodies(articles):
    semaphore = asyncio.Semaphore(NEWS_FETCH_CONCURRENCY)
    timeout = httpx.Timeout(20, connect=8)
    headers = {"User-Agent": "zndash-news-board/1.0"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        async def fetch(article):
            async with semaphore:
                text, status = await fetch_article_text(client, article)
                return {**article, "body": text, "body_status": status}

        return await asyncio.gather(*(fetch(article) for article in articles))
