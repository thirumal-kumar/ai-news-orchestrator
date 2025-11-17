import spacy
from collections import defaultdict

# Load Spacy model safely
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None


def extract_entities(cleaned_articles):
    """
    Extract PERSON, ORG, GPE, DATE entities from cleaned article text.
    cleaned_articles = list of dicts with 'cleaned_text'
    """

    if not nlp:
        return {"PERSON": [], "ORG": [], "GPE": [], "DATE": []}

    all_entities = defaultdict(list)

    for art in cleaned_articles:
        text = art.get("cleaned_text", "")
        if not text.strip():
            continue

        doc = nlp(text)

        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "DATE"]:
                all_entities[ent.label_].append(ent.text)

    # Deduplicate + sort
    return {label: sorted(set(values)) for label, values in all_entities.items()}
