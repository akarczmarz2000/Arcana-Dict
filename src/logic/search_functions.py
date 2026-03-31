import json
from pathlib import Path


# ------------------------------------------------------------
# FILE PATH SETUP
# ------------------------------------------------------------
# This file lives in:
# src/logic/search_functions.py
#
# So to reach the project root we go:
# search_functions.py -> logic -> src -> project root
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "dictionary.json"


# ------------------------------------------------------------
# LOAD DICTIONARY DATA
# ------------------------------------------------------------
def load_dictionary_data():
    """
    Load dictionary entries from data/dictionary.json.

    Returns:
        list[dict]: all dictionary entries

    If the file is missing or invalid, this returns an empty list.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("dictionary.json must contain a list of entries.")

        return data

    except FileNotFoundError:
        print(f"Error: dictionary file not found: {DATA_FILE}")
        return []

    except json.JSONDecodeError as error:
        print(f"Error: dictionary.json is not valid JSON: {error}")
        return []

    except Exception as error:
        print(f"Unexpected error while loading dictionary data: {error}")
        return []


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def normalise_text_list(values):
    """
    Take a list of values and return a clean lowercase string list.

    This helps protect the search functions if a field is missing,
    contains None, or contains non-string values.
    """
    cleaned_values = []

    for value in values or []:
        if value is None:
            continue
        cleaned_values.append(str(value).strip().lower())

    return cleaned_values


# ------------------------------------------------------------
# ARCANA SEARCHES
# ------------------------------------------------------------
def exact_search(query, data):
    """
    Search for an exact Arcana word using the 'id' field.

    Used by UI mode:
    Arcana (exact)
    """
    query = query.strip().lower()

    if not query:
        return []

    return [entry for entry in data if entry.get("id", "").strip().lower() == query]


def partial_search(query, data):
    """
    Search for part of an Arcana word using the 'id' field.

    Used by UI mode:
    Arcana (partial)
    """
    query = query.strip().lower()

    if not query:
        return []

    return [entry for entry in data if query in entry.get("id", "").strip().lower()]


# ------------------------------------------------------------
# ENGLISH SEARCHES
# ------------------------------------------------------------
def exact_english_search(query, data):
    """
    Search literal meanings and synonyms using exact matching only.

    Used by UI mode:
    English (exact meaning/synonym)
    """
    query = query.strip().lower()

    if not query:
        return []

    results = []

    for entry in data:
        literal_meanings = normalise_text_list(entry.get("literal_meaning", []))
        synonyms = normalise_text_list(entry.get("synonyms", []))

        meaning_match = query in literal_meanings
        synonym_match = query in synonyms

        if meaning_match or synonym_match:
            results.append(entry)

    return results


def synonym_search(query, data):
    """
    Search the synonyms field only.

    This is optional/internal and not required by the current UI,
    but it may still be useful later.
    """
    query = query.strip().lower()

    if not query:
        return []

    results = []

    for entry in data:
        synonyms = normalise_text_list(entry.get("synonyms", []))

        if any(query in synonym for synonym in synonyms):
            results.append(entry)

    return results


def english_search(query, data):
    """
    Search both literal meanings and synonyms using partial matching.

    Used by UI mode:
    English (meanings + synonyms)
    """
    query = query.strip().lower()

    if not query:
        return []

    results = []

    for entry in data:
        literal_meanings = normalise_text_list(entry.get("literal_meaning", []))
        synonyms = normalise_text_list(entry.get("synonyms", []))

        meaning_match = any(query in meaning for meaning in literal_meanings)
        synonym_match = any(query in synonym for synonym in synonyms)

        if meaning_match or synonym_match:
            results.append(entry)

    return results
