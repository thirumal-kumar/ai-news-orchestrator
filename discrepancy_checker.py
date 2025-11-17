# discrepancy_checker.py
from typing import List, Dict

def safe_text(a: Dict):
    """Extract usable text from cleaned article dict."""
    if not a:
        return ""
    return (
        a.get("cleaned_text")
        or a.get("content")
        or a.get("description")
        or ""
    )

def find_discrepancies(cleaned_articles: List[Dict]) -> Dict:
    """
    cleaned_articles: list of dicts as received from clean_article().
    ALWAYS returns a non-empty structured dictionary.
    """

    if not cleaned_articles or len(cleaned_articles) < 2:
        return {"note": "Not enough articles to compare."}

    titles = [a.get("title", "") for a in cleaned_articles]
    dates = [a.get("published_at", "") for a in cleaned_articles]
    texts = [safe_text(a) for a in cleaned_articles]

    out = {
        "Title Differences": [],
        "Publication Date Differences": [],
        "Content Length Differences": [],
        "Keyword Emphasis Differences": [],
    }

    # ---------------------------
    # TITLE DIFFERENCES
    # ---------------------------
    unique_titles = set([t for t in titles if t])
    if len(unique_titles) > 1:
        out["Title Differences"] = list(unique_titles)

    # ---------------------------
    # DATE DIFFERENCES
    # ---------------------------
    unique_dates = set([d for d in dates if d])
    if len(unique_dates) > 1:
        out["Publication Date Differences"] = list(unique_dates)

    # ---------------------------
    # CONTENT LENGTH DIFFERENCES
    # ---------------------------
    lengths = {i: len(texts[i]) for i in range(len(texts))}
    if max(lengths.values()) - min(lengths.values()) > 200:
        out["Content Length Differences"] = [
            f"Article {i+1}: {lengths[i]} characters" for i in lengths
        ]

    # ---------------------------
    # KEYWORD EMPHASIS DIFFERENCES
    # ---------------------------
    keywords = ["pollution", "aqi", "pm2.5", "government", "health", "traffic", "industry"]
    emphasis = {}

    for i, text in enumerate(texts):
        lower = text.lower()
        emphasis[i] = [kw for kw in keywords if kw in lower]

    if len(set([tuple(v) for v in emphasis.values()])) > 1:
        out["Keyword Emphasis Differences"] = emphasis

    # ---------------------------
    # GUARANTEE NON-EMPTY OUTPUT
    # ---------------------------
    if not any(out.values()):
        out["note"] = "Articles appear broadly similar; no major discrepancies detected."

    return out
