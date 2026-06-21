import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from dotenv import load_dotenv
from models.models import db, User, Patient, Diagnosis, Treatment, Alert
from models.train_model import preprocess_symptoms, get_patient_features, train_models_from_database
from utils.security import encrypt_data, decrypt_data, hash_password, verify_password

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration - supports multiple databases
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')

if DATABASE_TYPE == 'mysql':
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'tb_diagnostic')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
elif DATABASE_TYPE == 'postgresql':
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', 5432)
    DB_NAME = os.getenv('DB_NAME', 'tb_diagnostic')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tb_data.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tb-diagnostic-super-secret-key-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@tbdiagnostic.com')

mail = Mail(app)

tb_status_model = None
tb_status_label_encoder = None
drug_resistance_model = None
drug_resistance_label_encoder = None

def load_models():
    global tb_status_model, tb_status_label_encoder, drug_resistance_model, drug_resistance_label_encoder
    try:
        tb_model_path = os.path.join(os.path.dirname(__file__), "models", "tb_status_model.pkl")
        tb_le_path = os.path.join(os.path.dirname(__file__), "models", "tb_status_label_encoder.pkl")
        if os.path.exists(tb_model_path) and os.path.exists(tb_le_path):
            tb_status_model = joblib.load(tb_model_path)
            tb_status_label_encoder = joblib.load(tb_le_path)
        else:
            tb_status_model = None
            tb_status_label_encoder = None
    except Exception:
        tb_status_model = None
        tb_status_label_encoder = None

    try:
        dr_model_path = os.path.join(os.path.dirname(__file__), "models", "drug_resistance_model.pkl")
        dr_le_path = os.path.join(os.path.dirname(__file__), "models", "drug_resistance_label_encoder.pkl")
        if os.path.exists(dr_model_path) and os.path.exists(dr_le_path):
            drug_resistance_model = joblib.load(dr_model_path)
            drug_resistance_label_encoder = joblib.load(dr_le_path)
        else:
            drug_resistance_model = None
            drug_resistance_label_encoder = None
    except Exception:
        drug_resistance_model = None
        drug_resistance_label_encoder = None

load_models()

# Role-based access decorator
def get_current_user_from_jwt():
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id)


def role_required(*allowed_roles):
    def decorator(f):
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user = get_current_user_from_jwt()
            
            if not user or user.role not in allowed_roles:
                return jsonify({"msg": "Access denied"}), 403
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# ----------------------
# INTERNATIONAL WHO CLINICAL STANDARDS
# ----------------------

def analyze_who_symptoms(symptoms):
    """Analyze symptoms according to WHO international standards"""
    symptoms_lower = symptoms.lower() if symptoms else ""

    symptoms_present = {
        'persistent_cough_2_weeks': 'cough' in symptoms_lower and ('2 week' in symptoms_lower or 'two week' in symptoms_lower or '2w' in symptoms_lower or '3 week' in symptoms_lower or 'three week' in symptoms_lower or '3w' in symptoms_lower),
        'cough': 'cough' in symptoms_lower,
        'hemoptysis': 'blood' in symptoms_lower or 'hemoptysis' in symptoms_lower,
        'fever': 'fever' in symptoms_lower,
        'night_sweats': 'night' in symptoms_lower or 'sweat' in symptoms_lower, 
        'weight_loss': 'weight' in symptoms_lower or 'loss' in symptoms_lower,  
        'chest_pain': 'chest' in symptoms_lower and 'pain' in symptoms_lower,   
        'fatigue': 'fatigue' in symptoms_lower or 'tired' in symptoms_lower,    
        'dyspnea': 'shortness' in symptoms_lower or 'breath' in symptoms_lower or 'dyspnea' in symptoms_lower,
        'back_pain': 'back pain' in symptoms_lower,
        'joint_swelling': 'joint' in symptoms_lower and 'swell' in symptoms_lower,
        'lymph_node_swelling': 'neck' in symptoms_lower or 'lump' in symptoms_lower or 'lymph' in symptoms_lower,
        'difficulty_walking': 'walking' in symptoms_lower and ('difficult' in symptoms_lower or 'hard' in symptoms_lower),
        'headache_severe': 'severe headache' in symptoms_lower,
        'neck_stiffness': 'neck' in symptoms_lower and 'stiff' in symptoms_lower,
        'confusion': 'confusion' in symptoms_lower,
        'vomiting': 'vomit' in symptoms_lower,
        'painful_urination': 'painful urination' in symptoms_lower or 'pain when urinating' in symptoms_lower,
        'blood_in_urine': 'blood urine' in symptoms_lower or 'hematuria' in symptoms_lower,
        'pelvic_pain': 'pelvic' in symptoms_lower and 'pain' in symptoms_lower,
        'abdominal_pain': 'abdominal pain' in symptoms_lower,
        'diarrhea': 'diarrhea' in symptoms_lower
    }

    return symptoms_present

def is_presumptive_tb(symptoms):
    """Check if patient is a presumptive TB case according to WHO"""
    symptoms_present = analyze_who_symptoms(symptoms)
    
    presumptive = False
    reasons = []
    
    if symptoms_present['persistent_cough_2_weeks']:
        presumptive = True
        reasons.append('Cough lasting 2 weeks or more')
    if symptoms_present['hemoptysis']:
        presumptive = True
        reasons.append('Hemoptysis (coughing blood)')
    if symptoms_present['fever']:
        presumptive = True
        reasons.append('Fever')
    if symptoms_present['night_sweats']:
        presumptive = True
        reasons.append('Night sweats')
    if symptoms_present['weight_loss']:
        presumptive = True
        reasons.append('Unexplained weight loss')
    if symptoms_present['chest_pain']:
        presumptive = True
        reasons.append('Chest pain')
        
    return {
        'is_presumptive': presumptive,
        'reasons': reasons
    }

