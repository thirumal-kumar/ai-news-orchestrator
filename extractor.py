# extractor.py
import requests
from bs4 import BeautifulSoup
from typing import Dict
import re

def extract_raw_html(url: str, timeout=12):
    if not url:
        return ""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsOrchestrator/1.0)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def clean_html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # Try <article> first
    article = soup.find("article")
    text = ""
    if article:
        ps = article.find_all("p")
        text = "\n\n".join(p.get_text().strip() for p in ps if p.get_text().strip())
    else:
        # fallback: collect largest continuous paragraph blocks
        ps = soup.find_all("p")
        text = "\n\n".join(p.get_text().strip() for p in ps if p.get_text().strip())
    # minimal cleaning
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def clean_article(article_or_url) -> Dict:
    """
    Accept either article dict {'url':...} or url string.
    Return dict with at least 'raw_html' and 'cleaned_text'.
    """
    url = ""
    if isinstance(article_or_url, dict):
        url = article_or_url.get("url", "") or ""
    elif isinstance(article_or_url, str):
        url = article_or_url
    else:
        return {"raw_html": "", "cleaned_text": ""}

    if not url:
        return {"raw_html": "", "cleaned_text": ""}

    try:
        html = extract_raw_html(url)
        text = clean_html_to_text(html)
        return {"raw_html": html, "cleaned_text": text}
    except Exception:
        return {"raw_html": "", "cleaned_text": ""}
