# fetcher.py
"""
Unified news fetch pipeline:
1) Google News RSS (PRIMARY)
2) NewsAPI (secondary)
3) RSS feeds (fallback)
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Optional

import requests
import feedparser

# Google News RSS module
from google_news_fetcher_rss import fetch_google_news_articles_rss

# -------------------------------
# RSS FEEDS
# -------------------------------
DEFAULT_RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://feeds.reuters.com/reuters/topNews",
    "https://www.theguardian.com/world/rss",
]

DATA_RAW_DIR = os.path.join("data", "raw")
os.makedirs(DATA_RAW_DIR, exist_ok=True)


# -------------------------------
# SAVE RAW ARTICLE
# -------------------------------
def _save_raw_article(article: Dict) -> str:
    key = (article.get("url", "") + (article.get("title") or "")).encode("utf-8")
    fname = hashlib.sha256(key).hexdigest()[:16] + ".json"
    path = os.path.join(DATA_RAW_DIR, fname)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)

    return path


# -------------------------------
# NEWSAPI FETCH
# -------------------------------
def fetch_from_newsapi(query: str, api_key: Optional[str], max_results: int):
    if not api_key:
        return []

    endpoint = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": max_results,
        "language": "en",
        "sortBy": "publishedAt",
    }
    headers = {"Authorization": api_key}

    resp = requests.get(endpoint, params=params, headers=headers, timeout=15)
    data = resp.json()
    items = data.get("articles", [])

    out = []
    for it in items:
        a = {
            "source": it.get("source", {}).get("name"),
            "title": it.get("title"),
            "url": it.get("url"),
            "published_at": it.get("publishedAt"),
            "summary": it.get("description"),
            "content": it.get("content"),
            "fetched_with": "newsapi",
        }
        a["saved_path"] = _save_raw_article(a)
        out.append(a)
    return out


# -------------------------------
# RSS FETCH (Fallback)
# -------------------------------
def _normalize_rss_entry(entry):
    published = entry.get("published") or entry.get("updated")
    return {
        "source": entry.get("source", {}).get("title"),
        "title": entry.get("title"),
        "url": entry.get("link"),
        "published_at": published,
        "summary": entry.get("summary"),
        "content": entry.get("summary"),
        "fetched_with": "rss",
    }


def fetch_from_rss(rss_urls: List[str], query: str, max_results_per_feed: int):
    out = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
        except:
            continue

        entries = feed.entries[:max_results_per_feed]
        for e in entries:
            a = _normalize_rss_entry(e)

            text = ((a.get("title") or "") + " " + (a.get("summary") or "")).lower()
            if query.lower() not in text:
                continue

            a["feed_url"] = url
            a["saved_path"] = _save_raw_article(a)
            out.append(a)

        time.sleep(0.1)

    return out


# -------------------------------
# MAIN FETCH PIPELINE
# -------------------------------
def fetch_articles(query: str, max_results=10, newsapi_key=None, rss_feeds=None):
    print("=== FETCHING ARTICLES ===")
    print("Query:", query)

    if rss_feeds is None:
        rss_feeds = DEFAULT_RSS_FEEDS

    results = []

    # -------------------------------
    # 1) Google News RSS PRIMARY
    # -------------------------------
    print("Trying Google News (RSS)...")
    try:
        gn = fetch_google_news_articles_rss(query, max_results=max_results)
        print("Google News RSS returned:", len(gn))

        for g in gn:
            g["saved_path"] = _save_raw_article(g)

        results.extend(gn)
    except Exception as e:
        print("Google News RSS failed:", e)

    if len(results) >= max_results:
        return results[:max_results]

    # -------------------------------
    # 2) NEWSAPI SECONDARY
    # -------------------------------
    print("Trying NewsAPI...")
    try:
        na = fetch_from_newsapi(query, newsapi_key, max_results)
        print("NewsAPI returned:", len(na))

        results.extend(na)
    except Exception as e:
        print("NewsAPI failed:", e)

    if len(results) >= max_results:
        return results[:max_results]

    # -------------------------------
    # 3) RSS FALLBACK
    # -------------------------------
    print("Trying RSS feeds...")
    remaining = max_results - len(results)
    per_feed = max(1, remaining // len(rss_feeds))

    rss_items = fetch_from_rss(rss_feeds, query, per_feed)
    print("RSS returned:", len(rss_items))

    results.extend(rss_items[:remaining])

    print("=== TOTAL FETCHED:", len(results))
    return results[:max_results]
