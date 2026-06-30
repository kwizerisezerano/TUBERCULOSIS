
import sys
import os
import random

original_name = __name__
__name__ = "not_main"

from app import app, db
from models.models import (
    Diagnosis, Treatment, Alert, Prescription, LabTest,
    Patient, User, Hospital
)

__name__ = original_name

with app.app_context():
    print("=== CROSS-HOSPITAL PATIENT FLOW DEMO ===")
    print("=" * 60)
    
    # Step 1: Get our test hospitals and ANY users (not just doctors)
    print("\n[1] Getting test users and hospitals:")
    hospitals = Hospital.query.limit(2).all()
    hospital_a = hospitals[0]
    hospital_b = hospitals[1]
    
    # Get any users at Hospital A and B
    user_a = User.query.filter_by(hospital_id=hospital_a.id).first()
    user_b = User.query.filter_by(hospital_id=hospital_b.id).first()
    
    print(f"  - Hospital A: {hospital_a.name} (ID: {hospital_a.id})")
    print(f"    User: {user_a.username if user_a else 'None'} ({user_a.role if user_a else ''})")
    print(f"  - Hospital B: {hospital_b.name} (ID: {hospital_b.id})")
    print(f"    User: {user_b.username if user_b else 'None'} ({user_b.role if user_b else ''})")
    
    # Step 2: Get or create a test patient
    print("\n[2] Creating test patient at Hospital A:")
    test_patient = Patient.query.filter_by(patient_id="TEST-CROSS-HOSP-001").first()
    if not test_patient:
        test_patient = Patient(
            patient_id="TEST-CROSS-HOSP-001",
            first_name="Test",
            last_name="Patient",
            age=35,
            gender="Male",
            hospital_id=hospital_a.id,
            symptoms="Cough, fever, night sweats",
            tb_status_label="Yes"
        )
        db.session.add(test_patient)
        db.session.commit()
        print(f"  ✓ Created patient: {test_patient.patient_id} at {hospital_a.name}")
    else:
        print(f"  ✓ Found existing test patient: {test_patient.patient_id}")
    
    # Step 3: User A creates a diagnosis at Hospital A (if we have user_a)
    if user_a:
        print("\n[3] User A creates a diagnosis for patient at Hospital A:")
        existing_diagnosis_a = Diagnosis.query.filter_by(patient_id=test_patient.id, hospital_id=hospital_a.id).first()
        if not existing_diagnosis_a:
            diagnosis_a = Diagnosis(
                patient_id=test_patient.id,
                clinician_id=user_a.id,
                hospital_id=hospital_a.id,
                diagnosis_type="Pulmonary TB",
                risk_level="high",
                confidence_percent=85.5,
                details='{"tb_types": ["pulmonary"]}',
                status="completed"
            )
            db.session.add(diagnosis_a)
            
            # Also create a lab test at Hospital A
            labtest_a = LabTest(
                patient_id=test_patient.id,
                requested_by=user_a.id,
                hospital_id=hospital_a.id,
                test_type="GeneXpert",
                status="completed",
                results="Positive"
            )
            db.session.add(labtest_a)
            
            db.session.commit()
            print(f"  ✓ Diagnosis created at Hospital A")
            print(f"  ✓ Lab test created at Hospital A")
        else:
            print(f"  ✓ Existing diagnosis at Hospital A found")
    
    # Step 4: User B at Hospital B creates a follow-up record
    if user_b:
        print("\n[4] User B creates a follow-up lab test at Hospital B:")
        existing_diagnosis_b = Diagnosis.query.filter_by(patient_id=test_patient.id, hospital_id=hospital_b.id).first()
        if not existing_diagnosis_b:
            labtest_b = LabTest(
                patient_id=test_patient.id,
                requested_by=user_b.id,
                hospital_id=hospital_b.id,
                test_type="Chest X-ray",
                status="completed",
                results="Abnormal"
            )
            db.session.add(labtest_b)
            
            diagnosis_b = Diagnosis(
                patient_id=test_patient.id,
                clinician_id=user_b.id,
                hospital_id=hospital_b.id,
                diagnosis_type="Follow-up TB evaluation",
                risk_level="medium",
                confidence_percent=72.3,
                details='{"follow_up": true}',
                status="completed"
            )
            db.session.add(diagnosis_b)
            
            db.session.commit()
            print(f"  ✓ Lab test created at Hospital B")
            print(f"  ✓ Diagnosis created at Hospital B")
        else:
            print(f"  ✓ Existing records at Hospital B found")
    
    # Step 5: Verify access
    print("\n[5] Verifying access:")
    from sqlalchemy import or_
    
    if user_a and user_a.hospital_id:
        doc_a_query = Patient.query.filter(
            or_(
                Patient.hospital_id == user_a.hospital_id,
                Patient.id.in_(db.session.query(Diagnosis.patient_id).filter(Diagnosis.hospital_id == user_a.hospital_id)),
                Patient.id.in_(db.session.query(LabTest.patient_id).filter(LabTest.hospital_id == user_a.hospital_id))
            )
        )
        doc_a_patients = doc_a_query.filter(Patient.id == test_patient.id).all()
        print(f"  User A can see patient: {len(doc_a_patients) > 0}")
    
    if user_b and user_b.hospital_id:
        doc_b_query = Patient.query.filter(
            or_(
                Patient.hospital_id == user_b.hospital_id,
                Patient.id.in_(db.session.query(Diagnosis.patient_id).filter(Diagnosis.hospital_id == user_b.hospital_id)),
                Patient.id.in_(db.session.query(LabTest.patient_id).filter(LabTest.hospital_id == user_b.hospital_id))
            )
        )
        doc_b_patients = doc_b_query.filter(Patient.id == test_patient.id).all()
        print(f"  User B can see patient: {len(doc_b_patients) > 0}")
    
    # Show all records
    print("\n[6] Patient's full cross-hospital medical history:")
    all_diagnoses = Diagnosis.query.filter_by(patient_id=test_patient.id).all()
    for d in all_diagnoses:
        hosp_name = d.hospital.name if d.hospital else "Unknown"
        print(f"  - {d.diagnosis_type} at {hosp_name} ({d.created_at.date()})")
    
    all_labtests = LabTest.query.filter_by(patient_id=test_patient.id).all()
    for l in all_labtests:
        hosp_name = l.hospital.name if l.hospital else "Unknown"
        print(f"  - {l.test_type}: {l.results} at {hosp_name}")
    
    print("\n✅ CROSS-HOSPITAL INTEROPERABILITY DEMO SUCCESSFUL!")
    print("\nKey features:")
    print("- Patients can have records at multiple hospitals")
    print("- Users see patients from their primary hospital AND any patient their hospital has records for")
    print("- Full medical history is available across hospitals")