def has_bacteriological_confirmation(sputum, genexpert, tb_culture=None):
    """Check for bacteriologically confirmed TB according to WHO"""
    confirmed = False
    evidence = []
    
    if genexpert == 'Positive':
        confirmed = True
        evidence.append('GeneXpert MTB/RIF positive (TB bacteria detected)')
    if sputum == 'Positive':
        confirmed = True
        evidence.append('Sputum smear microscopy positive (acid-fast bacilli detected)')
    if tb_culture == 'Positive':
        confirmed = True
        evidence.append('TB culture positive (Mycobacterium tuberculosis grown)')
        
    return {
        'bacteriologically_confirmed': confirmed,
        'evidence': evidence
    }

def identify_tb_type_who(symptoms, sputum, genexpert, chest_xray, hiv, drug_resistant, tb_culture=None, tst=None, igra=None):
    """
    Identify TB type according to full WHO international clinical standards
    Classifies into:
    - No TB
    - Latent TB (LTBI)
    - Pulmonary TB (PTB)
    - Extrapulmonary TB (EPTB)
    - Miliary TB
    - RR-TB (Rifampicin-resistant)
    - MDR-TB (Multidrug-resistant)
    - XDR-TB (Extensively drug-resistant)
    """
    symptoms_present = analyze_who_symptoms(symptoms)
    tb_types = []
    details = []

    # Check for Presumptive TB
    presumptive = is_presumptive_tb(symptoms)
    if presumptive['is_presumptive']:
        details.append(f"Presumptive TB: {', '.join(presumptive['reasons'])}")

    # Bacteriological confirmation
    bacteriological = has_bacteriological_confirmation(sputum, genexpert, tb_culture)
    if bacteriological['bacteriologically_confirmed']:
        details.append(f"Bacteriologically confirmed: {', '.join(bacteriological['evidence'])}")

    # --- Pulmonary TB (PTB) ---
    ptb_signs = symptoms_present['persistent_cough_2_weeks'] or symptoms_present['cough']
    ptb_xray_abnormal = chest_xray == 'Abnormal'
    
    if bacteriological['bacteriologically_confirmed'] and (ptb_signs or ptb_xray_abnormal):
        tb_types.append('CONFIRMED PULMONARY TB (PTB)')
    elif presumptive['is_presumptive'] and ptb_xray_abnormal:
        tb_types.append('CLINICALLY DIAGNOSED PULMONARY TB (PTB)')
    elif presumptive['is_presumptive']:
        tb_types.append('PRESUMPTIVE PULMONARY TB (PTB)')

    # --- Extrapulmonary TB (EPTB) Types ---
    has_ptb = any('PULMONARY' in t for t in tb_types)
    
    # Lymph Node TB
    if symptoms_present['lymph_node_swelling'] and not has_ptb:
        if genexpert == 'Positive' or tb_culture == 'Positive':
            tb_types.append('CONFIRMED LYMPH NODE TB (EPTB)')
        else:
            tb_types.append('SUSPECTED LYMPH NODE TB (EPTB)')
            
    # Bone & Joint TB
    if symptoms_present['back_pain'] or symptoms_present['joint_swelling'] or symptoms_present['difficulty_walking']:
        if genexpert == 'Positive' or tb_culture == 'Positive':
            tb_types.append('CONFIRMED BONE/JOINT TB (EPTB, including Pott\'s disease)')
        else:
            tb_types.append('SUSPECTED BONE/JOINT TB (EPTB)')
            
    # TB Meningitis
    if symptoms_present['headache_severe'] or symptoms_present['neck_stiffness'] or symptoms_present['confusion'] or symptoms_present['vomiting']:
        if genexpert == 'Positive' or tb_culture == 'Positive':
            tb_types.append('CONFIRMED TB MENINGITIS (EPTB - LIFE THREATENING)')
        else:
            tb_types.append('SUSPECTED TB MENINGITIS (EPTB - URGENT)')
            
    # Genitourinary TB
    if symptoms_present['painful_urination'] or symptoms_present['blood_in_urine'] or symptoms_present['pelvic_pain']:
        if genexpert == 'Positive' or tb_culture == 'Positive':
            tb_types.append('CONFIRMED GENITOURINARY TB (EPTB)')
        else:
            tb_types.append('SUSPECTED GENITOURINARY TB (EPTB)')
            
    # Abdominal TB
    if symptoms_present['abdominal_pain'] or symptoms_present['diarrhea'] or symptoms_present['weight_loss']:
        if genexpert == 'Positive' or tb_culture == 'Positive':
            tb_types.append('CONFIRMED ABDOMINAL TB (EPTB)')
        else:
            tb_types.append('SUSPECTED ABDOMINAL TB (EPTB)')
            
    # Pleural TB
    if symptoms_present['chest_pain'] and symptoms_present['dyspnea']:
        if genexpert == 'Positive' or tb_culture == 'Positive':
            tb_types.append('CONFIRMED PLEURAL TB (EPTB)')
        else:
            tb_types.append('SUSPECTED PLEURAL TB (EPTB)')

    # --- Miliary TB ---
    miliary_signs = symptoms_present['fever'] or symptoms_present['fatigue'] or (sum([symptoms_present['dyspnea'], symptoms_present['weight_loss']]) >= 2)
    if miliary_signs and (chest_xray == 'Abnormal' or bacteriological['bacteriologically_confirmed']):
        tb_types.append('CONFIRMED/SUSPECTED MILIARY TB (DISSEMINATED - LIFE THREATENING)')

    # --- Latent TB (LTBI) ---
    if (tst == 'Positive' or igra == 'Positive') and not presumptive['is_presumptive'] and not bacteriological['bacteriologically_confirmed']:
        tb_types.append('LATENT TB INFECTION (LTBI) - NO ACTIVE DISEASE')
        
    # --- TB/HIV Co-infection ---
    if hiv == 'Yes' and (presumptive['is_presumptive'] or bacteriological['bacteriologically_confirmed'] or any('TB' in t for t in tb_types)):
        tb_types.append('TB/HIV CO-INFECTION')
        
    # --- Drug Resistance ---
    if drug_resistant == 'Yes' or genexpert == 'Rifampicin-resistant':
        tb_types.append('RIFAMPICIN-RESISTANT TB (RR-TB)')
        
        # Check for MDR-TB
        if drug_resistant == 'Isoniazid and Rifampicin' or genexpert == 'Multidrug-resistant':
            tb_types.append('MULTIDRUG-RESISTANT TB (MDR-TB)')
            
            # Check for XDR-TB
            if drug_resistant == 'Extensively drug-resistant':
                tb_types.append('EXTENSIVELY DRUG-RESISTANT TB (XDR-TB)')
    elif bacteriological['bacteriologically_confirmed']:
        tb_types.append('DRUG-SENSITIVE TB (DS-TB)')

    # --- Final Classification ---
    if len(tb_types) == 0:
        if tst == 'Positive' or igra == 'Positive':
            tb_types.append('LATENT TB INFECTION (LTBI)')
        elif presumptive['is_presumptive']:
            tb_types.append('PRESUMPTIVE TB CASE - FURTHER TESTING REQUIRED')
        else:
            tb_types.append('NO EVIDENCE OF TB')

    return {
        'tb_types': tb_types,
        'symptoms_present': symptoms_present,
        'presumptive_tb': presumptive,
        'bacteriological_confirmation': bacteriological,
        'details': details,
        'who_category': tb_types[0] if tb_types else 'NO EVIDENCE OF TB'
    }

