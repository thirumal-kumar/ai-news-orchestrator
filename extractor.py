import os
from bs4 import BeautifulSoup
import requests
from typing import Optional


def extract_raw_html(url: str) -> Optional[str]:
    """Downloads raw HTML safely."""
    try:
        r = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


def clean_html_to_text(html: str) -> str:
    """Cleans HTML and extracts readable text using BeautifulSoup."""
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts, styles, ads
    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # Extract paragraphs
    texts = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if len(t) > 40:  # avoid garbage
            texts.append(t)

    if not texts:
        # fallback: all text
        return soup.get_text("\n", strip=True)

    return "\n\n".join(texts)


def clean_article(article: dict) -> dict:
    """Main extraction function."""
    url = article.get("url")
    html = extract_raw_html(url)
    if html:
        article["raw_html"] = html
        article["cleaned_text"] = clean_html_to_text(html)
    else:
        article["cleaned_text"] = ""

    return article
