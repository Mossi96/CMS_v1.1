# Backend logic for the clinic system.

# This module is deliberately free of any input()/print() or GUI code.
# It only knows how to load, save, hash, check, and authenticate.
# That means both a terminal front-end and a tkinter front-end can
# import and use these exact functions without changing a line here.

import json
import os
import bcrypt
import random
import patients


# --- Constants ------------------------------------------------------
DB_FILE = "users.json"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "$2b$12$d4hQbmwxX2WF8TALii3XlOdvHGhWiynktCE4VxbmM4rEKmMQq68DG"

VALID_ROLES = ["Nurse", "Medical Officer", "Dr"]
DEFAULT_ROLE = "Nurse"


# --- Password helpers -----------------------------------------------
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# --- User record helpers --------------------------------------------
def normalize_user(data):
    # Upgrade the legacy flat (password-string) format to dict form.
    if isinstance(data, dict):
        return data
    return {"password": data, "role": DEFAULT_ROLE}

# Return the full name of a user record, or an empty string if not available.
def full_name(record):
    record = normalize_user(record)
    first = record.get("first_name", "")
    last = record.get("last_name", "")
    return f"{first} {last}".strip()

# load_users() and save_users() are the only two functions that touch the JSON file.
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def display_name(username):
    users = load_users()
    if username in users:
        return full_name(users[username])
    return username


# --- The key one: pure authentication -------------------------------

# Authenticate a username/password pair. Returns (username, role) if valid, or None if invalid.
def authenticate(username, password):
    users = load_users()
    username = username.strip()

    if username.lower() == ADMIN_USERNAME and check_password(password, ADMIN_PASSWORD):
        return (ADMIN_USERNAME, "Admin")

    if username in users:
        record = normalize_user(users[username])
        if check_password(password, record["password"]):
            return (username, record.get("role", DEFAULT_ROLE))

    return None


# Admin only functions

# Returns a list of (username, role, patient_id) pairs.
def list_users():
    users = load_users()
    result = []
    for name, data in users.items():
        record = normalize_user(data)
        role = record.get("role", DEFAULT_ROLE)
        result.append((name, full_name(record), role))
    return result

# Create and validate a user, returns (ok, message).
def create_user(username, first_name, last_name, password, role):
    username = username.strip()
    if not username:
        return (False, "Username cannot be empty.")
    if username.lower() == ADMIN_USERNAME:
        return (False, "This username is reserved.")
    if role not in VALID_ROLES:
        return (False, "Invalid role.")
    
    users = load_users()
    if username in users:
        return (False, "Username already exists.")
    if not password:
        return (False, "Password cannot be empty.")
    
    first_name = first_name.strip()
    last_name = last_name.strip()
    if not first_name or not last_name:
        return (False, "First and last name required.")
    record = {"password": hash_password(password), 
              "role": role,
              "first_name": first_name,
              "last_name": last_name}
    users[username] = record
    save_users(users)
    return (True, f"User '{username}' created as '{role}'.")

# Changes a users role. returns (ok, message).
def set_role(username, role):
    if role not in VALID_ROLES:
        return (False, "Invalid role.")
    users = load_users()
    if username not in users:
        return (False, f"User '{username}' not found.")
    record = normalize_user(users[username])
    record["role"] = role
    users[username] = record
    save_users(users)
    return (True, f"Updated '{username}' to '{role}'.")

# Deletes the user if they exist in the database.
def delete_user(username):
    users = load_users()

    if username not in users:
        return (False, f"User '{username}' not found.")
    
    del users[username]
    save_users(users)
    return (True, f"User '{username}' has been deleted.")