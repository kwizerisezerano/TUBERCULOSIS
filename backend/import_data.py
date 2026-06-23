
"""
Data Import & Preprocessing System
Imports TB datasets from CSV files into the database
"""
import os
import sys
import json
import subprocess
import pandas as pd
import numpy as np


def _use_project_venv_when_available():
    current_prefix = os.path.abspath(sys.prefix)
    base_prefix = os.path.abspath(getattr(sys, "base_prefix", sys.prefix))
    running_inside_venv = current_prefix != base_prefix
    if running_inside_venv:
        return

    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        return

    current_python = os.path.normcase(os.path.abspath(sys.executable))
    target_python = os.path.normcase(os.path.abspath(venv_python))
    if current_python == target_python:
        return

    completed = subprocess.run(
        [target_python, os.path.abspath(__file__), *sys.argv[1:]],
        env=os.environ.copy(),
        check=False,
    )
    raise SystemExit(completed.returncode)


_use_project_venv_when_available()

from app import app
from models.models import db, Patient, ExternalDatasetRow

def clean_text(text):
    """Clean and normalize text data"""
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()

def normalize_gender(gender):
    """Normalize gender values"""
    if pd.isna(gender):
        return None  # Let's collect mode fill this later
    gender = str(gender).lower().strip()
    if gender in ['m', 'male', '1']:
        return "Male"
    elif gender in ['f', 'female', '0']:
        return "Female"
    return "Other"

def normalize_test_result(result):
    """Normalize test results (Positive/Negative/Unknown)"""
    if pd.isna(result):
        return "Unknown"
    result = str(result).lower().strip()
    if result in ['positive', 'yes', '1', 'true', 'detected']:
        return "Positive"
    elif result in ['negative', 'no', '0', 'false', 'not detected']:
        return "Negative"
    return "Unknown"

def normalize_yes_no(value):
    """Normalize Yes/No values"""
    if pd.isna(value):
        return "No"
    value = str(value).lower().strip()
    if value in ['yes', '1', 'true', 'positive']:
        return "Yes"
    return "No"


def normalize_optional_result(value):
    """Normalize Positive/Negative/Unknown style optional test values"""
    if pd.isna(value) or value is None:
        return "Unknown"
    value = str(value).strip()
    if value == "":
        return "Unknown"
    lowered = value.lower()
    if lowered in ['positive', 'yes', '1', 'true', 'detected']:
        return "Positive"
    if lowered in ['negative', 'no', '0', 'false', 'not detected']:
        return "Negative"
    return value


def preprocess_and_fill_missing(df, patient_dict_list):
    """Preprocess dataframe and fill missing values using mode for categorical, median for numerical"""
    from collections import Counter
    import numpy as np

    # Initialize field collectors
    numerical_fields = ['age', 'weight', 'persistent_cough_duration_weeks', 'oxygen_saturation_spo2']
    categorical_fields = ['gender', 'hiv', 'diabetes', 'smoking_status', 'alcohol_use', 
                          'contact_with_tb_patient', 'previous_tb_treatment', 
                          'sputum_smear_test', 'genexpert_test', 'chest_xray', 
                          'tb_culture', 'tst', 'igra', 'drug_resistance']

    # Collect all values
    values = {}
    for field in numerical_fields + categorical_fields:
        values[field] = []

    for p in patient_dict_list:
        for field in numerical_fields:
            val = p.get(field)
            if val is not None and (isinstance(val, (int, float)) and not np.isnan(val)):
                values[field].append(val)
        for field in categorical_fields:
            val = p.get(field)
            if val is not None and val not in ['', 'Unknown']:
                values[field].append(val)

    # Calculate stats
    fill_values = {}

    # Numerical fields: use median
    for field in numerical_fields:
        if len(values[field]) > 0:
            fill_values[field] = np.median(values[field])
        else:
            # Default fallbacks
            if field == 'age':
                fill_values[field] = 35
            elif field == 'weight':
                fill_values[field] = 70
            elif field == 'persistent_cough_duration_weeks':
                fill_values[field] = 0
            elif field == 'oxygen_saturation_spo2':
                fill_values[field] = 98

    # Categorical fields: use mode
    for field in categorical_fields:
        if len(values[field]) > 0:
            fill_values[field] = Counter(values[field]).most_common(1)[0][0]
        else:
            # Default fallbacks
            if field == 'gender':
                fill_values[field] = 'Male'
            elif field in ['hiv', 'diabetes', 'contact_with_tb_patient', 'previous_tb_treatment']:
                fill_values[field] = 'No'
            elif field == 'smoking_status':
                fill_values[field] = 'Never'
            elif field == 'alcohol_use':
                fill_values[field] = 'Never'
            else:
                fill_values[field] = 'Unknown'

    # Apply fill values
    for p in patient_dict_list:
        for field in numerical_fields:
            val = p.get(field)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                p[field] = fill_values[field]
        for field in categorical_fields:
            val = p.get(field)
            if val is None or val == '' or val == 'Unknown':
                p[field] = fill_values[field]

    return patient_dict_list

