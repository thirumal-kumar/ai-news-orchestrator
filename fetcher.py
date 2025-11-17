import feedparser
import requests
from urllib.parse import quote

# Import our RSS helper
from google_news_fetcher_rss import fetch_google_news_articles_rss


# ============================================================
# Helper: Clean article structure
# ============================================================

def normalize_article(entry):
    """Ensure uniform article structure."""
    return {
        "title": entry.get("title", "").strip(),
        "url": entry.get("link") or entry.get("url") or "",
        "published_at": entry.get("published") or entry.get("pubDate") or "",
        "source": entry.get("source", "") or entry.get("publisher", "") or "",
        "summary": entry.get("summary", "") or entry.get("description", "")
    }


# ============================================================
# Fetch from Google RSS (primary)
# ============================================================

def fetch_google_rss(query, max_results=10):
    articles = fetch_google_news_articles_rss(query)
    normalized = [normalize_article(a) for a in articles]
    return normalized[:max_results]


# ============================================================
# Fallback fetcher: Bing news (no API key required)
# ============================================================

def fetch_bing_fallback(query, max_results=10):
    """Very lightweight scraper using Bing's news search HTML."""
    url = f"https://www.bing.com/news/search?q={quote(query)}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return []

        # Bing produces messy HTML; this is simple fallback extraction
        lines = r.text.split("<a")
        results = []

        for line in lines:
            if "href=" not in line or "news/search" in line:
                continue
            try:
                link = line.split('href="')[1].split('"')[0]
                title = line.split(">")[1].split("<")[0]
                if len(title) > 5 and link.startswith("http"):
                    results.append({
                        "title": title,
                        "url": link,
                        "published_at": "",
                        "source": "Bing News",
                        "summary": ""
                    })
            except Exception:
                pass

        return results[:max_results]

    except Exception:
        return []


# ============================================================
# Main universal fetcher (used in app.py)
# ============================================================

def fetch_articles(query, news_api_key=None, max_results=10):
    """
    Main fetcher used by Streamlit.
    Order:
     1. Google News RSS (fast, stable)
     2. Bing fallback (if RSS returns nothing)
    """

    # ---- FIX: Ensure max_results is always INT ----
    try:
        max_results = int(max_results or 10)
    except:
        max_results = 10
    # ----------------------------------------------

    all_articles = []

    # 1. GOOGLE RSS (primary)
    rss = fetch_google_rss(query, max_results=max_results)
    all_articles.extend(rss)

    # If RSS gave enough articles, return immediately
    if len(all_articles) >= max_results:
        return all_articles[:max_results]

    # 2. BING FALLBACK
    bing_articles = fetch_bing_fallback(query, max_results=max_results)
    all_articles.extend(bing_articles)

    # Deduplicate based on URLs
    seen = set()
    unique = []
    for a in all_articles:
        url = a.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(a)

    return unique[:max_results]
