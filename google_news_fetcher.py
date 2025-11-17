"""
google_news_fetcher.py
Google News scraper to fetch article URLs for any topic.
Works without any API key.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


GOOGLE_NEWS_URL = (
    "https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


def fetch_google_news_links(query: str, max_links: int = 10):
    """Fetch Google News result links (Google redirect URLs)."""
    search_url = GOOGLE_NEWS_URL.format(query=query.replace(" ", "+"))
    resp = requests.get(search_url, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    a_tags = soup.select("article h3 a")

    links = []
    for a in a_tags[:max_links]:
        href = a.get("href")
        if not href:
            continue
        # Convert relative link to full Google News redirect URL
        full_link = urljoin("https://news.google.com/", href)
        links.append(full_link)

    return links


def resolve_google_news_url(gn_url: str):
    """
    Convert Google redirect link into the actual publisher link.
    Example: Google link -> Mint / NDTV / IndianExpress real URL.
    """
    try:
        resp = requests.get(gn_url, allow_redirects=True, timeout=10)
        return resp.url
    except:
        return gn_url


def fetch_google_news_articles(query: str, max_results: int = 10):
    """
    Fetch real article URLs, wrapped as article dicts
    ready for extractor.py.
    """
    google_links = fetch_google_news_links(query, max_links=max_results)
    resolved_links = [resolve_google_news_url(url) for url in google_links]

    articles = []
    for url in resolved_links:
        articles.append(
            {
                "source": "GoogleNews",
                "title": url.split("/")[-1].replace("-", " ")[:80],
                "url": url,
                "summary": None,
                "content": "",
                "published_at": None,
                "fetched_with": "google_news",
            }
        )

    return articles