def upsert_external_dataset_row(dataset_name, source_key, record):
    existing = ExternalDatasetRow.query.filter_by(dataset_name=dataset_name, source_key=source_key).first()
    if existing:
        return False
    row = ExternalDatasetRow(
        dataset_name=dataset_name,
        source_key=source_key,
        record_json=json.dumps(record, ensure_ascii=False)
    )
    db.session.add(row)
    return True

def import_tb_symptdata_april2024(file_path):
    print(f"Importing TB_SymptdataApril2024 from: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} rows")

        symptom_columns = [c for c in df.columns if c.strip().lower() not in {"prediction"}]
        patient_dicts = []

        for idx, row in df.iterrows():
            patient_id = f"SYM2024_{idx+1:06d}"
            existing = Patient.query.filter_by(patient_id=patient_id).first()
            if existing:
                continue

            symptoms_list = []
            for col in symptom_columns:
                try:
                    val = int(row.get(col, 0))
                except Exception:
                    val = 0
                if val == 1:
                    symptoms_list.append(str(col).strip())

            symptoms = ", ".join(symptoms_list) if symptoms_list else "No symptoms reported"

            pred = row.get("Prediction", None)
            try:
                tb_label = "Yes" if int(pred) == 1 else "No"
            except Exception:
                tb_label = None

            patient_dicts.append({
                "patient_id": patient_id,
                "first_name": f"Patient{idx+1}",
                "last_name": "",
                "age": 35,
                "gender": None,
                "city": "",
                "symptoms": symptoms,
                "sputum_smear_test": "Unknown",
                "genexpert_test": "Unknown",
                "chest_xray": "Unknown",
                "drug_resistance": "Unknown",
                "hiv": "No",
                "diabetes": "No",
                "tb_status_label": tb_label,
                "source_dataset": "TB_SymptdataApril2024",
                "source_row_id": str(idx + 1)
            })

        # Preprocess and fill missing values
        patient_dicts = preprocess_and_fill_missing(df, patient_dicts)

        imported_count = 0
        for p_dict in patient_dicts:
            patient = Patient(**p_dict)
            db.session.add(patient)
            imported_count += 1

        db.session.commit()
        print(f"  Successfully imported {imported_count} patients")
        return imported_count

    except Exception as e:
        print(f"  Error importing TB_SymptdataApril2024: {e}")
        db.session.rollback()
        return 0

