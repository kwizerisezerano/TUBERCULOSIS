from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='clinician')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    region = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    date_of_diagnosis = db.Column(db.Integer)
    symptoms = db.Column(db.Text)
    sputum_smear_test = db.Column(db.String(50))
    genexpert_test = db.Column(db.String(50))
    chest_xray = db.Column(db.String(50))
    treatment_type = db.Column(db.String(100))
    duration_of_treatment = db.Column(db.Integer)
    drug_resistance = db.Column(db.String(50))
    treatment_outcome = db.Column(db.String(100))
    relapse = db.Column(db.String(50))
    mortality = db.Column(db.String(50))
    complications = db.Column(db.Text)
    malnutrition = db.Column(db.String(50))
    diabetes = db.Column(db.String(50))
    hiv = db.Column(db.String(50))
    chronic_lung_disease = db.Column(db.String(50))
    smoking_status = db.Column(db.String(100))
    alcohol_consumption = db.Column(db.String(100))
    living_conditions = db.Column(db.String(100))
    access_to_healthcare = db.Column(db.String(50))
    city = db.Column(db.String(100))
    region_code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "gender": self.gender,
            "region": self.region,
            "occupation": self.occupation,
            "symptoms": self.symptoms,
            "sputum_smear_test": self.sputum_smear_test,
            "genexpert_test": self.genexpert_test,
            "chest_xray": self.chest_xray,
            "treatment_type": self.treatment_type,
            "drug_resistance": self.drug_resistance,
            "treatment_outcome": self.treatment_outcome,
            "hiv": self.hiv,
            "diabetes": self.diabetes,
            "city": self.city,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    clinician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diagnosis_type = db.Column(db.String(100))
    risk_level = db.Column(db.String(50))
    confidence_percent = db.Column(db.Float)
    details = db.Column(db.Text)
    ml_prediction = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('diagnoses', lazy=True))
    clinician = db.relationship('User', backref=db.backref('diagnoses', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "clinician_id": self.clinician_id,
            "diagnosis_type": self.diagnosis_type,
            "risk_level": self.risk_level,
            "confidence_percent": self.confidence_percent,
            "details": self.details,
            "ml_prediction": self.ml_prediction,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'))
    treatment_type = db.Column(db.String(100))
    drugs = db.Column(db.Text)
    duration = db.Column(db.String(100))
    dosage = db.Column(db.Text)
    administration_notes = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('treatments', lazy=True))
    diagnosis = db.relationship('Diagnosis', backref=db.backref('treatments', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "diagnosis_id": self.diagnosis_id,
            "treatment_type": self.treatment_type,
            "drugs": self.drugs,
            "duration": self.duration,
            "dosage": self.dosage,
            "administration_notes": self.administration_notes,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    alert_type = db.Column(db.String(100))
    message = db.Column(db.Text)
    severity = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('alerts', lazy=True))
    user = db.relationship('User', backref=db.backref('alerts', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "is_read": self.is_read,
            "email_sent": self.email_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
