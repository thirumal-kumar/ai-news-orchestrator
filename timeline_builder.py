# timeline_builder.py
from dateutil import parser
from collections import defaultdict

def build_timeline_from_cleaned(cleaned_articles):
    """
    Returns dict date -> list of titles
    """
    timeline = defaultdict(list)
    for a in cleaned_articles:
        if not isinstance(a, dict):
            continue
        dt = a.get("published_at") or ""
        try:
            parsed = parser.parse(dt)
            key = parsed.date().isoformat()
        except Exception:
            key = "unknown"
        timeline[key].append(a.get("title") or a.get("url") or "")
    # sort keys
    return dict(sorted(timeline.items(), reverse=True))