def import_symptoms_dataset(file_path):
    """Import the Tb disease symptoms.csv dataset"""
    print(f"Importing Symptoms Dataset from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} patient records")

        patient_dicts = []

        for idx, row in df.iterrows():
            patient_id = str(row.get('id', f'SYM{idx+1:04d}'))

            # Check if already exists
            existing = Patient.query.filter_by(patient_id=patient_id).first()
            if existing:
                continue

            # Extract symptoms
            symptoms_list = []
            if int(row.get('fever for two weeks', 0)) == 1:
                symptoms_list.append("Fever for two weeks")
            if int(row.get('coughing blood', 0)) == 1:
                symptoms_list.append("Coughing blood")
            if int(row.get('sputum mixed with blood', 0)) == 1:
                symptoms_list.append("Sputum mixed with blood")
            if int(row.get('night sweats ', 0)) == 1:
                symptoms_list.append("Night sweats")
            if int(row.get('chest pain', 0)) == 1:
                symptoms_list.append("Chest pain")
            if int(row.get('back pain in certain parts ', 0)) == 1:
                symptoms_list.append("Back pain in certain parts")
            if int(row.get('shortness of breath', 0)) == 1:
                symptoms_list.append("Shortness of breath")
            if int(row.get('weight loss ', 0)) == 1:
                symptoms_list.append("Weight loss")
            if int(row.get('body feels tired', 0)) == 1:
                symptoms_list.append("Body feels tired")
            if int(row.get('lumps that appear around the armpits and neck', 0)) == 1:
                symptoms_list.append("Lumps that appear around the armpits and neck")
            if int(row.get('cough and phlegm continuously for two weeks to four weeks', 0)) == 1:
                symptoms_list.append("Cough and phlegm continuously for two weeks to four weeks")
            if int(row.get('swollen lymph nodes', 0)) == 1:
                symptoms_list.append("Swollen lymph nodes")
            if int(row.get('loss of appetite', 0)) == 1:
                symptoms_list.append("Loss of appetite")

            symptoms = ", ".join(symptoms_list) if symptoms_list else "No symptoms reported"

            # Determine test results based on symptoms (since dataset doesn't have direct tests)
            score = len(symptoms_list)
            sputum = "Positive" if score >= 4 else ("Negative" if score >= 2 else "Unknown")
            genexpert = "Positive" if score >= 3 else ("Negative" if score >= 2 else "Unknown")
            chest_xray = "Abnormal" if score >= 3 else ("Normal" if score < 2 else "Unknown")
            drug_resistant = "Yes" if score >= 6 else "No"

            patient_dicts.append({
                "patient_id": patient_id,
                "first_name": clean_text(row.get('name', f'Patient{idx+1}')),
                "last_name": '',
                "age": int(row.get('age', 35)) if pd.notna(row.get('age')) else None,
                "gender": normalize_gender(row.get('gender')),
                "city": '',
                "symptoms": symptoms,
                "sputum_smear_test": sputum,
                "genexpert_test": genexpert,
                "chest_xray": chest_xray,
                "drug_resistance": drug_resistant,
                "hiv": 'No',
                "diabetes": 'No'
            })

        # Preprocess and fill missing values
        patient_dicts = preprocess_and_fill_missing(df, patient_dicts)

        imported_count = 0
        for p_dict in patient_dicts:
            patient = Patient(**p_dict)
            db.session.add(patient)
            imported_count += 1

        db.session.commit()
        print(f"  Successfully imported {imported_count} patients")
        return imported_count

    except Exception as e:
        print(f"  Error importing symptoms dataset: {e}")
        db.session.rollback()
        return 0

def import_bangladesh_dataset(file_path):
    """Import the synthetic_tb_data_bangladesh.csv dataset"""
    print(f"Importing Bangladesh Dataset from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} patient records")

        patient_dicts = []

        for idx, row in df.iterrows():
            patient_id = f"BD{int(row.get('Patient ID', idx+1)):04d}"

            # Check if already exists
            existing = Patient.query.filter_by(patient_id=patient_id).first()
            if existing:
                continue

            patient_dicts.append({
                "patient_id": patient_id,
                "first_name": f'Patient{int(row.get("Patient ID", idx+1))}',
                "last_name": '',
                "age": int(row.get('Age', 35)) if pd.notna(row.get('Age')) else None,
                "gender": normalize_gender(row.get('Gender')),
                "city": clean_text(row.get('City', '')),
                "symptoms": clean_text(row.get('Symptoms', '')),
                "sputum_smear_test": normalize_test_result(row.get('Sputum Smear Test')),
                "genexpert_test": normalize_test_result(row.get('GeneXpert Test')),
                "chest_xray": normalize_test_result(row.get('Chest X-ray Results')),
                "drug_resistance": normalize_yes_no(row.get('Drug Resistance')),
                "hiv": normalize_yes_no(row.get('HIV')),
                "diabetes": normalize_yes_no(row.get('Diabetes'))
            })

        # Preprocess and fill missing values
        patient_dicts = preprocess_and_fill_missing(df, patient_dicts)

        imported_count = 0
        for p_dict in patient_dicts:
            patient = Patient(**p_dict)
            db.session.add(patient)
            imported_count += 1

        db.session.commit()
        print(f"  Successfully imported {imported_count} patients")
        return imported_count

    except Exception as e:
        print(f"  Error importing Bangladesh dataset: {e}")
        db.session.rollback()
        return 0

