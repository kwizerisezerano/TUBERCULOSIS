
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["BOOTSTRAP_RUNNING"] = "1"
print("Starting minimal password reset script...", flush=True)

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from models.models import db, Patient

# Create minimal Flask app
app = Flask(__name__)

# Configure database
from config import Config
app.config.from_object(Config)

# Initialize DB
db.init_app(app)
print("DB initialized", flush=True)

with app.app_context():
    print("App context created", flush=True)
    
    all_patients = Patient.query.all()
    print(f"Found {len(all_patients)} patients!", flush=True)
    
    count = 0
    for patient in all_patients:
        patient.set_password("Patient123!")
        db.session.add(patient)
        count += 1
        
        if count % 1000 == 0:
            print(f"Processed {count} patients...", flush=True)
            db.session.commit()
            
    db.session.commit()
    print(f"COMPLETED! {count} patients updated! All passwords = Patient123!", flush=True)
