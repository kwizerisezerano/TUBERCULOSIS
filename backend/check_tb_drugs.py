from app import app, db, ATCDrug, PharmacyInventory, Hospital

with app.app_context():
    print("=== TB Drugs in Database ===")
    tb_drugs = ATCDrug.query.filter(
        ATCDrug.drug_name.ilike('%isoniazid%') | 
        ATCDrug.drug_name.ilike('%rifampicin%') | 
        ATCDrug.drug_name.ilike('%pyrazinamide%') | 
        ATCDrug.drug_name.ilike('%ethambutol%')
    ).all()
    
    for drug in tb_drugs:
        print(f"- {drug.drug_name} (ID: {drug.id}, ATC: {drug.atc_code})")
    
    print("\n=== Pharmacy Inventory ===")
    inventory = PharmacyInventory.query.all()
    print(f"Total inventory items: {len(inventory)}")
    
    for item in inventory:
        drug = ATCDrug.query.get(item.atc_drug_id)
        hospital = Hospital.query.get(item.hospital_id)
        print(f"- {drug.drug_name if drug else 'Unknown'} (Stock: {item.stock_quantity}, Hospital: {hospital.name if hospital else 'Unknown'})")
    
    print("\n=== Hospitals ===")
    hospitals = Hospital.query.all()
    print(f"Total hospitals: {len(hospitals)}")
    for h in hospitals:
        print(f"- {h.name} (ID: {h.id})")
