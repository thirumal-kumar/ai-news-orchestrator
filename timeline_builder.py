# timeline_builder.py
"""
Improved AI timeline engine:
- Removes duplicate events
- Better clustering
- More stable date inference
"""

from datetime import datetime
import os
import re
import requests
import dateparser
from difflib import SequenceMatcher
from collections import Counter
from event_extractor import extract_events_from_text


OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "deepseek/deepseek-r1:free"


def _similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _llm_date(sentence, published_iso):
    if not OPENROUTER_KEY:
        return None

    prompt = (
        "Infer the exact date (YYYY-MM-DD) mentioned or implied here. "
        "If unclear, return NONE.\n"
        f"Article date: {published_iso}\n"
        f"Sentence: {sentence}"
    )

    try:
        resp = requests.post(
            OPENROUTER_URL,
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": "Return ONLY a date or NONE."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 15,
                "temperature": 0,
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=20,
        )

        txt = resp.json()["choices"][0]["message"]["content"].strip()
        m = re.search(r"\d{4}-\d{2}-\d{2}", txt)
        return m.group(0) if m else None

    except Exception:
        return None


def build_timeline_from_cleaned(cleaned, use_llm=True):
    raw_events = []
    seen_sentences = set()

    for art in cleaned:
        text = art.get("cleaned_text") or ""
        title = art.get("title") or ""
        pub = art.get("published_at")
        pub_dt = dateparser.parse(pub) if pub else None

        events = extract_events_from_text(text, title=title)[:5]

        for ev in events:
            sent = ev["sentence"].strip()

            # Skip duplicates
            key = sent.lower()
            if key in seen_sentences:
                continue
            seen_sentences.add(key)

            # Try parse explicit date
            dt = dateparser.parse(sent, settings={"PREFER_DATES_FROM": "past"})
            date_iso = dt.date().isoformat() if dt else None

            # Try LLM if needed
            if not date_iso and use_llm and pub:
                inferred = _llm_date(sent, pub)
                if inferred:
                    date_iso = inferred
                    dt = dateparser.parse(date_iso)

            # Fallback → article date
            if not date_iso and pub_dt:
                date_iso = pub_dt.date().isoformat()
                dt = pub_dt

            raw_events.append({
                "sentence": sent,
                "source": art.get("source"),
                "date_iso": date_iso,
                "date": dt,
            })

    # Cluster similar events
    timeline = []
    for ev in raw_events:
        placed = False
        for t in timeline:
            if _similar(ev["sentence"], t["summary"]) > 0.55:
                t["sources"].add(ev["source"])
                t["examples"].append(ev["sentence"])
                placed = True
                break

        if not placed:
            timeline.append({
                "summary": ev["sentence"],
                "date": ev["date"],
                "date_iso": ev["date_iso"],
                "sources": {ev["source"]},
                "examples": [ev["sentence"]],
            })

    # Sort by date → undated at bottom
    dated = [t for t in timeline if t["date"]]
    undated = [t for t in timeline if not t["date"]]

    dated_sorted = sorted(dated, key=lambda x: x["date"])
    return dated_sorted + undated
