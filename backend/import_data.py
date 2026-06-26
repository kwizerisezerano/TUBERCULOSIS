
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
from models.models import db, Patient, ExternalDatasetRow, ATCDrug, DetailedLabResult, AntibioticResistance

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

def extract_symptom_fields(symptoms_text):
    """Extract boolean symptom fields from symptoms text"""
    symptoms_lower = str(symptoms_text).lower()
    return {
        'has_fever': 'yes' if 'fever' in symptoms_lower else 'no',
        'has_cough': 'yes' if 'cough' in symptoms_lower else 'no',
        'has_blood': 'yes' if 'blood' in symptoms_lower or 'hemoptysis' in symptoms_lower else 'no',
        'has_chest_pain': 'yes' if 'chest pain' in symptoms_lower else 'no',
        'has_night_sweats': 'yes' if 'night sweats' in symptoms_lower else 'no',
        'has_weight_loss': 'yes' if 'weight loss' in symptoms_lower else 'no',
        'has_fatigue': 'yes' if 'fatigue' in symptoms_lower or 'tired' in symptoms_lower else 'no',
        'has_shortness_of_breath': 'yes' if 'shortness of breath' in symptoms_lower or 'breathlessness' in symptoms_lower else 'no'
    }


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
            elif field in ['sputum_smear_test', 'genexpert_test', 'tb_culture', 'tst', 'igra']:
                fill_values[field] = 'Negative'  # Default test results
            elif field == 'chest_xray':
                fill_values[field] = 'Normal'
            elif field == 'drug_resistance':
                fill_values[field] = 'No'

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
                "tb_culture": "Unknown",
                "tst": "Unknown",
                "igra": "Unknown",
                "drug_resistance": "Unknown",
                "hiv": "No",
                "diabetes": "No",
                "weight": None,
                "persistent_cough_duration_weeks": 0,
                "contact_with_tb_patient": "No",
                "previous_tb_treatment": "No",
                "smoking_status": "Never",
                "alcohol_use": "Never",
                "oxygen_saturation_spo2": 98,
                "tb_status_label": tb_label,
                "source_dataset": "TB_SymptdataApril2024",
                "source_row_id": str(idx + 1)
            })

        # Preprocess and fill missing values
        for idx in range(len(patient_dicts)):
            sym_fields = extract_symptom_fields(patient_dicts[idx]['symptoms'])
            patient_dicts[idx] = {**patient_dicts[idx], **sym_fields}
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
                "tb_culture": "Unknown",
                "tst": "Unknown",
                "igra": "Unknown",
                "drug_resistance": drug_resistant,
                "hiv": 'No',
                "diabetes": 'No',
                "weight": None,
                "persistent_cough_duration_weeks": 0,
                "contact_with_tb_patient": "No",
                "previous_tb_treatment": "No",
                "smoking_status": "Never",
                "alcohol_use": "Never",
                "oxygen_saturation_spo2": 98
            })

        # Preprocess and fill missing values
        for idx in range(len(patient_dicts)):
            sym_fields = extract_symptom_fields(patient_dicts[idx]['symptoms'])
            patient_dicts[idx] = {**patient_dicts[idx], **sym_fields}
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
        for idx in range(len(patient_dicts)):
            sym_fields = extract_symptom_fields(patient_dicts[idx]['symptoms'])
            patient_dicts[idx] = {**patient_dicts[idx], **sym_fields}
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
                "tb_culture": 'Unknown',
                "tst": 'Unknown',
                "igra": 'Unknown',
                "drug_resistance": 'No',
                "hiv": 'No',
                "diabetes": 'No',
                "weight": None,
                "persistent_cough_duration_weeks": int(row.get('Cough_Severity', 0)) * 2 if int(row.get('Cough_Severity', 0)) > 0 else 0,
                "contact_with_tb_patient": 'No',
                "previous_tb_treatment": 'No',
                "smoking_status": 'Never',
                "alcohol_use": 'Never',
                "oxygen_saturation_spo2": 98,
                "tb_status_label": tb_label,
                "source_dataset": 'tuberculosis_xray_dataset',
                "source_row_id": patient_id
            })

        # Preprocess and fill missing values
        for idx in range(len(patient_dicts)):
            sym_fields = extract_symptom_fields(patient_dicts[idx]['symptoms'])
            patient_dicts[idx] = {**patient_dicts[idx], **sym_fields}
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
                "tb_culture": normalize_optional_result(record.get('tb_culture')),
                "tst": normalize_optional_result(record.get('tst')),
                "igra": normalize_optional_result(record.get('igra')),
                "bacteria_species": clean_text(record.get('bacteria_species', '')) or None,
                "treatment_type": clean_text(record.get('treatment_regimen', '')),
                "drug_resistance": clean_text(record.get('drug_resistance', '')) or 'No',
                "hiv": normalize_optional_result(record.get('hiv')),
                "diabetes": normalize_optional_result(record.get('diabetes')),
                "weight": record.get('weight', None),
                "persistent_cough_duration_weeks": record.get('persistent_cough_duration_weeks', None),
                "contact_with_tb_patient": normalize_optional_result(record.get('contact_with_tb_patient')),
                "previous_tb_treatment": normalize_optional_result(record.get('previous_tb_treatment')),
                "smoking_status": record.get('smoking_status', 'Unknown'),
                "alcohol_use": record.get('alcohol_use', 'Unknown'),
                "oxygen_saturation_spo2": record.get('oxygen_saturation_spo2', None),
                "tb_status_label": 'Yes' if str(record.get('tb_status_label', 'Yes')).strip().lower() == 'yes' else 'No',
                "source_dataset": 'owner_tb_species_dataset',
                "source_row_id": patient_id
            })

        # Preprocess and fill missing values
        for idx in range(len(patient_dicts)):
            sym_fields = extract_symptom_fields(patient_dicts[idx]['symptoms'])
            patient_dicts[idx] = {**patient_dicts[idx], **sym_fields}
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

