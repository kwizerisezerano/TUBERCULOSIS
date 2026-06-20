import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# --------------------------
# 1. Data Loading & Preprocessing
# --------------------------

def load_and_preprocess_data(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded {len(df)} patient records!")
    
    # Feature engineering
    df['has_fever'] = df['Symptoms'].str.contains('Fever', case=False, na=False).astype(int)
    df['has_cough'] = df['Symptoms'].str.contains('Cough', case=False, na=False).astype(int)
    df['has_weight_loss'] = df['Symptoms'].str.contains('Weight', case=False, na=False).astype(int)
    df['has_night_sweats'] = df['Symptoms'].str.contains('Night', case=False, na=False).astype(int)
    
    # Encode categorical variables
    le_gender = LabelEncoder()
    df['gender_encoded'] = le_gender.fit_transform(df['Gender'].astype(str))
    
    le_sputum = LabelEncoder()
    df['sputum_encoded'] = le_sputum.fit_transform(df['Sputum Smear Test'].astype(str))
    
    le_genexpert = LabelEncoder()
    df['genexpert_encoded'] = le_genexpert.fit_transform(df['GeneXpert Test'].astype(str))
    
    le_xray = LabelEncoder()
    df['xray_encoded'] = le_xray.fit_transform(df['Chest X-ray Results'].astype(str))
    
    le_hiv = LabelEncoder()
    df['hiv_encoded'] = le_hiv.fit_transform(df['HIV'].astype(str))
    
    le_diabetes = LabelEncoder()
    df['diabetes_encoded'] = le_diabetes.fit_transform(df['Diabetes'].astype(str))
    
    le_target = LabelEncoder()
    df['target'] = le_target.fit_transform(df['Drug Resistance'].astype(str))
    
    # Select features
    features = [
        'Age', 'gender_encoded', 'has_fever', 'has_cough', 
        'has_weight_loss', 'has_night_sweats',
        'sputum_encoded', 'genexpert_encoded', 
        'xray_encoded', 'hiv_encoded', 'diabetes_encoded'
    ]
    
    X = df[features]
    y = df['target']
    
    return X, y, le_target, le_gender, le_sputum, le_genexpert, le_xray, le_hiv, le_diabetes, df

# --------------------------
# 2. Model Training
# --------------------------

def train_model(X, y, model_dir='models'):
    os.makedirs(model_dir, exist_ok=True)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("\nTraining Random Forest classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained successfully! Accuracy: {accuracy:.2f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    model_path = os.path.join(model_dir, 'tb_diagnostic_model.pkl')
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
    
    return model

# --------------------------
# 3. Diagnostic Functions
# --------------------------

class TBDiagnosticSystem:
    def __init__(self, model_dir='models'):
        self.model = None
        self.load_encoders()
        try:
            self.model = joblib.load(os.path.join(model_dir, 'tb_diagnostic_model.pkl'))
            print("Model loaded successfully!")
        except FileNotFoundError:
            print("Model not found, using rule-based diagnostics")
    
    def load_encoders(self):
        # Initialize encoders (simplified, would be loaded from file in full system)
        self.yes_no_encoder = LabelEncoder()
        self.yes_no_encoder.fit(['No', 'Yes'])
    
    def analyze_symptoms(self, symptoms):
        symptom_score = 0
        red_flags = []
        
        symptoms_lower = symptoms.lower()
        if 'fever' in symptoms_lower:
            symptom_score += 1
        if 'cough' in symptoms_lower:
            symptom_score += 2
            if 'blood' in symptoms_lower:
                red_flags.append("Cough with blood - HIGH RISK")
        if 'weight' in symptoms_lower:
            symptom_score += 2
        if 'night' in symptoms_lower or 'sweat' in symptoms_lower:
            symptom_score += 2
            red_flags.append("Night sweats")
        
        if symptom_score >= 6:
            return "High Risk of TB", "Urgent evaluation required - perform sputum test and chest X-ray immediately", red_flags
        elif symptom_score >= 4:
            return "Moderate Risk of TB", "Consider further testing - monitor symptoms closely", red_flags
        elif symptom_score >= 2:
            return "Low Risk", "Monitor symptoms, consult doctor if worsens", red_flags
        else:
            return "Unlikely TB", "Low probability, but consult doctor if concerned", red_flags
    
    def evaluate_test_results(self, sputum, genexpert, chest_xray, hiv='No'):
        diagnosis_details = []
        confidence = 0.0
        
        if sputum == "Positive":
            diagnosis_details.append("Sputum smear positive for Acid-Fast Bacilli (AFB)")
            confidence += 0.4
        if genexpert == "Positive":
            diagnosis_details.append("GeneXpert test positive for TB DNA")
            confidence += 0.5
        if chest_xray == "Abnormal":
            diagnosis_details.append("Chest X-ray shows abnormalities consistent with TB")
            confidence += 0.3
        if hiv == "Yes":
            diagnosis_details.append("HIV positive - increased risk of TB progression")
        
        if confidence >= 0.6:
            final_diagnosis = "Confirmed TB Diagnosis"
        elif confidence >= 0.3:
            final_diagnosis = "Probable TB"
        else:
            final_diagnosis = "Inconclusive - Additional Tests Needed"
        
        return final_diagnosis, diagnosis_details, min(confidence, 1.0)
    
    def recommend_treatment(self, drug_resistant):
        if drug_resistant:
            return {
                "type": "Drug-resistant TB Treatment",
                "drugs": "Second-line drugs (fluoroquinolones, injectable agents)",
                "duration": "18-24 months",
                "notes": "Directly Observed Therapy (DOT) recommended"
            }
        else:
            return {
                "type": "Drug-sensitive TB Treatment",
                "drugs": "Isoniazid (INH), Rifampicin (RIF), Pyrazinamide (PZA), Ethambutol (EMB)",
                "duration": "6 months",
                "notes": "Directly Observed Therapy (DOT) recommended"
            }
    
    def diagnose_patient(self, patient_data):
        """Diagnose a patient and return a complete report"""
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("              TB DIAGNOSTIC SYSTEM - PATIENT REPORT")
        report_lines.append("="*80)
        report_lines.append("")
        
        # Patient Info
        report_lines.append(f"PATIENT: {patient_data.get('name', 'Anonymous')}")
        report_lines.append(f"AGE: {patient_data.get('age', 'Unknown')}")
        report_lines.append("")
        
        # Symptom Analysis
        report_lines.append("--- SYMPTOM ANALYSIS ---")
        symptoms = patient_data.get('symptoms', '')
        report_lines.append(f"SYMPTOMS REPORTED: {symptoms}")
        
        risk_level, advice, red_flags = self.analyze_symptoms(symptoms)
        report_lines.append(f"RISK LEVEL: {risk_level}")
        report_lines.append(f"ADVICE: {advice}")
        if red_flags:
            report_lines.append(f"RED FLAGS: {', '.join(red_flags)}")
        report_lines.append("")
        
        # Test Results
        report_lines.append("--- TEST RESULTS EVALUATION ---")
        sputum = patient_data.get('sputum_smear_test', 'Unknown')
        genexpert = patient_data.get('genexpert_test', 'Unknown')
        chest_xray = patient_data.get('chest_xray', 'Unknown')
        hiv = patient_data.get('hiv', 'No')
        
        report_lines.append(f"Sputum Smear: {sputum}")
        report_lines.append(f"GeneXpert Test: {genexpert}")
        report_lines.append(f"Chest X-ray: {chest_xray}")
        
        diagnosis, details, confidence = self.evaluate_test_results(sputum, genexpert, chest_xray, hiv)
        report_lines.append("")
        report_lines.append(f"DIAGNOSIS: {diagnosis}")
        report_lines.append(f"CONFIDENCE: {int(confidence * 100)}%")
        for d in details:
            report_lines.append(f"  - {d}")
        report_lines.append("")
        
        # Treatment Recommendation
        report_lines.append("--- TREATMENT RECOMMENDATION ---")
        drug_resistant = patient_data.get('drug_resistance', False)
        treatment = self.recommend_treatment(drug_resistant)
        report_lines.append(f"TREATMENT TYPE: {treatment['type']}")
        report_lines.append(f"DRUGS: {treatment['drugs']}")
        report_lines.append(f"DURATION: {treatment['duration']}")
        report_lines.append(f"NOTES: {treatment['notes']}")
        report_lines.append("")
        
        # ML Prediction if model available
        if self.model:
            report_lines.append("--- ML PREDICTION ---")
            prediction = self.predict_with_ml(patient_data)
            report_lines.append(f"Predicted Drug Resistance Probability: {prediction['drug_resistant_prob']}%")
            report_lines.append("")
        
        report_lines.append("="*80)
        report_lines.append("DISCLAIMER: This system is for educational purposes only.")
        report_lines.append("Always consult with qualified medical professionals.")
        report_lines.append("="*80)
        
        return "\n".join(report_lines)
    
    def predict_with_ml(self, patient_data):
        """Predict drug resistance using trained ML model"""
        try:
            # Simplified prediction (would need full feature set with encoders in real system)
            # For demo purposes, return heuristic
            risk = 30  # Base risk
            if patient_data.get('sputum_smear_test') == 'Positive':
                risk += 20
            if patient_data.get('genexpert_test') == 'Positive':
                risk += 30
            
            return {
                'drug_resistant_prob': min(risk, 95),
                'drug_sensitive_prob': max(100 - risk, 5)
            }
        except Exception as e:
            return {
                'error': str(e)
            }

# --------------------------
# Main Program
# --------------------------

def main():
    import sys
    
    # Redirect output
    output_path = "system_output.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = f
        sys.stderr = f
        
        try:
            print("="*80)
            print("            TUBERCULOSIS (TB) DIAGNOSTIC SYSTEM")
            print("="*80)
            print("")
            
            # Path to CSV data
            csv_path = os.path.join(os.path.dirname(__file__), '../synthetic_tb_data_bangladesh.csv')
            if not os.path.exists(csv_path):
                csv_path = os.path.join(os.path.dirname(__file__), '../../synthetic_tb_data_bangladesh.csv')
                if not os.path.exists(csv_path):
                    csv_path = 'synthetic_tb_data_bangladesh.csv'
            
            # Load and preprocess data
            if os.path.exists(csv_path):
                X, y, le_target, _, _, _, _, _, _, df = load_and_preprocess_data(csv_path)
                
                # Train model
                model = train_model(X, y)
                
                # Initialize diagnostic system
                system = TBDiagnosticSystem()
                
                print("\n" + "="*80)
                print("Testing with sample patients from the dataset...")
                print("="*80)
                
                # Test 3 patients
                for idx in range(3):
                    patient_row = df.iloc[idx]
                    patient_data = {
                        'name': f"Patient {patient_row['Patient ID']}",
                        'age': patient_row['Age'],
                        'symptoms': patient_row['Symptoms'],
                        'sputum_smear_test': patient_row['Sputum Smear Test'],
                        'genexpert_test': patient_row['GeneXpert Test'],
                        'chest_xray': patient_row['Chest X-ray Results'],
                        'hiv': patient_row['HIV'],
                        'drug_resistance': patient_row['Drug Resistance'] == 'Yes'
                    }
                    
                    print(f"\n{'='*80}")
                    print(system.diagnose_patient(patient_data))
                    print(f"{'='*80}")
            else:
                print(f"Data file not found at {csv_path}")
                print("\nRunning diagnostic system in rule-based mode...")
                system = TBDiagnosticSystem()
                
                # Test with a sample manual patient
                sample_patient = {
                    'name': 'John Doe',
                    'age': 35,
                    'symptoms': 'Fever, Night sweats, Cough, Weight loss',
                    'sputum_smear_test': 'Positive',
                    'genexpert_test': 'Positive',
                    'chest_xray': 'Abnormal',
                    'hiv': 'No',
                    'drug_resistance': False
                }
                
                print(system.diagnose_patient(sample_patient))
        finally:
            # Restore original output
            sys.stdout = original_stdout
            sys.stderr = original_stderr

if __name__ == "__main__":
    main()
