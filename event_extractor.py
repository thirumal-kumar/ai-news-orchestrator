import re
import dateparser
from typing import List, Dict, Any

# Detect short date formats
DATE_PATTERN = re.compile(
    r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
)

# Detect month names
MONTH_PATTERN = re.compile(
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December'
    r'|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b',
    re.IGNORECASE
)

# Numeric mismatch detection
NUMBER_PATTERN = re.compile(r'\b\d+(?:\.\d+)?\b')


def extract_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Cloud-safe event extractor WITHOUT spaCy.
    Uses regex + dateparser + heuristics.
    Returns list of events: { "sentence", "date", "numbers" }
    """
    events = []
    if not text:
        return events

    # Split into sentences
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)

    for sent in raw_sentences:
        sent = sent.strip()
        if len(sent) < 40:
            continue

        # Extract dates
        dates = DATE_PATTERN.findall(sent)
        has_month = MONTH_PATTERN.search(sent)

        parsed_date = None
        if dates:
            parsed_date = dateparser.parse(dates[0], settings={"STRICT_PARSING": False})
        elif has_month:
            parsed_date = dateparser.parse(sent, settings={"STRICT_PARSING": False})

        # Extract numbers
        nums = NUMBER_PATTERN.findall(sent)

        events.append({
            "sentence": sent,
            "date": parsed_date.isoformat() if parsed_date else None,
            "numbers": nums or []
        })

    return events
