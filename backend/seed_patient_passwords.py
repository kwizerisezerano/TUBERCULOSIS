
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient
from datetime import datetime

def main():
    with app.app_context():
        db.create_all()
        
        # Get ALL patients
        patients = Patient.query.all()
        
        # Assign demo passwords to ALL of them
        demo_patients = []
        for i, patient in enumerate(patients):
            # Generate a simple patient ID and password
            # Keep existing patient_id if present
            patient_id = patient.patient_id
            if not patient_id or patient_id.strip() == "":
                patient_id = f"PAT-{1000 + i}"
                patient.patient_id = patient_id
            
            password = "Patient123!"
            patient.set_password(password)
            
            # Make sure first name and last name are set
            if not patient.first_name:
                patient.first_name = f"Patient{i+1}"
            if not patient.last_name:
                patient.last_name = "Demo"
            
            demo_patients.append({
                "role": "Patient",
                "patient_id": patient_id,
                "password": password,
                "first_name": patient.first_name,
                "last_name": patient.last_name
            })
            
            db.session.add(patient)
        
        # If there are no patients, create a few!
        if len(patients) == 0:
            # Get default hospital
            from models.models import Hospital
            default_hospital = Hospital.query.filter_by(name="Default Hospital").first()
            if not default_hospital:
                default_hospital = Hospital.query.first()
            
            for i in range(5):
                patient_id = f"PAT-{1000 + i}"
                password = "Patient123!"
                
                patient = Patient(
                    patient_id=patient_id,
                    first_name=f"Patient{i+1}",
                    last_name="Demo",
                    age=30 + i,
                    gender="Male" if i % 2 == 0 else "Female"
                )
                patient.set_password(password)
                
                if default_hospital:
                    patient.hospitals.append(default_hospital)
                
                db.session.add(patient)
                
                demo_patients.append({
                    "role": "Patient",
                    "patient_id": patient_id,
                    "password": password,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name
                })
        
        db.session.commit()
        
        print("Demo patients set up successfully!")
        for dp in demo_patients[:10]:  # Only show first 10 to avoid clutter
            print(f"- {dp['first_name']} {dp['last_name']}: Patient ID = {dp['patient_id']}, Password = {dp['password']}")
        if len(demo_patients) > 10:
            print(f"... and {len(demo_patients) - 10} more patients!")

if __name__ == "__main__":
    main()
