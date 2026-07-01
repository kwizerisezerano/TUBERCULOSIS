"""
Seed sample alerts for testing
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.models import Alert, Patient, Hospital

def seed_alerts():
    with app.app_context():
        # Get first hospital and patient for sample alerts
        hospital = Hospital.query.first()
        patient = Patient.query.first()
        
        if not hospital or not patient:
            print("Please seed hospitals and patients first!")
            return
        
        # Check if alerts already exist
        existing_alerts = Alert.query.count()
        if existing_alerts > 0:
            print(f"Found {existing_alerts} existing alerts. Skipping seeding.")
            return
        
        # Create sample alerts
        alerts_data = [
            {
                'patient_id': patient.id,
                'hospital_id': hospital.id,
                'alert_type': 'mdr_tb_suspected',
                'message': f"MDR-TB Suspected: Patient {patient.patient_id} shows signs of multidrug-resistant TB. Immediate DST and treatment review required.",
                'severity': 'critical',
                'is_read': False
            },
            {
                'patient_id': patient.id,
                'hospital_id': hospital.id,
                'alert_type': 'treatment_failure_risk',
                'message': f"Treatment Failure Risk Alert: Patient {patient.patient_id} has 85.2% probability of treatment failure. Consider regimen adjustment.",
                'severity': 'critical',
                'is_read': False
            },
            {
                'patient_id': patient.id,
                'hospital_id': hospital.id,
                'alert_type': 'critical_lab_result',
                'message': f"Critical Lab Result Available: GeneXpert for patient {patient.patient_id}. Results: MTB DETECTED, RIF RESISTANCE DETECTED.",
                'severity': 'critical',
                'is_read': True
            },
            {
                'patient_id': patient.id,
                'hospital_id': hospital.id,
                'alert_type': 'antibiotic_misuse',
                'message': f"Antibiotic Misuse Detected: Overprescription for patient {patient.patient_id}. Review medication history.",
                'severity': 'high',
                'is_read': False
            },
            {
                'patient_id': None,
                'hospital_id': hospital.id,
                'alert_type': 'low_stock',
                'message': f"Low Stock Alert: Isoniazid at {hospital.name}. Current: 5, Threshold: 10",
                'severity': 'high',
                'is_read': False
            }
        ]
        
        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            db.session.add(alert)
        
        db.session.commit()
        
        print(f"Successfully seeded {len(alerts_data)} alerts!")

if __name__ == '__main__':
    seed_alerts()
