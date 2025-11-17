from collections import Counter
from urllib.parse import urlparse


def domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return "unknown"


def score_sources(domain_list):
    """Input is now a list of strings (domains)."""
    freq = Counter(domain_list)
    scores = {}

    total = sum(freq.values()) or 1
    for d, c in freq.items():
        scores[d] = round(c / total, 2)

    return scores
