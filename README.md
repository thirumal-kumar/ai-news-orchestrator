# 📰 AI News Orchestrator (Free Version)

A fully free, Windows-friendly news analysis engine that:
- Fetches news from RSS + optional NewsAPI free tier
- Extracts readable article text via Newspaper3k + BeautifulSoup
- Summarizes using OpenRouter free models (no payment needed)
- Builds a chronological timeline of events
- Displays results in a clean Streamlit UI

---

## 🚀 Features
- Free LLM summarization via OpenRouter (`deepseek/deepseek-r1:free`)
- Configurable RSS feed list (BBC, Reuters, Guardian by default)
- Date extraction and ordered timeline generation
- Saves raw and cleaned articles locally
- Zero paid APIs required

---

## 🛠 Installation (Windows 11)

1. Install Python 3.10 or higher  
2. Clone or create project folder  
3. Install requirements:

```bash
pip install -r requirements.txt
