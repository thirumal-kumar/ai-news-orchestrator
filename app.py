# app_v3.py
import streamlit as st
import pandas as pd
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


newsapi_key = os.getenv("NEWSAPI_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

# ----------------------------------
# Page Setup
# ----------------------------------
st.set_page_config(
    layout="wide",
    page_title="AI News Orchestrator — GUVI Project by Dr Thirumal",
)

st.title("📰 AI News Orchestrator — GUVI Project by Dr Thirumal")

st.sidebar.header("Configuration")
query = st.sidebar.text_input("Topic", "Delhi air pollution")
newsapi_key = st.sidebar.text_input("NewsAPI Key (optional)", type="password")
max_articles = st.sidebar.slider("Max articles", 4, 12, 8)
use_llm = st.sidebar.checkbox("Use AI for Timeline Inference", True)

run = st.sidebar.button("Fetch & Analyze")


# ----------------------------------
# Run Pipeline
# ----------------------------------
if run:
    st.info("Fetching articles...")
    articles = fetch_articles(query, max_results=max_articles, newsapi_key=newsapi_key)
    st.success(f"Fetched {len(articles)} articles.")

    cleaned = [clean_article(a) for a in articles]

    # Snippets for combined summary
    snippets = []
    for c in cleaned:
        txt = c.get("cleaned_text") or ""
        if txt:
            snippets.append((c.get("title") or "") + " " + txt[:300])

    # Entities (merged across articles)
    all_ents = {}
    for c in cleaned:
        ents = extract_entities(c.get("cleaned_text"))
        for k, v in ents.items():
            all_ents.setdefault(k, set()).update(v)

    # Timeline
    timeline = build_timeline_from_cleaned(cleaned, use_llm=use_llm)

    # Events for discrepancy detector
    events_per_article = [
        extract_events_from_text(c.get("cleaned_text") or "") for c in cleaned
    ]
    discrepancies = find_discrepancies(events_per_article)

    # Credibility Score
    credibility = score_sources(articles)


    # ----------------------------------
    # Tabs for cleaner UI
    # ----------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📌 Summary", "🕒 Timeline", "🔍 Entities", "⚠ Discrepancies", "📰 Articles", "⭐ Credibility"]
    )

    # ---------------- TAB 1: SUMMARY ----------------
    with tab1:
        st.subheader("Combined Summary")
        st.markdown("A clean merged summary across all news sources.")
        st.write(combine_snippets(snippets))

    # ---------------- TAB 2: TIMELINE ----------------
    with tab2:
        st.subheader("AI-Inferred Timeline of Events")

        dated = [t for t in timeline if t["date"]]
        if dated:
            df = pd.DataFrame(
                [{"date": t["date"], "summary": t["summary"]} for t in dated]
            )
            fig = px.scatter(
                df,
                x="date",
                y=[1]*len(df),
                hover_data=["summary"],
                labels={"y": ""},
                title="Event Timeline"
            )
            fig.update_yaxes(visible=False)
            st.plotly_chart(fig, use_container_width=True)

        for t in timeline:
            dt = t.get("date_iso") or "Undated"
            st.markdown(f"**{dt}** — {t['summary']}")
            st.caption("Sources: " + ", ".join(t["sources"]))
            st.write("---")

    # ---------------- TAB 3: ENTITIES ----------------
    with tab3:
        st.subheader("Extracted Key Entities")
        st.json({k: list(v)[:12] for k, v in all_ents.items()})

    # ---------------- TAB 4: DISCREPANCIES ----------------
    with tab4:
        st.subheader("Detected Discrepancies Across Articles")
        if not discrepancies:
            st.success("No major conflicting claims detected.")
        else:
            for d in discrepancies:
                st.json(d)

    # ---------------- TAB 5: ARTICLES ----------------
    with tab5:
        st.subheader("Fetched Articles (Detailed View)")
        for c in cleaned:
            st.markdown(f"### {c.get('title')}")
            st.write(f"**Source:** {domain_from_url(c.get('url'))}")
            st.write(f"**Published:** {c.get('published_at')}")
            st.write((c.get("cleaned_text") or "")[:500])
            st.markdown(f"[Open Original]({c.get('url')})")
            st.write("---")

    # ---------------- TAB 6: CREDIBILITY ----------------
    with tab6:
        st.subheader("Credibility Score by Source")
        st.json(credibility)
