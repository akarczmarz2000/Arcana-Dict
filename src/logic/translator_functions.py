from src.logic.search_functions import load_dictionary_data, normalise_text_list


def tokenise_phrase(text):
    """
    Split text into useful lowercase tokens and remove common filler words.
    """
    text = text.lower()

    for char in ",.;:!?()[]{}\"'":
        text = text.replace(char, " ")

    tokens = text.split()
    return tokens


def format_entry_summary(entry):
    """
    Build a clean summary dictionary for UI display.
    """
    return {
        "id": entry.get("id", "Unknown"),
        "literal_meaning": entry.get("literal_meaning", []),
        "synonyms": entry.get("synonyms", []),
        "word_class": entry.get("word_class", []),
    }


def classify_english_token_matches(token, data):
    """
    For one English token, split matches into four groups:
    - exact literal
    - exact synonym
    - close literal
    - close synonym
    """
    token = token.strip().lower()

    grouped = {
        "exact_literal": [],
        "exact_synonym": [],
        "close_literal": [],
        "close_synonym": [],
    }

    if not token:
        return grouped

    for entry in data:
        literal_meanings = normalise_text_list(entry.get("literal_meaning", []))
        synonyms = normalise_text_list(entry.get("synonyms", []))
        summary = format_entry_summary(entry)

        # Exact literal match
        if token in literal_meanings:
            grouped["exact_literal"].append(summary)
            continue

        # Exact synonym match
        if token in synonyms:
            grouped["exact_synonym"].append(summary)
            continue

        # Close literal match
        if any(token in meaning for meaning in literal_meanings):
            grouped["close_literal"].append(summary)
            continue

        # Close synonym match
        if any(token in synonym for synonym in synonyms):
            grouped["close_synonym"].append(summary)
            continue

    # Sort each group alphabetically by id for consistency
    for group_name in grouped:
        grouped[group_name].sort(key=lambda item: item["id"])

    return grouped


def translate_english_to_arcana(text, data=None):
    """
    Writing-helper translation from English to Arcana.

    For single words and phrases, process each meaningful token separately.
    """
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

    if not tokens:
        return {
            "direction": "english_to_arcana",
            "input": text,
            "tokens": {},
            "notes": ["No meaningful words found after removing filler words."],
        }

    token_results = {}
    for token in tokens:
        token_results[token] = classify_english_token_matches(token, data)

    notes = []
    if len(tokens) > 1:
        notes.append("Phrase input detected. Results are grouped by meaningful word.")
    else:
        notes.append("Single-word input detected.")

    return {
        "direction": "english_to_arcana",
        "input": text,
        "tokens": token_results,
        "notes": notes,
    }


def translate_arcana_to_english(text, data=None):
    """
    Translate an Arcana word to English support data.
    """
    if data is None:
        data = load_dictionary_data()

    text = text.strip().lower()
    if not text:
        return {
            "direction": "arcana_to_english",
            "input": text,
            "matches": [],
            "close_matches": [],
            "notes": ["No input provided."],
        }

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

    notes = []
    if matches:
        notes.append("Exact Arcana match found.")
    elif close_matches:
        notes.append("No exact Arcana match found. Showing partial Arcana matches.")
    else:
        notes.append("No Arcana match found.")

    return {
        "direction": "arcana_to_english",
        "input": text,
        "matches": matches,
        "close_matches": close_matches,
        "notes": notes,
    }


def translate_text(text, direction, data=None):
    """
    Main translator entry point.
    """
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


def format_translation_result(result):
    """
    Convert a structured translation result into readable plain text.
    """
    lines = []

    direction = result.get("direction", "Unknown")
    input_text = result.get("input", "")

    lines.append(f"Direction: {direction}")
    lines.append(f"Input: {input_text}")
    lines.append("")

    if direction == "english_to_arcana":
        token_results = result.get("tokens", {})

        for token, groups in token_results.items():
            lines.append(f"Word: {token}")

            lines.append("  Exact literal matches:")
            if groups["exact_literal"]:
                for match in groups["exact_literal"]:
                    meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                    lines.append(f"  - {match['id']} -> {meanings}")
            else:
                lines.append("  - None")

            lines.append("  Exact synonym matches:")
            if groups["exact_synonym"]:
                for match in groups["exact_synonym"]:
                    meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                    lines.append(f"  - {match['id']} -> {meanings}")
            else:
                lines.append("  - None")

            lines.append("  Close literal matches:")
            if groups["close_literal"]:
                for match in groups["close_literal"]:
                    meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                    lines.append(f"  - {match['id']} -> {meanings}")
            else:
                lines.append("  - None")

            lines.append("  Close synonym matches:")
            if groups["close_synonym"]:
                for match in groups["close_synonym"]:
                    meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                    lines.append(f"  - {match['id']} -> {meanings}")
            else:
                lines.append("  - None")

            lines.append("")

    elif direction == "arcana_to_english":
        matches = result.get("matches", [])
        close_matches = result.get("close_matches", [])

        lines.append("Matches:")
        if matches:
            for match in matches:
                meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                synonyms = ", ".join(match.get("synonyms", [])) or "None"
                lines.append(f"- {match['id']} -> meanings: {meanings} | synonyms: {synonyms}")
        else:
            lines.append("- None")

        lines.append("")
        lines.append("Close matches:")
        if close_matches:
            for match in close_matches:
                meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                lines.append(f"- {match['id']} -> {meanings}")
        else:
            lines.append("- None")

    notes = result.get("notes", [])
    if notes:
        lines.append("Notes:")
        for note in notes:
            lines.append(f"- {note}")

    return "\n".join(lines)