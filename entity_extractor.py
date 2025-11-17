import openai
import os
import json

def extract_entities(text: str) -> dict:
    """
    Cloud-safe entity extractor using OpenRouter LLM.
    No spaCy required. Returns PERSON, ORG, GPE, DATE entities.
    """
    if not text or len(text.strip()) < 30:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    prompt = f"""
    Extract named entities from the following text.
    Return only JSON with keys PERSON, ORG, GPE, DATE.
    Text:
    {text[:2000]}
    """

    try:
        response = openai.ChatCompletion.create(
            model="openrouter/anthropic/claude-3.5-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)

    except Exception:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}
