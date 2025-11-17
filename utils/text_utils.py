"""
text_utils.py
General helpers for text processing.
"""

import re


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, limit=300):
    return text[:limit] + "..." if len(text) > limit else text
