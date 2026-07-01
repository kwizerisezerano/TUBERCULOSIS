
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient

with app.app_context():
    patients = Patient.query.all()
    print(f"Total patients in DB: {len(patients)}")
    for i, p in enumerate(patients):
        # Set password!
        if not p.password:
            p.set_password("Patient123!")
            db.session.add(p)
    db.session.commit()
    
    # Get first 5
    demo_patients = Patient.query.limit(5).all()
    print(f"First {len(demo_patients)} demo patients:")
    for i, p in enumerate(demo_patients):
        print(f"Patient {i+1}: patient_id='{p.patient_id}', name='{p.first_name} {p.last_name}'")
    if len(demo_patients) ==0:
        print("No patients found in DB!")
