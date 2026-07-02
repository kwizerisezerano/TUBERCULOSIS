from types import SimpleNamespace

from seed_users import resolve_test_user_hospital


def test_hosp2_users_share_the_default_hospital():
    default_hospital = SimpleNamespace(id=1)
    hospitals = [SimpleNamespace(id=2), SimpleNamespace(id=3), SimpleNamespace(id=4)]

    hospital = resolve_test_user_hospital({"username": "doctor_hosp2"}, hospitals, default_hospital)

    assert hospital.id == 1


def test_hosp3_users_use_the_next_available_hospital_when_present():
    default_hospital = SimpleNamespace(id=1)
    hospitals = [SimpleNamespace(id=2), SimpleNamespace(id=3), SimpleNamespace(id=4)]

    hospital = resolve_test_user_hospital({"username": "labtech_hosp3"}, hospitals, default_hospital)

    assert hospital.id == 3
