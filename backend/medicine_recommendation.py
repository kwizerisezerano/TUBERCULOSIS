"""
Medicine Recommendation Service
Maps model predictions to required TB medicines based on WHO guidelines.
"""
from models.models import ATCDrug, PharmacyInventory, Patient, Hospital, db

# WHO TB Treatment Guidelines
TB_REGIMENS = {
    'drug_sensitive': {
        'name': 'Drug-Sensitive TB (DS-TB)',
        'phase1': {
            'name': 'Intensive Phase (2 months)',
            'medicines': ['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol'],
            'abbreviation': 'HRZE'
        },
        'phase2': {
            'name': 'Continuation Phase (4 months)',
            'medicines': ['Isoniazid', 'Rifampicin'],
            'abbreviation': 'HR'
        },
        'duration_months': 6,
        'description': 'Standard 6-month regimen for drug-sensitive TB (2HRZE/4HR)'
    },
    'mdr_tb': {
        'name': 'Multidrug-Resistant TB (MDR-TB)',
        'phase1': {
            'name': 'Intensive Phase (6-9 months)',
            'medicines': ['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol'],
            'abbreviation': 'HRZE'
        },
        'phase2': {
            'name': 'Continuation Phase (12-18 months)',
            'medicines': ['Isoniazid', 'Rifampicin'],
            'abbreviation': 'HR'
        },
        'duration_months': 18,
        'description': 'Extended regimen for MDR-TB (6-9HRZE/12-18HR)'
    },
    'latent_tb': {
        'name': 'Latent TB Infection',
        'medicines': ['Isoniazid'],
        'duration_months': 6,
        'description': 'Isoniazid preventive therapy (6H)'
    },
    'tb_hiv': {
        'name': 'TB with HIV Co-infection',
        'phase1': {
            'name': 'Intensive Phase (2 months)',
            'medicines': ['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol'],
            'abbreviation': 'HRZE'
        },
        'phase2': {
            'name': 'Continuation Phase (4 months)',
            'medicines': ['Isoniazid', 'Rifampicin'],
            'abbreviation': 'HR'
        },
        'duration_months': 6,
        'description': 'Standard regimen with ART within 2-8 weeks'
    },
    'extrapulmonary': {
        'name': 'Extrapulmonary TB',
        'phase1': {
            'name': 'Intensive Phase (2 months)',
            'medicines': ['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol'],
            'abbreviation': 'HRZE'
        },
        'phase2': {
            'name': 'Continuation Phase (7-10 months)',
            'medicines': ['Isoniazid', 'Rifampicin'],
            'abbreviation': 'HR'
        },
        'duration_months': 9,
        'description': 'Extended regimen for extrapulmonary TB (2HRZE/7-10HR)'
    }
}

# Infection type to regimen mapping
INFECTION_REGIMEN_MAP = {
    'pulmonary_positive': 'drug_sensitive',
    'pulmonary_negative': 'drug_sensitive',
    'extrapulmonary': 'extrapulmonary',
    'mdr_tb': 'mdr_tb',
    'xdr_tb': 'mdr_tb',
    'latent': 'latent_tb',
    'tb_hiv': 'tb_hiv'
}

def get_recommended_medicines(infection_type, risk_score=None, drug_resistance=None, hiv_status=None):
    """
    Get recommended medicines based on infection type and clinical factors.
    
    Args:
        infection_type: Type of TB infection (pulmonary_positive, extrapulmonary, mdr_tb, etc.)
        risk_score: Patient's TB risk score (0-100)
        drug_resistance: Drug resistance pattern from lab results
        hiv_status: HIV status (Yes/No)
    
    Returns:
        Dictionary with regimen info and required medicines
    """
    # Determine regimen based on infection type
    if infection_type in INFECTION_REGIMEN_MAP:
        regimen_key = INFECTION_REGIMEN_MAP[infection_type]
    elif drug_resistance and 'MDR' in drug_resistance:
        regimen_key = 'mdr_tb'
    elif hiv_status == 'Yes':
        regimen_key = 'tb_hiv'
    elif risk_score and risk_score >= 70:
        regimen_key = 'drug_sensitive'
    elif risk_score and risk_score >= 50:
        regimen_key = 'latent_tb'
    else:
        return None  # Low risk, no medication recommended
    
    regimen = TB_REGIMENS[regimen_key]
    
    # Get all unique medicines from all phases
    all_medicines = []
    if 'phase1' in regimen:
        all_medicines.extend(regimen['phase1']['medicines'])
    if 'phase2' in regimen:
        all_medicines.extend(regimen['phase2']['medicines'])
    else:
        all_medicines.extend(regimen.get('medicines', []))
    
    # Remove duplicates
    all_medicines = list(set(all_medicines))
    
    return {
        'regimen': regimen,
        'medicines': all_medicines,
        'regimen_key': regimen_key
    }

