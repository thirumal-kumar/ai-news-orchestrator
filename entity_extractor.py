# entity_extractor.py
"""
Entity extractor: returns aggregated entities (PERSON, ORG, GPE, DATE)
"""

import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str):
    doc = nlp(text or "")
    out = defaultdict(list)
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE", "DATE", "LOC"):
            out[ent.label_].append(ent.text)
    # deduplicate
    return {k: list(dict.fromkeys(v)) for k, v in out.items()}
