"""
Encrypt all patient phone numbers that are stored in plaintext
"""
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient
from utils.security import encrypt_data, decrypt_data

def main():
    with app.app_context():
        db.create_all()
        
        # Get ALL patients
        patients = Patient.query.all()
        batch_size = 100
        encrypted_count = 0
        
        print(f"Checking {len(patients)} patients for plaintext phone numbers...")
        
        for i, patient in enumerate(patients):
            # Check if phone number is stored as plaintext (not encrypted)
            # by trying to decrypt it - if it returns the same value, it's plaintext
            if patient._phone_number:  # Check if there's a stored value
                try:
                    # Try to decrypt
                    decrypted = decrypt_data(patient._phone_number)
                    # If decrypted is same as stored value, it was plaintext
                    if decrypted == patient._phone_number:
                        # It's plaintext, encrypt it!
                        patient._phone_number = encrypt_data(decrypted)
                        encrypted_count += 1
                        db.session.add(patient)
                except:
                    # If decryption fails, it's already encrypted (or invalid)
                    pass
            
            # Commit every 100 patients
            if (i + 1) % batch_size == 0:
                db.session.commit()
                print(f"      Processed {i + 1}/{len(patients)} patients (encrypted {encrypted_count} phones)...")
        
        # Final commit
        if len(patients) > 0:
            db.session.commit()
        
        print(f"\nSuccessfully encrypted {encrypted_count} phone numbers!")
        
        # Verify a few patients
        all_patients = Patient.query.all()
        print("\nVerification - first 5 patients:")
        for patient in all_patients[:5]:
            print(f"Patient ID: {patient.patient_id}, Phone: {patient.phone_number}")

if __name__ == "__main__":
    main()
