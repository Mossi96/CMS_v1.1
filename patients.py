import random
import json
import os
from datetime import date

PATIENTS_FILE = "patients.json"

def load_patients():
    if not os.path.exists(PATIENTS_FILE):
        return {}
    try:
        with open(PATIENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_patients(patients):
    with open(PATIENTS_FILE, "w") as f:
        json.dump(patients, f, indent=4)

def valid_dob(value):
    try:
        dob = date.fromisoformat(value)
    except ValueError:
        return False
    return dob <= date.today()

def valid_medicare(value):
    digits = value.replace(" ", "")
    return len(digits) == 10 and digits.isdigit()

def generate_patient_id(users):
    existing = {
        u["id"] for u in users.values()
        if isinstance(u, dict) and "id" in u
    }
    while True:
        digits = f"{random.randint(0, 999_999_999):09d}"  # 9 digits, zero-padded
        formatted = f"{digits[0:3]}-{digits[3:6]}-{digits[6:9]}"
        if formatted not in existing:
            return formatted

def create_patient(first_name, last_name, dob, address, medicare):

    first_name = first_name.strip()
    last_name = last_name.strip()
    address = address.strip()

    if not first_name or not last_name:
        return (False, "First and last name are required.")
    if not valid_dob(dob):
        return (False, "DOB must be a valid past date (YYYY-MM-DD).")
    if not address:
        return (False, "Address is required.")
    if not valid_medicare(medicare):
        return (False, "Medicare number must be 10 digits.")
    
    medicare = medicare.replace(" ", "")
    patients = load_patients()
    new_id = generate_patient_id(patients)
    patients[new_id] = {
        "id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "address": address,
        "medicare": medicare,
    }
    save_patients(patients)
    return (True, f"Patient '{first_name} {last_name}' created.")

def get_patient(patient_id):
    return load_patients().get(patient_id)

def list_patients():
    patients = load_patients()
    result = []
    for record in patients.values():
        result.append((
            record["id"],
            record.get("first_name", ""),
            record.get("last_name", ""),
            record.get("dob", ""),
            record.get("address", ""),
        ))
    return result

def filter_patients(patient_list, query, criterion="all"):
    query = query.strip().lower()
    if not query:
        return patient_list
    result = []
    for pid, first, last, dob, address in patient_list:
        first_match = first.lower().startswith(query)
        last_match = last.lower().startswith(query)
        id_match = pid.replace("-", "").startswith(query.replace("-", ""))

        if criterion == "first":
            matches = first_match
        elif criterion == "last":
            matches = last_match
        elif criterion == "id":
            matches = id_match
        else:  # "all"
            matches = first_match or last_match or id_match

        if matches:
            result.append((pid, first, last, dob, address))
    return result