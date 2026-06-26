
from flask_sqlalchemy import SQLAlchemy
from utils.security import encrypt_data, decrypt_data, hash_password, verify_password

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Encrypted fields
    _username = db.Column('username', db.String(200), nullable=False)  # encrypted
    _email = db.Column('email', db.String(200), nullable=False, unique=True)  # encrypted
    password = db.Column(db.String(200), nullable=False)  # hashed
    role = db.Column(db.String(50), default='doctor')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    @property
    def username(self):
        return decrypt_data(self._username)

    @username.setter
    def username(self, value):
        self._username = encrypt_data(value)

    @property
    def email(self):
        return decrypt_data(self._email)

    @email.setter
    def email(self, value):
        self._email = encrypt_data(value)

    def set_password(self, plain_password):
        self.password = hash_password(plain_password)

    def check_password(self, plain_password):
        return verify_password(plain_password, self.password)

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
    weight = db.Column(db.Float)  # kg
    tb_status_label = db.Column(db.String(50))
    source_dataset = db.Column(db.String(100))
    source_row_id = db.Column(db.String(100))
    region = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    date_of_diagnosis = db.Column(db.Integer)
    symptoms = db.Column(db.Text)
    exposure_history = db.Column(db.Text)
    persistent_cough_duration_weeks = db.Column(db.Integer)
    contact_with_tb_patient = db.Column(db.String(50))  # Yes/No/Unknown
    previous_tb_treatment = db.Column(db.String(50))  # Yes/No/Unknown
    sputum_smear_test = db.Column(db.String(50))
    genexpert_test = db.Column(db.String(50))
    chest_xray = db.Column(db.String(50))
    tb_culture = db.Column(db.String(50))
    tst = db.Column(db.String(50))
    igra = db.Column(db.String(50))
    bacteria_species = db.Column(db.String(100))
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
    smoking_status = db.Column(db.String(100))  # Never/Former/Current/Unknown
    alcohol_use = db.Column(db.String(100))  # Never/Occasional/Regular/Unknown
    oxygen_saturation_spo2 = db.Column(db.Float)  # %
    living_conditions = db.Column(db.String(100))
    access_to_healthcare = db.Column(db.String(50))
    city = db.Column(db.String(100))
    region_code = db.Column(db.String(50))
    antibiotic_usage_history = db.Column(db.Text)
    # Symptom checkboxes for ML model
    has_fever = db.Column(db.String(10))  # Yes/No/Unknown
    has_cough = db.Column(db.String(10))
    has_weight_loss = db.Column(db.String(10))
    has_night_sweats = db.Column(db.String(10))
    has_chest_pain = db.Column(db.String(10))
    has_blood = db.Column(db.String(10))
    has_fatigue = db.Column(db.String(10))
    has_shortness_of_breath = db.Column(db.String(10))
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
            "weight": self.weight,
            "tb_status_label": self.tb_status_label,
            "source_dataset": self.source_dataset,
            "source_row_id": self.source_row_id,
            "region": self.region,
            "occupation": self.occupation,
            "symptoms": self.symptoms,
            "exposure_history": self.exposure_history,
            "persistent_cough_duration_weeks": self.persistent_cough_duration_weeks,
            "contact_with_tb_patient": self.contact_with_tb_patient,
            "previous_tb_treatment": self.previous_tb_treatment,
            "sputum_smear_test": self.sputum_smear_test,
            "genexpert_test": self.genexpert_test,
            "chest_xray": self.chest_xray,
            "tb_culture": self.tb_culture,
            "tst": self.tst,
            "igra": self.igra,
            "bacteria_species": self.bacteria_species,
            "treatment_type": self.treatment_type,
            "drug_resistance": self.drug_resistance,
            "treatment_outcome": self.treatment_outcome,
            "hiv": self.hiv,
            "diabetes": self.diabetes,
            "smoking_status": self.smoking_status,
            "alcohol_use": self.alcohol_use,
            "oxygen_saturation_spo2": self.oxygen_saturation_spo2,
            "city": self.city,
            "antibiotic_usage_history": self.antibiotic_usage_history,
            "has_fever": self.has_fever,
            "has_cough": self.has_cough,
            "has_weight_loss": self.has_weight_loss,
            "has_night_sweats": self.has_night_sweats,
            "has_chest_pain": self.has_chest_pain,
            "has_blood": self.has_blood,
            "has_fatigue": self.has_fatigue,
            "has_shortness_of_breath": self.has_shortness_of_breath,
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

