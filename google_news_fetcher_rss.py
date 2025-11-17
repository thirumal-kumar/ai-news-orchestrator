# google_news_fetcher_rss.py
import feedparser
from urllib.parse import quote
from datetime import datetime
import time

def fetch_google_news_articles_rss(query: str, max_results: int = 8):
    """
    Query Google News RSS and return list of dicts:
    { "title","url","published_at","source" }
    """
    q = quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    d = feedparser.parse(url)
    if d.bozo and getattr(d, "bozo_exception", None):
        raise RuntimeError(f"fetch_google_rss_error: {d.bozo_exception}")
    items = []
    for entry in d.entries[:max_results]:
        title = entry.get("title", "")
        link = entry.get("link", "")
        # published parsed fallback
        published = entry.get("published", "")
        try:
            published_at = published
        except Exception:
            published_at = ""
        source = entry.get("source", {}).get("title") if entry.get("source") else ""
        items.append({
            "title": title,
            "url": link,
            "published_at": published_at,
            "source": source or "news.google.com"
        })
        time.sleep(0.01)
    return items
