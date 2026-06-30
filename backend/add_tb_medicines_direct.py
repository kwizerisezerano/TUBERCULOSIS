"""
Direct database script to add TB medicines and inventory.
Bypasses API authentication by using direct database access.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, ATCDrug, PharmacyInventory, Hospital

def add_tb_medicines():
    with app.app_context():
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
        
        print("=== Adding TB Medicines to Database ===")
        
        # Add TB medicines to ATCDrug table
        added_drugs = 0
        for drug_data in tb_medicines:
            existing = ATCDrug.query.filter_by(atc_code=drug_data['atc_code']).first()
            if not existing:
                drug = ATCDrug(**drug_data)
                db.session.add(drug)
                added_drugs += 1
                print(f"✓ Added drug: {drug_data['drug_name']}")
            else:
                print(f"- Already exists: {drug_data['drug_name']}")
        
        db.session.commit()
        print(f"\nAdded {added_drugs} new TB medicines to database")
        
        # Get first hospital
        hospital = Hospital.query.first()
        if not hospital:
            print("\n⚠ No hospital found. Please create a hospital first.")
            print("You can create a hospital through the Admin panel.")
            return
        
        print(f"\n=== Using Hospital: {hospital.name} (ID: {hospital.id}) ===")
        
        # Add TB medicines to pharmacy inventory
        added_inventory = 0
        for drug_data in tb_medicines:
            drug = ATCDrug.query.filter_by(atc_code=drug_data['atc_code']).first()
            if drug:
                existing = PharmacyInventory.query.filter_by(
                    hospital_id=hospital.id,
                    atc_drug_id=drug.id
                ).first()
                
                if not existing:
                    inventory = PharmacyInventory(
                        hospital_id=hospital.id,
                        atc_drug_id=drug.id,
                        stock_quantity=1000,  # Initial stock
                        unit_type='tablets',
                        batch_number='TB-INITIAL-001',
                        location='Main Pharmacy'
                    )
                    db.session.add(inventory)
                    added_inventory += 1
                    print(f"✓ Added inventory: {drug.drug_name} (Stock: 1000)")
                else:
                    print(f"- Inventory already exists: {drug.drug_name} (Stock: {existing.stock_quantity})")
        
        db.session.commit()
        print(f"\nAdded {added_inventory} TB medicines to pharmacy inventory")
        
        # Summary
        print("\n=== Summary ===")
        tb_drug_count = ATCDrug.query.filter(
            ATCDrug.drug_name.in_(['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol'])
        ).count()
        inventory_count = PharmacyInventory.query.filter_by(hospital_id=hospital.id).count()
        
        print(f"Total TB drugs in database: {tb_drug_count}")
        print(f"Total inventory items: {inventory_count}")
        print("\n✓ TB medicines setup complete!")

if __name__ == '__main__':
    try:
        add_tb_medicines()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
