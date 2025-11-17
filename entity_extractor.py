# entity_extractor.py
from summarizer import extract_entities_llm
from typing import Dict, List

def extract_entities(text: str) -> Dict[str, List[str]]:
    if not text:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": [], "NUMBERS": []}
    out = extract_entities_llm(text)
    # Ensure keys exist
    result = {}
    for k in ("PERSON", "ORG", "GPE", "DATE", "NUMBERS"):
        v = out.get(k)
        if isinstance(v, list):
            result[k] = list(dict.fromkeys(v))
        else:
            result[k] = []
    return result
