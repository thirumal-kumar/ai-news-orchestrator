import os
import json
import requests
from typing import Dict, List
from collections import defaultdict

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "anthropic/claude-3.5-sonnet"


def call_llm(prompt: str) -> str:
    """Helper for OpenRouter API calls."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    LLM-based Named Entity Recognition (no spaCy).
    Extracts PERSON, ORG, GPE, DATE using an LLM.
    """

    if not text or text.strip() == "":
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

    prompt = f"""
    Extract named entities from the text.

    Return ONLY JSON with the following keys:
    PERSON, ORG, GPE, DATE.

    If a category has no entities, return an empty list.

    Text:
    \"\"\"{text}\"\"\"
    """

    try:
        result = call_llm(prompt)

        # Handle bad responses gracefully
        try:
            data = json.loads(result)
        except Exception:
            # fallback: extract lists manually
            data = {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

        cleaned = defaultdict(list)

        for key in ["PERSON", "ORG", "GPE", "DATE"]:
            values = data.get(key, [])
            if isinstance(values, list):
                cleaned[key] = list(dict.fromkeys([v.strip() for v in values if v.strip()]))
            else:
                cleaned[key] = []

        return cleaned

    except Exception:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}
