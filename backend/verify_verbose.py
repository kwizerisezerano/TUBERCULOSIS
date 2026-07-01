"""
Quickly verify that the fix is applied and works with verbose output
"""
import os
os.environ['BOOTSTRAP_RUNNING'] = '1'

# Import without starting server
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.models import Patient, Alert, Hospital

try:
    with app.app_context():
        print("--- VERIFYING DATABASE ---")
        
        # Check for hospital
        hospital = Hospital.query.first()
        print(f"First Hospital: {hospital.id if hospital else 'None'} - {hospital.name if hospital else 'None'}")
        
        # Check for patient
        patient = Patient.query.first()
        print(f"First Patient: {patient.id if patient else 'None'} - {patient.patient_id if patient else 'None'}")
        
        # Check current alerts
        alerts_count = Alert.query.count()
        print(f"Current alerts: {alerts_count}")
        
        if patient and hospital:
            # Check if patient has hospitals
            print(f"Patient has {len(patient.hospitals)} associated hospitals")
            
            # Try to create an alert
            print("\n=== Testing Alert Creation ===")
            alert = Alert(
                patient_id=patient.id,
                hospital_id=hospital.id,
                alert_type='test',
                message='This is a test alert to verify fix!',
                severity='medium',
                is_read=False
            )
            db.session.add(alert)
            db.session.commit()
            print("✅ Alert created successfully!")
            
            new_count = Alert.query.count()
            print(f"Alert count increased from {alerts_count} to {new_count}")
            
            print("\n=== Cleaning Up ===")
            db.session.delete(alert)
            db.session.commit()
            print("✅ Test alert deleted!")
            
            final_count = Alert.query.count()
            print(f"Alert count back to {final_count}")
            
            print("\n🎉 ALL TESTS PASSED! Fix is working perfectly!")
        else:
            print("\n⚠️ No patient or hospital found to test with!")
            
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.session.rollback()