def preprocess_atc_ddd_data(df):
    """Preprocess ATC-DDD DataFrame, clean data, handle missing values"""
    from collections import Counter

    # Clean ATC code: ensure it's uppercase and remove whitespace
    df['atc_code'] = df['atc_code'].astype(str).str.strip().str.upper()

    # Compute mode for administration route and unit to fill missing values
    route_values = []
    unit_values = []
    for val in df.get('adm_r', []):
        cleaned = clean_text(val)
        if cleaned:
            route_values.append(cleaned)
    for val in df.get('uom', []):
        cleaned = clean_text(val)
        if cleaned:
            unit_values.append(cleaned)

    route_mode = Counter(route_values).most_common(1)[0][0] if route_values else 'Oral'
    unit_mode = Counter(unit_values).most_common(1)[0][0] if unit_values else 'mg'

    return df, route_mode, unit_mode


def import_atc_ddd_dataset(file_path):
    """Import WHO ATC-DDD dataset into ATCDrug model"""
    print(f"Importing WHO ATC-DDD dataset from: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} ATC-DDD records")
        # Preprocess the data
        print("  Preprocessing ATC-DDD data...")
        df, route_mode, unit_mode = preprocess_atc_ddd_data(df)

        imported_count = 0

        for idx, row in df.iterrows():
            atc_code = row['atc_code']
            if not atc_code or atc_code == 'NAN':
                continue

            existing = ATCDrug.query.filter_by(atc_code=atc_code).first()
            if existing:
                continue

            atc_level_1 = atc_code[0] if len(atc_code) >=1 else None
            atc_level_2 = atc_code[:2] if len(atc_code)>=2 else None
            atc_level_3 = atc_code[:3] if len(atc_code)>=3 else None
            atc_level_4 = atc_code[:4] if len(atc_code)>=4 else None
            atc_level_5 = atc_code if len(atc_code)>=5 else None

            ddd_val = row.get('ddd')
            if pd.isna(ddd_val) or str(ddd_val).strip().upper() in ['NA', 'NAN', '']:
                ddd_val = None
            try:
                ddd_val = float(ddd_val) if ddd_val is not None else None
            except (ValueError, TypeError):
                ddd_val = None

            # Get cleaned values, use modes if missing
            drug_name = clean_text(row.get('atc_name', ''))
            ddd_unit = clean_text(row.get('uom', '')) or unit_mode
            administration_route = clean_text(row.get('adm_r', '')) or route_mode

            atc_drug = ATCDrug(
                atc_code=atc_code,
                atc_level_1=atc_level_1,
                atc_level_2=atc_level_2,
                atc_level_3=atc_level_3,
                atc_level_4=atc_level_4,
                atc_level_5=atc_level_5,
                drug_name=drug_name,
                ddd=ddd_val,
                ddd_unit=ddd_unit,
                administration_route=administration_route
            )

            with db.session.no_autoflush:
                db.session.add(atc_drug)
            imported_count +=1

        db.session.commit()
        print(f"  Successfully imported {imported_count} ATC drugs")
        return imported_count
    except Exception as e:
        print(f"  Error importing ATC-DDD dataset: {e}")
        db.session.rollback()
        return 0

