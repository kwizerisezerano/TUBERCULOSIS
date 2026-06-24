
"""
Synthetic TB Patient Data Generator
Generates realistic synthetic tuberculosis patient data with varied scenarios
"""

import random
import csv
from datetime import datetime, timedelta

# Weighted choices for realistic distributions
GENDERS = ['Male', 'Female', 'Other']
GENDER_WEIGHTS = [0.48, 0.48, 0.04]

CITIES_RW = ['Kigali', 'Butare', 'Gisenyi', 'Huye', 'Musanze', 'Rubavu', 'Nyagatare', 'Rwamagana']
CITIES = CITIES_RW

SMOKING_STATUSES = ['Never', 'Former', 'Current']
SMOKING_WEIGHTS = [0.6, 0.25, 0.15]

ALCOHOL_USE = ['Never', 'Occasional', 'Regular']
ALCOHOL_WEIGHTS = [0.5, 0.3, 0.2]

# Symptoms and correlations with TB status
TB_POSITIVE_SYMPTOMS = [
    'Persistent cough', 'Fever', 'Night sweats', 'Weight loss',
    'Chest pain', 'Fatigue', 'Shortness of breath', 'Coughing blood'
]
TB_NEGATIVE_SYMPTOMS = [
    'Headache', 'Sore throat', 'Runny nose', 'Muscle ache', 'Mild fatigue'
]

BACTERIA_SPECIES = [
    'Mycobacterium tuberculosis', 'Mycobacterium africanum',
    'Mycobacterium bovis', None
]
SPECIES_WEIGHTS = [0.7, 0.15, 0.05, 0.1]

DRUG_RESISTANCE_CHOICES = ['No', 'Yes']


