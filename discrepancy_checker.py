# discrepancy_checker.py
from typing import List, Dict
import re
from collections import defaultdict

def _extract_numbers_from_text(s: str):
    nums = re.findall(r"\b\d{1,4}(?:,\d{3})*(?:\.\d+)?\b", s)
    return [n.replace(",", "") for n in nums]

def find_discrepancies(events_per_article: List[List[Dict]]) -> List[Dict]:
    """
    events_per_article: list of lists (events extracted per article)
    Return list of discrepancy objects.
    """
    # flatten events to compare sentences and numeric claims
    flat = []
    for ai, events in enumerate(events_per_article):
        for ev in events:
            flat.append((ai, ev))
    discrepancies = []
    # simple pairwise numeric mismatch detector
    for i in range(len(flat)):
        ai, e1 = flat[i]
        s1 = e1.get("sentence", "") if isinstance(e1, dict) else str(e1)
        n1 = _extract_numbers_from_text(s1)
        for j in range(i+1, len(flat)):
            aj, e2 = flat[j]
            s2 = e2.get("sentence", "") if isinstance(e2, dict) else str(e2)
            n2 = _extract_numbers_from_text(s2)
            if n1 and n2 and set(n1) != set(n2):
                discrepancies.append({
                    "a_article": ai,
                    "b_article": aj,
                    "sent_a": s1,
                    "sent_b": s2,
                    "numbers_a": n1,
                    "numbers_b": n2,
                    "similarity": None
                })
    return discrepancies
