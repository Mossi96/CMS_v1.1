import prescriptions
def test_nurse_cannot_prescribe():
    ok, msg = prescriptions.add_prescription(
        "102-168-248", "Amoxicillin", "500mg", "Twice daily", "7", "days",
        "", "Nina Jones", "Nurse")
    assert ok is False
    assert "Doctor" in msg
    assert prescriptions.get_prescriptions("102-168-248") == []