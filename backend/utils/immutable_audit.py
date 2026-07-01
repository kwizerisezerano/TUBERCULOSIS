"""
Immutable Audit Logging System
Uses cryptographic hashing to ensure audit trail integrity
"""
import hashlib
import json
from datetime import datetime
from sqlalchemy import event
from models.models import AuditLog, db

class ImmutableAuditLogger:
    """
    Immutable audit logger that chains audit entries using cryptographic hashes
    to prevent tampering with the audit trail
    """
    
    @staticmethod
    def compute_hash(data, previous_hash=None):
        """
        Compute SHA-256 hash of audit data with optional previous hash for chaining
        """
        hash_input = json.dumps(data, sort_keys=True, default=str)
        if previous_hash:
            hash_input = f"{previous_hash}|{hash_input}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    @staticmethod
    def get_last_audit_hash():
        """Get the hash of the most recent audit entry"""
        last_audit = AuditLog.query.order_by(AuditLog.id.desc()).first()
        return last_audit.entry_hash if last_audit else None
    
    @staticmethod
    def create_immutable_audit(user_id, action, entity_type, entity_id, details, ip_address=None, commit=True):
        """
        Create an immutable audit log entry with cryptographic chaining
        """
        previous_hash = ImmutableAuditLogger.get_last_audit_hash()

        audit_data = {
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "ip_address": ip_address
        }

        entry_hash = ImmutableAuditLogger.compute_hash(audit_data, previous_hash)

        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            entry_hash=entry_hash,
            previous_hash=previous_hash,
            created_at=datetime.now()
        )

        db.session.add(audit)
        if commit:
            db.session.commit()

        return audit
    
    @staticmethod
    def verify_audit_integrity():
        """
        Verify the integrity of the entire audit trail by checking hash chain
        Returns (is_valid, broken_at_id, error_message)
        """
        audits = AuditLog.query.order_by(AuditLog.id.asc()).all()
        
        if not audits:
            return True, None, "No audit entries to verify"
        
        previous_hash = None
        
        for audit in audits:
            # Reconstruct the audit data
            audit_data = {
                "user_id": audit.user_id,
                "action": audit.action,
                "entity_type": audit.entity_type,
                "entity_id": audit.entity_id,
                "details": audit.details,
                "timestamp": audit.created_at.isoformat() if audit.created_at else None,
                "ip_address": audit.ip_address
            }
            
            # Compute expected hash
            expected_hash = ImmutableAuditLogger.compute_hash(audit_data, previous_hash)
            
            # Verify hash matches
            if audit.entry_hash != expected_hash:
                return False, audit.id, f"Hash mismatch at audit ID {audit.id}"
            
            # Verify previous hash chain
            if audit.previous_hash != previous_hash:
                return False, audit.id, f"Previous hash chain broken at audit ID {audit.id}"
            
            previous_hash = audit.entry_hash
        
        return True, None, "Audit trail integrity verified"
    
    @staticmethod
    def get_audit_chain(start_id=None, end_id=None):
        """
        Get a segment of the audit chain with hash verification status
        """
        query = AuditLog.query.order_by(AuditLog.id.asc())
        
        if start_id:
            query = query.filter(AuditLog.id >= start_id)
        if end_id:
            query = query.filter(AuditLog.id <= end_id)
        
        audits = query.all()
        
        chain = []
        for audit in audits:
            chain.append({
                "id": audit.id,
                "user_id": audit.user_id,
                "action": audit.action,
                "entity_type": audit.entity_type,
                "entity_id": audit.entity_id,
                "details": audit.details,
                "ip_address": audit.ip_address,
                "entry_hash": audit.entry_hash,
                "previous_hash": audit.previous_hash,
                "created_at": audit.created_at.isoformat() if audit.created_at else None
            })
        
        return chain

# Module-level variable to track pending audits
_pending_audits = []

# Register SQLAlchemy event listeners for automatic audit logging
def register_audit_listeners():
    """Register automatic audit logging for critical model changes"""

    @event.listens_for(db.session, 'before_flush')
    def before_flush(session, context, instances):
        """Track instances for audit logging"""
        global _pending_audits
        from models.models import Patient, Diagnosis, Prescription, LabTest, User

        for instance in session.new:
            if isinstance(instance, (Patient, Diagnosis, Prescription, LabTest, User)):
                _pending_audits.append({
                    'user_id': getattr(instance, 'created_by', None) or 1,
                    'action': 'create',
                    'entity_type': instance.__class__.__name__,
                    'entity_id': instance.id,
                    'details': f"Created {instance.__class__.__name__} record",
                    'ip_address': None
                })

        for instance in session.deleted:
            if isinstance(instance, (Patient, Diagnosis, Prescription, LabTest, User)):
                _pending_audits.append({
                    'user_id': getattr(instance, 'deleted_by', None) or 1,
                    'action': 'delete',
                    'entity_type': instance.__class__.__name__,
                    'entity_id': instance.id,
                    'details': f"Deleted {instance.__class__.__name__} record",
                    'ip_address': None
                })

        for instance in session.dirty:
            if isinstance(instance, (Patient, Diagnosis, Prescription, LabTest, User)):
                _pending_audits.append({
                    'user_id': getattr(instance, 'updated_by', None) or 1,
                    'action': 'update',
                    'entity_type': instance.__class__.__name__,
                    'entity_id': instance.id,
                    'details': f"Updated {instance.__class__.__name__} record",
                    'ip_address': None
                })

    @event.listens_for(db.session, 'after_commit')
    def after_commit(session):
        """Create audit logs after successful commit"""
        global _pending_audits
        for audit_data in _pending_audits:
            try:
                # Use a new session to avoid session state conflicts
                from sqlalchemy.orm import sessionmaker
                Session = sessionmaker(bind=db.engine)
                new_session = Session()

                try:
                    audit = AuditLog(
                        user_id=audit_data['user_id'],
                        action=audit_data['action'],
                        entity_type=audit_data['entity_type'],
                        entity_id=audit_data['entity_id'],
                        details=audit_data['details'],
                        ip_address=audit_data['ip_address'],
                        entry_hash='',  # Will be computed
                        previous_hash=ImmutableAuditLogger.get_last_audit_hash(),
                        created_at=datetime.now()
                    )

                    # Compute hash with previous hash
                    previous_hash = ImmutableAuditLogger.get_last_audit_hash()
                    audit_data_for_hash = {
                        "user_id": audit_data['user_id'],
                        "action": audit_data['action'],
                        "entity_type": audit_data['entity_type'],
                        "entity_id": audit_data['entity_id'],
                        "details": audit_data['details'],
                        "timestamp": datetime.now().isoformat(),
                        "ip_address": audit_data['ip_address']
                    }
                    audit.entry_hash = ImmutableAuditLogger.compute_hash(audit_data_for_hash, previous_hash)
                    audit.previous_hash = previous_hash

                    new_session.add(audit)
                    new_session.commit()
                finally:
                    new_session.close()
            except Exception as e:
                print(f"Error creating audit log: {e}")
        _pending_audits = []

    @event.listens_for(db.session, 'after_rollback')
    def after_rollback(session):
        """Clear pending audits on rollback"""
        global _pending_audits
        _pending_audits = []

# Initialize audit listeners
register_audit_listeners()
