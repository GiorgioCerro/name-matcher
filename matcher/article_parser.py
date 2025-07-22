# matcher/article_parser.py - Improved version

import re
import spacy
from langchain_openai import OpenAI
from dotenv import load_dotenv
import ast

load_dotenv() 
llm = OpenAI()

# Try to load spacy model, fall back if not available
try:
    nlp = spacy.load("en_core_web_sm")
    USE_SPACY = True
except OSError:
    print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    USE_SPACY = False

def extract_names_spacy(text: str) -> set[str]:
    """Extract names using spaCy NER."""
    if not USE_SPACY:
        return set()
    
    doc = nlp(text)
    names = set()
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Clean and normalize the name
            name = re.sub(r'\s+', ' ', ent.text.strip())
            if len(name.split()) >= 2:  # At least first and last name
                names.add(name.lower())
    
    return names

def extract_names_regex(text: str) -> set[str]:
    """Extract potential names using regex patterns."""
    names = set()
    
    # Pattern for capitalized words (potential names)
    # Look for 2-4 consecutive capitalized words
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'
    matches = re.findall(pattern, text)
    
    for match in matches:
        # Filter out common non-name patterns
        words = match.split()
        if len(words) >= 2:
            # Skip if it contains common non-name words
            skip_words = {'The', 'This', 'That', 'When', 'Where', 'What', 'Why', 'How',
                         'Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'President', 'CEO', 'Inc', 'Ltd',
                         'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                         'January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December'}
            
            if not any(word in skip_words for word in words):
                names.add(match.lower())
    
    return names

def extract_person_names(text: str) -> list[str]:
    """
    Extract personal names using multiple methods with fallback.
    """
    if not text or not text.strip():
        return []
    
    names = set()
    
    # Method 1: spaCy NER (if available)
    if USE_SPACY:
        spacy_names = extract_names_spacy(text)
        names.update(spacy_names)
    
    # Method 2: Regex patterns
    regex_names = extract_names_regex(text)
    names.update(regex_names)
    
    # Method 3: LLM extraction (with better prompt and parsing)
    llm_names = extract_names_llm(text)
    names.update(llm_names)
    
    # Convert to list and return
    return list(names)

def extract_names_llm(text: str) -> set[str]:
    """Extract names using LLM with improved prompt and parsing."""
    
    prompt = f"""
    Extract all personal names (people's names) mentioned in the following text.
    Return ONLY a Python list of names in lowercase, with no explanation.
    Include full names when possible (first and last name).
    Exclude titles (Mr, Mrs, Dr) and company names.
    
    Format: ["john smith", "mary jane doe", "alex johnson"]
    If no names found, return: []

    TEXT:
    {text[:2000]}  # Limit text length to avoid token limits
    """

    try:
        response = llm.invoke(prompt).strip()
        
        # Better parsing of LLM response
        if response.startswith('[') and response.endswith(']'):
            names_list = ast.literal_eval(response)
            if isinstance(names_list, list):
                # Validate and clean names
                valid_names = set()
                for name in names_list:
                    if isinstance(name, str) and len(name.strip()) > 2:
                        clean_name = re.sub(r'\s+', ' ', name.strip().lower())
                        if len(clean_name.split()) >= 2:  # At least first and last
                            valid_names.add(clean_name)
                return valid_names
        
        return set()
        
    except Exception as e:
        print(f"[LLM name extraction error]: {e}")
        return set()