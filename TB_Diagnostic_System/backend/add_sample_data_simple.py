"""
Add sample patient data to the database
"""
import os
from app import app
from models.models import db, Patient

# Create sample patients
sample_patients = [
    {
        'patient_id': 'P001',
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 45,
        'gender': 'Male',
        'city': 'New York',
        'symptoms': 'Persistent cough, fever, night sweats, weight loss',
        'sputum_smear_test': 'Positive',
        'genexpert_test': 'Positive',
        'chest_xray': 'Abnormal',
        'drug_resistance': 'No',
        'hiv': 'No',
        'diabetes': 'No'
    },
    {
        'patient_id': 'P002',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'age': 32,
        'gender': 'Female',
        'city': 'Los Angeles',
        'symptoms': 'Cough, fatigue, mild fever',
        'sputum_smear_test': 'Negative',
        'genexpert_test': 'Positive',
        'chest_xray': 'Abnormal',
        'drug_resistance': 'No',
        'hiv': 'No',
        'diabetes': 'Yes'
    },
    {
        'patient_id': 'P003',
        'first_name': 'Robert',
        'last_name': 'Johnson',
        'age': 58,
        'gender': 'Male',
        'city': 'Chicago',
        'symptoms': 'Cough with blood, high fever, severe weight loss, night sweats',
        'sputum_smear_test': 'Positive',
        'genexpert_test': 'Positive',
        'chest_xray': 'Abnormal',
        'drug_resistance': 'Yes',
        'hiv': 'Yes',
        'diabetes': 'No'
    },
    {
        'patient_id': 'P004',
        'first_name': 'Emily',
        'last_name': 'Davis',
        'age': 28,
        'gender': 'Female',
        'city': 'Houston',
        'symptoms': 'Mild cough, occasional fever',
        'sputum_smear_test': 'Negative',
        'genexpert_test': 'Negative',
        'chest_xray': 'Normal',
        'drug_resistance': 'No',
        'hiv': 'No',
        'diabetes': 'No'
    },
    {
        'patient_id': 'P005',
        'first_name': 'Michael',
        'last_name': 'Brown',
        'age': 62,
        'gender': 'Male',
        'city': 'Phoenix',
        'symptoms': 'Persistent cough, night sweats, weight loss',
        'sputum_smear_test': 'Positive',
        'genexpert_test': 'Negative',
        'chest_xray': 'Abnormal',
        'drug_resistance': 'No',
        'hiv': 'No',
        'diabetes': 'Yes'
    }
]

def add_sample_data():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Add sample patients
        added_count = 0
        for patient_data in sample_patients:
            # Check if patient already exists
            existing = Patient.query.filter_by(patient_id=patient_data['patient_id']).first()
            if not existing:
                patient = Patient(**patient_data)
                db.session.add(patient)
                added_count += 1
        
        db.session.commit()
        
        print("Added", added_count, "sample patients to the database!")
        print("Total patients now:", Patient.query.count())

if __name__ == "__main__":
    add_sample_data()
