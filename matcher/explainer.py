# matcher/explainer.py

def explain_match(result: dict, input_name: str):
    """
    Generate a simple explanation for a match or non-match.
    """
    if result["match"]:
        return (
            f"The name '{result['matched_name']}' in the article matched with the input "
            f"'{input_name}' (score: {result['score']})."
        )
    else:
        return (
            f"No name in the article sufficiently matched '{input_name}'. "
            f"Highest similarity was with '{result['matched_name']}' (score: {result['score']})."
        )