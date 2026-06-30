import os
import pandas as pd
from app import app, db
from models.models import Hospital, Patient, ATCDrug

def import_healthcare_dataset():
    """Import healthcare_dataset.csv for multi-hospital simulation"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'NEWDATASETS', 'healthcare_dataset.csv', 'healthcare_dataset.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ healthcare_dataset.csv not found at {csv_path}")
        return
    
    print("=== Importing Healthcare Dataset ===")
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} rows")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Validate required columns
    required_cols = ['Hospital', 'Name', 'Age', 'Gender']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return
    
    # Data quality check
    print(f"📊 Data Quality Check:")
    print(f"  - Rows with missing Name: {df['Name'].isna().sum()}")
    print(f"  - Rows with missing Age: {df['Age'].isna().sum()}")
    print(f"  - Rows with missing Gender: {df['Gender'].isna().sum()}")
    print(f"  - Rows with missing Hospital: {df['Hospital'].isna().sum()}")
    
    # Extract unique hospitals
    unique_hospitals = df['Hospital'].unique()
    print(f"🏥 Found {len(unique_hospitals)} unique hospitals")
    print(f"⚠️  Limiting import to top 100 hospitals for performance")
    
    # Create hospitals (limit to top 100 for performance)
    hospital_map = {}
    max_hospitals = 100
    for idx, hospital_name in enumerate(unique_hospitals[:max_hospitals]):
        if not hospital_name or pd.isna(hospital_name):
            continue
            
        # Use different ID pattern to avoid conflict with default hospital
        hospital_id = f"HCD-{idx+1:04d}"
        
        # Check if hospital already exists
        existing = Hospital.query.filter_by(name=str(hospital_name).strip()).first()
        if existing:
            hospital_map[str(hospital_name).strip()] = existing.id
            print(f"  ✓ Hospital already exists: {hospital_name}")
            continue
        
        hospital = Hospital(
            hospital_id=hospital_id,
            name=str(hospital_name).strip(),
            facility_type='Hospital',
            city='Kigali',  # Default city
            region='Kigali City',
            country='Rwanda',
            bed_capacity=200,  # Default capacity
            icu_beds=20,
            source_dataset='healthcare_dataset.csv'
        )
        db.session.add(hospital)
        db.session.commit()
        hospital_map[str(hospital_name).strip()] = hospital.id
        print(f"  ✓ Created hospital: {hospital_name} (ID: {hospital_id})")
    
    # Import patients
    patients_imported = 0
    skipped_patients = 0
    error_patients = 0
    
    for idx, row in df.iterrows():
        try:
            # Validate hospital
            hospital_name = row.get('Hospital')
            if pd.isna(hospital_name) or not hospital_name:
                skipped_patients += 1
                continue
            
            hospital_id = hospital_map.get(str(hospital_name).strip())
            if not hospital_id:
                skipped_patients += 1
                continue
            
            # Generate patient ID
            patient_id = f"HC-{idx+1:06d}"
            
            # Check if patient already exists
            existing = Patient.query.filter_by(patient_id=patient_id).first()
            if existing:
                skipped_patients += 1
                continue
            
            # Parse and validate name
            name = row.get('Name')
            if pd.isna(name) or not name:
                first_name = 'Unknown'
                last_name = 'Unknown'
            else:
                name_parts = str(name).strip().split()
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Unknown'
            
            # Parse and validate age
            age = row.get('Age')
            if pd.isna(age) or age is None:
                age = 30
            else:
                try:
                    age = int(age)
                    if age < 0 or age > 150:
                        age = 30  # Invalid age, use default
                except:
                    age = 30
            
            # Parse and validate gender
            gender = row.get('Gender')
            if pd.isna(gender) or not gender:
                gender = 'Unknown'
            else:
                gender = str(gender).strip().lower()
                if gender not in ['male', 'female', 'other', 'unknown']:
                    gender = 'Unknown'
                gender = gender.capitalize()
            
            # Parse medical condition
            medical_condition = row.get('Medical Condition')
            if pd.isna(medical_condition):
                medical_condition = 'Unknown'
            else:
                medical_condition = str(medical_condition)
            
            # Parse medication
            medication = row.get('Medication')
            if pd.isna(medication):
                antibiotic_usage_history = 'Unknown'
            else:
                antibiotic_usage_history = f"Medication: {str(medication)}"
            
            # Create patient
            patient = Patient(
                patient_id=patient_id,
                hospital_id=hospital_id,
                first_name=first_name,
                last_name=last_name,
                age=age,
                gender=gender,
                weight=70.0,  # Default weight
                city='Kigali',
                source_dataset='healthcare_dataset.csv',
                source_row_id=str(idx),
                symptoms=medical_condition,
                antibiotic_usage_history=antibiotic_usage_history,
                has_fever='Yes' if 'Fever' in medical_condition else 'No',
                has_cough='Yes' if 'Cough' in medical_condition else 'No',
                has_weight_loss='Yes' if 'Weight' in medical_condition else 'No',
                has_chest_pain='Yes' if 'Chest' in medical_condition else 'No',
                has_fatigue='Yes' if 'Fatigue' in medical_condition else 'No',
                has_shortness_of_breath='Yes' if 'Breath' in medical_condition else 'No'
            )
            db.session.add(patient)
            patients_imported += 1
            
            if patients_imported % 1000 == 0:
                db.session.commit()
                print(f"  Imported {patients_imported} patients...")
                
        except Exception as e:
            error_patients += 1
            print(f"  ⚠️  Error importing patient at row {idx}: {e}")
            continue
    
    db.session.commit()
    print(f"✅ Successfully imported {patients_imported} patients from healthcare_dataset.csv")
    print(f"⚠️  Skipped {skipped_patients} patients (duplicates or missing hospital)")
    print(f"❌ Errors: {error_patients} patients")
    print(f"✅ Total hospitals in system: {Hospital.query.count()}")
    print(f"✅ Total patients in system: {Patient.query.count()}")

def import_medicine_dataset():
    """Import medicine_dataset.csv to expand ATC drug database"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'NEWDATASETS', 'medicine_dataset.csv', 'medicine_dataset.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ medicine_dataset.csv not found at {csv_path}")
        return
    
    print("\n=== Importing Medicine Dataset ===")
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} medicine records")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Validate required columns
    required_cols = ['Name', 'Strength']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return
    
    # Data quality check
    print(f"📊 Data Quality Check:")
    print(f"  - Rows with missing Name: {df['Name'].isna().sum()}")
    print(f"  - Rows with missing Strength: {df['Strength'].isna().sum()}")
    
    medicines_imported = 0
    skipped_medicines = 0
    error_medicines = 0
    
    for idx, row in df.iterrows():
        try:
            # Validate drug name
            drug_name = row.get('Name')
            if pd.isna(drug_name) or not drug_name:
                skipped_medicines += 1
                continue
            
            drug_name = str(drug_name).strip()
            
            # Check if drug already exists
            existing = ATCDrug.query.filter_by(drug_name=drug_name).first()
            if existing:
                skipped_medicines += 1
                continue
            
            # Generate ATC code (simplified - in production, use actual ATC mapping)
            atc_code = f"M{idx+1:05d}"
            
            # Parse strength
            strength_str = row.get('Strength')
            if pd.isna(strength_str) or not strength_str:
                strength_mg = 500.0
            else:
                try:
                    # Extract numeric value from strength string
                    strength_str_clean = str(strength_str).replace('mg', '').replace('g', '').strip()
                    strength_mg = float(strength_str_clean)
                    # Convert to mg if value is in grams
                    if 'g' in str(strength_str).lower():
                        strength_mg = strength_mg * 1000
                except:
                    strength_mg = 500.0
            
            # Validate strength
            if strength_mg <= 0 or strength_mg > 10000:
                strength_mg = 500.0  # Invalid strength, use default
            
            drug = ATCDrug(
                atc_code=atc_code,
                atc_level_1='J',  # Anti-infectives (default)
                atc_level_2='J01',  # Antibacterials (default)
                atc_level_3='J01C',  # Beta-lactam (default)
                atc_level_4='J01CA',  # Penicillins (default)
                atc_level_5=atc_code,
                drug_name=drug_name,
                ddd=strength_mg / 1000.0 if strength_mg > 0 else 0.5,  # Convert mg to g for DDD, default 0.5g
                ddd_unit='g',
                administration_route='oral'  # Default route
            )
            db.session.add(drug)
            medicines_imported += 1
            
            if medicines_imported % 1000 == 0:
                db.session.commit()
                print(f"  Imported {medicines_imported} medicines...")
                
        except Exception as e:
            error_medicines += 1
            print(f"  ⚠️  Error importing medicine at row {idx}: {e}")
            continue
    
    db.session.commit()
    print(f"✅ Successfully imported {medicines_imported} medicines from medicine_dataset.csv")
    print(f"⚠️  Skipped {skipped_medicines} medicines (duplicates or missing data)")
    print(f"❌ Errors: {error_medicines} medicines")
    print(f"✅ Total ATC drugs in system: {ATCDrug.query.count()}")

