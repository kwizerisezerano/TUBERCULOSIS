"""
Set phone numbers for all patients
"""
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient
import random

# Sample Rwandan phone numbers (starts with +250)
DEFAULT_PHONE = "+250 780 219 351"
SAMPLE_PHONES = ["+250 780 219 351"]

def main():
    with app.app_context():
        db.create_all()
        
        # Get ALL patients
        patients = Patient.query.all()
        batch_size = 100  # Process in batches for speed
        updated_count = 0
        
        # Assign phone numbers to ALL patients (use default for all)
        for i, patient in enumerate(patients):
            # Keep existing patient_id if present
            patient_id = patient.patient_id
            if not patient_id or patient_id.strip() == "":
                patient_id = f"PAT-{1000 + i}"
                patient.patient_id = patient_id
            
            # Assign phone number to ALL patients
            patient.phone_number = DEFAULT_PHONE
            updated_count += 1
            
            # Make sure first name and last name are set
            if not patient.first_name:
                patient.first_name = f"Patient{i+1}"
            if not patient.last_name:
                patient.last_name = "Demo"
            
            db.session.add(patient)
            
            # Commit every 100 patients to avoid memory issues and show progress
            if (i + 1) % batch_size == 0:
                db.session.commit()
                print(f"      Processed {i + 1}/{len(patients)} patients (updated {updated_count} phones)...")
        
        # Final commit for remaining patients
        if len(patients) > 0:
            db.session.commit()
        
        # If there are no patients, create a few!
        if len(patients) == 0:
            # Get default hospital
            from models.models import Hospital
            default_hospital = Hospital.query.filter_by(name="Default Hospital").first()
            if not default_hospital:
                default_hospital = Hospital.query.first()
            
            for i in range(5):
                patient_id = f"PAT-{1000 + i}"
                
                patient = Patient(
                    patient_id=patient_id,
                    first_name=f"Patient{i+1}",
                    last_name="Demo",
                    age=30 + i,
                    gender="Male" if i % 2 == 0 else "Female"
                )
                patient.phone_number = DEFAULT_PHONE
                
                if default_hospital:
                    patient.hospitals.append(default_hospital)
                
                db.session.add(patient)
            
            db.session.commit()
            updated_count = 5
        
        print(f"\nSuccessfully updated {updated_count} patients with phone numbers!")
        
        # Show first few patients
        all_patients = Patient.query.all()
        print("\nFirst 5 patients:")
        for patient in all_patients[:5]:
            print(f"Patient ID: {patient.patient_id}, Phone: {patient.phone_number}, Name: {patient.first_name} {patient.last_name}")

if __name__ == "__main__":
    main()
