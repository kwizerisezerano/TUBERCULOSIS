"""
Test OTP encryption/decryption
"""
import os
import sys
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import Patient, db

sys.stdout.write("Testing OTP encryption/decryption...\n")
sys.stdout.flush()

with app.app_context():
    # Get a patient
    patient = Patient.query.first()
    if patient:
        sys.stdout.write(f"Patient ID: {patient.patient_id}\n")
        sys.stdout.write(f"Stored OTP (encrypted): {patient._otp_code}\n")
        sys.stdout.write(f"Decrypted OTP: {patient.otp_code}\n")
        sys.stdout.write(f"OTP Expires At: {patient.otp_expires_at}\n")
        sys.stdout.flush()
        
        # Test setting a new OTP
        test_otp = "123456"
        patient.otp_code = test_otp
        db.session.commit()
        
        # Retrieve and verify
        patient = Patient.query.first()
        sys.stdout.write(f"\nAfter setting OTP to '{test_otp}':\n")
        sys.stdout.write(f"Stored OTP (encrypted): {patient._otp_code}\n")
        sys.stdout.write(f"Decrypted OTP: {patient.otp_code}\n")
        sys.stdout.write(f"Match: {patient.otp_code == test_otp}\n")
        sys.stdout.flush()
    else:
        sys.stdout.write("No patients found\n")
        sys.stdout.flush()
