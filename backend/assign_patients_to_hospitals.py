
import sys

original_name = __name__
__name__ = 'not_main'

from app import app, db
from models.models import Hospital, Patient
import random

__name__ = original_name

with app.app_context():
    print('=== ASSIGNING PATIENTS TO HOSPITALS ===')
    
    # Get all hospitals
    hospitals = Hospital.query.all()
    print(f'Total hospitals: {len(hospitals)}')
    
    # Get patients without hospital
    patients = Patient.query.filter_by(hospital_id=None).limit(5000).all()
    print(f'Patients to assign: {len(patients)}')
    
    # Assign each patient to a random hospital
    count = 0
    for patient in patients:
        hospital = random.choice(hospitals)
        patient.hospital_id = hospital.id
        db.session.add(patient)
        count += 1
        if count % 500 == 0:
            db.session.commit()
            print(f'  Assigned {count} patients...')
    
    db.session.commit()
    
    print(f'\n✅ Done! Assigned {count} patients to hospitals.')
