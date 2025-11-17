# fetcher.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
import feedparser

def _normalize_article(a):
    return {
        "title": a.get("title") or a.get("headline") or "",
        "url": a.get("url") or a.get("link") or "",
        "source": a.get("source") or (a.get("source_name") if isinstance(a.get("source_name"), str) else ""),
        "published_at": a.get("published_at") or a.get("published") or "",
    }

def fetch_google_rss(query, max_results=20):
    q = quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        articles = []
        for e in feed.entries:
            articles.append({
                "title": e.get("title", ""),
                "url": e.get("link", ""),
                "source": e.get("source", {}).get("title", "") if e.get("source") else "",
                "published_at": e.get("published", "") or e.get("published_parsed", "")
            })
            if len(articles) >= max_results:
                break
        return articles
    except Exception:
        return []

def fetch_newsapi(query, news_api_key, max_results=20):
    if not news_api_key:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": min(max_results, 100),
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": news_api_key
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", ""),
                "published_at": a.get("publishedAt", "")
            })
        return articles
    except Exception:
        return []

def fetch_articles(query, news_api_key=None, max_results=20):
    """
    Returns list of normalized article dicts (see data model).
    Tries NewsAPI first (if key provided), then Google RSS as fallback.
    """
    max_results = int(max_results)  # guard
    results = []

    if news_api_key:
        results = fetch_newsapi(query, news_api_key, max_results)
    if len(results) < max_results:
        rss = fetch_google_rss(query, max_results=max_results)
        # combine, avoid duplicates by url
        seen = set(a["url"] for a in results if a.get("url"))
        for a in rss:
            if a.get("url") and a["url"] not in seen:
                results.append(a)
                seen.add(a["url"])
            if len(results) >= max_results:
                break

    # normalize dicts
    normalized = []
    for a in results[:max_results]:
        normalized.append(_normalize_article(a))
    return normalized
