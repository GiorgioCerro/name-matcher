# matcher/matcher.py - Improved version

from fuzzywuzzy import fuzz
from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
llm = OpenAI()

def calculate_multiple_fuzzy_scores(variant: str, article_name: str) -> dict[str, int]:
    """Calculate multiple fuzzy matching scores for better accuracy."""
    return {
        'ratio': fuzz.ratio(variant, article_name),
        'partial_ratio': fuzz.partial_ratio(variant, article_name),
        'token_sort_ratio': fuzz.token_sort_ratio(variant, article_name),
        'token_set_ratio': fuzz.token_set_ratio(variant, article_name)
    }

def get_best_fuzzy_match(name_variants: set[str], article_names: list[str]) -> tuple[float, str, str, dict]:
    """Find the best fuzzy match with detailed scoring."""
    best_score = 0
    best_variant = None
    best_match = None
    best_scores = {}
    
    for variant in name_variants:
        for article_name in article_names:
            scores = calculate_multiple_fuzzy_scores(variant, article_name)
            
            # Weighted combination of scores - token_set_ratio is most reliable for names
            combined_score = (
                scores['token_set_ratio'] * 0.4 +
                scores['token_sort_ratio'] * 0.3 +
                scores['ratio'] * 0.2 +
                scores['partial_ratio'] * 0.1
            )
            
            if combined_score > best_score:
                best_score = combined_score
                best_variant = variant
                best_match = article_name
                best_scores = scores
    
    return best_score, best_variant, best_match, best_scores

def match_name_against_article(name_variants: set[str], article_names: list[str], 
                             high_threshold: float = 85, low_threshold: float = 20):
    """
    Enhanced matching with tiered thresholds and better decision logic.
    
    Args:
        high_threshold: Above this score, we're confident it's a match
        low_threshold: Below this score, we're confident it's not a match
        Between the two: Use LLM for disambiguation
    """
    
    if not name_variants or not article_names:
        return {
            "match": False,
            "method": "no_data",
            "matched_name": None,
            "matched_variant": None,
            "score": 0,
            "explanation": "No name variants or article names to compare",
            "confidence": "high"
        }
    
    best_score, best_variant, best_match, detailed_scores = get_best_fuzzy_match(name_variants, article_names)
    
    # High confidence match
    if best_score >= high_threshold:
        return {
            "match": True,
            "method": "fuzzy_high_confidence",
            "matched_name": best_match,
            "matched_variant": best_variant,
            "score": best_score,
            "detailed_scores": detailed_scores,
            "explanation": f"High confidence match (score: {best_score:.1f}) between variant '{best_variant}' and article name '{best_match}'",
            "confidence": "high"
        }
    
    # High confidence no match
    elif best_score < low_threshold:
        return {
            "match": False,
            "method": "fuzzy_high_confidence",
            "matched_name": best_match,
            "matched_variant": best_variant,
            "score": best_score,
            "detailed_scores": detailed_scores,
            "explanation": f"High confidence no match (score: {best_score:.1f}) - names are too dissimilar",
            "confidence": "high"
        }
    
    # Uncertain - use LLM
    else:
        llm_result = llm_name_match_fallback(name_variants, article_names, best_score, best_variant, best_match)
        llm_result["fuzzy_score"] = best_score
        llm_result["best_fuzzy_match"] = best_match
        return llm_result

def llm_name_match_fallback(name_variants: set[str], article_names: list[str], 
                          fuzzy_score: float, best_variant: str, best_match: str):
    """
    Enhanced LLM fallback with more context and better prompting.
    """
    
    # Limit the data sent to LLM to avoid token limits
    limited_variants = list(name_variants)[:10]  
    limited_article_names = article_names[:20]
    
    prompt = f"""
    You are helping a financial analyst determine if a news article refers to a specific person for regulatory compliance.

    TARGET PERSON'S POSSIBLE NAMES: {limited_variants}
    NAMES MENTIONED IN ARTICLE: {limited_article_names}

    CONTEXT:
    - The fuzzy matching system gave a score of {fuzzy_score:.1f}/100 
    - Best fuzzy match was between "{best_variant}" and "{best_match}"
    - This is for regulatory screening, so false negatives (missing a real match) are more costly than false positives

    Consider:
    1. Cultural name variations (nicknames, different name orders)
    2. Spelling variations and typos
    3. Use of initials or partial names
    4. Same person might be referred to differently in the article

    Respond in exactly this format:
    MATCH: yes/no
    CONFIDENCE: high/medium/low
    EXPLANATION: [clear reasoning for your decision]
    """

    try:
        response = llm.invoke(prompt).strip()
        lines = response.split('\n')
        
        # Parse response
        match_line = next((line for line in lines if line.lower().startswith('match:')), "")
        confidence_line = next((line for line in lines if line.lower().startswith('confidence:')), "")
        explanation_line = next((line for line in lines if line.lower().startswith('explanation:')), "")
        
        match = "yes" in match_line.lower()
        confidence = confidence_line.split(':', 1)[-1].strip().lower() if confidence_line else "medium"
        explanation = explanation_line.split(':', 1)[-1].strip() if explanation_line else response
        
        return {
            "match": match,
            "method": "llm_disambiguation",
            "matched_name": best_match,
            "matched_variant": best_variant,
            "score": None,
            "explanation": explanation,
            "confidence": confidence,
            "llm_raw_response": response
        }

    except Exception as e:
        return {
            "match": False,  # Conservative default for regulatory context
            "method": "llm_error",
            "matched_name": None,
            "matched_variant": None,
            "score": None,
            "explanation": f"LLM analysis failed: {e}. Defaulting to no match for safety.",
            "confidence": "low"
        }