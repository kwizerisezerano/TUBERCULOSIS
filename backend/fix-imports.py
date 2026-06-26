import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.models import AntibioticResistance
from import_data import import_antibiotic_resistance

def fix_ar_data():
    with app.app_context():
        print("Step 1: Dropping and recreating AntibioticResistance table...")
        # Drop the existing table if it exists
        if AntibioticResistance.__table__.exists(bind=db.engine):
            AntibioticResistance.__table__.drop(bind=db.engine)
        
        # Create new table
        db.create_all()
        print("Step 1 done!")
        
        print("Step 2: Re-importing antibiotic resistance data...")
        # Find the data file
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        ar_file = os.path.join(data_dir, 'antibiotic_resistance_data.csv')
        if os.path.exists(ar_file):
            imported = import_antibiotic_resistance(ar_file)
            print(f"Step 2 done! Imported {imported} records!")
        else:
            print(f"Could not find antibiotic resistance data file at: {ar_file}")

if __name__ == "__main__":
    fix_ar_data()
