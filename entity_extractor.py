# entity_extractor.py
import re
from collections import defaultdict

def _naive_entities(text):
    """
    Very small heuristic extractor:
    - Dates, CAPS (possible ORG), capitalized sequences (PERSON/ORG)
    Not perfect but no heavy deps.
    """
    ents = defaultdict(list)
    if not text:
        return ents
    # dates (simple)
    for m in re.findall(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                        r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', text, flags=re.I):
        ents["DATE"].append(m)
    # capitalized phrases (2+ tokens)
    caps = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
    for c in caps:
        if len(c.split()) <= 5:
            ents["MISC"].append(c)
    # simple ORG detection by common words
    orgs = re.findall(r'\b([A-Z][\w&]+\s+(?:Ltd|Inc|Corporation|University|Institute|Company|Council|Bank|Ministry))\b', text)
    for o in orgs:
        ents["ORG"].append(o)
    return ents

def extract_entities(cleaned_articles):
    """
    cleaned_articles: list of dicts. Returns dict of entity_type -> list of unique entities.
    """
    if not isinstance(cleaned_articles, list):
        raise TypeError("cleaned_articles must be a list")

    merged = defaultdict(set)
    for art in cleaned_articles:
        if not isinstance(art, dict):
            continue
        text = art.get("cleaned_text") or ""
        ents = _naive_entities(text)
        for k, vals in ents.items():
            for v in vals:
                merged[k].add(v)
    # convert sets -> lists
    return {k: sorted(list(v)) for k, v in merged.items()}
