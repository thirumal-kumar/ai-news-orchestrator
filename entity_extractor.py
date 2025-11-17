import openai
import os
import json

def extract_entities(text: str) -> dict:
    """
    Cloud-safe LLM-based NER with strict JSON output.
    Extracts PERSON, ORG, GPE, and DATE entities.
    """

    # Not enough text → return empty entities
    if not text or len(text.strip()) < 30:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    prompt = f"""
Extract PERSON, ORG, GPE, and DATE entities from the following text.

⚠️ Return ONLY valid JSON, no markdown, no code fences, no comments.

Correct format:
{{
  "PERSON": ["Alice"],
  "ORG": ["Google"],
  "GPE": ["India"],
  "DATE": ["Monday"]
}}

TEXT:
{text[:2000]}
"""

    try:
        response = openai.ChatCompletion.create(
            model="openrouter/anthropic/claude-3.5-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )

        raw = response["choices"][0]["message"]["content"]

        # Remove markdown wrappers
        raw = raw.replace("```json", "").replace("```", "").strip()

        # Ensure valid JSON
        return json.loads(raw)

    except Exception:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}
