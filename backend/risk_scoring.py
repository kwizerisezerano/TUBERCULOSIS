"""
Continuous Risk Scoring Service
Recalculates patient risk scores whenever new data (lab results, prescriptions) is added.
"""
from datetime import datetime
from models.models import Patient, LabTest, Prescription, db
from models.train_model import get_patient_features
import joblib
import numpy as np
import os

def calculate_risk_score(patient_id):
    """
    Calculate continuous risk score for a patient using ML model.
    Returns risk score (0-100) and updates patient record.
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        return None
    
    try:
        # Load the trained model
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'tb_status_model.pkl')
        encoder_path = os.path.join(os.path.dirname(__file__), 'models', 'tb_status_label_encoder.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(encoder_path):
            # Fallback to rule-based scoring if model not available
            return calculate_rule_based_risk(patient)
        
        model = joblib.load(model_path)
        le = joblib.load(encoder_path)
        
        # Get patient features (returns 25 features matching the trained model)
        features = get_patient_features(patient)
        if features is None:
            return calculate_rule_based_risk(patient)
        
        # Prepare feature vector in the same order as training data
        feature_names = [
            'age', 'weight', 'gender_male', 'gender_female', 'gender_other',
            'persistent_cough_duration_weeks', 'contact_with_tb_patient_yes',
            'previous_tb_treatment_yes', 'smoking_current', 'smoking_former',
            'alcohol_regular', 'oxygen_saturation_spo2', 'has_fever', 'has_cough',
            'has_weight_loss', 'has_night_sweats', 'has_chest_pain', 'has_blood',
            'has_fatigue', 'has_shortness_of_breath', 'sputum_positive',
            'genexpert_positive', 'chest_xray_abnormal', 'hiv_yes', 'diabetes_yes'
        ]
        
        feature_vector = []
        for name in feature_names:
            value = features.get(name, 0)
            if value is None:
                feature_vector.append(0)
            else:
                feature_vector.append(float(value))
        
        # Create DataFrame with proper feature names to avoid sklearn warning
        import pandas as pd
        X = pd.DataFrame([feature_vector], columns=feature_names)
        
        # Predict
        prediction_proba = model.predict_proba(X)[0]
        
        # Get probability of positive TB class
        positive_class_idx = list(le.classes_).index('Yes') if 'Yes' in le.classes_ else 0
        risk_score = prediction_proba[positive_class_idx] * 100
        
        # Update patient
        patient.risk_score = round(risk_score, 2)
        patient.last_risk_calculation = datetime.now()
        db.session.commit()
        
        print(f"DEBUG: Risk score calculated for patient {patient.patient_id}: {risk_score:.2f}%")
        
        # Trigger alert if risk > 50% (lowered threshold for better visibility)
        if risk_score > 50:
            print(f"DEBUG: Triggering high risk alert for patient {patient.patient_id} (risk: {risk_score:.2f}%)")
            trigger_high_risk_alert(patient, risk_score)
        
        return patient.risk_score
        
    except Exception as e:
        print(f"Error calculating ML risk score: {e}")
        return calculate_rule_based_risk(patient)

def calculate_rule_based_risk(patient):
    """
    Fallback rule-based risk scoring when ML model is unavailable.
    """
    risk_score = 0.0
    
    # Symptom scoring (max 40 points)
    if patient.has_fever == 'Yes':
        risk_score += 10
    if patient.has_cough == 'Yes':
        risk_score += 10
    if patient.has_weight_loss == 'Yes':
        risk_score += 10
    if patient.has_night_sweats == 'Yes':
        risk_score += 10
    
    # Risk factors (max 30 points)
    if patient.hiv == 'Yes':
        risk_score += 15
    if patient.diabetes == 'Yes':
        risk_score += 10
    if patient.smoking_status == 'Current':
        risk_score += 5
    
    # Lab results (max 30 points)
    if patient.genexpert_test == 'Positive':
        risk_score += 30
    elif patient.sputum_smear_test == 'Positive':
        risk_score += 20
    elif patient.chest_xray == 'Abnormal':
        risk_score += 15
    
    # Contact history (max 10 points)
    if patient.contact_with_tb_patient == 'Yes':
        risk_score += 10
    
    # Previous treatment (max 10 points)
    if patient.previous_tb_treatment == 'Yes':
        risk_score += 10
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Update patient
    patient.risk_score = round(risk_score, 2)
    patient.last_risk_calculation = datetime.now()
    db.session.commit()
    
    # Trigger alert if risk > 70%
    if risk_score > 70:
        trigger_high_risk_alert(patient, risk_score)
    
    return patient.risk_score

def trigger_high_risk_alert(patient, risk_score):
    """
    Create an alert when patient risk exceeds threshold and send notifications.
    """
    from models.models import Alert, User, Hospital
    from app import mail
    from flask_mail import Message
    
    # Check if recent high-risk alert already exists
    recent_alert = Alert.query.filter(
        Alert.patient_id == patient.id,
        Alert.alert_type == 'high_risk_tb',
        Alert.severity == 'critical',
        Alert.is_read == False
    ).first()
    
    if recent_alert:
        return  # Alert already exists
    
    # Get patient's associated hospital (if any)
    hospital_id = None
    if patient.hospitals:
        hospital_id = patient.hospitals[0].id
    else:
        # Fallback: get first available hospital
        hospital = Hospital.query.first()
        if hospital:
            hospital_id = hospital.id
    
    # Create new alert
    alert = Alert(
        patient_id=patient.id,
        hospital_id=hospital_id,
        alert_type='high_risk_tb',
        message=f"High TB Risk Alert: Patient {patient.patient_id} has risk score of {risk_score:.1f}%. Immediate clinical review recommended.",
        severity='critical',
        is_read=False
    )
    
    db.session.add(alert)
    db.session.commit()
    
    # Notify doctors and admins via email
    doctors = User.query.filter(User.role.in_(['doctor', 'admin', 'hospital_admin'])).all()
    email_count = 0
    
    for doctor in doctors:
        if doctor.email:
            try:
                msg = Message(
                    f"High TB Risk Alert - Patient {patient.patient_id}",
                    recipients=[doctor.email],
                    sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@tbdiagnostic.com')
                )
                msg.body = f"""
URGENT: High TB Risk Alert

Patient ID: {patient.patient_id}
Risk Score: {risk_score:.1f}%
Severity: CRITICAL

Message: Patient has a high TB risk score. Immediate clinical review is recommended.

Please log in to the TB Diagnostic System for more details.

---
This is an automated alert from the TB Predictive EHR Analytics Dashboard.
                """
                mail.send(msg)
                email_count += 1
                print(f"Email sent to {doctor.email} for high-risk alert")
            except Exception as e:
                print(f"Failed to send email to {doctor.email}: {e}")
    
    print(f"High-risk alert triggered for patient {patient.patient_id}. Emails sent: {email_count}/{len(doctors)}")

def recalculate_risk_on_lab_result(patient_id):
    """
    Recalculate risk score when new lab result is added.
    """
    return calculate_risk_score(patient_id)

def recalculate_risk_on_prescription(patient_id):
    """
    Recalculate risk score when new prescription is added.
    """
    return calculate_risk_score(patient_id)

def recalculate_risk_on_diagnosis(patient_id):
    """
    Recalculate risk score when new diagnosis is made.
    """
    return calculate_risk_score(patient_id)

def batch_recalculate_risk_scores():
    """
    Recalculate risk scores for all patients (for scheduled tasks).
    """
    patients = Patient.query.all()
    updated_count = 0
    
    for patient in patients:
        calculate_risk_score(patient.id)
        updated_count += 1
    
    return updated_count
