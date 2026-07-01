
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient

with app.app_context():
    db.create_all()
    patients = Patient.query.limit(5).all()  # Check first 5
    print("Checking first 5 patients:")
    for i, p in enumerate(patients):
        print(f"\nPatient {i+1}:")
        print(f"  ID: {p.id}")
        print(f"  Patient ID: {p.patient_id}")
        print(f"  Password hash exists: {bool(p.password_hash)}")
        
        print("  Setting password to 'Patient123!'...")
        p.set_password("Patient123!")
        db.session.add(p)
        
        verify = p.verify_password("Patient123!")
        print(f"  Verify password 'Patient123!': {verify}")
    
    # Do ALL patients now
    all_patients = Patient.query.all()
    print(f"\nUpdating ALL {len(all_patients)} patients...")
    for p in all_patients:
        p.set_password("Patient123!")
        db.session.add(p)
    db.session.commit()
    print("SUCCESS! All patients have password 'Patient123!'")
