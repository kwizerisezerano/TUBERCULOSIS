"""
Simple script to add TB medicines directly to database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import ATCDrug, PharmacyInventory, Hospital

# Database connection - MySQL
DATABASE_URL = 'mysql+pymysql://root:@localhost:3306/tb_diagnostic'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def add_tb_medicines():
    try:
        # Define TB medicines
        tb_medicines = [
            {
                "atc_code": "J04AC01",
                "atc_level_1": "J",
                "atc_level_2": "J04",
                "atc_level_3": "J04A",
                "atc_level_4": "J04AC",
                "atc_level_5": "J04AC01",
                "drug_name": "Isoniazid",
                "ddd": 0.3,
                "ddd_unit": "g",
                "administration_route": "Oral"
            },
            {
                "atc_code": "J04AC02",
                "atc_level_1": "J",
                "atc_level_2": "J04",
                "atc_level_3": "J04A",
                "atc_level_4": "J04AC",
                "atc_level_5": "J04AC02",
                "drug_name": "Rifampicin",
                "ddd": 0.6,
                "ddd_unit": "g",
                "administration_route": "Oral"
            },
            {
                "atc_code": "J04AC05",
                "atc_level_1": "J",
                "atc_level_2": "J04",
                "atc_level_3": "J04A",
                "atc_level_4": "J04AC",
                "atc_level_5": "J04AC05",
                "drug_name": "Pyrazinamide",
                "ddd": 2.0,
                "ddd_unit": "g",
                "administration_route": "Oral"
            },
            {
                "atc_code": "J04AC03",
                "atc_level_1": "J",
                "atc_level_2": "J04",
                "atc_level_3": "J04A",
                "atc_level_4": "J04AC",
                "atc_level_5": "J04AC03",
                "drug_name": "Ethambutol",
                "ddd": 1.2,
                "ddd_unit": "g",
                "administration_route": "Oral"
            }
        ]
        
        print("=== Adding TB Medicines ===")
        
        added_drugs = 0
        for drug_data in tb_medicines:
            existing = session.query(ATCDrug).filter_by(atc_code=drug_data['atc_code']).first()
            if not existing:
                drug = ATCDrug(**drug_data)
                session.add(drug)
                added_drugs += 1
                print(f"+ {drug_data['drug_name']}")
            else:
                print(f"- {drug_data['drug_name']} (exists)")
        
        session.commit()
        print(f"\nAdded {added_drugs} drugs")
        
        # Get hospital
        hospital = session.query(Hospital).first()
        if not hospital:
            print("\nNo hospital found!")
            return
        
        print(f"\nHospital: {hospital.name}")
        
        # Add inventory
        added_inv = 0
        for drug_data in tb_medicines:
            drug = session.query(ATCDrug).filter_by(atc_code=drug_data['atc_code']).first()
            if drug:
                existing = session.query(PharmacyInventory).filter_by(
                    hospital_id=hospital.id,
                    atc_drug_id=drug.id
                ).first()
                if not existing:
                    inv = PharmacyInventory(
                        hospital_id=hospital.id,
                        atc_drug_id=drug.id,
                        stock_quantity=1000,
                        unit_type='tablets',
                        batch_number='TB-INITIAL-001',
                        location='Main Pharmacy'
                    )
                    session.add(inv)
                    added_inv += 1
                    print(f"+ {drug.drug_name} (1000 units)")
        
        session.commit()
        print(f"\nAdded {added_inv} inventory items")
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    add_tb_medicines()
