import streamlit as st
import plotly.express as px
import os

# -------------------------------
# IMPORT PROJECT MODULES
# -------------------------------
from fetcher import fetch_articles
from extractor import clean_article
from combined_summary import combine_snippets
from entity_extractor import extract_entities
from timeline_builder import build_timeline_from_cleaned
from discrepancy_checker import find_discrepancies
from credibility import score_sources, domain_from_url
from event_extractor import extract_events_from_text


# -------------------------------
# STREAMLIT PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI News Orchestrator — GUVI Edition",
    layout="wide",
    page_icon="📰"
)


# -------------------------------
# SIDEBAR CONFIGURATION
# -------------------------------
st.sidebar.header("Configuration")

topic = st.sidebar.text_input("Topic", "Delhi air pollution")
news_api_key = st.sidebar.text_input("NewsAPI Key (optional)", type="password")

max_articles = st.sidebar.slider("Max articles", 3, 20, 8)
use_llm = st.sidebar.checkbox("Use AI for Timeline Inference", value=True)

go = st.sidebar.button("Fetch & Analyze")


# -------------------------------
# MAIN UI HEADER
# -------------------------------
st.title("📰 AI News Orchestrator — GUVI Edition")


# -------------------------------
# WHEN USER CLICKS FETCH
# -------------------------------
if go:

    st.info("Fetching articles...")

    # 1) FETCH ARTICLES
    articles = fetch_articles(topic, max_articles, news_api_key)

    st.success(f"Fetched {len(articles)} articles.")

    # CLEAN ARTICLES
    cleaned = []
    for a in articles:
        processed = clean_article(a)
        cleaned.append(processed)

    # -------------------------------------
    # COMBINED SUMMARY (LLM)
    # -------------------------------------
    snippets = [c.get("cleaned_text", "") for c in cleaned]
    combined = combine_snippets(snippets)

    # TABS FOR OUTPUT
    tab_sum, tab_time, tab_ent, tab_disc, tab_art, tab_cred = st.tabs(
        ["✍ Summary", "⏱ Timeline", "🔍 Entities",
         "⚠ Discrepancies", "🗞 Articles", "⭐ Credibility"]
    )

    # -------------------------------------
    # SUMMARY TAB
    # -------------------------------------
    with tab_sum:
        st.subheader("Combined Summary")
        st.write(combined)

    # -------------------------------------
    # TIMELINE TAB
    # -------------------------------------
    with tab_time:
        st.subheader("AI-Inferred Timeline of Events")
        timeline = build_timeline_from_cleaned(cleaned, use_llm=use_llm)

        if not timeline:
            st.warning("No timeline events extracted.")
        else:
            # PLOT
            dates = [t["date"] for t in timeline]
            labels = [t["summary"][:50] for t in timeline]

            fig = px.scatter(
                x=dates,
                y=[1] * len(dates),
                hover_name=labels,
                labels={"x": "Date", "y": ""},
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

            # DETAILED EVENTS
            for ev in timeline:
                st.markdown(
                    f"**{ev['date']}** — {ev['summary']}\n\n"
                    f"Sources: {', '.join(ev['sources'])}"
                )
                st.markdown("---")

    # -------------------------------------
    # ENTITY TAB (FIXED VERSION)
    # -------------------------------------
    with tab_ent:
        st.subheader("Extracted Key Entities")

        all_entities = {"PERSON": set(), "ORG": set(), "GPE": set(), "DATE": set()}

        for art in cleaned:
            text = art.get("cleaned_text", "")
            ents = extract_entities(text)

            for key in all_entities:
                for item in ents.get(key, []):
                    if item and item.strip():
                        all_entities[key].add(item.strip())

        # Display
        st.json({k: sorted(list(v)) for k, v in all_entities.items()})

    # -------------------------------------
    # DISCREPANCIES TAB
    # -------------------------------------
    with tab_disc:
        st.subheader("Detected Discrepancies Across Articles")
        disc = find_discrepancies([c["cleaned_text"] for c in cleaned])

        if not disc:
            st.info("No discrepancies detected.")
        else:
            st.json(disc)

    # -------------------------------------
    # ARTICLES TAB
    # -------------------------------------
    with tab_art:
        st.subheader("Articles (detailed)")

        for art in cleaned:
            st.markdown(f"### {art.get('title', '')}")
            st.markdown(f"Source: {art.get('source', '')}")
            st.markdown(f"Published: {art.get('published_at', '')}")
            st.write(art.get("cleaned_text", ""))
            st.markdown(f"[Open original]({art.get('url', '')})")
            st.markdown("---")

    # -------------------------------------
    # CREDIBILITY TAB
    # -------------------------------------
    with tab_cred:
        st.subheader("Credibility Score by Source")

        domains = [domain_from_url(a.get("url", "")) for a in cleaned]
        scores = score_sources(domains)

        st.json(scores)