def import_xray_dataset(file_path):
    """Import the tuberculosis_xray_dataset.csv dataset"""
    print(f"Importing X-ray Dataset from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} patient records")

        patient_dicts = []

        for idx, row in df.iterrows():
            patient_id = clean_text(row.get('Patient_ID', f'XRAY{idx+1:04d}'))

            # Check if already exists
            existing = Patient.query.filter_by(patient_id=patient_id).first()
            if existing:
                continue

            # Build symptoms list
            symptoms_list = []
            if normalize_yes_no(row.get('Chest_Pain')) == 'Yes':
                symptoms_list.append('Chest pain')
            if int(row.get('Cough_Severity', 0)) > 0:
                symptoms_list.append(f'Cough (severity: {row.get("Cough_Severity")})')
            if int(row.get('Breathlessness', 0)) > 0:
                symptoms_list.append('Breathlessness')
            if int(row.get('Fatigue', 0)) > 0:
                symptoms_list.append('Fatigue')
            if float(row.get('Weight_Loss', 0.0)) > 0.0:
                symptoms_list.append('Weight loss')
            if str(row.get('Fever', '')).strip() != '':
                symptoms_list.append(f'Fever ({row.get("Fever")})')
            if normalize_yes_no(row.get('Night_Sweats')) == 'Yes':
                symptoms_list.append('Night sweats')
            if str(row.get('Sputum_Production', '')).strip() != '':
                symptoms_list.append(f'Sputum production ({row.get("Sputum_Production")})')
            if normalize_yes_no(row.get('Blood_in_Sputum')) == 'Yes':
                symptoms_list.append('Blood in sputum (hemoptysis)')

            symptoms = ", ".join(symptoms_list) if symptoms_list else 'No symptoms reported'

            class_label = str(row.get('Class', '')).strip()
            is_tb = class_label == 'Tuberculosis'
            tb_label = 'Yes' if is_tb else 'No'

            patient_dicts.append({
                "patient_id": patient_id,
                "first_name": f'Patient{idx+1}',
                "last_name": '',
                "age": int(row.get('Age', 35)) if pd.notna(row.get('Age')) else None,
                "gender": normalize_gender(row.get('Gender')),
                "city": '',
                "symptoms": symptoms,
                "sputum_smear_test": 'Positive' if is_tb else 'Negative',
                "genexpert_test": 'Positive' if is_tb else 'Negative',
                "chest_xray": 'Abnormal' if is_tb else 'Normal',
                "drug_resistance": 'No',
                "hiv": 'No',
                "diabetes": 'No',
                "tb_status_label": tb_label,
                "source_dataset": 'tuberculosis_xray_dataset',
                "source_row_id": patient_id
            })

        # Preprocess and fill missing values
        patient_dicts = preprocess_and_fill_missing(df, patient_dicts)

        imported_count = 0
        for p_dict in patient_dicts:
            patient = Patient(**p_dict)
            db.session.add(patient)
            imported_count += 1

        db.session.commit()
        print(f"  Successfully imported {imported_count} patients")
        return imported_count

    except Exception as e:
        print(f"  Error importing X-ray dataset: {e}")
        db.session.rollback()
        return 0


