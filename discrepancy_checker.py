# discrepancy_checker.py
"""
Discrepancy checker:
- For each pair of article event sentences, compute simple similarity.
- Flag pairs where the overlap is low but they refer to same subject (heuristic)
- Detect numeric or date mismatches using regex/dateparser
"""

import re
from difflib import SequenceMatcher
from typing import List, Dict
import dateparser


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _find_first_date(text: str):
    dt = dateparser.parse(text, settings={"PREFER_DATES_FROM": "past"})
    return dt


def _extract_numbers(text: str):
    return re.findall(r"\d{1,4}(?:\.\d+)?", text)


def find_discrepancies(events_per_article: List[List[Dict]]) -> List[Dict]:
    """
    events_per_article: list where each element is the list of events (dicts) for an article
    returns list of discrepancies: {a_idx, b_idx, sent_a, sent_b, similarity, date_a, date_b, numbers_a, numbers_b}
    """
    discrepancies = []
    # flatten with article index and event idx
    flat = []
    for ai, evs in enumerate(events_per_article):
        for ei, ev in enumerate(evs):
            flat.append((ai, ei, ev))

    N = len(flat)
    for i in range(N):
        ai, ei, e1 = flat[i]
        s1 = e1.get("sentence", "")
        d1 = _find_first_date(s1)
        nums1 = _extract_numbers(s1)

        for j in range(i+1, N):
            aj, ej, e2 = flat[j]
            s2 = e2.get("sentence", "")
            d2 = _find_first_date(s2)
            nums2 = _extract_numbers(s2)

            sim = _similar(s1, s2)
            # If similarity < 0.5 but they mention same key entities (heuristic), mark as discrepancy
            if sim < 0.5:
                # numeric mismatch detection
                if nums1 and nums2 and nums1 != nums2:
                    discrepancies.append({
                        "a_article": ai, "a_event": ei, "b_article": aj, "b_event": ej,
                        "sent_a": s1, "sent_b": s2, "similarity": sim,
                        "date_a": d1 and d1.isoformat(), "date_b": d2 and d2.isoformat(),
                        "numbers_a": nums1, "numbers_b": nums2
                    })
                # date mismatch
                elif d1 and d2 and d1.date() != d2.date() and sim < 0.6:
                    discrepancies.append({
                        "a_article": ai, "a_event": ei, "b_article": aj, "b_event": ej,
                        "sent_a": s1, "sent_b": s2, "similarity": sim,
                        "date_a": d1.date().isoformat(), "date_b": d2.date().isoformat(),
                        "numbers_a": nums1, "numbers_b": nums2
                    })
    return discrepancies
