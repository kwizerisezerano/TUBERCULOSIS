
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
        # Seed ATC drugs
        added_atc = 0
        for drug_data in sample_atc_drugs:
            existing = ATCDrug.query.filter_by(atc_code=drug_data['atc_code']).first()
            if existing:
                continue
            drug = ATCDrug(**drug_data)
            db.session.add(drug)
            added_atc += 1
        
        # Get some users for associations
        doctor = User.query.filter_by(role="doctor").first()
        lab_tech = User.query.filter_by(role="lab_technician").first()
        pharmacist = User.query.filter_by(role="pharmacist").first()
        admin = User.query.filter_by(role="system_admin").first()
        
        # Get some patients
        patients = Patient.query.all()
        sample_patients = patients[:5] if len(patients) >=5 else patients
        
        # Seed sample lab tests
        added_lab_tests = 0
        test_types = ['GeneXpert', 'Sputum Smear', 'Chest X-ray', 'Blood Test', 'TB Culture', 'DST (Drug Susceptibility Test)']
        test_statuses = ['requested', 'in_progress', 'completed', 'completed', 'completed']
        results = ['Positive', 'Negative', 'Normal', 'Abnormal', 'Positive for MTB']
        
        for i, patient in enumerate(sample_patients):
            existing_test = LabTest.query.filter_by(patient_id=patient.id, test_type=test_types[i%len(test_types)]).first()
            if existing_test:
                continue
            lt = LabTest(
                patient_id=patient.id,
                requested_by=doctor.id,
                test_type=test_types[i%len(test_types)],
                status=test_statuses[i%len(test_statuses)],
                results=results[i%len(results)] if test_statuses[i%len(test_statuses)] == 'completed' else None,
                notes=f"Sample lab test for {patient.first_name}",
                completed_by=lab_tech.id if test_statuses[i%len(test_statuses)] == 'completed' else None,
                completed_at=datetime.now() - timedelta(days=i) if test_statuses[i%len(test_statuses)] == 'completed' else None
            )
            db.session.add(lt)
            added_lab_tests += 1
            
            # Create audit log
            audit = AuditLog(
                user_id=doctor.id,
                action='create_lab_test',
                entity_type='lab_test',
                entity_id=lt.id,
                details=f"Created lab test {lt.test_type} for patient {patient.patient_id}"
            )
            db.session.add(audit)
        
        # Seed sample prescriptions
        added_prescriptions = 0
        meds = ['Amoxicillin', 'Ciprofloxacin', 'Isoniazid and rifampicin', 'Ceftriaxone']
        atc_drugs = ATCDrug.query.all()
        
        for i, patient in enumerate(sample_patients):
            atc_drug = atc_drugs[i%len(atc_drugs)] if atc_drugs else None
            existing_presc = Prescription.query.filter_by(patient_id=patient.id, medication=meds[i%len(meds)]).first()
            if existing_presc:
                continue
            presc = Prescription(
                patient_id=patient.id,
                created_by=doctor.id,
                medication=meds[i%len(meds)],
                atc_drug_id=atc_drug.id if atc_drug else None,
                dosage="500mg",
                dosage_mg=500.0,
                duration_days=14,
                total_mg=500.0 * 14,
                ddds=(500.0 * 14 / 1000) / (atc_drug.ddd if atc_drug else 1.0) if atc_drug else None,
                duration="2 weeks",
                risk_level="Moderate",
                ml_recommended=True,
                status="pending" if i%2 ==0 else "approved",
                approved_by=pharmacist.id if i%2 !=0 else None,
                approved_at=datetime.now() - timedelta(days=i) if i%2 !=0 else None
            )
            db.session.add(presc)
            added_prescriptions += 1
            
            # Audit log for prescription
            audit_presc = AuditLog(
                user_id=doctor.id,
                action='create_prescription',
                entity_type='prescription',
                entity_id=presc.id,
                details=f"Created prescription for {presc.medication} to patient {patient.patient_id}"
            )
            db.session.add(audit_presc)
            
            if i%2 !=0:
                audit_approve = AuditLog(
                    user_id=pharmacist.id,
                    action='approve_prescription',
                    entity_type='prescription',
                    entity_id=presc.id,
                    details=f"Approved prescription {presc.id}"
                )
                db.session.add(audit_approve)
        
        # Seed sample diagnoses and treatments
        added_diagnoses = 0
        added_treatments = 0
        for i, patient in enumerate(sample_patients):
            existing_diag = Diagnosis.query.filter_by(patient_id=patient.id).first()
            if existing_diag:
                continue
            diag = Diagnosis(
                patient_id=patient.id,
                clinician_id=doctor.id,
                diagnosis_type="Pulmonary TB" if patient.tb_status_label == "Yes" else "Respiratory Infection",
                risk_level="High" if patient.tb_status_label == "Yes" else "Low",
                confidence_percent=85.0 + (i*2),
                details="Sample diagnosis based on symptoms and test results",
                ml_prediction="TB Positive" if patient.tb_status_label == "Yes" else "TB Negative",
                status="confirmed"
            )
            db.session.add(diag)
            added_diagnoses += 1
            
            # Add treatment
            treatment = Treatment(
                patient_id=patient.id,
                diagnosis_id=diag.id,
                treatment_type="Standard First-line TB Treatment" if patient.tb_status_label == "Yes" else "Supportive Care",
                drugs="Isoniazid, Rifampicin, Pyrazinamide, Ethambutol" if patient.tb_status_label == "Yes" else "Rest, fluids",
                duration="6 months" if patient.tb_status_label == "Yes" else "1 week",
                dosage="Standard doses",
                administration_notes="Directly observed therapy (DOT) recommended",
                start_date=datetime.now() - timedelta(days=30*i),
                status="active"
            )
            db.session.add(treatment)
            added_treatments +=1
        
        # Seed sample alerts
        added_alerts =0
        alert_types = ['antimicrobial_stewardship', 'treatment_adherence', 'lab_result_ready', 'high_risk_patient']
        messages = [
            "Possible antibiotic overuse detected. Review patient prescription history.",
            "Patient at risk of treatment non-adherence. Schedule follow-up.",
            "Lab test results ready for review.",
            "High TB risk patient identified. Immediate evaluation recommended."
        ]
        severities = ['warning', 'medium', 'info', 'high']
        
        for i, patient in enumerate(sample_patients):
            existing_alert = Alert.query.filter_by(patient_id=patient.id, alert_type=alert_types[i%len(alert_types)]).first()
            if existing_alert:
                continue
            alert = Alert(
                patient_id=patient.id,
                user_id=doctor.id,
                alert_type=alert_types[i%len(alert_types)],
                message=messages[i%len(messages)],
                severity=severities[i%len(severities)],
                is_read=False
            )
            db.session.add(alert)
            added_alerts += 1
        
        db.session.commit()
        
        return {
            "added_atc_drugs": added_atc,
            "added_lab_tests": added_lab_tests,
            "added_prescriptions": added_prescriptions,
            "added_diagnoses": added_diagnoses,
            "added_treatments": added_treatments,
            "added_alerts": added_alerts
        }

def seed_all():
    users_result = seed_users()
    sample_result = seed_sample_data()
    return {"users": users_result, "sample_data": sample_result}
        
if __name__ == "__main__":
    result = seed_all()
    print(result)