def import_amr_dataset():
    """Import Kaggle_AMR_Dataset_v1.0.csv for enhanced antibiogram"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'NEWDATASETS', 'Kaggle_AMR_Dataset_v1.0 (1).csv')
    
    # Try alternate path if not found
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'NEWDATASETS', 'Kaggle_AMR_Dataset_v1.0.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Kaggle_AMR_Dataset_v1.0.csv not found at {csv_path}")
        return
    
    print("\n=== Importing AMR Dataset ===")
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} AMR records")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Validate required columns
    required_cols = ['Isolate_ID', 'organism']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return
    
    # Data quality check
    print(f"📊 Data Quality Check:")
    print(f"  - Rows with missing Isolate_ID: {df['Isolate_ID'].isna().sum()}")
    print(f"  - Rows with missing organism: {df['organism'].isna().sum()}")
    
    from models.models import AntibioticResistance
    
    amr_imported = 0
    amr_updated = 0
    skipped_amr = 0
    error_amr = 0
    
    for idx, row in df.iterrows():
        try:
            # Validate sample ID
            sample_id = row.get('Isolate_ID')
            if pd.isna(sample_id) or not sample_id:
                skipped_amr += 1
                continue
            
            sample_id = str(sample_id).strip()
            
            # Map resistance classes to antibiotic fields
            # The dataset has resistance class columns (class_*) that indicate resistance
            amx_amp = 'Resistant' if row.get('class_penam', 0) == 1 else 'Sensitive'
            ctx_cro = 'Resistant' if row.get('class_cephalosporin', 0) == 1 else 'Sensitive'
            ipm = 'Resistant' if row.get('class_carbapenem', 0) == 1 else 'Sensitive'
            gen = 'Resistant' if row.get('class_aminoglycoside', 0) == 1 else 'Sensitive'
            cip = 'Resistant' if row.get('class_fluoroquinolone', 0) == 1 else 'Sensitive'
            
            # Build comprehensive resistance profile
            resistance_profile = []
            if row.get('class_penam', 0) == 1:
                resistance_profile.append('Penicillins')
            if row.get('class_cephalosporin', 0) == 1:
                resistance_profile.append('Cephalosporins')
            if row.get('class_carbapenem', 0) == 1:
                resistance_profile.append('Carbapenems')
            if row.get('class_aminoglycoside', 0) == 1:
                resistance_profile.append('Aminoglycosides')
            if row.get('class_fluoroquinolone', 0) == 1:
                resistance_profile.append('Fluoroquinolones')
            if row.get('class_tetracycline', 0) == 1:
                resistance_profile.append('Tetracyclines')
            if row.get('class_sulfonamide', 0) == 1:
                resistance_profile.append('Sulfonamides')
            if row.get('class_phenicol', 0) == 1:
                resistance_profile.append('Phenicols')
            if row.get('class_macrolide', 0) == 1:
                resistance_profile.append('Macrolides')
            
            resistance_profile_str = ', '.join(resistance_profile) if resistance_profile else 'No resistance detected'
            
            # Validate organism
            organism = row.get('organism')
            if pd.isna(organism) or not organism:
                bacterial_species = 'Unknown'
            else:
                bacterial_species = str(organism).strip()
            
            # Handle "Unknown" values - treat as actual unknown, not missing
            host = row.get('host_standardized', 'Unknown')
            if pd.isna(host):
                host = 'Unknown'
            else:
                host = str(host).strip()
            
            isolation_source = row.get('isolation_source_standardized', 'Unknown')
            if pd.isna(isolation_source):
                isolation_source = 'Unknown'
            else:
                isolation_source = str(isolation_source).strip()
            
            # Parse numeric values
            total_amr_genes = row.get('total_amr_genes', 0)
            if pd.isna(total_amr_genes):
                total_amr_genes = 0
            else:
                try:
                    total_amr_genes = int(total_amr_genes)
                except:
                    total_amr_genes = 0
            
            total_resistance_classes = row.get('total_resistance_classes', 0)
            if pd.isna(total_resistance_classes):
                total_resistance_classes = 0
            else:
                try:
                    total_resistance_classes = int(total_resistance_classes)
                except:
                    total_resistance_classes = 0
            
            # Parse collection date
            collection_date = row.get('collection_date')
            if pd.isna(collection_date):
                collection_date = 'Unknown'
            else:
                collection_date = str(collection_date).strip()
            
            # Check if sample already exists - if so, update it instead of skipping
            existing = AntibioticResistance.query.filter_by(sample_id=sample_id).first()
            if existing:
                # Update existing record with resistance profile
                existing.amx_amp = amx_amp
                existing.ctx_cro = ctx_cro
                existing.ipm = ipm
                existing.gen = gen
                existing.cip = cip
                existing.bacterial_species = bacterial_species
                existing.notes = f"Resistance Profile: {resistance_profile_str} | Host: {host} | Source: {isolation_source} | Total AMR Genes: {total_amr_genes} | Resistance Classes: {total_resistance_classes}"
                existing.collection_date = collection_date
                amr_updated += 1
                continue
            
            # Create AMR record
            amr = AntibioticResistance(
                sample_id=sample_id,
                patient_name=f"Sample_{sample_id}",  # AMR dataset doesn't have patient names
                bacterial_species=bacterial_species,
                amx_amp=amx_amp,
                ctx_cro=ctx_cro,
                ipm=ipm,
                gen=gen,
                cip=cip,
                collection_date=collection_date,
                notes=f"Resistance Profile: {resistance_profile_str} | Host: {host} | Source: {isolation_source} | Total AMR Genes: {total_amr_genes} | Resistance Classes: {total_resistance_classes}"
            )
            db.session.add(amr)
            amr_imported += 1
            
            if amr_imported % 10 == 0:
                db.session.commit()
                print(f"  Imported {amr_imported} AMR records...")
                
        except Exception as e:
            error_amr += 1
            print(f"  ⚠️  Error importing AMR record at row {idx}: {e}")
            continue
    
    db.session.commit()
    print(f"✅ Successfully imported {amr_imported} AMR records from Kaggle_AMR_Dataset_v1.0.csv")
    print(f"🔄 Updated {amr_updated} existing AMR records with resistance profiles")
    print(f"⚠️  Skipped {skipped_amr} AMR records (missing data)")
    print(f"❌ Errors: {error_amr} AMR records")
    print(f"✅ Total AMR records in system: {AntibioticResistance.query.count()}")

if __name__ == "__main__":
    with app.app_context():
        print("Starting new dataset import...")
        import_healthcare_dataset()
        import_medicine_dataset()
        import_amr_dataset()
        print("\n=== Import Complete ===")
