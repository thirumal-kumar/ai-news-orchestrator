"""
summarizer.py
Summarize text using OpenRouter free models (e.g., deepseek/deepseek-r1:free)
"""

import os
import requests

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "deepseek/deepseek-r1:free"

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def summarize_text(text: str, max_tokens=250):
    if not OPENROUTER_KEY:
        return text[:500] + "..."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI News Orchestrator",
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a clear and factual news summarizer."},
            {"role": "user", "content": f"Summarize this news text:\n\n{text}"},
        ],
        "max_tokens": max_tokens,
    }

    try:
        resp = requests.post(API_URL, json=data, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return text[:500] + "..."
