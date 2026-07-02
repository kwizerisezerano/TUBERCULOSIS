"""
Fix: add missing individual first-line TB drugs to ATCDrug table,
and fix prescription hospital_ids to match the creating doctor's hospital.
"""
from app import app
from models.models import db, ATCDrug, Prescription, User

TB_DRUGS = [
    {'atc_code': 'J04AC01', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AC', 'atc_level_5': 'J04AC01', 'drug_name': 'Isoniazid',      'ddd': 0.3,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AB02', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AB', 'atc_level_5': 'J04AB02', 'drug_name': 'Rifampicin',     'ddd': 0.6,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AK01', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AK', 'atc_level_5': 'J04AK01', 'drug_name': 'Pyrazinamide',  'ddd': 1.5,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AK02', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AK', 'atc_level_5': 'J04AK02', 'drug_name': 'Ethambutol',    'ddd': 1.2,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AM01', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AM', 'atc_level_5': 'J04AM01', 'drug_name': 'Streptomycin',  'ddd': 1.0,  'ddd_unit': 'g', 'administration_route': 'Injectable'},
    {'atc_code': 'J04AK03', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AK', 'atc_level_5': 'J04AK03', 'drug_name': 'Bedaquiline',   'ddd': 0.2,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AK06', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AK', 'atc_level_5': 'J04AK06', 'drug_name': 'Delamanid',    'ddd': 0.2,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AK05', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AK', 'atc_level_5': 'J04AK05', 'drug_name': 'Linezolid',    'ddd': 1.2,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J01MA12', 'atc_level_1': 'J', 'atc_level_2': 'J01', 'atc_level_3': 'J01M', 'atc_level_4': 'J01MA', 'atc_level_5': 'J01MA12', 'drug_name': 'Levofloxacin', 'ddd': 0.5,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J01MA14', 'atc_level_1': 'J', 'atc_level_2': 'J01', 'atc_level_3': 'J01M', 'atc_level_4': 'J01MA', 'atc_level_5': 'J01MA14', 'drug_name': 'Moxifloxacin', 'ddd': 0.4,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AK04', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AK', 'atc_level_5': 'J04AK04', 'drug_name': 'Clofazimine',  'ddd': 0.1,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J01XX08', 'atc_level_1': 'J', 'atc_level_2': 'J01', 'atc_level_3': 'J01X', 'atc_level_4': 'J01XX', 'atc_level_5': 'J01XX08', 'drug_name': 'Cycloserine',  'ddd': 0.5,  'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AB04', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AB', 'atc_level_5': 'J04AB04', 'drug_name': 'Rifabutin',    'ddd': 0.15, 'ddd_unit': 'g', 'administration_route': 'Oral'},
    {'atc_code': 'J04AB03', 'atc_level_1': 'J', 'atc_level_2': 'J04', 'atc_level_3': 'J04A', 'atc_level_4': 'J04AB', 'atc_level_5': 'J04AB03', 'drug_name': 'Rifapentine',  'ddd': 0.6,  'ddd_unit': 'g', 'administration_route': 'Oral'},
]

with app.app_context():
    # --- 1. Add missing TB drugs ---
    added = 0
    for drug_data in TB_DRUGS:
        existing = ATCDrug.query.filter_by(atc_code=drug_data['atc_code']).first()
        if existing:
            # Update drug_name if it's a combo name (e.g. J04AK01 was "Isoniazid and rifampicin")
            if existing.drug_name != drug_data['drug_name']:
                print(f"  Update id={existing.id}: '{existing.drug_name}' -> '{drug_data['drug_name']}'")
                existing.drug_name = drug_data['drug_name']
                existing.ddd = drug_data['ddd']
        else:
            db.session.add(ATCDrug(**drug_data))
            print(f"  Added: {drug_data['drug_name']} ({drug_data['atc_code']})")
            added += 1
    db.session.commit()
    print(f"Added {added} TB drugs.\n")

    # --- 2. Fix atc_drug_id on prescriptions that have None or wrong mapping ---
    fixed_rx = 0
    for p in Prescription.query.all():
        if p.atc_drug_id is None or True:  # re-resolve all to get correct individual drug
            drug = ATCDrug.query.filter(
                ATCDrug.drug_name.ilike(p.medication)  # exact match first
            ).first()
            if not drug:
                drug = ATCDrug.query.filter(
                    ATCDrug.drug_name.ilike(f'%{p.medication}%')
                ).order_by(
                    # Prefer shorter names (individual drugs over combos)
                    db.func.length(ATCDrug.drug_name)
                ).first()
            if drug and p.atc_drug_id != drug.id:
                print(f"  Fix prescription id={p.id} {p.medication}: atc_drug_id {p.atc_drug_id} -> {drug.id} ({drug.drug_name})")
                p.atc_drug_id = drug.id
                fixed_rx += 1
    db.session.commit()
    print(f"Fixed atc_drug_id on {fixed_rx} prescriptions.\n")

    # --- 3. Fix prescription hospital_ids to match the creating doctor's hospital ---
    fixed_hosp = 0
    for p in Prescription.query.all():
        creator = User.query.get(p.created_by)
        if creator and creator.hospital_id and p.hospital_id != creator.hospital_id:
            print(f"  Fix prescription id={p.id}: hospital_id {p.hospital_id} -> {creator.hospital_id} (creator={creator.username})")
            p.hospital_id = creator.hospital_id
            fixed_hosp += 1
    db.session.commit()
    print(f"Fixed hospital_id on {fixed_hosp} prescriptions.\n")

    # --- 4. Print final state ---
    print("=== Final prescriptions ===")
    for p in Prescription.query.all():
        drug = ATCDrug.query.get(p.atc_drug_id) if p.atc_drug_id else None
        print(f"  id={p.id} {p.medication:<15} atc_drug_id={p.atc_drug_id} ({drug.drug_name if drug else 'NONE'}) hospital_id={p.hospital_id}")
