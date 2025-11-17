"""
Lightweight entity extractor — Streamlit Cloud compatible
Uses OpenRouter/OpenAI instead of spaCy.
"""

import os
from collections import defaultdict
import requests
import json

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

LLM_MODEL = "gpt-4o-mini"     # Small, cheap, very good at NER

def llm_extract_entities(text: str) -> dict:

    if not OPENROUTER_KEY:
        return {
            "PERSON": [],
            "ORG": [],
            "GPE": [],
            "DATE": []
        }

    prompt = f"""
Extract named entities from the following text.
Return JSON with keys PERSON, ORG, GPE, DATE.

Text:
{text[:4000]}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             headers=headers, json=body, timeout=20)

        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        return json.loads(content)

    except Exception as e:
        return {
            "PERSON": [],
            "ORG": [],
            "GPE": [],
            "DATE": []
        }


def extract_entities(cleaned_articles):
    """
    cleaned_articles: list of dicts with "cleaned_text"
    """
    merged = defaultdict(set)

    for art in cleaned_articles:
        text = art.get("cleaned_text") or ""
        ents = llm_extract_entities(text)
        for k, v in ents.items():
            for item in v:
                merged[k].add(item)

    return {k: list(v) for k, v in merged.items()}
