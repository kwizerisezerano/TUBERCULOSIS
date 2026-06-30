
from app import app, db
from models.models import PatientConsent
from sqlalchemy import inspect, text

with app.app_context():
    print("Adding PatientConsent table to database...")
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'patient_consent' not in tables:
        # Create the table using db.create_all()
        print("Creating patient_consent table...")
        db.create_all()
        print("PatientConsent table created successfully!")
    else:
        print("patient_consent table already exists!")
    
    print("✅ Database migration complete!")
