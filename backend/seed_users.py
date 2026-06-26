
"""
Seed the database with users, roles, and sample data
"""
import random
from datetime import datetime, timedelta
from app import app
from models.models import db, User, Patient, ATCDrug, LabTest, Prescription, Diagnosis, Treatment, Alert, AuditLog

users = [
    {
        "username": "divinekageruka",
        "email": "divinekageruka@gmail.com",
        "password": "Admin123!",
        "role": "system_admin"
    },
    {
        "username": "igiranezac459",
        "email": "igiranezac459@gmail.com",
        "password": "Doctor123!",
        "role": "doctor"
    },
    {
        "username": "clarisseigiraneza56",
        "email": "clarisseigiraneza56@gmail.com",
        "password": "LabTech123!",
        "role": "lab_technician"
    },
    {
        "username": "clarisseigiraneza915",
        "email": "clarisseigiraneza915@gmail.com",
        "password": "Pharm123!",
        "role": "pharmacist"
    },
    {
        "username": "igiclarisse10",
        "email": "igiclarisse10@gmail.com",
        "password": "Admin123!",
        "role": "hospital_admin"
    }
]

sample_atc_drugs = [
    {
        "atc_code": "J01CA04",
        "atc_level_1": "J",
        "atc_level_2": "J01",
        "atc_level_3": "J01C",
        "atc_level_4": "J01CA",
        "atc_level_5": "J01CA04",
        "drug_name": "Amoxicillin",
        "ddd": 1.0,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J01CR02",
        "atc_level_1": "J",
        "atc_level_2": "J01",
        "atc_level_3": "J01C",
        "atc_level_4": "J01CR",
        "atc_level_5": "J01CR02",
        "drug_name": "Amoxicillin and beta-lactamase inhibitor",
        "ddd": 1.5,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J01DD04",
        "atc_level_1": "J",
        "atc_level_2": "J01",
        "atc_level_3": "J01D",
        "atc_level_4": "J01DD",
        "atc_level_5": "J01DD04",
        "drug_name": "Ceftriaxone",
        "ddd": 2.0,
        "ddd_unit": "g",
        "administration_route": "Injectable"
    },
    {
        "atc_code": "J01MA01",
        "atc_level_1": "J",
        "atc_level_2": "J01",
        "atc_level_3": "J01M",
        "atc_level_4": "J01MA",
        "atc_level_5": "J01MA01",
        "drug_name": "Ciprofloxacin",
        "ddd": 1.0,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J01GB03",
        "atc_level_1": "J",
        "atc_level_2": "J01",
        "atc_level_3": "J01G",
        "atc_level_4": "J01GB",
        "atc_level_5": "J01GB03",
        "drug_name": "Gentamicin",
        "ddd": 0.24,
        "ddd_unit": "g",
        "administration_route": "Injectable"
    },
    {
        "atc_code": "J01DH02",
        "atc_level_1": "J",
        "atc_level_2": "J01",
        "atc_level_3": "J01D",
        "atc_level_4": "J01DH",
        "atc_level_5": "J01DH02",
        "drug_name": "Meropenem",
        "ddd": 2.0,
        "ddd_unit": "g",
        "administration_route": "Injectable"
    },
    {
        "atc_code": "J04AK02",
        "atc_level_1": "J",
        "atc_level_2": "J04",
        "atc_level_3": "J04A",
        "atc_level_4": "J04AK",
        "atc_level_5": "J04AK02",
        "drug_name": "Isoniazid and pyrazinamide and rifampicin",
        "ddd": 0.6,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J04AK01",
        "atc_level_1": "J",
        "atc_level_2": "J04",
        "atc_level_3": "J04A",
        "atc_level_4": "J04AK",
        "atc_level_5": "J04AK01",
        "drug_name": "Isoniazid and rifampicin",
        "ddd": 0.45,
        "ddd_unit": "g",
        "administration_route": "Oral"
    }
]

def seed_users():
    with app.app_context():
        db.create_all()
        
        added = 0
        
        for user_data in users:
            existing = User.query.filter_by(email=user_data["email"]).first()
            if existing:
                continue
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            added += 1
        
        db.session.commit()
        return {"added": added, "total": User.query.count()}

def seed_sample_data():
    with app.app_context():
        # Seed ATC drugs only (no other sample data - diagnoses/prescriptions come from /api/diagnose)
        added_atc = 0
        for drug_data in sample_atc_drugs:
            existing = ATCDrug.query.filter_by(atc_code=drug_data['atc_code']).first()
            if existing:
                continue
            drug = ATCDrug(**drug_data)
            db.session.add(drug)
            added_atc += 1
        
        db.session.commit()
        
        return {
            "added_atc_drugs": added_atc,
            "added_lab_tests": 0,
            "added_prescriptions": 0,
            "added_diagnoses": 0,
            "added_treatments": 0,
            "added_alerts": 0
        }

def seed_all():
    users_result = seed_users()
    sample_result = seed_sample_data()
    return {"users": users_result, "sample_data": sample_result}
        
if __name__ == "__main__":
    result = seed_all()
    print(result)
