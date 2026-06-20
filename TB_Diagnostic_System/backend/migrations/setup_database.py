import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models import db, Patient
from flask import Flask

# Initialize app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/tb_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def setup_database():
    print("Setting up database...")
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("Tables created successfully!")
        
        # Import CSV data
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../database/synthetic_tb_data_bangladesh.csv')
        
        if os.path.exists(csv_path):
            print("Importing patient data from CSV...")
            df = pd.read_csv(csv_path)
            
            patients_to_add = []
            for idx, row in df.head(1000).iterrows():  # Import first 1000 patients for speed
                patient = Patient(
                    patient_id=str(row["Patient ID"]),
                    age=int(row["Age"]),
                    gender=row["Gender"],
                    region=row["Region"],
                    occupation=row["Occupation"],
                    date_of_diagnosis=int(row["Date of Diagnosis"]),
                    symptoms=row["Symptoms"],
                    sputum_smear_test=row["Sputum Smear Test"],
                    genexpert_test=row["GeneXpert Test"],
                    chest_xray=row["Chest X-ray Results"],
                    treatment_type=row["Treatment Type"],
                    duration_of_treatment=int(row["Duration of Treatment"]),
                    drug_resistance=row["Drug Resistance"],
                    treatment_outcome=row["Treatment Outcome"],
                    relapse=row["Relapse"],
                    mortality=row["Mortality"],
                    complications=row["Complications"],
                    malnutrition=row["Malnutrition"],
                    diabetes=row["Diabetes"],
                    hiv=row["HIV"],
                    chronic_lung_disease=row["Chronic Lung Disease"],
                    smoking_status=row["Smoking Status"],
                    alcohol_consumption=row["Alcohol Consumption"],
                    living_conditions=row["Living Conditions"],
                    access_to_healthcare=row["Access to Healthcare"],
                    city=row["City"],
                    region_code=str(row["Region Code"])
                )
                patients_to_add.append(patient)
                
            with app.app_context():
                db.session.bulk_save_objects(patients_to_add)
                db.session.commit()
                
            print(f"Successfully imported {len(patients_to_add)} patients!")
        
        print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