def check_medicine_availability(hospital_id, medicine_names):
    """
    Check if required medicines are in stock at a hospital.
    
    Args:
        hospital_id: Hospital ID
        medicine_names: List of medicine names to check
    
    Returns:
        Dictionary with availability status for each medicine
    """
    if not hospital_id:
        return {'error': 'Hospital not specified'}
    
    hospital = Hospital.query.get(hospital_id)
    if not hospital:
        return {'error': 'Hospital not found'}
    
    availability = {}
 
    for medicine_name in medicine_names:
        drug = ATCDrug.query.filter(ATCDrug.drug_name.ilike(f'%{medicine_name}%')).first()
        
        if not drug:
            availability[medicine_name] = {
                'available': False,
                'reason': 'Drug not found in database',
                'stock': 0
            }
            continue
        
        inventory = PharmacyInventory.query.filter_by(
            hospital_id=hospital_id,
            atc_drug_id=drug.id
        ).first()
        
        if not inventory:
            availability[medicine_name] = {
                'available': False,
                'reason': 'Not in inventory',
                'stock': 0
            }
        elif inventory.stock_quantity < 100:  # Minimum threshold
            availability[medicine_name] = {
                'available': False,
                'reason': 'Low stock',
                'stock': inventory.stock_quantity
            }
        else:
            availability[medicine_name] = {
                'available': True,
                'stock': inventory.stock_quantity
            }
    
    return availability

def get_prescription_recommendation(patient_id, infection_type=None):
    """
    Get complete prescription recommendation for a patient.
    
    Args:
        patient_id: Patient ID
        infection_type: Optional infection type override
    
    Returns:
        Dictionary with regimen, availability, and recommendations
    """
    from models.models import Prescription
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return {'error': 'Patient not found'}
    
    if not patient.hospital_id:
        return {'error': 'Patient hospital not found'}
    
    # Check for previous prescriptions and resistance patterns
    resistance_warning = check_previous_resistance(patient_id)
    
    # Determine infection type if not provided
    if not infection_type:
        if patient.genexpert_test == 'Positive':
            if patient.drug_resistance and 'MDR' in patient.drug_resistance:
                infection_type = 'mdr_tb'
            else:
                infection_type = 'pulmonary_positive'
        elif patient.sputum_smear_test == 'Positive':
            infection_type = 'pulmonary_positive'
        elif patient.chest_xray == 'Abnormal':
            infection_type = 'pulmonary_positive'
        elif patient.hiv == 'Yes':
            infection_type = 'tb_hiv'
        else:
            infection_type = 'latent'
    
    # Get recommended regimen
    recommendation = get_recommended_medicines(
        infection_type,
        patient.risk_score,
        patient.drug_resistance,
        patient.hiv
    )
    
    if not recommendation:
        return {
            'recommendation': 'No medication needed',
            'risk_score': patient.risk_score,
            'reason': 'Low TB risk score'
        }
    
    # Adjust regimen based on previous resistance
    if resistance_warning['has_previous_treatment']:
        recommendation = adjust_regimen_for_resistance(recommendation, resistance_warning)
    
    # Check availability
    availability = check_medicine_availability(patient.hospital_id, recommendation['medicines'])
    
    # Check if all medicines are available
    all_available = all(avail.get('available', False) for avail in availability.values())
    
    return {
        'infection_type': infection_type,
        'regimen': recommendation['regimen'],
        'medicines': recommendation['medicines'],
        'availability': availability,
        'all_available': all_available,
        'risk_score': patient.risk_score,
        'recommendation': 'Prescribe' if all_available else 'Order medicines first',
        'resistance_warning': resistance_warning
    }

