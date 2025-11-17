# event_extractor.py
"""
Event extractor:
- Splits article text into sentences
- Finds date mentions (dateparser)
- Extracts named entities per sentence (spaCy)
- Returns list of event dicts with: date (datetime or None), sentence, entities
"""

import re
from typing import List, Dict, Any, Optional
import dateparser
import spacy

# Ensure you installed: pip install spacy dateparser
# And downloaded a model: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")


def _sentences(text: str) -> List[str]:
    # fallback sentence splitter using spacy
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


def _find_date_in_text(text: str) -> Optional[Any]:
    # try to parse explicit dates in the sentence
    # dateparser can handle "yesterday", "Nov 17", "on Friday", etc.
    dt = dateparser.parse(text, settings={"PREFER_DATES_FROM": "past"})
    return dt


def extract_events_from_text(text: str, title: str = None) -> List[Dict]:
    events = []
    if not text:
        return events

    for sent in _sentences(text):
        # skip short sentences
        if len(sent) < 30:
            continue

        dt = _find_date_in_text(sent)
        # also try to anchor on title/published date later in pipeline if dt is None

        doc = nlp(sent)
        ents = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

        # Heuristic: sentences containing numbers/years or explicit date words are more likely events
        if dt or re.search(r"\b(20\d{2}|19\d{2}|today|yesterday|tomorrow|tonight|on|by|since|week|month)\b", sent, re.I):
            events.append({
                "date": dt,             # may be None
                "sentence": sent,
                "entities": ents,
            })
    return events
