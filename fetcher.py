import feedparser
import requests
from urllib.parse import quote


# ============================================================
# Google News RSS Fetcher (self-contained)
# ============================================================

def fetch_google_news_articles_rss(query):
    """
    Direct Google News RSS fetcher.
    Returns list of dicts with title, link, published, summary.
    """
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published_at": entry.get("published", ""),
            "source": entry.get("source", {}).get("title", ""),
            "summary": entry.get("summary", "")
        })

    return articles


# ============================================================
# Normalize (uniform dictionary)
# ============================================================

def normalize_article(entry):
    return {
        "title": entry.get("title", "").strip(),
        "url": entry.get("url") or entry.get("link") or "",
        "published_at": entry.get("published_at", entry.get("pubDate", "")),
        "source": entry.get("source", ""),
        "summary": entry.get("summary", entry.get("description", ""))
    }


# ============================================================
# Bing fallback (HTML scrape)
# ============================================================

def fetch_bing_fallback(query, max_results=10):
    url = f"https://www.bing.com/news/search?q={quote(query)}"

    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return []
    except Exception:
        return []

    articles = []
    chunks = r.text.split("<a")
    for c in chunks:
        if "href=" not in c or "news/search" in c:
            continue
        try:
            link = c.split('href="')[1].split('"')[0]
            title = c.split(">")[1].split("<")[0]
            if link.startswith("http") and len(title) > 5:
                articles.append({
                    "title": title,
                    "url": link,
                    "published_at": "",
                    "source": "Bing News",
                    "summary": ""
                })
        except:
            pass

    return articles[:max_results]


# ============================================================
# MAIN FETCH FUNCTION
# ============================================================

def fetch_articles(query, news_api_key=None, max_results=10):
    # Ensure integer
    try:
        max_results = int(max_results)
    except:
        max_results = 10

    final = []

    # 1. Google RSS
    rss_articles = fetch_google_news_articles_rss(query)
    final.extend([normalize_article(a) for a in rss_articles])

    if len(final) >= max_results:
        return final[:max_results]

    # 2. Bing fallback
    bing = fetch_bing_fallback(query, max_results)
    final.extend(bing)

    # Deduplicate
    seen = set()
    uniq = []
    for a in final:
        u = a.get("url", "")
        if u and u not in seen:
            seen.add(u)
            uniq.append(a)

    return uniq[:max_results]