def generate_patient(patient_id: int, tb_positive: bool = None) -&gt; dict:
    """Generate a single synthetic TB patient record"""
    if tb_positive is None:
        tb_positive = random.random() &lt; 0.4  # 40% TB positive rate

    # Basic demographics
    age = random.randint(5, 85)
    gender = random.choices(GENDERS, weights=GENDER_WEIGHTS, k=1)[0]
    weight = round(random.normalvariate(70, 15), 1) if gender == 'Male' else round(random.normalvariate(60, 12), 1)
    weight = max(20, min(120, weight))
    city = random.choice(CITIES)

    # Risk factors
    hiv = 'Yes' if (random.random() &lt; (0.15 if tb_positive else 0.05)) else 'No'
    diabetes = 'Yes' if (random.random() &lt; (0.12 if tb_positive else 0.08)) else 'No'
    contact_with_tb_patient = 'Yes' if (random.random() &lt; (0.4 if tb_positive else 0.1)) else 'No'
    previous_tb_treatment = 'Yes' if (random.random() &lt; (0.25 if tb_positive else 0.02)) else 'No'

    smoking_status = random.choices(SMOKING_STATUSES, weights=SMOKING_WEIGHTS, k=1)[0]
    alcohol_use = random.choices(ALCOHOL_USE, weights=ALCOHOL_WEIGHTS, k=1)[0]

    # Symptoms
    symptoms_list = []
    num_tb_symptoms = random.randint(3, 7) if tb_positive else random.randint(0, 2)
    num_other_symptoms = random.randint(0, 2) if tb_positive else random.randint(1, 3)

    symptoms_list.extend(random.sample(TB_POSITIVE_SYMPTOMS, num_tb_symptoms))
    symptoms_list.extend(random.sample(TB_NEGATIVE_SYMPTOMS, num_other_symptoms))
    random.shuffle(symptoms_list)
    symptoms = ', '.join(symptoms_list)

    # Extract boolean symptom fields
    def has_symptom(key):
        return 'yes' if key.lower() in symptoms.lower() else 'no'

    has_fever = has_symptom('fever')
    has_cough = has_symptom('cough')
    has_blood = has_symptom('blood')
    has_chest_pain = has_symptom('chest pain')
    has_night_sweats = has_symptom('night sweats')
    has_weight_loss = has_symptom('weight loss')
    has_fatigue = has_symptom('fatigue') or has_symptom('tired')
    has_shortness_of_breath = has_symptom('shortness of breath') or has_symptom('breathlessness')

    persistent_cough_duration_weeks = random.randint(2, 12) if has_cough == 'yes' and tb_positive else random.randint(0, 2)

    # Test results
    def test_result(prob_positive):
        r = random.random()
        if r &lt; prob_positive:
            return 'Positive'
        elif r &lt; prob_positive + 0.05:
            return 'Unknown'
        else:
            return 'Negative'

    if tb_positive:
        sputum_smear_test = test_result(0.7)
        genexpert_test = test_result(0.85)
        chest_xray = 'Abnormal' if random.random() &lt; 0.8 else ('Normal' if random.random() &lt; 0.1 else 'Unknown')
        tb_culture = test_result(0.65)
        tst = test_result(0.75)
        igra = test_result(0.8)
        drug_resistance = random.choices(DRUG_RESISTANCE_CHOICES, weights=[0.7, 0.3], k=1)[0]
        bacteria_species = random.choices(BACTERIA_SPECIES, weights=SPECIES_WEIGHTS, k=1)[0]
    else:
        sputum_smear_test = test_result(0.05)
        genexpert_test = test_result(0.03)
        chest_xray = 'Normal' if random.random() &lt; 0.85 else ('Abnormal' if random.random() &lt; 0.05 else 'Unknown')
        tb_culture = test_result(0.02)
        tst = test_result(0.1)
        igra = test_result(0.08)
        drug_resistance = 'No'
        bacteria_species = None

    oxygen_saturation_spo2 = round(random.normalvariate(97, 2) if not tb_positive else random.normalvariate(93, 4), 1)
    oxygen_saturation_spo2 = max(85, min(100, oxygen_saturation_spo2))

    return {
        'patient_id': f'SYN{patient_id:06d}',
        'first_name': f'SyntheticPatient{patient_id}',
        'last_name': '',
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
        'has_fever': has_fever,
        'has_cough': has_cough,
        'has_blood': has_blood,
        'has_chest_pain': has_chest_pain,
        'has_night_sweats': has_night_sweats,
        'has_weight_loss': has_weight_loss,
        'has_fatigue': has_fatigue,
        'has_shortness_of_breath': has_shortness_of_breath,
        'weight': weight,
        'persistent_cough_duration_weeks': persistent_cough_duration_weeks,
        'contact_with_tb_patient': contact_with_tb_patient,
        'previous_tb_treatment': previous_tb_treatment,
        'smoking_status': smoking_status,
        'alcohol_use': alcohol_use,
        'oxygen_saturation_spo2': oxygen_saturation_spo2,
        'tb_status_label': 'Yes' if tb_positive else 'No',
        'source_dataset': 'Synthetic Data',
        'source_row_id': str(patient_id)
    }


def generate_dataset(num_patients: int, output_file: str = None) -&gt; list:
    """Generate a complete synthetic dataset"""
    patients = []
    num_tb_pos = int(num_patients * 0.4)
    num_tb_neg = num_patients - num_tb_pos

    for i in range(num_tb_pos):
        patients.append(generate_patient(i + 1, tb_positive=True))
    for i in range(num_tb_neg):
        patients.append(generate_patient(num_tb_pos + i + 1, tb_positive=False))

    random.shuffle(patients)

    if output_file:
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if patients:
                writer = csv.DictWriter(f, fieldnames=patients[0].keys())
                writer.writeheader()
                writer.writerows(patients)

    return patients


if __name__ == "__main__":
    print("Generating synthetic TB patient data...")
    data_dir = "data/raw"
    dataset = generate_dataset(5000, output_file=f"{data_dir}/synthetic_tb_patients.csv")
    print(f"Generated {len(dataset)} synthetic patients! Saved to {data_dir}/synthetic_tb_patients.csv")
