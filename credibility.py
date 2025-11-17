# credibility.py
from collections import Counter
from urllib.parse import urlparse

def domain_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        return p.netloc.replace("www.", "")
    except Exception:
        return ""

def score_sources(article_list):
    """
    Accepts article_list: list of dicts (data model).
    Returns dict domain -> score (0..100).
    """
    domains = []
    for a in article_list:
        if isinstance(a, dict):
            domains.append(domain_from_url(a.get("url", "") or ""))
        elif isinstance(a, str):
            domains.append(domain_from_url(a))
    freq = Counter(d for d in domains if d)
    scores = {}
    for d, c in freq.items():
        # simple heuristic: large frequency -> more coverage (score up to 80)
        score = min(80, 20 + c * 5)
        # penalize suspicious TLDs (very simple)
        if d.endswith(".xyz") or d.endswith(".ru"):
            score = max(10, score - 30)
        scores[d] = score
    return scores
