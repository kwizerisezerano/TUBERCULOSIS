
import os
import sys

os.environ["BOOTSTRAP_RUNNING"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting password reset...", flush=True)

# IMPORT THE APP!
from app import app
print("Imported app successfully!", flush=True)
from models.models import db, Patient
print("Imported models", flush=True)

with app.app_context():
    print("App context active", flush=True)
    
    # Get all patients!
    all_patients = Patient.query.all()
    print(f"Found {len(all_patients)} patients!", flush=True)
    
    # Process them!
    for i, patient in enumerate(all_patients):
        patient.set_password("Patient123!")
        db.session.add(patient)
        
        if (i + 1) % 5000 == 0:
            print(f"Processed {i+1} patients, committing to DB...", flush=True)
            db.session.commit()
            
    db.session.commit()
    print(f"SUCCESS! All {len(all_patients)} patients have password Patient123!")
