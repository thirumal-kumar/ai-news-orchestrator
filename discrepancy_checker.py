import re
from difflib import SequenceMatcher
from typing import List, Dict, Any


# Helper: extract numbers from text
def _extract_numbers(text: str):
    return re.findall(r"\d+", text)


# Helper: extract first date-like token
def _find_first_date(text: str):
    m = re.search(r"\b(?:\d{4}|\d{1,2}\s+\w+|\w+\s+\d{1,2})\b", text)
    return m.group(0) if m else None


def _similarity(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()


def _normalize_entry(e):
    """
    Accepts either:
        - "string"
        - {"sentence": "...", "date": "..."}
    Converts to uniform format.
    """
    if isinstance(e, str):
        return {"sentence": e, "date": None}
    if isinstance(e, dict):
        return {
            "sentence": e.get("sentence", ""),
            "date": e.get("date"),
        }
    # fallback
    return {"sentence": str(e), "date": None}


def find_discrepancies(entries: List[Any]) -> List[Dict[str, Any]]:
    """
    entries = list of cleaned article texts (strings)
              OR list of event dicts ({sentence:..., date:...})

    Output: list of discrepancy records.
    """

    # Normalize all inputs
    normalized = [_normalize_entry(e) for e in entries]

    flat = []
    for idx, e in enumerate(normalized):
        s = e["sentence"]
        d = _find_first_date(s)
        nums = _extract_numbers(s)
        flat.append((idx, 0, {"sentence": s, "date": d, "numbers": nums}))

    discrepancies = []

    N = len(flat)
    for i in range(N):
        ai, _, e1 = flat[i]
        s1 = e1["sentence"]
        d1 = e1["date"]
        nums1 = e1["numbers"]

        for j in range(i + 1, N):
            bi, _, e2 = flat[j]
            s2 = e2["sentence"]
            d2 = e2["date"]
            nums2 = e2["numbers"]

            sim = _similarity(s1, s2)

            # If sentences differ significantly but talk same topic
            if sim < 0.55:
                if nums1 != nums2 or d1 != d2:
                    discrepancies.append({
                        "a_article": ai,
                        "b_article": bi,
                        "sent_a": s1,
                        "sent_b": s2,
                        "similarity": sim,
                        "date_a": d1,
                        "date_b": d2,
                        "numbers_a": nums1,
                        "numbers_b": nums2,
                    })

    return discrepancies
