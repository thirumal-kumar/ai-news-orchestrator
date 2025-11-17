# combined_summary.py
"""
Combine multiple article snippets into a single summary.
Removes repeated or near-duplicate lines.
"""

import re
from difflib import SequenceMatcher


def _similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def combine_snippets(snippets, similarity_threshold=0.75):
    """
    snippets: list of text blocks
    Returns a clean combined summary without duplicates.
    """
    cleaned = []

    for snip in snippets:
        # Remove double spaces, HTML, noise
        s = re.sub(r"\s+", " ", snip).strip()
        if len(s) < 40:
            continue

        # Deduplicate: skip if too similar to any existing line
        if any(_similar(s, c) > similarity_threshold for c in cleaned):
            continue

        cleaned.append(s)

    return "\n\n".join(cleaned)