class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_type = db.Column(db.String(100), nullable=False)  # e.g., "GeneXpert", "Sputum Smear", "Chest X-ray", "Blood Test"
    status = db.Column(db.String(50), default='requested')  # requested, in_progress, completed, cancelled
    results = db.Column(db.Text)
    notes = db.Column(db.Text)
    completed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('lab_tests', lazy=True))
    requester = db.relationship('User', foreign_keys=[requested_by], backref=db.backref('requested_lab_tests', lazy=True))
    completer = db.relationship('User', foreign_keys=[completed_by], backref=db.backref('completed_lab_tests', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "requested_by": self.requested_by,
            "test_type": self.test_type,
            "status": self.status,
            "results": self.results,
            "notes": self.notes,
            "completed_by": self.completed_by,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ATCDrug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    atc_code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., J01CA04
    atc_level_1 = db.Column(db.String(10))  # J
    atc_level_2 = db.Column(db.String(10))  # J01
    atc_level_3 = db.Column(db.String(10))  # J01C
    atc_level_4 = db.Column(db.String(10))  # J01CA
    atc_level_5 = db.Column(db.String(20))  # J01CA04
    drug_name = db.Column(db.String(200), nullable=False)
    ddd = db.Column(db.Float)  # Defined Daily Dose in grams
    ddd_unit = db.Column(db.String(50))  # e.g., g, mg
    administration_route = db.Column(db.String(100))  # e.g., oral, IV
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "atc_code": self.atc_code,
            "atc_level_1": self.atc_level_1,
            "atc_level_2": self.atc_level_2,
            "atc_level_3": self.atc_level_3,
            "atc_level_4": self.atc_level_4,
            "atc_level_5": self.atc_level_5,
            "drug_name": self.drug_name,
            "ddd": self.ddd,
            "ddd_unit": self.ddd_unit,
            "administration_route": self.administration_route,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication = db.Column(db.String(200), nullable=False)
    atc_drug_id = db.Column(db.Integer, db.ForeignKey('atc_drug.id'))
    dosage = db.Column(db.String(200))
    dosage_mg = db.Column(db.Float)  # Dosage in milligrams
    duration_days = db.Column(db.Integer)
    total_mg = db.Column(db.Float)  # Total dosage in milligrams
    ddds = db.Column(db.Float)  # Number of Defined Daily Doses
    duration = db.Column(db.String(100))
    risk_level = db.Column(db.String(50))
    ml_recommended = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    rejection_reason = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))
    diagnosis = db.relationship('Diagnosis', backref=db.backref('prescriptions', lazy=True))
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_prescriptions', lazy=True))
    approver = db.relationship('User', foreign_keys=[approved_by], backref=db.backref('approved_prescriptions', lazy=True))
    atc_drug = db.relationship('ATCDrug', backref=db.backref('prescriptions', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "diagnosis_id": self.diagnosis_id,
            "created_by": self.created_by,
            "medication": self.medication,
            "atc_drug_id": self.atc_drug_id,
            "atc_drug": self.atc_drug.to_dict() if self.atc_drug else None,
            "dosage": self.dosage,
            "dosage_mg": self.dosage_mg,
            "duration_days": self.duration_days,
            "total_mg": self.total_mg,
            "ddds": self.ddds,
            "duration": self.duration,
            "risk_level": self.risk_level,
            "ml_recommended": self.ml_recommended,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100))  # "patient", "lab_test", "prescription", "diagnosis"
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user": {
                "id": self.user.id if self.user else None,
                "username": self.user.username if self.user else None,
                "role": self.user.role if self.user else None
            } if self.user else None
        }


class ExternalDatasetRow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(100), nullable=False, index=True)
    source_key = db.Column(db.String(200), index=True)
    record_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_name": self.dataset_name,
            "source_key": self.source_key,
            "record_json": self.record_json,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class DetailedLabResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    hospital = db.Column(db.String(100))
    test_name = db.Column(db.String(100), nullable=False)
    test_value = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    reference_range = db.Column(db.String(100))
    collection_date = db.Column(db.String(50))
    source_dataset = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('detailed_lab_results', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "hospital": self.hospital,
            "test_name": self.test_name,
            "test_value": self.test_value,
            "unit": self.unit,
            "reference_range": self.reference_range,
            "collection_date": self.collection_date,
            "source_dataset": self.source_dataset,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AntibioticResistance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.String(100), unique=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient_name = db.Column(db.String(100))
    patient_email = db.Column(db.String(200))
    patient_address = db.Column(db.Text)
    age_gender = db.Column(db.String(50))
    bacterial_species = db.Column(db.String(100))
    diabetes = db.Column(db.String(10))
    hypertension = db.Column(db.String(10))
    previous_hospitalization = db.Column(db.String(10))
    infection_frequency = db.Column(db.Float)
    amx_amp = db.Column(db.String(10))  # Amoxicillin/Ampicillin
    amc = db.Column(db.String(10))  # Amoxicillin-clavulanate
    cz = db.Column(db.String(10))  # Cefazolin
    fox = db.Column(db.String(10))  # Cefoxitin
    ctx_cro = db.Column(db.String(10))  # Cefotaxime/Ceftriaxone
    ipm = db.Column(db.String(10))  # Imipenem
    gen = db.Column(db.String(10))  # Gentamicin
    an = db.Column(db.String(10))  # Amikacin
    nalidixic_acid = db.Column(db.String(10))
    ofx = db.Column(db.String(10))  # Ofloxacin
    cip = db.Column(db.String(10))  # Ciprofloxacin
    chloramphenicol = db.Column(db.String(10))
    co_trimoxazole = db.Column(db.String(10))
    furanes = db.Column(db.String(10))
    colistine = db.Column(db.String(10))
    collection_date = db.Column(db.String(50))
    notes = db.Column(db.Text)
    source_dataset = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship to Patient
    patient = db.relationship('Patient', backref=db.backref('antibiotic_resistance_records', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "sample_id": self.sample_id,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "patient_email": self.patient_email,
            "bacterial_species": self.bacterial_species,
            "diabetes": self.diabetes,
            "hypertension": self.hypertension,
            "amx_amp": self.amx_amp,
            "amc": self.amc,
            "cz": self.cz,
            "fox": self.fox,
            "ctx_cro": self.ctx_cro,
            "ipm": self.ipm,
            "gen": self.gen,
            "an": self.an,
            "nalidixic_acid": self.nalidixic_acid,
            "ofx": self.ofx,
            "cip": self.cip,
            "chloramphenicol": self.chloramphenicol,
            "co_trimoxazole": self.co_trimoxazole,
            "furanes": self.furanes,
            "colistine": self.colistine,
            "collection_date": self.collection_date,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
