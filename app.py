import streamlit as st
import plotly.express as px
from datetime import datetime

# -------------------------------
# IMPORT PROJECT MODULES
# -------------------------------
from fetcher import fetch_articles
from extractor import clean_article
from combined_summary import combine_snippets
from entity_extractor import extract_entities
from timeline_builder import build_timeline_from_cleaned
from credibility import score_sources
from discrepancy_checker import find_discrepancies   # if you have this file

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI News Orchestrator",
    layout="wide",
)

st.title("📰 AI News Orchestrator")

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
with st.sidebar:
    st.header("Search Settings")

    query = st.text_input("Enter topic", "Delhi air pollution")

    max_articles = st.number_input("Max Articles", min_value=5, max_value=50, value=20)

    # Load secure keys (NEVER store in repo)
    OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    NEWSAPI_KEY = st.secrets.get("NEWS_API_KEY", "")

    st.info("Keys loaded securely via Streamlit Secrets.")

# -------------------------------
# FETCH ARTICLES
# -------------------------------
st.subheader("Fetching articles...")

raw_articles = fetch_articles(query, NEWSAPI_KEY, max_articles)

if not raw_articles:
    st.error("No articles fetched. Try another query.")
    st.stop()

st.success(f"Fetched {len(raw_articles)} articles.")

# -------------------------------
# CLEAN ARTICLES (extract text)
# -------------------------------
cleaned = []
for article in raw_articles:
    try:
        cleaned_article = clean_article(article)  # returns dict with cleaned_text
        cleaned.append(cleaned_article)
    except Exception as e:
        st.warning(f"Extractor failed on {article.get('url')}: {e}")

if not cleaned:
    st.error("No articles could be cleaned.")
    st.stop()

# -------------------------------
# SUMMARY
# -------------------------------
summary_text = combine_snippets(cleaned)

# -------------------------------
# TIMELINE
# -------------------------------
timeline = build_timeline_from_cleaned(cleaned)

# -------------------------------
# ENTITIES
# -------------------------------
entities = extract_entities(cleaned)

# -------------------------------
# DISCREPANCIES (optional)
# -------------------------------
try:
    discrepancies = find_discrepancies(cleaned)
except:
    discrepancies = {}

# -------------------------------
# CREDIBILITY
# -------------------------------
credibility_scores = score_sources(cleaned)

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📌 Summary", "⏱ Timeline", "🔍 Entities", "⚠ Discrepancies", "📰 Articles", "⭐ Credibility"]
)

# -------------------------------
# TAB 1 — SUMMARY
# -------------------------------
with tab1:
    st.subheader("Consolidated Summary")
    st.write(summary_text)

# -------------------------------
# TAB 2 — TIMELINE
# -------------------------------
with tab2:
    st.subheader("Publication Timeline")
    st.json(timeline)

# -------------------------------
# TAB 3 — ENTITIES
# -------------------------------
with tab3:
    st.subheader("Named Entity Extraction")
    st.json(entities)

# -------------------------------
# TAB 4 — DISCREPANCIES
# -------------------------------
with tab4:
    st.subheader("Cross-Article Discrepancies")
    st.json(discrepancies)

# -------------------------------
# TAB 5 — ARTICLES
# -------------------------------
with tab5:
    st.subheader("Fetched Articles")
    st.json(cleaned)

# -------------------------------
# TAB 6 — CREDIBILITY
# -------------------------------
with tab6:
    st.subheader("Source Credibility Score")
    st.json(credibility_scores)

    # also plot bar chart
    if credibility_scores:
        df = {
            "domain": list(credibility_scores.keys()),
            "score": list(credibility_scores.values())
        }
        fig = px.bar(df, x="domain", y="score", title="Credibility by Source", width=900)
        st.plotly_chart(fig)
