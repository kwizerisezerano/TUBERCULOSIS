"""
Simple script to test alerts without starting server
"""
import sys
import os

# Prevent app from running
os.environ['FLASK_ENV'] = 'production'

from app import app, db
from models.models import Alert, Patient, Hospital

with app.app_context():
    print("=== Alert System Test ===\n")
    
    # Check hospitals
    hospitals = Hospital.query.count()
    print(f"Hospitals in DB: {hospitals}")
    
    # Check patients
    patients = Patient.query.count()
    print(f"Patients in DB: {patients}")
    
    # Check alerts
    alerts = Alert.query.all()
    print(f"\nAlerts in DB: {len(alerts)}")
    
    if alerts:
        print("\n--- Alert Details ---")
        for alert in alerts:
            print(f"  ID: {alert.id}")
            print(f"  Type: {alert.alert_type}")
            print(f"  Severity: {alert.severity}")
            print(f"  Hospital: {alert.hospital_id}")
            print(f"  Read: {alert.is_read}")
            print(f"  Message: {alert.message[:60]}...")
            print("  ---")
    else:
        print("\nNo alerts found! Let's create some...")
        
        # Get first hospital and patient
        hospital = Hospital.query.first()
        patient = Patient.query.first()
        
        if hospital and patient:
            print(f"Creating sample alerts for Hospital {hospital.name} and Patient {patient.patient_id}")
            
            # Create sample alert 1
            alert1 = Alert(
                patient_id=patient.id,
                hospital_id=hospital.id,
                alert_type='mdr_tb_suspected',
                message=f"MDR-TB Suspected: Patient {patient.patient_id} shows signs of multidrug-resistant TB.",
                severity='critical',
                is_read=False
            )
            
            # Create sample alert 2
            alert2 = Alert(
                patient_id=patient.id,
                hospital_id=hospital.id,
                alert_type='treatment_failure_risk',
                message=f"Treatment Failure Risk Alert: Patient {patient.patient_id} has 85% probability of failure.",
                severity='critical',
                is_read=False
            )
            
            # Create sample alert 3
            alert3 = Alert(
                patient_id=None,
                hospital_id=hospital.id,
                alert_type='low_stock',
                message=f"Low Stock Alert: Isoniazid at {hospital.name}.",
                severity='high',
                is_read=True
            )
            
            db.session.add_all([alert1, alert2, alert3])
            db.session.commit()
            
            print(f"Created {Alert.query.count()} alerts successfully!")
