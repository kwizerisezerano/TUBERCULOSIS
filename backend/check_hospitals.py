
import sys

original_name = __name__
__name__ = 'not_main'

from app import app, db
from models.models import Hospital, Patient, User

__name__ = original_name

with app.app_context():
    print('=== HOSPITALS ===')
    hospitals = Hospital.query.all()
    print(f'Total hospitals: {len(hospitals)}')
    for hospital in hospitals:
        patient_count = Patient.query.filter_by(hospital_id=hospital.id).count()
        user_count = User.query.filter_by(hospital_id=hospital.id).count()
        print(f'  Hospital {hospital.id}: {hospital.name} ({hospital.hospital_id}')
        print(f'    Patients: {patient_count}')
        print(f'    Users: {user_count}')
    
    print('\n=== PATIENTS WITH HOSPITAL ===')
    patients_no_hospital = Patient.query.filter_by(hospital_id=None).count()
    print(f'Patients without hospital: {patients_no_hospital}')
    
    patients_with_hospital = Patient.query.filter(Patient.hospital_id.isnot(None)).count()
    print(f'Patients with hospital: {patients_with_hospital}')
    
    print('\n=== USERS WITH HOSPITAL ===')
    users = User.query.all()
    for user in users:
        hospital_name = user.hospital.name if user.hospital else 'None'
        print(f'  {user.username} ({user.role}) - Hospital: {hospital_name}')
