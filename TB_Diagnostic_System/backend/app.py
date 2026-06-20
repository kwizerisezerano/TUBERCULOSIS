import os
import json
import joblib
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
from models.models import db, User, Patient, Diagnosis, Treatment, Alert

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration - supports multiple databases
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # sqlite, mysql, postgresql

if DATABASE_TYPE == 'mysql':
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'tb_diagnostic')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
elif DATABASE_TYPE == 'postgresql':
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'tb_diagnostic')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    # SQLite database in backend folder
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tb_data.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@tbdiagnostic.com')

mail = Mail(app)

# Load trained model if available
model = None
label_encoder = None
try:
    model_path = 'models/trained_model.pkl'
    le_path = 'models/label_encoder.pkl'
    if os.path.exists(model_path) and os.path.exists(le_path):
        model = joblib.load(model_path)
        label_encoder = joblib.load(le_path)
        print("Trained model loaded successfully!")
except Exception as e:
    print(f"Model not loaded: {e}")

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
        severity=severity
    )
    db.session.add(alert)
    db.session.commit()
    
    # Send email alert
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

def analyze_symptoms(symptoms):
    symptom_score = 0
    red_flags = []
    
    symptoms_lower = symptoms.lower() if symptoms else ''
    if 'fever' in symptoms_lower:
        symptom_score += 1
    if 'cough' in symptoms_lower:
        symptom_score += 2
        if 'blood' in symptoms_lower:
            red_flags.append("Cough with blood (hemoptysis) - critical sign")
    if 'weight' in symptoms_lower or 'loss' in symptoms_lower:
        symptom_score += 2
        red_flags.append("Unintentional weight loss")
    if 'night' in symptoms_lower or 'sweat' in symptoms_lower:
        symptom_score += 2
        red_flags.append("Night sweats")
    if 'chest' in symptoms_lower and 'pain' in symptoms_lower:
        symptom_score += 1
    if 'fatigue' in symptoms_lower or 'tired' in symptoms_lower:
        symptom_score += 1
    
    if symptom_score >= 6:
        return ("High Risk of TB", 
                "URGENT: Patient shows multiple classic TB symptoms. Immediate diagnostic testing required - sputum smear, GeneXpert, and chest X-ray should be performed without delay. Isolate patient if possible.", 
                red_flags)
    elif symptom_score >= 4:
        return ("Moderate Risk of TB", 
                "Patient presents with several TB symptoms. Schedule diagnostic tests promptly and monitor closely. Consider TB as a strong differential diagnosis.", 
                red_flags)
    elif symptom_score >= 2:
        return ("Low Risk", 
                "Patient has some non-specific symptoms. Monitor for progression. Advise return if symptoms worsen or persist beyond 2 weeks.", 
                red_flags)
    else:
        return ("Unlikely TB", 
                "Low probability of TB based on reported symptoms. Still, consider clinical context and patient history.", 
                red_flags)

def evaluate_tests(sputum, genexpert, chest_xray, hiv):
    diagnosis_details = []
    confidence = 0.0
    
    if sputum == "Positive":
        diagnosis_details.append("✓ Sputum smear positive for Acid-Fast Bacilli (AFB) - strong indicator of active TB")
        confidence += 0.4
    elif sputum == "Negative":
        diagnosis_details.append("✗ Sputum smear negative - does not rule out TB")
    
    if genexpert == "Positive":
        diagnosis_details.append("✓ GeneXpert test positive for TB DNA - confirms TB infection")
        confidence += 0.5
    elif genexpert == "Negative":
        diagnosis_details.append("✗ GeneXpert test negative")
    
    if chest_xray == "Abnormal":
        diagnosis_details.append("✓ Chest X-ray shows infiltrates/consolidation consistent with pulmonary TB")
        confidence += 0.3
    elif chest_xray == "Normal":
        diagnosis_details.append("✗ Chest X-ray appears normal")
    
    if hiv == "Yes":
        diagnosis_details.append("⚠ HIV positive - significantly increased risk of TB progression and extrapulmonary disease")
        confidence += 0.1
    
    if confidence >= 0.7:
        final_diagnosis = "CONFIRMED TB INFECTION"
    elif confidence >= 0.4:
        final_diagnosis = "PROBABLE TB - HIGH SUSPICION"
    elif confidence >= 0.2:
        final_diagnosis = "POSSIBLE TB - MODERATE SUSPICION"
    else:
        final_diagnosis = "INCONCLUSIVE - Additional Testing Recommended"
    
    return final_diagnosis, diagnosis_details, min(confidence, 1.0)

