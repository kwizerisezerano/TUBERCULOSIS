"""
Patient Consent API Endpoints

Provides REST API for patient consent management:
- Request consent
- Grant/revoke consent
- Verify consent status
- View consent history
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.consent_manager import ConsentManager

consent_bp = Blueprint('consent', __name__, url_prefix='/api/consent')


@consent_bp.route('/request', methods=['POST'])
@jwt_required()
def request_consent():
    """
    Request consent from a patient
    
    Request Body:
    {
        "patient_id": "TB-2026-001",
        "consent_type": "data_sharing"  // optional, defaults to data_sharing
    }
    """
    data = request.get_json()
    patient_id = data.get('patient_id')
    consent_type = data.get('consent_type', 'data_sharing')
    requested_by = get_jwt_identity()
    
    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400
    
    result = ConsentManager.create_consent_request(patient_id, consent_type, requested_by)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify(result), 201


@consent_bp.route('/grant', methods=['POST'])
@jwt_required()
def grant_consent():
    """
    Grant consent for a patient
    
    Request Body:
    {
        "patient_id": "TB-2026-001",
        "consent_type": "data_sharing",
        "verification_method": "signature"  // optional
    }
    """
    data = request.get_json()
    patient_id = data.get('patient_id')
    consent_type = data.get('consent_type', 'data_sharing')
    verification_method = data.get('verification_method', 'signature')
    granted_by = get_jwt_identity()
    
    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400
    
    result = ConsentManager.grant_consent(patient_id, consent_type, granted_by, verification_method)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify(result), 200


@consent_bp.route('/revoke', methods=['POST'])
@jwt_required()
def revoke_consent():
    """
    Revoke consent for a patient
    
    Request Body:
    {
        "patient_id": "TB-2026-001",
        "reason": "Patient request"  // optional
    }
    """
    data = request.get_json()
    patient_id = data.get('patient_id')
    reason = data.get('reason', 'Patient request')
    revoked_by = get_jwt_identity()
    
    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400
    
    result = ConsentManager.revoke_consent(patient_id, revoked_by, reason)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify(result), 200


@consent_bp.route('/verify/<patient_id>', methods=['GET'])
@jwt_required()
def verify_consent(patient_id):
    """
    Verify consent status for a patient
    
    Query Parameters:
    - consent_type: Type of consent to verify (default: data_sharing)
    """
    consent_type = request.args.get('consent_type', 'data_sharing')
    
    result = ConsentManager.verify_consent(patient_id, consent_type)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify(result), 200


@consent_bp.route('/history/<patient_id>', methods=['GET'])
@jwt_required()
def get_consent_history(patient_id):
    """
    Get complete consent history for a patient
    """
    result = ConsentManager.get_consent_history(patient_id)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify(result), 200


@consent_bp.route('/check-access', methods=['POST'])
@jwt_required()
def check_data_access():
    """
    Check if data access is allowed based on consent
    
    Request Body:
    {
        "patient_id": "TB-2026-001",
        "access_type": "read"  // read, write, share
    }
    """
    data = request.get_json()
    patient_id = data.get('patient_id')
    access_type = data.get('access_type', 'read')
    requested_by = get_jwt_identity()
    
    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400
    
    allowed, reason = ConsentManager.check_consent_before_data_access(
        patient_id, access_type, requested_by
    )
    
    return jsonify({
        'allowed': allowed,
        'reason': reason,
        'patient_id': patient_id,
        'access_type': access_type
    }), 200
