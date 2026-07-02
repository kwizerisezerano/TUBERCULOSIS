"""
Fix: assign all hosp2 test users to the same hospital, and all hosp3 test users to the same hospital.
This ensures doctor_hosp2, labtech_hosp2, and pharmacist_hosp2 share one hospital_id so they
can see each other's prescriptions and lab tests.
"""
from app import app
from models.models import db, User, Hospital

HOSP2_USERNAMES = {'doctor_hosp2', 'labtech_hosp2', 'pharmacist_hosp2', 'hospitaladmin_hosp2'}
HOSP3_USERNAMES = {'doctor_hosp3', 'labtech_hosp3', 'pharmacist_hosp3', 'hospitaladmin_hosp3'}

with app.app_context():
    hospitals = Hospital.query.order_by(Hospital.id).all()
    if len(hospitals) < 2:
        print("Not enough hospitals in DB. Aborting.")
        exit(1)

    hosp2 = hospitals[1]
    hosp3 = hospitals[2] if len(hospitals) > 2 else hospitals[1]
    print(f"hosp2 target -> id={hosp2.id} name={hosp2.name}")
    print(f"hosp3 target -> id={hosp3.id} name={hosp3.name}")

    changed = 0
    for u in User.query.all():
        name = u.username
        if name in HOSP2_USERNAMES and u.hospital_id != hosp2.id:
            print(f"  {name}: {u.hospital_id} -> {hosp2.id}")
            u.hospital_id = hosp2.id
            changed += 1
        elif name in HOSP3_USERNAMES and u.hospital_id != hosp3.id:
            print(f"  {name}: {u.hospital_id} -> {hosp3.id}")
            u.hospital_id = hosp3.id
            changed += 1

    db.session.commit()
    print(f"\nFixed {changed} user(s).")
    print("\nFinal state:")
    for u in User.query.all():
        print(f"  id={u.id} username={u.username} role={u.role} hospital_id={u.hospital_id}")
