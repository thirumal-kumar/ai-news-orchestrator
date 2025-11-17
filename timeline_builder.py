import os
import openai
import json
import dateparser
from typing import List, Dict, Any
from event_extractor import extract_events_from_text


def infer_dates_with_llm(events: List[Dict[str, Any]], openrouter_key: str):
    """
    Use OpenRouter LLM to infer missing dates from context.
    """
    if not openrouter_key:
        return events

    openai.api_key = openrouter_key
    openai.api_base = "https://openrouter.ai/api/v1"

    text_block = "\n".join([e["sentence"] for e in events[:20]])

    prompt = f"""
    From this text, extract a timeline of events with inferred dates.
    Return ONLY JSON:
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
        data = resp["choices"][0]["message"]["content"]

        return json.loads(data)
    except:
        return []


def build_timeline_from_cleaned(cleaned_articles: List[Dict[str, Any]], use_llm=True):
    """
    Build a timeline using regex events + optional LLM inference.
    """
    all_events = []

    # Extract events from each article
    for art in cleaned_articles:
        events = extract_events_from_text(art.get("cleaned_text") or "")
        source = art.get("url")
        for e in events:
            e["source"] = source
        all_events.extend(events)

    # If user wants AI-inferred dates
    if use_llm:
        key = os.getenv("OPENROUTER_API_KEY")
        llm_events = infer_dates_with_llm(all_events, key)
        if llm_events:
            # Convert LLM output into standard structure
            final = []
            for e in llm_events:
                final.append({
                    "summary": e["summary"],
                    "date": e.get("date"),
                    "sources": []  # LLM loses source, optional
                })
            return final

    # Fallback: sort regex-detected dates
    dated = [e for e in all_events if e["date"]]
    dated.sort(key=lambda x: x["date"])

    final = []
    for e in dated:
        final.append({
            "summary": e["sentence"],
            "date": e["date"],
            "sources": [e.get("source")]
        })

    return final
