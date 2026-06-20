"""
Train initial model with synthetic data
Run this once to create the trained_model.pkl and label_encoder.pkl files
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def create_synthetic_model():
    print("Creating synthetic training data...")
    
    # Create synthetic training data
    np.random.seed(42)
    n_samples = 500
    
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'gender': np.random.randint(0, 2, n_samples),  # 0 = Female, 1 = Male
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
    
    # Add patterns: higher test positivity correlates with drug resistance
    mask = (df['sputum_smear_test'] == 1) & (df['genexpert_test'] == 1)
    df.loc[mask, 'drug_resistance'] = np.random.choice(
        ['No', 'Yes'], 
        size=len(df[mask]), 
        p=[0.6, 0.4]
    )
    
    X = df.drop('drug_resistance', axis=1)
    y = df['drug_resistance']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    print("Training RandomForest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = (y_pred == y_test).mean()
    print(f"Model trained with accuracy: {accuracy:.2%}")
    
    # Save model and encoder
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/trained_model.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')
    
    print("Model saved to models/trained_model.pkl")
    print("Label encoder saved to models/label_encoder.pkl")
    print("\n✅ Initial model created successfully!")

if __name__ == "__main__":
    create_synthetic_model()
