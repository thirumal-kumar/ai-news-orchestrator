# timeline_builder.py
from typing import List, Dict
from event_extractor import extract_events_from_text
from dateparser import parse as dateparse
import pytz

def build_timeline_from_cleaned(cleaned_articles: List[Dict], use_llm: bool = True) -> List[Dict]:
    """
    Returns timeline list sorted by date_iso if available.
    Each event: { date, date_iso, sentence, sources }
    """
    raw_events = []
    for art in cleaned_articles:
        text = art.get("cleaned_text") or ""
        title = art.get("title") or ""
        events = []
        if use_llm:
            events = extract_events_from_text(text)
        else:
            # naive: split into sentences and find date-like tokens
            sents = text.split(".")
            for s in sents:
                if len(s.strip()) < 40:
                    continue
                events.append({"date": None, "date_iso": None, "sentence": s.strip(), "numbers": [], "sources": [art.get("source")]})
        # attach article info
        for e in events:
            e["sources"] = e.get("sources") or [art.get("source")]
            raw_events.append(e)
    # normalize dates
    for e in raw_events:
        if not e.get("date_iso"):
            dstr = e.get("date")
            parsed = None
            if dstr:
                parsed = dateparse(str(dstr))
            if parsed:
                try:
                    e["date_iso"] = parsed.isoformat()
                    e["date"] = parsed.date().isoformat()
                except Exception:
                    e["date_iso"] = None
    # sort: events with date_iso first by date_iso, others at end
    def _key(x):
        return x.get("date_iso") or "9999-12-31T00:00:00"
    raw_events.sort(key=_key)
    return raw_events
