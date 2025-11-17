import os
import openai
import json
import dateparser
from event_extractor import extract_events_from_text


def safe_event(summary, date, sources):
    """
    ALWAYS returns a unified timeline event structure.
    """
    parsed = None
    if date:
        try:
            parsed = dateparser.parse(date)
        except:
            parsed = None

    return {
        "summary": summary,
        "date": date,
        "date_iso": parsed.isoformat() if parsed else None,
        "sources": sources or []
    }


def infer_timeline_with_llm(events, openrouter_key):
    """
    LLM-based timeline inference.
    Returns a list of unified SAFE events.
    """
    if not openrouter_key:
        return []

    openai.api_key = openrouter_key
    openai.api_base = "https://openrouter.ai/api/v1"

    text_block = "\n".join([e["sentence"] for e in events[:20]])

    prompt = f"""
    Extract a timeline of events from the following text.
    Return ONLY JSON in this format:
    [
       {{ "summary": "...", "date": "YYYY-MM-DD or null" }}
    ]
    Text:
    {text_block}
    """

    try:
        resp = openai.ChatCompletion.create(
            model="openrouter/anthropic/claude-3.5-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        raw = resp["choices"][0]["message"]["content"]
        data = json.loads(raw)

        safe = []
        for e in data:
            safe.append(
                safe_event(
                    summary=e.get("summary", "Event"),
                    date=e.get("date"),
                    sources=[]
                )
            )
        return safe

    except:
        return []


def build_timeline_from_cleaned(cleaned_articles, use_llm=True):
    """
    Main function: builds a safe timeline structure.
    """
    all_events = []

    for art in cleaned_articles:
        events = extract_events_from_text(art.get("cleaned_text") or "")
        source = art.get("url")
        for e in events:
            all_events.append({
                "sentence": e["sentence"],
                "date": e["date"],
                "source": source
            })

    # Step 1 — LLM inference if enabled
    if use_llm:
        key = os.getenv("OPENROUTER_API_KEY")
        llm_events = infer_timeline_with_llm(all_events, key)
        if llm_events:
            return llm_events

    # Step 2 — Regex timeline fallback
    dated = [e for e in all_events if e["date"]]
    dated.sort(key=lambda x: x["date"])

    final = []
    for e in dated:
        final.append(
            safe_event(
                summary=e["sentence"],
                date=e["date"],
                sources=[e.get("source")]
            )
        )

    # Step 3 — No dates at all → return top events
    if not final:
        for e in all_events[:5]:
            final.append(
                safe_event(
                    summary=e["sentence"],
                    date=None,
                    sources=[e.get("source")]
                )
            )

    return final
