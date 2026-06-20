import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from models.models import db, Patient

def train_model_from_database():
    # Get all patients from database
    patients = Patient.query.all()
    
    if len(patients) < 10:
        # If not enough data, create synthetic data for demonstration
        return create_synthetic_model()
    
    # Prepare training data
    data = []
    for patient in patients:
        symptoms = patient.symptoms or ''
        symptoms_lower = symptoms.lower()
        
        data.append({
            'age': patient.age or 30,
            'gender': 1 if patient.gender == 'Male' else 0,
            'has_fever': 1 if 'fever' in symptoms_lower else 0,
            'has_cough': 1 if 'cough' in symptoms_lower else 0,
            'has_weight_loss': 1 if 'weight' in symptoms_lower else 0,
            'has_night_sweats': 1 if 'night' in symptoms_lower else 0,
            'sputum_smear_test': 1 if patient.sputum_smear_test == 'Positive' else 0,
            'genexpert_test': 1 if patient.genexpert_test == 'Positive' else 0,
            'chest_xray': 1 if patient.chest_xray == 'Abnormal' else 0,
            'hiv': 1 if patient.hiv == 'Yes' else 0,
            'diabetes': 1 if patient.diabetes == 'Yes' else 0,
            'drug_resistance': patient.drug_resistance or 'No'
        })
    
    df = pd.DataFrame(data)
    
    X = df.drop('drug_resistance', axis=1)
    y = df['drug_resistance']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model and encoder
    model_path = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
    le_path = os.path.join(os.path.dirname(__file__), 'label_encoder.pkl')
    joblib.dump(model, model_path)
    joblib.dump(le, le_path)
    
    return {
        "message": "Model trained successfully from database",
        "accuracy": round(accuracy * 100, 2),
        "patients_used": len(patients),
        "classification_report": classification_report(y_test, y_pred, target_names=le.classes_)
    }

def create_synthetic_model():
    # Create synthetic training data
    np.random.seed(42)
    n_samples = 500
    
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'gender': np.random.randint(0, 2, n_samples),
        'has_fever': np.random.randint(0, 2, n_samples),
        'has_cough': np.random.randint(0, 2, n_samples),
        'has_weight_loss': np.random.randint(0, 2, n_samples),
        'has_night_sweats': np.random.randint(0, 2, n_samples),
        'sputum_smear_test': np.random.randint(0, 2, n_samples),
        'genexpert_test': np.random.randint(0, 2, n_samples),
        'chest_xray': np.random.randint(0, 2, n_samples),
        'hiv': np.random.randint(0, 2, n_samples),
        'diabetes': np.random.randint(0, 2, n_samples),
        'drug_resistance': np.random.choice(['No', 'Yes'], n_samples, p=[0.85, 0.15])
    }
    
    df = pd.DataFrame(data)
    
    # Add some patterns
    df.loc[(df['sputum_smear_test'] == 1) & (df['genexpert_test'] == 1), 'drug_resistance'] = \
        np.random.choice(['No', 'Yes'], size=len(df[(df['sputum_smear_test'] == 1) & (df['genexpert_test'] == 1)]), p=[0.7, 0.3])
    
    X = df.drop('drug_resistance', axis=1)
    y = df['drug_resistance']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model and encoder
    model_path = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
    le_path = os.path.join(os.path.dirname(__file__), 'label_encoder.pkl')
    joblib.dump(model, model_path)
    joblib.dump(le, le_path)
    
    return {
        "message": "Synthetic model created (not enough real patient data)",
        "accuracy": round(accuracy * 100, 2),
        "note": "Add more patient records to train on real data"
    }

if __name__ == "__main__":
    result = train_model_from_database()
    print(result)
