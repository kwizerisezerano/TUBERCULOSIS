import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import AntibioticResistance

app = create_app()
with app.app_context():
    ars = AntibioticResistance.query.limit(5).all()
    print(f"Found {len(ars)} AntibioticResistance records (first 5):")
    for ar in ars:
        print(f"  ID: {ar.id}, SampleID: {ar.sample_id}, PatientID: {ar.patient_id}, Bacteria: {ar.bacterial_species}")
    print(f"Total AR records: {AntibioticResistance.query.count()}")
