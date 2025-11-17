# combined_summary.py
from typing import List, Dict
import re
from summarizer import summarize_text

def _ensure_string(x):
    if x is None:
        return ""
    if isinstance(x, dict):
        return x.get("cleaned_text") or x.get("text") or ""
    if isinstance(x, (list, tuple)):
        return " ".join(_ensure_string(i) for i in x)
    return str(x)

def combine_snippets(cleaned_articles: List[Dict], max_snippets=6) -> str:
    """
    cleaned_articles: list of dicts containing 'cleaned_text' and optionally 'title'
    Returns a unified summary string via LLM.
    """
    snippets = []
    for art in cleaned_articles:
        txt = _ensure_string(art)
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) < 60:
            continue
        snippets.append(txt)
        if len(snippets) >= max_snippets:
            break
    if not snippets:
        return ""
    combined = "\n\n---\n\n".join(snippets)
    prompt = (
        "You will produce a unified summary of multiple news article snippets."
        " Keep it factual, combine overlapping points, and avoid repetition. Output 5-8 short paragraphs."
    )
    return summarize_text(combined, prompt_add=prompt)
