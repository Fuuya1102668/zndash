"""Hourly collection, Codex summarization, clustering, and publication."""

import asyncio
import hashlib
import json
import logging
import re
import uuid
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .codex_client import (
    ARTICLE_TEXT_LIMIT,
    summarize_article,
    summarize_article_batch,
    summarize_topic,
)
from .config import (
    ARTICLE_SUMMARY_PROMPT_VERSION,
    CODEX_CONCURRENCY,
    CODEX_MODEL,
    NEWS_ARTICLE_DOMAINS,
    NEWS_FEEDS,
    NEWS_REFRESH_SECONDS,
    NEWS_WINDOW_HOURS,
    TOPIC_SUMMARY_PROMPT_VERSION,
)
from .news_digest import cluster_articles
from .news_storage import (
    begin_run,
    fail_run,
    get_cached_summary,
    get_cached_topic_summary,
    initialize_storage,
    prune_old_data,
    publish_run,
    save_article,
    save_article_summary,
    save_topic_summary,
    update_run_progress,
)
from .services import fetch_article_bodies, fetch_recent_news


LOGGER = logging.getLogger(__name__)
MODEL_CACHE_KEY = CODEX_MODEL or "codex-config-default"


def _canonical_url(url):
    try:
        parts = urlsplit(url.strip())
        if parts.scheme.lower() != "https" or not parts.hostname or parts.username or parts.password:
            return ""
        hostname = parts.hostname.lower()
        netloc = hostname
        if parts.port and parts.port != 443:
            netloc = f"{hostname}:{parts.port}"
        query = urlencode([
            (key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"}
        ])
        return urlunsplit(("https", netloc, parts.path.rstrip("/"), query, ""))
    except ValueError:
        return ""


def _article_id(article):
    canonical_url = _canonical_url(article.get("link", ""))
    if canonical_url:
        identity = canonical_url
    else:
        title = re.sub(r"\s+", " ", article.get("title", "")).strip().casefold()
        identity = f"{title}|{article['published_at'].date().isoformat()}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _deduplicate_articles(items):
    unique = {}
    for source_key, item in items:
        article = {
            **item,
            "id": _article_id(item),
            "source_key": source_key,
            "allowed_domains": NEWS_ARTICLE_DOMAINS.get(source_key, ()),
        }
        existing = unique.get(article["id"])
        if existing is None or len(article.get("description", "")) > len(existing.get("description", "")):
            unique[article["id"]] = article
    return sorted(unique.values(), key=lambda article: article["published_at"], reverse=True)


def _pack_articles(articles):
    batches, current, size = [], [], 0
    for article in articles:
        item_size = len(article["body"]) + len(article["title"])
        if item_size > ARTICLE_TEXT_LIMIT:
            if current:
                batches.append(current)
                current, size = [], 0
            batches.append([article])
            continue
        if current and (size + item_size > ARTICLE_TEXT_LIMIT or len(current) >= 4):
            batches.append(current)
            current, size = [], 0
        current.append(article)
        size += item_size
    if current:
        batches.append(current)
    return batches


async def refresh_news_once():
    run_id = str(uuid.uuid4())
    run_started = False
    failed_article_ids = set()
    try:
        initialize_storage()
        prune_old_data()
        begin_run(run_id)
        run_started = True
        source_keys = list(NEWS_FEEDS)
        feeds = await asyncio.gather(*(fetch_recent_news(key, hours=NEWS_WINDOW_HOURS) for key in source_keys))
        raw_articles = [(key, article) for key, feed in zip(source_keys, feeds) for article in feed]
        candidates = _deduplicate_articles(raw_articles)
        update_run_progress(len(candidates), 0, "記事本文を取得しています")

        fetched_articles = await fetch_article_bodies(candidates)
        model_id = MODEL_CACHE_KEY
        to_summarize = []
        summarized_articles = []
        for article in fetched_articles:
            body = article.pop("body", "").strip()
            article["body_hash"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
            article["body"] = body
            save_article(article)
            cached = get_cached_summary(
                article["id"], article["body_hash"], model_id, ARTICLE_SUMMARY_PROMPT_VERSION
            )
            if cached:
                summarized_articles.append({**article, **cached})
            elif len(body) < 40:
                failed_article_ids.add(article["id"])
            else:
                to_summarize.append(article)

        update_run_progress(len(candidates), len(failed_article_ids), "記事ごとに要約とキーワードを作成しています")
        semaphore = asyncio.Semaphore(CODEX_CONCURRENCY)

        async def summarize_batch(batch):
            async with semaphore:
                if len(batch) == 1 and len(batch[0]["body"]) > ARTICLE_TEXT_LIMIT:
                    return {batch[0]["id"]: await summarize_article(batch[0])}
                return await summarize_article_batch(batch)

        batches = _pack_articles(to_summarize)
        batch_results = await asyncio.gather(
            *(summarize_batch(batch) for batch in batches),
            return_exceptions=True,
        )
        for batch, result in zip(batches, batch_results):
            if isinstance(result, Exception):
                LOGGER.warning("記事要約バッチに失敗しました: %s", result)
                recovered = {}
                for article in batch:
                    try:
                        recovered[article["id"]] = await summarize_article(article)
                    except Exception:
                        failed_article_ids.add(article["id"])
                result = recovered
                if not result:
                    continue
            for article in batch:
                summary = result.get(article["id"])
                if not summary:
                    failed_article_ids.add(article["id"])
                    continue
                save_article_summary(
                    article["id"], article["body_hash"], model_id,
                    ARTICLE_SUMMARY_PROMPT_VERSION, summary,
                )
                summarized_articles.append({**article, **summary})

        groups = cluster_articles(summarized_articles)
        update_run_progress(len(candidates), len(failed_article_ids), "関連ニュースをまとめています")

        async def summarize_group(group):
            async with semaphore:
                signature_payload = {
                    "members": sorted(
                        (article["id"], article["body_hash"]) for article in group["articles"]
                    ),
                    "category": group["category"],
                    "keywords": group["keywords"],
                }
                signature = hashlib.sha256(
                    json.dumps(signature_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ).hexdigest()
                cached = get_cached_topic_summary(
                    signature, model_id, TOPIC_SUMMARY_PROMPT_VERSION
                )
                if cached:
                    return {**group, **cached}
                try:
                    digest = await summarize_topic(group["articles"])
                    save_topic_summary(signature, model_id, TOPIC_SUMMARY_PROMPT_VERSION, digest)
                    return {**group, **digest}
                except Exception as error:
                    LOGGER.warning("話題要約に失敗しました: %s", error)
                    failed_article_ids.update(article["id"] for article in group["articles"])
                    return {
                        **group,
                        "title": f"{group['category']}の話題（要約未完了）",
                        "summary": "話題全体の要約を作成できませんでした。記事ごとの要約を表示しています。",
                    }

        digests = await asyncio.gather(*(summarize_group(group) for group in groups))
        publish_run(run_id, digests, len(candidates), len(failed_article_ids))
        return {"run_id": run_id, "articles": len(candidates), "failed": len(failed_article_ids)}
    except asyncio.CancelledError:
        fail_run(run_id, "実行中にアプリが停止しました")
        raise
    except Exception as error:
        LOGGER.exception("ニュース更新に失敗しました")
        if run_started:
            fail_run(run_id, f"更新に失敗しました: {type(error).__name__}: {error}")
        return {"run_id": run_id, "error": str(error)}


async def run_hourly_news_pipeline():
    loop = asyncio.get_running_loop()
    next_run = loop.time()
    while True:
        await refresh_news_once()
        next_run += NEWS_REFRESH_SECONDS
        now = loop.time()
        while next_run <= now:
            next_run += NEWS_REFRESH_SECONDS
        await asyncio.sleep(next_run - now)
