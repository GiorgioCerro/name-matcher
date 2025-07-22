# matcher/name_variants.py

from nameparser import HumanName
from langchain_openai import OpenAI
from dotenv import load_dotenv
import ast
import re

load_dotenv() 
llm = OpenAI()

def generate_nicknames(name: str) -> list:
    """Generate nicknames with better error handling and validation."""
    if not name or len(name.strip()) < 2:
        return []
        
    prompt = f"""
    List common nicknames or diminutives for the first name '{name}'.
    Return only a valid Python list of strings, with no explanation or formatting.
    Return up to 5 variations, no more. 
    Example format: ["Gio", "Gigi", "George"]
    Return an empty list if there are no known nicknames.
    """
    try: 
        response = llm.invoke(prompt).strip()
        # Better parsing - handle various response formats
        if response.startswith("[") and response.endswith("]"):
            nicknames = ast.literal_eval(response)
            # Validate that it's actually a list of strings
            if isinstance(nicknames, list) and all(isinstance(n, str) for n in nicknames):
                return [n for n in nicknames if n.strip()]
        return []
    except Exception as e:
        print(f"[LLM generation nicknames error]: {e}")
        return []

def generate_name_variants(full_name: str) -> set:
    """
    Generate comprehensive name variants with better handling of edge cases.
    """
    if not full_name or not full_name.strip():
        return set()
    
    # Normalize the input
    name = HumanName(full_name)
    variants = set()

    first = name.first.lower().strip()
    middle = name.middle.lower().strip()
    last = name.last.lower().strip()
    
    # Handle cases where parsing failed
    if not first and not last:
        # Fallback: treat as space-separated tokens
        tokens = full_name.split()
        if len(tokens) >= 2:
            first, last = tokens[0], tokens[-1]
            if len(tokens) > 2:
                middle = ' '.join(tokens[1:-1])

    if not first or not last:
        return set()

    # Basic combinations
    variants.add(f"{first} {last}")
    if middle:
        variants.add(f"{first} {middle} {last}")
        variants.add(f"{first} {middle[0]}. {last}")
        # Middle name as first name (common in some cultures)
        variants.add(f"{middle} {last}")
        if len(middle) > 1:
            variants.add(f"{middle[0]}. {last}")

    # Initials variations
    if len(first) > 0:
        variants.add(f"{first[0]}. {last}")
        variants.add(f"{first[0]} {last}")  # Without period
    
    # Add nickname variants
    nicknames = generate_nicknames(first)
    for nick in nicknames:
        if nick:
            variants.add(f"{nick} {last}")
            if middle:
                variants.add(f"{nick} {middle[0]}. {last}")

    # Handle hyphenated names
    if '-' in last:
        last_parts = last.split('-')
        for part in last_parts:
            if part:
                variants.add(f"{first} {part}")
                
    # Handle apostrophes and special characters
    clean_variants = set()
    for variant in variants:
        if variant and variant.strip():
            # Remove extra spaces
            clean_variant = re.sub(r'\s+', ' ', variant.strip())
            clean_variants.add(clean_variant)
            # Also add version without apostrophes/special chars
            clean_variants.add(re.sub(r"['\-\.]", "", clean_variant))
    
    return clean_variants