def import_synthetic_dataset(file_path: str = None):
    """Import or generate synthetic TB patient data"""
    if file_path and os.path.exists(file_path):
        print(f"Importing synthetic TB dataset from {file_path}...")
        import pandas as pd
        df = pd.read_csv(file_path)
        patient_dicts = df.to_dict('records')
    else:
        print("Generating synthetic TB dataset (5000 patients)...")
        from generate_synthetic_tb_data import generate_dataset
        patient_dicts = generate_dataset(5000)
    
    # Preprocess and fill any missing values (as a safety net)
    print("  Preprocessing and validating synthetic data...")
    patient_dicts = preprocess_and_fill_missing(None, patient_dicts)
    
    imported_count = 0
    for p_dict in patient_dicts:
        existing = Patient.query.filter_by(patient_id=p_dict['patient_id']).first()
        if not existing:
            patient = Patient(**p_dict)
            db.session.add(patient)
            imported_count += 1
    db.session.commit()
    print(f"Successfully imported {imported_count} synthetic patients!")
    return imported_count


def normalize_ab_result(val):
    """Normalize antibiotic resistance result (R/S/I/Unknown)"""
    if pd.isna(val) or val is None:
        return 'Unknown'
    s = str(val).strip().upper()
    if s in ['R', 'RESISTANT']:
        return 'R'
    elif s in ['S', 'SUSCEPTIBLE']:
        return 'S'
    elif s in ['I', 'INTERMEDIATE']:
        return 'I'
    return 'Unknown'


def normalize_yes_no_unknown(val):
    """Normalize yes/no/unknown values"""
    if pd.isna(val) or val is None:
        return 'Unknown'
    s = str(val).strip().upper()
    if s in ['YES', 'Y', '1']:
        return 'Yes'
    elif s in ['NO', 'N', '0']:
        return 'No'
    return 'Unknown'


def import_multi_hospital_lab_results(file_path):
    """Import multi-hospital lab results dataset into DetailedLabResult model"""
    print(f"Importing multi-hospital lab results from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} lab results")
        
        from collections import Counter

        # Calculate mode for categorical fields first
        field_modes = {}
        text_fields = ['hospital', 'test_name', 'test_value', 'unit', 'reference_range', 'collection_date']
        
        for field in text_fields:
            values = []
            for val in df.get(field, []):
                cleaned = clean_text(val)
                if cleaned and cleaned not in ['', 'Unknown', 'Unknown Hospital', 'Unknown Test', 
                                               'Not Available', 'N/A', 'Not Specified', 'Unknown Date']:
                    values.append(cleaned)
            if values:
                field_modes[field] = Counter(values).most_common(1)[0][0]
            else:
                # Defaults
                if field == 'hospital':
                    field_modes[field] = 'General Hospital'
                elif field == 'test_name':
                    field_modes[field] = 'Complete Blood Count'
                elif field == 'test_value':
                    field_modes[field] = 'Normal'
                elif field == 'unit':
                    field_modes[field] = 'mg/dL'
                elif field == 'reference_range':
                    field_modes[field] = 'Standard Range'
                elif field == 'collection_date':
                    field_modes[field] = '2024-01-01'
        
        imported_count = 0
        for idx, row in df.iterrows():
            def get_field(field_name):
                val = clean_text(row.get(field_name))
                if val and val not in ['', 'Unknown', 'Unknown Hospital', 'Unknown Test', 
                                       'Not Available', 'N/A', 'Not Specified', 'Unknown Date']:
                    return val
                return field_modes[field_name]
            
            lab_result = DetailedLabResult(
                hospital=get_field('hospital'),
                test_name=get_field('test_name'),
                test_value=get_field('test_value'),
                unit=get_field('unit'),
                reference_range=get_field('reference_range'),
                collection_date=get_field('collection_date'),
                source_dataset='multi_hospital_lab_results'
            )
            db.session.add(lab_result)
            imported_count += 1
        db.session.commit()
        print(f"  Successfully imported {imported_count} detailed lab results")
        return imported_count
    except Exception as e:
        print(f"  Error importing lab results: {e}")
        db.session.rollback()
        return 0