def get_who_clinical_info(tb_type, symptoms, sputum, genexpert, chest_xray, hiv, drug_resistant):
    """Get comprehensive WHO clinical information about the TB type"""
    info = {}
    tb_type_lower = tb_type.lower()

    # --- Pulmonary TB ---
    if 'pulmonary' in tb_type_lower:
        info['diagnosis'] = 'Pulmonary TB (PTB)'
        info['description'] = 'TB infection affecting the lungs - the most common and contagious form of TB'
        info['symptoms'] = 'Cough lasting ≥2 weeks, hemoptysis, fever, night sweats, weight loss, chest pain'
        info['who_recommendation'] = 'Initiate treatment promptly according to national guidelines; ensure airborne precautions'
        info['infection_control'] = 'Airborne precautions, patient isolation, respiratory hygiene'
        info['test_required'] = 'Sputum smear, GeneXpert, chest X-ray, TB culture (if available)'
        
    # --- Extrapulmonary TB ---
    elif 'lymph node' in tb_type_lower:
        info['diagnosis'] = 'Lymph Node TB (EPTB)'
        info['description'] = 'TB infection affecting the lymph nodes, most commonly in the neck'
        info['symptoms'] = 'Painless swollen lymph nodes (usually in neck), fever, weight loss'
        info['who_recommendation'] = 'Fine-needle aspiration or biopsy for confirmation; standard EPTB regimen'
        info['infection_control'] = 'Standard precautions'
        
    elif 'bone' in tb_type_lower or 'joint' in tb_type_lower:
        info['diagnosis'] = 'Bone & Joint TB (EPTB, including Pott\'s disease)'
        info['description'] = 'TB infection affecting bones or joints, most commonly the spine'
        info['symptoms'] = 'Back pain, joint swelling, difficulty walking, fever, weight loss'
        info['who_recommendation'] = 'MRI/CT for diagnosis; consider orthopedic consultation; 9-12 month regimen'
        info['infection_control'] = 'Standard precautions'
        
    elif 'meningitis' in tb_type_lower:
        info['diagnosis'] = 'TB Meningitis (EPTB - LIFE THREATENING)'
        info['description'] = 'TB infection of the meninges covering the brain and spinal cord - high mortality'
        info['symptoms'] = 'Severe headache, neck stiffness, confusion, vomiting, fever'
        info['who_recommendation'] = 'URGENT hospitalization; lumbar puncture; 12-month regimen; steroids'
        info['infection_control'] = 'Standard precautions'
        
    elif 'genitourinary' in tb_type_lower:
        info['diagnosis'] = 'Genitourinary TB (EPTB)'
        info['description'] = 'TB infection affecting kidneys, bladder, or reproductive organs'
        info['symptoms'] = 'Painful urination, blood in urine, pelvic pain, infertility'
        info['who_recommendation'] = 'Urine analysis and culture; 6-9 month regimen'
        info['infection_control'] = 'Standard precautions'
        
    elif 'abdominal' in tb_type_lower:
        info['diagnosis'] = 'Abdominal TB (EPTB)'
        info['description'] = 'TB infection affecting intestines, peritoneum, or abdominal organs'
        info['symptoms'] = 'Abdominal pain, diarrhea, weight loss, abdominal swelling'
        info['who_recommendation'] = 'Imaging and biopsy; 6-9 month regimen'
        info['infection_control'] = 'Standard precautions'
        
    elif 'pleural' in tb_type_lower:
        info['diagnosis'] = 'Pleural TB (EPTB)'
        info['description'] = 'TB infection of the pleura (lining around the lungs)'
        info['symptoms'] = 'Chest pain, shortness of breath, pleural effusion'
        info['who_recommendation'] = 'Pleural fluid analysis; 6-month regimen'
        info['infection_control'] = 'Standard precautions'
        
    elif 'extrapulmonary' in tb_type_lower:
        info['diagnosis'] = 'Extrapulmonary TB (EPTB)'
        info['description'] = 'TB infection affecting organs other than the lungs'
        info['symptoms'] = 'Depends on affected organ'
        info['who_recommendation'] = 'Evaluate for specific site of infection, consider surgical consultation'
        info['infection_control'] = 'Standard precautions unless also has PTB'
        
    # --- Miliary TB ---
    elif 'miliary' in tb_type_lower:
        info['diagnosis'] = 'Miliary TB (DISSEMINATED - LIFE THREATENING)'
        info['description'] = 'Severe form where TB spreads through bloodstream to many organs'
        info['symptoms'] = 'High fever, severe weakness, weight loss, breathing difficulties'
        info['who_recommendation'] = 'URGENT hospitalization and treatment; 9-12 month regimen'
        info['infection_control'] = 'Airborne precautions'
        
    # --- TB/HIV Co-infection ---
    elif 'hiv' in tb_type_lower:
        info['diagnosis'] = 'TB/HIV Co-infection'
        info['description'] = 'Dual infection with both TB and HIV - high risk of progression and complications'
        info['symptoms'] = 'Any TB symptoms plus HIV-related symptoms'
        info['who_recommendation'] = 'Initiate ART within 2-8 weeks of starting TB treatment'
        info['infection_control'] = 'Comprehensive care, monitoring for IRIS'
        
    # --- Drug-Resistant TB ---
    elif 'xdr' in tb_type_lower:
        info['diagnosis'] = 'Extensively Drug-Resistant TB (XDR-TB)'
        info['description'] = 'TB resistant to first-line, second-line, and additional drugs'
        info['symptoms'] = 'Same as other TB, but fails to respond to standard treatment'
        info['who_recommendation'] = 'Specialized XDR-TB center; individualized all-oral regimen'
        info['infection_control'] = 'Enhanced airborne precautions'
        
    elif 'mdr' in tb_type_lower:
        info['diagnosis'] = 'Multidrug-Resistant TB (MDR-TB)'
        info['description'] = 'TB resistant to at least Isoniazid and Rifampicin'
        info['symptoms'] = 'Same as other TB, but fails to respond to first-line drugs'
        info['who_recommendation'] = 'Specialized DR-TB center; second-line regimen'
        info['infection_control'] = 'Enhanced airborne precautions'
        
    elif 'rifampicin' in tb_type_lower:
        info['diagnosis'] = 'Rifampicin-Resistant TB (RR-TB)'
        info['description'] = 'TB resistant to Rifampicin - often MDR-TB'
        info['symptoms'] = 'Same as other TB'
        info['who_recommendation'] = 'Further testing for MDR-TB; second-line regimen'
        info['infection_control'] = 'Enhanced airborne precautions'
        
    elif 'drug-resistant' in tb_type_lower:
        info['diagnosis'] = 'Drug-Resistant TB (DR-TB)'
        info['description'] = 'TB strain resistant to first-line anti-TB drugs'
        info['symptoms'] = 'Same as other TB, but fails to respond to standard treatment'
        info['who_recommendation'] = 'Refer to specialized DR-TB center for second-line treatment'
        info['infection_control'] = 'Enhanced airborne precautions'
        
    # --- Drug-Sensitive TB ---
    elif 'drug-sensitive' in tb_type_lower:
        info['diagnosis'] = 'Drug-Sensitive TB (DS-TB)'
        info['description'] = 'TB strain treatable with standard first-line anti-TB drugs'
        info['symptoms'] = 'Depends on site of infection'
        info['who_recommendation'] = 'Start standard first-line regimen (2HRZE/4HR) with DOT'
        info['infection_control'] = 'Standard airborne precautions'
        
    # --- Latent TB ---
    elif 'latent' in tb_type_lower or 'ltbi' in tb_type_lower:
        info['diagnosis'] = 'Latent TB Infection (LTBI)'
        info['description'] = 'TB bacteria are present but inactive; no symptoms and not contagious'
        info['symptoms'] = 'No symptoms'
        info['who_recommendation'] = 'Preventive therapy to prevent progression to active TB'
        info['infection_control'] = 'None - not contagious'
        
    # --- Presumptive ---
    elif 'presumptive' in tb_type_lower:
        info['diagnosis'] = 'Presumptive TB Case'
        info['description'] = 'Has TB symptoms but not yet confirmed by testing'
        info['symptoms'] = 'Any combination of: cough ≥2 weeks, fever, night sweats, weight loss, hemoptysis'
        info['who_recommendation'] = 'Complete diagnostic workup (sputum smear, GeneXpert, chest X-ray)'
        info['infection_control'] = 'Precautions while pending diagnosis'
        
    # --- No TB ---
    else:
        info['diagnosis'] = 'No Evidence of TB'
        info['description'] = 'Clinical picture not suggestive of TB'
        info['symptoms'] = 'No TB-specific symptoms'
        info['who_recommendation'] = 'Monitor symptoms, consider other diagnoses'
        info['infection_control'] = 'None'

    return info

