# matcher/article_parser.py

import spacy
from langdetect import detect

nlp = spacy.load("en_core_web_sm")

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"

def extract_person_names(text: str) -> list:
    """
    Use spaCy to extract PERSON entities from the article text.
    Returns a list of lowercased names.
    """
    doc = nlp(text)
    return [ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON"]