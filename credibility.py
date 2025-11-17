# credibility.py
from collections import Counter
from urllib.parse import urlparse
from typing import List, Dict

def domain_from_url(url: str) -> str:
    try:
        p = urlparse(url)
        return p.netloc.replace("www.", "") or url
    except Exception:
        return url

# simple credibility map (extend as needed)
TRUSTED = {
    "bbc.co.uk": 0.9, "bbc.com": 0.9, "reuters.com": 0.9, "thehindu.com": 0.8, "hindustantimes.com": 0.75,
    "timesofindia.indiatimes.com": 0.7, "ndtv.com": 0.7
}

def score_sources(article_list: List[Dict]) -> Dict[str, float]:
    domains = [domain_from_url(a if isinstance(a, str) else a.get("url","")) for a in article_list]
    freq = Counter(domains)
    scores = {}
    for d in set(domains):
        base = TRUSTED.get(d, 0.6)
        scores[d] = round(base, 2)
    return scores
