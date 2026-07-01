"""
HL7 FHIR API Endpoints for Hospital Interoperability

Implements FHIR R4 resources for:
- Patient (demographics)
- Observation (lab results, vital signs)
- Condition (diagnoses)
- MedicationRequest (prescriptions)

Follows HL7 FHIR R4 specification for healthcare data exchange.
"""
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

fhir_bp = Blueprint('fhir', __name__, url_prefix='/fhir')

# FHIR Resource Types
FHIR_RESOURCES = {
    'Patient': 'http://hl7.org/fhir/StructureDefinition/Patient',
    'Observation': 'http://hl7.org/fhir/StructureDefinition/Observation',
    'Condition': 'http://hl7.org/fhir/StructureDefinition/Condition',
    'MedicationRequest': 'http://hl7.org/fhir/StructureDefinition/MedicationRequest'
}


def fhir_response(resource_type, resource_data, status=200):
    """Format response as FHIR resource"""
    return jsonify({
        'resourceType': resource_type,
        'resource': resource_data,
        'meta': {
            'profile': [FHIR_RESOURCES.get(resource_type)]
        }
    }), status


def fhir_bundle(resources, resource_type, total=None):
    """Format response as FHIR Bundle"""
    if total is None:
        total = len(resources)
    
    return jsonify({
        'resourceType': 'Bundle',
        'type': 'searchset',
        'total': total,
        'entry': [
            {
                'resource': resource,
                'search': {
                    'mode': 'match'
                }
            }
            for resource in resources
        ]
    })


def patient_to_fhir(patient):
    """Convert internal Patient model to FHIR Patient resource"""
    return {
        'resourceType': 'Patient',
        'id': str(patient.id),
        'identifier': [
            {
                'use': 'usual',
                'system': 'http://tb-diagnostic.org/patient-id',
                'value': patient.patient_id
            }
        ],
        'name': [
            {
                'use': 'official',
                'family': patient.last_name or 'Unknown',
                'given': [patient.first_name or 'Unknown']
            }
        ],
        'gender': patient.gender.lower() if patient.gender in ['Male', 'Female'] else 'unknown',
        'birthDate': f"{datetime.now().year - patient.age}-01-01" if patient.age else None,
        'telecom': [
            {
                'system': 'email',
                'use': 'home'
            }
        ],
        'address': [
            {
                'city': getattr(patient, 'city', 'Unknown'),
                'country': 'RW'
            }
        ],
        'extension': [
            {
                'url': 'http://tb-diagnostic.org/StructureDefinition/tb-risk-score',
                'valueDecimal': patient.risk_score or 0.0
            },
            {
                'url': 'http://tb-diagnostic.org/StructureDefinition/data-sharing-consent',
                'valueCode': patient.data_sharing_consent or 'pending'
            }
        ]
    }


def observation_to_fhir(lab_test):
    """Convert internal LabTest model to FHIR Observation resource"""
    status_mapping = {
        'Pending': 'preliminary',
        'Completed': 'final',
        'Rejected': 'cancelled'
    }
    
    return {
        'resourceType': 'Observation',
        'id': str(lab_test.id),
        'status': status_mapping.get(lab_test.status, 'final'),
        'category': [
            {
                'coding': [
                    {
                        'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                        'code': 'laboratory',
                        'display': 'Laboratory'
                    }
                ]
            }
        ],
        'code': {
            'coding': [
                {
                    'system': 'http://loinc.org',
                    'code': lab_test.test_type,
                    'display': lab_test.test_type
                }
            ],
            'text': lab_test.test_type
        },
        'subject': {
            'reference': f'Patient/{lab_test.patient_id}',
            'display': lab_test.patient_id
        },
        'effectiveDateTime': lab_test.test_date.isoformat() if lab_test.test_date else None,
        'valueString': lab_test.result,
        'interpretation': [
            {
                'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
                'code': 'N' if lab_test.result and 'Negative' in lab_test.result else 'A',
                'display': 'Normal' if lab_test.result and 'Negative' in lab_test.result else 'Abnormal'
            }
        ]
    }


