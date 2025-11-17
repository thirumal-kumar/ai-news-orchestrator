# google_news_fetcher_rss.py
import feedparser
from urllib.parse import quote

def fetch_google_news_articles_rss(query: str, max_results: int = 10):
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    feed = feedparser.parse(url)
    seen = set()
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        # Avoid duplicates
        key = (title.lower(), link.lower())
        if key in seen:
            continue
        seen.add(key)

        articles.append({
            "source": entry.get("source", {}).get("title", "GoogleRSS"),
            "title": title,
            "url": link,
            "summary": entry.get("summary"),
            "content": entry.get("summary"),
            "published_at": entry.get("published"),
            "fetched_with": "google_rss",
        })

        if len(articles) >= max_results:
            break

    return articles