def preprocess_antibiotic_resistance_data(df):
    """Preprocess antibiotic resistance DataFrame to handle missing values, normalize data"""
    from collections import Counter
    import pandas as pd

    def is_valid_date(date_str):
        if pd.isna(date_str) or not date_str:
            return False
        try:
            pd.to_datetime(date_str, errors='raise')
            return True
        except:
            return False

    # First, collect all non-unknown values to compute mode for categorical fields
    yes_no_fields = ['Diabetes', 'Hypertension', 'Hospital_before']
    antibiotic_fields = ['AMX/AMP', 'AMC', 'CZ', 'FOX', 'CTX/CRO', 'IPM', 'GEN', 'AN', 
                         'Acide nalidixique', 'ofx', 'CIP', 'C', 'Co-trimoxazole', 'Furanes', 'colistine']
    text_fields_to_process = ['ID', 'Name', 'Email', 'Address', 'age/gender', 'Souches', 'Notes', 'Collection_Date']

    # Compute mode for yes/no fields
    field_modes = {}
    for field in yes_no_fields:
        values = []
        for val in df.get(field, []):
            normalized = normalize_yes_no_unknown(val)
            if normalized != 'Unknown':
                values.append(normalized)
        if values:
            field_modes[field] = Counter(values).most_common(1)[0][0]
        else:
            field_modes[field] = 'No'  # Default to No for yes/no fields

    # Compute mode for antibiotic fields
    for field in antibiotic_fields:
        values = []
        for val in df.get(field, []):
            normalized = normalize_ab_result(val)
            if normalized != 'Unknown':
                values.append(normalized)
        if values:
            field_modes[field] = Counter(values).most_common(1)[0][0]
        else:
            field_modes[field] = 'S'  # Default to susceptible for AB results

    # Compute mode for all text fields (including ID, Name, etc.)
    text_field_modes = {}
    for field in ['Souches', 'Name', 'Email', 'Address', 'age/gender', 'Notes']:
        values = []
        for val in df.get(field, []):
            cleaned = clean_text(val)
            if cleaned and cleaned not in ['Unknown', '', 'missing']:
                values.append(cleaned)
        if values:
            text_field_modes[field] = Counter(values).most_common(1)[0][0]
        else:
            # Default fallbacks
            defaults = {
                'Souches': 'Unknown Species',
                'Name': 'Anonymous Patient',
                'Email': 'unknown@example.com',
                'Address': 'Unknown Address',
                'age/gender': 'Unknown',
                'Notes': 'No notes'
            }
            text_field_modes[field] = defaults.get(field, 'Unknown')

    # Compute mode for valid Collection_Date
    date_values = []
    for val in df.get('Collection_Date', []):
        cleaned = clean_text(val)
        if cleaned and cleaned not in ['Unknown', '', 'missing'] and is_valid_date(cleaned):
            date_values.append(cleaned)
    if date_values:
        date_mode = Counter(date_values).most_common(1)[0][0]
    else:
        date_mode = 'Unknown Date'

    # Now fill missing values for ALL fields
    processed_records = []
    for idx, row in df.iterrows():
        record = row.to_dict()
        
        # Fill yes/no fields with mode
        for field in yes_no_fields:
            val = record.get(field)
            normalized = normalize_yes_no_unknown(val)
            if normalized == 'Unknown':
                record[field] = field_modes[field]
            else:
                record[field] = normalized
        
        # Fill antibiotic fields with mode
        for field in antibiotic_fields:
            val = record.get(field)
            normalized = normalize_ab_result(val)
            if normalized == 'Unknown':
                record[field] = field_modes[field]
            else:
                record[field] = normalized
        
        # Fill text fields - handle "missing" value too
        def get_processed_text(field_name, fallback_default):
            val = clean_text(record.get(field_name))
            if val and val not in ['Unknown', '', 'missing']:
                return val
            return text_field_modes.get(field_name, fallback_default)
        
        def normalize_bacterial_species(species_str):
            normalized = clean_text(species_str)
            typos = {
                'E.cli': 'E. coli',
                'Ecoli': 'E. coli',
                'E Coli': 'E. coli',
                'Escherichia Coli': 'Escherichia coli',
                'Escherichia coli ': 'Escherichia coli'
            }
            return typos.get(normalized, normalized)
        
        record['Name'] = get_processed_text('Name', 'Anonymous Patient')
        record['Email'] = get_processed_text('Email', 'unknown@example.com')
        record['Address'] = get_processed_text('Address', 'Unknown Address')
        record['age/gender'] = get_processed_text('age/gender', 'Unknown')
        record['Souches'] = normalize_bacterial_species(get_processed_text('Souches', 'Unknown Species'))
        record['Notes'] = get_processed_text('Notes', 'No notes')
        
        # Handle ID (sample_id): if missing, generate one (S + idx + 1)
        id_val = clean_text(record.get('ID'))
        if id_val and id_val not in ['Unknown', '', 'missing']:
            record['ID'] = id_val
        else:
            record['ID'] = f'S{idx + 1}'
        
        # Handle Collection_Date - validate and use mode if invalid/missing
        cd_val = clean_text(record.get('Collection_Date'))
        if cd_val and cd_val not in ['Unknown', '', 'missing'] and is_valid_date(cd_val):
            record['Collection_Date'] = cd_val
        else:
            record['Collection_Date'] = date_mode
        
        processed_records.append(record)
    
    return processed_records


