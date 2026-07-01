"""
Associate existing patients with the default hospital
This fixes the issue where hospital admins can't see patients because they're not linked to any hospital
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from models.models import db, Patient, Hospital
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'tb_diagnostic')

if db_password:
    database_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
else:
    database_url = f'mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}'

# Create engine and session
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Get default hospital
    default_hospital = session.query(Hospital).filter_by(name="Default Hospital").first()
    if not default_hospital:
        print("Default Hospital not found. Creating one...")
        default_hospital = Hospital(
            hospital_id="HOSP-0001",
            name="Default Hospital",
            facility_type='Hospital',
            city='Kigali',
            region='Kigali City',
            country='Rwanda',
            bed_capacity=200
        )
        session.add(default_hospital)
        session.commit()
        print(f"Created Default Hospital with ID: {default_hospital.id}")

    # Get all patients
    patients = session.query(Patient).all()
    print(f"Found {len(patients)} patients")

    # Associate patients with default hospital if they have no hospitals
    associated_count = 0
    for patient in patients:
        if not patient.hospitals:
            patient.hospitals.append(default_hospital)
            associated_count += 1

    session.commit()
    print(f"Associated {associated_count} patients with Default Hospital (ID: {default_hospital.id})")
    print("Done!")

except Exception as e:
    session.rollback()
    print(f"Error: {e}")
finally:
    session.close()

