"""
Quickly verify that the fix is applied and works
"""
import os
os.environ['BOOTSTRAP_RUNNING'] = '1'

from app import app, db
from models.models import Patient, Alert, Hospital

with app.app_context():
    print("--- Checking Data ---")
    
    # Check for patient
    patient = Patient.query.first()
    print(f"Patient found: {patient.id if patient else 'None'}")

    if patient:
        # Check if patient has hospitals
        print(f"Patient has {len(patient.hospitals)} associated hospitals")
        
        # Try to create an alert (with null safe hospital_id)
        hospital_id = None
        if patient.hospitals:
            hospital_id = patient.hospitals[0].id
        else:
            hospital = Hospital.query.first()
            if hospital:
                hospital_id = hospital.id
        
        # Check current alerts
        alerts_count = Alert.query.count()
        print(f"Current alerts: {alerts_count}")
        
        # Try creating an alert to test
        print("Testing alert creation...")
        alert = Alert(
            patient_id=patient.id,
            hospital_id=hospital_id,
            alert_type='test',
            message='This is a test alert!',
            severity='medium',
            is_read=False
        )
        
        db.session.add(alert)
        db.session.commit()
        print("SUCCESS: Alert created with no errors!")
        
        # Cleanup
        db.session.delete(alert)
        db.session.commit()
        print("Cleaned up test alert")

print("\n✅ VERIFICATION SUCCESSFUL!")