def import_antibiotic_resistance(file_path):
    """Import antibiotic resistance dataset into AntibioticResistance model"""
    print(f"Importing antibiotic resistance data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        print(f"  Found {len(df)} resistance records")
        # Preprocess data
        print("  Preprocessing data (handling missing values)...")
        processed_records = preprocess_antibiotic_resistance_data(df)
        imported_count = 0
        for idx, record in enumerate(processed_records):
            # Handle infection frequency: convert to float, default to 0.0
            try:
                inf_freq = float(record.get('Infection_Freq', 0)) if pd.notna(record.get('Infection_Freq')) else 0.0
            except (ValueError, TypeError):
                inf_freq = 0.0
                
            sample_id = clean_text(record.get('ID', f'S{idx+1}'))
            
            # Check if already exists
            existing = AntibioticResistance.query.filter_by(sample_id=sample_id).first()
            if existing:
                continue
                
            # For now, skip patient matching (Patient model doesn't have email/address)
            patient_id = None
                
            ar = AntibioticResistance(
                sample_id=sample_id,
                patient_id=patient_id,
                patient_name=record.get('Name'),
                patient_email=record.get('Email'),
                patient_address=record.get('Address'),
                age_gender=record.get('age/gender'),
                bacterial_species=record.get('Souches'),
                diabetes=record.get('Diabetes'),
                hypertension=record.get('Hypertension'),
                previous_hospitalization=record.get('Hospital_before'),
                infection_frequency=inf_freq,
                amx_amp=record.get('AMX/AMP'),
                amc=record.get('AMC'),
                cz=record.get('CZ'),
                fox=record.get('FOX'),
                ctx_cro=record.get('CTX/CRO'),
                ipm=record.get('IPM'),
                gen=record.get('GEN'),
                an=record.get('AN'),
                nalidixic_acid=record.get('Acide nalidixique'),
                ofx=record.get('ofx'),
                cip=record.get('CIP'),
                chloramphenicol=record.get('C'),
                co_trimoxazole=record.get('Co-trimoxazole'),
                furanes=record.get('Furanes'),
                colistine=record.get('colistine'),
                collection_date=record.get('Collection_Date'),
                notes=record.get('Notes'),
                source_dataset='Bacteria_dataset_Multiresictance'
            )
            with db.session.no_autoflush:
                db.session.add(ar)
            imported_count += 1
        db.session.commit()
        print(f"  Successfully imported {imported_count} antibiotic resistance records")
        return imported_count
    except Exception as e:
        print(f"  Error importing antibiotic resistance data: {e}")
        db.session.rollback()
        return 0


def create_comprehensive_sample_patients():
    """Create sample patients covering various TB scenarios"""
    print("Creating comprehensive sample patients...")
    
    sample_patients = []
    raw_samples = [
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
            'diabetes': 'No',
            'weight': 72,
            'persistent_cough_duration_weeks': 3,
            'contact_with_tb_patient': 'Yes',
            'previous_tb_treatment': 'No',
            'smoking_status': 'Former',
            'alcohol_use': 'Occasional',
            'oxygen_saturation_spo2': 95
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
            'diabetes': 'No',
            'weight': 65,
            'persistent_cough_duration_weeks': 2,
            'contact_with_tb_patient': 'No',
            'previous_tb_treatment': 'No',
            'smoking_status': 'Never',
            'alcohol_use': 'Never',
            'oxygen_saturation_spo2': 97
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
            'diabetes': 'Yes',
            'weight': 68,
            'persistent_cough_duration_weeks': 4,
            'contact_with_tb_patient': 'Yes',
            'previous_tb_treatment': 'Yes',
            'smoking_status': 'Current',
            'alcohol_use': 'Regular',
            'oxygen_saturation_spo2': 92
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
            'diabetes': 'No',
            'weight': 58,
            'persistent_cough_duration_weeks': 5,
            'contact_with_tb_patient': 'Yes',
            'previous_tb_treatment': 'No',
            'smoking_status': 'Never',
            'alcohol_use': 'Never',
            'oxygen_saturation_spo2': 93
        }
    ]

    for raw in raw_samples:
        sym_fields = extract_symptom_fields(raw['symptoms'])
        sample_patients.append({**raw, **sym_fields})
    
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
        print("=== TB Predictive EHR Analytics Dashboard - Data Import ===")
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
        atc_ddd_path = os.path.join(data_raw_dir, "WHO ATC-DDD 2026-04-25.csv")
        lab_results_path = os.path.join(data_raw_dir, "multi_hospital_lab_results.csv")
        ar_path = os.path.join(data_raw_dir, "Bacteria_dataset_Multiresictance.csv")

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

        synthetic_path = os.path.join(data_raw_dir, "synthetic_tb_patients.csv")
        total_imported += import_synthetic_dataset(synthetic_path)
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

        if os.path.exists(atc_ddd_path):
            import_atc_ddd_dataset(atc_ddd_path)
            print()
        else:
            print(f"WHO ATC-DDD dataset not found at: {atc_ddd_path}")
            print()
        
        if os.path.exists(lab_results_path):
            import_multi_hospital_lab_results(lab_results_path)
            print()
        else:
            print(f"Multi-hospital lab results not found at: {lab_results_path}")
            print()
        
        if os.path.exists(ar_path):
            import_antibiotic_resistance(ar_path)
            print()
        else:
            print(f"Antibiotic resistance dataset not found at: {ar_path}")
            print()
        
        # Create sample patients only when the database is still empty.
        if Patient.query.count() == 0:
            create_comprehensive_sample_patients()
        
        total_patients = Patient.query.count()
        total_lab_results = DetailedLabResult.query.count()
        total_ar_records = AntibioticResistance.query.count()
        print(f"\n=== Import Complete ===")
        print(f"Total patients in database: {total_patients}")
        print(f"Total detailed lab results: {total_lab_results}")
        print(f"Total antibiotic resistance records: {total_ar_records}")
        print("The system is ready to use!")

if __name__ == "__main__":
    main()