def condition_to_fhir(diagnosis):
    """Convert internal Diagnosis model to FHIR Condition resource"""
    clinical_status = 'active' if diagnosis.treatment_outcome in ['ongoing', None] else 'resolved'
    
    return {
        'resourceType': 'Condition',
        'id': str(diagnosis.id),
        'clinicalStatus': {
            'coding': [
                {
                    'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical',
                    'code': clinical_status,
                    'display': clinical_status.capitalize()
                }
            ]
        },
        'verificationStatus': {
            'coding': [
                {
                    'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status',
                    'code': 'confirmed',
                    'display': 'Confirmed'
                }
            ]
        },
        'category': [
            {
                'coding': [
                    {
                        'system': 'http://terminology.hl7.org/CodeSystem/condition-category',
                        'code': 'encounter-diagnosis',
                        'display': 'Encounter Diagnosis'
                    }
                ]
            }
        ],
        'code': {
            'coding': [
                {
                    'system': 'http://snomed.info/sct',
                    'code': '56711008',
                    'display': 'Tuberculosis'
                }
            ],
            'text': diagnosis.treatment_type or 'Tuberculosis'
        },
        'subject': {
            'reference': f'Patient/{diagnosis.patient_id}',
            'display': diagnosis.patient_id
        },
        'onsetDateTime': diagnosis.date_of_diagnosis.isoformat() if diagnosis.date_of_diagnosis else None,
        'note': [
            {
                'text': f"Drug resistance: {diagnosis.drug_resistance if hasattr(diagnosis, 'drug_resistance') else 'Unknown'}"
            }
        ]
    }


def medication_request_to_fhir(prescription):
    """Convert internal Prescription model to FHIR MedicationRequest resource"""
    status_mapping = {
        'Pending': 'active',
        'Approved': 'completed',
        'Rejected': 'cancelled'
    }
    
    return {
        'resourceType': 'MedicationRequest',
        'id': str(prescription.id),
        'status': status_mapping.get(prescription.status, 'active'),
        'intent': 'order',
        'medicationCodeableConcept': {
            'coding': [
                {
                    'system': 'http://www.whocc.no/atc',
                    'code': prescription.medication,
                    'display': prescription.medication
                }
            ],
            'text': prescription.medication
        },
        'subject': {
            'reference': f'Patient/{prescription.patient_id}',
            'display': prescription.patient_id
        },
        'authoredOn': prescription.created_at.isoformat() if prescription.created_at else None,
        'dosageInstruction': [
            {
                'text': f"{prescription.dosage}, {prescription.frequency if hasattr(prescription, 'frequency') else 'As directed'}",
                'doseAndRate': [
                    {
                        'doseQuantity': {
                            'value': float(prescription.dosage.split()[0]) if prescription.dosage else None,
                            'unit': prescription.dosage.split()[1] if prescription.dosage and len(prescription.dosage.split()) > 1 else 'mg',
                            'system': 'http://unitsofmeasure.org',
                            'code': 'mg'
                        }
                    }
                ]
            }
        ]
    }


@fhir_bp.route('/Patient', methods=['GET'])
@jwt_required()
def get_fhir_patients():
    """
    FHIR Patient Search Endpoint
    
    Query Parameters:
    - identifier: Patient ID
    - name: Patient name (partial match)
    - birthdate: Birth date
    - _count: Maximum number of results (default: 50)
    """
    from app import db
    from models.models import Patient
    
    identifier = request.args.get('identifier')
    name = request.args.get('name')
    _count = int(request.args.get('_count', 50))
    
    query = Patient.query
    
    if identifier:
        query = query.filter(Patient._patient_id.like(f'%{identifier}%'))
    
    if name:
        query = query.filter(
            (Patient._first_name.like(f'%{name}%')) |
            (Patient._last_name.like(f'%{name}%'))
        )
    
    patients = query.limit(_count).all()
    
    fhir_patients = [patient_to_fhir(p) for p in patients]
    
    return fhir_bundle(fhir_patients, 'Patient')


