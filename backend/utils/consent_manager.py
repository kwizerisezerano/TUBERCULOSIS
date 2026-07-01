"""
Patient Consent and Verification System

Implements GDPR-compliant consent management:
- Explicit consent for data sharing
- Consent verification workflow
- Immutable audit logging
- Consent expiration tracking
- Role-based consent access
"""
from datetime import datetime, timedelta
import hashlib
import json


class ConsentManager:
    """Manages patient consent lifecycle"""
    
    CONSENT_TYPES = {
        'data_sharing': 'Consent to share health data with healthcare providers',
        'research': 'Consent to use anonymized data for research',
        'treatment': 'Consent for medical treatment',
        'genexpert': 'Consent for GeneXpert molecular testing'
    }
    
    CONSENT_STATUSES = ['pending', 'granted', 'denied', 'expired', 'revoked']
    
    @staticmethod
    def create_consent_request(patient_id, consent_type='data_sharing', requested_by=None):
        """
        Create a new consent request for a patient
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent requested
            requested_by: User ID requesting consent (optional)
            
        Returns:
            Dictionary with consent request details
        """
        from app import app, db
        from models.models import Patient, AuditLog
        
        with app.app_context():
            patient = Patient.query.filter_by(_patient_id=patient_id).first()
            if not patient:
                return {'error': 'Patient not found'}, 404
            
            # Generate consent request token
            consent_token = ConsentManager._generate_consent_token(patient_id, consent_type)
            
            # Log consent request
            audit = AuditLog(
                user_id=requested_by or 1,  # System user if not specified
                action='consent_request_created',
                entity_type='patient_consent',
                entity_id=patient.id,
                details=f"Consent request created for {consent_type}",
                created_at=datetime.now()
            )
            audit.compute_hash()
            db.session.add(audit)
            db.session.commit()
            
            return {
                'patient_id': patient_id,
                'consent_type': consent_type,
                'consent_description': ConsentManager.CONSENT_TYPES.get(consent_type),
                'consent_token': consent_token,
                'status': 'pending',
                'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
                'created_at': datetime.now().isoformat()
            }
    
    @staticmethod
    def grant_consent(patient_id, consent_type='data_sharing', granted_by=None, verification_method='signature'):
        """
        Grant consent for a patient
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent being granted
            granted_by: User ID granting consent
            verification_method: Method of verification (signature, biometric, digital)
            
        Returns:
            Dictionary with consent grant details
        """
        from app import app, db
        from models.models import Patient, AuditLog
        
        with app.app_context():
            patient = Patient.query.filter_by(_patient_id=patient_id).first()
            if not patient:
                return {'error': 'Patient not found'}, 404
            
            # Update patient consent status
            patient.data_sharing_consent = 'granted'
            patient.consent_granted_at = datetime.now()
            patient.consent_expires_at = datetime.now() + timedelta(days=365)  # 1 year validity
            
            # Log consent grant with verification details
            audit = AuditLog(
                user_id=granted_by or patient.id,
                action='consent_granted',
                entity_type='patient_consent',
                entity_id=patient.id,
                details=json.dumps({
                    'consent_type': consent_type,
                    'verification_method': verification_method,
                    'granted_at': datetime.now().isoformat(),
                    'expires_at': patient.consent_expires_at.isoformat()
                }),
                created_at=datetime.now()
            )
            audit.compute_hash()
            db.session.add(audit)
            db.session.commit()
            
            return {
                'patient_id': patient_id,
                'consent_type': consent_type,
                'status': 'granted',
                'granted_at': patient.consent_granted_at.isoformat(),
                'expires_at': patient.consent_expires_at.isoformat(),
                'verification_method': verification_method
            }
    
    @staticmethod
    def revoke_consent(patient_id, revoked_by=None, reason='Patient request'):
        """
        Revoke previously granted consent
        
        Args:
            patient_id: Patient identifier
            revoked_by: User ID revoking consent
            reason: Reason for revocation
            
        Returns:
            Dictionary with revocation details
        """
        from app import app, db
        from models.models import Patient, AuditLog
        
        with app.app_context():
            patient = Patient.query.filter_by(_patient_id=patient_id).first()
            if not patient:
                return {'error': 'Patient not found'}, 404
            
            if patient.data_sharing_consent != 'granted':
                return {'error': 'No active consent to revoke'}, 400
            
            # Update patient consent status
            previous_status = patient.data_sharing_consent
            patient.data_sharing_consent = 'revoked'
            
            # Log consent revocation
            audit = AuditLog(
                user_id=revoked_by or patient.id,
                action='consent_revoked',
                entity_type='patient_consent',
                entity_id=patient.id,
                details=json.dumps({
                    'previous_status': previous_status,
                    'reason': reason,
                    'revoked_at': datetime.now().isoformat()
                }),
                created_at=datetime.now()
            )
            audit.compute_hash()
            db.session.add(audit)
            db.session.commit()
            
            return {
                'patient_id': patient_id,
                'status': 'revoked',
                'revoked_at': datetime.now().isoformat(),
                'reason': reason
            }
    
    @staticmethod
    def verify_consent(patient_id, consent_type='data_sharing'):
        """
        Verify if patient has valid consent
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent to verify
            
        Returns:
            Dictionary with consent verification result
        """
        from app import app, db
        from models.models import Patient, AuditLog
        
        with app.app_context():
            patient = Patient.query.filter_by(_patient_id=patient_id).first()
            if not patient:
                return {'error': 'Patient not found'}, 404
            
            # Check consent status
            status = patient.data_sharing_consent or 'pending'
            
            # Check if consent has expired
            is_expired = False
            if patient.consent_expires_at and patient.consent_expires_at < datetime.now():
                is_expired = True
                status = 'expired'
                # Auto-update status
                patient.data_sharing_consent = 'expired'
                db.session.commit()
            
            # Log consent verification
            audit = AuditLog(
                user_id=1,  # System user
                action='consent_verified',
                entity_type='patient_consent',
                entity_id=patient.id,
                details=json.dumps({
                    'consent_type': consent_type,
                    'status': status,
                    'is_expired': is_expired,
                    'verified_at': datetime.now().isoformat()
                }),
                created_at=datetime.now()
            )
            audit.compute_hash()
            db.session.add(audit)
            db.session.commit()
            
            return {
                'patient_id': patient_id,
                'consent_type': consent_type,
                'status': status,
                'is_valid': status == 'granted' and not is_expired,
                'granted_at': patient.consent_granted_at.isoformat() if patient.consent_granted_at else None,
                'expires_at': patient.consent_expires_at.isoformat() if patient.consent_expires_at else None,
                'verified_at': datetime.now().isoformat()
            }
    
    @staticmethod
    def get_consent_history(patient_id):
        """
        Get complete consent history for a patient
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            List of consent-related audit log entries
        """
        from app import app, db
        from models.models import Patient, AuditLog
        
        with app.app_context():
            patient = Patient.query.filter_by(_patient_id=patient_id).first()
            if not patient:
                return {'error': 'Patient not found'}, 404
            
            # Query audit logs for consent-related actions
            consent_actions = ['consent_request_created', 'consent_granted', 'consent_revoked', 'consent_verified']
            audit_logs = AuditLog.query.filter(
                AuditLog.entity_id == patient.id,
                AuditLog.entity_type == 'patient_consent',
                AuditLog.action.in_(consent_actions)
            ).order_by(AuditLog.created_at.desc()).all()
            
            history = []
            for log in audit_logs:
                try:
                    details = json.loads(log.details) if log.details else {}
                except:
                    details = {}
                
                history.append({
                    'action': log.action,
                    'details': details,
                    'created_at': log.created_at.isoformat(),
                    'user_id': log.user_id,
                    'entry_hash': log.entry_hash
                })
            
            return {
                'patient_id': patient_id,
                'current_status': patient.data_sharing_consent,
                'history': history
            }
    
    @staticmethod
    def _generate_consent_token(patient_id, consent_type):
        """Generate unique consent request token"""
        data = f"{patient_id}:{consent_type}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    @staticmethod
    def check_consent_before_data_access(patient_id, access_type='read', requested_by=None):
        """
        Check consent before allowing data access
        
        Args:
            patient_id: Patient identifier
            access_type: Type of access (read, write, share)
            requested_by: User requesting access
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        from app import app, db
        from models.models import Patient, AuditLog
        
        verification = ConsentManager.verify_consent(patient_id)
        
        if not verification.get('is_valid'):
            if verification.get('status') == 'pending':
                return False, "Patient consent is pending approval"
            elif verification.get('status') == 'denied':
                return False, "Patient has denied consent"
            elif verification.get('status') == 'revoked':
                return False, "Patient has revoked consent"
            elif verification.get('status') == 'expired':
                return False, "Patient consent has expired"
            else:
                return False, "No valid consent found"
        
        # Additional checks for write/share access
        if access_type in ['write', 'share']:
            # Require explicit consent for data modification or sharing
            if verification.get('status') != 'granted':
                return False, "Explicit consent required for data modification/sharing"
        
        # Log access attempt
        with app.app_context():
            patient = Patient.query.filter_by(_patient_id=patient_id).first()
            audit = AuditLog(
                user_id=requested_by or 1,
                action='data_access_attempt',
                entity_type='patient',
                entity_id=patient.id if patient else None,
                details=json.dumps({
                    'access_type': access_type,
                    'consent_status': verification.get('status'),
                    'allowed': True
                }),
                created_at=datetime.now()
            )
            audit.compute_hash()
            db.session.add(audit)
            db.session.commit()
        
        return True, "Access granted based on valid consent"
