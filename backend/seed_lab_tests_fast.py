
import sys
import os

# Modify sys.modules to prevent app.py from running the server
sys.modules['__main__'] = sys.modules[__name__]

from app import app, db
from models.models import User, Patient, LabTest
from datetime import datetime, timedelta
import random


def seed_lab_tests():
    with app.app_context():
        # Get test users
        doctor = User.query.filter_by(role='doctor').first()
        lab_tech = User.query.filter_by(role='lab_technician').first()
        patients = Patient.query.limit(20).all()

        if not doctor or not patients:
            print('Need doctor and patients to seed!')
            return

        test_types = ['Sputum Smear', 'GeneXpert', 'Chest X-ray', 'Blood Test', 'TB Culture', 'IGRA', 'TST']
        statuses = ['requested', 'in_progress', 'completed']

        added = 0
        for patient in patients:
            for _ in range(random.randint(1, 3)):
                test_type = random.choice(test_types)
                status = random.choice(statuses)

                completed_by = None
                completed_at = None
                results = None
                if status == 'completed' and lab_tech:
                    completed_by = lab_tech.id
                    completed_at = datetime.now() - timedelta(days=random.randint(0, 30))
                    results = random.choice(['Positive', 'Negative', 'Abnormal', 'Normal', 'Inconclusive'])

                test = LabTest(
                    patient_id=patient.id,
                    requested_by=doctor.id,
                    test_type=test_type,
                    status=status,
                    completed_by=completed_by,
                    completed_at=completed_at,
                    results=results
                )
                db.session.add(test)
                added += 1

        db.session.commit()
        print(f'Successfully seeded {added} lab tests!')


if __name__ == '__main__':
    seed_lab_tests()

