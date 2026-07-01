
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient
from datetime import datetime

with app.app_context():
    db.create_all()
    
    # Get first 5 existing patients
    patients = Patient.query.limit(5).all()
    
    # Assign passwords and collect their info
    demo_patients = []
    for patient in patients:
        # If patient doesn't have a password yet, set one!
        if not patient.password:
            patient.set_password("Patient123!")
            db.session.add(patient)
        
        demo_patients.append({
            "role": f"Patient ({patient.first_name or 'First'} {patient.last_name or 'Last'})",
            "patient_id": patient.patient_id,
            "pwd": "Patient123!"
        })
    
    db.session.commit()
    
    # Print them out as a JS array so we can copy-paste into index.vue!
    print("Copy this patientCredentials into index.vue:")
    print("const patientCredentials = [")
    for dp in demo_patients:
        print(f"    {{ role: '{dp['role']}', patient_id: '{dp['patient_id']}', pwd: '{dp['pwd']}' }},")
    print("];")
