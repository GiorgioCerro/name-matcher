# matcher/name_variants.py

from nameparser import HumanName

NICKNAMES = {
    "james": ["jim", "jimmy"],
    "william": ["bill", "billy", "will"],
    "robert": ["bob", "bobby", "rob", "robbie"],
    "michael": ["mike", "mickey"],
    "john": ["jack", "johnny"],
    # Add more as needed
}

def generate_name_variants(full_name: str) -> set:
    """
    Given a full name, generate a set of possible name variants,
    including nicknames and abbreviated forms.
    """
    name = HumanName(full_name)
    variants = set()

    first = name.first.lower()
    middle = name.middle.lower()
    last = name.last.lower()

    # Add full name combinations
    variants.add(f"{first} {last}")
    variants.add(f"{first} {middle} {last}".strip())
    variants.add(f"{first[0]}. {last}")
    variants.add(f"{first} {middle[0]}. {last}".strip() if middle else f"{first} {last}")

    # Add nickname variants
    for nick in NICKNAMES.get(first, []):
        variants.add(f"{nick} {last}")

    return set(variant.strip().lower() for variant in variants if variant)