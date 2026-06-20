import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

def main():
    output_file_path = "results.txt"
    with open(output_file_path, "w", encoding="utf-8") as out_file:
        def log(text):
            print(text)
            out_file.write(text + "\n")
        
        log("="*80)
        log("            TUBERCULOSIS (TB) DIAGNOSTIC SYSTEM")
        log("="*80)
        log("")
        
        # Load data
        csv_path = "../synthetic_tb_data_bangladesh.csv"
        if not os.path.exists(csv_path):
            csv_path = "../../synthetic_tb_data_bangladesh.csv"
            if not os.path.exists(csv_path):
                csv_path = "synthetic_tb_data_bangladesh.csv"
                
        log(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        log(f"Successfully loaded {len(df)} patient records!")
        log("")
        
        # Feature engineering
        log("Preprocessing data...")
        df['has_fever'] = df['Symptoms'].str.contains('Fever', case=False, na=False).astype(int)
        df['has_cough'] = df['Symptoms'].str.contains('Cough', case=False, na=False).astype(int)
        df['has_weight_loss'] = df['Symptoms'].str.contains('Weight', case=False, na=False).astype(int)
        df['has_night_sweats'] = df['Symptoms'].str.contains('Night', case=False, na=False).astype(int)
        
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
        
        # Train model
        log("Training Random Forest model...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        log(f"Model trained successfully! Accuracy: {accuracy:.2f}")
        
        log("\nClassification Report:")
        report = classification_report(y_test, y_pred)
        for line in report.split("\n"):
            log(line)
        
        # Save model
        os.makedirs("models", exist_ok=True)
        model_path = "models/tb_model.pkl"
        joblib.dump(model, model_path)
        log(f"\nModel saved to {model_path}")
        
        # Sample patient reports
        log("\n" + "="*80)
        log("Testing with sample patients from the dataset...")
        log("="*80)
        
        for idx in range(3):
            row = df.iloc[idx]
            log(f"\n{'='*80}")
            log(f"Patient {row['Patient ID']}")
            log("="*80)
            
            # Simple diagnosis
            risk = "Low"
            symptoms = row['Symptoms']
            if 'Cough' in symptoms and 'Weight' in symptoms:
                risk = "High"
            elif 'Fever' in symptoms or 'Night' in symptoms:
                risk = "Moderate"
                
            log(f"Symptoms: {symptoms}")
            log(f"Risk Level: {risk}")
            log(f"Sputum Test: {row['Sputum Smear Test']}")
            log(f"GeneXpert Test: {row['GeneXpert Test']}")
            log(f"Chest X-ray: {row['Chest X-ray Results']}")
            log(f"Drug Resistance: {row['Drug Resistance']}")
            
            treatment = "Drug-sensitive: 6-month course"
            if row['Drug Resistance'] == 'Yes':
                treatment = "Drug-resistant: 18-24 month course"
                
            log(f"Recommended Treatment: {treatment}")
        
        log("\n" + "="*80)
        log("DISCLAIMER: This system is for educational purposes only.")
        log("Always consult with qualified medical professionals.")
        log("="*80)
        
        log(f"\nAll results saved to {output_file_path}")

if __name__ == "__main__":
    main()
