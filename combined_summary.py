# combined_summary.py
import re
from summarizer import summarize_text  # uses OpenRouter wrapper you already have

def combine_snippets(cleaned_articles, prompt_add=""):
    """
    cleaned_articles: list of article dicts (see data model)
    returns a single summary string
    """
    if not isinstance(cleaned_articles, list):
        raise TypeError("cleaned_articles must be a list of dicts")

    snippets = []
    for art in cleaned_articles:
        if not isinstance(art, dict):
            continue
        text = art.get("cleaned_text") or ""
        if not text:
            # try title fallback
            text = art.get("title") or ""
        s = re.sub(r"\s+", " ", text).strip()
        if len(s) < 40:
            continue
        snippets.append(s)

    if not snippets:
        return "No usable article text to summarize."

    # join but keep within a safe size (we will chunk if too large)
    joined = "\n\n".join(snippets[:20])  # limit number of snippets
    # optionally add small system instruction
    prompt = "Summarize the following news passages into a single concise factual summary."
    if prompt_add:
        prompt += " " + prompt_add
    return summarize_text(joined, prompt_add=prompt)
