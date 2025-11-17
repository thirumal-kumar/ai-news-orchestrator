import os
import openai
import json
import dateparser
from event_extractor import extract_events_from_text


def safe_event(summary, date, sources):
    """
    Always return unified safe event format.
    Prevents KeyError in UI.
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
    Use Claude (OpenRouter) to infer missing dates.
    Enforces strict JSON output.
    """
    if not openrouter_key:
        return []

    openai.api_key = openrouter_key
    openai.api_base = "https://openrouter.ai/api/v1"

    # Use first few sentences for efficient processing
    text_block = "\n".join([e["sentence"] for e in events[:20]])

    prompt = f"""
You are generating a news timeline from multiple articles.

Rules:
1. If a sentence contains a date, use that date.
2. If no date is explicitly given, infer the date from context.
3. If an article mentions a publication date, assume events occur ON or BEFORE that date.
4. ALWAYS output STRICT JSON array, no markdown, no comments.

Correct JSON format:
[
  {{ "summary": "Event description", "date": "YYYY-MM-DD or null" }}
]

TEXT:
{text_block}
"""

    try:
        resp = openai.ChatCompletion.create(
            model="openrouter/anthropic/claude-3.5-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )

        raw = resp["choices"][0]["message"]["content"]
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)

        # Convert to safe event structure
        final = []
        for e in data:
            final.append(
                safe_event(
                    summary=e.get("summary", "Event"),
                    date=e.get("date"),
                    sources=[]
                )
            )
        return final

    except Exception:
        return []


def build_timeline_from_cleaned(cleaned_articles, use_llm=True):
    """
    Build a clean timeline from cleaned articles.
    LLM timeline → fallback regex → fallback recent events.
    """
    all_events = []

    for art in cleaned_articles:
        text = art.get("cleaned_text") or ""
        source = art.get("url")
        pub = art.get("published_at")

        events = extract_events_from_text(text)
        for e in events:
            all_events.append({
                "sentence": e["sentence"],
                "date": e["date"] or pub,   # default to publication date
                "source": source
            })

    # Prefer LLM inference
    if use_llm:
        key = os.getenv("OPENROUTER_API_KEY")
        llm = infer_timeline_with_llm(all_events, key)
        if llm:
            return llm

    # Regex-only timeline
    dated = [e for e in all_events if e["date"]]
    dated.sort(key=lambda x: x["date"])

    final = []
    for e in dated:
        final.append(
            safe_event(
                summary=e["sentence"],
                date=e["date"],
                sources=[e["source"]]
            )
        )

    # Last fallback: no dates at all
    if not final:
        for e in all_events[:5]:
            final.append(
                safe_event(
                    summary=e["sentence"],
                    date=None,
                    sources=[e["source"]]
                )
            )

    return final
