from collections import Counter
from urllib.parse import urlparse


def domain_from_url(url: str) -> str:
    """Extract clean domain name from URL."""
    try:
        d = urlparse(url).netloc.lower().strip()
        return d.replace("www.", "") if d else ""
    except:
        return ""


def score_sources(domain_list):
    """
    Accepts: list of domain strings like ["bbc.com", "ndtv.com", ...]
    Returns: { "bbc.com": 0.33, "ndtv.com": 0.17, ... }
    """

    domain_list = [d for d in domain_list if d]  # remove blanks

    if not domain_list:
        return {}

    freq = Counter(domain_list)
    total = sum(freq.values())

    return {d: round(freq[d] / total, 2) for d in freq}