def import_owner_species_dataset(file_path):
    """Import curated owner dataset with species-labeled TB cases"""
    print(f"Importing owner TB species dataset from: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} curated patient records")

        patient_dicts = []
        external_count = 0

        for idx, row in df.iterrows():
            record = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            patient_id = clean_text(record.get('patient_id', f'OWN{idx+1:04d}'))
            if not patient_id:
                patient_id = f'OWN{idx+1:04d}'

            if upsert_external_dataset_row("owner_tb_species_dataset", patient_id, record):
                external_count += 1

            existing = Patient.query.filter_by(patient_id=patient_id).first()
            if existing:
                continue

            patient_dicts.append({
                "patient_id": patient_id,
                "first_name": f'Owner{idx+1}',
                "last_name": 'Dataset',
                "age": int(record.get('age', 35)) if record.get('age') is not None else None,
                "gender": normalize_gender(record.get('gender')),
                "city": clean_text(record.get('city', '')),
                "region": clean_text(record.get('region', '')),
                "symptoms": clean_text(record.get('symptoms', '')),
                "exposure_history": clean_text(record.get('exposure_history', '')),
                "sputum_smear_test": normalize_optional_result(record.get('sputum_smear_test')),
                "genexpert_test": normalize_optional_result(record.get('genexpert_test')),
                "chest_xray": normalize_optional_result(record.get('chest_xray')),
                "bacteria_species": clean_text(record.get('bacteria_species', '')) or None,
                "treatment_type": clean_text(record.get('treatment_regimen', '')),
                "drug_resistance": clean_text(record.get('drug_resistance', '')) or 'No',
                "hiv": 'Unknown',
                "diabetes": 'Unknown',
                "tb_status_label": 'Yes' if str(record.get('tb_status_label', 'Yes')).strip().lower() == 'yes' else 'No',
                "source_dataset": 'owner_tb_species_dataset',
                "source_row_id": patient_id
            })

        # Preprocess and fill missing values
        patient_dicts = preprocess_and_fill_missing(df, patient_dicts)

        imported_count = 0
        for p_dict in patient_dicts:
            patient = Patient(**p_dict)
            db.session.add(patient)
            imported_count += 1

        db.session.commit()
        print(f"  Stored {external_count} owner dataset records in external dataset table")
        print(f"  Successfully imported {imported_count} curated patients")
        return imported_count

    except Exception as e:
        print(f"  Error importing owner TB species dataset: {e}")
        db.session.rollback()
        return 0

def create_comprehensive_sample_patients():
    """Create sample patients covering various TB scenarios"""
    print("Creating comprehensive sample patients...")
    
    sample_patients = [
        {
            'patient_id': 'PT001',
            'first_name': 'Kwizera',
            'last_name': 'Jean',
            'age': 34,
            'gender': 'Male',
            'city': 'Kigali',
            'symptoms': 'Persistent cough for 3 weeks, fever, night sweats, weight loss, chest pain',
            'sputum_smear_test': 'Positive',
            'genexpert_test': 'Positive',
            'chest_xray': 'Abnormal',
            'drug_resistance': 'No',
            'hiv': 'No',
            'diabetes': 'No'
        },
        {
            'patient_id': 'PT002',
            'first_name': 'Marie',
            'last_name': 'Uwimana',
            'age': 28,
            'gender': 'Female',
            'city': 'Butare',
            'symptoms': 'Back pain, lower limb weakness, fever, fatigue, weight loss',
            'sputum_smear_test': 'Negative',
            'genexpert_test': 'Positive',
            'chest_xray': 'Normal',
            'drug_resistance': 'No',
            'hiv': 'No',
            'diabetes': 'No'
        },
        {
            'patient_id': 'PT003',
            'first_name': 'Pierre',
            'last_name': 'Nkurunziza',
            'age': 45,
            'gender': 'Male',
            'city': 'Gisenyi',
            'symptoms': 'Cough with blood, high fever, severe weight loss, night sweats',
            'sputum_smear_test': 'Positive',
            'genexpert_test': 'Positive',
            'chest_xray': 'Abnormal',
            'drug_resistance': 'Yes',
            'hiv': 'No',
            'diabetes': 'Yes'
        },
        {
            'patient_id': 'PT004',
            'first_name': 'Aisha',
            'last_name': 'Mukeshimana',
            'age': 31,
            'gender': 'Female',
            'city': 'Huye',
            'symptoms': 'Chronic cough, fever, fatigue, weight loss, diarrhea',
            'sputum_smear_test': 'Positive',
            'genexpert_test': 'Positive',
            'chest_xray': 'Abnormal',
            'drug_resistance': 'No',
            'hiv': 'Yes',
            'diabetes': 'No'
        }
    ]
    
    added_count = 0
    for patient_data in sample_patients:
        existing = Patient.query.filter_by(patient_id=patient_data['patient_id']).first()
        if not existing:
            patient = Patient(**patient_data)
            db.session.add(patient)
            added_count += 1
    
    db.session.commit()
    print(f"  Added {added_count} comprehensive sample patients")
    return added_count

