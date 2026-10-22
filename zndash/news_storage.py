"""SQLite persistence for cached summaries and complete bulletin runs."""

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from .config import NEWS_DATABASE_PATH, NEWS_RETENTION_DAYS


def _now():
    return datetime.now(timezone.utc).isoformat()


def _connect():
    NEWS_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(NEWS_DATABASE_PATH, timeout=20)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_storage():
    with _connect() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                fetch_url TEXT NOT NULL,
                title TEXT NOT NULL,
                published_at TEXT NOT NULL,
                body_hash TEXT NOT NULL,
                body_status TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS article_summaries (
                article_id TEXT NOT NULL,
                body_hash TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_version TEXT NOT NULL,
                summary TEXT NOT NULL,
                category TEXT NOT NULL,
                keywords_json TEXT NOT NULL,
                confidence TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (article_id, body_hash, model, prompt_version)
            );
            CREATE TABLE IF NOT EXISTS topic_summaries (
                signature TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_version TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (signature, model, prompt_version)
            );
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                article_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                message TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS topics (
                run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                article_count INTEGER NOT NULL,
                keywords_json TEXT NOT NULL,
                articles_json TEXT NOT NULL,
                PRIMARY KEY (run_id, position)
            );
            CREATE TABLE IF NOT EXISTS pipeline_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                status TEXT NOT NULL,
                last_started_at TEXT,
                last_finished_at TEXT,
                article_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                message TEXT NOT NULL DEFAULT ''
            );
            INSERT OR IGNORE INTO pipeline_state(singleton, status) VALUES (1, '待機中');
        """)
    try:
        os.chmod(NEWS_DATABASE_PATH, 0o600)
    except OSError:
        pass


def prune_old_data():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEWS_RETENTION_DAYS)).isoformat()
    with _connect() as connection:
        connection.execute("DELETE FROM runs WHERE started_at < ?", (cutoff,))
        connection.execute("DELETE FROM articles WHERE fetched_at < ?", (cutoff,))
        connection.execute("DELETE FROM article_summaries WHERE updated_at < ?", (cutoff,))
        connection.execute("DELETE FROM topic_summaries WHERE updated_at < ?", (cutoff,))


def begin_run(run_id):
    started_at = _now()
    with _connect() as connection:
        connection.execute(
            "INSERT INTO runs(id, status, started_at) VALUES (?, 'running', ?)",
            (run_id, started_at),
        )
        connection.execute(
            "UPDATE pipeline_state SET status='処理中', last_started_at=?, message='ニュースを取得しています' WHERE singleton=1",
            (started_at,),
        )
    return started_at


def update_run_progress(article_count, failed_count, message):
    with _connect() as connection:
        connection.execute(
            "UPDATE pipeline_state SET article_count=?, failed_count=?, message=? WHERE singleton=1",
            (article_count, failed_count, message[:240]),
        )


def save_article(article):
    with _connect() as connection:
        connection.execute("""
            INSERT INTO articles(id, fetch_url, title, published_at, body_hash, body_status, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                fetch_url=excluded.fetch_url,
                title=excluded.title,
                published_at=excluded.published_at,
                body_hash=excluded.body_hash,
                body_status=excluded.body_status,
                fetched_at=excluded.fetched_at
        """, (
            article["id"], article.get("link", ""), article["title"],
            article["published_at"].isoformat(), article["body_hash"],
            article["body_status"], _now(),
        ))


def get_cached_summary(article_id, body_hash, model, prompt_version):
    with _connect() as connection:
        row = connection.execute("""
            SELECT summary, category, keywords_json, confidence
            FROM article_summaries
            WHERE article_id=? AND body_hash=? AND model=? AND prompt_version=?
        """, (article_id, body_hash, model, prompt_version)).fetchone()
    if not row:
        return None
    return {
        "summary": row["summary"],
        "category": row["category"],
        "keywords": json.loads(row["keywords_json"]),
        "confidence": row["confidence"],
    }


def save_article_summary(article_id, body_hash, model, prompt_version, result):
    with _connect() as connection:
        connection.execute("""
            INSERT OR REPLACE INTO article_summaries(
                article_id, body_hash, model, prompt_version, summary, category,
                keywords_json, confidence, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_id, body_hash, model, prompt_version, result["summary"],
            result["category"], json.dumps(result["keywords"], ensure_ascii=False),
            result["confidence"], _now(),
        ))


def get_cached_topic_summary(signature, model, prompt_version):
    with _connect() as connection:
        row = connection.execute("""
            SELECT title, summary FROM topic_summaries
            WHERE signature=? AND model=? AND prompt_version=?
        """, (signature, model, prompt_version)).fetchone()
    return dict(row) if row else None


def save_topic_summary(signature, model, prompt_version, result):
    with _connect() as connection:
        connection.execute("""
            INSERT OR REPLACE INTO topic_summaries(signature, model, prompt_version, title, summary, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (signature, model, prompt_version, result["title"], result["summary"], _now()))


def publish_run(run_id, groups, article_count, failed_count):
    finished_at = _now()
    status = "partial" if failed_count else "complete"
    message = f"{article_count - failed_count}/{article_count}件を処理"
    with _connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        for position, group in enumerate(groups):
            display_articles = [{
                "title": article["title"],
                "published_at": article["published_at"].isoformat(),
                "summary": article.get("summary", ""),
            } for article in group["articles"]]
            connection.execute("""
                INSERT INTO topics(run_id, position, title, summary, article_count, keywords_json, articles_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, position, group["title"], group["summary"], len(display_articles),
                json.dumps(group.get("keywords", []), ensure_ascii=False),
                json.dumps(display_articles, ensure_ascii=False),
            ))
        connection.execute(
            "UPDATE runs SET status=?, finished_at=?, article_count=?, failed_count=?, message=? WHERE id=?",
            (status, finished_at, article_count, failed_count, message, run_id),
        )
        connection.execute("""
            UPDATE pipeline_state SET status=?, last_finished_at=?, article_count=?, failed_count=?, message=?
            WHERE singleton=1
        """, ("一部の記事を処理できませんでした" if failed_count else "更新済み", finished_at,
              article_count, failed_count, message))


def fail_run(run_id, message):
    finished_at = _now()
    with _connect() as connection:
        connection.execute(
            "UPDATE runs SET status='failed', finished_at=?, message=? WHERE id=?",
            (finished_at, message[:240], run_id),
        )
        connection.execute(
            "UPDATE pipeline_state SET status='更新に失敗', last_finished_at=?, message=? WHERE singleton=1",
            (finished_at, message[:240]),
        )


def get_pipeline_state():
    initialize_storage()
    with _connect() as connection:
        row = connection.execute("SELECT * FROM pipeline_state WHERE singleton=1").fetchone()
    return dict(row) if row else {"status": "待機中", "message": ""}


def get_latest_topics():
    initialize_storage()
    with _connect() as connection:
        latest = connection.execute(
            "SELECT id FROM runs WHERE status IN ('complete', 'partial') ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if not latest:
            return []
        rows = connection.execute(
            "SELECT * FROM topics WHERE run_id=? ORDER BY position",
            (latest["id"],),
        ).fetchall()
    return [{
        "title": row["title"],
        "summary": row["summary"],
        "count": row["article_count"],
        "keywords": json.loads(row["keywords_json"]),
        "articles": json.loads(row["articles_json"]),
    } for row in rows]
