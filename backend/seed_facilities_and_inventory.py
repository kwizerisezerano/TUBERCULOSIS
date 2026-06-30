"""
Seed healthcare centers, laboratories, pharmacies and pharmacy inventory with TB medicines.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.models import Hospital, ATCDrug, PharmacyInventory, db
from app import app

# Database connection - MySQL
DATABASE_URL = 'mysql+pymysql://root:@localhost:3306/tb_diagnostic'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def seed_facilities():
    """Create healthcare centers, laboratories, and pharmacies"""
    with app.app_context():
        print("=== Creating Healthcare Centers ===")
        healthcare_centers = [
            {"name": "Kigali Health Center", "city": "Kigali", "region": "Kigali City"},
            {"name": "Remera Health Center", "city": "Kigali", "region": "Kigali City"},
            {"name": "Nyamirambo Health Center", "city": "Kigali", "region": "Kigali City"},
            {"name": "Musanze Health Center", "city": "Musanze", "region": "Northern Province"},
            {"name": "Butare Health Center", "city": "Butare", "region": "Southern Province"}
        ]
        
        for idx, hc in enumerate(healthcare_centers):
            existing = Hospital.query.filter_by(name=hc['name']).first()
            if not existing:
                hospital = Hospital(
                    hospital_id=f"HC-{idx+1:04d}",
                    name=hc['name'],
                    facility_type='Health Center',
                    city=hc['city'],
                    region=hc['region'],
                    country='Rwanda',
                    bed_capacity=50,
                    has_emergency=True,
                    has_maternity=True,
                    has_pediatrics=True
                )
                db.session.add(hospital)
                print(f"+ {hc['name']}")
            else:
                print(f"- {hc['name']} (exists)")
        
        print("\n=== Creating Laboratories ===")
        laboratories = [
            {"name": "National TB Reference Lab", "city": "Kigali", "region": "Kigali City"},
            {"name": "University Teaching Hospital Lab", "city": "Butare", "region": "Southern Province"},
            {"name": "Musanze District Lab", "city": "Musanze", "region": "Northern Province"}
        ]
        
        for idx, lab in enumerate(laboratories):
            existing = Hospital.query.filter_by(name=lab['name']).first()
            if not existing:
                hospital = Hospital(
                    hospital_id=f"LAB-{idx+1:04d}",
                    name=lab['name'],
                    facility_type='Laboratory',
                    city=lab['city'],
                    region=lab['region'],
                    country='Rwanda',
                    lab_capacity=200,
                    has_genexpert=True,
                    has_culture=True,
                    has_xray=True
                )
                db.session.add(hospital)
                print(f"+ {lab['name']}")
            else:
                print(f"- {lab['name']} (exists)")
        
        print("\n=== Creating Pharmacies ===")
        pharmacies = [
            {"name": "National Pharmacy Warehouse", "city": "Kigali", "region": "Kigali City"},
            {"name": "Kigali Central Pharmacy", "city": "Kigali", "region": "Kigali City"},
            {"name": "Butare Pharmacy", "city": "Butare", "region": "Southern Province"}
        ]
        
        for idx, pharm in enumerate(pharmacies):
            existing = Hospital.query.filter_by(name=pharm['name']).first()
            if not existing:
                hospital = Hospital(
                    hospital_id=f"PHARM-{idx+1:04d}",
                    name=pharm['name'],
                    facility_type='Pharmacy',
                    city=pharm['city'],
                    region=pharm['region'],
                    country='Rwanda',
                    pharmacy_capacity=500,
                    has_cold_storage=True
                )
                db.session.add(hospital)
                print(f"+ {pharm['name']}")
            else:
                print(f"- {pharm['name']} (exists)")
        
        db.session.commit()
        print("\n✓ Facilities created")

def seed_pharmacy_inventory():
    """Add TB medicines to pharmacy inventory for all facilities"""
    with app.app_context():
        print("\n=== Adding TB Medicines to Pharmacy Inventory ===")
        
        # Get TB medicines
        tb_drug_names = ['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol']
        tb_drugs = {}
        for name in tb_drug_names:
            drug = ATCDrug.query.filter(ATCDrug.drug_name.ilike(f'%{name}%')).first()
            if drug:
                tb_drugs[name] = drug
                print(f"Found: {name} (ID: {drug.id})")
        
        # Get all facilities
        hospitals = Hospital.query.all()
        print(f"\nFound {len(hospitals)} facilities")
        
        inventory_added = 0
        inventory_skipped = 0
        
        for hospital in hospitals:
            for drug_name, drug in tb_drugs.items():
                existing = PharmacyInventory.query.filter_by(
                    hospital_id=hospital.id,
                    atc_drug_id=drug.id
                ).first()
                
                if not existing:
                    inventory = PharmacyInventory(
                        hospital_id=hospital.id,
                        atc_drug_id=drug.id,
                        stock_quantity=1000,
                        unit_type='tablets',
                        batch_number=f'TB-{hospital.hospital_id}-001',
                        location='Main Storage'
                    )
                    db.session.add(inventory)
                    inventory_added += 1
                else:
                    inventory_skipped += 1
        
        db.session.commit()
        print(f"\n✓ Added {inventory_added} inventory records")
        print(f"✓ Skipped {inventory_skipped} existing records")

if __name__ == '__main__':
    try:
        seed_facilities()
        seed_pharmacy_inventory()
        
        # Summary
        with app.app_context():
            print("\n=== SUMMARY ===")
            print(f"Total facilities: {Hospital.query.count()}")
            
            result = db.session.execute(text("SELECT facility_type, COUNT(*) FROM hospital GROUP BY facility_type"))
            for row in result:
                print(f"  {row[0]}: {row[1]}")
            
            print(f"\nTotal pharmacy inventory: {PharmacyInventory.query.count()}")
        
        print("\n✓ Complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
