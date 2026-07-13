# Patient notes storage.

# Kept separate from auth.py on purpose: notes are a different concern with a
# different lifecycle and will grow much larger than the user records. This
# module only knows how to load, save, add, and list notes -- no GUI, no auth.
# Notes are append-only: once added, an entry is never overwritten or removed.

import json
import os
from datetime import datetime

NOTES_FILE = "notes.json"


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return {}
    try:
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=4)


# Append a signed note to a patient's record. Returns (ok, message).
# The timestamp is stored in ISO format (sortable, unambiguous); the
# signature is rendered for display elsewhere, not baked into the text.
def add_note(patient_id, text, author_name, author_role):
    
    text = text.strip()
    if not text:
        return (False, "Note cannot be empty.")

    notes = load_notes()
    entry = {
        "text": text,
        "author_name": author_name,
        "author_role": author_role,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    notes.setdefault(patient_id, []).append(entry)
    save_notes(notes)
    return (True, "Note added.")


def get_notes(patient_id):
    #Return the list of note entries for a patient (oldest first).
    return load_notes().get(patient_id, [])
