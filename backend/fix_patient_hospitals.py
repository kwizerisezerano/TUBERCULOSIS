
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"

from app import app, db
from models.models import Hospital, Patient
import random

with app.app_context():
    print('=== ASSIGNING PATIENTS TO HOSPITALS (MANY-TO-MANY) ===')
    
    # Get all hospitals
    hospitals = Hospital.query.all()
    print(f'Total hospitals: {len(hospitals)}')
    
    if not hospitals:
        print('No hospitals found!')
        exit()
    
    # Get all patients
    patients = Patient.query.all()
    print(f'Total patients: {len(patients)}')
    
    count = 0
    for patient in patients:
        # Check if patient already has hospitals
        if len(patient.hospitals) == 0:
            # Assign to random hospital
            hospital = random.choice(hospitals)
            patient.hospitals.append(hospital)
            count += 1
            if count % 500 == 0:
                db.session.commit()
                print(f'  Assigned {count} patients...')
    
    db.session.commit()
    
    print(f'\n✅ Done! Assigned {count} patients to hospitals.')

