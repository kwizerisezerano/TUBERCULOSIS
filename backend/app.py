import os
import re
import json
import subprocess
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import wraps


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
from models.models import db, User, Patient, Diagnosis, Treatment, Alert, LabTest, Prescription, AuditLog, ATCDrug, DetailedLabResult, AntibioticResistance, Hospital, PharmacyInventory
from models.train_model import preprocess_symptoms, get_patient_features, train_models_from_database
from risk_scoring import recalculate_risk_on_lab_result, recalculate_risk_on_prescription, recalculate_risk_on_diagnosis
from utils.security import encrypt_data, decrypt_data, hash_password, verify_password

load_dotenv()

app = Flask(__name__)
CORS(app)

SUPPORTED_UI_LANGS = {"EN", "FR", "SW", "RW"}


def role_required(*roles):
    """
    Decorator to restrict endpoint access to specific roles
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role not in roles:
                lang = get_request_lang()
                return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_request_lang():
    try:
        raw = (request.headers.get("X-UI-Language") or "").strip().upper()
    except Exception:
        raw = ""
    if raw in SUPPORTED_UI_LANGS:
        return raw

    accept = ""
    try:
        accept = (request.headers.get("Accept-Language") or "").strip().lower()
    except Exception:
        accept = ""
    if accept.startswith("fr"):
        return "FR"
    if accept.startswith("sw"):
        return "SW"
    if accept.startswith("rw"):
        return "RW"
    return "EN"


I18N = {
    "INVALID_EMAIL_OR_PASSWORD": {
        "EN": "Invalid email or password",
        "FR": "Email ou mot de passe invalide",
        "SW": "Barua pepe au nenosiri si sahihi",
        "RW": "Email cyangwa ijambo-banga si byo",
    },
    "EMAIL_EXISTS": {
        "EN": "User with this email already exists",
        "FR": "Un utilisateur avec cet email existe déjà",
        "SW": "Mtumiaji mwenye barua pepe hii tayari yupo",
        "RW": "Hari umukoresha ufite iyi email usanzwe ahari",
    },
    "USER_NOT_FOUND": {
        "EN": "User not found",
        "FR": "Utilisateur introuvable",
        "SW": "Mtumiaji hajapatikana",
        "RW": "Umukoresha ntaboneka",
    },
    "ACCESS_DENIED": {
        "EN": "Access denied",
        "FR": "Accès refusé",
        "SW": "Huruhusiwi",
        "RW": "Ntiwemerewe",
    },
    "PATIENT_DELETED": {
        "EN": "Patient deleted successfully",
        "FR": "Patient supprimé avec succès",
        "SW": "Mgonjwa amefutwa kikamilifu",
        "RW": "Umurwayi yasibwe neza",
    },
    "API_HOME_MESSAGE": {
        "EN": "TB Diagnostic System API",
        "FR": "API du système de diagnostic TB",
        "SW": "API ya mfumo wa uchunguzi wa TB",
        "RW": "API ya sisitemu yo gusuzuma igituntu",
    },
    "JWT_REQUIRED": {
        "EN": "JWT bearer token required for protected API routes",
        "FR": "Jeton JWT requis pour les routes protégées",
        "SW": "Token ya JWT inahitajika kwa njia zilizo na ulinzi",
        "RW": "JWT token irakenewe ku nzira zikingiwe",
    },
    "DATA_IMPORT_OK": {
        "EN": "Data import completed successfully",
        "FR": "Importation des données terminée avec succès",
        "SW": "Uingizaji wa data umekamilika",
        "RW": "Kwinjiza data byarangiye neza",
    },
    "SYMPTOM_ADVICE_DEFAULT": {
        "EN": "Complete TB diagnostic workup and follow national/WHO guidance.",
        "FR": "Compléter le bilan TB et suivre les directives nationales/OMS.",
        "SW": "Kamilisha uchunguzi wa TB na fuata miongozo ya kitaifa/WHO.",
        "RW": "Kora isuzuma rya TB ryuzuye kandi ukurikize amabwiriza y’igihugu/WHO.",
    },
    "SYMPTOM_ADVICE_HIGH": {
        "EN": "Urgent evaluation: isolate if infectious risk, order GeneXpert/sputum, and consider starting treatment per guidelines.",
        "FR": "Évaluation urgente : isoler si risque infectieux, demander GeneXpert/sputum, et envisager le traitement selon les directives.",
        "SW": "Tathmini ya haraka: mtenganishe kama kuna hatari ya maambukizi, agiza GeneXpert/sputum, na fikiria kuanza matibabu kulingana na mwongozo.",
        "RW": "Kwihutirwa: tanga isolation niba hari ibyago byo kwanduza, tegeka GeneXpert/sputum, kandi utekereze gutangira ubuvuzi uko amabwiriza abiteganya.",
    },
    "SYMPTOM_ADVICE_MODERATE": {
        "EN": "Prioritize TB testing (GeneXpert/sputum) and chest imaging; review comorbidities.",
        "FR": "Prioriser les tests TB (GeneXpert/sputum) et l’imagerie; revoir les comorbidités.",
        "SW": "Tanguliza vipimo vya TB (GeneXpert/sputum) na X-ray ya kifua; kagua magonjwa mengine.",
        "RW": "Shyira imbere ibizamini bya TB (GeneXpert/sputum) na X-ray; reba indwara zindi zifatanye.",
    },
    "SYMPTOM_ADVICE_LOW": {
        "EN": "TB less likely but possible; consider targeted testing if symptoms persist or risk factors present.",
        "FR": "TB moins probable mais possible ; envisager des tests ciblés si symptômes persistent ou facteurs de risque présents.",
        "SW": "TB inaonekana si ya juu lakini inawezekana; fanya vipimo maalum kama dalili zinaendelea au vihatarishi vipo.",
        "RW": "TB ishobora kuba atari yo cyane ariko birashoboka; tekereza ku bizamini byihariye niba ibimenyetso bikomeje cyangwa hari ibyago.",
    },
    "RED_FLAG_HEMOPTYSIS": {
        "EN": "Hemoptysis (coughing blood) - urgent assessment",
        "FR": "Hémoptysie (toux avec sang) - évaluation urgente",
        "SW": "Kukohoa damu - tathmini ya haraka",
        "RW": "Gukorora amaraso - kwihutirwa kwisuzuma",
    },
    "RED_FLAG_CNS": {
        "EN": "Possible CNS involvement (meningitis symptoms) - urgent referral",
        "FR": "Atteinte SNC possible (signes de méningite) - référence urgente",
        "SW": "Huenda mfumo wa neva umeathirika (dalili za meningitis) - rufaa ya haraka",
        "RW": "Hashobora kuba hari ikibazo ku bwonko/ubwonko (meningitis) - ohereza byihuse",
    },
    "RED_FLAG_BREATHLESSNESS": {
        "EN": "Breathlessness - assess severity and oxygenation",
        "FR": "Essoufflement - évaluer la gravité et l’oxygénation",
        "SW": "Upungufu wa pumzi - pima ukali na oksijeni",
        "RW": "Kubura umwuka - gupima ubukana n’oksijeni",
    },
    "RISK_LEVEL_DISPLAY": {
        "HIGH RISK": {"EN": "HIGH RISK", "FR": "RISQUE ÉLEVÉ", "SW": "HATARI KUBWA", "RW": "IBYAGO BIKOMEYE"},
        "MODERATE RISK": {"EN": "MODERATE RISK", "FR": "RISQUE MODÉRÉ", "SW": "HATARI YA KATI", "RW": "IBYAGO BY’INKERAGIHE"},
        "LOW RISK": {"EN": "LOW RISK", "FR": "FAIBLE RISQUE", "SW": "HATARI NDOGO", "RW": "IBYAGO BIKE"},
        "MINIMAL RISK": {"EN": "MINIMAL RISK", "FR": "RISQUE MINIME", "SW": "HATARI NDOGO SANA", "RW": "IBYAGO BIKE CYANE"},
    },
    "TEST_CLASS_INSUFFICIENT": {
        "EN": "Insufficient evidence",
        "FR": "Preuves insuffisantes",
        "SW": "Ushahidi hautoshi",
        "RW": "Ibimenyetso ntibihagije",
    },
    "TEST_CLASS_CONFIRMED_LIKELY": {
        "EN": "Bacteriologically confirmed TB likely",
        "FR": "TB probablement confirmée bactériologiquement",
        "SW": "TB inawezekana kuthibitishwa na maabara",
        "RW": "Birashoboka ko TB yemejwe na labo",
    },
    "TEST_CLASS_LESS_LIKELY": {
        "EN": "TB less likely (but not excluded)",
        "FR": "TB moins probable (mais pas exclue)",
        "SW": "TB inaonekana si ya juu (lakini haijaondolewa)",
        "RW": "TB ishobora kuba atari yo (ariko ntikurwaho)",
    },
    "FINDING_GENEXPERT_POS": {
        "EN": "GeneXpert MTB/RIF: Positive",
        "FR": "GeneXpert MTB/RIF : Positif",
        "SW": "GeneXpert MTB/RIF: Chanya",
        "RW": "GeneXpert MTB/RIF: Positive",
    },
    "FINDING_SPUTUM_POS": {
        "EN": "Sputum smear microscopy: Positive",
        "FR": "Frottis sputum : Positif",
        "SW": "Sputum smear: Chanya",
        "RW": "Sputum smear: Positive",
    },
    "FINDING_CXR_ABNORMAL": {
        "EN": "Chest X-ray: Abnormal",
        "FR": "Radio thoracique : Anormale",
        "SW": "X-ray ya kifua: Isiyo ya kawaida",
        "RW": "X-ray y'igituza: Abnormal",
    },
    "FINDING_ALL_NEGATIVE": {
        "EN": "GeneXpert/Sputum negative and X-ray normal",
        "FR": "GeneXpert/Sputum négatifs et radio normale",
        "SW": "GeneXpert/Sputum hasi na X-ray kawaida",
        "RW": "GeneXpert/Sputum negative na X-ray normal",
    },
    "LABEL_TB_CULTURE": {"EN": "TB culture", "FR": "Culture TB", "SW": "TB culture", "RW": "TB culture"},
    "LABEL_TST": {"EN": "TST", "FR": "TST", "SW": "TST", "RW": "TST"},
    "LABEL_IGRA": {"EN": "IGRA", "FR": "IGRA", "SW": "IGRA", "RW": "IGRA"},
    "LABEL_DST": {"EN": "Antibiogram/DST", "FR": "Antibiogramme/DST", "SW": "Antibiogram/DST", "RW": "Antibiogram/DST"},
    "INFECT_PULMONARY": {"EN": "Pulmonary TB", "FR": "TB pulmonaire", "SW": "TB ya mapafu", "RW": "TB yo mu bihaha"},
    "INFECT_LYMPH_NODE": {"EN": "Lymph Node TB", "FR": "TB ganglionnaire", "SW": "TB ya vifuko vya limfu", "RW": "TB yo mu dusabo twa lympho"},
    "INFECT_BONE_JOINT": {"EN": "Bone and Joint TB", "FR": "TB osseuse et articulaire", "SW": "TB y'amagufa n'ingingo", "RW": "TB yo mu magufa n'ingingo"},
    "INFECT_MENINGITIS": {"EN": "TB Meningitis", "FR": "Méningite tuberculeuse", "SW": "TB yo mu bwonko", "RW": "TB yo mu bwonko"},
    "INFECT_GENITOURINARY": {"EN": "Genitourinary TB", "FR": "TB génito-urinaire", "SW": "TB yo mu myanya ndangagitsina n'inkari", "RW": "TB yo mu myanya ndangagitsina n'inkari"},
    "INFECT_ABDOMINAL": {"EN": "Abdominal TB", "FR": "TB abdominale", "SW": "TB yo mu nda", "RW": "TB yo mu nda"},
    "INFECT_PLEURAL": {"EN": "Pleural TB", "FR": "TB pleurale", "SW": "TB yo ku gihu cy'ibihaha", "RW": "TB yo ku gihu cy'ibihaha"},
    "INFECT_MILIARY": {"EN": "Miliary TB", "FR": "TB miliaire", "SW": "TB yakwirakwiriye umubiri wose", "RW": "TB yakwirakwiriye umubiri wose"},
    "INFECT_LATENT": {"EN": "Latent TB Infection", "FR": "Infection tuberculeuse latente", "SW": "Ubwandu bwa TB butaragaragara", "RW": "Ubwandu bwa TB butaragaragara"},
    "INFECT_TB_HIV": {"EN": "TB/HIV Co-infection", "FR": "Co-infection TB/VIH", "SW": "Ubwandu bwa TB na HIV icyarimwe", "RW": "Ubwandu bwa TB na VIH icyarimwe"},
    "INFECT_NONE": {"EN": "No specific TB infection pattern confirmed", "FR": "Aucun schéma spécifique d'infection TB confirmé", "SW": "Nta bwandu bwa TB bwihariye bwemejwe", "RW": "Nta bwandu bwa TB bwihariye bwemejwe"},
    "SITE_LUNGS": {"EN": "Lungs", "FR": "Poumons", "SW": "Mapafu", "RW": "Ibihaha"},
    "SITE_LYMPH_NODES": {"EN": "Lymph nodes", "FR": "Ganglions lymphatiques", "SW": "Vifuko vya limfu", "RW": "Udusabo twa lympho"},
    "SITE_BONES_JOINTS": {"EN": "Spine, bones, or joints", "FR": "Colonne, os ou articulations", "SW": "Uti wa mgongo, amagufa cyangwa ingingo", "RW": "Urutirigongo, amagufa cyangwa ingingo"},
    "SITE_CNS": {"EN": "Central nervous system", "FR": "Système nerveux central", "SW": "Sisitemu yo hagati y'imyakura", "RW": "Sisitemu yo hagati y'imyakura"},
    "SITE_GU": {"EN": "Genitourinary tract", "FR": "Voies génito-urinaires", "SW": "Imiyoboro y'inkari n'imyanya ndangagitsina", "RW": "Imiyoboro y'inkari n'imyanya ndangagitsina"},
    "SITE_ABDOMEN": {"EN": "Abdomen/peritoneum", "FR": "Abdomen/péritoine", "SW": "Mu nda/peritoneum", "RW": "Mu nda/peritoneum"},
    "SITE_PLEURA": {"EN": "Pleura", "FR": "Plèvre", "SW": "Igihu cy'ibihaha", "RW": "Igihu cy'ibihaha"},
    "SITE_DISSEMINATED": {"EN": "Disseminated / whole body spread", "FR": "Disséminée / propagation dans tout le corps", "SW": "Byakwirakwiriye mu mubiri wose", "RW": "Byakwirakwiriye mu mubiri wose"},
    "SITE_LATENT": {"EN": "No active organ disease", "FR": "Aucune atteinte active d'organe", "SW": "Nta gice cy'umubiri cyarwaye ku buryo bugaragara", "RW": "Nta gice cy'umubiri cyarwaye ku buryo bugaragara"},
    "SITE_SYSTEMIC": {"EN": "Systemic comorbidity", "FR": "Comorbidité systémique", "SW": "Indi ndwara ikorana na yo mu mubiri", "RW": "Indi ndwara ijyana na yo mu mubiri"},
    "SITE_UNSPECIFIED": {"EN": "Unspecified", "FR": "Non précisé", "SW": "Bitasobanuwe neza", "RW": "Bitasobanuwe neza"},
    "ALERT_EMAIL_SUBJECT": {
        "EN": "TB Diagnostic Alert: {alert_type}",
        "FR": "Alerte TB : {alert_type}",
        "SW": "Tahadhari ya TB: {alert_type}",
        "RW": "Itangazo rya TB: {alert_type}",
    },
    "ALERT_EMAIL_BODY": {
        "EN": "Patient Alert:\n\n{message}\n\nPlease log in to the system for more details.",
        "FR": "Alerte patient :\n\n{message}\n\nVeuillez vous connecter pour plus de détails.",
        "SW": "Tahadhari ya mgonjwa:\n\n{message}\n\nTafadhali ingia kwenye mfumo kwa maelezo zaidi.",
        "RW": "Itangazo ku murwayi:\n\n{message}\n\nNyamuneka winjire muri sisitemu kugira ngo ubone ibisobanuro birambuye.",
    },
    "ALERT_MESSAGE_TEMPLATE": {
        "EN": "Patient {patient_name} (ID: {patient_id}) classified as {category} with estimated bacteria {species}. {who_recommendation}",
        "FR": "Patient {patient_name} (ID : {patient_id}) classé {category} avec bactérie estimée {species}. {who_recommendation}",
        "SW": "Mgonjwa {patient_name} (ID: {patient_id}) ameainishwa {category} na bakteria anayedhaniwa {species}. {who_recommendation}",
        "RW": "Umurwayi {patient_name} (ID: {patient_id}) yashyizwe mu rwego {category} n'udukoko twagereranijwe {species}. {who_recommendation}",
    },
    "RES_DS": {
        "EN": "Drug-sensitive TB (DS-TB)",
        "FR": "TB sensible aux médicaments (DS-TB)",
        "SW": "TB inayoitikia dawa (DS-TB)",
        "RW": "TB yumva imiti (DS-TB)",
    },
    "RES_XDR": {
        "EN": "Extensively Drug-Resistant TB (XDR-TB)",
        "FR": "TB ultra-résistante (XDR-TB)",
        "SW": "TB yenye usugu mkubwa sana wa dawa (XDR-TB)",
        "RW": "TB ifite usugire bukabije ku miti (XDR-TB)",
    },
    "RES_MDR": {
        "EN": "Multidrug-Resistant TB (MDR-TB)",
        "FR": "TB multirésistante (MDR-TB)",
        "SW": "TB yenye usugu kwa dawa nyingi (MDR-TB)",
        "RW": "TB irwanya imiti myinshi (MDR-TB)",
    },
    "RES_PZA": {
        "EN": "Pyrazinamide-resistant pattern",
        "FR": "Profil résistant au pyrazinamide",
        "SW": "Muundo wa usugu wa pyrazinamide",
        "RW": "Uko pyrazinamide irwanywa",
    },
    "RES_RR": {
        "EN": "Rifampicin-Resistant TB (RR-TB)",
        "FR": "TB résistante à la rifampicine (RR-TB)",
        "SW": "TB yenye usugu wa rifampicin (RR-TB)",
        "RW": "TB irwanya rifampicin (RR-TB)",
    },
    "RES_DR": {
        "EN": "Drug-Resistant TB (DR-TB)",
        "FR": "TB résistante aux médicaments (DR-TB)",
        "SW": "TB yenye usugu wa dawa (DR-TB)",
        "RW": "TB irwanya imiti (DR-TB)",
    },
    "BASIS_XDR": {
        "EN": "Detected XDR-level resistance markers from DST/GeneXpert metadata.",
        "FR": "Marqueurs de résistance XDR détectés dans les données DST/GeneXpert.",
        "SW": "Alama za usugu wa kiwango cha XDR zimeonekana kwenye DST/GeneXpert.",
        "RW": "Ibimenyetso bya resistance yo ku rwego rwa XDR byabonetse muri DST/GeneXpert.",
    },
    "BASIS_MDR": {
        "EN": "Detected rifampicin plus isoniazid resistance pattern.",
        "FR": "Profil de résistance à la rifampicine et à l'isoniazide détecté.",
        "SW": "Muundo wa usugu wa rifampicin na isoniazid umeonekana.",
        "RW": "Pattern ya resistance ya rifampicin na isoniazid yagaragaye.",
    },
    "BASIS_PZA": {
        "EN": "Only pyrazinamide resistance was provided; review for M. bovis or regimen modification.",
        "FR": "Seule une résistance au pyrazinamide est fournie ; revoir M. bovis ou modifier le schéma.",
        "SW": "Usugu wa pyrazinamide pekee umeonekana; kagua M. bovis au badili mpango wa dawa.",
        "RW": "Hagaragajwe resistance ya pyrazinamide gusa; reba M. bovis cyangwa uhindure gahunda y’imiti.",
    },
    "BASIS_RR": {
        "EN": "Detected rifampicin resistance signal.",
        "FR": "Signal de résistance à la rifampicine détecté.",
        "SW": "Ishara ya usugu wa rifampicin imeonekana.",
        "RW": "Ikimenyetso cya resistance ya rifampicin cyagaragaye.",
    },
    "BASIS_DR": {
        "EN": "Resistance data present but not enough to label RR/MDR/XDR confidently.",
        "FR": "Données de résistance présentes mais insuffisantes pour conclure RR/MDR/XDR.",
        "SW": "Data ya usugu ipo lakini haitoshi kuweka RR/MDR/XDR kwa uhakika.",
        "RW": "Hari data ya resistance ariko ntihagije ngo twemeze RR/MDR/XDR.",
    },
    "BASIS_DS": {
        "EN": "No resistance markers supplied; managed as drug-sensitive TB unless DST changes the plan.",
        "FR": "Aucun marqueur de résistance fourni ; prise en charge comme TB sensible sauf changement DST.",
        "SW": "Hakuna alama za usugu zilizotolewa; hushughulikiwa kama TB inayoitikia dawa hadi DST ibadilishe mpango.",
        "RW": "Nta bimenyetso bya resistance byatanzwe; ifatwa nka TB yumva imiti keretse DST ihinduye gahunda.",
    },
    "ALERT_LABEL": {
        "EN": "TB alert",
        "FR": "Alerte TB",
        "SW": "Tahadhari ya TB",
        "RW": "Itangazo rya TB",
    },
    "TRAIN_MODEL_FAILED": {
        "EN": "Model training failed",
        "FR": "L'entraînement du modèle a échoué",
        "SW": "Mafunzo ya modeli yameshindwa",
        "RW": "Gutoza modeli byanze",
    },
    "IMPORT_DATA_FAILED": {
        "EN": "Data import failed",
        "FR": "L'importation des données a échoué",
        "SW": "Uingizaji wa data umeshindwa",
        "RW": "Kwinjiza data byanze",
    },
}

LITERAL_I18N = {
    "Mycobacterium tuberculosis": {"EN": "Mycobacterium tuberculosis", "FR": "Mycobacterium tuberculosis", "SW": "Mycobacterium tuberculosis", "RW": "Mycobacterium tuberculosis"},
    "Mycobacterium bovis": {"EN": "Mycobacterium bovis", "FR": "Mycobacterium bovis", "SW": "Mycobacterium bovis", "RW": "Mycobacterium bovis"},
    "Mycobacterium africanum": {"EN": "Mycobacterium africanum", "FR": "Mycobacterium africanum", "SW": "Mycobacterium africanum", "RW": "Mycobacterium africanum"},
    "Mycobacterium canettii": {"EN": "Mycobacterium canettii", "FR": "Mycobacterium canettii", "SW": "Mycobacterium canettii", "RW": "Mycobacterium canettii"},
    "Mycobacterium microti": {"EN": "Mycobacterium microti", "FR": "Mycobacterium microti", "SW": "Mycobacterium microti", "RW": "Mycobacterium microti"},
    "Mycobacterium caprae": {"EN": "Mycobacterium caprae", "FR": "Mycobacterium caprae", "SW": "Mycobacterium caprae", "RW": "Mycobacterium caprae"},
    "Mycobacterium pinnipedii": {"EN": "Mycobacterium pinnipedii", "FR": "Mycobacterium pinnipedii", "SW": "Mycobacterium pinnipedii", "RW": "Mycobacterium pinnipedii"},
    "Mycobacterium orygis": {"EN": "Mycobacterium orygis", "FR": "Mycobacterium orygis", "SW": "Mycobacterium orygis", "RW": "Mycobacterium orygis"},
    "ALERT:": {"EN": "TB alert:", "FR": "Alerte TB :", "SW": "Tahadhari ya TB:", "RW": "Itangazo rya TB:"},
    "Clinician selected a specific TB bacteria species.": {
        "EN": "Clinician selected a specific TB bacteria species.",
        "FR": "Le clinicien a choisi une espèce précise de bactérie TB.",
        "SW": "Mhudumu wa afya amechagua aina maalum ya bakteria wa TB.",
        "RW": "Umuganga yahisemo ubwoko bwihariye bwa bagiteri itera TB.",
    },
    "Defaulted to the most common human TB species because the patient record did not contain enough species-specific evidence.": {
        "EN": "Defaulted to the most common human TB species because the patient record did not contain enough species-specific evidence.",
        "FR": "Le système a retenu l'espèce de TB humaine la plus fréquente car le dossier du patient ne contenait pas assez d'indices spécifiques.",
        "SW": "Mfumo umechagua aina ya TB inayopatikana sana kwa binadamu kwa sababu rekodi ya mgonjwa haikuwa na ushahidi wa kutosha wa aina maalum.",
        "RW": "Sisitemu yahisemo ubwoko bwa TB busanzwe buboneka ku bantu kuko dosiye y'umurwayi itari ifite ibimenyetso bihagije by'ubwoko bwihariye.",
    },
    "The most common cause of human tuberculosis worldwide.": {
        "EN": "The most common cause of human tuberculosis worldwide.",
        "FR": "La cause la plus fréquente de tuberculose humaine dans le monde.",
        "SW": "Ndiyo sababu ya kawaida zaidi ya TB kwa binadamu duniani.",
        "RW": "Ni yo ntandaro ikunze gutera igituntu ku bantu ku isi yose.",
    },
    "Human-to-human airborne transmission.": {
        "EN": "Human-to-human airborne transmission.",
        "FR": "Transmission aérienne d'une personne à l'autre.",
        "SW": "Maambukizi ya hewani kutoka mtu mmoja kwenda kwa mwingine.",
        "RW": "Yandura mu mwuka iva ku muntu umwe ikagera ku wundi.",
    },
    "Routine TB molecular tests and culture commonly target this species within the MTBC.": {
        "EN": "Routine TB molecular tests and culture commonly target this species within the MTBC.",
        "FR": "Les tests moléculaires TB courants et la culture ciblent souvent cette espèce dans le MTBC.",
        "SW": "Vipimo vya kawaida vya molekuli vya TB na culture hulenga aina hii mara nyingi ndani ya MTBC.",
        "RW": "Ibizamini bya molekile bya TB bisanzwe na culture bikunze kwibanda kuri ubu bwoko muri MTBC.",
    },
    "Use standard first-line treatment unless drug resistance is detected.": {
        "EN": "Use standard first-line treatment unless drug resistance is detected.",
        "FR": "Utiliser le traitement standard de première ligne sauf si une résistance est détectée.",
        "SW": "Tumia matibabu ya kawaida ya mstari wa kwanza isipokuwa usugu wa dawa ugundulike.",
        "RW": "Koresha ubuvuzi busanzwe bw'umurongo wa mbere keretse hagaragaye ko imiti idafata.",
    },
    "A zoonotic MTBC species linked to cattle and contaminated dairy products.": {
        "EN": "A zoonotic MTBC species linked to cattle and contaminated dairy products.",
        "FR": "Une espèce de MTBC zoonotique liée au bétail et aux produits laitiers contaminés.",
        "SW": "Aina ya MTBC inayotoka kwa wanyama, ikihusishwa na ng'ombe na maziwa yaliyosibikwa.",
        "RW": "Ni ubwoko bwa MTBC buva ku nyamaswa, bujyanye n'inka n'ibikomoka ku mata byanduye.",
    },
    "Cattle exposure or unpasteurized milk products.": {
        "EN": "Cattle exposure or unpasteurized milk products.",
        "FR": "Contact avec le bétail ou produits laitiers non pasteurisés.",
        "SW": "Mawasiliano na ng'ombe au bidhaa za maziwa zisizochemshwa/pasteurized.",
        "RW": "Guhura n'inka cyangwa kunywa ibikomoka ku mata bitapasterijwe.",
    },
    "Culture speciation is important when zoonotic exposure is suspected.": {
        "EN": "Culture speciation is important when zoonotic exposure is suspected.",
        "FR": "L'identification de l'espèce par culture est importante si une origine animale est suspectée.",
        "SW": "Kutambua aina kwa culture ni muhimu kama maambukizi kutoka kwa mnyama yanashukiwa.",
        "RW": "Kumenya ubwoko hakoreshejwe culture ni ngombwa niba hakekwa inkomoko ku nyamaswa.",
    },
    "Confirm speciation because M. bovis is typically pyrazinamide resistant; tailor regimen accordingly.": {
        "EN": "Confirm speciation because M. bovis is typically pyrazinamide resistant; tailor regimen accordingly.",
        "FR": "Confirmer l'espèce car M. bovis est habituellement résistant au pyrazinamide ; adapter le traitement en conséquence.",
        "SW": "Thibitisha aina kwa sababu M. bovis huwa na usugu kwa pyrazinamide; rekebisha mpango wa dawa ipasavyo.",
        "RW": "Emeza ubwoko kuko M. bovis akenshi irwanya pyrazinamide; hindura gahunda y'ubuvuzi bikurikije ibisubizo.",
    },
    "An MTBC member that causes human TB, especially in parts of West Africa.": {
        "EN": "An MTBC member that causes human TB, especially in parts of West Africa.",
        "FR": "Un membre du MTBC qui cause la TB humaine, surtout en Afrique de l'Ouest.",
        "SW": "Aina ya MTBC inayosababisha TB kwa binadamu, hasa maeneo ya Afrika Magharibi.",
        "RW": "Ni umwe mu bagize MTBC batera TB ku bantu, cyane cyane mu bice by'Afurika y'Iburengerazuba.",
    },
    "Human transmission, often with West African epidemiologic linkage.": {
        "EN": "Human transmission, often with West African epidemiologic linkage.",
        "FR": "Transmission humaine, souvent avec un lien épidémiologique ouest-africain.",
        "SW": "Huenea kati ya watu, mara nyingi ikiwa na uhusiano wa kieneo wa Afrika Magharibi.",
        "RW": "Yandurira hagati y'abantu, kenshi ifite aho ihuriye n'ibice by'Afurika y'Iburengerazuba.",
    },
    "Reference-lab speciation is useful where M. africanum is endemic.": {
        "EN": "Reference-lab speciation is useful where M. africanum is endemic.",
        "FR": "L'identification par laboratoire de référence est utile là où M. africanum est endémique.",
        "SW": "Kutambua aina kwenye maabara ya rufaa ni muhimu ambako M. africanum hupatikana sana.",
        "RW": "Kumenya ubwoko muri laboratwari yoherezwamo ni ngombwa aho M. africanum ikunze kuboneka.",
    },
    "Treat similarly to drug-sensitive TB unless resistance testing indicates otherwise.": {
        "EN": "Treat similarly to drug-sensitive TB unless resistance testing indicates otherwise.",
        "FR": "Traiter comme une TB sensible aux médicaments sauf indication contraire des tests de résistance.",
        "SW": "Tibu kama TB inayoitikia dawa isipokuwa vipimo vya usugu vionyeshe vinginevyo.",
        "RW": "Yivure nk'igituntu cyumva imiti keretse ibizamini byerekanye ibindi.",
    },
    "A rare smooth-colony MTBC member reported mainly in the Horn of Africa.": {
        "EN": "A rare smooth-colony MTBC member reported mainly in the Horn of Africa.",
        "FR": "Un membre rare du MTBC à colonies lisses, surtout signalé dans la Corne de l'Afrique.",
        "SW": "Aina adimu ya MTBC yenye koloni laini, iliyoripotiwa hasa kwenye Pembe ya Afrika.",
        "RW": "Ni ubwoko budakunze kuboneka bwa MTBC, bwagaragaye cyane mu Ihembe rya Afurika.",
    },
    "Rare human infection with specific geographic clustering.": {
        "EN": "Rare human infection with specific geographic clustering.",
        "FR": "Infection humaine rare avec regroupement géographique précis.",
        "SW": "Maambukizi adimu kwa binadamu yenye kujikusanya kwenye maeneo maalum.",
        "RW": "Ni ubwandu budakunze kuboneka ku bantu kandi bukagaragara cyane mu duce twihariye.",
    },
    "Requires specialist or reference-laboratory speciation support.": {
        "EN": "Requires specialist or reference-laboratory speciation support.",
        "FR": "Nécessite l'appui d'un spécialiste ou d'un laboratoire de référence pour identifier l'espèce.",
        "SW": "Inahitaji msaada wa mtaalamu au maabara ya rufaa ili kutambua aina.",
        "RW": "Bisaba ubufasha bw'inzobere cyangwa laboratwari yoherezwamo kugira ngo hamenyekane ubwoko.",
    },
    "Seek infectious-disease or TB-specialist input because cases are rare.": {
        "EN": "Seek infectious-disease or TB-specialist input because cases are rare.",
        "FR": "Demander l'avis d'un spécialiste des maladies infectieuses ou de la TB car les cas sont rares.",
        "SW": "Tafuta ushauri wa mtaalamu wa magonjwa ya kuambukiza au TB kwa sababu visa hivi ni adimu.",
        "RW": "Saba inama y'inzobere mu ndwara z'ubwandu cyangwa TB kuko izi ndwara zidakunze kuboneka.",
    },
    "An uncommon MTBC species more often associated with rodents than humans.": {
        "EN": "An uncommon MTBC species more often associated with rodents than humans.",
        "FR": "Une espèce peu fréquente du MTBC plus souvent liée aux rongeurs qu'aux humains.",
        "SW": "Aina isiyo ya kawaida ya MTBC inayohusishwa zaidi na panya kuliko binadamu.",
        "RW": "Ni ubwoko budasanzwe bwa MTBC bujyanye cyane n'imbeba kurusha abantu.",
    },
    "Rodent or wildlife exposure.": {
        "EN": "Rodent or wildlife exposure.",
        "FR": "Exposition aux rongeurs ou à la faune sauvage.",
        "SW": "Kugusana na panya au wanyamapori.",
        "RW": "Guhura n'imbeba cyangwa inyamaswa zo mu ishyamba.",
    },
    "Species confirmation often needs specialized molecular testing.": {
        "EN": "Species confirmation often needs specialized molecular testing.",
        "FR": "La confirmation de l'espèce nécessite souvent des tests moléculaires spécialisés.",
        "SW": "Kuthibitisha aina mara nyingi huhitaji vipimo maalum vya molekuli.",
        "RW": "Kwemeza ubwoko kenshi bisaba ibizamini byihariye bya molekile.",
    },
    "Manage with specialist input and drug-susceptibility guidance.": {
        "EN": "Manage with specialist input and drug-susceptibility guidance.",
        "FR": "Prise en charge avec avis spécialisé et orientation selon la sensibilité aux médicaments.",
        "SW": "Shughulikia kwa ushauri wa mtaalamu na mwongozo wa unyeti wa dawa.",
        "RW": "Byitabweho hifashishijwe inama y'inzobere n'ubuyobozi bushingiye ku buryo imiti ifata.",
    },
    "An MTBC species usually associated with goats and other livestock.": {
        "EN": "An MTBC species usually associated with goats and other livestock.",
        "FR": "Une espèce du MTBC généralement associée aux chèvres et autres animaux d'élevage.",
        "SW": "Aina ya MTBC inayohusishwa mara nyingi na mbuzi na mifugo mingine.",
        "RW": "Ni ubwoko bwa MTBC bukunda gufatanywa n'ihene n'indi matungo.",
    },
    "Goat, sheep, or livestock exposure.": {
        "EN": "Goat, sheep, or livestock exposure.",
        "FR": "Exposition aux chèvres, moutons ou autres animaux d'élevage.",
        "SW": "Kugusana na mbuzi, kondoo, au mifugo mingine.",
        "RW": "Guhura n'ihene, intama cyangwa andi matungo.",
    },
    "Consider speciation when livestock exposure is prominent.": {
        "EN": "Consider speciation when livestock exposure is prominent.",
        "FR": "Envisager l'identification de l'espèce si l'exposition au bétail est importante.",
        "SW": "Fikiria kutambua aina kama mgusano na mifugo ni mkubwa.",
        "RW": "Tekereza ku kumenya ubwoko niba guhura n'amatungo biri hejuru.",
    },
    "Treat as TB but review susceptibilities and zoonotic implications.": {
        "EN": "Treat as TB but review susceptibilities and zoonotic implications.",
        "FR": "Traiter comme une TB mais revoir les sensibilités et les implications zoonotiques.",
        "SW": "Tibu kama TB lakini kagua unyeti wa dawa na athari za maambukizi yatokayo kwa mnyama.",
        "RW": "Byivure nka TB ariko urebe uko imiti ifata n'ingaruka zijyanye no kuva ku nyamaswa.",
    },
    "A rare MTBC species associated with seals and sea lions.": {
        "EN": "A rare MTBC species associated with seals and sea lions.",
        "FR": "Une espèce rare du MTBC associée aux phoques et lions de mer.",
        "SW": "Aina adimu ya MTBC inayohusishwa na seals na sea lions.",
        "RW": "Ni ubwoko budakunze kuboneka bwa MTBC bujyanye na seals na sea lions.",
    },
    "Marine mammal exposure.": {
        "EN": "Marine mammal exposure.",
        "FR": "Exposition à des mammifères marins.",
        "SW": "Kugusana na mamalia wa baharini.",
        "RW": "Guhura n'inyamaswa z'inyabere zo mu nyanja.",
    },
    "Reference-lab confirmation is recommended.": {
        "EN": "Reference-lab confirmation is recommended.",
        "FR": "Une confirmation par laboratoire de référence est recommandée.",
        "SW": "Inashauriwa kuthibitisha kwenye maabara ya rufaa.",
        "RW": "Birasabwa kubyemeza muri laboratwari yoherezwamo.",
    },
    "Use specialist review because human infection is rare and zoonotic.": {
        "EN": "Use specialist review because human infection is rare and zoonotic.",
        "FR": "Faire revoir par un spécialiste car l'infection humaine est rare et zoonotique.",
        "SW": "Tumia uchunguzi wa mtaalamu kwa sababu maambukizi kwa binadamu ni adimu na hutoka kwa mnyama.",
        "RW": "Bigenzurwe n'inzobere kuko ubwandu ku bantu budakunze kuboneka kandi bushobora kuva ku nyamaswa.",
    },
    "An MTBC species reported in both animals and humans, often with zoonotic linkage.": {
        "EN": "An MTBC species reported in both animals and humans, often with zoonotic linkage.",
        "FR": "Une espèce du MTBC signalée chez l'animal et l'humain, souvent liée à une transmission zoonotique.",
        "SW": "Aina ya MTBC iliyoripotiwa kwa wanyama na binadamu, mara nyingi ikiwa na uhusiano wa zoonotic.",
        "RW": "Ni ubwoko bwa MTBC bwagaragaye ku nyamaswa no ku bantu, kenshi bufite inkomoko ku nyamaswa.",
    },
    "Animal exposure or South Asian epidemiologic linkage.": {
        "EN": "Animal exposure or South Asian epidemiologic linkage.",
        "FR": "Exposition animale ou lien épidémiologique avec l'Asie du Sud.",
        "SW": "Mgusano na mnyama au uhusiano wa kieneo wa Asia Kusini.",
        "RW": "Guhura n'inyamaswa cyangwa inkomoko ijyanye n'Aziya y'Epfo.",
    },
    "Speciation generally requires molecular reference testing.": {
        "EN": "Speciation generally requires molecular reference testing.",
        "FR": "L'identification de l'espèce nécessite généralement des tests moléculaires de référence.",
        "SW": "Kutambua aina kwa kawaida huhitaji vipimo vya molekuli vya maabara ya rufaa.",
        "RW": "Kumenya ubwoko akenshi bisaba ibizamini bya molekile byo muri laboratwari yoherezwamo.",
    },
    "Treat as TB while confirming species and resistance profile.": {
        "EN": "Treat as TB while confirming species and resistance profile.",
        "FR": "Traiter comme une TB tout en confirmant l'espèce et le profil de résistance.",
        "SW": "Tibu kama TB huku ukithibitisha aina na wasifu wa usugu wa dawa.",
        "RW": "Byivure nka TB mu gihe urimo wemeza ubwoko n'uko imiti ifata cyangwa idafata.",
    },
    "Pulmonary TB (PTB)": {
        "EN": "Pulmonary TB (PTB)",
        "FR": "TB pulmonaire (PTB)",
        "SW": "TB ya mapafu (PTB)",
        "RW": "TB yo mu bihaha (PTB)",
    },
    "TB infection affecting the lungs - the most common and contagious form of TB": {
        "EN": "TB infection affecting the lungs - the most common and contagious form of TB",
        "FR": "Infection TB touchant les poumons - la forme la plus fréquente et la plus contagieuse de TB",
        "SW": "Maambukizi ya TB yanayoathiri mapafu - ndiyo aina ya kawaida na ya kuambukiza zaidi ya TB",
        "RW": "Ubwandu bwa TB bufata ibihaha - ni bwo bwoko bukunze kuboneka kandi bwanduza cyane",
    },
    "Cough lasting ≥2 weeks, hemoptysis, fever, night sweats, weight loss, chest pain": {
        "EN": "Cough lasting >=2 weeks, hemoptysis, fever, night sweats, weight loss, chest pain",
        "FR": "Toux durant >=2 semaines, hémoptysie, fièvre, sueurs nocturnes, perte de poids, douleur thoracique",
        "SW": "Kikohozi cha zaidi ya wiki 2, kukohoa damu, homa, jasho la usiku, kupungua uzito, maumivu ya kifua",
        "RW": "Inkorora imaze nibura ibyumweru 2, gukorora amaraso, umuriro, kubira ibyuya nijoro, kugabanuka ibiro, kubabara mu gituza",
    },
    "Initiate treatment promptly according to national guidelines; ensure airborne precautions": {
        "EN": "Initiate treatment promptly according to national guidelines; ensure airborne precautions",
        "FR": "Commencer rapidement le traitement selon les directives nationales; assurer les précautions aériennes",
        "SW": "Anza matibabu haraka kulingana na miongozo ya taifa; hakikisha tahadhari za hewani",
        "RW": "Tangira ubuvuzi vuba ukurikije amabwiriza y'igihugu; hubahirizwe kwirinda ubwandu bwo mu mwuka",
    },
    "Fully susceptible first-line profile": {
        "EN": "Fully susceptible first-line profile",
        "FR": "Profil complètement sensible de première ligne",
        "SW": "Muundo wa mazingira yote ya kwanza yenye uwezo wa kukabiliwa na dawa",
        "RW": "Incamake y’umurongo wa mbere yumva imiti yose",
    },
    "Rifampicin resistance detected": {
        "EN": "Rifampicin resistance detected",
        "FR": "Résistance à la rifampicine détectée",
        "SW": "Usugu wa rifampicin umeonekana",
        "RW": "Resistance ya rifampicin yagaragaye",
    },
    "Pyrazinamide resistance suspected": {
        "EN": "Pyrazinamide resistance suspected",
        "FR": "Résistance à la pyrazinamide suspectée",
        "SW": "Usugu wa pyrazinamide unashukiwa",
        "RW": "Resistance ya pyrazinamide inekewa",
    },
    "Isoniazid resistance detected": {
        "EN": "Isoniazid resistance detected",
        "FR": "Résistance à l’isoniazide détectée",
        "SW": "Usugu wa isoniazid umeonekana",
        "RW": "Resistance ya isoniazid yagaragaye",
    },
    "MDR profile confirmed by DST": {
        "EN": "MDR profile confirmed by DST",
        "FR": "Profil MDR confirmé par DST",
        "SW": "Muundo wa MDR umethibitishwa na DST",
        "RW": "Incamake ya MDR yemejwe na DST",
    },
    "XDR profile suspected": {
        "EN": "XDR profile suspected",
        "FR": "Profil XDR suspecté",
        "SW": "Muundo wa XDR unashukiwa",
        "RW": "Incamake ya XDR inekewa",
    },
    "Airborne precautions, patient isolation, respiratory hygiene": {
        "EN": "Airborne precautions, patient isolation, respiratory hygiene",
        "FR": "Précautions aériennes, isolement du patient, hygiène respiratoire",
        "SW": "Tahadhari za hewani, kumtenga mgonjwa, na usafi wa njia ya hewa",
        "RW": "Kwikingira ubwandu bwo mu mwuka, gutandukanya umurwayi, no kwita ku isuku y'ubuhumekero",
    },
    "Sputum smear, GeneXpert, chest X-ray, TB culture (if available)": {
        "EN": "Sputum smear, GeneXpert, chest X-ray, TB culture (if available)",
        "FR": "Frottis sputum, GeneXpert, radiographie thoracique, culture TB (si disponible)",
        "SW": "Sputum smear, GeneXpert, X-ray ya kifua, culture ya TB (ikiwa ipo)",
        "RW": "Sputum smear, GeneXpert, X-ray y'igituza, na culture ya TB (niba ihari)",
    },
    "Lymph Node TB (EPTB)": {
        "EN": "Lymph Node TB (EPTB)",
        "FR": "TB ganglionnaire (EPTB)",
        "SW": "TB ya vifuko vya limfu (EPTB)",
        "RW": "TB yo mu dusabo twa lympho (EPTB)",
    },
    "TB infection affecting the lymph nodes, most commonly in the neck": {
        "EN": "TB infection affecting the lymph nodes, most commonly in the neck",
        "FR": "Infection TB touchant les ganglions lymphatiques, le plus souvent au cou",
        "SW": "Maambukizi ya TB kwenye vifuko vya limfu, mara nyingi shingoni",
        "RW": "Ubwandu bwa TB bufata udusabo twa lympho, kenshi mu ijosi",
    },
    "Painless swollen lymph nodes (usually in neck), fever, weight loss": {
        "EN": "Painless swollen lymph nodes (usually in neck), fever, weight loss",
        "FR": "Ganglions gonflés non douloureux (souvent au cou), fièvre, perte de poids",
        "SW": "Vifuko vya limfu vilivyovimba bila maumivu (mara nyingi shingoni), homa, kupungua uzito",
        "RW": "Udusabo twa lympho twabyimbye tudatera ububabare (kenshi mu ijosi), umuriro, kugabanuka ibiro",
    },
    "Fine-needle aspiration or biopsy for confirmation; standard EPTB regimen": {
        "EN": "Fine-needle aspiration or biopsy for confirmation; standard EPTB regimen",
        "FR": "Ponction à l'aiguille fine ou biopsie pour confirmer; schéma EPTB standard",
        "SW": "FNA au biopsy kuthibitisha; tumia mpango wa kawaida wa EPTB",
        "RW": "Hakoreshejwe urushinge ruto cyangwa biopsy kugira ngo byemezwe; ukoreshe gahunda isanzwe ya EPTB",
    },
    "Standard precautions": {
        "EN": "Standard precautions",
        "FR": "Précautions standard",
        "SW": "Tahadhari za kawaida",
        "RW": "Ingamba zisanzwe zo kwirinda",
    },
    "Bone & Joint TB (EPTB, including Pott's disease)": {
        "EN": "Bone & Joint TB (EPTB, including Pott's disease)",
        "FR": "TB osseuse et articulaire (EPTB, y compris maladie de Pott)",
        "SW": "TB ya mifupa na viungo (EPTB, ikijumuisha ugonjwa wa Pott)",
        "RW": "TB yo mu magufa n'ingingo (EPTB, harimo indwara ya Pott)",
    },
    "TB infection affecting bones or joints, most commonly the spine": {
        "EN": "TB infection affecting bones or joints, most commonly the spine",
        "FR": "Infection TB touchant les os ou les articulations, le plus souvent la colonne",
        "SW": "Maambukizi ya TB kwenye mifupa au viungo, hasa uti wa mgongo",
        "RW": "Ubwandu bwa TB bufata amagufa cyangwa ingingo, cyane cyane urutirigongo",
    },
    "Back pain, joint swelling, difficulty walking, fever, weight loss": {
        "EN": "Back pain, joint swelling, difficulty walking, fever, weight loss",
        "FR": "Douleur du dos, gonflement articulaire, difficulté à marcher, fièvre, perte de poids",
        "SW": "Maumivu ya mgongo, kuvimba kwa viungo, ugumu wa kutembea, homa, kupungua uzito",
        "RW": "Kubabara umugongo, kubyimba kw'ingingo, kugorwa no kugenda, umuriro, kugabanuka ibiro",
    },
    "MRI/CT for diagnosis; consider orthopedic consultation; 9-12 month regimen": {
        "EN": "MRI/CT for diagnosis; consider orthopedic consultation; 9-12 month regimen",
        "FR": "IRM/CT pour le diagnostic; envisager une consultation orthopédique; schéma de 9-12 mois",
        "SW": "MRI/CT kwa uchunguzi; fikiria ushauri wa daktari wa mifupa; mpango wa miezi 9-12",
        "RW": "MRI/CT mu gusuzuma; tekereza ku nama y'umuganga w'amagufa; gahunda y'amezi 9-12",
    },
    "TB Meningitis (EPTB - LIFE THREATENING)": {
        "EN": "TB Meningitis (EPTB - LIFE THREATENING)",
        "FR": "Méningite tuberculeuse (EPTB - menace vitale)",
        "SW": "Meningitis ya TB (EPTB - hatari kwa maisha)",
        "RW": "Meningitis ya TB (EPTB - ishobora gushyira ubuzima mu kaga)",
    },
    "TB infection of the meninges covering the brain and spinal cord - high mortality": {
        "EN": "TB infection of the meninges covering the brain and spinal cord - high mortality",
        "FR": "Infection TB des méninges couvrant le cerveau et la moelle épinière - mortalité élevée",
        "SW": "Maambukizi ya TB kwenye utando wa ubongo na uti wa mgongo - hatari kubwa ya kifo",
        "RW": "Ubwandu bwa TB ku tunyangingo dutwikira ubwonko n'umugongo - bufite ibyago byinshi byo gupfa",
    },
    "Severe headache, neck stiffness, confusion, vomiting, fever": {
        "EN": "Severe headache, neck stiffness, confusion, vomiting, fever",
        "FR": "Maux de tête intenses, raideur de la nuque, confusion, vomissements, fièvre",
        "SW": "Maumivu makali ya kichwa, shingo kukakamaa, kuchanganyikiwa, kutapika, homa",
        "RW": "Kubabara umutwe cyane, ijosi rikomeye, urujijo, kuruka, umuriro",
    },
    "URGENT hospitalization; lumbar puncture; 12-month regimen; steroids": {
        "EN": "URGENT hospitalization; lumbar puncture; 12-month regimen; steroids",
        "FR": "Hospitalisation URGENTE; ponction lombaire; schéma de 12 mois; corticoïdes",
        "SW": "Kulazwa HARAKA; lumbar puncture; mpango wa miezi 12; steroids",
        "RW": "Kujyanwa kwa muganga byihutirwa; lumbar puncture; gahunda y'amezi 12; steroids",
    },
    "Genitourinary TB (EPTB)": {
        "EN": "Genitourinary TB (EPTB)",
        "FR": "TB génito-urinaire (EPTB)",
        "SW": "TB ya mfumo wa mkojo na uzazi (EPTB)",
        "RW": "TB yo mu myanya ndangagitsina n'inkari (EPTB)",
    },
    "TB infection affecting kidneys, bladder, or reproductive organs": {
        "EN": "TB infection affecting kidneys, bladder, or reproductive organs",
        "FR": "Infection TB touchant les reins, la vessie ou les organes reproducteurs",
        "SW": "Maambukizi ya TB kwenye figo, kibofu, au viungo vya uzazi",
        "RW": "Ubwandu bwa TB bufata impyiko, uruhago cyangwa imyanya myibarukiro",
    },
    "Painful urination, blood in urine, pelvic pain, infertility": {
        "EN": "Painful urination, blood in urine, pelvic pain, infertility",
        "FR": "Douleur à la miction, sang dans les urines, douleur pelvienne, infertilité",
        "SW": "Maumivu wakati wa kukojoa, damu kwenye mkojo, maumivu ya nyonga, utasa",
        "RW": "Kubabara mu gihe cyo kunyara, amaraso mu nkari, ububabare mu nda yo hasi, kutabyara",
    },
    "Urine analysis and culture; 6-9 month regimen": {
        "EN": "Urine analysis and culture; 6-9 month regimen",
        "FR": "Analyse d'urine et culture; schéma de 6-9 mois",
        "SW": "Uchunguzi wa mkojo na culture; mpango wa miezi 6-9",
        "RW": "Isuzuma ry'inkari na culture; gahunda y'amezi 6-9",
    },
    "Abdominal TB (EPTB)": {
        "EN": "Abdominal TB (EPTB)",
        "FR": "TB abdominale (EPTB)",
        "SW": "TB ya tumbo (EPTB)",
        "RW": "TB yo mu nda (EPTB)",
    },
    "TB infection affecting intestines, peritoneum, or abdominal organs": {
        "EN": "TB infection affecting intestines, peritoneum, or abdominal organs",
        "FR": "Infection TB touchant les intestins, le péritoine ou les organes abdominaux",
        "SW": "Maambukizi ya TB kwenye utumbo, peritoneum au viungo vya tumboni",
        "RW": "Ubwandu bwa TB bufata amara, peritoneum cyangwa ibice byo mu nda",
    },
    "Abdominal pain, diarrhea, weight loss, abdominal swelling": {
        "EN": "Abdominal pain, diarrhea, weight loss, abdominal swelling",
        "FR": "Douleur abdominale, diarrhée, perte de poids, ballonnement abdominal",
        "SW": "Maumivu ya tumbo, kuhara, kupungua uzito, kuvimba kwa tumbo",
        "RW": "Kubabara mu nda, impiswi, kugabanuka ibiro, kubyimba inda",
    },
    "Imaging and biopsy; 6-9 month regimen": {
        "EN": "Imaging and biopsy; 6-9 month regimen",
        "FR": "Imagerie et biopsie; schéma de 6-9 mois",
        "SW": "Imaging na biopsy; mpango wa miezi 6-9",
        "RW": "Imaging na biopsy; gahunda y'amezi 6-9",
    },
    "Pleural TB (EPTB)": {
        "EN": "Pleural TB (EPTB)",
        "FR": "TB pleurale (EPTB)",
        "SW": "TB ya pleura (EPTB)",
        "RW": "TB yo ku gihu cy'ibihaha (EPTB)",
    },
    "TB infection of the pleura (lining around the lungs)": {
        "EN": "TB infection of the pleura (lining around the lungs)",
        "FR": "Infection TB de la plèvre (membrane autour des poumons)",
        "SW": "Maambukizi ya TB kwenye pleura (utando unaozunguka mapafu)",
        "RW": "Ubwandu bwa TB ku gihu cy'ibihaha (udutambaro tuzengurutse ibihaha)",
    },
    "Chest pain, shortness of breath, pleural effusion": {
        "EN": "Chest pain, shortness of breath, pleural effusion",
        "FR": "Douleur thoracique, essoufflement, épanchement pleural",
        "SW": "Maumivu ya kifua, upungufu wa pumzi, maji kwenye pleura",
        "RW": "Kubabara mu gituza, kubura umwuka, amazi ku gihu cy'ibihaha",
    },
    "Pleural fluid analysis; 6-month regimen": {
        "EN": "Pleural fluid analysis; 6-month regimen",
        "FR": "Analyse du liquide pleural; schéma de 6 mois",
        "SW": "Uchunguzi wa maji ya pleura; mpango wa miezi 6",
        "RW": "Isuzuma ry'amazi yo ku gihu cy'ibihaha; gahunda y'amezi 6",
    },
    "Extrapulmonary TB (EPTB)": {
        "EN": "Extrapulmonary TB (EPTB)",
        "FR": "TB extrapulmonaire (EPTB)",
        "SW": "TB iliyo nje ya mapafu (EPTB)",
        "RW": "TB yo hanze y'ibihaha (EPTB)",
    },
    "TB infection affecting organs other than the lungs": {
        "EN": "TB infection affecting organs other than the lungs",
        "FR": "Infection TB touchant des organes autres que les poumons",
        "SW": "Maambukizi ya TB kwenye viungo visivyo mapafu",
        "RW": "Ubwandu bwa TB bufata ibindi bice bitari ibihaha",
    },
    "Depends on affected organ": {
        "EN": "Depends on affected organ",
        "FR": "Dépend de l'organe atteint",
        "SW": "Hutegemea kiungo kilichoathirika",
        "RW": "Biterwa n'igice cy'umubiri cyafashwe",
    },
    "Evaluate for specific site of infection, consider surgical consultation": {
        "EN": "Evaluate for specific site of infection, consider surgical consultation",
        "FR": "Évaluer le site exact de l'infection, envisager une consultation chirurgicale",
        "SW": "Tathmini eneo maalum la maambukizi, fikiria ushauri wa upasuaji",
        "RW": "Suzuma aho ubwandu buri, kandi utekereze ku nama y'abaganga b'ububaga",
    },
    "Standard precautions unless also has PTB": {
        "EN": "Standard precautions unless also has PTB",
        "FR": "Précautions standard sauf s'il existe aussi une PTB",
        "SW": "Tahadhari za kawaida isipokuwa pia ana PTB",
        "RW": "Ingamba zisanzwe zo kwirinda keretse niba anafite PTB",
    },
    "Miliary TB (DISSEMINATED - LIFE THREATENING)": {
        "EN": "Miliary TB (DISSEMINATED - LIFE THREATENING)",
        "FR": "TB miliaire (disséminée - menace vitale)",
        "SW": "TB iliyosambaa mwilini (hatari kwa maisha)",
        "RW": "TB yakwirakwiriye mu mubiri (ishyira ubuzima mu kaga)",
    },
    "Severe form where TB spreads through bloodstream to many organs": {
        "EN": "Severe form where TB spreads through bloodstream to many organs",
        "FR": "Forme grave où la TB se propage par le sang à de nombreux organes",
        "SW": "Aina kali ambapo TB husambaa kupitia damu hadi viungo vingi",
        "RW": "Ni uburyo bukomeye aho TB ikwira mu maraso ikagera mu bice byinshi by'umubiri",
    },
    "High fever, severe weakness, weight loss, breathing difficulties": {
        "EN": "High fever, severe weakness, weight loss, breathing difficulties",
        "FR": "Forte fièvre, grande faiblesse, perte de poids, difficultés respiratoires",
        "SW": "Homa kali, udhaifu mkubwa, kupungua uzito, shida ya kupumua",
        "RW": "Umuriro mwinshi, intege nke nyinshi, kugabanuka ibiro, ikibazo cyo guhumeka",
    },
    "URGENT hospitalization and treatment; 9-12 month regimen": {
        "EN": "URGENT hospitalization and treatment; 9-12 month regimen",
        "FR": "Hospitalisation et traitement URGENTS; schéma de 9-12 mois",
        "SW": "Kulazwa na matibabu ya HARAKA; mpango wa miezi 9-12",
        "RW": "Kujyanwa kwa muganga no kuvurwa byihutirwa; gahunda y'amezi 9-12",
    },
    "Airborne precautions": {
        "EN": "Airborne precautions",
        "FR": "Précautions aériennes",
        "SW": "Tahadhari za hewani",
        "RW": "Ingamba zo kwirinda ubwandu bwo mu mwuka",
    },
    "TB/HIV Co-infection": {
        "EN": "TB/HIV Co-infection",
        "FR": "Co-infection TB/VIH",
        "SW": "Maambukizi ya TB na HIV kwa pamoja",
        "RW": "Ubwandu bwa TB na VIH icyarimwe",
    },
    "Dual infection with both TB and HIV - high risk of progression and complications": {
        "EN": "Dual infection with both TB and HIV - high risk of progression and complications",
        "FR": "Double infection TB/VIH - risque élevé d'aggravation et de complications",
        "SW": "Maambukizi ya TB na HIV pamoja - hatari kubwa ya kuongezeka na matatizo",
        "RW": "Ubwandu bwa TB na VIH icyarimwe - bufite ibyago byinshi byo gukomera no guteza ibibazo",
    },
    "Any TB symptoms plus HIV-related symptoms": {
        "EN": "Any TB symptoms plus HIV-related symptoms",
        "FR": "Tout symptôme de TB avec symptômes liés au VIH",
        "SW": "Dalili zo TB pamoja na dalili zinazohusiana na HIV",
        "RW": "Ibimenyetso bya TB hamwe n'ibindi bifitanye isano na VIH",
    },
    "Initiate ART within 2-8 weeks of starting TB treatment": {
        "EN": "Initiate ART within 2-8 weeks of starting TB treatment",
        "FR": "Commencer les ARV dans les 2-8 semaines après le début du traitement TB",
        "SW": "Anza ART ndani ya wiki 2-8 baada ya kuanza matibabu ya TB",
        "RW": "Tangira ART mu byumweru 2-8 nyuma yo gutangira kuvura TB",
    },
    "Comprehensive care, monitoring for IRIS": {
        "EN": "Comprehensive care, monitoring for IRIS",
        "FR": "Prise en charge globale, surveillance de l'IRIS",
        "SW": "Huduma ya kina, ufuatiliaji wa IRIS",
        "RW": "Kwita ku murwayi mu buryo bwuzuye no gukurikirana IRIS",
    },
    "Extensively Drug-Resistant TB (XDR-TB)": {
        "EN": "Extensively Drug-Resistant TB (XDR-TB)",
        "FR": "TB ultra-résistante (XDR-TB)",
        "SW": "TB yenye usugu mkubwa sana wa dawa (XDR-TB)",
        "RW": "TB ifite usugire bukabije ku miti (XDR-TB)",
    },
    "TB resistant to first-line, second-line, and additional drugs": {
        "EN": "TB resistant to first-line, second-line, and additional drugs",
        "FR": "TB résistante aux médicaments de première ligne, de deuxième ligne et autres",
        "SW": "TB yenye usugu kwa dawa za mstari wa kwanza, wa pili, na nyinginezo",
        "RW": "TB irwanya imiti y'umurongo wa mbere, uwa kabiri n'indi y'inyongera",
    },
    "Same as other TB, but fails to respond to standard treatment": {
        "EN": "Same as other TB, but fails to respond to standard treatment",
        "FR": "Comme les autres TB, mais ne répond pas au traitement standard",
        "SW": "Sawa na TB nyingine, lakini haiguswi na matibabu ya kawaida",
        "RW": "Imeze nk'izindi TB, ariko ntisubiza neza ku buvuzi busanzwe",
    },
    "Specialized XDR-TB center; individualized all-oral regimen": {
        "EN": "Specialized XDR-TB center; individualized all-oral regimen",
        "FR": "Centre spécialisé XDR-TB; schéma oral individualisé",
        "SW": "Kituo maalum cha XDR-TB; mpango wa dawa za kunywa uliobinafsishwa",
        "RW": "Ikigo cyihariye cya XDR-TB; gahunda y'ibinini byanditswe ku murwayi ku giti cye",
    },
    "Enhanced airborne precautions": {
        "EN": "Enhanced airborne precautions",
        "FR": "Précautions aériennes renforcées",
        "SW": "Tahadhari za hewani zilizoimarishwa",
        "RW": "Ingamba zikomeye zo kwirinda ubwandu bwo mu mwuka",
    },
    "Multidrug-Resistant TB (MDR-TB)": {
        "EN": "Multidrug-Resistant TB (MDR-TB)",
        "FR": "TB multirésistante (MDR-TB)",
        "SW": "TB yenye usugu kwa dawa nyingi (MDR-TB)",
        "RW": "TB irwanya imiti myinshi (MDR-TB)",
    },
    "TB resistant to at least Isoniazid and Rifampicin": {
        "EN": "TB resistant to at least Isoniazid and Rifampicin",
        "FR": "TB résistante au moins à l'isoniazide et à la rifampicine",
        "SW": "TB yenye usugu angalau kwa Isoniazid na Rifampicin",
        "RW": "TB irwanya nibura Isoniazid na Rifampicin",
    },
    "Same as other TB, but fails to respond to first-line drugs": {
        "EN": "Same as other TB, but fails to respond to first-line drugs",
        "FR": "Comme les autres TB, mais ne répond pas aux médicaments de première ligne",
        "SW": "Sawa na TB nyingine, lakini haitikii dawa za mstari wa kwanza",
        "RW": "Imeze nk'izindi TB, ariko ntisubiza ku miti y'umurongo wa mbere",
    },
    "Specialized DR-TB center; second-line regimen": {
        "EN": "Specialized DR-TB center; second-line regimen",
        "FR": "Centre spécialisé DR-TB; schéma de deuxième ligne",
        "SW": "Kituo maalum cha DR-TB; mpango wa mstari wa pili",
        "RW": "Ikigo cyihariye cya DR-TB; gahunda y'umurongo wa kabiri",
    },
    "Rifampicin-Resistant TB (RR-TB)": {
        "EN": "Rifampicin-Resistant TB (RR-TB)",
        "FR": "TB résistante à la rifampicine (RR-TB)",
        "SW": "TB yenye usugu wa rifampicin (RR-TB)",
        "RW": "TB irwanya rifampicin (RR-TB)",
    },
    "TB resistant to Rifampicin - often MDR-TB": {
        "EN": "TB resistant to Rifampicin - often MDR-TB",
        "FR": "TB résistante à la rifampicine - souvent MDR-TB",
        "SW": "TB yenye usugu kwa Rifampicin - mara nyingi huwa MDR-TB",
        "RW": "TB irwanya Rifampicin - akenshi iba MDR-TB",
    },
    "Same as other TB": {
        "EN": "Same as other TB",
        "FR": "Comme les autres TB",
        "SW": "Sawa na TB nyingine",
        "RW": "Imeze nk'izindi TB",
    },
    "Further testing for MDR-TB; second-line regimen": {
        "EN": "Further testing for MDR-TB; second-line regimen",
        "FR": "Tests complémentaires pour MDR-TB; schéma de deuxième ligne",
        "SW": "Vipimo zaidi kwa MDR-TB; mpango wa mstari wa pili",
        "RW": "Hakenewe ibindi bizamini bya MDR-TB; gahunda y'umurongo wa kabiri",
    },
    "Drug-Resistant TB (DR-TB)": {
        "EN": "Drug-Resistant TB (DR-TB)",
        "FR": "TB résistante aux médicaments (DR-TB)",
        "SW": "TB yenye usugu wa dawa (DR-TB)",
        "RW": "TB irwanya imiti (DR-TB)",
    },
    "TB strain resistant to first-line anti-TB drugs": {
        "EN": "TB strain resistant to first-line anti-TB drugs",
        "FR": "Souche de TB résistante aux médicaments anti-TB de première ligne",
        "SW": "Aina ya TB yenye usugu kwa dawa za kwanza za TB",
        "RW": "Ubwoko bwa TB burwanya imiti ya mbere ikoreshwa kuri TB",
    },
    "Refer to specialized DR-TB center for second-line treatment": {
        "EN": "Refer to specialized DR-TB center for second-line treatment",
        "FR": "Référer vers un centre spécialisé DR-TB pour le traitement de deuxième ligne",
        "SW": "Mpeleke kwenye kituo maalum cha DR-TB kwa matibabu ya mstari wa pili",
        "RW": "Mwohereze ku kigo cyihariye cya DR-TB kugira ngo ahabwe ubuvuzi bw'umurongo wa kabiri",
    },
    "Drug-Sensitive TB (DS-TB)": {
        "EN": "Drug-Sensitive TB (DS-TB)",
        "FR": "TB sensible aux médicaments (DS-TB)",
        "SW": "TB inayoitikia dawa (DS-TB)",
        "RW": "TB yumva imiti (DS-TB)",
    },
    "TB strain treatable with standard first-line anti-TB drugs": {
        "EN": "TB strain treatable with standard first-line anti-TB drugs",
        "FR": "Souche de TB traitable avec les médicaments standards de première ligne",
        "SW": "Aina ya TB inayoweza kutibiwa kwa dawa za kawaida za mstari wa kwanza",
        "RW": "Ubwoko bwa TB bushobora kuvurwa n'imiti isanzwe y'umurongo wa mbere",
    },
    "Start standard first-line regimen (2HRZE/4HR) with DOT": {
        "EN": "Start standard first-line regimen (2HRZE/4HR) with DOT",
        "FR": "Commencer le schéma standard de première ligne (2HRZE/4HR) avec DOT",
        "SW": "Anza mpango wa kawaida wa mstari wa kwanza (2HRZE/4HR) na DOT",
        "RW": "Tangira gahunda isanzwe y'umurongo wa mbere (2HRZE/4HR) hamwe na DOT",
    },
    "Standard airborne precautions": {
        "EN": "Standard airborne precautions",
        "FR": "Précautions aériennes standard",
        "SW": "Tahadhari za kawaida za hewani",
        "RW": "Ingamba zisanzwe zo kwirinda ubwandu bwo mu mwuka",
    },
    "Latent TB Infection (LTBI)": {
        "EN": "Latent TB Infection (LTBI)",
        "FR": "Infection tuberculeuse latente (LTBI)",
        "SW": "Maambukizi fiche ya TB (LTBI)",
        "RW": "Ubwandu bwa TB butaragaragara (LTBI)",
    },
    "TB bacteria are present but inactive; no symptoms and not contagious": {
        "EN": "TB bacteria are present but inactive; no symptoms and not contagious",
        "FR": "Les bactéries TB sont présentes mais inactives; pas de symptômes et pas contagieuse",
        "SW": "Bakteria wa TB wapo lakini hawafanyi kazi; hakuna dalili na haiambukizi",
        "RW": "Bagiteri za TB zirahari ariko zituje; nta bimenyetso kandi ntibyanduza",
    },
    "No symptoms": {
        "EN": "No symptoms",
        "FR": "Aucun symptôme",
        "SW": "Hakuna dalili",
        "RW": "Nta bimenyetso",
    },
    "Preventive therapy to prevent progression to active TB": {
        "EN": "Preventive therapy to prevent progression to active TB",
        "FR": "Traitement préventif pour éviter l'évolution vers une TB active",
        "SW": "Matibabu kinga ili kuzuia kugeuka kuwa TB hai",
        "RW": "Umuti wo gukumira kugira ngo bidahinduka TB ikora",
    },
    "None - not contagious": {
        "EN": "None - not contagious",
        "FR": "Aucune - non contagieuse",
        "SW": "Hakuna - haiambukizi",
        "RW": "Nta na kimwe - ntibyanduza",
    },
    "Presumptive TB Case": {
        "EN": "Presumptive TB Case",
        "FR": "Cas présumé de TB",
        "SW": "Kesi inayoshukiwa kuwa TB",
        "RW": "Urubanza rukekwamo TB",
    },
    "Has TB symptoms but not yet confirmed by testing": {
        "EN": "Has TB symptoms but not yet confirmed by testing",
        "FR": "Présente des symptômes de TB mais pas encore confirmés par les tests",
        "SW": "Ana dalili za TB lakini bado hajathibitishwa kwa vipimo",
        "RW": "Agaragaza ibimenyetso bya TB ariko ntibiracyemezwa n'ibizamini",
    },
    "Any combination of: cough ≥2 weeks, fever, night sweats, weight loss, hemoptysis": {
        "EN": "Any combination of: cough >=2 weeks, fever, night sweats, weight loss, hemoptysis",
        "FR": "Toute combinaison de : toux >=2 semaines, fièvre, sueurs nocturnes, perte de poids, hémoptysie",
        "SW": "Mchanganyiko wowote wa: kikohozi cha wiki 2 au zaidi, homa, jasho la usiku, kupungua uzito, kukohoa damu",
        "RW": "Ihuriro iryo ari ryo ryose ry'ibi: inkorora y'ibyumweru 2 cyangwa birenga, umuriro, kubira ibyuya nijoro, kugabanuka ibiro, gukorora amaraso",
    },
    "Complete diagnostic workup (sputum smear, GeneXpert, chest X-ray)": {
        "EN": "Complete diagnostic workup (sputum smear, GeneXpert, chest X-ray)",
        "FR": "Compléter le bilan diagnostique (frottis sputum, GeneXpert, radiographie thoracique)",
        "SW": "Kamilisha uchunguzi wote (sputum smear, GeneXpert, X-ray ya kifua)",
        "RW": "Kora isuzuma ryose rikenewe (sputum smear, GeneXpert, X-ray y'igituza)",
    },
    "Precautions while pending diagnosis": {
        "EN": "Precautions while pending diagnosis",
        "FR": "Précautions en attendant le diagnostic",
        "SW": "Tahadhari wakati uchunguzi bado unasubiriwa",
        "RW": "Ingamba zo kwirinda mu gihe igisubizo kigitegerejwe",
    },
    "No Evidence of TB": {
        "EN": "No Evidence of TB",
        "FR": "Aucune preuve de TB",
        "SW": "Hakuna ushahidi wa TB",
        "RW": "Nta bimenyetso bya TB",
    },
    "Clinical picture not suggestive of TB": {
        "EN": "Clinical picture not suggestive of TB",
        "FR": "Le tableau clinique n'évoque pas une TB",
        "SW": "Muonekano wa ugonjwa hauonyeshi TB",
        "RW": "Isura y'uburwayi ntigaragaza ko ari TB",
    },
    "No TB-specific symptoms": {
        "EN": "No TB-specific symptoms",
        "FR": "Aucun symptôme spécifique de TB",
        "SW": "Hakuna dalili maalum za TB",
        "RW": "Nta bimenyetso byihariye bya TB",
    },
    "Monitor symptoms, consider other diagnoses": {
        "EN": "Monitor symptoms, consider other diagnoses",
        "FR": "Surveiller les symptômes, envisager d'autres diagnostics",
        "SW": "Fuatilia dalili, fikiria magonjwa mengine",
        "RW": "Kurikirana ibimenyetso kandi utekereze ku zindi ndwara",
    },
    "None": {"EN": "None", "FR": "Aucun", "SW": "Hakuna", "RW": "Nta na kimwe"},
    "XDR-TB Regimen": {
        "EN": "XDR-TB Regimen",
        "FR": "Schéma XDR-TB",
        "SW": "Mpango wa XDR-TB",
        "RW": "Gahunda ya XDR-TB",
    },
    "18-24 months total": {
        "EN": "18-24 months total",
        "FR": "18-24 mois au total",
        "SW": "Miezi 18-24 kwa jumla",
        "RW": "Amezi 18-24 yose hamwe",
    },
    "6-8 months": {"EN": "6-8 months", "FR": "6-8 mois", "SW": "Miezi 6-8", "RW": "Amezi 6-8"},
    "12-16 months": {"EN": "12-16 months", "FR": "12-16 mois", "SW": "Miezi 12-16", "RW": "Amezi 12-16"},
    "Individualized based on DST: Bedaquiline, Linezolid, Clofazimine, Fluoroquinolone, Cycloserine, plus additional agents": {
        "EN": "Individualized based on DST: Bedaquiline, Linezolid, Clofazimine, Fluoroquinolone, Cycloserine, plus additional agents",
        "FR": "Personnalisé selon le DST : Bedaquiline, Linezolid, Clofazimine, Fluoroquinolone, Cycloserine, plus autres agents",
        "SW": "Hubinafsishwa kulingana na DST: Bedaquiline, Linezolid, Clofazimine, Fluoroquinolone, Cycloserine, pamoja na dawa nyingine",
        "RW": "Ihuzwa n'ibisubizo bya DST: Bedaquiline, Linezolid, Clofazimine, Fluoroquinolone, Cycloserine n'indi miti y'inyongera",
    },
    "WHO recommends all-oral XDR-TB regimens; close monitoring for adverse effects": {
        "EN": "WHO recommends all-oral XDR-TB regimens; close monitoring for adverse effects",
        "FR": "L'OMS recommande des schémas XDR-TB tout oraux; surveillance étroite des effets indésirables",
        "SW": "WHO inapendekeza mipango ya XDR-TB ya dawa za kunywa pekee; fuatilia madhara kwa karibu",
        "RW": "OMS isaba gahunda za XDR-TB zikoresha ibinini gusa; hakurikiranywe neza ingaruka mbi",
    },
    "MDR-TB Regimen (Second-line)": {
        "EN": "MDR-TB Regimen (Second-line)",
        "FR": "Schéma MDR-TB (deuxième ligne)",
        "SW": "Mpango wa MDR-TB (mstari wa pili)",
        "RW": "Gahunda ya MDR-TB (umurongo wa kabiri)",
    },
    "6-8 months with at least 5 drugs": {
        "EN": "6-8 months with at least 5 drugs",
        "FR": "6-8 mois avec au moins 5 médicaments",
        "SW": "Miezi 6-8 na angalau dawa 5",
        "RW": "Amezi 6-8 harimo nibura imiti 5",
    },
    "12-16 months with at least 4 drugs": {
        "EN": "12-16 months with at least 4 drugs",
        "FR": "12-16 mois avec au moins 4 médicaments",
        "SW": "Miezi 12-16 na angalau dawa 4",
        "RW": "Amezi 12-16 harimo nibura imiti 4",
    },
    "Based on DST: Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine + other agents": {
        "EN": "Based on DST: Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine + other agents",
        "FR": "Selon le DST : Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine + autres agents",
        "SW": "Kulingana na DST: Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine + dawa nyingine",
        "RW": "Bishingiye kuri DST: Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine + indi miti",
    },
    "WHO recommends all-oral MDR-TB regimens when possible; Directly Observed Therapy (DOT) mandatory": {
        "EN": "WHO recommends all-oral MDR-TB regimens when possible; Directly Observed Therapy (DOT) mandatory",
        "FR": "L'OMS recommande des schémas MDR-TB tout oraux si possible; DOT obligatoire",
        "SW": "WHO inapendekeza mipango ya MDR-TB ya dawa za kunywa inapowezekana; DOT ni lazima",
        "RW": "OMS isaba gahunda za MDR-TB zikoresha ibinini gusa igihe bishoboka; DOT ni ngombwa",
    },
    "RR-TB Regimen": {"EN": "RR-TB Regimen", "FR": "Schéma RR-TB", "SW": "Mpango wa RR-TB", "RW": "Gahunda ya RR-TB"},
    "Based on DST, similar to MDR-TB": {
        "EN": "Based on DST, similar to MDR-TB",
        "FR": "Basé sur le DST, similaire au MDR-TB",
        "SW": "Inategemea DST, sawa na MDR-TB",
        "RW": "Bishingiye kuri DST, bisa na MDR-TB",
    },
    "Rule out MDR-TB with further testing; refer to DR-TB center": {
        "EN": "Rule out MDR-TB with further testing; refer to DR-TB center",
        "FR": "Éliminer un MDR-TB par des tests complémentaires; référer au centre DR-TB",
        "SW": "Ondoa uwezekano wa MDR-TB kwa vipimo zaidi; mpeleke kituo cha DR-TB",
        "RW": "Kuraho cyangwa kwemeza MDR-TB hifashishijwe ibindi bizamini; mwohereze ku kigo cya DR-TB",
    },
    "Second-line anti-TB drugs": {
        "EN": "Second-line anti-TB drugs",
        "FR": "Médicaments anti-TB de deuxième ligne",
        "SW": "Dawa za TB za mstari wa pili",
        "RW": "Imiti ya TB yo ku murongo wa kabiri",
    },
    "Based on DST: Fluoroquinolone + Injectable + Bedaquiline + Linezolid + Clofazimine + Cycloserine": {
        "EN": "Based on DST: Fluoroquinolone + Injectable + Bedaquiline + Linezolid + Clofazimine + Cycloserine",
        "FR": "Selon le DST : Fluoroquinolone + injectable + Bedaquiline + Linezolid + Clofazimine + Cycloserine",
        "SW": "Kulingana na DST: Fluoroquinolone + sindano + Bedaquiline + Linezolid + Clofazimine + Cycloserine",
        "RW": "Bishingiye kuri DST: Fluoroquinolone + umuti uterwa + Bedaquiline + Linezolid + Clofazimine + Cycloserine",
    },
    "WHO recommends individualized treatment based on DST; use all-oral regimens when possible": {
        "EN": "WHO recommends individualized treatment based on DST; use all-oral regimens when possible",
        "FR": "L'OMS recommande un traitement individualisé selon le DST; utiliser des schémas oraux si possible",
        "SW": "WHO inapendekeza matibabu yaliyobinafsishwa kulingana na DST; tumia mipango ya dawa za kunywa inapowezekana",
        "RW": "OMS isaba ubuvuzi bujyanye n'ibisubizo bya DST; ukoreshe gahunda z'ibinini gusa igihe bishoboka",
    },
    "First-line TB treatment + ART": {
        "EN": "First-line TB treatment + ART",
        "FR": "Traitement TB de première ligne + ARV",
        "SW": "Matibabu ya TB ya mstari wa kwanza + ART",
        "RW": "Umuti wa TB wo ku murongo wa mbere + ART",
    },
    "6 months": {"EN": "6 months", "FR": "6 mois", "SW": "Miezi 6", "RW": "Amezi 6"},
    "2 months (HRZE)": {"EN": "2 months (HRZE)", "FR": "2 mois (HRZE)", "SW": "Miezi 2 (HRZE)", "RW": "Amezi 2 (HRZE)"},
    "4 months (HR)": {"EN": "4 months (HR)", "FR": "4 mois (HR)", "SW": "Miezi 4 (HR)", "RW": "Amezi 4 (HR)"},
    "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); ART within 2-8 weeks": {
        "EN": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); ART within 2-8 weeks",
        "FR": "Isoniazide (H) + Rifampicine (R) + Pyrazinamide (Z) + Ethambutol (E); ARV dans les 2-8 semaines",
        "SW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); ART ndani ya wiki 2-8",
        "RW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); ART mu byumweru 2-8",
    },
    "EFV-based ART; Pyridoxine 25-50mg/day to prevent neuropathy; monitor for Immune Reconstitution Inflammatory Syndrome (IRIS)": {
        "EN": "EFV-based ART; Pyridoxine 25-50mg/day to prevent neuropathy; monitor for Immune Reconstitution Inflammatory Syndrome (IRIS)",
        "FR": "ARV à base d'EFV; Pyridoxine 25-50mg/jour pour prévenir la neuropathie; surveiller l'IRIS",
        "SW": "ART ya msingi wa EFV; Pyridoxine 25-50mg/siku kuzuia neuropathy; fuatilia IRIS",
        "RW": "ART ishingiye kuri EFV; Pyridoxine 25-50mg ku munsi mu gukumira neuropathy; kurikirana IRIS",
    },
    "Standard First-line + Steroids": {
        "EN": "Standard First-line + Steroids",
        "FR": "Première ligne standard + corticoïdes",
        "SW": "Mstari wa kwanza wa kawaida + steroids",
        "RW": "Umurongo wa mbere usanzwe + steroids",
    },
    "9-12 months total": {
        "EN": "9-12 months total",
        "FR": "9-12 mois au total",
        "SW": "Miezi 9-12 kwa jumla",
        "RW": "Amezi 9-12 yose hamwe",
    },
    "2-3 months (HRZE)": {"EN": "2-3 months (HRZE)", "FR": "2-3 mois (HRZE)", "SW": "Miezi 2-3 (HRZE)", "RW": "Amezi 2-3 (HRZE)"},
    "7-9 months (HR)": {"EN": "7-9 months (HR)", "FR": "7-9 mois (HR)", "SW": "Miezi 7-9 (HR)", "RW": "Amezi 7-9 (HR)"},
    "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); consider adjunctive steroids": {
        "EN": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); consider adjunctive steroids",
        "FR": "Isoniazide (H) + Rifampicine (R) + Pyrazinamide (Z) + Ethambutol (E); envisager des corticoïdes adjuvants",
        "SW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); fikiria steroids za ziada",
        "RW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); tekereza kuri steroids zunganira",
    },
    "Hospitalization required; monitor closely for complications; Pyridoxine 25-50mg/day": {
        "EN": "Hospitalization required; monitor closely for complications; Pyridoxine 25-50mg/day",
        "FR": "Hospitalisation nécessaire; surveillance étroite des complications; Pyridoxine 25-50mg/jour",
        "SW": "Kulazwa kunahitajika; fuatilia matatizo kwa karibu; Pyridoxine 25-50mg/siku",
        "RW": "Gukenera kuryazwa; kurikirana ibibazo bya hafi; Pyridoxine 25-50mg ku munsi",
    },
    "First-line + Steroids": {
        "EN": "First-line + Steroids",
        "FR": "Première ligne + corticoïdes",
        "SW": "Mstari wa kwanza + steroids",
        "RW": "Umurongo wa mbere + steroids",
    },
    "12 months total": {"EN": "12 months total", "FR": "12 mois au total", "SW": "Miezi 12 kwa jumla", "RW": "Amezi 12 yose hamwe"},
    "9-10 months (HR)": {"EN": "9-10 months (HR)", "FR": "9-10 mois (HR)", "SW": "Miezi 9-10 (HR)", "RW": "Amezi 9-10 (HR)"},
    "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); Adjunctive corticosteroids": {
        "EN": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); Adjunctive corticosteroids",
        "FR": "Isoniazide (H) + Rifampicine (R) + Pyrazinamide (Z) + Ethambutol (E); corticoïdes adjuvants",
        "SW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); corticosteroids za ziada",
        "RW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E); corticosteroids zunganira",
    },
    "URGENT hospitalization; lumbar puncture; high-dose steroids early; Pyridoxine 50-100mg/day": {
        "EN": "URGENT hospitalization; lumbar puncture; high-dose steroids early; Pyridoxine 50-100mg/day",
        "FR": "Hospitalisation URGENTE; ponction lombaire; fortes doses de corticoïdes précoces; Pyridoxine 50-100mg/jour",
        "SW": "Kulazwa HARAKA; lumbar puncture; steroids dozi kubwa mapema; Pyridoxine 50-100mg/siku",
        "RW": "Kuryazwa byihutirwa; lumbar puncture; gutanga steroids nyinshi kare; Pyridoxine 50-100mg ku munsi",
    },
    "Standard First-line": {
        "EN": "Standard First-line",
        "FR": "Première ligne standard",
        "SW": "Mstari wa kwanza wa kawaida",
        "RW": "Umurongo wa mbere usanzwe",
    },
    "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E)": {
        "EN": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E)",
        "FR": "Isoniazide (H) + Rifampicine (R) + Pyrazinamide (Z) + Ethambutol (E)",
        "SW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E)",
        "RW": "Isoniazid (H) + Rifampicin (R) + Pyrazinamide (Z) + Ethambutol (E)",
    },
    "Consider orthopedic consultation; surgical intervention may be needed; Pyridoxine 25-50mg/day": {
        "EN": "Consider orthopedic consultation; surgical intervention may be needed; Pyridoxine 25-50mg/day",
        "FR": "Envisager une consultation orthopédique; une chirurgie peut être nécessaire; Pyridoxine 25-50mg/jour",
        "SW": "Fikiria ushauri wa daktari wa mifupa; upasuaji unaweza kuhitajika; Pyridoxine 25-50mg/siku",
        "RW": "Tekereza ku nama y'umuganga w'amagufa; kubagwa bishobora gukenerwa; Pyridoxine 25-50mg ku munsi",
    },
    "WHO Standard First-line Treatment (2HRZE/4HR)": {
        "EN": "WHO Standard First-line Treatment (2HRZE/4HR)",
        "FR": "Traitement standard OMS de première ligne (2HRZE/4HR)",
        "SW": "Matibabu ya kawaida ya WHO ya mstari wa kwanza (2HRZE/4HR)",
        "RW": "Ubuvuzi busanzwe bwa OMS bwo ku murongo wa mbere (2HRZE/4HR)",
    },
    "2 months (Isoniazid + Rifampicin + Pyrazinamide + Ethambutol)": {
        "EN": "2 months (Isoniazid + Rifampicin + Pyrazinamide + Ethambutol)",
        "FR": "2 mois (Isoniazide + Rifampicine + Pyrazinamide + Ethambutol)",
        "SW": "Miezi 2 (Isoniazid + Rifampicin + Pyrazinamide + Ethambutol)",
        "RW": "Amezi 2 (Isoniazid + Rifampicin + Pyrazinamide + Ethambutol)",
    },
    "4 months (Isoniazid + Rifampicin)": {
        "EN": "4 months (Isoniazid + Rifampicin)",
        "FR": "4 mois (Isoniazide + Rifampicine)",
        "SW": "Miezi 4 (Isoniazid + Rifampicin)",
        "RW": "Amezi 4 (Isoniazid + Rifampicin)",
    },
    "Isoniazid (H) 5mg/kg/day, Rifampicin (R) 10mg/kg/day, Pyrazinamide (Z) 25mg/kg/day, Ethambutol (E) 15-20mg/kg/day": {
        "EN": "Isoniazid (H) 5mg/kg/day, Rifampicin (R) 10mg/kg/day, Pyrazinamide (Z) 25mg/kg/day, Ethambutol (E) 15-20mg/kg/day",
        "FR": "Isoniazide (H) 5mg/kg/jour, Rifampicine (R) 10mg/kg/jour, Pyrazinamide (Z) 25mg/kg/jour, Ethambutol (E) 15-20mg/kg/jour",
        "SW": "Isoniazid (H) 5mg/kg/siku, Rifampicin (R) 10mg/kg/siku, Pyrazinamide (Z) 25mg/kg/siku, Ethambutol (E) 15-20mg/kg/siku",
        "RW": "Isoniazid (H) 5mg/kg/umunsi, Rifampicin (R) 10mg/kg/umunsi, Pyrazinamide (Z) 25mg/kg/umunsi, Ethambutol (E) 15-20mg/kg/umunsi",
    },
    "WHO recommends Directly Observed Treatment (DOT) to ensure adherence; Pyridoxine 25-50mg/day to prevent peripheral neuropathy; monitor LFTs monthly": {
        "EN": "WHO recommends Directly Observed Treatment (DOT) to ensure adherence; Pyridoxine 25-50mg/day to prevent peripheral neuropathy; monitor LFTs monthly",
        "FR": "L'OMS recommande le traitement directement observé (DOT) pour assurer l'adhérence; Pyridoxine 25-50mg/jour pour prévenir la neuropathie périphérique; surveiller les tests hépatiques chaque mois",
        "SW": "WHO inapendekeza DOT kuhakikisha ufuasi; Pyridoxine 25-50mg/siku kuzuia neuropathy ya pembeni; fuatilia vipimo vya ini kila mwezi",
        "RW": "OMS isaba DOT kugira ngo umuti ufatwe neza; Pyridoxine 25-50mg ku munsi mu gukumira neuropathy yo ku mpera z'imyakura; ukurikirane ibizamini by'umwijima buri kwezi",
    },
    "6-12 months depending on site": {
        "EN": "6-12 months depending on site",
        "FR": "6-12 mois selon le site atteint",
        "SW": "Miezi 6-12 kutegemea eneo lililoathirika",
        "RW": "Amezi 6-12 bitewe n'aho indwara iri",
    },
    "4-10 months (HR)": {"EN": "4-10 months (HR)", "FR": "4-10 mois (HR)", "SW": "Miezi 4-10 (HR)", "RW": "Amezi 4-10 (HR)"},
    "Duration depends on specific site of EPTB (6 months for most, 9-12 for bone/joint/meningitis); Pyridoxine 25-50mg/day": {
        "EN": "Duration depends on specific site of EPTB (6 months for most, 9-12 for bone/joint/meningitis); Pyridoxine 25-50mg/day",
        "FR": "La durée dépend du site précis de l'EPTB (6 mois pour la plupart, 9-12 pour os/articulations/méningite); Pyridoxine 25-50mg/jour",
        "SW": "Muda hutegemea eneo la EPTB (miezi 6 kwa wengi, 9-12 kwa mifupa/viungo/meningitis); Pyridoxine 25-50mg/siku",
        "RW": "Igihe cyo kuvura giterwa n'aho EPTB iri (amezi 6 kuri benshi, 9-12 ku magufa/ingingo/meningitis); Pyridoxine 25-50mg ku munsi",
    },
    "LTBI Preventive Therapy": {
        "EN": "LTBI Preventive Therapy",
        "FR": "Traitement préventif LTBI",
        "SW": "Matibabu kinga ya LTBI",
        "RW": "Ubuvuzi bwo gukumira LTBI",
    },
    "3-9 months depending on regimen": {
        "EN": "3-9 months depending on regimen",
        "FR": "3-9 mois selon le schéma",
        "SW": "Miezi 3-9 kutegemea mpango",
        "RW": "Amezi 3-9 bitewe na gahunda",
    },
    "Options: Isoniazid 300mg/day for 6-9 months; Isoniazid + Rifapentine weekly for 3 months; Rifampicin 600mg/day for 4 months": {
        "EN": "Options: Isoniazid 300mg/day for 6-9 months; Isoniazid + Rifapentine weekly for 3 months; Rifampicin 600mg/day for 4 months",
        "FR": "Options : Isoniazide 300mg/jour pendant 6-9 mois; Isoniazide + Rifapentine chaque semaine pendant 3 mois; Rifampicine 600mg/jour pendant 4 mois",
        "SW": "Chaguo: Isoniazid 300mg/siku kwa miezi 6-9; Isoniazid + Rifapentine kila wiki kwa miezi 3; Rifampicin 600mg/siku kwa miezi 4",
        "RW": "Amahitamo: Isoniazid 300mg ku munsi mu mezi 6-9; Isoniazid + Rifapentine buri cyumweru mu mezi 3; Rifampicin 600mg ku munsi mu mezi 4",
    },
    "WHO recommends LTBI treatment for people at high risk of progression to active TB; monitor LFTs": {
        "EN": "WHO recommends LTBI treatment for people at high risk of progression to active TB; monitor LFTs",
        "FR": "L'OMS recommande le traitement LTBI pour les personnes à haut risque d'évolution vers une TB active; surveiller les tests hépatiques",
        "SW": "WHO inapendekeza matibabu ya LTBI kwa watu walio katika hatari kubwa ya kupata TB hai; fuatilia vipimo vya ini",
        "RW": "OMS isaba kuvura LTBI ku bantu bafite ibyago byinshi byo kugira TB ikora; ukurikirane ibizamini by'umwijima",
    },
    "MODERATE (high-risk individuals only)": {
        "EN": "MODERATE (high-risk individuals only)",
        "FR": "MODÉRÉ (personnes à haut risque uniquement)",
        "SW": "KATI (kwa walio hatarini sana tu)",
        "RW": "IKIGERO CYO HAGATI (ku bafite ibyago byinshi gusa)",
    },
    "OBSERVATION AND FURTHER TESTING": {
        "EN": "OBSERVATION AND FURTHER TESTING",
        "FR": "OBSERVATION ET TESTS SUPPLÉMENTAIRES",
        "SW": "UFUATILIAJI NA VIPIMO ZAIDI",
        "RW": "GUKURIKIRANA N'IBINDI BIZAMINI",
    },
    "N/A": {"EN": "N/A", "FR": "N/A", "SW": "N/A", "RW": "N/A"},
    "No anti-TB treatment unless clinical suspicion remains high": {
        "EN": "No anti-TB treatment unless clinical suspicion remains high",
        "FR": "Pas de traitement anti-TB sauf si la suspicion clinique reste forte",
        "SW": "Hakuna matibabu ya TB isipokuwa shaka ya kitabibu ibaki kubwa",
        "RW": "Nta muti wa TB utangwa keretse ugukeka kwa muganga kugumye kuba hejuru",
    },
    "Monitor closely, repeat tests as indicated, evaluate for alternative diagnoses": {
        "EN": "Monitor closely, repeat tests as indicated, evaluate for alternative diagnoses",
        "FR": "Surveiller de près, répéter les tests si nécessaire, évaluer d'autres diagnostics",
        "SW": "Fuatilia kwa karibu, rudia vipimo inapohitajika, tathmini magonjwa mengine",
        "RW": "Kurikirana hafi, subiramo ibizamini igihe bikenewe, usuzume izindi ndwara zishoboka",
    },
    "WHO-aligned XDR-TB individualized regimen": {
        "EN": "WHO-aligned XDR-TB individualized regimen",
        "FR": "Schéma individualisé XDR-TB aligné sur l'OMS",
        "SW": "Mpango wa XDR-TB uliobinafsishwa unaolingana na WHO",
        "RW": "Gahunda ya XDR-TB ihuye na OMS kandi ikorwa hakurikijwe umurwayi",
    },
    "18-24 months": {"EN": "18-24 months", "FR": "18-24 mois", "SW": "Miezi 18-24", "RW": "Amezi 18-24"},
    "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + additional active agents guided by DST": {
        "EN": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + additional active agents guided by DST",
        "FR": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + autres agents actifs guidés par le DST",
        "SW": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + dawa nyingine zinazofaa kulingana na DST",
        "RW": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + indi miti ihitwamo hashingiwe kuri DST",
    },
    "Daily supervised treatment under specialist DR-TB care; all-oral regimen preferred.": {
        "EN": "Daily supervised treatment under specialist DR-TB care; all-oral regimen preferred.",
        "FR": "Traitement quotidien supervisé sous soins spécialisés DR-TB; schéma oral préféré.",
        "SW": "Matibabu ya kila siku chini ya uangalizi wa mtaalamu wa DR-TB; dawa za kunywa hupendelewa.",
        "RW": "Ubuvuzi bwa buri munsi bukurikiranwa n'inzobere ya DR-TB; hakundwa gahunda y'ibinini gusa.",
    },
    "Monthly clinical review, ECG where indicated, liver tests, neuropathy and hematology monitoring.": {
        "EN": "Monthly clinical review, ECG where indicated, liver tests, neuropathy and hematology monitoring.",
        "FR": "Revue clinique mensuelle, ECG si indiqué, tests hépatiques, suivi neuropathique et hématologique.",
        "SW": "Mapitio ya kliniki kila mwezi, ECG inapohitajika, vipimo vya ini, ufuatiliaji wa neuropathy na damu.",
        "RW": "Isuzuma rya kwa muganga buri kwezi, ECG aho bikenewe, ibizamini by'umwijima, gukurikirana neuropathy n'amaraso.",
    },
    "Must be individualized from DST/antibiogram and WHO DR-TB guidance.": {
        "EN": "Must be individualized from DST/antibiogram and WHO DR-TB guidance.",
        "FR": "Doit être individualisé selon le DST/antibiogramme et les directives OMS DR-TB.",
        "SW": "Lazima ubinafsishwe kulingana na DST/antibiogram na miongozo ya WHO ya DR-TB.",
        "RW": "Igomba kugenwa hashingiwe kuri DST/antibiogram n'amabwiriza ya OMS ya DR-TB.",
    },
    "WHO MDR-TB second-line regimen": {
        "EN": "WHO MDR-TB second-line regimen",
        "FR": "Schéma OMS MDR-TB de deuxième ligne",
        "SW": "Mpango wa WHO wa MDR-TB wa mstari wa pili",
        "RW": "Gahunda ya OMS ya MDR-TB yo ku murongo wa kabiri",
    },
    "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine / other active drugs": {
        "EN": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine / other active drugs",
        "FR": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine / autres médicaments actifs",
        "SW": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine / dawa nyingine zinazofaa",
        "RW": "Bedaquiline + Linezolid + Clofazimine + Fluoroquinolone + Cycloserine / indi miti ikora",
    },
    "Daily supervised treatment, preferably all-oral, with DR-TB specialist oversight.": {
        "EN": "Daily supervised treatment, preferably all-oral, with DR-TB specialist oversight.",
        "FR": "Traitement quotidien supervisé, de préférence oral, sous contrôle d'un spécialiste DR-TB.",
        "SW": "Matibabu ya kila siku chini ya uangalizi, ikiwezekana dawa za kunywa, kwa usimamizi wa mtaalamu wa DR-TB.",
        "RW": "Ubuvuzi bwa buri munsi bukurikiranwa, byiza hakoreshejwe ibinini gusa, buyobowe n'inzobere ya DR-TB.",
    },
    "Frequent DST review, toxicity review, liver/kidney tests, ECG, adherence tracking.": {
        "EN": "Frequent DST review, toxicity review, liver/kidney tests, ECG, adherence tracking.",
        "FR": "Révision fréquente du DST, de la toxicité, tests foie/reins, ECG et suivi de l'adhérence.",
        "SW": "Mapitio ya mara kwa mara ya DST, sumu ya dawa, vipimo vya ini/figo, ECG, na ufuatiliaji wa ufuasi.",
        "RW": "Gusubiramo DST kenshi, kureba uburozi bw'imiti, ibizamini by'umwijima/impyiko, ECG no gukurikirana uko umuti ufatwa.",
    },
    "WHO RR/DR-TB regimen": {
        "EN": "WHO RR/DR-TB regimen",
        "FR": "Schéma OMS RR/DR-TB",
        "SW": "Mpango wa WHO wa RR/DR-TB",
        "RW": "Gahunda ya OMS ya RR/DR-TB",
    },
    "Second-line anti-TB regimen selected from DST-active medicines": {
        "EN": "Second-line anti-TB regimen selected from DST-active medicines",
        "FR": "Schéma anti-TB de deuxième ligne choisi selon les médicaments actifs au DST",
        "SW": "Mpango wa TB wa mstari wa pili uliochaguliwa kutoka dawa zinazofaa kwenye DST",
        "RW": "Gahunda ya TB yo ku murongo wa kabiri ihitwamo imiti igaragara ko ikora muri DST",
    },
    "Daily supervised treatment under a DR-TB protocol.": {
        "EN": "Daily supervised treatment under a DR-TB protocol.",
        "FR": "Traitement quotidien supervisé selon un protocole DR-TB.",
        "SW": "Matibabu ya kila siku chini ya uangalizi kwa itifaki ya DR-TB.",
        "RW": "Ubuvuzi bwa buri munsi bukurikiranwa hakurikijwe protocole ya DR-TB.",
    },
    "Repeat DST, adverse-effect monitoring, adherence checks, and specialist review.": {
        "EN": "Repeat DST, adverse-effect monitoring, adherence checks, and specialist review.",
        "FR": "Répéter le DST, surveiller les effets indésirables, vérifier l'adhérence et revoir par un spécialiste.",
        "SW": "Rudia DST, fuatilia madhara, kagua ufuasi, na upitiwe na mtaalamu.",
        "RW": "Subiramo DST, ukurikirane ingaruka mbi, ugenzure uko umuti ufatwa, kandi usubirwe n'inzobere.",
    },
    "Escalate to MDR/XDR protocol if additional resistance is confirmed.": {
        "EN": "Escalate to MDR/XDR protocol if additional resistance is confirmed.",
        "FR": "Passer au protocole MDR/XDR si une résistance supplémentaire est confirmée.",
        "SW": "Hamia kwenye itifaki ya MDR/XDR ikiwa usugu mwingine utathibitishwa.",
        "RW": "Jya kuri protocole ya MDR/XDR niba hamejwe indi resistance y'inyongera.",
    },
    "M. bovis pyrazinamide-sparing regimen": {
        "EN": "M. bovis pyrazinamide-sparing regimen",
        "FR": "Schéma M. bovis sans pyrazinamide",
        "SW": "Mpango wa M. bovis usiotegemea pyrazinamide",
        "RW": "Gahunda ya M. bovis idakoresha pyrazinamide",
    },
    "modified first-line": {
        "EN": "modified first-line",
        "FR": "première ligne modifiée",
        "SW": "mstari wa kwanza uliorekebishwa",
        "RW": "umurongo wa mbere wahinduwe",
    },
    "Isoniazid (H) + Rifampicin (R) + Ethambutol (E)": {
        "EN": "Isoniazid (H) + Rifampicin (R) + Ethambutol (E)",
        "FR": "Isoniazide (H) + Rifampicine (R) + Ethambutol (E)",
        "SW": "Isoniazid (H) + Rifampicin (R) + Ethambutol (E)",
        "RW": "Isoniazid (H) + Rifampicin (R) + Ethambutol (E)",
    },
    "6-9 months": {"EN": "6-9 months", "FR": "6-9 mois", "SW": "Miezi 6-9", "RW": "Amezi 6-9"},
    "Daily oral therapy with DOTS strongly recommended.": {
        "EN": "Daily oral therapy with DOTS strongly recommended.",
        "FR": "Traitement oral quotidien avec DOTS fortement recommandé.",
        "SW": "Matibabu ya kila siku kwa dawa za kunywa huku DOTS ikipendekezwa sana.",
        "RW": "Ubuvuzi bwa buri munsi bw'ibinini, kandi DOTS irasabwa cyane.",
    },
    "Review species confirmation, liver tests, response to therapy, and zoonotic exposure control.": {
        "EN": "Review species confirmation, liver tests, response to therapy, and zoonotic exposure control.",
        "FR": "Revoir la confirmation de l'espèce, les tests hépatiques, la réponse au traitement et le contrôle de l'exposition zoonotique.",
        "SW": "Kagua uthibitisho wa aina, vipimo vya ini, mwitikio wa matibabu, na udhibiti wa mgusano wa zoonotic.",
        "RW": "Suzuma ukwemezwa kw'ubwoko, ibizamini by'umwijima, uko ubuvuzi bugenda, no kugenzura guhura n'inyamaswa.",
    },
    "Avoid relying on pyrazinamide because M. bovis is usually resistant.": {
        "EN": "Avoid relying on pyrazinamide because M. bovis is usually resistant.",
        "FR": "Éviter de compter sur le pyrazinamide car M. bovis y est habituellement résistant.",
        "SW": "Epuka kutegemea pyrazinamide kwa sababu M. bovis huwa na usugu nayo.",
        "RW": "Irinde gushingira kuri pyrazinamide kuko M. bovis akenshi iyirwanya.",
    },
    "M. microti HR-based regimen": {
        "EN": "M. microti HR-based regimen",
        "FR": "Schéma M. microti basé sur HR",
        "SW": "Mpango wa M. microti unaotegemea HR",
        "RW": "Gahunda ya M. microti ishingiye kuri HR",
    },
    "Isoniazid (H) + Rifampicin (R)-based regimen with or without Ethambutol depending on severity": {
        "EN": "Isoniazid (H) + Rifampicin (R)-based regimen with or without Ethambutol depending on severity",
        "FR": "Schéma à base d'Isoniazide (H) + Rifampicine (R), avec ou sans Ethambutol selon la gravité",
        "SW": "Mpango wa Isoniazid (H) + Rifampicin (R) ukiwa na au bila Ethambutol kulingana na ukali",
        "RW": "Gahunda ishingiye kuri Isoniazid (H) + Rifampicin (R) ishobora kujyana cyangwa kutajyana na Ethambutol bitewe n'ubukana",
    },
    "Daily oral therapy, ideally under supervised adherence support.": {
        "EN": "Daily oral therapy, ideally under supervised adherence support.",
        "FR": "Traitement oral quotidien, idéalement avec soutien supervisé à l'adhérence.",
        "SW": "Matibabu ya kila siku kwa dawa za kunywa, ikiwezekana kwa uangalizi wa ufuasi.",
        "RW": "Ubuvuzi bwa buri munsi bw'ibinini, byiza bukaba bukurikiranwa kugira ngo umuti ufatwe neza.",
    },
    "Confirm species and review response because human disease is uncommon.": {
        "EN": "Confirm species and review response because human disease is uncommon.",
        "FR": "Confirmer l'espèce et revoir la réponse au traitement car la maladie humaine est rare.",
        "SW": "Thibitisha aina na kagua mwitikio wa matibabu kwa sababu ugonjwa huu kwa binadamu si wa kawaida.",
        "RW": "Emeza ubwoko kandi urebe uko ubuvuzi bugenda kuko iyi ndwara ku bantu idakunze kuboneka.",
    },
    "Specialist review is advised for rare-species disease.": {
        "EN": "Specialist review is advised for rare-species disease.",
        "FR": "Un avis spécialisé est conseillé pour une maladie due à une espèce rare.",
        "SW": "Ushauri wa mtaalamu unashauriwa kwa ugonjwa wa aina adimu.",
        "RW": "Isuzuma ry'inzobere rirakenewe ku ndwara itewe n'ubwoko budakunze kuboneka.",
    },
    "first-line": {"EN": "first-line", "FR": "première ligne", "SW": "mstari wa kwanza", "RW": "umurongo wa mbere"},
    "preventive therapy": {"EN": "preventive therapy", "FR": "thérapie préventive", "SW": "tiba kinga", "RW": "ubuvuzi bwo gukumira"},
    "LTBI 6-9H option": {"EN": "LTBI 6-9H option", "FR": "Option LTBI 6-9H", "SW": "Chaguo la LTBI 6-9H", "RW": "Ihitamo rya LTBI 6-9H"},
    "Isoniazid daily": {"EN": "Isoniazid daily", "FR": "Isoniazide quotidien", "SW": "Isoniazid kila siku", "RW": "Isoniazid buri munsi"},
    "Daily oral therapy with adherence follow-up.": {
        "EN": "Daily oral therapy with adherence follow-up.",
        "FR": "Traitement oral quotidien avec suivi de l'adhérence.",
        "SW": "Matibabu ya kila siku kwa dawa za kunywa na ufuatiliaji wa ufuasi.",
        "RW": "Ubuvuzi bwa buri munsi bw'ibinini hamwe no gukurikirana ifatwa ry'umuti.",
    },
    "Baseline and interval liver monitoring where indicated.": {
        "EN": "Baseline and interval liver monitoring where indicated.",
        "FR": "Surveillance hépatique initiale et périodique si indiqué.",
        "SW": "Fuatilia ini mwanzoni na mara kwa mara inapohitajika.",
        "RW": "Kurikirana umwijima mbere yo gutangira no hagati aho igihe bikenewe.",
    },
    "Standard WHO preventive option for LTBI.": {
        "EN": "Standard WHO preventive option for LTBI.",
        "FR": "Option préventive standard OMS pour le LTBI.",
        "SW": "Chaguo la kawaida la kinga la WHO kwa LTBI.",
        "RW": "Ihitamo risanzwe rya OMS ryo gukumira LTBI.",
    },
    "LTBI 3HP option": {"EN": "LTBI 3HP option", "FR": "Option LTBI 3HP", "SW": "Chaguo la LTBI 3HP", "RW": "Ihitamo rya LTBI 3HP"},
    "Isoniazid + Rifapentine weekly": {
        "EN": "Isoniazid + Rifapentine weekly",
        "FR": "Isoniazide + Rifapentine chaque semaine",
        "SW": "Isoniazid + Rifapentine kila wiki",
        "RW": "Isoniazid + Rifapentine buri cyumweru",
    },
    "3 months": {"EN": "3 months", "FR": "3 mois", "SW": "Miezi 3", "RW": "Amezi 3"},
    "Weekly directly observed or closely supported therapy.": {
        "EN": "Weekly directly observed or closely supported therapy.",
        "FR": "Traitement hebdomadaire directement observé ou étroitement soutenu.",
        "SW": "Tiba ya kila wiki inayofuatiliwa moja kwa moja au kwa karibu.",
        "RW": "Ubuvuzi bwa buri cyumweru bukurikiranwa neza cyangwa bugafashwa bya hafi.",
    },
    "Monitor adherence and drug interactions.": {
        "EN": "Monitor adherence and drug interactions.",
        "FR": "Surveiller l'adhérence et les interactions médicamenteuses.",
        "SW": "Fuatilia ufuasi na mwingiliano wa dawa.",
        "RW": "Kurikirana ifatwa ry'umuti n'uko imiti ishobora kugongana.",
    },
    "Short-course WHO preventive option.": {
        "EN": "Short-course WHO preventive option.",
        "FR": "Option préventive OMS de courte durée.",
        "SW": "Chaguo la kinga la WHO la muda mfupi.",
        "RW": "Ihitamo rya OMS ryo gukumira rimara igihe gito.",
    },
    "LTBI 4R option": {"EN": "LTBI 4R option", "FR": "Option LTBI 4R", "SW": "Chaguo la LTBI 4R", "RW": "Ihitamo rya LTBI 4R"},
    "Rifampicin daily": {"EN": "Rifampicin daily", "FR": "Rifampicine quotidienne", "SW": "Rifampicin kila siku", "RW": "Rifampicin buri munsi"},
    "4 months": {"EN": "4 months", "FR": "4 mois", "SW": "Miezi 4", "RW": "Amezi 4"},
    "Daily oral therapy.": {"EN": "Daily oral therapy.", "FR": "Traitement oral quotidien.", "SW": "Matibabu ya kila siku kwa dawa za kunywa.", "RW": "Ubuvuzi bwa buri munsi bw'ibinini."},
    "Monitor liver function and interactions.": {
        "EN": "Monitor liver function and interactions.",
        "FR": "Surveiller la fonction hépatique et les interactions.",
        "SW": "Fuatilia kazi ya ini na mwingiliano wa dawa.",
        "RW": "Kurikirana imikorere y'umwijima n'uko imiti ishobora kugongana.",
    },
    "Alternative preventive option when appropriate.": {
        "EN": "Alternative preventive option when appropriate.",
        "FR": "Option préventive alternative selon le contexte.",
        "SW": "Chaguo jingine la kinga inapofaa.",
        "RW": "Ubundi buryo bwo gukumira igihe bikwiye.",
    },
    "WHO-aligned TB rule engine with species notes, infection-site classification, and DST-aware regimen escalation.": {
        "EN": "WHO-aligned TB rule engine with species notes, infection-site classification, and DST-aware regimen escalation.",
        "FR": "Moteur de règles TB aligné sur l'OMS avec notes d'espèce, classification du site d'infection et adaptation du traitement selon le DST.",
        "SW": "Mfumo wa sheria za TB unaolingana na WHO wenye maelezo ya aina, eneo la maambukizi, na kuongeza mpango wa dawa kulingana na DST.",
        "RW": "Sisitemu y'amabwiriza ya TB ihuje na OMS, ifite ibisobanuro by'ubwoko, aho ubwandu buri n'ihindurwa rya gahunda y'imiti hashingiwe kuri DST.",
    },
    "CONFIRMED PULMONARY TB (PTB)": {
        "EN": "CONFIRMED PULMONARY TB (PTB)",
        "FR": "TB PULMONAIRE CONFIRMÉE (PTB)",
        "SW": "TB YA MAPAFU ILIYOTHIBITISHWA (PTB)",
        "RW": "TB Y'IBIHAHA YEMEJWE (PTB)",
    },
    "CLINICALLY DIAGNOSED PULMONARY TB (PTB)": {
        "EN": "CLINICALLY DIAGNOSED PULMONARY TB (PTB)",
        "FR": "TB PULMONAIRE DIAGNOSTIQUÉE CLINIQUEMENT (PTB)",
        "SW": "TB YA MAPAFU ILIYOGUNDULIWA KIKLINIKI (PTB)",
        "RW": "TB Y'IBIHAHA YASUZUMWE NA MUGANGA (PTB)",
    },
    "PRESUMPTIVE PULMONARY TB (PTB)": {
        "EN": "PRESUMPTIVE PULMONARY TB (PTB)",
        "FR": "TB PULMONAIRE PRÉSUMÉE (PTB)",
        "SW": "TB YA MAPAFU INAYOSHUKIWA (PTB)",
        "RW": "TB Y'IBIHAHA IKEKWA (PTB)",
    },
    "CONFIRMED LYMPH NODE TB (EPTB)": {
        "EN": "CONFIRMED LYMPH NODE TB (EPTB)",
        "FR": "TB GANGLIONNAIRE CONFIRMÉE (EPTB)",
        "SW": "TB YA VIFUKO VYA LIMFU ILIYOTHIBITISHWA (EPTB)",
        "RW": "TB YO MU DUSABO TWA LYMPHO YEMEJWE (EPTB)",
    },
    "SUSPECTED LYMPH NODE TB (EPTB)": {
        "EN": "SUSPECTED LYMPH NODE TB (EPTB)",
        "FR": "TB GANGLIONNAIRE SUSPECTÉE (EPTB)",
        "SW": "TB YA VIFUKO VYA LIMFU INAYOSHUKIWA (EPTB)",
        "RW": "TB YO MU DUSABO TWA LYMPHO IKEKWA (EPTB)",
    },
    "CONFIRMED BONE/JOINT TB (EPTB, including Pott's disease)": {
        "EN": "CONFIRMED BONE/JOINT TB (EPTB, including Pott's disease)",
        "FR": "TB OSSEUSE/ARTICULAIRE CONFIRMÉE (EPTB, y compris maladie de Pott)",
        "SW": "TB YA MIFUPA/VIUNGO ILIYOTHIBITISHWA (EPTB, ikijumuisha ugonjwa wa Pott)",
        "RW": "TB YO MU MAGUFA/INGINGO YEMEJWE (EPTB, harimo indwara ya Pott)",
    },
    "SUSPECTED BONE/JOINT TB (EPTB)": {
        "EN": "SUSPECTED BONE/JOINT TB (EPTB)",
        "FR": "TB OSSEUSE/ARTICULAIRE SUSPECTÉE (EPTB)",
        "SW": "TB YA MIFUPA/VIUNGO INAYOSHUKIWA (EPTB)",
        "RW": "TB YO MU MAGUFA/INGINGO IKEKWA (EPTB)",
    },
    "CONFIRMED TB MENINGITIS (EPTB - LIFE THREATENING)": {
        "EN": "CONFIRMED TB MENINGITIS (EPTB - LIFE THREATENING)",
        "FR": "MÉNINGITE TB CONFIRMÉE (EPTB - menace vitale)",
        "SW": "MENINGITIS YA TB ILIYOTHIBITISHWA (EPTB - hatari kwa maisha)",
        "RW": "MENINGITIS YA TB YEMEJWE (EPTB - ishobora gushyira ubuzima mu kaga)",
    },
    "SUSPECTED TB MENINGITIS (EPTB - URGENT)": {
        "EN": "SUSPECTED TB MENINGITIS (EPTB - URGENT)",
        "FR": "MÉNINGITE TB SUSPECTÉE (EPTB - urgent)",
        "SW": "MENINGITIS YA TB INAYOSHUKIWA (EPTB - haraka)",
        "RW": "MENINGITIS YA TB IKEKWA (EPTB - byihutirwa)",
    },
    "CONFIRMED GENITOURINARY TB (EPTB)": {
        "EN": "CONFIRMED GENITOURINARY TB (EPTB)",
        "FR": "TB GÉNITO-URINAIRE CONFIRMÉE (EPTB)",
        "SW": "TB YA MFUMO WA MKOJO/UZAZI ILIYOTHIBITISHWA (EPTB)",
        "RW": "TB YO MU MYANYA NDANGAGITSINA N'INKARI YEMEJWE (EPTB)",
    },
    "SUSPECTED GENITOURINARY TB (EPTB)": {
        "EN": "SUSPECTED GENITOURINARY TB (EPTB)",
        "FR": "TB GÉNITO-URINAIRE SUSPECTÉE (EPTB)",
        "SW": "TB YA MFUMO WA MKOJO/UZAZI INAYOSHUKIWA (EPTB)",
        "RW": "TB YO MU MYANYA NDANGAGITSINA N'INKARI IKEKWA (EPTB)",
    },
    "CONFIRMED ABDOMINAL TB (EPTB)": {
        "EN": "CONFIRMED ABDOMINAL TB (EPTB)",
        "FR": "TB ABDOMINALE CONFIRMÉE (EPTB)",
        "SW": "TB YA TUMBO ILIYOTHIBITISHWA (EPTB)",
        "RW": "TB YO MU NDA YEMEJWE (EPTB)",
    },
    "SUSPECTED ABDOMINAL TB (EPTB)": {
        "EN": "SUSPECTED ABDOMINAL TB (EPTB)",
        "FR": "TB ABDOMINALE SUSPECTÉE (EPTB)",
        "SW": "TB YA TUMBO INAYOSHUKIWA (EPTB)",
        "RW": "TB YO MU NDA IKEKWA (EPTB)",
    },
    "CONFIRMED PLEURAL TB (EPTB)": {
        "EN": "CONFIRMED PLEURAL TB (EPTB)",
        "FR": "TB PLEURALE CONFIRMÉE (EPTB)",
        "SW": "TB YA PLEURA ILIYOTHIBITISHWA (EPTB)",
        "RW": "TB YO KU GIHU CY'IBIHAHA YEMEJWE (EPTB)",
    },
    "SUSPECTED PLEURAL TB (EPTB)": {
        "EN": "SUSPECTED PLEURAL TB (EPTB)",
        "FR": "TB PLEURALE SUSPECTÉE (EPTB)",
        "SW": "TB YA PLEURA INAYOSHUKIWA (EPTB)",
        "RW": "TB YO KU GIHU CY'IBIHAHA IKEKWA (EPTB)",
    },
    "CONFIRMED/SUSPECTED MILIARY TB (DISSEMINATED - LIFE THREATENING)": {
        "EN": "CONFIRMED/SUSPECTED MILIARY TB (DISSEMINATED - LIFE THREATENING)",
        "FR": "TB MILIAIRE CONFIRMÉE/SUSPECTÉE (disséminée - menace vitale)",
        "SW": "TB ILIYOSAMBAA MWILINI ILIYOTHIBITISHWA/INAYOSHUKIWA (hatari kwa maisha)",
        "RW": "TB YAKWIRAKWIRIYE MU MUBIRI YEMEJWE/KEKWA (ishyira ubuzima mu kaga)",
    },
    "LATENT TB INFECTION (LTBI) - NO ACTIVE DISEASE": {
        "EN": "LATENT TB INFECTION (LTBI) - NO ACTIVE DISEASE",
        "FR": "INFECTION TUBERCULEUSE LATENTE (LTBI) - PAS DE MALADIE ACTIVE",
        "SW": "MAAMBUKIZI FICHE YA TB (LTBI) - HAKUNA UGONJWA HAI",
        "RW": "UBWANDU BWA TB BUTARAGARAGARA (LTBI) - NTA NDWARA IRI GUKORA",
    },
    "TB/HIV CO-INFECTION": {
        "EN": "TB/HIV CO-INFECTION",
        "FR": "CO-INFECTION TB/VIH",
        "SW": "MAAMBUKIZI YA TB/HIV KWA PAMOJA",
        "RW": "UBWANDU BWA TB/VIH ICYARIMWE",
    },
    "DRUG-SENSITIVE TB (DS-TB)": {
        "EN": "DRUG-SENSITIVE TB (DS-TB)",
        "FR": "TB SENSIBLE AUX MÉDICAMENTS (DS-TB)",
        "SW": "TB INAYOITIKIA DAWA (DS-TB)",
        "RW": "TB YUMVA IMITI (DS-TB)",
    },
    "LATENT TB INFECTION (LTBI)": {
        "EN": "LATENT TB INFECTION (LTBI)",
        "FR": "INFECTION TUBERCULEUSE LATENTE (LTBI)",
        "SW": "MAAMBUKIZI FICHE YA TB (LTBI)",
        "RW": "UBWANDU BWA TB BUTARAGARAGARA (LTBI)",
    },
    "PRESUMPTIVE TB CASE - FURTHER TESTING REQUIRED": {
        "EN": "PRESUMPTIVE TB CASE - FURTHER TESTING REQUIRED",
        "FR": "CAS PRÉSUMÉ DE TB - TESTS SUPPLÉMENTAIRES REQUIS",
        "SW": "KESI INAYOSHUKIWA KUWA TB - VIPIMO ZAIDI VINAHITAJIKA",
        "RW": "URUBANZA RUKEKWAHO TB - HAKENEWE IBINDI BIZAMINI",
    },
    "NO EVIDENCE OF TB": {
        "EN": "NO EVIDENCE OF TB",
        "FR": "AUCUNE PREUVE DE TB",
        "SW": "HAKUNA USHAHIDI WA TB",
        "RW": "NTA BIMENYETSO BYA TB",
    },
    "Primary TB classification:": {
        "EN": "Primary TB classification:",
        "FR": "Classification TB principale :",
        "SW": "Ainisho kuu ya TB:",
        "RW": "Icyiciro nyamukuru cya TB:",
    },
    "Bacteria estimate:": {
        "EN": "Bacteria estimate:",
        "FR": "Estimation de la bactérie :",
        "SW": "Makadirio ya bakteria:",
        "RW": "Igereranya rya bagiteri:",
    },
    "Resistance class:": {
        "EN": "Resistance class:",
        "FR": "Classe de résistance :",
        "SW": "Daraja la usugu:",
        "RW": "Icyiciro cya resistance:",
    },
    "Inferred from exposure or epidemiology clues: {clues}.": {
        "EN": "Inferred from exposure or epidemiology clues: {clues}.",
        "FR": "Déduit à partir d'indices d'exposition ou d'épidémiologie : {clues}.",
        "SW": "Imekadiriwa kutokana na viashiria vya mgusano au epidemiolojia: {clues}.",
        "RW": "Byagereranyijwe hashingiwe ku bimenyetso by'aho yahuye n'indwara cyangwa ku miterere yayo: {clues}.",
    },
    "Estimated from curated owner dataset matches using patient symptoms, exposure, geography, and tests. Matched {count} similar case(s); strongest evidence: {evidence}.": {
        "EN": "Estimated from curated owner dataset matches using patient symptoms, exposure, geography, and tests. Matched {count} similar case(s); strongest evidence: {evidence}.",
        "FR": "Estimé à partir de correspondances avec le jeu de données du propriétaire en utilisant symptômes, exposition, géographie et tests. {count} cas similaire(s) trouvés ; preuve la plus forte : {evidence}.",
        "SW": "Imekadiriwa kutoka ulinganisho wa dataset ya mmiliki kwa kutumia dalili, mgusano, eneo na vipimo. Imefanana na kesi {count}; ushahidi mkuu: {evidence}.",
        "RW": "Byagereranyijwe hakoreshejwe guhuza amakuru yo muri dataset ya nyirayo hifashishijwe ibimenyetso, aho yahuye n'indwara, aho atuye n'ibizamini. Habonetse dosiye {count} zisa; ibimenyetso bikomeye ni: {evidence}.",
    },
    "shared context: {context}": {
        "EN": "shared context: {context}",
        "FR": "contexte partagé : {context}",
        "SW": "muktadha unaofanana: {context}",
        "RW": "ibintu bihuriyeho: {context}",
    },
    "{field} match": {
        "EN": "{field} match",
        "FR": "correspondance pour {field}",
        "SW": "{field} inafanana",
        "RW": "{field} bihuye",
    },
    "{field} positive": {
        "EN": "{field} positive",
        "FR": "{field} positif",
        "SW": "{field} chanya",
        "RW": "{field} cyagaragaye",
    },
    "sputum smear test": {
        "EN": "sputum smear test",
        "FR": "test de frottis sputum",
        "SW": "kipimo cha sputum smear",
        "RW": "ikizamini cya sputum smear",
    },
    "genexpert test": {
        "EN": "GeneXpert test",
        "FR": "test GeneXpert",
        "SW": "kipimo cha GeneXpert",
        "RW": "ikizamini cya GeneXpert",
    },
    "chest xray": {
        "EN": "chest X-ray",
        "FR": "radio thoracique",
        "SW": "X-ray ya kifua",
        "RW": "X-ray y'igituza",
    },
    "tb culture": {
        "EN": "TB culture",
        "FR": "culture TB",
        "SW": "TB culture",
        "RW": "TB culture",
    },
    "tst": {"EN": "TST", "FR": "TST", "SW": "TST", "RW": "TST"},
    "igra": {"EN": "IGRA", "FR": "IGRA", "SW": "IGRA", "RW": "IGRA"},
    "Intensive phase: {intensive}; continuation phase: {continuation}; daily DOTS/supervised dosing where feasible.": {
        "EN": "Intensive phase: {intensive}; continuation phase: {continuation}; daily DOTS/supervised dosing where feasible.",
        "FR": "Phase intensive : {intensive} ; phase de continuation : {continuation} ; prise quotidienne supervisée/DOTS si possible.",
        "SW": "Hatua ya mwanzo: {intensive}; hatua ya kuendelea: {continuation}; dawa kila siku chini ya uangalizi/DOTS inapowezekana.",
        "RW": "Icyiciro cya mbere: {intensive}; icyiciro gikurikiraho: {continuation}; gufata imiti buri munsi hakurikiranwa/DOTS igihe bishoboka.",
    },
    "Intensive: {intensive}, Continuation: {continuation}": {
        "EN": "Intensive: {intensive}, Continuation: {continuation}",
        "FR": "Intensive : {intensive}, Continuation : {continuation}",
        "SW": "Hatua ya mwanzo: {intensive}, Kuendelea: {continuation}",
        "RW": "Icyiciro cya mbere: {intensive}, Gikurikiraho: {continuation}",
    },
}


def tr(key, lang=None, **kwargs):
    lang = lang or get_request_lang()
    value = I18N.get(key, {}).get(lang) or I18N.get(key, {}).get("EN") or key
    try:
        return value.format(**kwargs)
    except Exception:
        return value


def tr_lit(value, lang=None, **kwargs):
    lang = lang or get_request_lang()
    value = str(value)
    translations = LITERAL_I18N.get(value, {})
    template = translations.get(lang) or translations.get("EN")
    if template is None:
        return value
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def translate_backend_text_value(value, lang=None):
    lang = lang or get_request_lang()
    if not isinstance(value, str):
        return value

    raw = value.strip()
    if not raw:
        return value

    translated = tr_lit(raw, lang=lang)
    if raw in LITERAL_I18N:
        return translated

    if raw.startswith("Primary TB classification: "):
        return f"{tr_lit('Primary TB classification:', lang=lang)[:-1]}: {translate_backend_text_value(raw[len('Primary TB classification: '):], lang=lang)}"
    if raw.startswith("Bacteria estimate: "):
        return f"{tr_lit('Bacteria estimate:', lang=lang)[:-1]}: {translate_backend_text_value(raw[len('Bacteria estimate: '):], lang=lang)}"
    if raw.startswith("Resistance class: "):
        return f"{tr_lit('Resistance class:', lang=lang)[:-1]}: {translate_backend_text_value(raw[len('Resistance class: '):], lang=lang)}"
    if raw.startswith("ALERT: "):
        return f"{tr_lit('ALERT:', lang=lang)} {translate_backend_text_value(raw[len('ALERT: '):], lang=lang)}"

    match = re.match(r"^Inferred from exposure or epidemiology clues: (.+)\.$", raw)
    if match:
        clues = match.group(1)
        return tr_lit(
            "Inferred from exposure or epidemiology clues: {clues}.",
            lang=lang,
            clues=clues,
        )

    match = re.match(
        r"^Estimated from curated owner dataset matches using patient symptoms, exposure, geography, and tests\. Matched (\d+) similar case\(s\); strongest evidence: (.+)\.$",
        raw,
    )
    if match:
        count = match.group(1)
        evidence = ", ".join(
            translate_backend_text_value(part.strip(), lang=lang)
            for part in match.group(2).split(",")
        )
        return tr_lit(
            "Estimated from curated owner dataset matches using patient symptoms, exposure, geography, and tests. Matched {count} similar case(s); strongest evidence: {evidence}.",
            lang=lang,
            count=count,
            evidence=evidence,
        )

    match = re.match(r"^shared context: (.+)$", raw)
    if match:
        return tr_lit("shared context: {context}", lang=lang, context=match.group(1))

    match = re.match(r"^(sputum smear test|genexpert test|chest xray) match$", raw)
    if match:
        field_name = match.group(1)
        return tr_lit("{field} match", lang=lang, field=tr_lit(field_name, lang=lang))

    match = re.match(r"^(tb culture|tst|igra) positive$", raw)
    if match:
        field_name = match.group(1)
        return tr_lit("{field} positive", lang=lang, field=tr_lit(field_name, lang=lang))

    match = re.match(
        r"^Intensive phase: (.*); continuation phase: (.*); daily DOTS/supervised dosing where feasible\.$",
        raw,
    )
    if match:
        intensive = translate_backend_text_value(match.group(1), lang=lang)
        continuation = translate_backend_text_value(match.group(2), lang=lang)
        return tr_lit(
            "Intensive phase: {intensive}; continuation phase: {continuation}; daily DOTS/supervised dosing where feasible.",
            lang=lang,
            intensive=intensive,
            continuation=continuation,
        )

    match = re.match(r"^Intensive: (.*), Continuation: (.*)$", raw)
    if match:
        intensive = translate_backend_text_value(match.group(1), lang=lang)
        continuation = translate_backend_text_value(match.group(2), lang=lang)
        return tr_lit(
            "Intensive: {intensive}, Continuation: {continuation}",
            lang=lang,
            intensive=intensive,
            continuation=continuation,
        )

    return raw


def localize_payload(value, lang=None):
    lang = lang or get_request_lang()
    if isinstance(value, dict):
        return {key: localize_payload(item, lang=lang) for key, item in value.items()}
    if isinstance(value, list):
        return [localize_payload(item, lang=lang) for item in value]
    if isinstance(value, str):
        return translate_backend_text_value(value, lang=lang)
    return value

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
    lang = get_request_lang()
    resistant_drugs = normalize_drug_list(resistant_to)
    susceptible_drugs = normalize_drug_list(susceptible_to)
    antibiogram_text = str(antibiogram_result or "").strip()
    decision_basis = []
    regimen_level = "first-line"
    classification_code = "DS"
    classification = tr("RES_DS", lang=lang)
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
        classification_code = "XDR"
        classification = tr("RES_XDR", lang=lang)
        regimen_level = "individualized second-line"
        decision_basis.append(tr("BASIS_XDR", lang=lang))
    elif (
        "multidrug-resistant" in combined_text
        or "mdr" in combined_text
        or {"isoniazid", "rifampicin"}.issubset({drug.lower() for drug in resistant_drugs})
        or str(drug_resistant or "").strip() == "Isoniazid and Rifampicin"
    ):
        classification_code = "MDR"
        classification = tr("RES_MDR", lang=lang)
        regimen_level = "second-line"
        decision_basis.append(tr("BASIS_MDR", lang=lang))
    elif resistant_drug_set == {"pyrazinamide"}:
        classification_code = "PZA"
        classification = tr("RES_PZA", lang=lang)
        regimen_level = "modified first-line"
        decision_basis.append(tr("BASIS_PZA", lang=lang))
    elif "rifampicin-resistant" in combined_text or "rr-tb" in combined_text or "rifampicin" in {drug.lower() for drug in resistant_drugs}:
        classification_code = "RR"
        classification = tr("RES_RR", lang=lang)
        regimen_level = "second-line"
        decision_basis.append(tr("BASIS_RR", lang=lang))
    elif str(drug_resistant or "").strip().lower() in {"yes", "drug-resistant"} or resistant_drugs:
        classification_code = "DR"
        classification = tr("RES_DR", lang=lang)
        regimen_level = "second-line"
        decision_basis.append(tr("BASIS_DR", lang=lang))
    else:
        decision_basis.append(tr("BASIS_DS", lang=lang))

    if antibiogram_text:
        decision_basis.append(f"Antibiogram/DST summary: {antibiogram_text}")

    return {
        "classification_code": classification_code,
        "classification": classification,
        "regimen_level": regimen_level,
        "antibiogram_result": antibiogram_text or "Not provided",
        "resistant_to": resistant_drugs,
        "susceptible_to": susceptible_drugs,
        "decision_basis": decision_basis,
        "dst_required": classification_code != "DS",
    }


def build_infection_assessment(tb_analysis, bacteria_assessment=None, lang=None):
    lang = lang or get_request_lang()
    infection_types = []
    seen = set()

    infection_rules = [
        ("pulmonary", "INFECT_PULMONARY", "SITE_LUNGS"),
        ("lymph node", "INFECT_LYMPH_NODE", "SITE_LYMPH_NODES"),
        ("bone/joint", "INFECT_BONE_JOINT", "SITE_BONES_JOINTS"),
        ("meningitis", "INFECT_MENINGITIS", "SITE_CNS"),
        ("genitourinary", "INFECT_GENITOURINARY", "SITE_GU"),
        ("abdominal", "INFECT_ABDOMINAL", "SITE_ABDOMEN"),
        ("pleural", "INFECT_PLEURAL", "SITE_PLEURA"),
        ("miliary", "INFECT_MILIARY", "SITE_DISSEMINATED"),
        ("latent", "INFECT_LATENT", "SITE_LATENT"),
        ("hiv", "INFECT_TB_HIV", "SITE_SYSTEMIC"),
    ]

    # First check tb_types for infection patterns
    for tb_type in tb_analysis["tb_types"]:
        lower = tb_type.lower()
        for key, label_key, site_key in infection_rules:
            label = tr(label_key, lang=lang)
            if key in lower and label not in seen:
                infection_types.append(
                    {
                        "label": label,
                        "site": tr(site_key, lang=lang),
                        "source_classification": tb_type,
                    }
                )
                seen.add(label)

    # If no infection types from tb_types, use bacteria species to infer infection
    if not infection_types and bacteria_assessment:
        species = bacteria_assessment.get("species", "").lower()
        
        # Map common TB species to likely infection types
        species_infection_map = {
            "mycobacterium tuberculosis": ("INFECT_PULMONARY", "SITE_LUNGS"),
            "m. tuberculosis": ("INFECT_PULMONARY", "SITE_LUNGS"),
            "mycobacterium bovis": ("INFECT_EXTRAPULMONARY", "SITE_EXTRAPULMONARY"),
            "m. bovis": ("INFECT_EXTRAPULMONARY", "SITE_EXTRAPULMONARY"),
            "mycobacterium africanum": ("INFECT_PULMONARY", "SITE_LUNGS"),
            "m. africanum": ("INFECT_PULMONARY", "SITE_LUNGS"),
            "mycobacterium microti": ("INFECT_EXTRAPULMONARY", "SITE_EXTRAPULMONARY"),
            "m. microti": ("INFECT_EXTRAPULMONARY", "SITE_EXTRAPULMONARY"),
        }
        
        for species_key, (label_key, site_key) in species_infection_map.items():
            if species_key in species:
                label = tr(label_key, lang=lang)
                site = tr(site_key, lang=lang)
                if label not in seen:
                    infection_types.append({
                        "label": label,
                        "site": site,
                        "source_classification": f"Species-based: {bacteria_assessment.get('species')}",
                    })
                    seen.add(label)
                break

    # If still no infection types, check lab results for clues
    if not infection_types:
        # Check for pulmonary indicators
        if tb_analysis.get("sputum_smear") == "Positive" or tb_analysis.get("genexpert") == "Positive":
            label = tr("INFECT_PULMONARY", lang=lang)
            site = tr("SITE_LUNGS", lang=lang)
            infection_types.append({
                "label": label,
                "site": site,
                "source_classification": "Lab-based: Positive sputum/GeneXpert",
            })
            seen.add(label)
        # Check for extrapulmonary indicators
        elif tb_analysis.get("chest_xray") == "Abnormal":
            label = tr("INFECT_PULMONARY", lang=lang)
            site = tr("SITE_LUNGS", lang=lang)
            infection_types.append({
                "label": label,
                "site": site,
                "source_classification": "Lab-based: Abnormal chest X-ray",
            })
            seen.add(label)

    # Final fallback
    if not infection_types:
        infection_types.append(
            {
                "label": tr("INFECT_NONE", lang=lang),
                "site": tr("SITE_UNSPECIFIED", lang=lang),
                "source_classification": tb_analysis["who_category"],
            }
        )

    # Determine primary infection site more specifically
    primary_site = infection_types[0]["site"]
    if "unspecified" in primary_site.lower() and bacteria_assessment:
        # Try to infer site from species
        species = bacteria_assessment.get("species", "").lower()
        if "microti" in species or "bovis" in species:
            infection_types[0]["site"] = tr("SITE_EXTRAPULMONARY", lang=lang)
        elif "tuberculosis" in species:
            infection_types[0]["site"] = tr("SITE_LUNGS", lang=lang)

    return {
        "primary_infection": infection_types[0]["label"],
        "site": infection_types[0]["site"],
        "infection_types": infection_types,
    }


def build_treatment_plan(tb_analysis, bacteria_assessment, resistance_profile, treatment, clinical_info):
    tb_type = tb_analysis["who_category"]
    species = bacteria_assessment["species"]
    resistance_class = resistance_profile["classification"]
    resistance_code = resistance_profile.get("classification_code")
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

    if resistance_code == "XDR":
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
    elif resistance_code == "MDR":
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
    elif resistance_code in {"RR", "DR"}:
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
                return jsonify({"msg": tr("ACCESS_DENIED")}), 403
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
    lang = get_request_lang()
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
                tr("ALERT_EMAIL_SUBJECT", lang=lang, alert_type=alert_type),
                tr("ALERT_EMAIL_BODY", lang=lang, message=message),
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
        return jsonify({'msg': tr('INVALID_EMAIL_OR_PASSWORD')}), 401

    if not user.check_password(password):
        return jsonify({'msg': tr('INVALID_EMAIL_OR_PASSWORD')}), 401

    # Create access token
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'username': user.username,
            'role': user.role
        }
    )

    # Create audit log for login
    audit = AuditLog(
        user_id=user.id,
        action='user_login',
        entity_type='user',
        entity_id=user.id,
        details=f'User {user.username} logged in',
        created_at=datetime.now()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })

@app.route('/api/auth/register', methods=['POST'])
@role_required('admin', 'hospital_admin')
def register_user():
    data = request.get_json()

    # Check if email already exists
    all_users = User.query.all()
    for u in all_users:
        if u.email == data.get('email'):
            return jsonify({'msg': tr('EMAIL_EXISTS')}), 409

    user = User(
        username=data.get('username'),
        email=data.get('email'),
        role=data.get('role', 'doctor')
    )
    user.set_password(data.get('password'))

    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201

# User Management
@app.route('/api/users', methods=['GET', 'POST'])
@jwt_required()
def get_users():
    user = get_current_user_from_jwt()
    if user.role not in ['admin', 'hospital_admin']:
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    if request.method == 'GET':
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            'users': [u.to_dict() for u in users],
            'total': len(users)
        })
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Check if username or email already exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'msg': 'Username already exists'}), 400
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        # Hash the password
        from utils.security import hash_password
        hashed_password = hash_password(data.get('password'))
        
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            password=hashed_password,
            role=data.get('role', 'doctor'),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(new_user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_user(user_id):
    user = get_current_user_from_jwt()
    if user.role not in ['admin', 'hospital_admin']:
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        
        # Update fields if provided
        if 'username' in data:
            # Check if username already exists for another user
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'msg': 'Username already exists'}), 400
            target_user.username = data['username']
        
        if 'email' in data:
            # Check if email already exists for another user
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'msg': 'Email already exists'}), 400
            target_user.email = data['email']
        
        if 'role' in data:
            target_user.role = data['role']
        
        if 'is_active' in data:
            target_user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            from utils.security import hash_password
            target_user.password = hash_password(data['password'])
        
        db.session.commit()
        return jsonify(target_user.to_dict())
    
    if request.method == 'DELETE':
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'msg': tr('USER_NOT_FOUND')}), 404
    return jsonify(user.to_dict())

# ----------------------
# API Endpoints
# ----------------------

@app.route('/')
def home():
    return jsonify({
        'message': tr('API_HOME_MESSAGE'),
        'version': '2.1.0',
        'database': DATABASE_TYPE,
        'standards': 'WHO International Clinical Guidelines for TB',
        'authentication': tr('JWT_REQUIRED'),
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


@app.route('/api/model-info')
def model_info():
    model_info_path = os.path.join(os.path.dirname(__file__), 'models', 'model_info.json')
    if os.path.exists(model_info_path):
        with open(model_info_path, 'r') as f:
            import json
            return jsonify(json.load(f))
    return jsonify({
        'message': 'No model information available',
        'reason': 'Model training may not have run yet'
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

def calculate_risk_level(patient):
    """Calculate risk level for a patient (same logic as frontend)."""
    score = 0
    if patient.tb_status_label == 'Yes':
        score += 10
    if patient.genexpert_test == 'Positive':
        score += 8
    if patient.sputum_smear_test == 'Positive':
        score += 6
    if patient.chest_xray == 'Abnormal':
        score += 4
    if patient.has_fever == 'Yes':
        score += 1
    if patient.has_cough == 'Yes':
        score += 1
    if patient.has_weight_loss == 'Yes':
        score += 1
    if patient.has_night_sweats == 'Yes':
        score += 1
    if patient.has_chest_pain == 'Yes':
        score += 1
    if patient.has_blood == 'Yes':
        score += 2
    
    if score >= 8:
        return 'high'
    elif score >= 4:
        return 'medium'
    else:
        return 'low'


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
        
        high_risk = query.filter(
            db.or_(Patient.tb_status_label == 'Yes', Patient.genexpert_test == 'Positive')
        ).count()
        medium_risk = query.filter(
            db.and_(
                Patient.tb_status_label != 'Yes',
                Patient.genexpert_test != 'Positive',
                db.or_(Patient.sputum_smear_test == 'Positive', Patient.chest_xray == 'Abnormal')
            )
        ).count()
        low_risk = max(0, pagination.total - high_risk - medium_risk)

        return jsonify({
            'patients': patients_list,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'sort': sort,
            'risk_counts': {
                'high': high_risk,
                'medium': medium_risk,
                'low': low_risk
            }
        })

    if request.method == 'POST':
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        # Get or validate hospital_id
        hospital_id = data.get('hospital_id')
        if not hospital_id:
            # Use user's hospital if available
            if user.hospital_id:
                hospital_id = user.hospital_id
            else:
                # Get first available hospital as fallback
                hospital = Hospital.query.first()
                if hospital:
                    hospital_id = hospital.id
                else:
                    return jsonify({'msg': 'No hospital found. Please create a hospital first.'}), 400
        
        # Validate hospital exists
        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            return jsonify({'msg': 'Hospital not found'}), 400
        
        patient = Patient(
            patient_id=data.get('patient_id'),
            hospital_id=hospital_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            gender=data.get('gender'),
            weight=data.get('weight'),
            city=data.get('city'),
            symptoms=data.get('symptoms'),
            exposure_history=data.get('exposure_history'),
            persistent_cough_duration_weeks=data.get('persistent_cough_duration_weeks'),
            contact_with_tb_patient=data.get('contact_with_tb_patient'),
            previous_tb_treatment=data.get('previous_tb_treatment'),
            sputum_smear_test=data.get('sputum_smear_test'),
            genexpert_test=data.get('genexpert_test'),
            chest_xray=data.get('chest_xray'),
            tb_culture=data.get('tb_culture'),
            tst=data.get('tst'),
            igra=data.get('igra'),
            bacteria_species=data.get('bacteria_species'),
            drug_resistance=data.get('drug_resistance'),
            hiv=data.get('hiv'),
            diabetes=data.get('diabetes'),
            smoking_status=data.get('smoking_status'),
            alcohol_use=data.get('alcohol_use'),
            oxygen_saturation_spo2=data.get('oxygen_saturation_spo2'),
            has_fever=data.get('has_fever'),
            has_cough=data.get('has_cough'),
            has_weight_loss=data.get('has_weight_loss'),
            has_night_sweats=data.get('has_night_sweats'),
            has_chest_pain=data.get('has_chest_pain'),
            has_blood=data.get('has_blood'),
            has_fatigue=data.get('has_fatigue'),
            has_shortness_of_breath=data.get('has_shortness_of_breath')
        )
        db.session.add(patient)
        db.session.commit()

        # Create audit log
        audit = AuditLog(
            user_id=user_id,
            action='create_patient',
            entity_type='patient',
            entity_id=patient.id,
            details=f'Created patient {patient.patient_id}: {patient.first_name} {patient.last_name}',
            created_at=datetime.now()
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify(patient.to_dict()), 201

# Lab Test Management
@app.route('/api/lab-tests', methods=['GET', 'POST'])
@jwt_required()
def lab_tests():
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        patient_id = request.args.get('patient_id', type=int)
        
        print(f"Fetching lab tests: page={page}, per_page={per_page}, user_role={user.role}, patient_id={patient_id}")
        
        # Build query with patient_id filter if provided
        query = LabTest.query
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        if user.role == 'lab_technician':
            # Lab techs can see all requested lab tests (or filtered by patient)
            pagination = query.order_by(LabTest.completed_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            tests = pagination.items
        elif user.role in ['doctor', 'admin', 'hospital_admin']:
            # Doctors and admins can see all lab tests (or filtered by patient)
            pagination = query.order_by(LabTest.completed_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            tests = pagination.items
        elif user.role == 'pharmacist':
            # Pharmacists don't see lab tests
            tests = []
            pagination = None
        else:
            tests = []
            pagination = None
        
        print(f"Found {len(tests)} lab tests total")
        print(f"Test statuses: {[t.status for t in tests]}")
        
        if pagination:
            return jsonify({
                'lab_tests': [test.to_dict() for test in tests],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page
            })
        else:
            return jsonify({'lab_tests': [], 'total': 0, 'pages': 1, 'current_page': 1})
    
    if request.method == 'POST':
        if user.role not in ['doctor', 'admin', 'hospital_admin']:
            lang = get_request_lang()
            return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403
        
        data = request.get_json()
        print(f"Creating lab test: patient_id={data.get('patient_id')}, test_type={data.get('test_type')}, user_id={user_id}")
        
        test = LabTest(
            patient_id=data.get('patient_id'),
            requested_by=user_id,
            test_type=data.get('test_type'),
            notes=data.get('notes'),
            status='requested'
        )
        db.session.add(test)
        db.session.commit()
        
        print(f"Lab test created with ID: {test.id}, status: {test.status}")
        
        # Create audit log after test is committed (so test.id exists)
        audit = AuditLog(
            user_id=user_id,
            action='request_lab_test',
            entity_type='lab_test',
            entity_id=test.id,
            details=f"Requested {test.test_type} for patient {test.patient_id}"
        )
        db.session.add(audit)
        db.session.commit()
        
        print(f"Total lab tests in database: {LabTest.query.count()}")
        print(f"Pending lab tests (status='requested'): {LabTest.query.filter_by(status='requested').count()}")
        
        return jsonify(test.to_dict()), 201


@app.route('/api/lab-tests/<int:test_id>', methods=['GET', 'PUT'])
@jwt_required()
def lab_test_detail(test_id):
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    test = LabTest.query.get_or_404(test_id)
    
    if request.method == 'GET':
        # Check if user can access
        if user.role == 'lab_technician' or user.role in ['doctor', 'admin', 'hospital_admin']:
            return jsonify(test.to_dict())
        else:
            lang = get_request_lang()
            return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403
    
    if request.method == 'PUT':
        # Only lab techs, doctors, or admins can update
        if user.role not in ['lab_technician', 'doctor', 'admin', 'hospital_admin']:
            lang = get_request_lang()
            return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403
        
        data = request.get_json()
        for key, value in data.items():
            if hasattr(test, key):
                setattr(test, key, value)
        
        # If status is being set to completed, set completed by and completed at
        if data.get('status') == 'completed' and user.role == 'lab_technician':
            test.completed_by = user_id
            test.completed_at = datetime.now()
            
            # Recalculate risk score when lab result is completed
            try:
                recalculate_risk_on_lab_result(test.patient_id)
            except Exception as e:
                print(f"Error recalculating risk score: {e}")
        
        # Create audit log
        audit = AuditLog(
            user_id=user_id,
            action='update_lab_test',
            entity_type='lab_test',
            entity_id=test.id,
            details=f"Updated lab test {test.id}"
        )
        db.session.add(audit)
        
        db.session.commit()
        return jsonify(test.to_dict())

@app.route('/api/lab-tests/<int:test_id>/submit-result', methods=['POST'])
@jwt_required()
def submit_lab_result(test_id):
    user = get_current_user_from_jwt()
    if user.role not in ['lab_technician', 'admin', 'hospital_admin']:
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    test = LabTest.query.get_or_404(test_id)
    
    if test.status == 'completed':
        return jsonify({'error': 'Test already completed'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('results'):
        return jsonify({'error': 'Results are required'}), 400
    
    # Update test with results
    test.status = 'completed'
    test.results = data.get('results')
    test.notes = data.get('notes')
    test.completed_by = user.id
    test.completed_at = datetime.now()
    
    # Recalculate risk score when lab result is completed
    try:
        recalculate_risk_on_lab_result(test.patient_id)
    except Exception as e:
        print(f"Error recalculating risk score: {e}")
    
    # Create audit log
    audit = AuditLog(
        user_id=user.id,
        action='submit_lab_result',
        entity_type='lab_test',
        entity_id=test.id,
        details=f"Submitted results for {test.test_type} for patient {test.patient_id}"
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify(test.to_dict())

@app.route('/api/lab-tests/pending', methods=['GET'])
@jwt_required()
def get_pending_lab_tests():
    user = get_current_user_from_jwt()
    print(f"Fetching pending tests for user: {user.username}, role: {user.role}")
    
    if user.role not in ['lab_technician', 'admin', 'hospital_admin']:
        print(f"Access denied: user role is {user.role}")
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    pending_tests = LabTest.query.filter_by(status='requested').order_by(LabTest.created_at).all()
    print(f"Found {len(pending_tests)} pending tests")
    
    return jsonify({
        'pending_tests': [test.to_dict() for test in pending_tests],
        'total': len(pending_tests)
    })


# ATC Drug Management
@app.route('/api/atc-drugs', methods=['GET', 'POST'])
@jwt_required()
def atc_drugs():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        pagination = ATCDrug.query.order_by(ATCDrug.drug_name.desc()).paginate(page=page, per_page=per_page, error_out=False)
        drugs = [d.to_dict() for d in pagination.items]
        return jsonify({
            'atc_drugs': drugs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    
    if request.method == 'POST':
        data = request.get_json()
        drug = ATCDrug(
            atc_code=data.get('atc_code'),
            atc_level_1=data.get('atc_level_1'),
            atc_level_2=data.get('atc_level_2'),
            atc_level_3=data.get('atc_level_3'),
            atc_level_4=data.get('atc_level_4'),
            atc_level_5=data.get('atc_level_5'),
            drug_name=data.get('drug_name'),
            ddd=data.get('ddd'),
            ddd_unit=data.get('ddd_unit'),
            administration_route=data.get('administration_route')
        )
        db.session.add(drug)
        db.session.commit()
        return jsonify(drug.to_dict()), 201


# Detailed Lab Results Management
@app.route('/api/detailed-lab-results', methods=['GET', 'POST'])
@jwt_required()
def detailed_lab_results():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        pagination = DetailedLabResult.query.order_by(DetailedLabResult.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        results = [r.to_dict() for r in pagination.items]
        return jsonify({
            'detailed_lab_results': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    
    if request.method == 'POST':
        data = request.get_json()
        lab_result = DetailedLabResult(
            patient_id=data.get('patient_id'),
            hospital=data.get('hospital'),
            test_name=data.get('test_name'),
            test_value=data.get('test_value'),
            unit=data.get('unit'),
            reference_range=data.get('reference_range'),
            collection_date=data.get('collection_date'),
            source_dataset=data.get('source_dataset')
        )
        db.session.add(lab_result)
        db.session.commit()
        return jsonify(lab_result.to_dict()), 201


# Antibiotic Resistance Management
@app.route('/api/antibiotic-resistance', methods=['GET', 'POST'])
@jwt_required()
def antibiotic_resistance():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        pagination = AntibioticResistance.query.order_by(AntibioticResistance.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        results = [r.to_dict() for r in pagination.items]
        return jsonify({
            'antibiotic_resistance_records': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    
    if request.method == 'POST':
        data = request.get_json()
        ar = AntibioticResistance(
            sample_id=data.get('sample_id'),
            patient_name=data.get('patient_name'),
            patient_email=data.get('patient_email'),
            patient_address=data.get('patient_address'),
            age_gender=data.get('age_gender'),
            bacterial_species=data.get('bacterial_species'),
            diabetes=data.get('diabetes'),
            hypertension=data.get('hypertension'),
            previous_hospitalization=data.get('previous_hospitalization'),
            infection_frequency=data.get('infection_frequency'),
            amx_amp=data.get('amx_amp'),
            amc=data.get('amc'),
            cz=data.get('cz'),
            fox=data.get('fox'),
            ctx_cro=data.get('ctx_cro'),
            ipm=data.get('ipm'),
            gen=data.get('gen'),
            an=data.get('an'),
            nalidixic_acid=data.get('nalidixic_acid'),
            ofx=data.get('ofx'),
            cip=data.get('cip'),
            chloramphenicol=data.get('chloramphenicol'),
            co_trimoxazole=data.get('co_trimoxazole'),
            furanes=data.get('furanes'),
            colistine=data.get('colistine'),
            collection_date=data.get('collection_date'),
            notes=data.get('notes'),
            source_dataset=data.get('source_dataset')
        )
        db.session.add(ar)
        db.session.commit()
        return jsonify(ar.to_dict()), 201


# Prescription Management
@app.route('/api/prescriptions', methods=['GET', 'POST'])
@jwt_required()
def prescriptions():
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if request.method == 'GET':
        if user.role == 'pharmacist':
            # Pharmacists see all pending and their approved/rejected
            prescs = Prescription.query.order_by(Prescription.created_at.desc()).all()
        elif user.role in ['doctor', 'admin', 'hospital_admin']:
            # Doctors and admins see all
            prescs = Prescription.query.order_by(Prescription.created_at.desc()).all()
        elif user.role == 'lab_technician':
            # Lab techs don't see prescriptions
            prescs = []
        else:
            prescs = []
        
        return jsonify({'prescriptions': [p.to_dict() for p in prescs]})
    
    if request.method == 'POST':
        if user.role not in ['doctor', 'admin', 'hospital_admin']:
            lang = get_request_lang()
            return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403
        
        data = request.get_json()
        presc = Prescription(
            patient_id=data.get('patient_id'),
            diagnosis_id=data.get('diagnosis_id'),
            created_by=user_id,
            medication=data.get('medication'),
            atc_drug_id=data.get('atc_drug_id'),
            dosage=data.get('dosage'),
            dosage_mg=data.get('dosage_mg'),
            frequency=data.get('frequency', '1 time daily'),
            duration_days=data.get('duration_days'),
            duration=data.get('duration'),
            risk_level=data.get('risk_level'),
            ml_recommended=data.get('ml_recommended', False)
        )
        
        # Calculate total_mg, tablets_per_dose, and total_tablets
        if presc.dosage_mg and presc.duration_days:
            # Parse frequency to get doses per day
            freq_str = presc.frequency.lower()
            if 'once' in freq_str or '1 time' in freq_str:
                doses_per_day = 1
            elif 'twice' in freq_str or '2 times' in freq_str:
                doses_per_day = 2
            elif '3 times' in freq_str:
                doses_per_day = 3
            elif '4 times' in freq_str:
                doses_per_day = 4
            else:
                doses_per_day = 1  # default
            
            presc.total_mg = presc.dosage_mg * doses_per_day * presc.duration_days
            
            # Calculate tablets
            if presc.atc_drug_id:
                atc_drug = ATCDrug.query.get(presc.atc_drug_id)
                if atc_drug and atc_drug.ddd:
                    # DDD is in grams, convert to mg
                    tablet_strength_mg = atc_drug.ddd * 1000
                    presc.tablets_per_dose = int(presc.dosage_mg / tablet_strength_mg) if tablet_strength_mg > 0 else 1
                    presc.total_tablets = presc.tablets_per_dose * doses_per_day * presc.duration_days
                    
                    # Calculate DDDs
                    ddd_mg = tablet_strength_mg
                    if ddd_mg > 0:
                        presc.ddds = presc.total_mg / ddd_mg
                else:
                    # Fallback: assume 500mg per tablet
                    presc.tablets_per_dose = int(presc.dosage_mg / 500)
                    presc.total_tablets = presc.tablets_per_dose * doses_per_day * presc.duration_days
            else:
                # Fallback: assume 500mg per tablet
                presc.tablets_per_dose = int(presc.dosage_mg / 500)
                presc.total_tablets = presc.tablets_per_dose * doses_per_day * presc.duration_days
        
        db.session.add(presc)
        
        # Check for antimicrobial stewardship alerts
        # Basic check: if more than 2 prescriptions for antibiotics in last 30 days
        recent_prescs = Prescription.query.filter(
            Prescription.patient_id == presc.patient_id,
            Prescription.created_at >= datetime.now() - timedelta(days=30)
        ).all()
        
        if len(recent_prescs) >= 2:
            # Create alert
            alert = Alert(
                patient_id=presc.patient_id,
                user_id=user_id,
                alert_type='antimicrobial_stewardship',
                message='Possible antibiotic overuse detected. Review patient prescription history before prescribing.',
                severity='warning'
            )
            db.session.add(alert)
        
        # Recalculate risk score when prescription is created
        try:
            recalculate_risk_on_prescription(presc.patient_id)
        except Exception as e:
            print(f"Error recalculating risk score: {e}")
            # Don't fail the prescription creation if risk recalculation fails
        
        # Create audit log
        audit = AuditLog(
            user_id=user_id,
            action='create_prescription',
            entity_type='prescription',
            entity_id=presc.id,
            details=f"Created prescription for {presc.medication}"
        )
        db.session.add(audit)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error committing prescription: {e}")
            return jsonify({"msg": "Failed to create prescription due to database error"}), 500
        
        return jsonify(presc.to_dict()), 201


@app.route('/api/prescriptions/<int:presc_id>', methods=['GET', 'PUT'])
@jwt_required()
def prescription_detail(presc_id):
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    presc = Prescription.query.get_or_404(presc_id)
    
    if request.method == 'GET':
        # Check if user can access
        if user.role in ['doctor', 'pharmacist', 'admin', 'hospital_admin']:
            return jsonify(presc.to_dict())
        else:
            lang = get_request_lang()
            return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403
    
    if request.method == 'PUT':
        data = request.get_json()
        
        if user.role == 'pharmacist' and ('status' in data):
            # Pharmacist can only update status to approved/rejected/dispensed
            if data['status'] == 'approved':
                presc.status = 'approved'
                presc.approved_by = user_id
                presc.approved_at = datetime.now()
            elif data['status'] == 'rejected':
                presc.status = 'rejected'
                presc.rejection_reason = data.get('rejection_reason')
            elif data['status'] == 'dispensed':
                presc.status = 'dispensed'
                presc.dispensed_by = user_id
                presc.dispensed_at = datetime.now()
                presc.stock_updated = data.get('stock_updated', False)
            
            # Create audit log
            audit = AuditLog(
                user_id=user_id,
                action=f"{data['status']}_prescription",
                entity_type='prescription',
                entity_id=presc.id,
                details=f"{data['status'].capitalize()} prescription for {presc.medication}"
            )
            db.session.add(audit)
            
            db.session.commit()
            return jsonify(presc.to_dict())
        elif user.role in ['doctor', 'admin', 'hospital_admin']:
            # Doctor or admin can update other fields
            for key, value in data.items():
                if hasattr(presc, key):
                    setattr(presc, key, value)
            
            # Create audit log
            audit = AuditLog(
                user_id=user_id,
                action='update_prescription',
                entity_type='prescription',
                entity_id=presc.id,
                details=f"Updated prescription {presc.id}"
            )
            db.session.add(audit)
            
            db.session.commit()
            return jsonify(presc.to_dict())
        else:
            lang = get_request_lang()
            return jsonify({"msg": I18N["ACCESS_DENIED"][lang]}), 403


# Dashboard
@app.route('/api/dashboard')
@jwt_required()
def dashboard():
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    role = user.role
    
    # Base response structure
    response = {
        'role': role,
        'alert_stats': {
            'total': 0,
            'unread': 0,
            'stewardship': 0
        },
        'recent_activity': []
    }
    
    # Universal stats for all roles that should see them
    total_detailed_lab_results = DetailedLabResult.query.count()
    total_antibiotic_resistance_records = AntibioticResistance.query.count()
    total_atc_drugs = ATCDrug.query.count()
    total_diagnoses = Diagnosis.query.count()
    total_treatments = Treatment.query.count()
    total_hospitals = Hospital.query.count()
    
    # Calculate patient risk levels using DB counts (avoids loading all patients into memory)
    total_patients = Patient.query.count()
    # High risk: tb_status_label=Yes OR genexpert=Positive OR (sputum=Positive AND chest_xray=Abnormal)
    high_risk_patients = Patient.query.filter(
        db.or_(
            Patient.tb_status_label == 'Yes',
            Patient.genexpert_test == 'Positive',
        )
    ).count()
    medium_risk_patients = Patient.query.filter(
        db.and_(
            Patient.tb_status_label != 'Yes',
            Patient.genexpert_test != 'Positive',
            db.or_(
                Patient.sputum_smear_test == 'Positive',
                Patient.chest_xray == 'Abnormal',
            )
        )
    ).count()
    low_risk_patients = max(0, total_patients - high_risk_patients - medium_risk_patients)
    recent_patients = Patient.query.filter(
        Patient.created_at >= datetime.now() - timedelta(days=30)
    ).count()
    
    response['patient_stats'] = {
        'total': total_patients,
        'high_risk': high_risk_patients,
        'medium_risk': medium_risk_patients,
        'low_risk': low_risk_patients,
        'recent': recent_patients
    }
    response['hospital_stats'] = { 'total': total_hospitals }
    response['detailed_lab_stats'] = { 'total': total_detailed_lab_results }
    response['antimicrobial_resistance_stats'] = { 'total': total_antibiotic_resistance_records }
    response['atc_drug_stats'] = { 'total': total_atc_drugs }
    response['diagnosis_stats'] = { 'total': total_diagnoses }
    response['treatment_stats'] = { 'total': total_treatments }
    
    if role in ['admin', 'hospital_admin']:
        # Admin dashboard: Full stats
        total_alerts = Alert.query.count()
        unread_alerts = Alert.query.filter_by(is_read=False).count()
        stewardship_alerts = Alert.query.filter_by(alert_type='antimicrobial_stewardship').count()
        requested_lab_tests = LabTest.query.filter_by(status='requested').count()
        completed_lab_tests = LabTest.query.filter_by(status='completed').count()
        pending_prescriptions = Prescription.query.filter_by(status='pending').count()
        approved_prescriptions = Prescription.query.filter_by(status='approved').count()
        rejected_prescriptions = Prescription.query.filter_by(status='rejected').count()
        recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(20).all()
        
        model_info = {}
        model_info_path = os.path.join(os.path.dirname(__file__), 'models', 'model_info.json')
        if os.path.exists(model_info_path):
            with open(model_info_path, 'r', encoding='utf-8') as f:
                model_info = json.load(f)
        
        response['lab_test_stats'] = {
            'requested': requested_lab_tests,
            'completed': completed_lab_tests
        }
        response['prescription_stats'] = {
            'pending': pending_prescriptions,
            'approved': approved_prescriptions,
            'rejected': rejected_prescriptions
        }
        response['model_info'] = model_info
        response['recent_activity'] = [audit.to_dict() for audit in recent_audits]
        response['alert_stats'] = {
            'total': total_alerts,
            'unread': unread_alerts,
            'stewardship': stewardship_alerts
        }
    
    elif role == 'doctor':
        # Doctor dashboard
        unread_alerts = Alert.query.filter_by(is_read=False, user_id=user_id).count()
        stewardship_alerts = Alert.query.filter_by(alert_type='antimicrobial_stewardship').count()
        requested_lab_tests = LabTest.query.filter_by(requested_by=user_id, status='requested').count()
        completed_lab_tests = DetailedLabResult.query.count()
        recent_audits = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.created_at.desc()).limit(10).all()
        pending_prescriptions = Prescription.query.filter_by(status='pending').count()
        approved_prescriptions = Prescription.query.filter_by(status='approved').count()
        rejected_prescriptions = Prescription.query.filter_by(status='rejected').count()
        
        response['lab_test_stats'] = {
            'requested': requested_lab_tests,
            'completed': completed_lab_tests
        }
        response['prescription_stats'] = {
            'pending': pending_prescriptions,
            'approved': approved_prescriptions,
            'rejected': rejected_prescriptions
        }
        response['alert_stats']['unread'] = unread_alerts
        response['alert_stats']['stewardship'] = stewardship_alerts
        response['recent_activity'] = [audit.to_dict() for audit in recent_audits]
    
    elif role == 'lab_technician':
        # Lab tech dashboard: Only lab tests
        requested_lab_tests = LabTest.query.filter_by(status='requested').count()
        in_progress_lab_tests = LabTest.query.filter_by(status='in_progress').count()
        completed_lab_tests = LabTest.query.filter_by(status='completed', completed_by=user_id).count()
        recent_audits = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.created_at.desc()).limit(10).all()
        
        response['lab_test_stats'] = {
            'requested': requested_lab_tests,
            'in_progress': in_progress_lab_tests,
            'completed_by_me': completed_lab_tests
        }
        response['prescription_stats'] = {
            'pending': Prescription.query.filter_by(status='pending').count(),
            'approved': Prescription.query.filter_by(status='approved').count(),
            'rejected': Prescription.query.filter_by(status='rejected').count()
        }
        response['recent_activity'] = [audit.to_dict() for audit in recent_audits]
    
    elif role == 'pharmacist':
        # Pharmacist dashboard: Only prescriptions
        pending_prescriptions = Prescription.query.filter_by(status='pending').count()
        approved_prescriptions = Prescription.query.filter_by(status='approved', approved_by=user_id).count()
        rejected_prescriptions = Prescription.query.filter_by(status='rejected', approved_by=user_id).count()
        recent_audits = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.created_at.desc()).limit(10).all()
        
        response['prescription_stats'] = {
            'pending': pending_prescriptions,
            'approved': Prescription.query.filter_by(status='approved').count(),
            'rejected': Prescription.query.filter_by(status='rejected').count()
        }
        response['recent_activity'] = [audit.to_dict() for audit in recent_audits]
    
    return jsonify(response)


# Cumulative Antibiogram
@app.route('/api/antibiogram')
@jwt_required()
def antibiogram():
    # Sample antibiogram data - in a real system this would aggregate from DST/Lab results
    antibiogram_data = [
        {
            'bacteria': 'Mycobacterium tuberculosis complex',
            'isoniazid': 85,
            'rifampicin': 78,
            'pyrazinamide': 90,
            'ethambutol': 92,
            'streptomycin': 70,
            'fluoroquinolones': 82
        },
        {
            'bacteria': 'Escherichia coli',
            'amoxicillin': 68,
            'ceftriaxone': 82,
            'ciprofloxacin': 75,
            'gentamicin': 90,
            'meropenem': 98
        },
        {
            'bacteria': 'Staphylococcus aureus',
            'amoxicillin': 35,
            'ceftriaxone': 58,
            'ciprofloxacin': 62,
            'gentamicin': 78,
            'meropenem': 95
        },
        {
            'bacteria': 'Klebsiella pneumoniae',
            'amoxicillin': 42,
            'ceftriaxone': 70,
            'ciprofloxacin': 65,
            'gentamicin': 85,
            'meropenem': 96
        }
    ]
    
    return jsonify({'antibiogram': antibiogram_data})

# Audit Logs
@app.route('/api/audit-logs', methods=['GET'])
@jwt_required()
@role_required('admin', 'hospital_admin')
def audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'audit_logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])  
@jwt_required()
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'GET':
        return jsonify({
            'patient': patient.to_dict(),
            'diagnoses': [d.to_dict() for d in patient.diagnoses],
            'treatments': [t.to_dict() for t in patient.treatments],
            'alerts': [a.to_dict() for a in patient.alerts],
            'detailed_lab_results': [r.to_dict() for r in patient.detailed_lab_results],
            'antibiotic_resistance_records': [r.to_dict() for r in patient.antibiotic_resistance_records]
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
        if user.role not in ['admin', 'hospital_admin']:
            return jsonify({'msg': tr('ACCESS_DENIED')}), 403

        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': tr('PATIENT_DELETED')})

@app.route('/api/patients/<int:patient_id>/drug-resistance', methods=['GET'])
@jwt_required()
def get_patient_drug_resistance(patient_id):
    """
    Get drug resistance information from patient's previous records.
    Checks prescriptions and antibiotic resistance records.
    """
    patient = Patient.query.get_or_404(patient_id)
    
    resistance_patterns = []
    
    # Check patient's current drug_resistance field
    if patient.drug_resistance and patient.drug_resistance.strip():
        resistance_patterns.append(patient.drug_resistance)
    
    # Check antibiotic resistance records
    for record in patient.antibiotic_resistance_records:
        if record.resistance_pattern and record.resistance_pattern not in resistance_patterns:
            resistance_patterns.append(record.resistance_pattern)
    
    # Check previous prescriptions for resistance indicators
    from models.models import Prescription
    previous_prescriptions = Prescription.query.filter_by(
        patient_id=patient_id
    ).order_by(Prescription.created_at.desc()).limit(10).all()
    
    resistance_drugs = set()
    for presc in previous_prescriptions:
        if presc.medication:
            # Check if medication contains resistance indicators
            med_lower = presc.medication.lower()
            if 'resistant' in med_lower or 'mdr' in med_lower or 'xdr' in med_lower:
                if presc.medication not in resistance_patterns:
                    resistance_patterns.append(presc.medication)
    
    # Combine all resistance information
    combined_resistance = '; '.join(resistance_patterns) if resistance_patterns else ''
    
    return jsonify({
        'patient_id': patient_id,
        'drug_resistance': combined_resistance,
        'resistance_patterns': resistance_patterns,
        'has_resistance': len(resistance_patterns) > 0,
        'previous_prescriptions_count': len(previous_prescriptions)
    })

# Hospital Management
@app.route('/api/hospitals', methods=['GET', 'POST'])
@jwt_required()
def hospitals():
    if request.method == 'GET':
        hospitals = Hospital.query.order_by(Hospital.created_at.desc()).all()
        return jsonify({
            'hospitals': [h.to_dict() for h in hospitals],
            'total': len(hospitals)
        })
    
    if request.method == 'POST':
        user = get_current_user_from_jwt()
        if user.role not in ['admin', 'hospital_admin']:
            return jsonify({'msg': tr('ACCESS_DENIED')}), 403
        
        data = request.get_json()
        
        # Auto-generate hospital_id if not provided
        hospital_id = data.get('hospital_id')
        if not hospital_id:
            # Generate a unique hospital_id based on name and timestamp
            import time
            import hashlib
            name = data.get('name', '')
            timestamp = str(int(time.time()))
            hash_input = f"{name}_{timestamp}".encode()
            hospital_id = hashlib.md5(hash_input).hexdigest()[:12].upper()
        
        hospital = Hospital(
            hospital_id=hospital_id,
            name=data.get('name'),
            facility_type=data.get('facility_type', 'Hospital'),
            address=data.get('address'),
            city=data.get('city'),
            region=data.get('region'),
            country=data.get('country', 'Rwanda'),
            phone=data.get('phone'),
            email=data.get('email'),
            bed_capacity=data.get('bed_capacity'),
            icu_beds=data.get('icu_beds'),
            source_dataset='manual_entry'
        )
        db.session.add(hospital)
        db.session.commit()
        
        # Log the action
        audit = AuditLog(
            user_id=user.id,
            action='create_hospital',
            entity_type='hospital',
            entity_id=hospital.id,
            details=f"Created hospital: {hospital.name}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify(hospital.to_dict()), 201

@app.route('/api/hospitals/<int:hospital_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def hospital_detail(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    
    if request.method == 'GET':
        return jsonify({
            'hospital': hospital.to_dict(),
            'patients': [p.to_dict() for p in hospital.patients],
            'users': [u.to_dict() for u in hospital.users]
        })
    
    if request.method == 'PUT':
        user = get_current_user_from_jwt()
        if user.role not in ['admin', 'hospital_admin']:
            return jsonify({'msg': tr('ACCESS_DENIED')}), 403
        
        data = request.get_json()
        for key, value in data.items():
            if hasattr(hospital, key):
                setattr(hospital, key, value)
        db.session.commit()
        
        # Log the action
        audit = AuditLog(
            user_id=user.id,
            action='update_hospital',
            entity_type='hospital',
            entity_id=hospital.id,
            details=f"Updated hospital: {hospital.name}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify(hospital.to_dict())
    
    if request.method == 'DELETE':
        user = get_current_user_from_jwt()
        if user.role not in ['admin', 'hospital_admin']:
            return jsonify({'msg': tr('ACCESS_DENIED')}), 403
        
        db.session.delete(hospital)
        db.session.commit()
        
        # Log the action
        audit = AuditLog(
            user_id=user.id,
            action='delete_hospital',
            entity_type='hospital',
            entity_id=hospital_id,
            details=f"Deleted hospital: {hospital.name}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({'message': 'Hospital deleted successfully'})

# Pharmacy Inventory Management
@app.route('/api/pharmacy-inventory', methods=['GET', 'POST'])
@jwt_required()
def pharmacy_inventory():
    user = get_current_user_from_jwt()
    if user.role not in ['pharmacist', 'admin', 'hospital_admin']:
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    if request.method == 'GET':
        hospital_id = request.args.get('hospital_id', type=int)
        query = PharmacyInventory.query
        
        if hospital_id:
            query = query.filter_by(hospital_id=hospital_id)
        
        inventory = query.order_by(PharmacyInventory.created_at.desc()).all()
        return jsonify({
            'inventory': [inv.to_dict() for inv in inventory],
            'total': len(inventory)
        })
    
    if request.method == 'POST':
        data = request.get_json()
        inventory = PharmacyInventory(
            hospital_id=data.get('hospital_id'),
            atc_drug_id=data.get('atc_drug_id'),
            stock_quantity=data.get('stock_quantity', 0),
            unit_type=data.get('unit_type', 'tablets'),
            batch_number=data.get('batch_number'),
            expiry_date=pd.to_datetime(data.get('expiry_date')) if data.get('expiry_date') else None,
            location=data.get('location'),
            minimum_stock_level=data.get('minimum_stock_level', 10),
            last_restocked=datetime.now()
        )
        db.session.add(inventory)
        
        audit = AuditLog(
            user_id=user.id,
            action='create_inventory',
            entity_type='pharmacy_inventory',
            entity_id=inventory.id,
            details=f"Added inventory for drug ID {data.get('atc_drug_id')}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify(inventory.to_dict()), 201

@app.route('/api/pharmacy-inventory/<int:inventory_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def inventory_detail(inventory_id):
    user = get_current_user_from_jwt()
    if user.role not in ['pharmacist', 'admin', 'hospital_admin']:
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    inventory = PharmacyInventory.query.get_or_404(inventory_id)
    
    if request.method == 'GET':
        return jsonify(inventory.to_dict())
    
    if request.method == 'PUT':
        data = request.get_json()
        
        # Update stock quantity and log restock
        if 'stock_quantity' in data:
            old_quantity = inventory.stock_quantity
            inventory.stock_quantity = data['stock_quantity']
            if data['stock_quantity'] > old_quantity:
                inventory.last_restocked = datetime.now()
        
        for key, value in data.items():
            if hasattr(inventory, key) and key != 'stock_quantity':
                setattr(inventory, key, value)
        
        db.session.commit()
        
        audit = AuditLog(
            user_id=user.id,
            action='update_inventory',
            entity_type='pharmacy_inventory',
            entity_id=inventory.id,
            details=f"Updated inventory for {inventory.atc_drug.drug_name if inventory.atc_drug else 'unknown'}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify(inventory.to_dict())
    
    if request.method == 'DELETE':
        if user.role != 'admin':
            return jsonify({'msg': tr('ACCESS_DENIED')}), 403
        
        db.session.delete(inventory)
        db.session.commit()
        
        return jsonify({'message': 'Inventory item deleted'})

@app.route('/api/prescriptions/<int:presc_id>/check-stock', methods=['GET'])
@jwt_required()
def check_prescription_stock(presc_id):
    user = get_current_user_from_jwt()
    if user.role not in ['pharmacist', 'admin', 'hospital_admin']:
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    presc = Prescription.query.get_or_404(presc_id)
    
    if not presc.atc_drug_id:
        return jsonify({
            'available': False,
            'message': 'No ATC drug linked to this prescription'
        })
    
    # Get patient's hospital
    patient = Patient.query.get(presc.patient_id)
    if not patient or not patient.hospital_id:
        return jsonify({
            'available': False,
            'message': 'Patient hospital not found'
        })
    
    # Check inventory
    inventory = PharmacyInventory.query.filter_by(
        hospital_id=patient.hospital_id,
        atc_drug_id=presc.atc_drug_id
    ).first()
    
    if not inventory:
        return jsonify({
            'available': False,
            'message': 'Drug not in inventory',
            'stock_quantity': 0,
            'inventory_exists': False
        })
    
    required_quantity = presc.duration_days if presc.duration_days else 30  # Default 30 days
    available = inventory.stock_quantity >= required_quantity
    
    return jsonify({
        'available': available,
        'stock_quantity': inventory.stock_quantity,
        'required_quantity': required_quantity,
        'drug_name': inventory.atc_drug.drug_name if inventory.atc_drug else 'Unknown',
        'below_minimum': inventory.stock_quantity <= inventory.minimum_stock_level,
        'inventory_exists': True
    })

@app.route('/api/prescriptions/<int:presc_id>/dispense', methods=['POST'])
@jwt_required()
def dispense_prescription(presc_id):
    user = get_current_user_from_jwt()
    if user.role != 'pharmacist':
        return jsonify({'msg': tr('ACCESS_DENIED')}), 403
    
    presc = Prescription.query.get_or_404(presc_id)
    
    if presc.status != 'approved':
        return jsonify({
            'error': 'Prescription must be approved before dispensing'
        }), 400
    
    # Get patient's hospital
    patient = Patient.query.get(presc.patient_id)
    if not patient or not patient.hospital_id:
        return jsonify({'error': 'Patient hospital not found'}), 400
    
    # Check and update inventory
    if presc.atc_drug_id:
        inventory = PharmacyInventory.query.filter_by(
            hospital_id=patient.hospital_id,
            atc_drug_id=presc.atc_drug_id
        ).first()
        
        if inventory:
            # Use pre-calculated total_tablets if available, otherwise calculate
            if presc.total_tablets:
                required_quantity = presc.total_tablets
            elif presc.dosage_mg and presc.duration_days:
                # Fallback calculation
                atc_drug = ATCDrug.query.get(presc.atc_drug_id)
                if atc_drug and atc_drug.ddd:
                    tablet_strength_mg = atc_drug.ddd * 1000
                    required_quantity = int((presc.dosage_mg * presc.duration_days) / tablet_strength_mg)
                else:
                    required_quantity = int((presc.dosage_mg * presc.duration_days) / 500)
            else:
                required_quantity = presc.duration_days if presc.duration_days else 30
            
            if inventory.stock_quantity < required_quantity:
                return jsonify({
                    'error': 'Insufficient stock',
                    'stock_quantity': inventory.stock_quantity,
                    'required_quantity': required_quantity,
                    'unit': inventory.unit_type,
                    'total_tablets_needed': presc.total_tablets,
                    'tablets_per_dose': presc.tablets_per_dose,
                    'frequency': presc.frequency
                }), 400
            
            # Update stock - reduce by actual quantity dispensed
            inventory.stock_quantity -= required_quantity
            presc.stock_updated = True
    
    # Update prescription
    presc.status = 'dispensed'
    presc.dispensed_by = user.id
    presc.dispensed_at = datetime.now()
    
    # Create audit log
    audit = AuditLog(
        user_id=user.id,
        action='dispense_prescription',
        entity_type='prescription',
        entity_id=presc.id,
        details=f"Dispensed {presc.medication} to patient {presc.patient_id}"
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify(presc.to_dict())

# Comprehensive Diagnosis with WHO Standards
@app.route('/api/diagnose', methods=['POST'])
@jwt_required()
def diagnose():
    data = request.get_json() or {}
    patient_data = data.get('patient', {}) or {}
    user = get_current_user_from_jwt()
    lang = get_request_lang()
    user_id = user.id

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
            "weight",
            "city",
            "symptoms",
            "exposure_history",
            "persistent_cough_duration_weeks",
            "contact_with_tb_patient",
            "previous_tb_treatment",
            "sputum_smear_test",
            "genexpert_test",
            "chest_xray",
            "tb_culture",
            "tst",
            "igra",
            "bacteria_species",
            "drug_resistance",
            "hiv",
            "diabetes",
            "smoking_status",
            "alcohol_use",
            "oxygen_saturation_spo2",
            "antibiotic_usage_history",
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
            red_flags.append(tr("RED_FLAG_HEMOPTYSIS", lang=lang))
        if symptoms_present.get("neck_stiffness") or symptoms_present.get("confusion") or symptoms_present.get("headache_severe"):
            red_flags.append(tr("RED_FLAG_CNS", lang=lang))
        if symptoms_present.get("dyspnea"):
            red_flags.append(tr("RED_FLAG_BREATHLESSNESS", lang=lang))

        clinical_advice = tr("SYMPTOM_ADVICE_DEFAULT", lang=lang)
        if risk_level == "HIGH RISK":
            clinical_advice = tr("SYMPTOM_ADVICE_HIGH", lang=lang)
        elif risk_level == "MODERATE RISK":
            clinical_advice = tr("SYMPTOM_ADVICE_MODERATE", lang=lang)
        elif risk_level == "LOW RISK":
            clinical_advice = tr("SYMPTOM_ADVICE_LOW", lang=lang)

        return {
            "risk_level": risk_level,
            "risk_level_display": (I18N.get("RISK_LEVEL_DISPLAY", {}).get(risk_level, {}).get(lang) or risk_level),
            "risk_score": score,
            "red_flags": red_flags,
            "clinical_advice": clinical_advice,
        }

    def evaluate_tests(sputum, genexpert, chest_xray, tb_culture=None, tst=None, igra=None):
        sputum = sputum or "Unknown"
        genexpert = genexpert or "Unknown"
        chest_xray = chest_xray or "Unknown"
        tb_culture = tb_culture or "Unknown"
        tst = tst or "Unknown"
        igra = igra or "Unknown"

        findings = []
        confidence = 40
        classification = tr("TEST_CLASS_INSUFFICIENT", lang=lang)

        if genexpert == "Positive":
            findings.append(tr("FINDING_GENEXPERT_POS", lang=lang))
            classification = tr("TEST_CLASS_CONFIRMED_LIKELY", lang=lang)
            confidence = 95
        if sputum == "Positive":
            findings.append(tr("FINDING_SPUTUM_POS", lang=lang))
            classification = tr("TEST_CLASS_CONFIRMED_LIKELY", lang=lang)
            confidence = max(confidence, 85)
        if tb_culture == "Positive":
            findings.append("TB Culture positive (gold standard confirmation)")
            classification = tr("TEST_CLASS_CONFIRMED", lang=lang)
            confidence = 98  # Culture is gold standard
        if chest_xray == "Abnormal":
            findings.append(tr("FINDING_CXR_ABNORMAL", lang=lang))
            confidence = max(confidence, 60)
        if tst == "Positive":
            findings.append("Tuberculin Skin Test (TST) positive")
            if classification == tr("TEST_CLASS_INSUFFICIENT", lang=lang):
                classification = "Possible latent TB infection"
                confidence = 50
        if igra == "Positive":
            findings.append("IGRA positive")
            if classification == tr("TEST_CLASS_INSUFFICIENT", lang=lang):
                classification = "Possible latent TB infection"
                confidence = 55
        if genexpert == "Negative" and sputum == "Negative" and chest_xray == "Normal" and tb_culture in ["Negative", "Unknown"]:
            findings.append(tr("FINDING_ALL_NEGATIVE", lang=lang))
            classification = tr("TEST_CLASS_LESS_LIKELY", lang=lang)
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
    localized_who_category = translate_backend_text_value(tb_analysis["who_category"], lang=lang)
    localized_tb_types = localize_payload(tb_analysis["tb_types"], lang=lang)
    bacteria_assessment = localize_payload(build_bacteria_assessment(species_result, tb_analysis), lang=lang)
    infection_assessment = build_infection_assessment(tb_analysis, bacteria_assessment, lang=lang)

    # Get WHO clinical info
    clinical_info = localize_payload(get_who_clinical_info(
        tb_analysis['who_category'],
        patient.symptoms or '',
        patient.sputum_smear_test or 'Unknown',
        patient.genexpert_test or 'Unknown',
        patient.chest_xray or 'Unknown',
        patient.hiv or 'No',
        patient.drug_resistance or 'No'
    ), lang=lang)

    # Get WHO Treatment Regimen
    treatment = localize_payload(get_who_treatment_regimen(
        tb_analysis['who_category'],
        patient.hiv or 'No',
        patient.drug_resistance or 'No'
    ), lang=lang)

    # Get detailed prescription recommendation with drug dosages
    from medicine_recommendation import get_prescription_recommendation
    
    # Determine infection type for prescription recommendation (only if risk is sufficient)
    infection_type = None
    if patient.risk_score and patient.risk_score >= 50:  # Only recommend if risk is at least moderate
        if 'pulmonary' in tb_analysis['who_category'].lower():
            infection_type = 'pulmonary_positive'
        elif 'extrapulmonary' in tb_analysis['who_category'].lower():
            infection_type = 'extrapulmonary'
        elif 'latent' in tb_analysis['who_category'].lower():
            infection_type = 'latent'
        elif patient.hiv == 'Yes':
            infection_type = 'tb_hiv'
    
    # Compute ML prediction first to base everything on it
    ml_prediction = predict_ml(patient)
    
    # Pass ML prediction to prescription recommendation
    prescription_recommendation = get_prescription_recommendation(patient.id, infection_type, ml_prediction)
    
    # Extract detailed medicines if available (only if TB is actually detected)
    detailed_medicines = []
    if prescription_recommendation and 'medicines' in prescription_recommendation and prescription_recommendation.get('recommendation') != 'No medication needed':
        detailed_medicines = prescription_recommendation['medicines']
    resistance_profile = determine_resistance_profile(
        patient.drug_resistance or 'No',
        patient.genexpert_test or 'Unknown',
        patient_data.get('antibiogram_result'),
        patient_data.get('resistant_to'),
        patient_data.get('susceptible_to'),
    )
    treatment, clinical_info = apply_species_treatment_adjustments(treatment, clinical_info, bacteria_assessment)
    treatment = localize_payload(treatment, lang=lang)
    clinical_info = localize_payload(clinical_info, lang=lang)
    treatment_plan = localize_payload(
        build_treatment_plan(tb_analysis, bacteria_assessment, resistance_profile, treatment, clinical_info),
        lang=lang,
    )

    # Determine if alert should be created
    alert_created = None
    symptom_analysis = compute_symptom_analysis(patient.symptoms or "")
    test_evaluation = evaluate_tests(patient.sputum_smear_test, patient.genexpert_test, patient.chest_xray, tb_culture, tst, igra)
    if tb_culture and tb_culture != 'Unknown':
        test_evaluation["findings"].append(f"{tr('LABEL_TB_CULTURE', lang=lang)}: {tb_culture}")
    if tst and tst != 'Unknown':
        test_evaluation["findings"].append(f"{tr('LABEL_TST', lang=lang)}: {tst}")
    if igra and igra != 'Unknown':
        test_evaluation["findings"].append(f"{tr('LABEL_IGRA', lang=lang)}: {igra}")
    if resistance_profile["antibiogram_result"] != "Not provided":
        test_evaluation["findings"].append(f"{tr('LABEL_DST', lang=lang)}: {resistance_profile['antibiogram_result']}")

    diagnosis_record = Diagnosis(
        patient_id=patient.id,
        clinician_id=user.id,
        diagnosis_type=tb_analysis['who_category'],
        risk_level=symptom_analysis["risk_level"],
        confidence_percent=test_evaluation["confidence_percent"],
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

    # Only create treatment record if ML predicts TB
    treatment_record = None
    if ml_prediction and ml_prediction.get('tb_status', {}).get('prediction') == 'Yes':
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
        db.session.flush()
    else:
        print(f"DEBUG: No treatment record created - ML predicts no TB")

    # Initialize prescription variable
    prescription = None

    # Only create prescription if ML prediction indicates TB and risk score is sufficient
    # Base decision on ML prediction (yes/no) and risk score, not WHO category
    print(f"DEBUG: ML Prediction = {ml_prediction}")
    print(f"DEBUG: Risk Score = {patient.risk_score}")
    
    # Check if ML predicts TB and risk score is above threshold
    tb_detected = (
        ml_prediction and 
        ml_prediction.get('tb_status', {}).get('prediction') == 'Yes' and
        patient.risk_score and
        patient.risk_score >= 30  # Minimum risk score threshold
    )
    
    print(f"DEBUG: TB Detected (based on ML) = {tb_detected}")
    
    if tb_detected:
        # Automatically create ML-recommended prescription
        atc_drug = ATCDrug.query.filter(
            ATCDrug.drug_name.ilike("%isoniazid%") | ATCDrug.drug_name.ilike("%rifampicin%")
        ).first()

        # Parse dosage from treatment record to calculate tablets
        dosage_mg = 300  # Default for isoniazid/rifampicin
        frequency = "once daily"
        duration_days = 180  # Default 6 months for TB treatment
        
        # Try to extract dosage from treatment record
        if treatment_record and treatment_record.dosage:
            dosage_str = str(treatment_record.dosage).lower()
            # Extract mg value if present
            import re
            mg_match = re.search(r'(\d+)\s*mg', dosage_str)
            if mg_match:
                dosage_mg = int(mg_match.group(1))
            
            # Extract frequency
            if 'twice' in dosage_str or '2 times' in dosage_str or 'bid' in dosage_str:
                frequency = "twice daily"
            elif '3 times' in dosage_str or 'tid' in dosage_str:
                frequency = "3 times daily"
            elif 'once' in dosage_str or '1 time' in dosage_str or 'qd' in dosage_str:
                frequency = "once daily"
        
        # Extract duration from treatment record
        if treatment_record and treatment_record.duration:
            duration_str = str(treatment_record.duration).lower()
            months_match = re.search(r'(\d+)\s*months?', duration_str)
            if months_match:
                duration_days = int(months_match.group(1)) * 30
            else:
                days_match = re.search(r'(\d+)\s*days?', duration_str)
                if days_match:
                    duration_days = int(days_match.group(1))
        
        # Calculate doses per day
        freq_str = frequency.lower()
        if 'once' in freq_str or '1 time' in freq_str:
            doses_per_day = 1
        elif 'twice' in freq_str or '2 times' in freq_str:
            doses_per_day = 2
        elif '3 times' in freq_str:
            doses_per_day = 3
        else:
            doses_per_day = 1
        
        # Calculate tablets
        tablets_per_dose = 1  # Default
        if atc_drug and atc_drug.ddd:
            tablet_strength_mg = atc_drug.ddd * 1000
            tablets_per_dose = int(dosage_mg / tablet_strength_mg) if tablet_strength_mg > 0 else 1
        else:
            tablets_per_dose = int(dosage_mg / 500) if dosage_mg >= 500 else 1
        
        total_tablets = tablets_per_dose * doses_per_day * duration_days

        prescription = Prescription(
            patient_id=patient.id,
            diagnosis_id=diagnosis_record.id,
            created_by=user.id,
            medication=treatment_plan["selected_option"]["drugs"],
            atc_drug_id=atc_drug.id if atc_drug else None,
            dosage=treatment_record.dosage if treatment_record else dosage_mg,
            duration=treatment_record.duration if treatment_record else f"{duration_days} days",
            risk_level=symptom_analysis["risk_level"],
            ml_recommended=True,
            status="pending",
            dosage_mg=dosage_mg,
            frequency=frequency,
            duration_days=duration_days,
            tablets_per_dose=tablets_per_dose,
            total_tablets=total_tablets
        )
        db.session.add(prescription)
        print(f"DEBUG: Prescription created for patient {patient.patient_id} with {total_tablets} total tablets")
    else:
        print(f"DEBUG: No prescription created - ML prediction: {ml_prediction.get('tb_status', {}).get('prediction') if ml_prediction else 'N/A'}, Risk: {patient.risk_score}")

    # Check for antibiotic misuse
    recent_prescriptions = Prescription.query.filter(
        Prescription.patient_id == patient.id,
        Prescription.created_at >= datetime.now() - timedelta(days=90)
    ).all()

    misuse_detected = False
    misuse_reason = ""
    if len(recent_prescriptions) >= 3:
        misuse_detected = True
        misuse_reason = "Multiple antibiotic prescriptions in last 90 days"
    if patient.antibiotic_usage_history and "without prescription" in patient.antibiotic_usage_history.lower():
        misuse_detected = True
        misuse_reason = "Reported antibiotic use without prescription"

    if misuse_detected:
        alert = Alert(
            patient_id=patient.id,
            user_id=user.id,
            alert_type="antimicrobial_stewardship",
            message=f"Possible antibiotic misuse detected: {misuse_reason}. Review patient history.",
            severity="high"
        )
        db.session.add(alert)
        alert_created = alert

    urgency = treatment.get("priority", "MODERATE")
    treatment_recommendation = {
        "type": clinical_info.get("diagnosis", tb_analysis["who_category"]),
        "category": localized_who_category,
        "bacteria_species": bacteria_assessment["species"],
        "infection_type": infection_assessment["primary_infection"],
        "resistance_class": resistance_profile["classification"],
        "regimen_name": treatment_plan["selected_option"]["name"],
        "regimen_level": treatment_plan["selected_option"]["level"],
        "duration": treatment_plan["selected_option"]["duration"],
        "drugs": treatment_plan["selected_option"]["drugs"],
        "dosage": treatment_record.dosage if treatment_record else treatment_plan["selected_option"]["administration"],
        "administration": treatment_plan["selected_option"]["administration"],
        "monitoring": treatment_plan["selected_option"]["monitoring"],
        "urgency": urgency,
        "notes": treatment_plan["selected_option"]["notes"],
        "guideline_source": treatment_plan["guideline_source"],
        "decision_basis": treatment_plan["decision_basis"],
        "treatment_options": treatment_plan["options"],
        "medicines": detailed_medicines if detailed_medicines else [],
        "recommendation": prescription_recommendation.get('recommendation') if prescription_recommendation else 'No medication needed'
    }

    if 'CONFIRMED' in tb_analysis['who_category'] or 'URGENT' in urgency or 'CRITICAL' in urgency:
        alert_created = create_alert(
            patient_id=patient.id,
            user_id=user.id,
            alert_type=tr("ALERT_LABEL", lang=lang),
            message=tr(
                "ALERT_MESSAGE_TEMPLATE",
                lang=lang,
                patient_name=patient_name,
                patient_id=patient.patient_id,
                category=localized_who_category,
                species=bacteria_assessment['species'],
                who_recommendation=clinical_info.get('who_recommendation', ''),
            ),
            severity='high'
        )

    db.session.commit()

    # Create audit log for diagnosis
    audit = AuditLog(
        user_id=user_id,
        action='create_diagnosis',
        entity_type='diagnosis',
        entity_id=diagnosis_record.id,
        details=f'Diagnosis created for patient {patient.patient_id}: {localized_who_category}',
        created_at=datetime.now()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "patient_name": patient_name,
        "patient_id": patient.patient_id,
        "symptom_analysis": symptom_analysis,
        "test_evaluation": test_evaluation,
        "who_standards": {
            "tb_types": localized_tb_types,
            "primary_diagnosis": localized_who_category,
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
        "saved_treatment": treatment_record.to_dict() if treatment_record else None,
        "saved_prescription": prescription.to_dict() if prescription else None,
        "alert_created": alert_created.id if alert_created else None,
    })
    
    # Recalculate risk score when diagnosis is made
    try:
        recalculate_risk_on_diagnosis(patient.id)
    except Exception as e:
        print(f"Error recalculating risk score: {e}")

@app.route('/api/diagnoses', methods=['GET'])
@jwt_required()
def get_diagnoses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Diagnosis.query.order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    diagnoses = [d.to_dict() for d in pagination.items]
    return jsonify({
        'diagnoses': diagnoses, 
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

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
@role_required('admin')
def train_model_endpoint():
    try:
        result = train_models_from_database()
        load_models()
        return jsonify(result)
    except Exception as e:
        print(f"Model training failed: {e}")
        return jsonify({'error': tr('TRAIN_MODEL_FAILED')}), 500

@app.route('/api/import-data', methods=['POST'])
@role_required('admin')
def import_data_endpoint():
    try:
        from import_data import main
        main()
        return jsonify({'message': tr('DATA_IMPORT_OK')})
    except Exception as e:
        print(f"Data import failed: {e}")
        return jsonify({'error': tr('IMPORT_DATA_FAILED')}), 500


@app.route('/api/dashboard/charts')
@jwt_required()
def dashboard_charts():
    from sqlalchemy import func, case

    # 1. Patient Risk Level distribution (bar)
    high = Patient.query.filter(
        db.or_(Patient.tb_status_label == 'Yes', Patient.genexpert_test == 'Positive')
    ).count()
    medium = Patient.query.filter(
        db.and_(
            Patient.tb_status_label != 'Yes', Patient.genexpert_test != 'Positive',
            db.or_(Patient.sputum_smear_test == 'Positive', Patient.chest_xray == 'Abnormal')
        )
    ).count()
    total = Patient.query.count()
    low = max(0, total - high - medium)
    risk_chart = {
        'labels': ['High Risk', 'Medium Risk', 'Low Risk'],
        'data': [high, medium, low],
        'colors': ['#ef4444', '#f59e0b', '#10b981']
    }

    # 2. TB Status breakdown (doughnut)
    tb_positive = Patient.query.filter(Patient.tb_status_label == 'Yes').count()
    tb_negative = Patient.query.filter(Patient.tb_status_label == 'No').count()
    tb_unknown = total - tb_positive - tb_negative
    tb_status_chart = {
        'labels': ['TB Positive', 'TB Negative', 'Unknown'],
        'data': [tb_positive, tb_negative, tb_unknown],
        'colors': ['#ef4444', '#10b981', '#6b7280']
    }

    # 3. Drug Resistance distribution (bar)
    dr_yes = Patient.query.filter(Patient.drug_resistance == 'Yes').count()
    dr_no = Patient.query.filter(Patient.drug_resistance == 'No').count()
    dr_unknown = total - dr_yes - dr_no
    resistance_chart = {
        'labels': ['Resistant', 'Sensitive', 'Unknown'],
        'data': [dr_yes, dr_no, dr_unknown],
        'colors': ['#f97316', '#06b6d4', '#6b7280']
    }

    # 4. Antibiogram – resistance rates per antibiotic from AntibioticResistance table (bar)
    ab_fields = [
        ('amx_amp', 'AMX/AMP'), ('amc', 'AMC'), ('cz', 'CZ'), ('fox', 'FOX'),
        ('ctx_cro', 'CTX/CRO'), ('ipm', 'IPM'), ('gen', 'GEN'), ('an', 'AN'),
        ('ofx', 'OFX'), ('cip', 'CIP'), ('chloramphenicol', 'CHL'),
        ('co_trimoxazole', 'SXT'), ('colistine', 'CST')
    ]
    ar_total = AntibioticResistance.query.count()
    antibiogram_labels, antibiogram_data = [], []
    if ar_total > 0:
        for col_name, label in ab_fields:
            col = getattr(AntibioticResistance, col_name)
            r_count = AntibioticResistance.query.filter(col == 'R').count()
            pct = round(r_count / ar_total * 100, 1)
            antibiogram_labels.append(label)
            antibiogram_data.append(pct)
    antibiogram_chart = {
        'labels': antibiogram_labels,
        'data': antibiogram_data,
        'title': 'Antibiotic Resistance Rate (%)'
    }

    # 5. Top bacterial species from AntibioticResistance (horizontal bar)
    species_rows = db.session.query(
        AntibioticResistance.bacterial_species,
        func.count(AntibioticResistance.id).label('cnt')
    ).filter(AntibioticResistance.bacterial_species.isnot(None)) \
     .group_by(AntibioticResistance.bacterial_species) \
     .order_by(func.count(AntibioticResistance.id).desc()) \
     .limit(8).all()
    species_chart = {
        'labels': [r.bacterial_species for r in species_rows],
        'data': [r.cnt for r in species_rows],
        'colors': ['#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#f97316', '#3b82f6', '#ec4899']
    }

    # 6. Key symptom prevalence (horizontal bar)
    symptom_fields = [
        (Patient.has_fever, 'Fever'), (Patient.has_cough, 'Cough'),
        (Patient.has_weight_loss, 'Weight Loss'), (Patient.has_night_sweats, 'Night Sweats'),
        (Patient.has_chest_pain, 'Chest Pain'), (Patient.has_blood, 'Hemoptysis'),
        (Patient.has_fatigue, 'Fatigue'), (Patient.has_shortness_of_breath, 'Shortness of Breath')
    ]
    symptom_labels, symptom_data = [], []
    for col, label in symptom_fields:
        cnt = Patient.query.filter(col == 'Yes').count()
        pct = round(cnt / total * 100, 1) if total > 0 else 0
        symptom_labels.append(label)
        symptom_data.append(pct)
    symptoms_chart = {
        'labels': symptom_labels,
        'data': symptom_data,
        'title': 'Symptom Prevalence (% of patients)'
    }

    # 7. Test positivity rates (bar)
    genexpert_pos = Patient.query.filter(Patient.genexpert_test == 'Positive').count()
    sputum_pos = Patient.query.filter(Patient.sputum_smear_test == 'Positive').count()
    xray_abn = Patient.query.filter(Patient.chest_xray == 'Abnormal').count()
    culture_pos = Patient.query.filter(Patient.tb_culture == 'Positive').count()
    tests_chart = {
        'labels': ['GeneXpert+', 'Sputum+', 'X-ray Abnormal', 'Culture+'],
        'data': [
            round(genexpert_pos / total * 100, 1) if total > 0 else 0,
            round(sputum_pos / total * 100, 1) if total > 0 else 0,
            round(xray_abn / total * 100, 1) if total > 0 else 0,
            round(culture_pos / total * 100, 1) if total > 0 else 0,
        ],
        'colors': ['#8b5cf6', '#06b6d4', '#f59e0b', '#10b981']
    }

    # 8. Gender distribution (doughnut)
    gender_rows = db.session.query(
        Patient.gender, func.count(Patient.id).label('cnt')
    ).filter(Patient.gender.isnot(None)).group_by(Patient.gender).all()
    gender_chart = {
        'labels': [r.gender for r in gender_rows],
        'data': [r.cnt for r in gender_rows],
        'colors': ['#3b82f6', '#ec4899', '#6b7280']
    }

    # 9. Prescription status (doughnut)
    p_pending = Prescription.query.filter_by(status='pending').count()
    p_approved = Prescription.query.filter_by(status='approved').count()
    p_rejected = Prescription.query.filter_by(status='rejected').count()
    prescription_chart = {
        'labels': ['Pending', 'Approved', 'Rejected'],
        'data': [p_pending, p_approved, p_rejected],
        'colors': ['#f59e0b', '#10b981', '#ef4444']
    }

    # 10. HIV & Comorbidities (bar)
    hiv_yes = Patient.query.filter(Patient.hiv == 'Yes').count()
    diabetes_yes = Patient.query.filter(Patient.diabetes == 'Yes').count()
    smoking_current = Patient.query.filter(Patient.smoking_status == 'Current').count()
    alcohol_reg = Patient.query.filter(Patient.alcohol_use == 'Regular').count()
    comorbidity_chart = {
        'labels': ['HIV+', 'Diabetes', 'Smoking', 'Alcohol Regular'],
        'data': [
            round(hiv_yes / total * 100, 1) if total > 0 else 0,
            round(diabetes_yes / total * 100, 1) if total > 0 else 0,
            round(smoking_current / total * 100, 1) if total > 0 else 0,
            round(alcohol_reg / total * 100, 1) if total > 0 else 0,
        ],
        'colors': ['#ef4444', '#f97316', '#8b5cf6', '#06b6d4']
    }

    return jsonify({
        'risk_distribution': risk_chart,
        'tb_status': tb_status_chart,
        'drug_resistance': resistance_chart,
        'antibiogram': antibiogram_chart,
        'bacterial_species': species_chart,
        'symptom_prevalence': symptoms_chart,
        'test_positivity': tests_chart,
        'gender_distribution': gender_chart,
        'prescription_status': prescription_chart,
        'comorbidities': comorbidity_chart,
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
