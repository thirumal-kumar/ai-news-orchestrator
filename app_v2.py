# app_v2.py
import streamlit as st
import pandas as pd
import plotly.express as px
from fetcher import fetch_articles
from extractor import clean_article
from combined_summary import combine_snippets
from timeline_builder import build_timeline_from_cleaned
from entity_extractor import extract_entities
from discrepancy_checker import find_discrepancies
from credibility import score_sources, domain_from_url


st.set_page_config(layout="wide", page_title="AI News Orchestrator (Fixed)")

st.title("📰 AI News Orchestrator — Final Fixed Version")

query = st.text_input("Topic", "Delhi air pollution")
newsapi = st.text_input("NewsAPI Key (optional)", type="password")
max_articles = st.slider("Max articles", 4, 12, 8)
use_llm = st.checkbox("Use LLM for timeline", True)

if st.button("Fetch & Analyze"):
    st.info("Fetching articles...")
    articles = fetch_articles(query, max_results=max_articles, newsapi_key=newsapi)

    st.success(f"Fetched {len(articles)} articles.")

    # CLEAN ARTICLES
    cleaned = [clean_article(a) for a in articles]

    # --- Combined Summary ---
    st.header("Combined Summary")
    snippets = []
    for c in cleaned:
        txt = c.get("cleaned_text") or ""
        if txt:
            snippets.append((c.get("title") or "") + " " + txt[:300])
    st.write(combine_snippets(snippets))

    # --- Entities ---
    st.header("Key Entities")
    all_ents = {}
    for c in cleaned:
        ents = extract_entities(c["cleaned_text"])
        for k, v in ents.items():
            all_ents.setdefault(k, set()).update(v)
    st.json({k: list(v)[:10] for k, v in all_ents.items()})

    # --- Timeline ---
    st.header("Event Timeline (AI-Inferred)")
    timeline = build_timeline_from_cleaned(cleaned, use_llm=use_llm)

    dated = [t for t in timeline if t["date"]]
    if dated:
        df = pd.DataFrame([{"date": t["date"], "summary": t["summary"]} for t in dated])
        fig = px.scatter(df, x="date", y=[1]*len(df), hover_data=["summary"])
        fig.update_yaxes(visible=False)
        st.plotly_chart(fig, use_container_width=True)

    for t in timeline:
        st.markdown(f"**{t['date_iso'] or 'Undated'}** — {t['summary']}")
        st.caption(f"Sources: {', '.join(t['sources'])}")
        st.write("---")

    # --- Discrepancies ---
    st.header("Discrepancies")
    evs = [extract_entities(c["cleaned_text"]) for c in cleaned]
    disc = find_discrepancies([extract_entities(c["cleaned_text"]) for c in cleaned])
    st.json(disc)

    # --- Credibility ---
    st.header("Credibility Scores")
    st.json(score_sources(articles))

    # --- Articles ---
    st.header("Articles (Details)")
    for c in cleaned:
        st.subheader(c.get("title"))
        st.write(f"**Source:** {domain_from_url(c.get('url'))}")
        st.write(f"**Published:** {c.get('published_at')}")
        st.write((c.get("cleaned_text") or "")[:500])
        st.write(f"[Open]({c.get('url')})")
        st.write("---")
