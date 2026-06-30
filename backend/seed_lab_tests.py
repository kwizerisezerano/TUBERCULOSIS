
import sys
print('Starting seed script...')
sys.stdout.flush()

from app import app, db
from models.models import User, Patient, LabTest
from datetime import datetime, timedelta
import random

print('Imports complete')
sys.stdout.flush()

def seed_lab_tests():
    print('Entering seed function')
    sys.stdout.flush()
    with app.app_context():
        print('App context created')
        sys.stdout.flush()
        # Get test users
        doctor = User.query.filter_by(role='doctor').first()
        print(f'Doctor found: {doctor.username if doctor else 'NONE'}')
        sys.stdout.flush()
        
        lab_tech = User.query.filter_by(role='lab_technician').first()
        print(f'Lab tech found: {lab_tech.username if lab_tech else 'NONE'}')
        sys.stdout.flush()
        
        patients = Patient.query.all()
        print(f'Patients found: {len(patients)}')
        sys.stdout.flush()

        if not doctor or not patients:
            print('Need doctor and patients to seed!')
            return

        test_types = ['Sputum Smear', 'GeneXpert', 'Chest X-ray', 'Blood Test', 'TB Culture', 'IGRA', 'TST']

        added = 0
        # Target: 1500+ completed tests
        target_completed = 1500
        
        while LabTest.query.filter_by(status='completed').count() < target_completed:
            for patient in patients:
                # Create 1-5 tests per patient, mostly completed
                for _ in range(random.randint(1, 5)):
                    test_type = random.choice(test_types)
                    # 80% completed, 10% requested, 10% in_progress
                    status_roll = random.random()
                    if status_roll < 0.8:
                        status = 'completed'
                    elif status_roll < 0.9:
                        status = 'requested'
                    else:
                        status = 'in_progress'

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
                    
                    # Commit every 100 to prevent memory issues
                    if added % 100 == 0:
                        db.session.commit()
                        print(f'Seeded {added} tests so far, completed: {LabTest.query.filter_by(status="completed").count()}')
                        sys.stdout.flush()

        db.session.commit()
        final_completed = LabTest.query.filter_by(status='completed').count()
        print(f'Successfully seeded {added} lab tests! Total completed: {final_completed}')
        sys.stdout.flush()


if __name__ == '__main__':
    seed_lab_tests()

