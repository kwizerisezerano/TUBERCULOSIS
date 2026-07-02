
"""
Seed the database with users, roles, and sample data
"""
import random
from datetime import datetime, timedelta
# Defer app import to avoid circular dependency during bootstrap
from models.models import db, User, Patient, ATCDrug, LabTest, Prescription, Diagnosis, Treatment, Alert, AuditLog, Hospital

users = [
    {
        "username": "divinekageruka",
        "email": "divinekageruka@gmail.com",
        "password": "Admin123!",
        "role": "admin"
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

# Additional test users distributed across hospitals for interoperability testing
test_users = [
    {
        "username": "doctor_hosp2",
        "email": "doctor2@hospital2.com",
        "password": "Doctor123!",
        "role": "doctor"
    },
    {
        "username": "doctor_hosp3",
        "email": "doctor3@hospital3.com",
        "password": "Doctor123!",
        "role": "doctor"
    },
    {
        "username": "labtech_hosp2",
        "email": "labtech2@hospital2.com",
        "password": "LabTech123!",
        "role": "lab_technician"
    },
    {
        "username": "labtech_hosp3",
        "email": "labtech3@hospital3.com",
        "password": "LabTech123!",
        "role": "lab_technician"
    },
    {
        "username": "pharmacist_hosp2",
        "email": "pharmacist2@hospital2.com",
        "password": "Pharm123!",
        "role": "pharmacist"
    },
    {
        "username": "pharmacist_hosp3",
        "email": "pharmacist3@hospital3.com",
        "password": "Pharm123!",
        "role": "pharmacist"
    },
    {
        "username": "hospitaladmin_hosp2",
        "email": "admin2@hospital2.com",
        "password": "Admin123!",
        "role": "hospital_admin"
    },
    {
        "username": "hospitaladmin_hosp3",
        "email": "admin3@hospital3.com",
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
    {"atc_code": "J04AC01", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AC", "atc_level_5": "J04AC01", "drug_name": "Isoniazid",     "ddd": 0.3,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AB02", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AB", "atc_level_5": "J04AB02", "drug_name": "Rifampicin",    "ddd": 0.6,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AK01", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AK", "atc_level_5": "J04AK01", "drug_name": "Pyrazinamide", "ddd": 1.5,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AK02", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AK", "atc_level_5": "J04AK02", "drug_name": "Ethambutol",   "ddd": 1.2,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AM01", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AM", "atc_level_5": "J04AM01", "drug_name": "Streptomycin", "ddd": 1.0,  "ddd_unit": "g", "administration_route": "Injectable"},
    {"atc_code": "J04AK03", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AK", "atc_level_5": "J04AK03", "drug_name": "Bedaquiline",  "ddd": 0.2,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AK06", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AK", "atc_level_5": "J04AK06", "drug_name": "Delamanid",   "ddd": 0.2,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AK05", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AK", "atc_level_5": "J04AK05", "drug_name": "Linezolid",   "ddd": 1.2,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J01MA12", "atc_level_1": "J", "atc_level_2": "J01", "atc_level_3": "J01M", "atc_level_4": "J01MA", "atc_level_5": "J01MA12", "drug_name": "Levofloxacin","ddd": 0.5,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J01MA14", "atc_level_1": "J", "atc_level_2": "J01", "atc_level_3": "J01M", "atc_level_4": "J01MA", "atc_level_5": "J01MA14", "drug_name": "Moxifloxacin","ddd": 0.4,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AK04", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AK", "atc_level_5": "J04AK04", "drug_name": "Clofazimine", "ddd": 0.1,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J01XX08", "atc_level_1": "J", "atc_level_2": "J01", "atc_level_3": "J01X", "atc_level_4": "J01XX", "atc_level_5": "J01XX08", "drug_name": "Cycloserine", "ddd": 0.5,  "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AB04", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AB", "atc_level_5": "J04AB04", "drug_name": "Rifabutin",   "ddd": 0.15, "ddd_unit": "g", "administration_route": "Oral"},
    {"atc_code": "J04AB03", "atc_level_1": "J", "atc_level_2": "J04", "atc_level_3": "J04A", "atc_level_4": "J04AB", "atc_level_5": "J04AB03", "drug_name": "Rifapentine", "ddd": 0.6,  "ddd_unit": "g", "administration_route": "Oral"},
]

def get_or_create_named_hospital(name, hospital_id_code, city="Kigali"):
    """Get or create a hospital by name, ensuring it always exists."""
    from models.models import Hospital, db
    hospital = Hospital.query.filter_by(name=name).first()
    if not hospital:
        hospital = Hospital(
            hospital_id=hospital_id_code,
            name=name,
            facility_type='Hospital',
            city=city,
            region='Kigali City',
            country='Rwanda',
            bed_capacity=200
        )
        db.session.add(hospital)
        db.session.commit()
    return hospital


def resolve_test_user_hospital(user_data, default_hospital):
    username = user_data.get("username", "")
    if username.endswith("hosp2"):
        return get_or_create_named_hospital("Test Hospital 2", "HOSP-TEST-002")
    if username.endswith("hosp3"):
        return get_or_create_named_hospital("Test Hospital 3", "HOSP-TEST-003")
    return default_hospital


def seed_users():
    # Import app only when needed
    from app import app
    with app.app_context():
        db.create_all()
        
        # Get or create default hospital for original users
        default_hospital = Hospital.query.filter_by(name="Default Hospital").first()
        if not default_hospital:
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
        
        # Get all available hospitals for test user distribution
        hospitals = Hospital.query.all()
        if not hospitals:
            hospitals = [default_hospital]
        
        added = 0
        updated = 0
        
        # Seed original users - keep them in default hospital
        for user_data in users:
            existing = User.query.filter_by(email=user_data["email"]).first()
            if existing:
                # Ensure original users are in default hospital
                if existing.hospital_id is None:
                    existing.hospital_id = default_hospital.id
                    updated += 1
                continue
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                hospital_id=default_hospital.id
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            added += 1
        
        # Seed test users - all hosp2 users share "Test Hospital 2", all hosp3 users share "Test Hospital 3"
        for user_data in test_users:
            existing = User.query.filter_by(email=user_data["email"]).first()
            hospital = resolve_test_user_hospital(user_data, default_hospital)

            if existing:
                if existing.hospital_id != hospital.id:
                    existing.hospital_id = hospital.id
                    updated += 1
                continue
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                hospital_id=hospital.id
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            added += 1
        
        db.session.commit()
        return {"added": added, "updated": updated, "total": User.query.count()}

def seed_sample_data():
    # Import app only when needed
    from app import app
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
        
        # Get default hospital for lab tests
        default_hospital = Hospital.query.filter_by(name="Default Hospital").first()
        if not default_hospital:
            default_hospital = Hospital.query.first()
        
        # Seed sample lab tests
        added_lab_tests = 0
        patients = Patient.query.limit(20).all()
        doctors = User.query.filter_by(role='doctor').all()
        lab_techs = User.query.filter_by(role='lab_technician').all()
        
        if patients and doctors and default_hospital:
            test_types = ["GeneXpert", "Sputum Smear", "Chest X-ray", "Blood Test", "TB Culture", "IGRA", "TST"]
            statuses = ["requested", "in_progress", "completed"]
            
            for i, patient in enumerate(patients):
                for test_type in random.sample(test_types, random.randint(1, 3)):
                    status = random.choice(statuses)
                    requested_by = random.choice(doctors)
                    # Use the requesting doctor's hospital so lab techs at the same hospital can see it
                    test_hospital_id = requested_by.hospital_id or default_hospital.id
                    # Pick a lab tech from the same hospital if possible
                    same_hosp_techs = [t for t in lab_techs if t.hospital_id == test_hospital_id]
                    eligible_techs = same_hosp_techs or lab_techs
                    completed_by = random.choice(eligible_techs) if status == "completed" and eligible_techs else None
                    completed_at = datetime.now() - timedelta(days=random.randint(1, 30)) if status == "completed" else None

                    results = None
                    if status == "completed":
                        possible_results = ["Positive", "Negative", "Abnormal", "Normal", "Inconclusive"]
                        results = random.choice(possible_results)

                    test = LabTest(
                        patient_id=patient.id,
                        requested_by=requested_by.id,
                        hospital_id=test_hospital_id,
                        test_type=test_type,
                        status=status,
                        results=results,
                        notes="Sample lab test note",
                        completed_by=completed_by.id if completed_by else None,
                        completed_at=completed_at
                    )
                    db.session.add(test)
                    added_lab_tests += 1
        
        db.session.commit()
        
        return {
            "added_atc_drugs": added_atc,
            "added_lab_tests": added_lab_tests,
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
