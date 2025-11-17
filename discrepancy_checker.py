# discrepancy_checker.py

def safe_text(x):
    if not x:
        return ""
    if isinstance(x, dict):
        return x.get("cleaned_text", "") or ""
    return str(x)

def find_discrepancies(cleaned_articles):
    """
    Identify contradictions across article texts, titles, or published dates.
    cleaned_articles: list of dicts (from extractor + fetcher)
    Returns: dict summarizing possible discrepancies
    """

    discrepancies = {
        "conflicting_dates": [],
        "conflicting_titles": [],
        "textual_mismatch_pairs": []
    }

    # --------------------------
    # COLLECT FIELDS
    # --------------------------
    titles = []
    dates = []
    texts = []

    for art in cleaned_articles:
        titles.append(art.get("title") or "")
        dates.append(art.get("published_at") or "")
        texts.append(safe_text(art))

    # --------------------------
    # DATE CONTRADICTIONS
    # --------------------------
    unique_dates = set([d for d in dates if d])
    if len(unique_dates) > 1:
        discrepancies["conflicting_dates"] = list(unique_dates)

    # --------------------------
    # TITLE CONTRADICTIONS
    # --------------------------
    unique_titles = set([t.strip() for t in titles if t])
    if len(unique_titles) > 1:
        discrepancies["conflicting_titles"] = list(unique_titles)

    # --------------------------
    # TEXTUAL SIMILARITY CHECK
    # --------------------------
    # Very lightweight heuristic: length mismatch or keyword mismatch
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            t1, t2 = texts[i], texts[j]

            if not t1 or not t2:
                continue

            # Heuristic mismatch: texts differ by >70% length
            len1, len2 = len(t1), len(t2)
            length_ratio = abs(len1 - len2) / max(len1, len2)

            if length_ratio > 0.7:
                discrepancies["textual_mismatch_pairs"].append(
                    {
                        "article_1_title": titles[i],
                        "article_2_title": titles[j],
                        "reason": f"Large content mismatch ({length_ratio:.2f})"
                    }
                )

    return discrepancies
