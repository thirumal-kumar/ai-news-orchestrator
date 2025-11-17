import requests
import streamlit as st
import time

# ---------------------------
# CONFIG
# ---------------------------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Load key from Streamlit Secrets (never from file)
OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "X-Title": "AI News Orchestrator"
}


# ---------------------------
# INTERNAL CALL WRAPPER
# ---------------------------
def _call_openrouter(messages, max_tokens=500, retries=3):
    """
    Robust OpenRouter call with retry, error handling, and validation.
    """

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "max_tokens": max_tokens
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=30)

            # Basic network failure
            if response.status_code != 200:
                raise Exception(
                    f"Bad status {response.status_code}: {response.text}"
                )

            data = response.json()

            # Validate structure
            if "choices" not in data or not data["choices"]:
                raise Exception(f"Malformed API response: {data}")

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            if attempt == retries:
                return f"[ERROR contacting LLM after {retries} attempts]\n{e}"
            time.sleep(1.5)

    return "[LLM call failed]"  # fallback (should never happen)


# ---------------------------
# PUBLIC SUMMARIZER
# ---------------------------
def summarize_text(text: str, prompt_add: str = "") -> str:
    """
    Summarizes a long input text using OpenRouter.
    """

    if not text or len(text.strip()) < 40:
        return "Not enough content to summarize."

    system_prompt = (
        "You are an AI assistant that writes clean, factual, concise summaries "
        "from multiple news articles. Remove duplicates. Remove speculation. "
        "Focus on verified facts only."
    )

    if prompt_add:
        system_prompt += "\n" + prompt_add

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    return _call_openrouter(messages, max_tokens=400)


# ---------------------------
# HELPER FOR COMBINATIONS
# ---------------------------
def summarize_snippets(snippets: list[str]) -> str:
    """
    Accepts list of text strings → returns combined summary.
    """
    combined = "\n\n".join(snippets)
    return summarize_text(combined)
