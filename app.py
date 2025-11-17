# app.py
import streamlit as st
from fetcher import fetch_articles
from extractor import clean_article
from combined_summary import combine_snippets
from entity_extractor import extract_entities
from timeline_builder import build_timeline_from_cleaned
from discrepancy_checker import find_discrepancies
from credibility import score_sources, domain_from_url
from summarizer import summarize_text
import json

st.set_page_config(page_title="AI News Orchestrator — GUVI Edition", layout="wide")

st.title("📰 AI News Orchestrator — GUVI Edition")

with st.sidebar:
    st.subheader("Configuration")
    topic = st.text_input("Topic", value="Delhi air pollution")
    news_key = st.text_input("NewsAPI Key (optional)", type="password")
    max_articles = st.slider("Max articles", min_value=2, max_value=12, value=8)
    use_llm_timeline = st.checkbox("Use AI for Timeline Inference", value=True)
    if st.button("Fetch & Analyze"):
        st.session_state["run"] = True

if not st.session_state.get("run"):
    st.info("Click 'Fetch & Analyze' in the sidebar to begin.")
    st.stop()

st.info("Fetching articles...")

articles = fetch_articles(topic, max_articles)

st.success(f"Fetched {len(articles)} articles.")

if not articles:
    st.warning("No articles found for the query.")
    st.stop()

# Clean articles
cleaned = []
for a in articles:
    cleaned_text = clean_article(a).get("cleaned_text", "")
    cleaned.append({
        "title": a.get("title", ""),
        "url": a.get("url", ""),
        "source": a.get("source", ""),
        "published_at": a.get("published_at", ""),
        "cleaned_text": cleaned_text
    })

# Summary
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📌 Summary", "🕒 Timeline", "🔎 Entities", "⚠️ Discrepancies", "📄 Articles", "⭐ Credibility"])

with tab1:
    st.header("Unified AI Summary")
    combined = combine_snippets(cleaned)
    if combined:
        st.write(combined)
    else:
        st.warning("No article content found to summarize.")

with tab2:
    st.header("AI-Inferred Timeline of Events")
    timeline = build_timeline_from_cleaned(cleaned, use_llm=use_llm_timeline)
    if timeline:
        for ev in timeline:
            st.markdown(f"**{ev.get('date_iso') or 'Undated'}** — {ev.get('sentence')}")
            sources = ev.get("sources") or []
            if sources:
                st.write("Sources:", ", ".join(sources))
    else:
        st.info("No timeline events found.")

with tab3:
    st.header("Extracted Key Entities")
    all_ents = {}
    for a in cleaned:
        ents = extract_entities(a.get("cleaned_text",""))
        for k,v in ents.items():
            all_ents.setdefault(k, []).extend(v)
    # dedupe
    for k in list(all_ents.keys()):
        all_ents[k] = list(dict.fromkeys([x for x in all_ents[k] if x]))
    st.json(all_ents)

with tab4:
    st.header("Detected Discrepancies Across Articles")
    events_per_article = [build_timeline_from_cleaned([c], use_llm=False) for c in cleaned]
    disc = find_discrepancies(events_per_article)
    if disc:
        st.json(disc)
    else:
        st.info("No numeric discrepancies detected.")

with tab5:
    st.header("Articles (detailed)")
    for a in cleaned:
        st.subheader(a.get("title"))
        st.write("Source:", a.get("source"))
        st.write("Published:", a.get("published_at"))
        st.write("Open original:", a.get("url"))
        st.write("---")

with tab6:
    st.header("Credibility Score by Source")
    domains = [domain_from_url(a.get("url","")) for a in cleaned]
    scores = score_sources(domains)
    st.json(scores)
