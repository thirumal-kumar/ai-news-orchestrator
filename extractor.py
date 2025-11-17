"""
extractor.py
Extract clean article text using Newspaper3k + BeautifulSoup fallback.
"""

import os
import json
import hashlib
from typing import Dict, Optional

from bs4 import BeautifulSoup
from newspaper import Article

DATA_CLEAN_DIR = os.path.join("data", "cleaned")
os.makedirs(DATA_CLEAN_DIR, exist_ok=True)


def _save_cleaned(article_id: str, content: str) -> str:
    path = os.path.join(DATA_CLEAN_DIR, f"{article_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _extract_with_newspaper(url: str) -> Optional[str]:
    try:
        art = Article(url)
        art.download()
        art.parse()
        return art.text
    except Exception:
        return None


def _clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ")


def clean_article(raw_article: Dict) -> Dict:
    url = raw_article.get("url") or ""
    raw_content = raw_article.get("content") or raw_article.get("summary") or ""

    key = (url + raw_article.get("title", "")).encode("utf-8")
    article_id = hashlib.sha256(key).hexdigest()[:16]

    cleaned_text = None

    if url.startswith("http"):
        cleaned_text = _extract_with_newspaper(url)

    if not cleaned_text:
        cleaned_text = _clean_html(raw_content)

    cleaned_path = _save_cleaned(article_id, cleaned_text)

    return {
        "id": article_id,
        "title": raw_article.get("title"),
        "url": raw_article.get("url"),
        "published_at": raw_article.get("published_at"),
        "cleaned_text": cleaned_text,
        "cleaned_path": cleaned_path,
        "source": raw_article.get("source"),
    }
