from datetime import date, timedelta
import patients

def test_valid_dob_accepts_real_past_date():
    assert patients.valid_dob("1985-03-14") is True

def test_valid_dob_rejects_bad_format():
    assert patients.valid_dob("14/03/1985") is False
    assert patients.valid_dob("hello") is False

def test_valid_dob_rejects_impossible_date():
    assert patients.valid_dob("1985-13-40") is False

def test_valid_dob_rejects_future_date():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert patients.valid_dob(tomorrow) is False

def test_valid_medicare_accepts_ten_digits():
    assert patients.valid_medicare("2123456701") is True

def test_valid_medicare_accepts_spaced_format():
    assert patients.valid_medicare("2123 45670 1") is True

def test_valid_medicare_rejects_wrong_length():
    assert patients.valid_medicare("212345670") is False    
    assert patients.valid_medicare("21234567012") is False  

def test_valid_medicare_rejects_non_numeric():
    assert patients.valid_medicare("212345670a") is False

def test_create_patient_success():
    ok, msg = patients.create_patient("Max", "Smith", "1985-03-14",
                                      "12 Baker St", "2123 45670 1")
    assert ok is True
    all_patients = patients.load_patients()
    assert len(all_patients) == 1


def test_create_patient_stores_fields_correctly():
    patients.create_patient("Max", "Smith", "1985-03-14",
                            "12 Baker St", "2123 45670 1")
    record = list(patients.load_patients().values())[0]
    assert record["first_name"] == "Max"
    assert record["dob"] == "1985-03-14"
    assert record["medicare"] == "2123456701"        
    assert record["address"] == "12 Baker St"


def test_create_patient_rejects_bad_dob():
    ok, _ = patients.create_patient("Max", "Smith", "not-a-date",
                                    "12 Baker St", "2123456701")
    assert ok is False


def test_create_patient_rejects_bad_medicare():
    ok, _ = patients.create_patient("Max", "Smith", "1985-03-14",
                                    "12 Baker St", "123")      
    assert ok is False


def test_create_patient_rejects_empty_name():
    ok, _ = patients.create_patient("   ", "Smith", "1985-03-14",
                                    "12 Baker St", "2123456701")
    assert ok is False


def test_create_patient_generates_unique_ids():
    for _ in range(10):
        patients.create_patient("A", "B", "1990-01-01",
                                "somewhere", "2123456701")
    ids = [pid for pid, _, _, _, _ in patients.list_patients()]
    assert len(ids) == len(set(ids))


def test_get_patient_returns_record():
    patients.create_patient("Max", "Smith", "1985-03-14",
                            "12 Baker St", "2123456701")
    pid = patients.list_patients()[0][0]      
    record = patients.get_patient(pid)
    assert record["first_name"] == "Max"


def test_get_patient_unknown_returns_none():
    assert patients.get_patient("000-000-000") is None

def test_filter_empty_query_returns_all():
    plist = [("102-168-248", "Max", "Smith", "1985-03-14", "12 Baker St"),
             ("440-921-007", "Amy", "Jones", "1990-02-20", "5 Main Rd")]
    assert patients.filter_patients(plist, "") == plist


def test_filter_by_first_name_prefix():
    plist = [("102-168-248", "Max", "Smith", "1985-03-14", "12 Baker St")]
    assert patients.filter_patients(plist, "ma", "first") == plist


def test_filter_by_last_name_prefix():
    plist = [("102-168-248", "Max", "Smith", "1985-03-14", "12 Baker St"),
             ("440-921-007", "Amy", "Stone", "1990-02-20", "5 Main Rd"),
             ("550-000-111", "Bob", "Jones", "1988-07-07", "9 Oak Ave")]
    result = patients.filter_patients(plist, "s", "last")
    lasts = [last for _, _, last, _, _ in result]
    assert lasts == ["Smith", "Stone"]


def test_filter_by_id_prefix_ignores_dashes():
    plist = [("912-000-000", "A", "One", "1980-01-01", "x"),
             ("102-912-000", "B", "Two", "1980-01-01", "y")]
    result = patients.filter_patients(plist, "9", "id")
    ids = [pid for pid, _, _, _, _ in result]
    assert ids == ["912-000-000"]


def test_filter_criterion_first_ignores_id():
    plist = [("102-168-248", "Max", "Smith", "1985-03-14", "12 Baker St")]
    assert patients.filter_patients(plist, "102", "first") == []


def test_filter_no_match_returns_empty():
    plist = [("102-168-248", "Max", "Smith", "1985-03-14", "12 Baker St")]
    assert patients.filter_patients(plist, "zzz") == []