import os
import json
import subprocess
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def _use_project_venv_when_available():
    current_prefix = os.path.abspath(sys.prefix)
    base_prefix = os.path.abspath(getattr(sys, "base_prefix", sys.prefix))
    running_inside_venv = current_prefix != base_prefix
    if running_inside_venv:
        return

    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        return

    current_python = os.path.normcase(os.path.abspath(sys.executable))
    target_python = os.path.normcase(os.path.abspath(venv_python))
    if current_python == target_python:
        return

    env = os.environ.copy()
    env["TB_BACKEND_AUTO_VENV"] = "1"
    completed = subprocess.run(
        [target_python, os.path.abspath(__file__), *sys.argv[1:]],
        env=env,
        check=False,
    )
    raise SystemExit(completed.returncode)


_use_project_venv_when_available()

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

TB_BACTERIA_PROFILES = {
    "Mycobacterium tuberculosis": {
        "description": "The most common cause of human tuberculosis worldwide.",
        "typical_source": "Human-to-human airborne transmission.",
        "lab_note": "Routine TB molecular tests and culture commonly target this species within the MTBC.",
        "treatment_note": "Use standard first-line treatment unless drug resistance is detected.",
    },
    "Mycobacterium bovis": {
        "description": "A zoonotic MTBC species linked to cattle and contaminated dairy products.",
        "typical_source": "Cattle exposure or unpasteurized milk products.",
        "lab_note": "Culture speciation is important when zoonotic exposure is suspected.",
        "treatment_note": "Confirm speciation because M. bovis is typically pyrazinamide resistant; tailor regimen accordingly.",
    },
    "Mycobacterium africanum": {
        "description": "An MTBC member that causes human TB, especially in parts of West Africa.",
        "typical_source": "Human transmission, often with West African epidemiologic linkage.",
        "lab_note": "Reference-lab speciation is useful where M. africanum is endemic.",
        "treatment_note": "Treat similarly to drug-sensitive TB unless resistance testing indicates otherwise.",
    },
    "Mycobacterium canettii": {
        "description": "A rare smooth-colony MTBC member reported mainly in the Horn of Africa.",
        "typical_source": "Rare human infection with specific geographic clustering.",
        "lab_note": "Requires specialist or reference-laboratory speciation support.",
        "treatment_note": "Seek infectious-disease or TB-specialist input because cases are rare.",
    },
    "Mycobacterium microti": {
        "description": "An uncommon MTBC species more often associated with rodents than humans.",
        "typical_source": "Rodent or wildlife exposure.",
        "lab_note": "Species confirmation often needs specialized molecular testing.",
        "treatment_note": "Manage with specialist input and drug-susceptibility guidance.",
    },
    "Mycobacterium caprae": {
        "description": "An MTBC species usually associated with goats and other livestock.",
        "typical_source": "Goat, sheep, or livestock exposure.",
        "lab_note": "Consider speciation when livestock exposure is prominent.",
        "treatment_note": "Treat as TB but review susceptibilities and zoonotic implications.",
    },
    "Mycobacterium pinnipedii": {
        "description": "A rare MTBC species associated with seals and sea lions.",
        "typical_source": "Marine mammal exposure.",
        "lab_note": "Reference-lab confirmation is recommended.",
        "treatment_note": "Use specialist review because human infection is rare and zoonotic.",
    },
    "Mycobacterium orygis": {
        "description": "An MTBC species reported in both animals and humans, often with zoonotic linkage.",
        "typical_source": "Animal exposure or South Asian epidemiologic linkage.",
        "lab_note": "Speciation generally requires molecular reference testing.",
        "treatment_note": "Treat as TB while confirming species and resistance profile.",
    },
}

BOVIS_LIKE_SPECIES = {"Mycobacterium bovis"}

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


