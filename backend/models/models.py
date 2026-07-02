
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from utils.security import encrypt_data, decrypt_data, hash_password, verify_password

db = SQLAlchemy()

# Association table for Patient-Hospital many-to-many relationship
patient_hospital = db.Table('patient_hospital',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'), primary_key=True),
    db.Column('hospital_id', db.Integer, db.ForeignKey('hospital.id'), primary_key=True),
    db.Column('is_primary', db.Boolean, default=True),  # Mark primary hospital
    db.Column('visited_at', db.DateTime, default=db.func.current_timestamp())
)

# Association table for Hospital-Laboratory relationships
hospital_laboratory = db.Table('hospital_laboratory',
    db.Column('hospital_id', db.Integer, db.ForeignKey('hospital.id'), primary_key=True),
    db.Column('laboratory_id', db.Integer, db.ForeignKey('laboratory.id'), primary_key=True),
    db.Column('is_primary', db.Boolean, default=True),
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
)

# Association table for Hospital-Pharmacy relationships
hospital_pharmacy = db.Table('hospital_pharmacy',
    db.Column('hospital_id', db.Integer, db.ForeignKey('hospital.id'), primary_key=True),
    db.Column('pharmacy_id', db.Integer, db.ForeignKey('pharmacy.id'), primary_key=True),
    db.Column('is_primary', db.Boolean, default=True),
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    facility_type = db.Column(db.String(50), default='Hospital')  # Hospital, Health Center, Laboratory, Pharmacy
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Rwanda')
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    bed_capacity = db.Column(db.Integer)
    icu_beds = db.Column(db.Integer)
    
    # Healthcare specific
    has_emergency = db.Column(db.Boolean, default=False)
    has_surgery = db.Column(db.Boolean, default=False)
    has_maternity = db.Column(db.Boolean, default=False)
    has_pediatrics = db.Column(db.Boolean, default=False)
    
    # Laboratory specific
    lab_capacity = db.Column(db.Integer)  # Tests per day
    has_genexpert = db.Column(db.Boolean, default=False)
    has_culture = db.Column(db.Boolean, default=False)
    has_xray = db.Column(db.Boolean, default=False)
    
    # Pharmacy specific
    pharmacy_capacity = db.Column(db.Integer)  # Prescriptions per day
    has_cold_storage = db.Column(db.Boolean, default=False)
    
    source_dataset = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "hospital_id": self.hospital_id,
            "name": self.name,
            "facility_type": self.facility_type,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "phone": self.phone,
            "email": self.email,
            "bed_capacity": self.bed_capacity,
            "icu_beds": self.icu_beds,
            "has_emergency": self.has_emergency,
            "has_surgery": self.has_surgery,
            "has_maternity": self.has_maternity,
            "has_pediatrics": self.has_pediatrics,
            "lab_capacity": self.lab_capacity,
            "has_genexpert": self.has_genexpert,
            "has_culture": self.has_culture,
            "has_xray": self.has_xray,
            "pharmacy_capacity": self.pharmacy_capacity,
            "has_cold_storage": self.has_cold_storage,
            "source_dataset": self.source_dataset,
            "patient_count": len(self.patients) if hasattr(self, 'patients') else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    # Relationships to laboratories and pharmacies
    laboratories = db.relationship('Laboratory', secondary=hospital_laboratory, backref=db.backref('hospitals', lazy=True))
    pharmacies = db.relationship('Pharmacy', secondary=hospital_pharmacy, backref=db.backref('hospitals', lazy=True))

class Laboratory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    facility_type = db.Column(db.String(50), default='Laboratory')
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Rwanda')
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    
    # Laboratory capabilities
    daily_test_capacity = db.Column(db.Integer)
    has_genexpert = db.Column(db.Boolean, default=False)
    has_culture = db.Column(db.Boolean, default=False)
    has_xray = db.Column(db.Boolean, default=False)
    has_molecular = db.Column(db.Boolean, default=False)
    has_sputum_smear = db.Column(db.Boolean, default=True)
    has_blood_tests = db.Column(db.Boolean, default=True)
    
    # Accreditation
    accreditation_number = db.Column(db.String(100))
    accreditation_expiry = db.Column(db.Date)
    
    source_dataset = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "lab_id": self.lab_id,
            "name": self.name,
            "facility_type": self.facility_type,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "phone": self.phone,
            "email": self.email,
            "daily_test_capacity": self.daily_test_capacity,
            "has_genexpert": self.has_genexpert,
            "has_culture": self.has_culture,
            "has_xray": self.has_xray,
            "has_molecular": self.has_molecular,
            "has_sputum_smear": self.has_sputum_smear,
            "has_blood_tests": self.has_blood_tests,
            "accreditation_number": self.accreditation_number,
            "accreditation_expiry": self.accreditation_expiry.isoformat() if self.accreditation_expiry else None,
            "source_dataset": self.source_dataset,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Pharmacy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    facility_type = db.Column(db.String(50), default='Pharmacy')
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Rwanda')
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    
    # Pharmacy capabilities
    daily_prescription_capacity = db.Column(db.Integer)
    has_cold_storage = db.Column(db.Boolean, default=False)
    has_controlled_drugs_license = db.Column(db.Boolean, default=False)
    license_number = db.Column(db.String(100))
    license_expiry = db.Column(db.Date)
    
    # Inventory tracking
    total_drug_types = db.Column(db.Integer, default=0)
    
    source_dataset = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "pharmacy_id": self.pharmacy_id,
            "name": self.name,
            "facility_type": self.facility_type,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "phone": self.phone,
            "email": self.email,
            "daily_prescription_capacity": self.daily_prescription_capacity,
            "has_cold_storage": self.has_cold_storage,
            "has_controlled_drugs_license": self.has_controlled_drugs_license,
            "license_number": self.license_number,
            "license_expiry": self.license_expiry.isoformat() if self.license_expiry else None,
            "total_drug_types": self.total_drug_types,
            "source_dataset": self.source_dataset,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Encrypted fields
    _username = db.Column('username', db.String(200), nullable=False)  # encrypted
    _email = db.Column('email', db.String(200), nullable=False, unique=True)  # encrypted
    password = db.Column(db.String(200), nullable=False)  # hashed
    role = db.Column(db.String(50), default='doctor')
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # New field: is user active?
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    hospital = db.relationship('Hospital', backref=db.backref('users', lazy=True))

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
            "hospital_id": self.hospital_id,
            "hospital": self.hospital.to_dict() if self.hospital else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Encrypted PII and sensitive health data
    _patient_id = db.Column('patient_id', db.String(200), unique=True, nullable=False, index=True)
    _phone_number = db.Column('phone_number', db.String(200), default=lambda: encrypt_data('+250 780 219 351'))  # Encrypted phone number
    _first_name = db.Column('first_name', db.String(200), index=True)
    _last_name = db.Column('last_name', db.String(200), index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    weight = db.Column(db.Float)  # kg
    tb_status_label = db.Column(db.String(50))
    source_dataset = db.Column(db.String(100))
    source_row_id = db.Column(db.String(100))
    _region = db.Column('region', db.String(200))
    _occupation = db.Column('occupation', db.String(200))
    date_of_diagnosis = db.Column(db.Integer)
    # OTP fields (encrypted like other sensitive data)
    _otp_code = db.Column('otp_code', db.String(200))  # Encrypted OTP code - larger size for encryption
    otp_expires_at = db.Column(db.DateTime, index=True)

    # Many-to-many relationship with hospitals
    hospitals = db.relationship('Hospital', secondary=patient_hospital, backref=db.backref('patients', lazy=True))
    _symptoms = db.Column('symptoms', db.Text)
    _exposure_history = db.Column('exposure_history', db.Text)
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
    _drug_resistance = db.Column('drug_resistance', db.String(200))
    treatment_outcome = db.Column(db.String(100))
    relapse = db.Column(db.String(50))
    mortality = db.Column(db.String(50))
    _complications = db.Column('complications', db.Text)
    malnutrition = db.Column(db.String(50))
    _diabetes = db.Column('diabetes', db.String(200))
    _hiv = db.Column('hiv', db.String(200))
    chronic_lung_disease = db.Column(db.String(50))
    smoking_status = db.Column(db.String(100))  # Never/Former/Current/Unknown
    alcohol_use = db.Column(db.String(100))  # Never/Occasional/Regular/Unknown
    oxygen_saturation_spo2 = db.Column(db.Float)  # %
    living_conditions = db.Column(db.String(100))
    access_to_healthcare = db.Column(db.String(50))
    _city = db.Column('city', db.String(200))
    region_code = db.Column(db.String(50))
    _antibiotic_usage_history = db.Column('antibiotic_usage_history', db.Text)
    # Symptom checkboxes for ML model
    has_fever = db.Column(db.String(10))  # Yes/No/Unknown
    has_cough = db.Column(db.String(10))
    has_weight_loss = db.Column(db.String(10))
    has_night_sweats = db.Column(db.String(10))
    has_chest_pain = db.Column(db.String(10))
    has_blood = db.Column(db.String(10))
    has_fatigue = db.Column(db.String(10))
    has_shortness_of_breath = db.Column(db.String(10))
    risk_score = db.Column(db.Float, default=0.0)  # 0-100 continuous risk score
    last_risk_calculation = db.Column(db.DateTime)
    data_sharing_consent = db.Column(db.String(50), default='pending')  # 'pending', 'granted', 'denied'
    consent_granted_at = db.Column(db.DateTime)
    consent_expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Property getters/setters for encrypted fields
    @property
    def patient_id(self):
        return decrypt_data(self._patient_id)

    @patient_id.setter
    def patient_id(self, value):
        self._patient_id = encrypt_data(value)

    @property
    def first_name(self):
        return decrypt_data(self._first_name)

    @first_name.setter
    def first_name(self, value):
        self._first_name = encrypt_data(value)

    @property
    def last_name(self):
        return decrypt_data(self._last_name)

    @last_name.setter
    def last_name(self, value):
        self._last_name = encrypt_data(value)

    @property
    def region(self):
        return decrypt_data(self._region)

    @region.setter
    def region(self, value):
        self._region = encrypt_data(value)

    @property
    def occupation(self):
        return decrypt_data(self._occupation)

    @occupation.setter
    def occupation(self, value):
        self._occupation = encrypt_data(value)

    @property
    def symptoms(self):
        return decrypt_data(self._symptoms)

    @symptoms.setter
    def symptoms(self, value):
        self._symptoms = encrypt_data(value)

    @property
    def exposure_history(self):
        return decrypt_data(self._exposure_history)

    @exposure_history.setter
    def exposure_history(self, value):
        self._exposure_history = encrypt_data(value)

    @property
    def drug_resistance(self):
        return decrypt_data(self._drug_resistance)

    @drug_resistance.setter
    def drug_resistance(self, value):
        self._drug_resistance = encrypt_data(value)

    @property
    def complications(self):
        return decrypt_data(self._complications)

    @complications.setter
    def complications(self, value):
        self._complications = encrypt_data(value)

    @property
    def diabetes(self):
        return decrypt_data(self._diabetes)

    @diabetes.setter
    def diabetes(self, value):
        self._diabetes = encrypt_data(value)

    @property
    def hiv(self):
        return decrypt_data(self._hiv)

    @hiv.setter
    def hiv(self, value):
        self._hiv = encrypt_data(value)

    @property
    def city(self):
        return decrypt_data(self._city)

    @city.setter
    def city(self, value):
        self._city = encrypt_data(value)

    @property
    def antibiotic_usage_history(self):
        return decrypt_data(self._antibiotic_usage_history)

    @antibiotic_usage_history.setter
    def antibiotic_usage_history(self, value):
        self._antibiotic_usage_history = encrypt_data(value)

    @property
    def phone_number(self):
        return decrypt_data(self._phone_number)

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = encrypt_data(value)

    @property
    def otp_code(self):
        return decrypt_data(self._otp_code)

    @otp_code.setter
    def otp_code(self, value):
        self._otp_code = encrypt_data(value)

    def get_primary_hospital(self):
        """Get the primary hospital for this patient"""
        # Use the already loaded hospitals relationship to avoid extra DB queries
        # Since we don't have direct access to the association table's is_primary from the relationship,
        # fallback to first hospital
        if self.hospitals:
            return self.hospitals[0]
        return None

    def to_dict(self):
        primary_hospital = self.get_primary_hospital()
        hospital_count = len(self.hospitals)
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "role": "patient",
            "hospital_id": primary_hospital.id if primary_hospital else None,
            "hospital": primary_hospital.to_dict() if primary_hospital else None,
            "hospitals": [h.to_dict() for h in self.hospitals],
            "hospital_count": hospital_count,
            "is_single_hospital": hospital_count == 1,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
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
            "data_sharing_consent": self.data_sharing_consent,
            "consent_granted_at": self.consent_granted_at.isoformat() if self.consent_granted_at else None,
            "consent_expires_at": self.consent_expires_at.isoformat() if self.consent_expires_at else None,
            "has_shortness_of_breath": self.has_shortness_of_breath,
            "risk_score": self.risk_score,
            "last_risk_calculation": self.last_risk_calculation.isoformat() if self.last_risk_calculation else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    def to_list_dict(self):
        """Lightweight dict for list views—only includes necessary fields for speed"""
        hospital_count = len(self.hospitals)
        hospital_ids = [h.id for h in self.hospitals]
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "is_single_hospital": hospital_count == 1,
            "hospital_ids": hospital_ids,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "symptoms": self.symptoms,
            "tb_status_label": self.tb_status_label,
            "genexpert_test": self.genexpert_test,
            "sputum_smear_test": self.sputum_smear_test,
            "chest_xray": self.chest_xray,
            "has_fever": self.has_fever,
            "has_cough": self.has_cough,
            "has_weight_loss": self.has_weight_loss,
            "has_night_sweats": self.has_night_sweats,
            "has_chest_pain": self.has_chest_pain,
            "has_blood": self.has_blood,
            "weight": self.weight,
            "oxygen_saturation_spo2": self.oxygen_saturation_spo2,
            "contact_with_tb_patient": self.contact_with_tb_patient,
            "previous_tb_treatment": self.previous_tb_treatment,
            "hiv": self.hiv,
            "drug_resistance": self.drug_resistance
        }

class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    clinician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    diagnosis_type = db.Column(db.String(100))
    risk_level = db.Column(db.String(50))
    confidence_percent = db.Column(db.Float)
    _details = db.Column('details', db.Text)
    _ml_prediction = db.Column('ml_prediction', db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('diagnoses', lazy=True))
    clinician = db.relationship('User', backref=db.backref('diagnoses', lazy=True))
    hospital = db.relationship('Hospital', backref=db.backref('diagnoses', lazy=True))

    @property
    def details(self):
        return decrypt_data(self._details)

    @details.setter
    def details(self, value):
        self._details = encrypt_data(value)

    @property
    def ml_prediction(self):
        return decrypt_data(self._ml_prediction)

    @ml_prediction.setter
    def ml_prediction(self, value):
        self._ml_prediction = encrypt_data(value)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "clinician_id": self.clinician_id,
            "hospital_id": self.hospital_id,
            "hospital": self.hospital.to_dict() if self.hospital else None,
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
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    treatment_type = db.Column(db.String(100))
    _drugs = db.Column('drugs', db.Text)
    duration = db.Column(db.String(100))
    _dosage = db.Column('dosage', db.Text)
    _administration_notes = db.Column('administration_notes', db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('treatments', lazy=True))
    diagnosis = db.relationship('Diagnosis', backref=db.backref('treatments', lazy=True))
    hospital = db.relationship('Hospital', backref=db.backref('treatments', lazy=True))

    @property
    def drugs(self):
        return decrypt_data(self._drugs)

    @drugs.setter
    def drugs(self, value):
        self._drugs = encrypt_data(value)

    @property
    def dosage(self):
        return decrypt_data(self._dosage)

    @dosage.setter
    def dosage(self, value):
        self._dosage = encrypt_data(value)

    @property
    def administration_notes(self):
        return decrypt_data(self._administration_notes)

    @administration_notes.setter
    def administration_notes(self, value):
        self._administration_notes = encrypt_data(value)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "diagnosis_id": self.diagnosis_id,
            "hospital_id": self.hospital_id,
            "hospital": self.hospital.to_dict() if self.hospital else None,
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
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)
    alert_type = db.Column(db.String(100))
    _message = db.Column('message', db.Text)
    severity = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('alerts', lazy=True))
    user = db.relationship('User', backref=db.backref('alerts', lazy=True))
    hospital = db.relationship('Hospital', backref=db.backref('alerts', lazy=True))

    @property
    def message(self):
        return decrypt_data(self._message)

    @message.setter
    def message(self, value):
        self._message = encrypt_data(value)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "user_id": self.user_id,
            "hospital_id": self.hospital_id,
            "hospital": self.hospital.to_dict() if self.hospital else None,
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
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    test_type = db.Column(db.String(100), nullable=False)  # e.g., "GeneXpert", "Sputum Smear", "Chest X-ray", "Blood Test"
    status = db.Column(db.String(50), default='requested')  # requested, in_progress, completed, cancelled
    _results = db.Column('results', db.Text)
    _notes = db.Column('notes', db.Text)
    completed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('lab_tests', lazy=True))
    requester = db.relationship('User', foreign_keys=[requested_by], backref=db.backref('requested_lab_tests', lazy=True))
    completer = db.relationship('User', foreign_keys=[completed_by], backref=db.backref('completed_lab_tests', lazy=True))
    hospital = db.relationship('Hospital', backref=db.backref('lab_tests', lazy=True))

    @property
    def results(self):
        return decrypt_data(self._results)

    @results.setter
    def results(self, value):
        self._results = encrypt_data(value)

    @property
    def notes(self):
        return decrypt_data(self._notes)

    @notes.setter
    def notes(self, value):
        self._notes = encrypt_data(value)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": f"{self.patient.first_name or ''} {self.patient.last_name or ''}".strip() if self.patient else None,
            "requested_by": self.requested_by,
            "requester_name": self.requester.username if self.requester else None,
            "hospital_id": self.hospital_id,
            "hospital": self.hospital.to_dict() if self.hospital else None,
            "test_type": self.test_type,
            "status": self.status,
            "results": self.results,
            "notes": self.notes,
            "completed_by": self.completed_by,
            "completer_name": self.completer.username if self.completer else None,
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


class PharmacyInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    atc_drug_id = db.Column(db.Integer, db.ForeignKey('atc_drug.id'), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)  # Number of units in stock
    unit_type = db.Column(db.String(50))  # e.g., tablets, vials, bottles
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    location = db.Column(db.String(100))  # Shelf/Storage location
    minimum_stock_level = db.Column(db.Integer, default=10)  # Alert threshold
    last_restocked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    hospital = db.relationship('Hospital', backref=db.backref('pharmacy_inventory', lazy=True))
    atc_drug = db.relationship('ATCDrug', backref=db.backref('inventory_records', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "hospital_id": self.hospital_id,
            "atc_drug_id": self.atc_drug_id,
            "atc_drug": self.atc_drug.to_dict() if self.atc_drug else None,
            "stock_quantity": self.stock_quantity,
            "unit_type": self.unit_type,
            "batch_number": self.batch_number,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "location": self.location,
            "minimum_stock_level": self.minimum_stock_level,
            "last_restocked": self.last_restocked.isoformat() if self.last_restocked else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _medication = db.Column('medication', db.String(200), nullable=False)
    atc_drug_id = db.Column(db.Integer, db.ForeignKey('atc_drug.id'))
    _dosage = db.Column('dosage', db.String(200))
    dosage_mg = db.Column(db.Float)  # Dosage in milligrams per dose
    frequency = db.Column(db.String(50))  # e.g., "2 times daily", "3 times daily"
    duration_days = db.Column(db.Integer)
    total_mg = db.Column(db.Float)  # Total dosage in milligrams
    ddds = db.Column(db.Float)  # Number of Defined Daily Doses
    tablets_per_dose = db.Column(db.Integer)  # Number of tablets per dose
    total_tablets = db.Column(db.Integer)  # Total tablets to dispense
    duration = db.Column(db.String(100))
    risk_level = db.Column(db.String(50))
    ml_recommended = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, dispensed
    _rejection_reason = db.Column('rejection_reason', db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    dispensed_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Pharmacist who dispensed
    dispensed_at = db.Column(db.DateTime)  # When medication was dispensed
    stock_updated = db.Column(db.Boolean, default=False)  # Whether stock was updated
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))
    diagnosis = db.relationship('Diagnosis', backref=db.backref('prescriptions', lazy=True))
    hospital = db.relationship('Hospital', backref=db.backref('prescriptions', lazy=True))
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_prescriptions', lazy=True))
    approver = db.relationship('User', foreign_keys=[approved_by], backref=db.backref('approved_prescriptions', lazy=True))
    dispenser = db.relationship('User', foreign_keys=[dispensed_by], backref=db.backref('dispensed_prescriptions', lazy=True))
    atc_drug = db.relationship('ATCDrug', backref=db.backref('prescriptions', lazy=True))

    @property
    def medication(self):
        return decrypt_data(self._medication)

    @medication.setter
    def medication(self, value):
        self._medication = encrypt_data(value)

    @property
    def dosage(self):
        return decrypt_data(self._dosage)

    @dosage.setter
    def dosage(self, value):
        self._dosage = encrypt_data(value)

    @property
    def rejection_reason(self):
        return decrypt_data(self._rejection_reason)

    @rejection_reason.setter
    def rejection_reason(self, value):
        self._rejection_reason = encrypt_data(value)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "diagnosis_id": self.diagnosis_id,
            "hospital_id": self.hospital_id,
            "hospital": self.hospital.to_dict() if self.hospital else None,
            "created_by": self.created_by,
            "medication": self.medication,
            "atc_drug_id": self.atc_drug_id,
            "atc_drug": self.atc_drug.to_dict() if self.atc_drug else None,
            "dosage": self.dosage,
            "dosage_mg": self.dosage_mg,
            "frequency": self.frequency,
            "duration_days": self.duration_days,
            "total_mg": self.total_mg,
            "ddds": self.ddds,
            "tablets_per_dose": self.tablets_per_dose,
            "total_tablets": self.total_tablets,
            "duration": self.duration,
            "risk_level": self.risk_level,
            "ml_recommended": self.ml_recommended,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "dispensed_by": self.dispensed_by,
            "dispensed_at": self.dispensed_at.isoformat() if self.dispensed_at else None,
            "stock_updated": self.stock_updated,
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
    
    # Immutable audit fields for tamper evidence
    entry_hash = db.Column('entry_hash', db.String(64), nullable=False)  # SHA-256 hash
    previous_hash = db.Column(db.String(64))  # Chain to previous log entry
    ip_address = db.Column(db.String(50))  # Client IP for additional verification
    user_agent = db.Column(db.String(500))  # Browser/client info
    is_verified = db.Column(db.Boolean, default=True)  # Integrity check flag

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def compute_hash(self):
        """Compute cryptographic hash of audit log entry for tamper evidence"""
        import hashlib
        import json
        
        # Create canonical representation of the log entry
        data = {
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'previous_hash': self.previous_hash,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
        
        # Sort keys for consistent hashing
        canonical = json.dumps(data, sort_keys=True, default=str)
        hash_value = hashlib.sha256(canonical.encode()).hexdigest()
        self.entry_hash = hash_value
        return hash_value

    def verify_integrity(self):
        """Verify that the audit log entry has not been tampered with"""
        computed_hash = self.compute_hash()
        return computed_hash == self.entry_hash

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "audit_hash": self.entry_hash,
            "previous_hash": self.previous_hash,
            "ip_address": self.ip_address,
            "is_verified": self.is_verified,
            "user": {
                "id": self.user.id if self.user else None,
                "username": self.user.username if self.user else None,
                "role": self.user.role if self.user else None
            } if self.user else None
        }


# Event listener to make AuditLog immutable (prevent updates/deletes)
@event.listens_for(AuditLog, 'before_insert')
def before_audit_log_insert(mapper, connection, target):
    """Compute hash and chain to previous log entry before insert"""
    # Get previous audit log entry for chaining
    from sqlalchemy import select
    previous_log = connection.execute(
        select(AuditLog).order_by(AuditLog.id.desc()).limit(1)
    ).first()
    
    if previous_log:
        target.previous_hash = previous_log.entry_hash
    
    # Capture IP address from request context if available
    try:
        from flask import request
        target.ip_address = request.remote_addr
        target.user_agent = request.headers.get('User-Agent')
    except:
        pass
    
    # Compute and set hash
    target.entry_hash = target.compute_hash()

@event.listens_for(AuditLog, 'before_update')
def before_audit_log_update(mapper, connection, target):
    """Prevent updates to audit logs - they should be immutable"""
    raise Exception("Audit logs are immutable and cannot be updated")

@event.listens_for(AuditLog, 'before_delete')
def before_audit_log_delete(mapper, connection, target):
    """Prevent deletion of audit logs - they should be immutable"""
    raise Exception("Audit logs are immutable and cannot be deleted")



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


class PatientConsent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    requesting_hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    sharing_hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    consent_type = db.Column(db.String(50), nullable=False)  # 'full_record', 'diagnoses_only', 'lab_tests_only'
    status = db.Column(db.String(50), default='pending')  # 'pending', 'granted', 'denied', 'revoked'
    granted_at = db.Column(db.DateTime)
    revoked_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # Optional expiry date
    verification_method = db.Column(db.String(50))  # 'sms', 'email', 'in_person'
    _verification_code = db.Column('verification_code', db.String(200))  # Encrypted verification code
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    patient = db.relationship('Patient', backref=db.backref('consents', lazy=True))
    requesting_hospital = db.relationship('Hospital', foreign_keys=[requesting_hospital_id], backref=db.backref('incoming_consents', lazy=True))
    sharing_hospital = db.relationship('Hospital', foreign_keys=[sharing_hospital_id], backref=db.backref('outgoing_consents', lazy=True))
    
    @property
    def verification_code(self):
        from utils.security import decrypt_data
        return decrypt_data(self._verification_code) if self._verification_code else None
    
    @verification_code.setter
    def verification_code(self, value):
        from utils.security import encrypt_data
        self._verification_code = encrypt_data(value) if value else None
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "requesting_hospital_id": self.requesting_hospital_id,
            "requesting_hospital": self.requesting_hospital.to_dict() if self.requesting_hospital else None,
            "sharing_hospital_id": self.sharing_hospital_id,
            "sharing_hospital": self.sharing_hospital.to_dict() if self.sharing_hospital else None,
            "consent_type": self.consent_type,
            "status": self.status,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "verification_method": self.verification_method,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

