# matcher/matcher.py

from fuzzywuzzy import fuzz

def match_name_against_article(name_variants: set, article_names: list, threshold=90):
    """
    Compare each name variant against all names found in the article.
    Return the best match and its score.
    """
    best_score = 0
    best_match = None

    for variant in name_variants:
        for article_name in article_names:
            score = fuzz.token_set_ratio(variant, article_name)
            if score > best_score:
                best_score = score
                best_match = article_name

    return {
        "match": best_score >= threshold,
        "matched_name": best_match,
        "score": best_score
    }