def normalize_bacteria_species(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() in {"auto", "auto-detect", "autodetect", "unknown", "none"}:
        return None

    aliases = {
        "m. tuberculosis": "Mycobacterium tuberculosis",
        "mtb": "Mycobacterium tuberculosis",
        "m. bovis": "Mycobacterium bovis",
        "m. africanum": "Mycobacterium africanum",
        "m. canettii": "Mycobacterium canettii",
        "m. microti": "Mycobacterium microti",
        "m. caprae": "Mycobacterium caprae",
        "m. pinnipedii": "Mycobacterium pinnipedii",
        "m. orygis": "Mycobacterium orygis",
    }
    normalized = aliases.get(cleaned.lower(), cleaned)
    return normalized if normalized in TB_BACTERIA_PROFILES else None


def tokenize_case_text(*values):
    stopwords = {
        "the", "and", "with", "from", "that", "this", "have", "has", "for", "into",
        "patient", "history", "positive", "negative", "unknown", "daily", "oral",
        "weeks", "week", "months", "month", "mild", "severe", "common", "rare",
        "likely", "possible", "tb", "tuberculosis",
    }
    tokens = set()
    for value in values:
        if not value:
            continue
        cleaned = str(value).lower()
        for char in [",", ".", ";", ":", "(", ")", "/", "-", "_"]:
            cleaned = cleaned.replace(char, " ")
        for token in cleaned.split():
            if len(token) >= 3 and token not in stopwords:
                tokens.add(token)
    return tokens


def infer_bacteria_species_from_owner_dataset(exposure_history, region=None, city=None, symptoms=None, sputum_smear=None, genexpert=None, chest_xray=None, tb_culture=None, tst=None, igra=None):
    reference_cases = (
        Patient.query.filter(
            Patient.source_dataset == "owner_tb_species_dataset",
            Patient.bacteria_species.isnot(None),
        )
        .all()
    )
    if not reference_cases:
        return None

    patient_tokens = tokenize_case_text(exposure_history, region, city, symptoms)
    patient_test_values = {
        "sputum_smear_test": str(sputum_smear or "").strip().lower(),
        "genexpert_test": str(genexpert or "").strip().lower(),
        "chest_xray": str(chest_xray or "").strip().lower(),
    }
    patient_positive_tests = {
        "tb_culture": str(tb_culture or "").strip().lower(),
        "tst": str(tst or "").strip().lower(),
        "igra": str(igra or "").strip().lower(),
    }

    species_scores = {}
    species_examples = {}
    species_reasons = {}

    for case in reference_cases:
        score = 0.0
        reason_parts = []
        case_tokens = tokenize_case_text(case.exposure_history, case.region, case.city, case.symptoms)
        overlap = sorted(patient_tokens & case_tokens)
        if overlap:
            overlap_score = min(len(overlap), 5) * 1.5
            score += overlap_score
            reason_parts.append(f"shared context: {', '.join(overlap[:4])}")

        for field, patient_value in patient_test_values.items():
            case_value = str(getattr(case, field, "") or "").strip().lower()
            if patient_value and patient_value != "unknown" and case_value == patient_value:
                score += 2.0
                reason_parts.append(f"{field.replace('_', ' ')} match")

        for field, patient_value in patient_positive_tests.items():
            if patient_value and patient_value != "unknown" and patient_value == "positive":
                score += 1.0
                reason_parts.append(f"{field.replace('_', ' ')} positive")

        if score <= 0:
            continue

        species = case.bacteria_species
        species_scores[species] = species_scores.get(species, 0.0) + score
        species_examples[species] = species_examples.get(species, 0) + 1
        species_reasons.setdefault(species, []).extend(reason_parts[:3])

    if not species_scores:
        return None

    ranked = sorted(species_scores.items(), key=lambda item: item[1], reverse=True)
    top_species, top_score = ranked[0]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0.0
    if top_score < 4.0 or top_score - runner_up_score < 1.5:
        return None

    unique_reasons = []
    for reason in species_reasons.get(top_species, []):
        if reason not in unique_reasons:
            unique_reasons.append(reason)

    return {
        "species": top_species,
        "mode": "dataset-assisted",
        "reason": (
            f"Estimated from curated owner dataset matches using patient symptoms, exposure, geography, and tests. "
            f"Matched {species_examples.get(top_species, 1)} similar case(s); strongest evidence: {', '.join(unique_reasons[:3])}."
        ),
    }


def infer_bacteria_species(explicit_species, exposure_history, region=None, city=None, symptoms=None, sputum_smear=None, genexpert=None, chest_xray=None, tb_culture=None, tst=None, igra=None):
    species = normalize_bacteria_species(explicit_species)
    if species:
        return {
            "species": species,
            "mode": "manual",
            "reason": "Clinician selected a specific TB bacteria species.",
        }

    context = " ".join(
        [
            str(exposure_history or ""),
            str(region or ""),
            str(city or ""),
        ]
    ).lower()

    dataset_result = infer_bacteria_species_from_owner_dataset(
        exposure_history,
        region,
        city,
        symptoms,
        sputum_smear,
        genexpert,
        chest_xray,
        tb_culture,
        tst,
        igra,
    )
    if dataset_result:
        return dataset_result

    inference_rules = [
        ("Mycobacterium bovis", ["cattle", "cow", "bovine", "unpasteurized", "milk", "dairy"]),
        ("Mycobacterium africanum", ["west africa", "ghana", "gambia", "senegal", "nigeria", "sierra leone", "liberia"]),
        ("Mycobacterium canettii", ["horn of africa", "djibouti", "somalia", "eritrea", "ethiopia"]),
        ("Mycobacterium microti", ["rodent", "vole", "mouse", "wild rodent"]),
        ("Mycobacterium caprae", ["goat", "sheep", "caprine", "livestock herd"]),
        ("Mycobacterium pinnipedii", ["seal", "sea lion", "pinniped", "marine mammal"]),
        ("Mycobacterium orygis", ["south asia", "india", "pakistan", "bangladesh", "nepal", "oryx"]),
    ]

    for candidate, keywords in inference_rules:
        if any(keyword in context for keyword in keywords):
            return {
                "species": candidate,
                "mode": "inferred",
                "reason": f"Inferred from exposure or epidemiology clues: {', '.join(keywords[:3])}.",
            }

    return {
        "species": "Mycobacterium tuberculosis",
        "mode": "default",
        "reason": "Defaulted to the most common human TB species because the patient record did not contain enough species-specific evidence.",
    }


def build_bacteria_assessment(species_result, tb_analysis):
    species = species_result["species"]
    profile = TB_BACTERIA_PROFILES.get(species, TB_BACTERIA_PROFILES["Mycobacterium tuberculosis"])
    tb_detected = tb_analysis["who_category"] != "NO EVIDENCE OF TB"

    return {
        "species": species,
        "mode": species_result["mode"],
        "reason": species_result["reason"],
        "description": profile["description"],
        "typical_source": profile["typical_source"],
        "lab_note": profile["lab_note"],
        "treatment_note": profile["treatment_note"],
        "supported_species_count": len(TB_BACTERIA_PROFILES),
        "supported_species": list(TB_BACTERIA_PROFILES.keys()),
        "tb_detected": tb_detected,
    }


def apply_species_treatment_adjustments(treatment, clinical_info, bacteria_assessment):
    adjusted_treatment = dict(treatment)
    adjusted_clinical_info = dict(clinical_info)
    species = bacteria_assessment["species"]
    species_note = bacteria_assessment["treatment_note"]

    adjusted_treatment["species_specific_notes"] = species_note

    if species in BOVIS_LIKE_SPECIES:
        adjusted_treatment["drugs"] = (
            f"{adjusted_treatment.get('drugs')} "
            "If M. bovis is confirmed, review the regimen because pyrazinamide is usually not effective."
        ).strip()
        adjusted_treatment["notes"] = (
            f"{adjusted_treatment.get('notes')} "
            "Confirm M. bovis with a reference laboratory and tailor therapy to susceptibility results."
        ).strip()
        adjusted_clinical_info["who_recommendation"] = (
            f"{adjusted_clinical_info.get('who_recommendation', '')} "
            "Add zoonotic exposure review and confirm pyrazinamide susceptibility assumptions."
        ).strip()
    elif bacteria_assessment["mode"] in {"manual", "inferred"} and species != "Mycobacterium tuberculosis":
        adjusted_treatment["notes"] = (
            f"{adjusted_treatment.get('notes')} "
            "Confirm species at a reference laboratory and review zoonotic/public-health implications."
        ).strip()
        adjusted_clinical_info["who_recommendation"] = (
            f"{adjusted_clinical_info.get('who_recommendation', '')} "
            "Request species confirmation if clinical management depends on the exact MTBC member."
        ).strip()

    return adjusted_treatment, adjusted_clinical_info


def normalize_drug_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        raw_items = value
    else:
        normalized = str(value).replace(";", ",").replace("|", ",")
        raw_items = normalized.split(",")

    cleaned = []
    for item in raw_items:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def determine_resistance_profile(drug_resistant, genexpert, antibiogram_result=None, resistant_to=None, susceptible_to=None):
    resistant_drugs = normalize_drug_list(resistant_to)
    susceptible_drugs = normalize_drug_list(susceptible_to)
    antibiogram_text = str(antibiogram_result or "").strip()
    decision_basis = []
    regimen_level = "first-line"
    classification = "Drug-sensitive TB (DS-TB)"
    resistant_drug_set = {drug.lower() for drug in resistant_drugs}

    combined_text = " ".join(
        [
            str(drug_resistant or ""),
            str(genexpert or ""),
            antibiogram_text,
            ", ".join(resistant_drugs),
        ]
    ).lower()

    if "extensively drug-resistant" in combined_text or "xdr" in combined_text:
        classification = "Extensively Drug-Resistant TB (XDR-TB)"
        regimen_level = "individualized second-line"
        decision_basis.append("Detected XDR-level resistance markers from DST/GeneXpert metadata.")
    elif (
        "multidrug-resistant" in combined_text
        or "mdr" in combined_text
        or {"isoniazid", "rifampicin"}.issubset({drug.lower() for drug in resistant_drugs})
        or str(drug_resistant or "").strip() == "Isoniazid and Rifampicin"
    ):
        classification = "Multidrug-Resistant TB (MDR-TB)"
        regimen_level = "second-line"
        decision_basis.append("Detected rifampicin plus isoniazid resistance pattern.")
    elif resistant_drug_set == {"pyrazinamide"}:
        classification = "Pyrazinamide-resistant pattern"
        regimen_level = "modified first-line"
        decision_basis.append("Only pyrazinamide resistance was provided; review for M. bovis or regimen modification.")
    elif "rifampicin-resistant" in combined_text or "rr-tb" in combined_text or "rifampicin" in {drug.lower() for drug in resistant_drugs}:
        classification = "Rifampicin-Resistant TB (RR-TB)"
        regimen_level = "second-line"
        decision_basis.append("Detected rifampicin resistance signal.")
    elif str(drug_resistant or "").strip().lower() in {"yes", "drug-resistant"} or resistant_drugs:
        classification = "Drug-Resistant TB (DR-TB)"
        regimen_level = "second-line"
        decision_basis.append("Resistance data present but not enough to label RR/MDR/XDR confidently.")
    else:
        decision_basis.append("No resistance markers supplied; managed as drug-sensitive TB unless DST changes the plan.")

    if antibiogram_text:
        decision_basis.append(f"Antibiogram/DST summary: {antibiogram_text}")

    return {
        "classification": classification,
        "regimen_level": regimen_level,
        "antibiogram_result": antibiogram_text or "Not provided",
        "resistant_to": resistant_drugs,
        "susceptible_to": susceptible_drugs,
        "decision_basis": decision_basis,
        "dst_required": classification != "Drug-sensitive TB (DS-TB)",
    }


def build_infection_assessment(tb_analysis):
    infection_types = []
    seen = set()

    infection_rules = [
        ("pulmonary", "Pulmonary TB", "Lungs"),
        ("lymph node", "Lymph Node TB", "Lymph nodes"),
        ("bone/joint", "Bone and Joint TB", "Spine, bones, or joints"),
        ("meningitis", "TB Meningitis", "Central nervous system"),
        ("genitourinary", "Genitourinary TB", "Genitourinary tract"),
        ("abdominal", "Abdominal TB", "Abdomen/peritoneum"),
        ("pleural", "Pleural TB", "Pleura"),
        ("miliary", "Miliary TB", "Disseminated / whole body spread"),
        ("latent", "Latent TB Infection", "No active organ disease"),
        ("hiv", "TB/HIV Co-infection", "Systemic comorbidity"),
    ]

    for tb_type in tb_analysis["tb_types"]:
        lower = tb_type.lower()
        for key, label, site in infection_rules:
            if key in lower and label not in seen:
                infection_types.append(
                    {
                        "label": label,
                        "site": site,
                        "source_classification": tb_type,
                    }
                )
                seen.add(label)

    if not infection_types:
        infection_types.append(
            {
                "label": "No specific TB infection pattern confirmed",
                "site": "Unspecified",
                "source_classification": tb_analysis["who_category"],
            }
        )

    return {
        "primary_infection": infection_types[0]["label"],
        "infection_types": infection_types,
    }


def build_treatment_plan(tb_analysis, bacteria_assessment, resistance_profile, treatment, clinical_info):
    tb_type = tb_analysis["who_category"]
    species = bacteria_assessment["species"]
    resistance_class = resistance_profile["classification"]
    options = []

    def option(name, level, drugs, duration, administration, monitoring, notes):
        return {
            "name": name,
            "level": level,
            "drugs": drugs,
            "duration": duration,
            "administration": administration,
            "monitoring": monitoring,
            "notes": notes,
        }

    if "XDR-TB" in resistance_class:
        options.append(
            option(
                "WHO-aligned XDR-TB individualized regimen",
                "individualized second-line",
                "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + additional active agents guided by DST",
                "18-24 months",
                "Daily supervised treatment under specialist DR-TB care; all-oral regimen preferred.",
                "Monthly clinical review, ECG where indicated, liver tests, neuropathy and hematology monitoring.",
                "Must be individualized from DST/antibiogram and WHO DR-TB guidance.",
            )
        )
    elif "MDR-TB" in resistance_class:
        options.append(
            option(
                "WHO MDR-TB second-line regimen",
                "second-line",
                "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine / other active drugs",
                "18-24 months",
                "Daily supervised treatment, preferably all-oral, with DR-TB specialist oversight.",
                "Frequent DST review, toxicity review, liver/kidney tests, ECG, adherence tracking.",
                "Chosen because rifampicin and isoniazid resistance is present or strongly suspected.",
            )
        )
    elif "RR-TB" in resistance_class or "Drug-Resistant TB" in resistance_class:
        options.append(
            option(
                "WHO RR/DR-TB regimen",
                "second-line",
                "Second-line anti-TB regimen selected from DST-active medicines",
                "18-24 months",
                "Daily supervised treatment under a DR-TB protocol.",
                "Repeat DST, adverse-effect monitoring, adherence checks, and specialist review.",
                "Escalate to MDR/XDR protocol if additional resistance is confirmed.",
            )
        )
    elif species == "Mycobacterium bovis":
        options.append(
            option(
                "M. bovis pyrazinamide-sparing regimen",
                "modified first-line",
                "Isoniazid (H) + Rifampicin (R) + Ethambutol (E)",
                "6-9 months",
                "Daily oral therapy with DOTS strongly recommended.",
                "Review species confirmation, liver tests, response to therapy, and zoonotic exposure control.",
                "Avoid relying on pyrazinamide because M. bovis is usually resistant.",
            )
        )
    elif species == "Mycobacterium microti":
        options.append(
            option(
                "M. microti HR-based regimen",
                "modified first-line",
                "Isoniazid (H) + Rifampicin (R)-based regimen with or without Ethambutol depending on severity",
                "6-9 months",
                "Daily oral therapy, ideally under supervised adherence support.",
                "Confirm species and review response because human disease is uncommon.",
                "Specialist review is advised for rare-species disease.",
            )
        )
    else:
        options.append(
            option(
                treatment.get("regimen", clinical_info.get("diagnosis", tb_type)),
                "first-line",
                treatment.get("drugs"),
                treatment.get("duration"),
                f"Intensive phase: {treatment.get('intensive_phase')}; continuation phase: {treatment.get('continuation_phase')}; daily DOTS/supervised dosing where feasible.",
                clinical_info.get("who_recommendation"),
                treatment.get("notes"),
            )
        )

    if "Latent TB" in tb_type:
        options.extend(
            [
                option(
                    "LTBI 6-9H option",
                    "preventive therapy",
                    "Isoniazid daily",
                    "6-9 months",
                    "Daily oral therapy with adherence follow-up.",
                    "Baseline and interval liver monitoring where indicated.",
                    "Standard WHO preventive option for LTBI.",
                ),
                option(
                    "LTBI 3HP option",
                    "preventive therapy",
                    "Isoniazid + Rifapentine weekly",
                    "3 months",
                    "Weekly directly observed or closely supported therapy.",
                    "Monitor adherence and drug interactions.",
                    "Short-course WHO preventive option.",
                ),
                option(
                    "LTBI 4R option",
                    "preventive therapy",
                    "Rifampicin daily",
                    "4 months",
                    "Daily oral therapy.",
                    "Monitor liver function and interactions.",
                    "Alternative preventive option when appropriate.",
                ),
            ]
        )

    return {
        "selected_option": options[0],
        "options": options,
        "guideline_source": "WHO-aligned TB rule engine with species notes, infection-site classification, and DST-aware regimen escalation.",
        "decision_basis": [
            f"Primary TB classification: {tb_type}",
            f"Bacteria estimate: {species}",
            f"Resistance class: {resistance_class}",
            *resistance_profile["decision_basis"],
        ],
    }

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

def has_bacteriological_confirmation(sputum, genexpert, tb_culture=None, bacteria_species=None):
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
        cultured_species = normalize_bacteria_species(bacteria_species) or 'Mycobacterium tuberculosis complex'
        evidence.append(f'TB culture positive ({cultured_species} grown or suspected)')
        
    return {
        'bacteriologically_confirmed': confirmed,
        'evidence': evidence
    }

def identify_tb_type_who(symptoms, sputum, genexpert, chest_xray, hiv, drug_resistant, tb_culture=None, tst=None, igra=None, bacteria_species=None):
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
    bacteriological = has_bacteriological_confirmation(sputum, genexpert, tb_culture, bacteria_species)
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
            exposure_history=data.get('exposure_history'),
            sputum_smear_test=data.get('sputum_smear_test'),
            genexpert_test=data.get('genexpert_test'),
            chest_xray=data.get('chest_xray'),
            bacteria_species=data.get('bacteria_species'),
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
            "exposure_history",
            "sputum_smear_test",
            "genexpert_test",
            "chest_xray",
            "bacteria_species",
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

    tb_culture = patient_data.get('tb_culture', None)
    tst = patient_data.get('tst', None)
    igra = patient_data.get('igra', None)

    species_result = infer_bacteria_species(
        patient_data.get("bacteria_species", patient.bacteria_species),
        patient_data.get("exposure_history", patient.exposure_history),
        patient.region,
        patient.city,
        patient.symptoms,
        patient.sputum_smear_test,
        patient.genexpert_test,
        patient.chest_xray,
        tb_culture,
        tst,
        igra,
    )

    # WHO Clinical Analysis
    tb_analysis = identify_tb_type_who(
        patient.symptoms or '',
        patient.sputum_smear_test or 'Unknown',
        patient.genexpert_test or 'Unknown',
        patient.chest_xray or 'Unknown',
        patient.hiv or 'No',
        patient.drug_resistance or 'No',
        tb_culture,
        tst,
        igra,
        species_result["species"],
    )
    bacteria_assessment = build_bacteria_assessment(species_result, tb_analysis)
    infection_assessment = build_infection_assessment(tb_analysis)

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
    resistance_profile = determine_resistance_profile(
        patient.drug_resistance or 'No',
        patient.genexpert_test or 'Unknown',
        patient_data.get('antibiogram_result'),
        patient_data.get('resistant_to'),
        patient_data.get('susceptible_to'),
    )
    treatment, clinical_info = apply_species_treatment_adjustments(treatment, clinical_info, bacteria_assessment)
    treatment_plan = build_treatment_plan(tb_analysis, bacteria_assessment, resistance_profile, treatment, clinical_info)

    ml_prediction = predict_ml(patient)

    # Determine if alert should be created
    alert_created = None
    symptom_analysis = compute_symptom_analysis(patient.symptoms or "")
    test_evaluation = evaluate_tests(patient.sputum_smear_test, patient.genexpert_test, patient.chest_xray)
    if tb_culture:
        test_evaluation["findings"].append(f"TB culture: {tb_culture}")
    if tst:
        test_evaluation["findings"].append(f"TST: {tst}")
    if igra:
        test_evaluation["findings"].append(f"IGRA: {igra}")
    if resistance_profile["antibiogram_result"] != "Not provided":
        test_evaluation["findings"].append(f"Antibiogram/DST: {resistance_profile['antibiogram_result']}")

    diagnosis_record = Diagnosis(
        patient_id=patient.id,
        clinician_id=user.id,
        diagnosis_type=tb_analysis['who_category'],
        details=json.dumps({
            'tb_types': tb_analysis['tb_types'],
            'symptoms_present': tb_analysis['symptoms_present'],
            'presumptive_tb': tb_analysis['presumptive_tb'],
            'bacteriological_confirmation': tb_analysis['bacteriological_confirmation'],
            'bacteria_assessment': bacteria_assessment,
            'infection_assessment': infection_assessment,
            'resistance_profile': resistance_profile,
            'clinical_info': clinical_info,
            'treatment_regimen': treatment,
            'treatment_plan': treatment_plan,
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
        treatment_type=treatment_plan["selected_option"]["name"],
        drugs=treatment_plan["selected_option"]["drugs"],
        duration=treatment_plan["selected_option"]["duration"],
        dosage=(
            f"Intensive: {treatment.get('intensive_phase')}, Continuation: {treatment.get('continuation_phase')}"
            if treatment.get('intensive_phase') and treatment.get('continuation_phase')
            else treatment_plan["selected_option"]["administration"]
        ),
        administration_notes=treatment_plan["selected_option"]["notes"]
    )
    db.session.add(treatment_record)

    urgency = treatment.get("priority", "MODERATE")
    treatment_recommendation = {
        "type": clinical_info.get("diagnosis", tb_analysis["who_category"]),
        "category": tb_analysis["who_category"],
        "bacteria_species": bacteria_assessment["species"],
        "infection_type": infection_assessment["primary_infection"],
        "resistance_class": resistance_profile["classification"],
        "regimen_name": treatment_plan["selected_option"]["name"],
        "regimen_level": treatment_plan["selected_option"]["level"],
        "duration": treatment_plan["selected_option"]["duration"],
        "drugs": treatment_plan["selected_option"]["drugs"],
        "dosage": treatment_record.dosage,
        "administration": treatment_plan["selected_option"]["administration"],
        "monitoring": treatment_plan["selected_option"]["monitoring"],
        "urgency": urgency,
        "notes": treatment_plan["selected_option"]["notes"],
        "guideline_source": treatment_plan["guideline_source"],
        "decision_basis": treatment_plan["decision_basis"],
        "treatment_options": treatment_plan["options"],
    }

    if 'CONFIRMED' in tb_analysis['who_category'] or 'URGENT' in urgency or 'CRITICAL' in urgency:
        alert_created = create_alert(
            patient_id=patient.id,
            user_id=user.id,
            alert_type=f"ALERT: {tb_analysis['who_category']}",
            message=f"Patient {patient_name} (ID: {patient.patient_id}) classified as {tb_analysis['who_category']} with estimated bacteria {bacteria_assessment['species']}. {clinical_info.get('who_recommendation','')}",
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
        "bacteria_assessment": bacteria_assessment,
        "infection_assessment": infection_assessment,
        "resistance_profile": resistance_profile,
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
