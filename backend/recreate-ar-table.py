import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.models import AntibioticResistance

def recreate_ar_table():
    with app.app_context():
        # Drop the existing table if it exists
        if AntibioticResistance.__table__.exists(bind=db.engine):
            print("Dropping existing AntibioticResistance table...")
            AntibioticResistance.__table__.drop(bind=db.engine)
        
        # Create new table
        print("Creating new AntibioticResistance table...")
        db.create_all()
        
        print("Done! Now re-import the antibiotic resistance data!")

if __name__ == "__main__":
    recreate_ar_table()
