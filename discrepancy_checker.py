# discrepancy_checker.py

def safe(x):
    if not x:
        return ""
    if isinstance(x, dict):
        return (x.get("cleaned_text") or 
                x.get("content") or 
                x.get("description") or 
                "")
    return str(x)


def find_discrepancies(cleaned_articles):
    """
    Always returns meaningful discrepancies.
    Never returns empty list.
    Output is a dictionary so Streamlit JSON viewer renders correctly.
    """

    if not cleaned_articles or len(cleaned_articles) < 2:
        return {
            "note": "Not enough articles to compare."
        }

    # --------------------------------
    # Extract key fields
    # --------------------------------
    titles = [a.get("title", "") for a in cleaned_articles]
    dates = [a.get("published_at", "") for a in cleaned_articles]
    texts = [safe(a) for a in cleaned_articles]

    # --------------------------------
    # Prepare container
    # --------------------------------
    out = {
        "Title Differences": [],
        "Publication Date Differences": [],
        "Content Length Differences": [],
        "Keyword Emphasis Differences": []
    }

    # --------------------------------
    # TITLE DIFFERENCES
    # --------------------------------
    unique_titles = set([t for t in titles if t])
    if len(unique_titles) > 1:
        out["Title Differences"] = list(unique_titles)

    # --------------------------------
    # DATE DIFFERENCES
    # --------------------------------
    unique_dates = set([d for d in dates if d])
    if len(unique_dates) > 1:
        out["Publication Date Differences"] = list(unique_dates)

    # --------------------------------
    # CONTENT LENGTH DIFFERENCES
    # --------------------------------
    lengths = {i: len(texts[i]) for i in range(len(texts))}
    if max(lengths.values()) - min(lengths.values()) > 300:
        out["Content Length Differences"] = [
            f"Article {i+1}: {lengths[i]} chars" for i in lengths
        ]

    # --------------------------------
    # KEYWORD EMPHASIS DIFFERENCES
    # --------------------------------
    keywords = ["pollution", "AQI", "PM2.5", "health", "government",
                "traffic", "industry", "weather"]

    emphasis = {}
    for idx, txt in enumerate(texts):
        lower = txt.lower()
        emphasis[idx] = [kw for kw in keywords if kw.lower() in lower]

    if len(set([tuple(v) for v in emphasis.values()])) > 1:
        out["Keyword Emphasis Differences"] = emphasis

    # --------------------------------
    # ENSURE SOMETHING IS RETURNED
    # --------------------------------
    if (
        not out["Title Differences"]
        and not out["Publication Date Differences"]
        and not out["Content Length Differences"]
        and not out["Keyword Emphasis Differences"]
    ):
        out["note"] = "Articles appear broadly consistent. No large cross-article discrepancies detected."

    return out
