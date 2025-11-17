import time
import requests

# -------------------------------------------------
# CONFIG — Replace with your API key
# -------------------------------------------------
OPENROUTER_API_KEY = "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"

# New endpoint (old one is dead)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default model
DEFAULT_MODEL = "openai/gpt-4o-mini"


# -------------------------------------------------
# INTERNAL API CALL WRAPPER
# -------------------------------------------------
def _call_openrouter(messages, model=DEFAULT_MODEL, max_tokens=400, retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "AI News Orchestrator"
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=40
            )

            # Raise for 4xx and 5xx
            response.raise_for_status()

            data = response.json()

            return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"[OpenRouter] Attempt {attempt}/{retries} failed: {e}")

            # Small delay before retry
            time.sleep(1.5 * attempt)

    # If we ever reach here, API failed after all retries
    raise RuntimeError(
        f"OpenRouter API failed after {retries} retries. Last error: {last_error}"
    )


# -------------------------------------------------
# PUBLIC SUMMARIZATION FUNCTION
# (USED BY YOUR APP)
# -------------------------------------------------
def summarize_text(text, prompt_add=""):
    """
    Generates a clean summary of the given text.
    """
    if not text or not text.strip():
        return "No text available for summarization."

    system_prompt = (
        "You are an expert news summarizer. Your job is to produce a clear, "
        "factual, concise summary without adding extra speculation. "
        "Do NOT change meaning. Focus on correctness."
    )

    if prompt_add:
        system_prompt += " " + prompt_add

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    return _call_openrouter(messages, max_tokens=400)
