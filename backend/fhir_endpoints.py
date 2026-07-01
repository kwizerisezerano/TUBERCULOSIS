"""
HL7 FHIR API Endpoints for Hospital Interoperability
Implements FHIR R4 resources for healthcare data exchange
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from models.models import db, Patient, Hospital, Diagnosis, Treatment, LabTest, Prescription
from utils.security import decrypt_data

fhir_bp = Blueprint('fhir', __name__, url_prefix='/fhir')

def patient_to_fhir(patient):
    """Convert Patient model to FHIR Patient resource"""
    return {
        "resourceType": "Patient",
        "id": str(patient.id),
        "identifier": [{
            "system": "http://tb-system.org/patient-ids",
            "value": decrypt_data(patient._patient_id)
        }],
        "name": [{
            "given": [decrypt_data(patient._first_name)] if patient._first_name else [],
            "family": decrypt_data(patient._last_name) if patient._last_name else ""
        }],
        "gender": patient.gender.lower() if patient.gender else "unknown",
        "birthDate": f"{datetime.now().year - (patient.age or 0)}-01-01",  # Approximate from age
        "address": [{
            "city": decrypt_data(patient._city) if patient._city else "",
            "state": decrypt_data(patient._region) if patient._region else "",
            "country": "Rwanda"
        }],
        "extension": [{
            "url": "http://tb-system.org/StructureDefinition/tb-specific",
            "extension": [
                {"url": "tbStatus", "valueString": patient.tb_status_label or "unknown"},
                {"url": "riskScore", "valueDecimal": patient.risk_score or 0.0},
                {"url": "dataSharingConsent", "valueString": patient.data_sharing_consent or "pending"}
            ]
        }]
    }

def observation_to_fhir(lab_test):
    """Convert LabTest model to FHIR Observation resource"""
    return {
        "resourceType": "Observation",
        "id": str(lab_test.id),
        "status": "final" if lab_test.status == "completed" else "preliminary",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": lab_test.test_type,
                "display": lab_test.test_type
            }],
            "text": lab_test.test_type
        },
        "valueString": lab_test.results if lab_test.results else "Not available",
        "effectiveDateTime": lab_test.completed_at.isoformat() if lab_test.completed_at else None,
        "note": [{"text": lab_test.notes}] if lab_test.notes else []
    }

def condition_to_fhir(diagnosis):
    """Convert Diagnosis model to FHIR Condition resource"""
    return {
        "resourceType": "Condition",
        "id": str(diagnosis.id),
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": "confirmed"
            }]
        },
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "56717001",
                "display": "Tuberculosis of lung"
            }],
            "text": diagnosis.diagnosis
        },
        "subject": {
            "reference": f"Patient/{diagnosis.patient_id}",
            "display": f"Patient {diagnosis.patient_id}"
        },
        "recordedDate": diagnosis.created_at.isoformat() if diagnosis.created_at else None
    }

def medication_request_to_fhir(prescription):
    """Convert Prescription model to FHIR MedicationRequest resource"""
    return {
        "resourceType": "MedicationRequest",
        "id": str(prescription.id),
        "status": prescription.status.lower(),
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [{
                "system": "http://www.whocc.no/atc",
                "code": prescription.medicines or "unknown",
                "display": prescription.medicines or "Unknown medication"
            }],
            "text": prescription.medicines or "Unknown medication"
        },
        "subject": {
            "reference": f"Patient/{prescription.patient_id}",
            "display": f"Patient {prescription.patient_id}"
        },
        "dosageInstruction": [{
            "text": prescription.dosages or "As prescribed",
            "timing": {
                "repeat": {
                    "frequency": prescription.frequency or "daily"
                }
            }
        }],
        "authoredOn": prescription.generated_date.isoformat() if prescription.generated_date else None
    }

@fhir_bp.route('/Patient/<patient_id>', methods=['GET'])
def get_fhir_patient(patient_id):
    """Get FHIR Patient resource by ID"""
    try:
        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            return jsonify({
                "resourceType": "OperationOutcome",
                "issue": [{"severity": "error", "code": "not-found", "diagnostics": "Patient not found"}]
            }), 404
        
        return jsonify(patient_to_fhir(patient))
    except Exception as e:
        return jsonify({
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "processing", "diagnostics": str(e)}]
        }), 500

@fhir_bp.route('/Patient', methods=['GET'])
def search_fhir_patients():
    """Search FHIR Patient resources"""
    try:
        identifier = request.args.get('identifier')
        name = request.args.get('name')
        birthdate = request.args.get('birthdate')
        
        query = Patient.query
        
        if identifier:
            query = query.filter(Patient._patient_id.like(f'%{identifier}%'))
        if name:
            query = query.filter(
                db.or_(
                    Patient._first_name.like(f'%{name}%'),
                    Patient._last_name.like(f'%{name}%')
                )
            )
        
        patients = query.limit(50).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(patients),
            "entry": [{"resource": patient_to_fhir(p)} for p in patients]
        }
        
        return jsonify(bundle)
    except Exception as e:
        return jsonify({
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "processing", "diagnostics": str(e)}]
        }), 500

@fhir_bp.route('/Observation', methods=['GET'])
def search_fhir_observations():
    """Search FHIR Observation resources (lab results)"""
    try:
        patient_id = request.args.get('subject')
        code = request.args.get('code')
        
        query = LabTest.query
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if code:
            query = query.filter(LabTest.test_type.like(f'%{code}%'))
        
        lab_tests = query.limit(50).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(lab_tests),
            "entry": [{"resource": observation_to_fhir(lt)} for lt in lab_tests]
        }
        
        return jsonify(bundle)
    except Exception as e:
        return jsonify({
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "processing", "diagnostics": str(e)}]
        }), 500

@fhir_bp.route('/Condition', methods=['GET'])
def search_fhir_conditions():
    """Search FHIR Condition resources (diagnoses)"""
    try:
        patient_id = request.args.get('subject')
        
        query = Diagnosis.query
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        diagnoses = query.limit(50).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(diagnoses),
            "entry": [{"resource": condition_to_fhir(d)} for d in diagnoses]
        }
        
        return jsonify(bundle)
    except Exception as e:
        return jsonify({
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "processing", "diagnostics": str(e)}]
        }), 500

@fhir_bp.route('/MedicationRequest', methods=['GET'])
def search_fhir_medication_requests():
    """Search FHIR MedicationRequest resources (prescriptions)"""
    try:
        patient_id = request.args.get('subject')
        
        query = Prescription.query
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        prescriptions = query.limit(50).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(prescriptions),
            "entry": [{"resource": medication_request_to_fhir(p)} for p in prescriptions]
        }
        
        return jsonify(bundle)
    except Exception as e:
        return jsonify({
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "processing", "diagnostics": str(e)}]
        }), 500

@fhir_bp.route('/CapabilityStatement', methods=['GET'])
def capability_statement():
    """FHIR Capability Statement - describes system capabilities"""
    return jsonify({
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": datetime.now().isoformat(),
        "publisher": "TB Predictive EHR Analytics Dashboard",
        "kind": "instance",
        "implementation": {
            "description": "TB Predictive EHR Analytics Dashboard FHIR Server",
            "url": request.host_url
        },
        "rest": [{
            "mode": "server",
            "resource": [
                {
                    "type": "Patient",
                    "interaction": [{"code": "read"}, {"code": "search-type"}],
                    "searchParam": [
                        {"name": "identifier", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "birthdate", "type": "date"}
                    ]
                },
                {
                    "type": "Observation",
                    "interaction": [{"code": "search-type"}],
                    "searchParam": [
                        {"name": "subject", "type": "reference"},
                        {"name": "code", "type": "token"}
                    ]
                },
                {
                    "type": "Condition",
                    "interaction": [{"code": "search-type"}],
                    "searchParam": [
                        {"name": "subject", "type": "reference"}
                    ]
                },
                {
                    "type": "MedicationRequest",
                    "interaction": [{"code": "search-type"}],
                    "searchParam": [
                        {"name": "subject", "type": "reference"}
                    ]
                }
            ]
        }]
    })
