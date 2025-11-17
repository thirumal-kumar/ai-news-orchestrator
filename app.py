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

st.set_page_config(page_title="AI News Orchestrator", layout="wide")

st.title("📰 AI News Orchestrator — GUVI Edition")


# ---------------- CONFIGURATION SIDEBAR ----------------

with st.sidebar:
    st.header("Configuration")

    query = st.text_input("Topic", "Delhi air pollution")
    news_key = st.text_input("NewsAPI Key (optional)", type="password")
    max_articles = st.slider("Max articles", 1, 20, 8)
    use_llm = st.checkbox("Use AI for Timeline Inference", value=True)

    if st.button("Fetch & Analyze"):
        st.session_state["run"] = True


# ---------------- MAIN EXECUTION ----------------

if st.session_state.get("run"):

    # Fetching
    st.info("Fetching articles...")
    articles = fetch_articles(query, news_key, max_articles)
    st.success(f"Fetched {len(articles)} articles.")

    # ---------------- CLEAN ARTICLES ----------------
    cleaned = []
    for a in articles:
        cleaned_article = {
            "title": a.get("title", ""),
            "url": a.get("url", ""),
            "source": a.get("source", ""),
            "published_at": a.get("published_at", ""),
            "summary": a.get("summary", "")
        }

        # FIXED: Always pass dict → not URL string
        cleaned.append(clean_article(cleaned_article))

    # ---------------- TABS ----------------

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📌 Summary", "⏱ Timeline", "🔍 Entities", "⚠ Discrepancies", "📰 Articles", "⭐ Credibility"]
    )


    # ---------------- TAB 1: SUMMARY ----------------
    with tab1:
        st.subheader("Unified AI Summary")
        st.write(combine_snippets(cleaned))


    # ---------------- TAB 2: TIMELINE ----------------
    with tab2:
        st.subheader("AI-Inferred Timeline of Events")
        timeline = build_timeline_from_cleaned(cleaned, use_llm)
        st.json(timeline)


    # ---------------- TAB 3: ENTITIES ----------------
    with tab3:
        st.subheader("Extracted Key Entities")

        all_text = "\n".join([c.get("cleaned_text", "") for c in cleaned])
        ents = extract_entities(all_text)

        st.json(ents)


    # ---------------- TAB 4: DISCREPANCIES ----------------
    with tab4:
        st.subheader("Detected Discrepancies Across Articles")

        events_per_article = [
            extract_events_from_text(c.get("cleaned_text", "")) for c in cleaned
        ]

        disc = find_discrepancies(events_per_article)
        st.json(disc)


    # ---------------- TAB 5: RAW ARTICLES ----------------
    with tab5:
        st.subheader("Fetched Articles")

        for a in cleaned:
            st.markdown(f"### [{a['title']}]({a['url']})")
            st.write(f"**Source:** {a['source']}")
            st.write(f"**Published:** {a['published_at']}")
            st.write(a.get("summary", ""))
            st.write("---")


    # ---------------- TAB 6: CREDIBILITY ----------------
    with tab6:
        st.subheader("Credibility Score by Source")

        domains = [
            domain_from_url(a.get("url", "")) for a in cleaned
        ]

        scores = score_sources(domains)
        st.json(scores)