def get_who_treatment_regimen(tb_type, hiv_status, drug_resistant):
    """Get complete WHO-recommended treatment regimens"""
    tb_type_lower = tb_type.lower()
    
    # --- DR-TB and Variants ---
    if 'xdr' in tb_type_lower:
        return {
            'regimen': 'XDR-TB Regimen',
            'duration': '18-24 months total',
            'intensive_phase': '6-8 months',
            'continuation_phase': '12-16 months',
            'drugs': 'Individualized based on DST: Bedaquiline, Linezolid, Clofazimine, Fluoroquinolone, Cycloserine, plus additional agents',
            'notes': 'WHO recommends all-oral XDR-TB regimens; close monitoring for adverse effects',
            'priority': 'CRITICAL - LIFE THREATENING'
        }
    elif 'mdr' in tb_type_lower:
        return {
            'regimen': 'MDR-TB Regimen (Second-line)',
            'duration': '18-24 months total',
            'intensive_phase': '6-8 months with at least 5 drugs',
            'continuation_phase': '12-16 months with at least 4 drugs',
            'drugs': 'Based on DST: Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine + other agents',
            'notes': 'WHO recommends all-oral MDR-TB regimens when possible; Directly Observed Therapy (DOT) mandatory',
            'priority': 'URGENT'
        }
    elif 'rifampicin' in tb_type_lower:
        return {
            'regimen': 'RR-TB Regimen',
            'duration': '18-24 months total',
            'intensive_phase': '6-8 months',
            'continuation_phase': '12-16 months',
            'drugs': 'Based on DST, similar to MDR-TB',
            'notes': 'Rule out MDR-TB with further testing; refer to DR-TB center',
            'priority': 'URGENT'
        }
    elif 'drug-resistant' in tb_type_lower:
        return {
            'regimen': 'Second-line anti-TB drugs',
            'duration': '18-24 months total',
            'intensive_phase': '6-8 months with at least 5 drugs',
            'continuation_phase': '12-16 months with at least 4 drugs',
            'drugs': 'Based on DST: Fluoroquinolone + Injectable + Bedaquiline + Linezolid + Clofazimine + Cycloserine',
            'notes': 'WHO recommends individualized treatment based on DST; use all-oral regimens when possible',
            'priority': 'URGENT'
        }
    # --- TB/HIV ---
    elif 'hiv' in tb_type_lower:
        return {
            'regimen': 'First-line TB treatment + ART',
            'duration': '6 months',
            'intensive_phase': '2 months (HRZE)',
            'continuation_phase': '4 months (HR)',
            'drugs': 'Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); ART within 2-8 weeks',
            'notes': 'EFV-based ART; Pyridoxine 25-50mg/day to prevent neuropathy; monitor for Immune Reconstitution Inflammatory Syndrome (IRIS)',
            'priority': 'HIGH'
        }
    # --- Miliary TB ---
    elif 'miliary' in tb_type_lower:
        return {
            'regimen': 'Standard First-line + Steroids',
            'duration': '9-12 months total',
            'intensive_phase': '2-3 months (HRZE)',
            'continuation_phase': '7-9 months (HR)',
            'drugs': 'Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); consider adjunctive steroids',
            'notes': 'Hospitalization required; monitor closely for complications; Pyridoxine 25-50mg/day',
            'priority': 'CRITICAL - LIFE THREATENING'
        }
    # --- TB Meningitis ---
    elif 'meningitis' in tb_type_lower:
        return {
            'regimen': 'First-line + Steroids',
            'duration': '12 months total',
            'intensive_phase': '2-3 months (HRZE)',
            'continuation_phase': '9-10 months (HR)',
            'drugs': 'Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); Adjunctive corticosteroids',
            'notes': 'URGENT hospitalization; lumbar puncture; high-dose steroids early; Pyridoxine 50-100mg/day',
            'priority': 'CRITICAL - LIFE THREATENING'
        }
    # --- Bone/Joint TB ---
    elif 'bone' in tb_type_lower or 'joint' in tb_type_lower:
        return {
            'regimen': 'Standard First-line',
            'duration': '9-12 months total',
            'intensive_phase': '2-3 months (HRZE)',
            'continuation_phase': '7-9 months (HR)',
            'drugs': 'Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E)',
            'notes': 'Consider orthopedic consultation; surgical intervention may be needed; Pyridoxine 25-50mg/day',
            'priority': 'HIGH'
        }
    # --- Pulmonary or DS-TB ---
    elif 'pulmonary' in tb_type_lower or 'drug-sensitive' in tb_type_lower: 
        return {
            'regimen': 'WHO Standard First-line Treatment (2HRZE/4HR)',
            'duration': '6 months total',
            'intensive_phase': '2 months (Isoniazid + Rifampicin + Pyrazinamide + Ethambutol)',
            'continuation_phase': '4 months (Isoniazid + Rifampicin)',
            'drugs': 'Isoniazid (H) 5mg/kg/day, Rifampicin (R) 10mg/kg/day, Pyrazinamide (Z) 25mg/kg/day, Ethambutol (E) 15-20mg/kg/day',
            'notes': 'WHO recommends Directly Observed Treatment (DOT) to ensure adherence; Pyridoxine 25-50mg/day to prevent peripheral neuropathy; monitor LFTs monthly',
            'priority': 'HIGH'
        }
    # --- Other EPTB ---
    elif 'extrapulmonary' in tb_type_lower:
        return {
            'regimen': 'Standard First-line Treatment',
            'duration': '6-12 months depending on site',
            'intensive_phase': '2-3 months (HRZE)',
            'continuation_phase': '4-10 months (HR)',
            'drugs': 'Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E)',
            'notes': 'Duration depends on specific site of EPTB (6 months for most, 9-12 for bone/joint/meningitis); Pyridoxine 25-50mg/day',
            'priority': 'HIGH'
        }
    # --- Latent TB ---
    elif 'latent' in tb_type_lower or 'ltbi' in tb_type_lower:
        return {
            'regimen': 'LTBI Preventive Therapy',
            'duration': '3-9 months depending on regimen',
            'intensive_phase': 'N/A',
            'continuation_phase': 'N/A',
            'drugs': 'Options: Isoniazid 300mg/day for 6-9 months; Isoniazid + Rifapentine weekly for 3 months; Rifampicin 600mg/day for 4 months',
            'notes': 'WHO recommends LTBI treatment for people at high risk of progression to active TB; monitor LFTs',
            'priority': 'MODERATE (high-risk individuals only)'
        }
    # --- Observation ---
    else:
        return {
            'regimen': 'OBSERVATION AND FURTHER TESTING',
            'duration': 'N/A',
            'intensive_phase': 'N/A',
            'continuation_phase': 'N/A',
            'drugs': 'No anti-TB treatment unless clinical suspicion remains high',
            'notes': 'Monitor closely, repeat tests as indicated, evaluate for alternative diagnoses',
            'priority': 'MODERATE'
        }

