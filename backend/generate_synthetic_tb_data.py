"""
Synthetic TB Patient Data Generator
Generates WHO-aligned synthetic tuberculosis patient data with 100% complete fields
"""

import random
import csv
import os


def weighted_choice(choices, weights):
    """Choose a random item from choices with given weights"""
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for c, w in zip(choices, weights):
        if upto + w >= r:
            return c
        upto += w
    return choices[0]


# Weighted choices for realistic WHO-aligned distributions
GENDERS = ['Male', 'Female', 'Other']
GENDER_WEIGHTS = [0.48, 0.48, 0.04]

CITIES_RW = ['Kigali', 'Butare', 'Gisenyi', 'Huye', 'Musanze', 'Rubavu', 'Nyagatare', 'Rwamagana']
CITIES = CITIES_RW

SMOKING_STATUSES = ['Never', 'Former', 'Current']
SMOKING_WEIGHTS = [0.6, 0.25, 0.15]

ALCOHOL_USE = ['Never', 'Occasional', 'Regular']
ALCOHOL_WEIGHTS = [0.5, 0.3, 0.2]

# Symptoms and correlations with TB status (WHO-relevant)
TB_POSITIVE_SYMPTOMS = [
    'Persistent cough', 'Fever', 'Night sweats', 'Weight loss',
    'Chest pain', 'Fatigue', 'Shortness of breath', 'Coughing blood'
]
TB_NEGATIVE_SYMPTOMS = [
    'Headache', 'Sore throat', 'Runny nose', 'Muscle ache', 'Mild fatigue'
]

BACTERIA_SPECIES = [
    'Mycobacterium tuberculosis', 'Mycobacterium africanum',
    'Mycobacterium bovis', 'Mycobacterium microti'
]
SPECIES_WEIGHTS = [0.75, 0.12, 0.1, 0.03]

DRUG_RESISTANCE_CHOICES = ['No', 'Yes']


def generate_patient(patient_id, tb_positive=None):
    """Generate a single WHO-aligned synthetic TB patient record with NO missing data"""
    if tb_positive is None:
        tb_positive = random.random() < 0.3

    # Basic demographics
    age = random.randint(2, 90)
    gender = weighted_choice(GENDERS, GENDER_WEIGHTS)
    if gender in ['Male', 'Other']:
        weight = round(random.normalvariate(70, 15), 1)
    else:
        weight = round(random.normalvariate(60, 12), 1)
    weight = max(10, min(130, weight))
    city = random.choice(CITIES)

    # Risk factors
    if tb_positive:
        if random.random() < 0.18:
            hiv = 'Yes'
        else:
            hiv = 'No'
        if random.random() < 0.14:
            diabetes = 'Yes'
        else:
            diabetes = 'No'
        if random.random() < 0.45:
            contact_with_tb_patient = 'Yes'
        else:
            contact_with_tb_patient = 'No'
        if random.random() < 0.28:
            previous_tb_treatment = 'Yes'
        else:
            previous_tb_treatment = 'No'
    else:
        if random.random() < 0.04:
            hiv = 'Yes'
        else:
            hiv = 'No'
        if random.random() < 0.07:
            diabetes = 'Yes'
        else:
            diabetes = 'No'
        if random.random() < 0.08:
            contact_with_tb_patient = 'Yes'
        else:
            contact_with_tb_patient = 'No'
        if random.random() < 0.015:
            previous_tb_treatment = 'Yes'
        else:
            previous_tb_treatment = 'No'

    smoking_status = weighted_choice(SMOKING_STATUSES, SMOKING_WEIGHTS)
    alcohol_use = weighted_choice(ALCOHOL_USE, ALCOHOL_WEIGHTS)

    # Symptoms
    symptoms_list = []
    if tb_positive:
        num_tb_symptoms = random.randint(3, 7)
        num_other_symptoms = random.randint(0, 2)
    else:
        num_tb_symptoms = random.randint(0, 2)
        num_other_symptoms = random.randint(1, 3)

    symptoms_list.extend(random.sample(TB_POSITIVE_SYMPTOMS, num_tb_symptoms))
    symptoms_list.extend(random.sample(TB_NEGATIVE_SYMPTOMS, num_other_symptoms))
    random.shuffle(symptoms_list)
    symptoms = ', '.join(symptoms_list)

    # Extract boolean symptom fields
    def has_symptom(key):
        if key.lower() in symptoms.lower():
            return 'yes'
        else:
            return 'no'

    has_fever = has_symptom('fever')
    has_cough = has_symptom('cough')
    has_blood = has_symptom('blood')
    has_chest_pain = has_symptom('chest pain')
    has_night_sweats = has_symptom('night sweats')
    has_weight_loss = has_symptom('weight loss')
    has_fatigue = has_symptom('fatigue') or has_symptom('tired')
    has_shortness_of_breath = has_symptom('shortness of breath') or has_symptom('breathlessness')

    if has_cough == 'yes' and tb_positive:
        persistent_cough_duration_weeks = random.randint(2, 12)
    else:
        persistent_cough_duration_weeks = random.randint(0, 2)

    # Test results (NO UNKNOWN values!)
    def test_result(prob_positive):
        if random.random() < prob_positive:
            return 'Positive'
        else:
            return 'Negative'

    if tb_positive:
        sputum_smear_test = test_result(0.75)
        genexpert_test = test_result(0.9)
        if random.random() < 0.88:
            chest_xray = 'Abnormal'
        else:
            chest_xray = 'Normal'
        tb_culture = test_result(0.7)
        tst = test_result(0.8)
        igra = test_result(0.85)
        drug_resistance = weighted_choice(DRUG_RESISTANCE_CHOICES, [0.72, 0.28])
        bacteria_species = weighted_choice(BACTERIA_SPECIES, SPECIES_WEIGHTS)
    else:
        sputum_smear_test = test_result(0.03)
        genexpert_test = test_result(0.02)
        if random.random() < 0.9:
            chest_xray = 'Normal'
        else:
            chest_xray = 'Abnormal'
        tb_culture = test_result(0.01)
        tst = test_result(0.08)
        igra = test_result(0.06)
        drug_resistance = 'No'
        bacteria_species = 'Mycobacterium tuberculosis'

    if not tb_positive:
        oxygen_saturation_spo2 = round(random.normalvariate(97.5, 1.8), 1)
    else:
        oxygen_saturation_spo2 = round(random.normalvariate(92.5, 3.5), 1)
    oxygen_saturation_spo2 = max(85, min(100, oxygen_saturation_spo2))

    if tb_positive:
        tb_status_label = 'Yes'
    else:
        tb_status_label = 'No'

    return {
        'patient_id': 'SYN%06d' % patient_id,
        'first_name': 'SyntheticPatient%d' % patient_id,
        'last_name': 'PatientLast%d' % patient_id,
        'age': age,
        'gender': gender,
        'city': city,
        'symptoms': symptoms,
        'sputum_smear_test': sputum_smear_test,
        'genexpert_test': genexpert_test,
        'chest_xray': chest_xray,
        'tb_culture': tb_culture,
        'tst': tst,
        'igra': igra,
        'drug_resistance': drug_resistance,
        'bacteria_species': bacteria_species,
        'hiv': hiv,
        'diabetes': diabetes,
        'weight': weight,
        'persistent_cough_duration_weeks': persistent_cough_duration_weeks,
        'contact_with_tb_patient': contact_with_tb_patient,
        'previous_tb_treatment': previous_tb_treatment,
        'smoking_status': smoking_status,
        'alcohol_use': alcohol_use,
        'oxygen_saturation_spo2': oxygen_saturation_spo2,
        'tb_status_label': tb_status_label,
        'source_dataset': 'Synthetic Data',
        'source_row_id': str(patient_id)
    }


