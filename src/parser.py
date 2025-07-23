import re

def parse_ingredients(raw_text):
    """
    Parses raw comma-separated ingredient text,
    removes parentheses and extra spaces.
    """
    cleaned = [re.sub(r"\s*\(.*?\)", "", i).strip() for i in raw_text.split(",")]
    return [i for i in cleaned if i]
