import json
from pathlib import Path
import shutil


# ------------------------------------------------------------
# FILE PATH SETUP
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "dictionary.json"
BACKUP_DIR = PROJECT_ROOT / "data" / "backup"

# Fixed backup copy that is not part of the numbered rotation
CORE_BACKUP_FILE = BACKUP_DIR / "dictionary.json"

# Maximum number of rotating numbered backups
MAX_NUMBERED_BACKUPS = 5


# ------------------------------------------------------------
# LOAD / SAVE
# ------------------------------------------------------------
def load_dictionary_data():
    """
    Load dictionary entries from data/dictionary.json.

    Returns:
        list[dict]: all dictionary entries
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("dictionary.json must contain a list of entries.")

        return sort_entries(data)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as error:
        raise ValueError(f"dictionary.json is not valid JSON: {error}") from error


def save_dictionary_data(data):
    """
    Save the full dictionary list back to dictionary.json.

    Before saving:
    - update the fixed backup copy
    - rotate numbered backups

    Returns:
        pathlib.Path: the saved file path
    """
    if not isinstance(data, list):
        raise ValueError("Data to save must be a list of dictionary entries.")

    cleaned_data = [clean_entry(entry) for entry in data]
    cleaned_data = sort_entries(cleaned_data)

    create_backup_rotation()

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file, indent=2, ensure_ascii=False)

    return DATA_FILE


# ------------------------------------------------------------
# BACKUP SYSTEM
# ------------------------------------------------------------
def create_backup_rotation():
    """
    Maintain:
    - one fixed backup copy: backup/dictionary.json
    - a limited rotating set of numbered backups:
      dictionary_1.json, dictionary_2.json, etc.

    Rotation rule:
    - highest numbered backup is deleted if needed
    - others move up by one number
    - current live dictionary becomes dictionary_1.json
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # If there is no current live dictionary yet, there is nothing to back up.
    if not DATA_FILE.exists():
        return

    # Update the fixed core backup copy.
    shutil.copy2(DATA_FILE, CORE_BACKUP_FILE)

    # Delete the oldest numbered backup if it exists.
    oldest_backup = get_numbered_backup_file(MAX_NUMBERED_BACKUPS)
    if oldest_backup.exists():
        oldest_backup.unlink()

    # Shift existing numbered backups upward.
    for number in range(MAX_NUMBERED_BACKUPS - 1, 0, -1):
        current_file = get_numbered_backup_file(number)
        next_file = get_numbered_backup_file(number + 1)

        if current_file.exists():
            current_file.rename(next_file)

    # Save current live dictionary as the newest numbered backup.
    shutil.copy2(DATA_FILE, get_numbered_backup_file(1))


def get_numbered_backup_file(number):
    """
    Return the path for a numbered backup file.

    Example:
    number=1 -> backup/dictionary_1.json
    """
    return BACKUP_DIR / f"dictionary_{number}.json"


# ------------------------------------------------------------
# CLEANING / VALIDATION
# ------------------------------------------------------------
def split_csv_field(value):
    """
    Turn a comma-separated string into a clean list.
    """
    parts = [part.strip() for part in str(value).split(",")]
    return [part for part in parts if part]


def clean_list_field(value):
    """
    Ensure a field is returned as a clean list of non-empty strings.
    """
    if value is None:
        return []

    if isinstance(value, str):
        return split_csv_field(value)

    if isinstance(value, list):
        cleaned = []
        for item in value:
            text = str(item).strip()
            if text:
                cleaned.append(text)
        return cleaned

    text = str(value).strip()
    return [text] if text else []


def clean_entry(entry):
    """
    Make sure an entry has the correct basic structure.
    """
    return {
        "id": str(entry.get("id", "")).strip(),
        "literal_meaning": clean_list_field(entry.get("literal_meaning", [])),
        "synonyms": clean_list_field(entry.get("synonyms", [])),
        "word_class": clean_list_field(entry.get("word_class", [])),
    }


def validate_entry(entry):
    """
    Validate a dictionary entry.

    Returns:
        tuple[bool, str]
    """
    entry_id = str(entry.get("id", "")).strip()

    if not entry_id:
        return False, "The entry must have an ID / word."

    return True, "Entry is valid."


# ------------------------------------------------------------
# ENTRY LOOKUP
# ------------------------------------------------------------
def find_entry_index(data, entry_id):
    """
    Find the index of an entry by ID.

    Returns:
        int | None
    """
    target_id = str(entry_id).strip().lower()

    for index, entry in enumerate(data):
        if str(entry.get("id", "")).strip().lower() == target_id:
            return index

    return None


def id_exists(data, entry_id, ignore_index=None):
    """
    Check whether an ID already exists in the dictionary.
    """
    target_id = str(entry_id).strip().lower()

    for index, entry in enumerate(data):
        if ignore_index is not None and index == ignore_index:
            continue

        if str(entry.get("id", "")).strip().lower() == target_id:
            return True

    return False


def sort_entries(data):
    """
    Return dictionary data sorted by ID.
    """
    return sorted(data, key=lambda entry: str(entry.get("id", "")).lower())


# ------------------------------------------------------------
# CRUD OPERATIONS
# ------------------------------------------------------------
def add_entry(data, entry):
    """
    Add a new entry to the dictionary data.
    """
    entry = clean_entry(entry)
    is_valid, message = validate_entry(entry)

    if not is_valid:
        raise ValueError(message)

    if id_exists(data, entry["id"]):
        raise ValueError("An entry with this ID already exists.")

    updated_data = list(data)
    updated_data.append(entry)
    return sort_entries(updated_data)


def update_entry(data, original_id, updated_entry):
    """
    Update an existing entry identified by original_id.
    """
    updated_entry = clean_entry(updated_entry)
    is_valid, message = validate_entry(updated_entry)

    if not is_valid:
        raise ValueError(message)

    original_index = find_entry_index(data, original_id)
    if original_index is None:
        raise ValueError(f"Entry '{original_id}' was not found.")

    updated_data = list(data)
    updated_data[original_index] = updated_entry
    return sort_entries(updated_data)


def delete_entry(data, entry_id):
    """
    Delete an entry by ID.
    """
    index = find_entry_index(data, entry_id)
    if index is None:
        raise ValueError(f"Entry '{entry_id}' was not found.")

    updated_data = list(data)
    del updated_data[index]
    return sort_entries(updated_data)


# ------------------------------------------------------------
# SAVE HELPERS
# ------------------------------------------------------------
def add_entry_and_save(data, entry):
    updated_data = add_entry(data, entry)
    save_dictionary_data(updated_data)
    return updated_data


def update_entry_and_save(data, original_id, updated_entry):
    updated_data = update_entry(data, original_id, updated_entry)
    save_dictionary_data(updated_data)
    return updated_data


def delete_entry_and_save(data, entry_id):
    updated_data = delete_entry(data, entry_id)
    save_dictionary_data(updated_data)
    return updated_data