def main():
    """Main import function"""
    with app.app_context():
        print("=== TB Diagnostic System - Data Import ===")
        print()
        
        # Create tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
        print()
        
        total_imported = 0

        data_raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")

        sympt_2024_path = os.path.join(data_raw_dir, "TB_SymptdataApril2024.csv")
        xray_path = os.path.join(data_raw_dir, "tuberculosis_xray_dataset.csv")
        owner_species_path = os.path.join(data_raw_dir, "owner_tb_species_dataset.csv")
        incidence_path = os.path.join(data_raw_dir, "incidenceoftuberculosis_new.csv")
        treatment_path = os.path.join(data_raw_dir, "treatment.csv")

        if os.path.exists(sympt_2024_path):
            total_imported += import_tb_symptdata_april2024(sympt_2024_path)
            print()
        else:
            print(f"TB_SymptdataApril2024 not found at: {sympt_2024_path}")
            print()

        if os.path.exists(xray_path):
            total_imported += import_xray_dataset(xray_path)
            print()
        else:
            print(f"X-ray dataset not found at: {xray_path}")
            print()

        if os.path.exists(owner_species_path):
            total_imported += import_owner_species_dataset(owner_species_path)
            print()
        else:
            print(f"Owner TB species dataset not found at: {owner_species_path}")
            print()

        if os.path.exists(incidence_path):
            print(f"Importing incidence dataset rows from: {incidence_path}")
            try:
                df_inc = pd.read_csv(incidence_path)
                added = 0
                for _, r in df_inc.iterrows():
                    record = {k: (None if pd.isna(v) else v) for k, v in r.to_dict().items()}
                    source_key = f"{record.get('Entity','')}-{record.get('Code','')}-{record.get('Year','')}"
                    if upsert_external_dataset_row("incidenceoftuberculosis", source_key, record):
                        added += 1
                db.session.commit()
                print(f"  Stored {added} incidence rows in database")
                print()
            except Exception as e:
                print(f"  Error importing incidence dataset: {e}")
                db.session.rollback()
                print()

        if os.path.exists(treatment_path):
            print(f"Importing treatment dataset rows from: {treatment_path}")
            try:
                df_treat = pd.read_csv(treatment_path, sep=";", engine="python")
                df_treat = df_treat.dropna(axis=1, how="all")
                added = 0
                for i, r in df_treat.iterrows():
                    record = {k: (None if pd.isna(v) else v) for k, v in r.to_dict().items()}
                    country = record.get("country", "")
                    year = record.get("year", "")
                    source_key = f"{country}-{year}-{i}"
                    if upsert_external_dataset_row("treatment", source_key, record):
                        added += 1
                db.session.commit()
                print(f"  Stored {added} treatment rows in database")
                print()
            except Exception as e:
                print(f"  Error importing treatment dataset: {e}")
                db.session.rollback()
                print()
        
        # Create sample patients only when the database is still empty.
        if Patient.query.count() == 0:
            create_comprehensive_sample_patients()
        
        total_patients = Patient.query.count()
        print(f"\n=== Import Complete ===")
        print(f"Total patients in database: {total_patients}")
        print("The system is ready to use!")

if __name__ == "__main__":
    main()
