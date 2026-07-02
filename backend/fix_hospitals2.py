from app import app
from models.models import db, User, Prescription, LabTest, Diagnosis

HOSP2_ID = 1
HOSP3_ID = 2
HOSP2_USERS = {'doctor_hosp2', 'labtech_hosp2', 'pharmacist_hosp2', 'hospitaladmin_hosp2'}
HOSP3_USERS = {'doctor_hosp3', 'labtech_hosp3', 'pharmacist_hosp3', 'hospitaladmin_hosp3'}

with app.app_context():
    # Fix user hospital_ids
    for u in User.query.all():
        if u.username in HOSP2_USERS and u.hospital_id != HOSP2_ID:
            print(f'Fix user {u.username}: {u.hospital_id} -> {HOSP2_ID}')
            u.hospital_id = HOSP2_ID
        elif u.username in HOSP3_USERS and u.hospital_id != HOSP3_ID:
            print(f'Fix user {u.username}: {u.hospital_id} -> {HOSP3_ID}')
            u.hospital_id = HOSP3_ID
    db.session.flush()

    # Fix prescriptions/lab tests/diagnoses to match their creator's hospital
    for p in Prescription.query.all():
        creator = User.query.filter_by(id=p.created_by).first()
        if creator and creator.hospital_id and p.hospital_id != creator.hospital_id:
            print(f'Fix presc id={p.id} {p.medication}: hospital_id {p.hospital_id} -> {creator.hospital_id}')
            p.hospital_id = creator.hospital_id

    for l in LabTest.query.all():
        requester = User.query.filter_by(id=l.requested_by).first()
        if requester and requester.hospital_id and l.hospital_id != requester.hospital_id:
            print(f'Fix labtest id={l.id}: hospital_id {l.hospital_id} -> {requester.hospital_id}')
            l.hospital_id = requester.hospital_id

    for d in Diagnosis.query.all():
        clinician = User.query.filter_by(id=d.clinician_id).first()
        if clinician and clinician.hospital_id and d.hospital_id != clinician.hospital_id:
            print(f'Fix diagnosis id={d.id}: hospital_id {d.hospital_id} -> {clinician.hospital_id}')
            d.hospital_id = clinician.hospital_id

    db.session.commit()
    print('\nDone. Final state:')
    for u in User.query.filter(User.username.in_(HOSP2_USERS | HOSP3_USERS)).all():
        print(f'  {u.username} hospital_id={u.hospital_id}')
    for p in Prescription.query.all():
        print(f'  presc id={p.id} {p.medication} hospital_id={p.hospital_id}')
