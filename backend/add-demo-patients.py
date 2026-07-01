
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db, Patient, Hospital
from datetime import datetime, timedelta

with app.app_context():
    # Get default hospital
    default_hospital = Hospital.query.first()
    if not default_hospital:
        # Create default hospital if not exists
        default_hospital = Hospital(
            hospital_id="HOSP-0001",
            name="Default Hospital",
            facility_type='Hospital',
            city='Kigali',
            region='Kigali City',
            country='Rwanda',
            bed_capacity=200
        )
        db.session.add(default_hospital)
        db.session.commit()

    demo_patient_ids = ["SYM2024000001", "SYM2024000002", "SYM2024000003"]
    demo_names = [
        ("Jean-Pierre", "Nkurunziza"),
        ("Marie-Claire", "Uwimana"),
        ("Paul", "Rwigara")
    ]
    for idx, pid in enumerate(demo_patient_ids):
        # Check if patient exists
        existing_patient = None
        all_patients = Patient.query.all()
        for p in all_patients:
            if p.patient_id == pid:
                existing_patient = p
                break
        
        if not existing_patient:
            # Create new patient
            p = Patient(
                patient_id=pid,
                first_name=demo_names[idx][0],
                last_name=demo_names[idx][1],
                age=35 + idx,
                gender="Male" if idx !=1 else "Female"
            )
            p.set_password("Patient123!")
            p.hospitals.append(default_hospital)
            db.session.add(p)
            print(f"Created patient {pid}: {demo_names[idx][0]} {demo_names[idx][1]}")
        else:
            # Ensure has password
            if not existing_patient.password:
                existing_patient.set_password("Patient123!")
                db.session.add(existing_patient)
                print(f"Set password for existing patient {pid}")
    db.session.commit()
    print("Demo patients ready!")
