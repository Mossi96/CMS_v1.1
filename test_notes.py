# Tests for notes.py.

# Run from the project folder with:  pytest

# Each test starts from an empty notes file (see conftest.py).

from datetime import datetime
import notes

# Test that get_notes returns an empty list for a patient with no notes, and that add_note adds a note correctly and preserves the order of notes.
def test_get_notes_unknown_patient_is_empty():
    assert notes.get_notes("000-000-000") == []

# Test that add_note is successful and that the note is stored correctly with all required fields.
def test_add_note_success():
    ok, _ = notes.add_note("102-168-248", "Patient stable.", "nina", "Nurse")
    assert ok is True
    assert len(notes.get_notes("102-168-248")) == 1


def test_add_note_records_all_fields():
    notes.add_note("102-168-248", "Patient stable.", "nina", "Nurse")
    note = notes.get_notes("102-168-248")[0]
    assert note["text"] == "Patient stable."
    assert note["author_name"] == "nina"
    assert note["author_role"] == "Nurse"
    assert "created_at" in note


def test_add_note_rejects_empty_text():
    ok, _ = notes.add_note("102-168-248", "   ", "nina", "Nurse")
    assert ok is False
    assert notes.get_notes("102-168-248") == []


def test_add_note_trims_whitespace():
    notes.add_note("102-168-248", "  trimmed  ", "nina", "Nurse")
    assert notes.get_notes("102-168-248")[0]["text"] == "trimmed"


def test_notes_kept_in_creation_order():
    notes.add_note("102-168-248", "first", "nina", "Nurse")
    notes.add_note("102-168-248", "second", "dr_lee", "Dr")
    texts = [n["text"] for n in notes.get_notes("102-168-248")]
    assert texts == ["first", "second"]


def test_notes_isolated_per_patient():
    notes.add_note("111", "note for A", "nina", "Nurse")
    notes.add_note("222", "note for B", "nina", "Nurse")
    a = notes.get_notes("111")
    assert len(a) == 1
    assert a[0]["text"] == "note for A"


def test_created_at_is_iso_parseable():
    notes.add_note("102-168-248", "x", "nina", "Nurse")
    stamp = notes.get_notes("102-168-248")[0]["created_at"]
    datetime.fromisoformat(stamp)   # raises if not valid ISO format
