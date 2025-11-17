# event_extractor.py
from summarizer import _call_openrouter
import json

def extract_events_from_text(text: str):
    """
    Ask LLM to extract events into a strict JSON list of objects:
    [{ "date": "...", "date_iso": "...", "sentence":"...", "numbers":[...], "sources":[...]}]
    """
    if not text:
        return []
    system = "You are an extractor. Output valid JSON list of event objects with keys: date, date_iso, sentence, numbers, sources."
    user = (
        "Extract distinct events from the text. Each event should be an object with:\n"
        "- date: human-friendly date if present, otherwise null\n"
        "- date_iso: ISO 8601 if possible, otherwise null\n"
        "- sentence: the sentence describing the event\n"
        "- numbers: array of numeric values found\n"
        "- sources: array of source names if mentioned\n\n"
        f"Text:\n{text}\n\nReturn JSON only."
    )
    messages = [{"role":"system","content":system},{"role":"user","content":user}]
    out = _call_openrouter(messages, max_tokens=700)
    try:
        return json.loads(out)
    except Exception:
        # fallback: single event with whole text
        return [{"date": None, "date_iso": None, "sentence": text[:800], "numbers": [], "sources": []}]
