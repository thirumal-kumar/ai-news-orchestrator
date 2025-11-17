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

st.set_page_config(
    page_title="AI News Orchestrator — GUVI Edition",
    layout="wide",
    page_icon="📰"
)

# Sidebar
with st.sidebar:
    st.header("Configuration")

    query = st.text_input("Topic", value="AI news")
    news_key = st.text_input("NewsAPI Key (optional)", type="password")
    max_articles = st.slider("Max articles", min_value=4, max_value=16, value=8)
    use_llm = st.checkbox("Use AI for Timeline Inference", value=True)

    if st.button("Fetch & Analyze"):
        st.session_state["run"] = True
        st.session_state["query"] = query
        st.session_state["news_key"] = news_key
        st.session_state["max_articles"] = max_articles
        st.session_state["use_llm"] = use_llm

# Run when user clicks button
if "run" in st.session_state:

    query = st.session_state["query"]
    news_key = st.session_state["news_key"]
    max_articles = st.session_state["max_articles"]
    use_llm = st.session_state["use_llm"]

    st.title("📰 AI News Orchestrator — GUVI Edition")

    st.info("Fetching articles...")

    articles = fetch_articles(query, news_key, max_articles)

    st.success(f"Fetched {len(articles)} articles.")

    # Clean content
    cleaned = []
    for a in articles:
        cleaned.append({
            "title": a.get("title"),
            "url": a.get("url"),
            "source": a.get("source"),
            "published_at": a.get("published_at"),
            "cleaned_text": clean_article(a.get("url"))
        })

    # Build tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📌 Summary", "⏱ Timeline", "🔍 Entities", "⚠ Discrepancies", "📰 Articles", "⭐ Credibility"]
    )

    # ---------------- TAB 1: SUMMARY ----------------
    with tab1:
        st.subheader("Combined Summary")
        snippets = [c["cleaned_text"] for c in cleaned]
        combined = combine_snippets(snippets)
        st.write(combined)

    # ---------------- TAB 2: TIMELINE ----------------
    with tab2:
        st.subheader("AI-Inferred Timeline of Events")

        timeline = build_timeline_from_cleaned(cleaned, use_llm)
        
        if timeline:
            df = px.data.gapminder().query("year==2007").head(1)  # dummy to avoid crash
            dates = [t["date"] for t in timeline]
            titles = [t["event"] for t in timeline]
            fig = px.scatter(x=dates, y=[1] * len(dates), text=titles)
            st.plotly_chart(fig, use_container_width=True)

            # Detail list
            for t in timeline:
                st.markdown(f"**{t['date']}** — {t['event']}")
                st.write("Sources:", t.get("sources"))
                st.write("---")
        else:
            st.warning("No timeline events detected.")

    # ---------------- TAB 3: ENTITIES ----------------
    with tab3:
        st.subheader("Extracted Key Entities")
        entities = extract_entities(cleaned)
        st.json(entities)

    # ---------------- TAB 4: DISCREPANCIES ----------------
    with tab4:
        st.subheader("Detected Discrepancies Across Articles")
        disc = find_discrepancies(
            [extract_events_from_text(c["cleaned_text"]) for c in cleaned]
        )
        st.json(disc)

    # ---------------- TAB 5: ARTICLES ----------------
    with tab5:
        st.subheader("Articles (detailed)")
        for a in cleaned:
            st.markdown(f"### {a['title']}")
            st.write(f"Source: {a['source']}")
            st.write(f"Published: {a['published_at']}")
            st.write(a["cleaned_text"][:600] + "...")
            st.markdown(f"[Open original]({a['url']})")
            st.write("---")

    # ---------------- TAB 6: CREDIBILITY ----------------
    with tab6:
        st.subheader("Credibility Score by Source")

        # take only URLs and extract domain correctly
        domains = [
            domain_from_url(a.get("url", ""))
            for a in cleaned
            if isinstance(a, dict)
        ]

        scores = score_sources(domains)

        st.json(scores)
