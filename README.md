# 📰 AI News Orchestrator — Advanced Version  
*A smart multi-source news analyzer with AI-powered timelines, discrepancies, entity extraction, and credibility scoring.*

![Banner](https://i.imgur.com/zCcG5xA.png)

---

## 🚀 Overview
AI News Orchestrator is an advanced, AI-driven platform that:
- Aggregates breaking news from multiple free sources
- Extracts clean text from articles
- Generates a combined summary
- Reconstructs timelines using AI
- Detects conflicting claims between sources
- Extracts key entities (ORG, GPE, DATE, PERSON)
- Scores credibility based on domain reliability
- Provides an interactive UI built with Streamlit

This is a fully working, deployable project with **zero paid APIs required**.

---

## ✨ Features
### 🔍 1. Multi-Source News Aggregation
- Google News RSS
- NewsAPI (optional)
- Deduplication
- Automatic fallback

### 🧠 2. AI Combined Summary
- Unified summary across articles
- Noise-free and ad-free clean text

### 🕒 3. AI-Inferred Event Timeline
- NLP + regex based date extraction
- AI-based inference for missing dates
- Chronologically ordered timeline
- Interactive Plotly visualization

### 🧩 4. Discrepancy Detection
- Detects conflicting numerical and factual claims
- Side-by-side comparison of mismatches

### 🔎 5. Key Entity Extraction
- Extracts ORG, GPE, DATE, PERSON entities
- Clean, structured JSON-style output

### ⭐ 6. Credibility Scoring
- Lightweight domain-based reliability scoring

### 📰 7. Article Viewer
- Clean text display
- Metadata (source, publish date)
- Link to original article

---

## 🗂 Project Structure
```
ai-news-orchestrator/
│ app.py
│ fetcher.py
│ extractor.py
│ entity_extractor.py
│ event_extractor.py
│ combined_summary.py
│ timeline_builder.py
│ discrepancy_checker.py
│ credibility.py
│ requirements.txt
│ README.md
└── .streamlit/
       secrets.toml  (should NOT be committed)
```

---

## 🔧 Installation
### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-news-orchestrator.git
cd ai-news-orchestrator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add API keys
Create the following file:
```
.streamlit/secrets.toml
```
Add:
```
NEWSAPI_KEY = "your_newsapi_key"
OPENROUTER_API_KEY = "your_openrouter_key"
```

### 4. Run locally
```bash
streamlit run app.py
```

---

## 🌐 Deploy on Streamlit Cloud
1. Push repo to GitHub
2. Go to https://share.streamlit.io
3. Select your repo
4. Choose `app.py`
5. Add secrets under **App → Settings → Secrets**:
```
NEWSAPI_KEY = "your_newsapi_key"
OPENROUTER_API_KEY = "your_openrouter_key"
```
6. Deploy 🎉

---

## 🛠 Tech Stack
| Component | Technology |
|----------|------------|
| Frontend | Streamlit |
| Summaries | OpenRouter (LLMs) |
| News Sources | Google RSS + NewsAPI |
| NLP Processing | spaCy, regex, heuristics |
| Visualization | Plotly |
| Backend | Python |

---

## 📌 Future Enhancements
- Sentiment + bias detection
- Multi-language summarization
- Voice-enabled summaries
- PDF exporters
- Source reliability history

---

## 📜 License
MIT License. Free to use and modify.

---

## 🙌 Acknowledgments
Built with:
- Streamlit
- BeautifulSoup
- spaCy
- Plotly
- OpenRouter
- NewsAPI