def validate_patient_data(patients):
    """Validate that all patient data has no missing values and meets quality standards"""
    errors = []

    required_fields = [
        'patient_id', 'first_name', 'last_name', 'age', 'gender', 'city',
        'symptoms', 'sputum_smear_test', 'genexpert_test', 'chest_xray',
        'tb_culture', 'tst', 'igra', 'drug_resistance', 'bacteria_species',
        'hiv', 'diabetes', 'weight', 'persistent_cough_duration_weeks',
        'contact_with_tb_patient', 'previous_tb_treatment', 'smoking_status',
        'alcohol_use', 'oxygen_saturation_spo2', 'tb_status_label',
        'source_dataset', 'source_row_id'
    ]

    for idx, patient in enumerate(patients):
        patient_num = idx + 1
        for field in required_fields:
            if field not in patient:
                errors.append('Patient %d: Missing field %r' % (patient_num, field))
                continue

        for field, value in patient.items():
            if value is None:
                errors.append('Patient %d: Field %r is None' % (patient_num, field))
            elif isinstance(value, str) and value.strip() == '':
                errors.append('Patient %d: Field %r is empty' % (patient_num, field))

    return len(errors) == 0, errors


def generate_dataset(num_patients, output_file=None):
    """Generate a complete synthetic WHO-aligned dataset"""
    patients = []
    num_tb_pos = int(num_patients * 0.3)
    num_tb_neg = num_patients - num_tb_pos

    for i in range(num_tb_pos):
        patients.append(generate_patient(i + 1, tb_positive=True))
    for i in range(num_tb_neg):
        patients.append(generate_patient(num_tb_pos + i + 1, tb_positive=False))

    random.shuffle(patients)

    # Validate before saving
    is_valid, validation_errors = validate_patient_data(patients)
    if not is_valid:
        print('WARNING: Data validation errors found:')
        for error in validation_errors[:10]:
            print('  - %s' % error)
        if len(validation_errors) > 10:
            print('  ... and %d more errors' % (len(validation_errors) - 10))
    else:
        print('OK All data validated - 100%% complete with no missing values!')

    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if patients:
                writer = csv.DictWriter(f, fieldnames=patients[0].keys())
                writer.writeheader()
                writer.writerows(patients)

    return patients


if __name__ == '__main__':
    print('Generating WHO-aligned synthetic TB patient data...')
    data_dir = 'data/raw'
    dataset = generate_dataset(6000, output_file='%s/synthetic_tb_patients.csv' % data_dir)
    print('Generated %d synthetic patients with 100%% complete data! Saved to %s/synthetic_tb_patients.csv' % (len(dataset), data_dir))
