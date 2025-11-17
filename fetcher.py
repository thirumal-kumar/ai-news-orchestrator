import requests
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
import time


# -------------------------------------------------------------------
# Google News RSS Fallback
# -------------------------------------------------------------------
def fetch_google_rss(query, max_results=10):
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    d = feedparser.parse(url)

    articles = []
    for entry in d.entries[:max_results]:
        articles.append({
            "title": entry.title,
            "url": entry.link,
            "published_at": entry.get("published"),
            "source": entry.get("source", {}).get("title", "Google News"),
            "raw_html": None,  # will be filled by extractor
        })
    return articles


# -------------------------------------------------------------------
# NewsAPI (Optional)
# -------------------------------------------------------------------
def fetch_newsapi(query, api_key, max_results=10):
    try:
        url = (
            "https://newsapi.org/v2/everything?"
            f"q={query}&pageSize={max_results}&apiKey={api_key}"
        )

        resp = requests.get(url, timeout=10)
        data = resp.json()

        if data.get("status") != "ok":
            return []

        articles = []
        for a in data["articles"]:
            articles.append({
                "title": a["title"],
                "url": a["url"],
                "published_at": a.get("publishedAt"),
                "source": a["source"]["name"],
                "raw_html": None,
            })
        return articles

    except Exception:
        return []


# -------------------------------------------------------------------
# Combined Fetcher
# -------------------------------------------------------------------
def fetch_articles(query, max_results=10, newsapi_key=None):
    articles = []

    # First: Google News RSS
    try:
        rss_results = fetch_google_rss(query, max_results)
        if rss_results:
            print(f"Google News RSS returned: {len(rss_results)}")
            articles.extend(rss_results)
    except Exception as e:
        print("Google RSS failed:", e)

    # Second: NewsAPI (optional)
    if newsapi_key:
        api_results = fetch_newsapi(query, newsapi_key, max_results)
        if api_results:
            print(f"NewsAPI returned: {len(api_results)}")
            articles.extend(api_results)

    # Deduplicate by URL
    seen = set()
    unique = []
    for a in articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    return unique[:max_results]