def recommend_treatment(drug_resistant, hiv_status="No"):
    if drug_resistant == "Yes":
        return {
            "type": "Drug-Resistant TB (DR-TB) Treatment",
            "category": "Second-line Therapy",
            "drugs": "Regimen based on resistance profile:\n- Fluoroquinolones (Levofloxacin, Moxifloxacin)\n- Injectable agents (Amikacin, Kanamycin)\n- Bedaquiline, Linezolid, Clofazimine\n- Other second-line drugs as per sensitivity",
            "duration": "18-24 months total",
            "intensive_phase": "6-8 months (daily DOT)",
            "continuation_phase": "12-16 months",
            "dosage": "Individualized based on weight and tolerance",
            "administration": "Directly Observed Therapy (DOT) mandatory for entire course",
            "monitoring": "Monthly: clinical assessment, liver/kidney function tests, hearing tests (for injectables)",
            "notes": "Refer to specialized DR-TB center. Monitor for adverse drug reactions closely."
        }
    else:
        if hiv_status == "Yes":
            return {
                "type": "Drug-Sensitive TB with HIV Co-infection",
                "category": "First-line Therapy + ART",
                "drugs": "Isoniazid (INH), Rifampicin (RIF), Pyrazinamide (PZA), Ethambutol (EMB)\n+ Antiretroviral Therapy (ART) within 2-8 weeks of TB treatment initiation",
                "duration": "6 months total",
                "intensive_phase": "2 months (HRZE daily)",
                "continuation_phase": "4 months (HR daily)",
                "dosage": "INH: 5 mg/kg/day, RIF: 10 mg/kg/day, PZA: 25 mg/kg/day, EMB: 15 mg/kg/day",
                "administration": "Directly Observed Therapy (DOT) recommended",
                "monitoring": "Monthly: liver function, CD4 count, viral load",
                "notes": "Ensure drug-drug interactions are managed (especially with EFV-based ART)"
            }
        else:
            return {
                "type": "Drug-Sensitive TB (DS-TB) Treatment",
                "category": "First-line Therapy",
                "drugs": "Isoniazid (INH) + Rifampicin (RIF) + Pyrazinamide (PZA) + Ethambutol (EMB)",
                "duration": "6 months total",
                "intensive_phase": "2 months (HRZE daily)",
                "continuation_phase": "4 months (HR daily)",
                "dosage": "INH: 300 mg/day, RIF: 600 mg/day, PZA: 1500-2000 mg/day, EMB: 800-1200 mg/day (weight-based)",
                "administration": "Directly Observed Therapy (DOT) recommended - improves adherence and outcomes",
                "monitoring": "Monthly: clinical assessment, liver function tests",
                "notes": "Vitamin B6 (pyridoxine) 25-50 mg/day with INH to prevent peripheral neuropathy"
            }

