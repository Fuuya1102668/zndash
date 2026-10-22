import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


DATA_DIR = Path(__file__).resolve().parent / "data"

WEATHER_FORECAST_URL = "https://weather.tsukumijima.net/api/forecast/city/170010"
RAINFALL_URL = "https://map.yahooapis.jp/weather/V1/place"
RAINFALL_COORDINATES = "136.571755,36.484950"
RAINFALL_APP_ID = os.environ.get("YAHOO_WEATHER_APP_ID", "")

NEWS_FEEDS = {
    "ITmedia": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "Zenn": "https://zenn.dev/topics/llm/feed",
    "note": "https://note.com/hashtag/huggingface/rss",
}

WEATHER_REFRESH_SECONDS = 3600
RAINFALL_REFRESH_SECONDS = 300
NEWS_WINDOW_HOURS = 24
NEWS_REFRESH_SECONDS = 3600
NEWS_DATABASE_PATH = DATA_DIR / "news.sqlite3"
NEWS_FETCH_CONCURRENCY = 6
CODEX_CONCURRENCY = 2
CODEX_TIMEOUT_SECONDS = 240
CODEX_MODEL = os.environ.get("ZNDASH_CODEX_MODEL", "")
CODEX_CLI = os.environ.get("ZNDASH_CODEX_CLI", "codex")
NEWS_RETENTION_DAYS = int(os.environ.get("ZNDASH_NEWS_RETENTION_DAYS", "30"))
NEWS_CLUSTER_SIMILARITY_THRESHOLD = float(
    os.environ.get("ZNDASH_CLUSTER_SIMILARITY_THRESHOLD", "0.18")
)
ARTICLE_SUMMARY_PROMPT_VERSION = "1"
TOPIC_SUMMARY_PROMPT_VERSION = "5"
NEWS_ARTICLE_DOMAINS = {
    "ITmedia": ("itmedia.co.jp",),
    "Zenn": ("zenn.dev",),
    "note": ("note.com",),
}
KEYWORD_ALIAS_PATH = Path(__file__).resolve().parent / "keyword_aliases.json"
