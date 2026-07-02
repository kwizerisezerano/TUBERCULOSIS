
"""
Update all existing patients to have phone numbers for OTP testing
"""
import os
import sys
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient

# Single phone number for testing OTP
TEST_PHONE = "+250 780 219 351"

def main():
    print("Starting patient phone number update...", file=sys.stderr, flush=True)
    with app.app_context():
        db.create_all()
        
        # Get ALL patients
        patients = Patient.query.all()
        print(f"Total patients in database: {len(patients)}", file=sys.stderr, flush=True)
        
        updated_count = 0
        
        for patient in patients:
            patient.phone_number = TEST_PHONE
            db.session.add(patient)
            updated_count += 1
                
        db.session.commit()
        
        print(f"Updated {updated_count} patients with phone number {TEST_PHONE}!", file=sys.stderr, flush=True)
        
        # Verify
        patients_without_phone = Patient.query.filter(Patient._phone_number.is_(None)).count()
        print(f"Patients without phone number now: {patients_without_phone}", file=sys.stderr, flush=True)
        
        # Show first few patients
        print("\nFirst 5 patients:", file=sys.stderr, flush=True)
        for patient in patients[:5]:
            print(f"Patient ID: {patient.patient_id}, Phone: {patient.phone_number}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
