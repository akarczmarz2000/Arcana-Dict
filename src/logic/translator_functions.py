from src.logic.search_functions import load_dictionary_data, normalise_text_list


def tokenise_phrase(text):
    text = text.lower()

    for char in ",.;:!?()[]{}\"'":
        text = text.replace(char, " ")

    return text.split()


def format_entry_summary(entry):
    return {
        "id": entry.get("id", "Unknown"),
        "literal_meaning": entry.get("literal_meaning", []),
        "synonyms": entry.get("synonyms", []),
        "interpretations": entry.get("interpretations", []),
        "word_class": entry.get("word_class", []),
    }


def _unique_entries(entries):
    seen_ids = set()
    unique = []

    for entry in entries:
        entry_id = entry.get("id", "")
        if entry_id in seen_ids:
            continue
        seen_ids.add(entry_id)
        unique.append(entry)

    return unique


def _build_alternative_terms(token, literal_matches):
    """
    Only take synonyms from literal matches.
    """
    terms = set()

    for match in literal_matches:
        for synonym in match.get("synonyms", []):
            cleaned = str(synonym).strip().lower()
            if cleaned and cleaned != token:
                terms.add(cleaned)

    return terms


def _find_alternatives(token, data, literal_matches, existing_matches):
    if not literal_matches:
        return []

    existing_ids = {entry.get("id", "") for entry in existing_matches}
    terms = _build_alternative_terms(token, literal_matches)

    if not terms:
        return []

    results = []

    for entry in data:
        entry_id = str(entry.get("id", "")).strip()
        if not entry_id or entry_id in existing_ids:
            continue

        literal_meanings = set(normalise_text_list(entry.get("literal_meaning", [])))

        if terms.intersection(literal_meanings):
            results.append(format_entry_summary(entry))

    results.sort(key=lambda item: item["id"])
    return _unique_entries(results)

def classify_english_token_matches(token, data):
    token = token.strip().lower()

    grouped = {
        "literal": [],
        "synonym": [],
        "interpretation": [],
        "alternatives": [],
    }

    if not token:
        return grouped

    for entry in data:
        literal_meanings = normalise_text_list(entry.get("literal_meaning", []))
        synonyms = normalise_text_list(entry.get("synonyms", []))
        interpretations = normalise_text_list(entry.get("interpretations", []))
        summary = format_entry_summary(entry)

        if token in literal_meanings:
            grouped["literal"].append(summary)
            continue

        if token in synonyms:
            grouped["synonym"].append(summary)
            continue

        if token in interpretations:
            grouped["interpretation"].append(summary)
            continue

    for group in ("literal", "synonym", "interpretation"):
        grouped[group].sort(key=lambda item: item["id"])
        grouped[group] = _unique_entries(grouped[group])

    existing = (
        grouped["literal"]
        + grouped["synonym"]
        + grouped["interpretation"]
    )

    grouped["alternatives"] = _find_alternatives(
        token=token,
        data=data,
        literal_matches=grouped["literal"],
        existing_matches=existing,
    )

    return grouped



def translate_english_to_arcana(text, data=None):
    if data is None:
        data = load_dictionary_data()

    text = text.strip()
    if not text:
        return {
            "direction": "english_to_arcana",
            "input": text,
            "tokens": {},
            "notes": ["No input provided."],
        }

    tokens = tokenise_phrase(text)

    token_results = {
        token: classify_english_token_matches(token, data)
        for token in tokens
    }

    notes = [
        "Match order: literal, synonym, interpretation, then alternatives.",
        "Alternatives only expand from synonyms of exact literal matches.",
        "Alternatives only match against literal meanings of other entries.",
    ]

    return {
        "direction": "english_to_arcana",
        "input": text,
        "tokens": token_results,
        "notes": notes,
    }


def translate_arcana_to_english(text, data=None):
    if data is None:
        data = load_dictionary_data()

    text = text.strip().lower()

    matches = []
    close_matches = []

    for entry in data:
        word_id = str(entry.get("id", "")).strip().lower()
        summary = format_entry_summary(entry)

        if word_id == text:
            matches.append(summary)
        elif text in word_id:
            close_matches.append(summary)

    matches.sort(key=lambda item: item["id"])
    close_matches.sort(key=lambda item: item["id"])

    return {
        "direction": "arcana_to_english",
        "input": text,
        "matches": matches,
        "close_matches": close_matches,
        "notes": [],
    }


def translate_text(text, direction, data=None):
    if data is None:
        data = load_dictionary_data()

    if direction == "English to Arcana":
        return translate_english_to_arcana(text, data)
    if direction == "Arcana to English":
        return translate_arcana_to_english(text, data)

    return {
        "direction": direction,
        "input": text,
        "notes": ["Unknown translation direction."],
    }