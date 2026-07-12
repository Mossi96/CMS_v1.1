import json
from datetime import datetime
import os


VALID_FREQUENCIES = [
    "Once daily",
    "Twice daily",
    "Three times daily",
    "Four times daily",
    "As needed",
]

PRESCRIPTIONS_FILE = "prescriptions.json"

VALID_DURATION_UNITS = ["days", "weeks", "months"]

PRESCRIBER_ROLE = "Dr"  

def load_prescriptions():
    if not os.path.exists(PRESCRIPTIONS_FILE):
        return {}
    try:
        with open(PRESCRIPTIONS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    

def get_prescriptions(patient_id):
    return load_prescriptions().get(patient_id, [])


def save_prescriptions(prescriptions):
    with open(PRESCRIPTIONS_FILE, "w") as f:
        json.dump(prescriptions, f, indent=4)

def add_prescription(patient_id, medication, dosage, frequency,
                     duration_amount, duration_unit, instructions,
                     prescriber_name, prescriber_role):
    # --- authorization: the real gate, not the hidden UI ---
    if prescriber_role != PRESCRIBER_ROLE:
        return (False, "Only a Doctor can create a prescription.")

    medication = medication.strip()
    dosage = dosage.strip()
    instructions = instructions.strip()

    if not medication:
        return (False, "Medication name is required.")
    if not dosage:
        return (False, "Dosage is required.")
    if frequency not in VALID_FREQUENCIES:
        return (False, "Invalid frequency.")
    if duration_unit not in VALID_DURATION_UNITS:
        return (False, "Invalid duration unit.")
    if not valid_duration_amount(duration_amount):
        return (False, "Duration must be a whole number greater than zero.")

    prescriptions = load_prescriptions()
    entry = {
        "medication": medication,
        "dosage": dosage,
        "frequency": frequency,
        "duration_amount": int(duration_amount),
        "duration_unit": duration_unit,
        "instructions": instructions,
        "prescriber_name": prescriber_name,
        "prescriber_role": prescriber_role,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    prescriptions.setdefault(patient_id, []).append(entry)
    save_prescriptions(prescriptions)
    return (True, "Prescription added.")

def valid_duration_amount(value):
    try:
        amount = int(value)
    except (ValueError, TypeError):
        return False
    return amount > 0