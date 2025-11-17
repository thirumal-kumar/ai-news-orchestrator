# credibility.py
"""
Simple credibility heuristic:
- Known reputable domains get higher base score
- If domain is repeated across many articles => higher trust
- If domain is unknown, neutral score
This is intentionally simple; you can extend using external trust databases.
"""

from collections import Counter
from urllib.parse import urlparse

# Small curated domain trust map (expandable)
TRUSTED_DOMAINS = {
    "reuters.com": 0.95,
    "bbc.co.uk": 0.92,
    "bbc.com": 0.92,
    "nytimes.com": 0.93,
    "theguardian.com": 0.9,
    "indianexpress.com": 0.82,
    "livemint.com": 0.80,
    "ndtv.com": 0.78,
    "timesofindia.indiatimes.com": 0.75,
}

def domain_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        return p.netloc.replace("www.", "")
    except:
        return ""

def score_sources(article_list):
    # article_list: list of dicts with 'url', 'source' fields
    domains = [domain_from_url(a.get("url") or "") for a in article_list]
    freq = Counter(domains)
    scores = {}
    for d in set(domains):
        base = TRUSTED_DOMAINS.get(d, 0.5)
        # boost if domain appears multiple times
        boost = min(0.2, 0.02 * freq.get(d, 1))
        scores[d] = round(base + boost, 3)
    return scores
