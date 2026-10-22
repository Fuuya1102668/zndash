"""Deterministic clustering from concise, normalized Codex keywords."""

import json
import unicodedata
from collections import Counter
from pathlib import Path

from .config import KEYWORD_ALIAS_PATH, NEWS_CLUSTER_SIMILARITY_THRESHOLD


def _load_aliases():
    try:
        return json.loads(KEYWORD_ALIAS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


KEYWORD_ALIASES = _load_aliases()


def normalize_keyword(value):
    keyword = " ".join(unicodedata.normalize("NFKC", str(value)).split()).strip(" ,、。")
    if not keyword:
        return ""
    return KEYWORD_ALIASES.get(keyword.casefold(), keyword)


def _article_keywords(article):
    return {normalize_keyword(keyword) for keyword in article.get("keywords", []) if normalize_keyword(keyword)}


def _similarity(left, right):
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def cluster_articles(articles, threshold=NEWS_CLUSTER_SIMILARITY_THRESHOLD):
    """Cluster by shared normalized keywords within a Codex-assigned category."""
    groups = []
    ordered = sorted(articles, key=lambda article: article["published_at"], reverse=True)
    for article in ordered:
        keywords = _article_keywords(article)
        article["keywords"] = sorted(keywords)
        candidates = []
        for index, group in enumerate(groups):
            if group["category"] != article.get("category") or not keywords:
                continue
            core = Counter(keyword for member in group["articles"] for keyword in member["keywords"])
            centroid = {keyword for keyword, _ in core.most_common(3)}
            if not keywords & centroid:
                continue
            similarity = _similarity(keywords, centroid)
            if similarity >= threshold:
                candidates.append((similarity, index))
        if candidates:
            _, group_index = max(candidates)
            groups[group_index]["articles"].append(article)
        else:
            groups.append({
                "category": article.get("category", "その他"),
                "articles": [article],
            })

    for group in groups:
        frequency = Counter(keyword for article in group["articles"] for keyword in article["keywords"])
        group["keywords"] = [keyword for keyword, _ in frequency.most_common(5)]
        group["count"] = len(group["articles"])
        group["published_at"] = group["articles"][0]["published_at"]
    groups.sort(key=lambda group: (group["count"], group["published_at"]), reverse=True)
    return groups