# ----------------------
# Helper Functions
# ----------------------

def send_email(recipient, subject, body):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def create_alert(patient_id, user_id, alert_type, message, severity='medium'):
    alert = Alert(
        patient_id=patient_id,
        user_id=user_id,
        alert_type=alert_type,
        message=message,
        severity=severity,
    )
    db.session.add(alert)
    db.session.commit()

    if user_id:
        user = User.query.get(user_id)
        if user and user.email:
            email_sent = send_email(
                user.email,
                f"TB Diagnostic Alert: {alert_type}",
                f"Patient Alert:\n\n{message}\n\nPlease log in to the system for more details."
            )
            alert.email_sent = email_sent
            db.session.commit()
    return alert

# ----------------------
# API Endpoints - Authentication
# ----------------------

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find user by email (search through encrypted emails)
    user = None
    all_users = User.query.all()
    for u in all_users:
        if u.email == email:
            user = u
            break

    if not user:
        return jsonify({'msg': 'Invalid email or password'}), 401

    if not user.check_password(password):
        return jsonify({'msg': 'Invalid email or password'}), 401

    # Create access token
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'username': user.username,
            'role': user.role
        }
    )
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })

@app.route('/api/auth/register', methods=['POST'])
@role_required('system_admin', 'hospital_admin')
def register_user():
    data = request.get_json()

    # Check if email already exists
    all_users = User.query.all()
    for u in all_users:
        if u.email == data.get('email'):
            return jsonify({'msg': 'User with this email already exists'}), 409

    user = User(
        username=data.get('username'),
        email=data.get('email'),
        role=data.get('role', 'doctor')
    )
    user.set_password(data.get('password'))

    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify(user.to_dict())

