"""
Fix: ensure all hosp2/hosp3 users share the correct hospital_id,
reassign FK references from duplicate users to canonical users, then delete duplicates.
"""
from app import app
from models.models import db, User, Prescription, LabTest, Diagnosis, Treatment, Alert, AuditLog

HOSP2_ID = 1  # Kigali Health Center
HOSP3_ID = 2  # Remera Health Center
HOSP2_USERS = {'doctor_hosp2', 'labtech_hosp2', 'pharmacist_hosp2', 'hospitaladmin_hosp2'}
HOSP3_USERS = {'doctor_hosp3', 'labtech_hosp3', 'pharmacist_hosp3', 'hospitaladmin_hosp3'}

with app.app_context():
    # --- 1. Build canonical user map (lowest id wins) ---
    canonical = {}  # username -> canonical User
    duplicates = []
    for u in User.query.order_by(User.id).all():
        if u.username not in canonical:
            canonical[u.username] = u
        else:
            duplicates.append(u)

    print(f"Found {len(duplicates)} duplicate users to remove.")

    # --- 2. Reassign all FK references from duplicate ids to canonical ids ---
    for dup in duplicates:
        canon = canonical[dup.username]
        dup_id, canon_id = dup.id, canon.id

        # lab_test.requested_by
        n = LabTest.query.filter_by(requested_by=dup_id).update({'requested_by': canon_id})
        if n: print(f"  Reassigned {n} lab_test.requested_by {dup_id}->{canon_id}")

        # lab_test.completed_by
        n = LabTest.query.filter_by(completed_by=dup_id).update({'completed_by': canon_id})
        if n: print(f"  Reassigned {n} lab_test.completed_by {dup_id}->{canon_id}")

        # prescription.created_by
        n = Prescription.query.filter_by(created_by=dup_id).update({'created_by': canon_id})
        if n: print(f"  Reassigned {n} prescription.created_by {dup_id}->{canon_id}")

        # prescription.approved_by
        n = Prescription.query.filter_by(approved_by=dup_id).update({'approved_by': canon_id})
        if n: print(f"  Reassigned {n} prescription.approved_by {dup_id}->{canon_id}")

        # prescription.dispensed_by
        n = Prescription.query.filter_by(dispensed_by=dup_id).update({'dispensed_by': canon_id})
        if n: print(f"  Reassigned {n} prescription.dispensed_by {dup_id}->{canon_id}")

        # diagnosis.clinician_id
        n = Diagnosis.query.filter_by(clinician_id=dup_id).update({'clinician_id': canon_id})
        if n: print(f"  Reassigned {n} diagnosis.clinician_id {dup_id}->{canon_id}")

        # treatment (no user FK, skip)

        # alert.user_id
        n = Alert.query.filter_by(user_id=dup_id).update({'user_id': canon_id})
        if n: print(f"  Reassigned {n} alert.user_id {dup_id}->{canon_id}")

        # audit_log.user_id
        n = AuditLog.query.filter_by(user_id=dup_id).update({'user_id': canon_id})
        if n: print(f"  Reassigned {n} audit_log.user_id {dup_id}->{canon_id}")

    db.session.flush()

    # --- 3. Delete duplicates ---
    for dup in duplicates:
        print(f"  Delete duplicate: id={dup.id} {dup.username}")
        db.session.delete(dup)

    db.session.commit()
    print(f"Deleted {len(duplicates)} duplicates.\n")

    # --- 4. Fix hospital_id for hosp2/hosp3 canonical users ---
    fixed = 0
    for username, u in canonical.items():
        target = None
        if username in HOSP2_USERS:
            target = HOSP2_ID
        elif username in HOSP3_USERS:
            target = HOSP3_ID
        if target and u.hospital_id != target:
            print(f"  Fix {u.username} id={u.id}: hospital_id {u.hospital_id} -> {target}")
            u.hospital_id = target
            fixed += 1

    db.session.commit()
    print(f"Fixed hospital_id for {fixed} users.\n")

    # --- 5. Fix orphaned prescriptions/lab tests/diagnoses created by hosp2 doctor ---
    doctor2 = canonical.get('doctor_hosp2')
    if doctor2:
        rx = Prescription.query.filter_by(created_by=doctor2.id).filter(
            Prescription.hospital_id != doctor2.hospital_id
        ).update({'hospital_id': doctor2.hospital_id})
        lt = LabTest.query.filter_by(requested_by=doctor2.id).filter(
            LabTest.hospital_id != doctor2.hospital_id
        ).update({'hospital_id': doctor2.hospital_id})
        dx = Diagnosis.query.filter_by(clinician_id=doctor2.id).filter(
            Diagnosis.hospital_id != doctor2.hospital_id
        ).update({'hospital_id': doctor2.hospital_id})
        db.session.commit()
        print(f"Fixed records for doctor_hosp2 (hospital_id={doctor2.hospital_id}):")
        print(f"  {rx} prescriptions, {lt} lab tests, {dx} diagnoses\n")

    # --- 6. Print final state ---
    print("=== Final user hospital assignments ===")
    for u in User.query.order_by(User.id).all():
        print(f"  id={u.id}  {u.username:<30} {u.role:<20} hospital_id={u.hospital_id}")
