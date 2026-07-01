"""
Enhanced Real-Time Alert System
Handles critical clinical events: MDR-TB, treatment failure, antibiotic misuse, lab results, stock alerts
"""
from datetime import datetime, timedelta
from models.models import db, Patient, Alert, User, LabTest, Prescription, PharmacyInventory, AntibioticResistance
from app import mail
from flask_mail import Message
import os

class AlertSystem:
    """
    Comprehensive alert system for critical clinical events
    """
    
    @staticmethod
    def trigger_mdr_tb_alert(patient_id):
        """Alert when MDR-TB or XDR-TB is suspected"""
        patient = Patient.query.get(patient_id)
        if not patient:
            return
        
        # Get patient's primary hospital
        hospital_id = None
        if patient.hospitals:
            hospital_id = patient.hospitals[0].id
        
        # Check if recent MDR-TB alert exists
        recent_alert = Alert.query.filter(
            Alert.patient_id == patient_id,
            Alert.alert_type == 'mdr_tb_suspected',
            Alert.severity == 'critical',
            Alert.is_read == False,
            Alert.created_at >= datetime.now() - timedelta(hours=24)
        ).first()
        
        if recent_alert:
            return
        
        # Create alert
        alert = Alert(
            patient_id=patient_id,
            hospital_id=hospital_id,
            alert_type='mdr_tb_suspected',
            message=f"MDR-TB Suspected: Patient {patient.patient_id} shows signs of multidrug-resistant TB. Immediate DST and treatment review required.",
            severity='critical',
            is_read=False
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Send email notifications
        AlertSystem._send_alert_email(
            patient,
            'MDR-TB Suspected Alert',
            f"Patient {patient.patient_id} shows signs of multidrug-resistant TB. Immediate DST and treatment review required.",
            'critical'
        )
    
    @staticmethod
    def trigger_treatment_failure_alert(patient_id, failure_probability):
        """Alert when treatment failure risk exceeds threshold"""
        if failure_probability < 80:
            return
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return
        
        # Get patient's primary hospital
        hospital_id = None
        if patient.hospitals:
            hospital_id = patient.hospitals[0].id
        
        # Check if recent alert exists
        recent_alert = Alert.query.filter(
            Alert.patient_id == patient_id,
            Alert.alert_type == 'treatment_failure_risk',
            Alert.severity == 'critical',
            Alert.is_read == False,
            Alert.created_at >= datetime.now() - timedelta(hours=24)
        ).first()
        
        if recent_alert:
            return
        
        # Create alert
        alert = Alert(
            patient_id=patient_id,
            hospital_id=hospital_id,
            alert_type='treatment_failure_risk',
            message=f"Treatment Failure Risk Alert: Patient {patient.patient_id} has {failure_probability:.1f}% probability of treatment failure. Consider regimen adjustment.",
            severity='critical',
            is_read=False
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Send email notifications
        AlertSystem._send_alert_email(
            patient,
            f'Treatment Failure Risk Alert - {failure_probability:.1f}%',
            f"Patient {patient.patient_id} has {failure_probability:.1f}% probability of treatment failure. Consider regimen adjustment.",
            'critical'
        )
    
    @staticmethod
    def trigger_antibiotic_misuse_alert(patient_id, misuse_type, details):
        """Alert when antibiotic misuse is detected"""
        patient = Patient.query.get(patient_id)
        if not patient:
            return
        
        # Get patient's primary hospital
        hospital_id = None
        if patient.hospitals:
            hospital_id = patient.hospitals[0].id
        
        # Check if recent alert exists
        recent_alert = Alert.query.filter(
            Alert.patient_id == patient_id,
            Alert.alert_type == 'antibiotic_misuse',
            Alert.severity == 'high',
            Alert.is_read == False,
            Alert.created_at >= datetime.now() - timedelta(hours=48)
        ).first()
        
        if recent_alert:
            return
        
        # Create alert
        alert = Alert(
            patient_id=patient_id,
            hospital_id=hospital_id,
            alert_type='antibiotic_misuse',
            message=f"Antibiotic Misuse Detected: {misuse_type} for patient {patient.patient_id}. {details}",
            severity='high',
            is_read=False
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Send email notifications
        AlertSystem._send_alert_email(
            patient,
            'Antibiotic Misuse Alert',
            f"{misuse_type} detected for patient {patient.patient_id}. {details}",
            'high'
        )
    
    @staticmethod
    def trigger_critical_lab_result_alert(lab_test_id):
        """Alert when critical laboratory results are available"""
        lab_test = LabTest.query.get(lab_test_id)
        if not lab_test:
            return
        
        patient = Patient.query.get(lab_test.patient_id)
        if not patient:
            return
        
        # Check if recent alert exists
        recent_alert = Alert.query.filter(
            Alert.patient_id == lab_test.patient_id,
            Alert.alert_type == 'critical_lab_result',
            Alert.severity == 'critical',
            Alert.is_read == False,
            Alert.created_at >= datetime.now() - timedelta(hours=24)
        ).first()
        
        if recent_alert:
            return
        
        # Create alert
        alert = Alert(
            patient_id=lab_test.patient_id,
            hospital_id=lab_test.hospital_id,
            alert_type='critical_lab_result',
            message=f"Critical Lab Result Available: {lab_test.test_type} for patient {patient.patient_id}. Results: {lab_test.results}",
            severity='critical',
            is_read=False
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Send email notifications
        AlertSystem._send_alert_email(
            patient,
            f'Critical Lab Result - {lab_test.test_type}',
            f"{lab_test.test_type} results are available for patient {patient.patient_id}. Results: {lab_test.results}",
            'critical'
        )
    
    @staticmethod
    def trigger_stock_alert(hospital_id, atc_drug_id, current_stock, threshold):
        """Alert when medication stock is below threshold"""
        inventory = PharmacyInventory.query.filter_by(
            hospital_id=hospital_id,
            atc_drug_id=atc_drug_id
        ).first()
        
        if not inventory:
            return
        
        # Check if recent alert exists
        recent_alert = Alert.query.filter(
            Alert.alert_type == 'low_stock',
            Alert.severity == 'high',
            Alert.is_read == False,
            Alert.created_at >= datetime.now() - timedelta(hours=24)
        ).filter(
            Alert.message.like(f'%{inventory.atc_drug.drug_name}%')
        ).first()
        
        if recent_alert:
            return
        
        # Create alert (no patient_id for system-wide alerts)
        alert = Alert(
            patient_id=None,
            alert_type='low_stock',
            message=f"Low Stock Alert: {inventory.atc_drug.drug_name} at {inventory.hospital.name}. Current: {current_stock}, Threshold: {threshold}",
            severity='high',
            is_read=False,
            hospital_id=hospital_id
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Send email to pharmacists and admins
        AlertSystem._send_stock_alert_email(inventory, current_stock, threshold)
    
    @staticmethod
    def _send_alert_email(patient, subject, message, severity):
        """Send email alert to relevant staff"""
        # Get doctors and admins
        recipients = User.query.filter(User.role.in_(['doctor', 'admin', 'hospital_admin'])).all()
        
        for recipient in recipients:
            if recipient.email:
                try:
                    msg = Message(
                        f"[{severity.upper()}] {subject} - Patient {patient.patient_id}",
                        recipients=[recipient.email],
                        sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@tbdiagnostic.com')
                    )
                    msg.body = f"""
{severity.upper()} ALERT

Patient ID: {patient.patient_id}
Severity: {severity.upper()}

Message: {message}

Please log in to the TB Diagnostic System for more details.

---
This is an automated alert from the TB Predictive EHR Analytics Dashboard.
                    """
                    mail.send(msg)
                    print(f"Email sent to {recipient.email} for {severity} alert")
                except Exception as e:
                    print(f"Failed to send email to {recipient.email}: {e}")
    
    @staticmethod
    def _send_stock_alert_email(inventory, current_stock, threshold):
        """Send stock alert email to pharmacists"""
        recipients = User.query.filter(
            User.role.in_(['pharmacist', 'admin', 'hospital_admin']),
            User.hospital_id == inventory.hospital_id
        ).all()
        
        for recipient in recipients:
            if recipient.email:
                try:
                    msg = Message(
                        f"Low Stock Alert - {inventory.atc_drug.drug_name}",
                        recipients=[recipient.email],
                        sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@tbdiagnostic.com')
                    )
                    msg.body = f"""
LOW STOCK ALERT

Hospital: {inventory.hospital.name}
Medication: {inventory.atc_drug.drug_name}
Current Stock: {current_stock}
Threshold: {threshold}

Please restock immediately.

---
This is an automated alert from the TB Predictive EHR Analytics Dashboard.
                    """
                    mail.send(msg)
                    print(f"Stock alert email sent to {recipient.email}")
                except Exception as e:
                    print(f"Failed to send stock alert to {recipient.email}: {e}")
    
    @staticmethod
    def check_and_trigger_stock_alerts():
        """Check all inventory and trigger alerts for low stock"""
        inventories = PharmacyInventory.query.all()
        
        for inventory in inventories:
            # Define threshold (e.g., 10 units)
            threshold = 10
            
            if inventory.stock_quantity <= threshold:
                AlertSystem.trigger_stock_alert(
                    inventory.hospital_id,
                    inventory.atc_drug_id,
                    inventory.stock_quantity,
                    threshold
                )