@fhir_bp.route('/Patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_fhir_patient(patient_id):
    """Get specific patient by internal ID"""
    from models.models import Patient
    patient = Patient.query.get_or_404(patient_id)
    return fhir_response('Patient', patient_to_fhir(patient))


@fhir_bp.route('/Patient', methods=['POST'])
@jwt_required()
def create_fhir_patient():
    """
    Create patient from FHIR Patient resource
    
    Accepts FHIR Patient resource JSON and creates internal patient record
    """
    from app import db
    from models.models import Patient
    
    data = request.get_json()
    
    if data.get('resourceType') != 'Patient':
        return jsonify({'error': 'ResourceType must be Patient'}), 400
    
    # Extract patient data from FHIR resource
    name_data = data.get('name', [{}])[0]
    identifier_data = data.get('identifier', [{}])[0]
    
    patient_id = identifier_data.get('value')
    first_name = name_data.get('given', [''])[0]
    last_name = name_data.get('family', '')
    gender = data.get('gender', 'unknown')
    
    # Check if patient already exists
    existing = Patient.query.filter_by(_patient_id=patient_id).first()
    if existing:
        return jsonify({'error': 'Patient already exists'}), 409
    
    # Create new patient
    patient = Patient(
        patient_id=patient_id,
        first_name=first_name,
        last_name=last_name,
        gender=gender.capitalize(),
        age=30,  # Default age
        city='Kigali',
        data_sharing_consent='pending'
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return fhir_response('Patient', patient_to_fhir(patient), 201)


@fhir_bp.route('/Observation', methods=['GET'])
@jwt_required()
def get_fhir_observations():
    """
    FHIR Observation Search Endpoint (Lab Results)
    
    Query Parameters:
    - subject: Patient ID
    - code: Test type
    - date: Observation date
    - _count: Maximum results (default: 50)
    """
    from models.models import LabTest
    
    subject = request.args.get('subject')
    code = request.args.get('code')
    _count = int(request.args.get('_count', 50))
    
    query = LabTest.query
    
    if subject:
        query = query.filter(LabTest.patient_id == subject)
    
    if code:
        query = query.filter(LabTest.test_type == code)
    
    lab_tests = query.limit(_count).all()
    
    fhir_observations = [observation_to_fhir(lt) for lt in lab_tests]
    
    return fhir_bundle(fhir_observations, 'Observation')


@fhir_bp.route('/Observation', methods=['POST'])
@jwt_required()
def create_fhir_observation():
    """
    Create lab result from FHIR Observation resource
    
    Accepts FHIR Observation resource and creates internal lab test record
    """
    from app import db
    from models.models import LabTest
    
    data = request.get_json()
    
    if data.get('resourceType') != 'Observation':
        return jsonify({'error': 'ResourceType must be Observation'}), 400
    
    # Extract observation data
    patient_ref = data.get('subject', {}).get('reference', '')
    patient_id = patient_ref.replace('Patient/', '') if patient_ref else None
    code = data.get('code', {}).get('coding', [{}])[0].get('code')
    value = data.get('valueString')
    
    if not patient_id or not code:
        return jsonify({'error': 'Missing required fields: subject, code'}), 400
    
    # Create lab test
    lab_test = LabTest(
        patient_id=patient_id,
        test_type=code,
        result=value,
        status='Completed',
        test_date=datetime.now()
    )
    
    db.session.add(lab_test)
    db.session.commit()
    
    return fhir_response('Observation', observation_to_fhir(lab_test), 201)


@fhir_bp.route('/Condition', methods=['GET'])
@jwt_required()
def get_fhir_conditions():
    """
    FHIR Condition Search Endpoint (Diagnoses)
    
    Query Parameters:
    - subject: Patient ID
    - clinical-status: Condition status
    - _count: Maximum results (default: 50)
    """
    from models.models import Diagnosis
    
    subject = request.args.get('subject')
    clinical_status = request.args.get('clinical-status')
    _count = int(request.args.get('_count', 50))
    
    query = Diagnosis.query
    
    if subject:
        query = query.filter(Diagnosis.patient_id == subject)
    
    diagnoses = query.limit(_count).all()
    
    fhir_conditions = [condition_to_fhir(d) for d in diagnoses]
    
    return fhir_bundle(fhir_conditions, 'Condition')


@fhir_bp.route('/MedicationRequest', methods=['GET'])
@jwt_required()
def get_fhir_medication_requests():
    """
    FHIR MedicationRequest Search Endpoint (Prescriptions)
    
    Query Parameters:
    - subject: Patient ID
    - status: Prescription status
    - _count: Maximum results (default: 50)
    """
    from models.models import Prescription
    
    subject = request.args.get('subject')
    status = request.args.get('status')
    _count = int(request.args.get('_count', 50))
    
    query = Prescription.query
    
    if subject:
        query = query.filter(Prescription.patient_id == subject)
    
    if status:
        query = query.filter(Prescription.status == status)
    
    prescriptions = query.limit(_count).all()
    
    fhir_prescriptions = [medication_request_to_fhir(p) for p in prescriptions]
    
    return fhir_bundle(fhir_prescriptions, 'MedicationRequest')


@fhir_bp.route('/MedicationRequest', methods=['POST'])
@jwt_required()
def create_fhir_medication_request():
    """
    Create prescription from FHIR MedicationRequest resource
    
    Accepts FHIR MedicationRequest and creates internal prescription record
    """
    from app import db
    from models.models import Prescription
    
    data = request.get_json()
    
    if data.get('resourceType') != 'MedicationRequest':
        return jsonify({'error': 'ResourceType must be MedicationRequest'}), 400
    
    # Extract medication request data
    patient_ref = data.get('subject', {}).get('reference', '')
    patient_id = patient_ref.replace('Patient/', '') if patient_ref else None
    medication = data.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('code')
    dosage = data.get('dosageInstruction', [{}])[0].get('text', 'As directed')
    
    if not patient_id or not medication:
        return jsonify({'error': 'Missing required fields: subject, medication'}), 400
    
    # Create prescription
    prescription = Prescription(
        patient_id=patient_id,
        medication=medication,
        dosage=dosage,
        status='Pending',
        approved_by=None
    )
    
    db.session.add(prescription)
    db.session.commit()
    
    return fhir_response('MedicationRequest', medication_request_to_fhir(prescription), 201)


@fhir_bp.route('/metadata', methods=['GET'])
def fhir_metadata():
    """
    FHIR Capability Statement
    
    Returns system metadata describing supported FHIR resources and operations
    """
    return jsonify({
        'resourceType': 'CapabilityStatement',
        'status': 'active',
        'date': datetime.now().isoformat(),
        'kind': 'instance',
        'fhirVersion': '4.0.1',
        'format': ['application/fhir+json'],
        'rest': [
            {
                'mode': 'server',
                'resource': [
                    {
                        'type': 'Patient',
                        'interaction': [
                            {'code': 'read'},
                            {'code': 'search-type'},
                            {'code': 'create'}
                        ],
                        'searchParam': [
                            {'name': 'identifier', 'type': 'string'},
                            {'name': 'name', 'type': 'string'}
                        ]
                    },
                    {
                        'type': 'Observation',
                        'interaction': [
                            {'code': 'read'},
                            {'code': 'search-type'},
                            {'code': 'create'}
                        ],
                        'searchParam': [
                            {'name': 'subject', 'type': 'reference'},
                            {'name': 'code', 'type': 'token'}
                        ]
                    },
                    {
                        'type': 'Condition',
                        'interaction': [
                            {'code': 'read'},
                            {'code': 'search-type'}
                        ],
                        'searchParam': [
                            {'name': 'subject', 'type': 'reference'}
                        ]
                    },
                    {
                        'type': 'MedicationRequest',
                        'interaction': [
                            {'code': 'read'},
                            {'code': 'search-type'},
                            {'code': 'create'}
                        ],
                        'searchParam': [
                            {'name': 'subject', 'type': 'reference'},
                            {'name': 'status', 'type': 'token'}
                        ]
                    }
                ]
            }
        ]
    })
