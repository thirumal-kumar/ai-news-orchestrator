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

st.set_page_config(
    page_title="AI News Orchestrator — GUVI Edition",
    layout="wide",
    page_icon="📰"
)

# ============================================================
# SIDEBAR CONFIG
# ============================================================

st.sidebar.title("Configuration")

query = st.sidebar.text_input("Topic", value="Delhi air pollution")
news_key = st.sidebar.text_input("NewsAPI Key (optional)", type="password")

max_articles = st.sidebar.slider("Max articles", 1, 20, 8)

use_llm = st.sidebar.checkbox("Use AI for Timeline Inference", value=True)

if st.sidebar.button("Fetch & Analyze"):
    st.info("Fetching articles...")

    articles = fetch_articles(query, news_key, max_articles)
    st.success(f"Fetched {len(articles)} articles.")

    # ============================================================
    # CLEAN RAW HTML
    # ============================================================

    cleaned = []
    for a in articles:
        if not isinstance(a, dict):
            continue

        url = a.get("url", "")
        pub = a.get("published_at", "")
        src = a.get("source", "Unknown")
        summary = a.get("summary", "")

        cleaned.append({
            "title": a.get("title", ""),
            "url": url,
            "published_at": pub,
            "source": src,
            "summary": summary,
            "cleaned_text": clean_article(url)
        })

    # ============================================================
    # TABS
    # ============================================================

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📌 Summary", "⏱ Timeline", "🔍 Entities",
         "⚠ Discrepancies", "📰 Articles", "⭐ Credibility"]
    )

    # ============================================================
    # TAB 1 — SUMMARY
    # ============================================================

    with tab1:
        summary = combine_snippets([c["cleaned_text"] for c in cleaned])
        st.subheader("Combined Summary")
        st.write(summary)

    # ============================================================
    # TAB 2 — TIMELINE
    # ============================================================

    with tab2:
        st.subheader("AI-Inferred Timeline of Events")

        timeline = build_timeline_from_cleaned(cleaned, use_llm=use_llm)

        if not timeline:
            st.warning("No timeline events extracted.")
        else:
            dates = [t["date_iso"] for t in timeline if t["date_iso"]]
            titles = [t["event"] for t in timeline if t["event"]]

            if dates:
                fig = px.scatter(x=dates, y=[1]*len(dates),
                                 hover_name=titles, labels={"x": "date", "y": ""})
                st.plotly_chart(fig, use_container_width=True)

            for t in timeline:
                st.write(f"### {t['date']} — {t['event']}")
                for s in t["sources"]:
                    st.caption(f"Source: {s}")

    # ============================================================
    # TAB 3 — ENTITIES
    # ============================================================

    with tab3:
        st.subheader("Extracted Key Entities")
        entities = extract_entities([c["cleaned_text"] for c in cleaned])
        st.json(entities)

    # ============================================================
    # TAB 4 — DISCREPANCIES
    # ============================================================

    with tab4:
        st.subheader("Detected Discrepancies Across Articles")
        disc = find_discrepancies([c["cleaned_text"] for c in cleaned])
        st.json(disc)

    # ============================================================
    # TAB 5 — ARTICLE LIST
    # ============================================================

    with tab5:
        st.subheader("Articles (detailed)")
        for a in cleaned:
            st.write(f"### {a['title']}")
            st.write(f"Source: {a['source']}")
            st.write(f"Published: {a['published_at']}")
            st.write(f"Summary: {a['summary']}")
            st.markdown(f"[Open Source]({a['url']})")
            st.write("---")

    # ============================================================
    # TAB 6 — CREDIBILITY SCORE
    # ============================================================

    with tab6:
        st.subheader("Credibility Score by Source")

        domains = [domain_from_url(a["url"]) for a in cleaned if isinstance(a, dict)]
        scores = score_sources(domains)

        st.json(scores)
