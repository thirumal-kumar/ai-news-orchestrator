# extractor.py
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

def extract_raw_html(url, timeout=10):
    if not url or not isinstance(url, str):
        return None
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return r.text
    except RequestException:
        return None

def _html_to_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    # remove scripts/styles
    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.decompose()
    # prefer <article>
    article = soup.find("article")
    text_source = article or soup.body or soup
    texts = [t.strip() for t in text_source.stripped_strings]
    return " ".join(texts)

def clean_article(article: dict) -> dict:
    """
    article: dict with at least 'url' field (per data model)
    returns same dict with 'raw_html' and 'cleaned_text' added (or empty string)
    """
    if not isinstance(article, dict):
        raise TypeError("clean_article expects a dict article")
    url = article.get("url") or ""
    html = extract_raw_html(url)
    if html:
        article["raw_html"] = html
        article["cleaned_text"] = _html_to_text(html)
    else:
        article["raw_html"] = ""
        article["cleaned_text"] = ""
    return article
