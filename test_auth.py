# Tests for auth.py.

# Run from the project folder with:  pytest

# Each test starts from an empty data file (see conftest.py), so they can create
# users freely without affecting your real users.json or each other.

import auth
 
 
# --- password hashing ------------------------------------------------
def test_password_hash_roundtrip():
    hashed = auth.hash_password("hunter2")
    assert auth.check_password("hunter2", hashed) is True
    assert auth.check_password("wrong", hashed) is False
 
 
def test_hashes_are_salted_and_differ():
    # the same password hashed twice gives different hashes (unique salt)
    assert auth.hash_password("same") != auth.hash_password("same")
 
 
# --- normalize_user (legacy format upgrade) -------------------------
def test_normalize_user_upgrades_flat_string():
    assert auth.normalize_user("just-a-hash") == {
        "password": "just-a-hash", "role": auth.DEFAULT_ROLE}
 
 
def test_normalize_user_leaves_dict_untouched():
    record = {"password": "h", "role": "Nurse"}
    assert auth.normalize_user(record) is record
 
 
# --- create_user validation -----------------------------------------
def test_create_user_success():
    ok, _ = auth.create_user("nina", "Test", "User", "pw", "Nurse")
    assert ok is True
    assert "nina" in auth.load_users()
 
 
def test_create_user_rejects_duplicate():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    ok, msg = auth.create_user("nina", "Test", "User", "pw", "Dr")
    assert ok is False
    assert "exists" in msg
 
 
def test_create_user_rejects_reserved_admin_name():
    ok, msg = auth.create_user("admin", "Test", "User", "pw", "Dr")
    assert ok is False
    assert "reserved" in msg
 
 
def test_create_user_rejects_empty_username():
    ok, _ = auth.create_user("   ", "Test", "User", "pw", "Nurse")
    assert ok is False
 
 
def test_create_user_rejects_empty_password():
    ok, _ = auth.create_user("bob", "Test", "User", "", "Nurse")
    assert ok is False
 
 
def test_create_user_rejects_invalid_role():
    ok, _ = auth.create_user("bob", "Test", "User", "pw", "Wizard")
    assert ok is False

def test_create_user_stores_names():
    auth.create_user("max", "Max", "Smith", "pw", "Nurse")
    record = auth.load_users()["max"]
    assert record["first_name"] == "Max"
    assert record["last_name"] == "Smith"

def test_create_user_rejects_missing_names():
    ok, _ = auth.create_user("max", "", "Smith", "pw", "Nurse")
    assert ok is False
    ok, _ = auth.create_user("max", "Max", "", "pw", "Nurse")
    assert ok is False

def test_full_name_combines_parts():
    record = {"first_name": "Max", "last_name": "Smith", "role": "Nurse"}
    assert auth.full_name(record) == "Max Smith"

def test_full_name_missing_parts():
    record = {"password": "h", "role": "Nurse"}
    assert auth.full_name(record) == ""

# --- patient IDs -----------------------------------------------------
def test_patient_gets_id_on_creation():
    auth.create_user("sam", "Test", "User", "pw", "Patient")
    pid = auth.load_users()["sam"].get("id")
    parts = (pid or "").split("-")
    assert len(parts) == 3
    assert all(len(p) == 3 and p.isdigit() for p in parts)
 
 
def test_non_patient_has_no_id():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    assert "id" not in auth.load_users()["nina"]
 
 
def test_patient_ids_are_unique():
    for i in range(20):
        auth.create_user(f"p{i}", "Test", "User", "pw", "Patient")
    ids = [pid for _, _, pid in auth.list_patients()]
    assert len(ids) == len(set(ids))
 
 
# --- authenticate ----------------------------------------------------
def test_authenticate_success_returns_user_and_role():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    assert auth.authenticate("nina", "pw") == ("nina", "Nurse")
 
 
def test_authenticate_wrong_password_returns_none():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    assert auth.authenticate("nina", "nope") is None
 
 
def test_authenticate_unknown_user_returns_none():
    assert auth.authenticate("ghost", "pw") is None
 
 
def test_authenticate_admin(monkeypatch):
    # swap in a known admin hash so we don't depend on the real credential
    monkeypatch.setattr(auth, "ADMIN_PASSWORD", auth.hash_password("secret"))
    assert auth.authenticate("admin", "secret") == ("admin", "Admin")
    assert auth.authenticate("admin", "wrong") is None
 
 
# --- set_role --------------------------------------------------------
def test_set_role_changes_role():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    ok, _ = auth.set_role("nina", "Dr")
    assert ok is True
    assert auth.load_users()["nina"]["role"] == "Dr"
 
 
def test_set_role_rejects_unknown_user():
    ok, _ = auth.set_role("ghost", "Dr")
    assert ok is False
 
 
def test_set_role_rejects_invalid_role():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    ok, _ = auth.set_role("nina", "Wizard")
    assert ok is False
 
 
def test_promote_to_patient_generates_id():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    auth.set_role("nina", "Patient")
    assert auth.load_users()["nina"].get("id")
 
 
def test_patient_id_is_permanent_across_role_changes():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    auth.set_role("nina", "Patient")
    original = auth.load_users()["nina"]["id"]
    auth.set_role("nina", "Nurse")      # demote
    auth.set_role("nina", "Patient")    # re-promote
    assert auth.load_users()["nina"]["id"] == original
 
 
def test_list_users_hides_id_for_non_patients():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    auth.set_role("nina", "Patient")
    auth.set_role("nina", "Nurse")      # id stays in storage, hidden in display
    display = {name: pid for name, _, role, pid in auth.list_users()}
    assert display["nina"] == ""
    assert auth.load_users()["nina"].get("id")
 
 
# --- delete_user -----------------------------------------------------
def test_delete_user_success():
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    ok, _ = auth.delete_user("nina")
    assert ok is True
    assert "nina" not in auth.load_users()
 
 
def test_delete_unknown_user_fails():
    ok, _ = auth.delete_user("ghost")
    assert ok is False
 
 
# --- list_patients ---------------------------------------------------
def test_list_patients_only_returns_patients():
    auth.create_user("sam", "Test", "User", "pw", "Patient")
    auth.create_user("nina", "Test", "User", "pw", "Nurse")
    usernames = [username for username, _, _ in auth.list_patients()]
    assert "sam" in usernames
    assert "nina" not in usernames

def test_display_name_resolves_full_name():
    auth.create_user("max", "Max", "Smith", "pw", "Nurse")
    assert auth.display_name("max") == "Max Smith"


def test_display_name_falls_back_for_unknown_user():
    # admin isn't in users.json, so this must not crash
    assert auth.display_name("admin") == "admin"