def check_previous_resistance(patient_id):
    """
    Check patient's previous prescriptions for resistance patterns.
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Dictionary with resistance warning information
    """
    from models.models import Prescription
    
    previous_prescriptions = Prescription.query.filter_by(
        patient_id=patient_id
    ).order_by(Prescription.created_at.desc()).limit(5).all()
    
    if not previous_prescriptions:
        return {
            'has_previous_treatment': False,
            'previous_medications': [],
            'resistance_detected': False,
            'resistant_drugs': []
        }
    
    previous_medications = []
    resistant_drugs = []
    
    for presc in previous_prescriptions:
        if presc.medication:
            previous_medications.append(presc.medication)
    
    # Check patient's current resistance status
    patient = Patient.query.get(patient_id)
    if patient and patient.drug_resistance:
        resistance_text = patient.drug_resistance.lower()
        
        # Map resistance patterns to specific drugs
        resistance_map = {
            'isoniazid': ['Isoniazid', 'H'],
            'rifampicin': ['Rifampicin', 'R'],
            'pyrazinamide': ['Pyrazinamide', 'Z'],
            'ethambutol': ['Ethambutol', 'E']
        }
        
        for drug, abbreviations in resistance_map.items():
            if drug in resistance_text or any(abbr in resistance_text for abbr in abbreviations):
                resistant_drugs.extend([drug] + abbreviations)
    
    return {
        'has_previous_treatment': True,
        'previous_medications': list(set(previous_medications)),
        'resistance_detected': len(resistant_drugs) > 0,
        'resistant_drugs': list(set(resistant_drugs))
    }

def adjust_regimen_for_resistance(recommendation, resistance_warning):
    """
    Adjust recommended regimen based on detected resistance.
    
    Args:
        recommendation: Current recommendation dictionary
        resistance_warning: Resistance warning from check_previous_resistance
    
    Returns:
        Adjusted recommendation dictionary
    """
    if not resistance_warning['resistance_detected']:
        return recommendation
    
    resistant_drugs = resistance_warning['resistant_drugs']
    current_medicines = recommendation['medicines']
    
    # Remove resistant drugs from the regimen
    adjusted_medicines = []
    for med in current_medicines:
        med_lower = med.lower()
        is_resistant = False
        
        for resistant in resistant_drugs:
            if resistant.lower() in med_lower or med_lower in resistant.lower():
                is_resistant = True
                break
        
        if not is_resistant:
            adjusted_medicines.append(med)
    
    # If too many drugs removed, switch to MDR regimen
    if len(adjusted_medicines) < 2:
        mdr_regimen = TB_REGIMENS['mdr_tb']
        all_medicines = []
        if 'phase1' in mdr_regimen:
            all_medicines.extend(mdr_regimen['phase1']['medicines'])
        if 'phase2' in mdr_regimen:
            all_medicines.extend(mdr_regimen['phase2']['medicines'])
        
        return {
            'regimen': mdr_regimen,
            'medicines': list(set(all_medicines)),
            'regimen_key': 'mdr_tb',
            'adjusted_for_resistance': True,
            'reason': 'Resistance detected, switched to MDR regimen'
        }
    
    return {
        'regimen': recommendation['regimen'],
        'medicines': adjusted_medicines,
        'regimen_key': recommendation['regimen_key'],
        'adjusted_for_resistance': True,
        'removed_drugs': list(set(current_medicines) - set(adjusted_medicines))
    }

def get_medicine_by_name(medicine_name):
    """
    Get ATC drug by name (case-insensitive partial match).
    """
    return ATCDrug.query.filter(ATCDrug.drug_name.ilike(f'%{medicine_name}%')).first()

def get_tb_medicine_ids():
    """
    Get IDs of all TB medicines in the database.
    """
    tb_drug_names = ['Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol']
    drug_ids = []
    
    for name in tb_drug_names:
        drug = get_medicine_by_name(name)
        if drug:
            drug_ids.append(drug.id)
    
    return drug_ids

def get_who_regimen_summary():
    """
    Get summary of all WHO TB regimens for reference.
    """
    return {
        'regimens': TB_REGIMENS,
        'infection_map': INFECTION_REGIMEN_MAP,
        'description': 'WHO TB Treatment Guidelines'
    }
