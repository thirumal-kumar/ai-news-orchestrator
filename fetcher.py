# fetcher.py
import os
import requests
from typing import List, Dict
from urllib.parse import quote
from datetime import datetime
from google_news_fetcher_rss import fetch_google_news_articles_rss

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def _fetch_from_newsapi(query: str, max_results: int = 8) -> List[Dict]:
    if not NEWSAPI_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "pageSize": max_results,
        "sortBy": "publishedAt",
        "apiKey": NEWSAPI_KEY
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    items = []
    for a in data.get("articles", []):
        items.append({
            "title": a.get("title"),
            "url": a.get("url"),
            "published_at": a.get("publishedAt") or a.get("publishedAt"),
            "source": (a.get("source") or {}).get("name", "")
        })
    return items

def fetch_articles(query: str, max_results: int = 8) -> List[Dict]:
    """
    Returns list of normalized article dicts:
    { title, url, published_at, source }
    """
    # Try NewsAPI
    try:
        items = _fetch_from_newsapi(query, max_results)
        if items:
            return items[:max_results]
    except Exception:
        # ignore and fallback
        pass
    # Fallback to Google News RSS
    try:
        items = fetch_google_news_articles_rss(query, max_results)
        return items[:max_results]
    except Exception as e:
        # final fallback: empty
        return []
