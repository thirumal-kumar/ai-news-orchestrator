import streamlit as st
import plotly.express as px
import os

from fetcher import fetch_articles
from extractor import clean_article
from combined_summary import combine_snippets
from entity_extractor import extract_entities
from timeline_builder import build_timeline_from_cleaned
from discrepancy_checker import find_discrepancies
from credibility import score_sources, domain_from_url
from event_extractor import extract_events_from_text

st.set_page_config(page_title="AI News Orchestrator — GUVI Edition", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Configuration")

query = st.sidebar.text_input("Topic")
news_key = st.sidebar.text_input("NewsAPI Key (optional)", type="password")
max_articles = st.sidebar.slider("Max articles", 1, 20, 8)

use_llm = st.sidebar.checkbox("Use AI for Timeline Inference", True)
if st.sidebar.button("Fetch & Analyze"):
    st.session_state["fetch"] = True

if not st.session_state.get("fetch"):
    st.stop()

# -----------------------------
# Fetch Articles
# -----------------------------
st.info("Fetching articles...")
articles = fetch_articles(query, news_key, max_articles)
st.success(f"Fetched {len(articles)} articles.")

# -----------------------------
# Clean Articles
# -----------------------------
cleaned = []
for a in articles:
    if not isinstance(a, dict):
        continue
    cleaned.append({
        "title": a.get("title", ""),
        "url": a.get("url", ""),
        "source": a.get("source", ""),
        "published_at": a.get("published_at", None),
        "cleaned_text": clean_article(a)
    })

# Build Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📄 Summary", "🕒 Timeline", "🔍 Entities", "⚠️ Discrepancies", "📰 Articles", "⭐ Credibility"]
)

# ---------------- TAB 1: SUMMARY ----------------
with tab1:
    st.subheader("Unified AI Summary")

    snippet_texts = [a.get("cleaned_text", "") for a in cleaned if a.get("cleaned_text")]
    if not snippet_texts:
        st.warning("No article content found to summarize.")
    else:
        st.write(combine_snippets(snippet_texts))

# ---------------- TAB 2: TIMELINE ----------------
with tab2:
    st.subheader("AI-Inferred Timeline of Events")
    timeline = build_timeline_from_cleaned(cleaned, use_llm=use_llm)
    st.write(timeline)

# ---------------- TAB 3: ENTITIES ----------------
with tab3:
    st.subheader("Extracted Key Entities")
    all_ents = {}
    for a in cleaned:
        ents = extract_entities(a.get("cleaned_text", ""))
        for k, v in ents.items():
            all_ents.setdefault(k, []).extend(v)
    st.json(all_ents)

# ---------------- TAB 4: DISCREPANCIES ----------------
with tab4:
    st.subheader("Detected Discrepancies Across Articles")
    disc = find_discrepancies([extract_events_from_text(a.get("cleaned_text", "")) for a in cleaned])
    st.json(disc)

# ---------------- TAB 5: ARTICLES ----------------
with tab5:
    st.subheader("Fetched Articles")
    for a in cleaned:
        st.markdown(f"### [{a['title']}]({a['url']}) — *{a['source']}*")
        st.write(a["cleaned_text"])
        st.write("---")

# ---------------- TAB 6: CREDIBILITY ----------------
with tab6:
    st.subheader("Credibility Score by Source")

    domain_list = [domain_from_url(a.get("url", "")) for a in cleaned if isinstance(a, dict)]
    scores = score_sources(domain_list)
    st.json(scores)
