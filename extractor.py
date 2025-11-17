import requests
from bs4 import BeautifulSoup


def extract_raw_html(url: str) -> str:
    try:
        if not url:
            return ""
        r = requests.get(url, timeout=8)
        return r.text
    except:
        return ""


def clean_article(article) -> str:
    """Convert article (dict or string) → cleaned text."""
    if not isinstance(article, dict):
        return ""

    url = article.get("url", "")
    html = extract_raw_html(url)

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(" ", strip=True)
    return text[:5000]