def predict_with_model(patient_data):
    if not model or not label_encoder:
        return None
    
    try:
        features = {
            'age': patient_data.get('age', 30),
            'gender': 1 if patient_data.get('gender', 'Male') == 'Male' else 0,
            'has_fever': 1 if 'fever' in patient_data.get('symptoms', '').lower() else 0,
            'has_cough': 1 if 'cough' in patient_data.get('symptoms', '').lower() else 0,
            'has_weight_loss': 1 if 'weight' in patient_data.get('symptoms', '').lower() else 0,
            'has_night_sweats': 1 if 'night' in patient_data.get('symptoms', '').lower() else 0,
            'sputum_smear_test': 1 if patient_data.get('sputum_smear_test') == 'Positive' else 0,
            'genexpert_test': 1 if patient_data.get('genexpert_test') == 'Positive' else 0,
            'chest_xray': 1 if patient_data.get('chest_xray') == 'Abnormal' else 0,
            'hiv': 1 if patient_data.get('hiv') == 'Yes' else 0,
            'diabetes': 1 if patient_data.get('diabetes') == 'Yes' else 0
        }
        
        feature_df = pd.DataFrame([features])
        prediction = model.predict(feature_df)[0]
        probability = model.predict_proba(feature_df)[0]
        
        predicted_class = label_encoder.inverse_transform([prediction])[0]
        
        return {
            "prediction": predicted_class,
            "probability_drug_resistant": round(float(probability[1]) * 100, 2),
            "probability_sensitive": round(float(probability[0]) * 100, 2)
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {"error": str(e)}

# ----------------------
# API Routes
# ----------------------

@app.route('/')
def home():
    return jsonify({
        "message": "TB Diagnostic System API",
        "version": "2.0.0",
        "database": DATABASE_TYPE
    })

# Patient Routes
@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Patient.query
        if search:
            query = query.filter(
                (Patient.first_name.ilike(f'%{search}%')) |
                (Patient.last_name.ilike(f'%{search}%')) |
                (Patient.patient_id.ilike(f'%{search}%'))
            )
        
        pagination = query.order_by(Patient.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        patients = [patient.to_dict() for patient in pagination.items]
        
        return jsonify({
            "patients": patients,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        })
    
    if request.method == 'POST':
        data = request.get_json()
        patient = Patient(
            patient_id=data.get('patient_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            gender=data.get('gender'),
            region=data.get('region'),
            occupation=data.get('occupation'),
            symptoms=data.get('symptoms'),
            sputum_smear_test=data.get('sputum_smear_test'),
            genexpert_test=data.get('genexpert_test'),
            chest_xray=data.get('chest_xray'),
            drug_resistance=data.get('drug_resistance'),
            hiv=data.get('hiv'),
            diabetes=data.get('diabetes'),
            city=data.get('city')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201

@app.route('/api/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        return jsonify({
            "patient": patient.to_dict(),
            "diagnoses": [d.to_dict() for d in patient.diagnoses],
            "treatments": [t.to_dict() for t in patient.treatments],
            "alerts": [a.to_dict() for a in patient.alerts]
        })
    
    if request.method == 'PUT':
        data = request.get_json()
        for key, value in data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        db.session.commit()
        return jsonify(patient.to_dict())
    
    if request.method == 'DELETE':
        db.session.delete(patient)
        db.session.commit()
        return jsonify({"message": "Patient deleted successfully"})

# Diagnosis Routes
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.get_json()
    patient_data = data.get('patient', {})
    
    # Symptom analysis
    symptoms = patient_data.get('symptoms', '')
    risk_level, symptom_advice, red_flags = analyze_symptoms(symptoms)
    
    # Test results evaluation
    sputum = patient_data.get('sputum_smear_test', 'Unknown')
    genexpert = patient_data.get('genexpert_test', 'Unknown')
    chest_xray = patient_data.get('chest_xray', 'Unknown')
    hiv = patient_data.get('hiv', 'No')
    diagnosis, test_details, confidence = evaluate_tests(sputum, genexpert, chest_xray, hiv)
    
    # Treatment recommendation
    drug_resistant = patient_data.get('drug_resistance', 'No')
    treatment = recommend_treatment(drug_resistant, hiv)
    
    # ML Prediction
    ml_prediction = predict_with_model(patient_data)
    
    # Save diagnosis if patient exists
    patient_id = patient_data.get('patient_id')
    saved_diagnosis = None
    if patient_id:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if patient:
            diagnosis_record = Diagnosis(
                patient_id=patient.id,
                diagnosis_type=diagnosis,
                risk_level=risk_level,
                confidence_percent=round(confidence * 100, 2),
                details=json.dumps(test_details),
                ml_prediction=json.dumps(ml_prediction) if ml_prediction else None,
                status='completed'
            )
            db.session.add(diagnosis_record)
            
            # Save treatment
            treatment_record = Treatment(
                patient_id=patient.id,
                diagnosis_id=diagnosis_record.id,
                treatment_type=treatment['type'],
                drugs=treatment['drugs'],
                duration=treatment['duration'],
                dosage=treatment['dosage'],
                administration_notes=treatment['administration'] + '\n' + treatment['notes']
            )
            db.session.add(treatment_record)
            
            # Create alert for high risk
            if risk_level == 'High Risk of TB' or 'CONFIRMED' in diagnosis:
                create_alert(
                    patient_id=patient.id,
                    user_id=None,
                    alert_type='URGENT: High Risk/Confirmed TB',
                    message=f"Patient {patient.first_name} {patient.last_name} (ID: {patient.patient_id}) has been diagnosed with {diagnosis}. Immediate attention required.",
                    severity='high'
                )
            
            db.session.commit()
            saved_diagnosis = diagnosis_record.to_dict()
    
    return jsonify({
        "patient_name": f"{patient_data.get('first_name', 'Patient')} {patient_data.get('last_name', '')}",
        "symptom_analysis": {
            "risk_level": risk_level,
            "clinical_advice": symptom_advice,
            "red_flags": red_flags
        },
        "test_evaluation": {
            "diagnosis": diagnosis,
            "findings": test_details,
            "confidence_percent": round(confidence * 100, 2)
        },
        "treatment_recommendation": treatment,
        "ml_prediction": ml_prediction,
        "saved_diagnosis": saved_diagnosis
    })

@app.route('/api/diagnoses', methods=['GET'])
def get_diagnoses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Diagnosis.query.order_by(Diagnosis.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    diagnoses = [d.to_dict() for d in pagination.items]
    return jsonify({"diagnoses": diagnoses, "total": pagination.total})

# Treatment Routes
@app.route('/api/treatments', methods=['GET'])
def get_treatments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Treatment.query.order_by(Treatment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    treatments = [t.to_dict() for t in pagination.items]
    return jsonify({"treatments": treatments, "total": pagination.total})

# Alert Routes
@app.route('/api/alerts', methods=['GET'])
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
        "alerts": alerts,
        "total": pagination.total,
        "unread_count": Alert.query.filter_by(is_read=False).count()
    })

@app.route('/api/alerts/<int:alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify(alert.to_dict())

# Model Training Route
@app.route('/api/train-model', methods=['POST'])
def train_model():
    try:
        from models.train_model import train_model_from_database
        result = train_model_from_database()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
