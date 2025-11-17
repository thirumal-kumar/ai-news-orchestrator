import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

# =======================================================================
# GOOGLE NEWS RSS FALLBACK (always works, no API key required)
# =======================================================================

def fetch_google_rss(query: str, max_results: int = 10):
    """Fetch news headlines from Google News RSS."""
    rss_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        resp = requests.get(rss_url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")

        articles = []
        for item in soup.find_all("item")[:max_results]:
            title = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            pub_date = item.pubDate.text if item.pubDate else ""

            try:
                pub_date = str(dateparser.parse(pub_date))
            except:
                pass

            articles.append({
                "title": title,
                "url": link,
                "source": "Google News RSS",
                "summary": "",
                "published_at": pub_date
            })
        return articles

    except Exception:
        return []

# =======================================================================
# OPTIONAL NEWSAPI FETCHER (only if key is provided)
# =======================================================================

def fetch_newsapi(query: str, max_results: int, key: str):
    """Fetch articles using NewsAPI if the user provides a key."""
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={quote(query)}&sortBy=publishedAt&pageSize={max_results}&apiKey={key}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if "articles" not in data:
            return []

        results = []
        for a in data["articles"]:
            results.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
                "summary": a.get("description", ""),
                "published_at": a.get("publishedAt", "")
            })
        return results

    except Exception:
        return []

# =======================================================================
# MAIN FETCHER LOGIC (RSS → NewsAPI)
# =======================================================================

def fetch_articles(query: str, newsapi_key: str = "", max_results: int = 10):
    """Unified article fetcher. Always returns a list of dicts."""
    results = []

    # 1) Try RSS first
    rss_articles = fetch_google_rss(query, max_results)
    results.extend(rss_articles)

    # 2) If NewsAPI key exists → merge results (dedupe by URL)
    if newsapi_key:
        api_articles = fetch_newsapi(query, max_results, newsapi_key)
        results.extend(api_articles)

    # DEDUPLICATE
    final = []
    seen = set()

    for a in results:
        if not isinstance(a, dict):
            continue
        url = a.get("url", "")
        if url and url not in seen:
            seen.add(url)
            final.append(a)

    return final[:max_results]
