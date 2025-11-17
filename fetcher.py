# fetcher.py
# Self-contained article fetcher (no external google_news_fetcher_rss import)
# Uses requests + BeautifulSoup to fetch Google News RSS (no extra packages beyond requests & beautifulsoup4)

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from dateutil import parser as dateparser


def fetch_google_rss(query: str, max_results: int = 10):
    """
    Fetch news items from Google News RSS search feed.
    Returns a list of article dicts with keys: title, url, source, published_at, summary.
    """
    try:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")

        items = soup.find_all("item")
        articles = []
        for item in items[:max_results]:
            title = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            pub = item.pubDate.text if item.pubDate else None
            summary = item.description.text if item.description else ""

            # Normalize published date
            pub_iso = None
            try:
                if pub:
                    pub_iso = str(dateparser.parse(pub))
            except Exception:
                pub_iso = pub

            # Try to extract source from <source> tag (if present)
            source = None
            try:
                if item.find("source"):
                    source = item.find("source").text
            except Exception:
                source = None

            articles.append({
                "title": title,
                "url": link,
                "source": source or "Google News",
                "published_at": pub_iso,
                "summary": summary
            })
        return articles
    except Exception as e:
        # don't crash the app; log to stdout for Streamlit logs
        print("fetch_google_rss error:", e)
        return []


def fetch_newsapi(query: str, max_results: int, key: str):
    """
    Optional: fetch via NewsAPI if API key provided.
    Returns list of article dicts (same format).
    """
    try:
        url = (
            "https://newsapi.org/v2/everything?"
            f"q={quote(query)}&sortBy=publishedAt&pageSize={max_results}&apiKey={key}"
        )
        resp = requests.get(url, timeout=12)
        data = resp.json()
        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
                "published_at": a.get("publishedAt"),
                "summary": a.get("description", "") or a.get("content", "")
            })
        return articles
    except Exception as e:
        print("fetch_newsapi error:", e)
        return []


def normalize_article(a):
    """Ensure the article is always a dict with expected keys."""
    if isinstance(a, dict):
        return a
    if isinstance(a, str):
        return {
            "title": a,
            "url": "",
            "source": "Unknown",
            "published_at": None,
            "summary": ""
        }
    return {
        "title": "",
        "url": "",
        "source": "Unknown",
        "published_at": None,
        "summary": ""
    }


def fetch_articles(query: str, newsapi_key: str = None, max_results: int = 8):
    """
    Unified fetcher. Attempts Google RSS first; if NewsAPI key provided,
    merges NewsAPI results (deduplicated by URL). Always returns list of dicts.
    """
    max_results = int(max_results or 8)
    results = []

    # 1. Google RSS
    results.extend(fetch_google_rss(query, max_results))

    # 2. Optional: NewsAPI (if API key provided)
    if newsapi_key:
        try:
            results.extend(fetch_newsapi(query, max_results, newsapi_key))
        except Exception as e:
            print("newsapi fetch error:", e)

    # Dedupe by URL and ensure dict format
    unique = []
    seen = set()
    for a in results:
        a = normalize_article(a)
        url = (a.get("url") or "").strip()
        # use title fallback when url empty
        key = url if url else a.get("title", "").strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        unique.append(a)

    # Return up to max_results
    return unique[:max_results]