# ----------------------
# API Endpoints
# ----------------------

@app.route('/')
def home():
    return jsonify({
        'message': 'TB Diagnostic System API',
        'version': '2.1.0',
        'database': DATABASE_TYPE,
        'standards': 'WHO International Clinical Guidelines for TB',
        'authentication': 'JWT bearer token required for protected API routes',
        'bootstrap_command': 'python bootstrap.py --runserver',
        'bootstrap_behavior': 'Drops the existing database if it exists, recreates it from scratch, imports datasets, seeds users, trains models, and can start the API server',
        'protected_endpoints': [
            '/api/auth/me',
            '/api/patients',
            '/api/diagnose',
            '/api/diagnoses',
            '/api/alerts'
        ]
    })


@app.route('/api/health')
def health():
    with app.app_context():
        return jsonify({
            'status': 'ok',
            'database': DATABASE_TYPE,
            'patients': Patient.query.count(),
            'users': User.query.count(),
            'models_loaded': {
                'tb_status_model': tb_status_model is not None,
                'drug_resistance_model': drug_resistance_model is not None
            }
        })

# Patient Management
@app.route('/api/patients', methods=['GET', 'POST'])
@jwt_required()
def patients():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        sort = request.args.get('sort', 'created_desc')

        query = Patient.query
        if search:
            query = query.filter(
                (Patient.first_name.ilike(f'%{search}%')) |
                (Patient.last_name.ilike(f'%{search}%')) |
                (Patient.patient_id.ilike(f'%{search}%'))
            )

        sort_mapping = {
            'id_asc': Patient.id.asc(),
            'id_desc': Patient.id.desc(),
            'created_asc': Patient.created_at.asc(),
            'created_desc': Patient.created_at.desc(),
        }
        order_clause = sort_mapping.get(sort, Patient.created_at.desc())

        pagination = query.order_by(order_clause).paginate(page=page, per_page=per_page, error_out=False)
        patients_list = [patient.to_dict() for patient in pagination.items]
        
        return jsonify({
            'patients': patients_list,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'sort': sort
        })

    if request.method == 'POST':
        data = request.get_json()
        patient = Patient(
            patient_id=data.get('patient_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            gender=data.get('gender'),
            city=data.get('city'),
            symptoms=data.get('symptoms'),
            sputum_smear_test=data.get('sputum_smear_test'),
            genexpert_test=data.get('genexpert_test'),
            chest_xray=data.get('chest_xray'),
            drug_resistance=data.get('drug_resistance'),
            hiv=data.get('hiv'),
            diabetes=data.get('diabetes')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201

@app.route('/api/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])  
@jwt_required()
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'GET':
        return jsonify({
            'patient': patient.to_dict(),
            'diagnoses': [d.to_dict() for d in patient.diagnoses],
            'treatments': [t.to_dict() for t in patient.treatments],
            'alerts': [a.to_dict() for a in patient.alerts]
        })

    if request.method == 'PUT':
        data = request.get_json()
        for key, value in data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        db.session.commit()
        return jsonify(patient.to_dict())

    if request.method == 'DELETE':
        user = get_current_user_from_jwt()
        if user.role not in ['system_admin', 'hospital_admin']:
            return jsonify({'msg': 'Access denied'}), 403

        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted successfully'})

# Comprehensive Diagnosis with WHO Standards
@app.route('/api/diagnose', methods=['POST'])
@jwt_required()
def diagnose():
    data = request.get_json() or {}
    patient_data = data.get('patient', {}) or {}
    user = get_current_user_from_jwt()

    def normalize_value(v):
        if v is None:
            return None
        if isinstance(v, str):
            vv = v.strip()
            return vv if vv != "" else None
        return v

    def upsert_patient(payload):
        pid = normalize_value(payload.get("patient_id"))
        if not pid:
            pid = f"AUTO_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        patient = Patient.query.filter_by(patient_id=pid).first()
        if not patient:
            patient = Patient(patient_id=pid)
            db.session.add(patient)

        for field in [
            "first_name",
            "last_name",
            "age",
            "gender",
            "city",
            "symptoms",
            "sputum_smear_test",
            "genexpert_test",
            "chest_xray",
            "drug_resistance",
            "hiv",
            "diabetes",
        ]:
            if field in payload:
                setattr(patient, field, payload.get(field))

        db.session.commit()
        return patient

    patient = upsert_patient(patient_data)
    patient_name = f"{patient.first_name or 'Patient'} {patient.last_name or ''}".strip()

    def compute_symptom_analysis(symptoms_text):
        symptoms_present = analyze_who_symptoms(symptoms_text or "")
        weights = {
            "persistent_cough_2_weeks": 3,
            "hemoptysis": 4,
            "fever": 2,
            "night_sweats": 2,
            "weight_loss": 2,
            "chest_pain": 1,
            "fatigue": 1,
            "dyspnea": 1,
        }
        score = 0
        for k, w in weights.items():
            if symptoms_present.get(k):
                score += w

        if score >= 7:
            risk_level = "HIGH RISK"
        elif score >= 4:
            risk_level = "MODERATE RISK"
        elif score >= 1:
            risk_level = "LOW RISK"
        else:
            risk_level = "MINIMAL RISK"

        red_flags = []
        if symptoms_present.get("hemoptysis"):
            red_flags.append("Hemoptysis (coughing blood) - urgent assessment")
        if symptoms_present.get("neck_stiffness") or symptoms_present.get("confusion") or symptoms_present.get("headache_severe"):
            red_flags.append("Possible CNS involvement (meningitis symptoms) - urgent referral")
        if symptoms_present.get("dyspnea"):
            red_flags.append("Breathlessness - assess severity and oxygenation")

        clinical_advice = "Complete TB diagnostic workup and follow national/WHO guidance."
        if risk_level == "HIGH RISK":
            clinical_advice = "Urgent evaluation: isolate if infectious risk, order GeneXpert/sputum, and consider starting treatment per guidelines."
        elif risk_level == "MODERATE RISK":
            clinical_advice = "Prioritize TB testing (GeneXpert/sputum) and chest imaging; review comorbidities."
        elif risk_level == "LOW RISK":
            clinical_advice = "TB less likely but possible; consider targeted testing if symptoms persist or risk factors present."

        return {
            "risk_level": risk_level,
            "risk_score": score,
            "red_flags": red_flags,
            "clinical_advice": clinical_advice,
        }

    def evaluate_tests(sputum, genexpert, chest_xray):
        sputum = sputum or "Unknown"
        genexpert = genexpert or "Unknown"
        chest_xray = chest_xray or "Unknown"

        findings = []
        confidence = 40
        classification = "Insufficient evidence"

        if genexpert == "Positive":
            findings.append("GeneXpert MTB/RIF: Positive")
            classification = "Bacteriologically confirmed TB likely"
            confidence = 95
        if sputum == "Positive":
            findings.append("Sputum smear microscopy: Positive")
            classification = "Bacteriologically confirmed TB likely"
            confidence = max(confidence, 85)
        if chest_xray == "Abnormal":
            findings.append("Chest X-ray: Abnormal")
            confidence = max(confidence, 60)
        if genexpert == "Negative" and sputum == "Negative" and chest_xray == "Normal":
            findings.append("GeneXpert/Sputum negative and X-ray normal")
            classification = "TB less likely (but not excluded)"
            confidence = 70

        return {
            "classification": classification,
            "confidence_percent": confidence,
            "findings": findings,
        }

    def predict_ml(patient_obj):
        features = get_patient_features(patient_obj)
        x_df = pd.DataFrame([features])
        predictions = {}

        if tb_status_model and tb_status_label_encoder:
            proba = tb_status_model.predict_proba(x_df)[0]
            classes = list(tb_status_label_encoder.classes_)
            pred_idx = int(np.argmax(proba))
            predictions["tb_status"] = {
                "prediction": classes[pred_idx],
                "confidence": float(proba[pred_idx]),
                "probabilities": {classes[i]: float(proba[i]) for i in range(len(classes))},
            }

        if drug_resistance_model and drug_resistance_label_encoder:
            proba = drug_resistance_model.predict_proba(x_df)[0]
            classes = list(drug_resistance_label_encoder.classes_)
            pred_idx = int(np.argmax(proba))
            predictions["drug_resistance"] = {
                "prediction": classes[pred_idx],
                "confidence": float(proba[pred_idx]),
                "probabilities": {classes[i]: float(proba[i]) for i in range(len(classes))},
            }

        return predictions if predictions else None

    # WHO Clinical Analysis
    tb_analysis = identify_tb_type_who(
        patient.symptoms or '',
        patient.sputum_smear_test or 'Unknown',
        patient.genexpert_test or 'Unknown',
        patient.chest_xray or 'Unknown',
        patient.hiv or 'No',
        patient.drug_resistance or 'No',
        patient_data.get('tb_culture', None),
        patient_data.get('tst', None),
        patient_data.get('igra', None)
    )

    # Get WHO clinical info
    clinical_info = get_who_clinical_info(
        tb_analysis['who_category'],
        patient.symptoms or '',
        patient.sputum_smear_test or 'Unknown',
        patient.genexpert_test or 'Unknown',
        patient.chest_xray or 'Unknown',
        patient.hiv or 'No',
        patient.drug_resistance or 'No'
    )

    # Get WHO Treatment Regimen
    treatment = get_who_treatment_regimen(
        tb_analysis['who_category'],
        patient.hiv or 'No',
        patient.drug_resistance or 'No'
    )

    ml_prediction = predict_ml(patient)

    # Determine if alert should be created
    alert_created = None
    symptom_analysis = compute_symptom_analysis(patient.symptoms or "")
    test_evaluation = evaluate_tests(patient.sputum_smear_test, patient.genexpert_test, patient.chest_xray)

    diagnosis_record = Diagnosis(
        patient_id=patient.id,
        clinician_id=user.id,
        diagnosis_type=tb_analysis['who_category'],
        details=json.dumps({
            'tb_types': tb_analysis['tb_types'],
            'symptoms_present': tb_analysis['symptoms_present'],
            'presumptive_tb': tb_analysis['presumptive_tb'],
            'bacteriological_confirmation': tb_analysis['bacteriological_confirmation'],
            'clinical_info': clinical_info,
            'treatment_regimen': treatment,
            'symptom_analysis': symptom_analysis,
            'test_evaluation': test_evaluation,
            'ml_prediction': ml_prediction
        }),
        ml_prediction=json.dumps(ml_prediction) if ml_prediction else None,
        status='completed'
    )
    db.session.add(diagnosis_record)
    db.session.flush()

    treatment_record = Treatment(
        patient_id=patient.id,
        diagnosis_id=diagnosis_record.id,
        treatment_type=tb_analysis['who_category'],
        drugs=treatment.get('drugs'),
        duration=treatment.get('duration'),
        dosage=f"Intensive: {treatment.get('intensive_phase')}, Continuation: {treatment.get('continuation_phase')}",
        administration_notes=treatment.get('notes')
    )
    db.session.add(treatment_record)

    urgency = treatment.get("priority", "MODERATE")
    treatment_recommendation = {
        "type": clinical_info.get("diagnosis", tb_analysis["who_category"]),
        "category": tb_analysis["who_category"],
        "duration": treatment.get("duration"),
        "drugs": treatment.get("drugs"),
        "dosage": treatment_record.dosage,
        "administration": treatment.get("notes"),
        "monitoring": clinical_info.get("who_recommendation"),
        "urgency": urgency,
        "notes": clinical_info.get("infection_control"),
    }

    if 'CONFIRMED' in tb_analysis['who_category'] or 'URGENT' in urgency or 'CRITICAL' in urgency:
        alert_created = create_alert(
            patient_id=patient.id,
            user_id=user.id,
            alert_type=f"ALERT: {tb_analysis['who_category']}",
            message=f"Patient {patient_name} (ID: {patient.patient_id}) classified as {tb_analysis['who_category']}. {clinical_info.get('who_recommendation','')}",
            severity='high'
        )

    db.session.commit()

    return jsonify({
        "patient_name": patient_name,
        "patient_id": patient.patient_id,
        "symptom_analysis": symptom_analysis,
        "test_evaluation": test_evaluation,
        "who_standards": {
            "tb_types": tb_analysis["tb_types"],
            "primary_diagnosis": tb_analysis["who_category"],
            "presumptive": tb_analysis["presumptive_tb"],
            "bacteriological_confirmation": tb_analysis["bacteriological_confirmation"],
            "clinical_info": clinical_info,
        },
        "ml_prediction": ml_prediction,
        "treatment_recommendation": treatment_recommendation,
        "saved_diagnosis": diagnosis_record.to_dict(),
        "saved_treatment": treatment_record.to_dict(),
        "alert_created": alert_created.id if alert_created else None,
    })

@app.route('/api/diagnoses', methods=['GET'])
@jwt_required()
def get_diagnoses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Diagnosis.query.order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    diagnoses = [d.to_dict() for d in pagination.items]
    return jsonify({'diagnoses': diagnoses, 'total': pagination.total})

@app.route('/api/treatments', methods=['GET'])
@jwt_required()
def get_treatments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Treatment.query.order_by(Treatment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    treatments = [t.to_dict() for t in pagination.items]
    return jsonify({'treatments': treatments, 'total': pagination.total})       

@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'    

    query = Alert.query
    if unread_only:
        query = query.filter_by(is_read=False)

    pagination = query.order_by(Alert.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    alerts = [a.to_dict() for a in pagination.items]
    return jsonify({
        'alerts': alerts,
        'total': pagination.total,
        'unread_count': Alert.query.filter_by(is_read=False).count()
    })

@app.route('/api/alerts/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_alert_read(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify(alert.to_dict())

@app.route('/api/train-model', methods=['POST'])
@role_required('system_admin')
def train_model_endpoint():
    try:
        result = train_models_from_database()
        load_models()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-data', methods=['POST'])
@role_required('system_admin')
def import_data_endpoint():
    try:
        from import_data import main
        main()
        return jsonify({'message': 'Data import completed successfully'})       
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
