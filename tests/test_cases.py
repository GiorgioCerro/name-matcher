# tests/test_cases.py

from matcher.name_variants import generate_name_variants
from matcher.article_parser import extract_person_names
from matcher.matcher import match_name_against_article
from matcher.explainer import explain_match

def test_article_matching():
    # Step 1: Input
    input_name = "James Robert Smith"

    # Step 2: Generate name variants
    variants = generate_name_variants(input_name)
    print("Generated variants:", variants)

    # Step 3: Load test article
    with open("tests/test_data/sample_article_1.txt", "r", encoding="utf-8") as f:
        article_text = f.read()

    # Step 4: Extract names from article
    article_names = extract_person_names(article_text)
    print("Names found in article:", article_names)

    # Step 5: Match
    result = match_name_against_article(variants, article_names)
    print("Match result:", result)

    # Step 6: Explanation
    explanation = explain_match(result, input_name)
    print("Explanation:", explanation)

if __name__ == "__main__":
    test_article_matching()