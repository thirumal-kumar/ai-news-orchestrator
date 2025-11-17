import feedparser
from urllib.parse import quote

def fetch_google_news_articles_rss(query, max_results=10):
    """
    Fetch articles from Google News RSS feed.
    Always works because RSS has no API limits.
    """
    try:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)

        articles = []
        for entry in feed.entries[:max_results]:
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "source": entry.get("source", {}).get("title", "Google News"),
                "published_at": entry.get("published", None),
                "summary": entry.get("summary", "")
            })

        return articles
    except Exception as e:
        print("RSS fetch failed:", e)
        return []
