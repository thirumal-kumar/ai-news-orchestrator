"""
timeline.py
Extract dates + create a chronological event timeline.
"""

from typing import List, Dict
import dateparser


def extract_events(cleaned_articles: List[Dict]):
    events = []
    for art in cleaned_articles:
        text = art["cleaned_text"]
        date = dateparser.parse(art.get("published_at") or "")
        if not date:
            continue

        snippet = text[:220] + "..." if len(text) > 220 else text

        events.append({
            "date": date,
            "title": art["title"],
            "snippet": snippet,
            "url": art["url"],
            "source": art["source"],
        })
    return events


def build_timeline(events):
    return sorted(events, key=lambda x: x["date"])
