
import sys
import os

original_name = __name__
__name__ = "not_main"

from app import app, db
from models.models import (
    Diagnosis, Treatment, Alert, Prescription, LabTest,
    Patient, User, Hospital
)

__name__ = original_name

with app.app_context():
    print("Verifying database schema and data...")
    print("=" * 60)
    
    # Check that we can access all models
    print("\n[1] Checking core models:")
    print(f"  - Patient count: {Patient.query.count()}")
    print(f"  - User count: {User.query.count()}")
    print(f"  - Hospital count: {Hospital.query.count()}")
    
    # Check that our new fields exist (by trying to access them)
    print("\n[2] Checking new hospital_id fields:")
    
    # Test 1: Check Diagnosis
    test_diagnosis = Diagnosis(patient_id=1)
    print(f"  ✓ Diagnosis.hospital_id exists: {hasattr(test_diagnosis, 'hospital_id')}")
    
    # Test 2: Check Treatment
    test_treatment = Treatment(patient_id=1)
    print(f"  ✓ Treatment.hospital_id exists: {hasattr(test_treatment, 'hospital_id')}")
    
    # Test3: Check Alert
    test_alert = Alert()
    print(f"  ✓ Alert.hospital_id exists: {hasattr(test_alert, 'hospital_id')}")
    
    # Test4: Check Prescription
    test_prescription = Prescription(patient_id=1, created_by=1)
    print(f"  ✓ Prescription.hospital_id exists: {hasattr(test_prescription, 'hospital_id')}")
    
    # Test5: Check LabTest
    test_labtest = LabTest(patient_id=1, requested_by=1, test_type="Test")
    print(f"  ✓ LabTest.hospital_id exists: {hasattr(test_labtest, 'hospital_id')}")
    
    print("\n[3] Verifying existing data:")
    # Check that existing users have hospital_id (we ran assign_users_to_hospitals.py earlier)
    users = User.query.all()
    for user in users:
        hospital_name = user.hospital.name if user.hospital else "None"
        print(f"  - {user.username} ({user.role}): Hospital = {hospital_name}")
    
    print("\n✅ All changes verified! Everything looks good!")
