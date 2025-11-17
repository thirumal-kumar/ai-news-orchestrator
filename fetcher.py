import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from urllib.parse import quote

from google_news_fetcher_rss import fetch_google_news_articles_rss


def normalize_article(a):
    """Ensure the article is always a dict."""
    if isinstance(a, dict):
        return a
    if isinstance(a, str):
        return {
            "title": a,
            "url": "",
            "source": "Unknown",
            "published_at": None
        }
    return {
        "title": "Unknown",
        "url": "",
        "source": "Unknown",
        "published_at": None
    }


def fetch_articles(query, newsapi_key=None, max_results=8):
    max_results = int(max_results)

    results = []

    # 1) Google News RSS first
    try:
        rss_articles = fetch_google_news_articles_rss(query)
        results.extend(rss_articles)
    except Exception as e:
        print("RSS fetch failed:", e)

    # 2) Clean up URLs and enforce dict
    unique = []
    seen = set()

    for a in results:
        a = normalize_article(a)

        url = a.get("url", "")
        if url in seen:
            continue

        seen.add(url)
        unique.append(a)

    return unique[:max_results]
