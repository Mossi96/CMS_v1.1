# CMS_v1.1

Clinic Management System

A role-based clinic desktop app (Python + CustomTkinter). Staff log in, manage
patient records, write clinical notes, and if they're a Doctor prescribe
medications.

--- Setup ---

Requirements: 

Make sure you have Python 3.10+ installed

bashpip install -r requirements.txt - this will install the requirements.

python app.py - To run the app after installing requirements.


If pip doesn't work, try python -m pip install -r requirements.txt.

On Linux only, you may also need Tkinter:

bashsudo apt install python3-tk

(Windows and macOS ship with it.)



--- Logging in ---

Log in as admin to create staff accounts.

What to try:

As Admin you can create users, assign roles, delete users. Patients aren't users,
so they don't appear here.

As a Nurse, Medical Officer or Dr you land on the Staff Dashboard. From here you can open the Patients app.

Search patients by first name, last name, or patient ID (prefix search type
"s" to see everyone whose name starts with S).
Select a patient and Open Patient to see their details and notes, you can also double click to open a patient.
New Patient to create a record (DOB must be YYYY-MM-DD, Medicare must be
10 digits).
New notes and Prescriptions are automatically signed with your name, role, and a timestamp.

As a Dr specifically you can open a patient and you'll see an extra
Prescriptions tab and a New Prescription button. Log in as a Nurse and
they disappear. (The restriction is enforced in the backend too, not just hidden
in the UI.)

You can open multiple patient windows at once, they work independently.

Running the tests

bashpython -m pytest

Notes:

Data is stored in local JSON files (users.json, patients.json, notes.json,
prescriptions.json), they're created automatically.
patients.json ships with 50 sample patients so there's something to search.
This is a portfolio project. For a real client, credentials would come from
environment variables and data would live in a real database.
