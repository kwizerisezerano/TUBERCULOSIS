"""
Prescription Guard Module
Implements drug resistance flagging, antibiogram integration, and Dose Guard with ATC/DDD validation
"""
from models.models import db, Patient, Prescription, ATCDrug, AntibioticResistance, PharmacyInventory
from datetime import datetime

class PrescriptionGuard:
    """
    Validates prescriptions against:
    - Drug resistance patterns (antibiogram)
    - ATC/DDD standards
    - Pharmacy inventory
    """
    
    @staticmethod
    def check_drug_resistance(patient_id, atc_drug_id):
        """
        Check if the prescribed antibiotic has resistance issues for this patient
        Returns: (is_blocked, resistance_data, recommendations)
        """
        patient = Patient.query.get(patient_id)
        atc_drug = ATCDrug.query.get(atc_drug_id)
        
        if not patient or not atc_drug:
            return False, {}, []
        
        resistance_data = {
            'has_resistance': False,
            'resistance_level': 'none',
            'susceptibility': 'unknown',
            'resistance_records': []
        }
        
        # Check antibiotic resistance records for this patient
        resistance_records = AntibioticResistance.query.filter_by(
            patient_id=patient_id
        ).all()
        
        for record in resistance_records:
            # Check if this antibiotic is in the resistance pattern
            if atc_drug.drug_name.lower() in record.antibiotic_name.lower():
                resistance_data['has_resistance'] = True
                resistance_data['resistance_records'].append({
                    'antibiotic': record.antibiotic_name,
                    'organism': record.organism,
                    'resistance_pattern': record.resistance_pattern,
                    'susceptibility': record.susceptibility
                })
                
                if record.susceptibility == 'Resistant':
                    resistance_data['resistance_level'] = 'high'
                    resistance_data['susceptibility'] = 'resistant'
                elif record.susceptibility == 'Intermediate':
                    resistance_data['resistance_level'] = 'medium'
                    resistance_data['susceptibility'] = 'intermediate'
        
        # Check hospital antibiogram for this antibiotic
        # Get recent resistance data for the antibiotic class
        atc_class = atc_drug.atc_code[:5] if len(atc_drug.atc_code) >= 5 else atc_drug.atc_code
        
        recent_resistance = AntibioticResistance.query.filter(
            AntibioticResistance.antibiotic_name.like(f'%{atc_drug.drug_name}%')
        ).limit(50).all()
        
        if recent_resistance:
            resistant_count = sum(1 for r in recent_resistance if r.susceptibility == 'Resistant')
            resistance_rate = (resistant_count / len(recent_resistance)) * 100
            
            if resistance_rate > 30:
                resistance_data['resistance_level'] = 'high'
                resistance_data['hospital_resistance_rate'] = resistance_rate
            elif resistance_rate > 15:
                resistance_data['resistance_level'] = 'medium'
                resistance_data['hospital_resistance_rate'] = resistance_rate
        
        # Generate recommendations
        recommendations = []
        if resistance_data['has_resistance']:
            recommendations.append({
                'priority': 'high',
                'action': 'Consider alternative antibiotic',
                'reason': f'Patient has documented resistance to {atc_drug.drug_name}'
            })
        
        if resistance_data.get('hospital_resistance_rate', 0) > 30:
            recommendations.append({
                'priority': 'high',
                'action': 'Review hospital antibiogram',
                'reason': f'High hospital resistance rate ({resistance_data["hospital_resistance_rate"]:.1f}%) for this antibiotic'
            })
        
        # Block if high resistance
        is_blocked = resistance_data['resistance_level'] == 'high'
        
        return is_blocked, resistance_data, recommendations
    
    @staticmethod
    def validate_dose_guard(patient_id, atc_drug_id, dosage_mg, frequency, duration_days):
        """
        Validate prescription dosage against ATC/DDD standards
        Returns: (is_valid, validation_data, recommendations)
        """
        patient = Patient.query.get(patient_id)
        atc_drug = ATCDrug.query.get(atc_drug_id)
        
        if not patient or not atc_drug:
            return False, {}, []
        
        validation_data = {
            'is_valid': True,
            'ddd': atc_drug.ddd,
            'prescribed_mg_per_day': 0,
            'prescribed_ddds': 0,
            'within_standard_range': True,
            'warnings': []
        }
        
        # Calculate prescribed mg per day
        frequency_multiplier = {
            'once daily': 1,
            'twice daily': 2,
            'three times daily': 3,
            'four times daily': 4,
            '2 times daily': 2,
            '3 times daily': 3
        }.get(frequency.lower(), 1)
        
        prescribed_mg_per_day = dosage_mg * frequency_multiplier
        validation_data['prescribed_mg_per_day'] = prescribed_mg_per_day
        
        # Calculate DDDs
        if atc_drug.ddd and atc_drug.ddd > 0:
            prescribed_ddds = prescribed_mg_per_day / atc_drug.ddd
            validation_data['prescribed_ddds'] = prescribed_ddds
            
            # Check if within reasonable range (0.5x to 2x DDD)
            if prescribed_ddds < 0.5:
                validation_data['within_standard_range'] = False
                validation_data['warnings'].append('Dose below standard DDD range')
            elif prescribed_ddds > 2.0:
                validation_data['within_standard_range'] = False
                validation_data['warnings'].append('Dose above standard DDD range')
        
        # Age-based validation
        if patient.age:
            if patient.age < 15 and prescribed_ddds > 1.0:
                validation_data['within_standard_range'] = False
                validation_data['warnings'].append('High dose for pediatric patient')
            elif patient.age > 65 and prescribed_ddds > 1.5:
                validation_data['within_standard_range'] = False
                validation_data['warnings'].append('Consider dose adjustment for elderly patient')
        
        # Weight-based validation
        if patient.weight:
            mg_per_kg = dosage_mg / patient.weight if patient.weight > 0 else 0
            validation_data['mg_per_kg'] = mg_per_kg
            
            # General weight-based range (5-30 mg/kg depending on drug)
            if mg_per_kg > 30:
                validation_data['within_standard_range'] = False
                validation_data['warnings'].append('Dose exceeds recommended mg/kg range')
            elif mg_per_kg < 5:
                validation_data['within_standard_range'] = False
                validation_data['warnings'].append('Dose below recommended mg/kg range')
        
        recommendations = []
        if not validation_data['within_standard_range']:
            for warning in validation_data['warnings']:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Review dosage',
                    'reason': warning
                })
        
        validation_data['is_valid'] = validation_data['within_standard_range']
        
        return validation_data['is_valid'], validation_data, recommendations
    
    @staticmethod
    def check_inventory(hospital_id, atc_drug_id, quantity):
        """
        Check if pharmacy has sufficient inventory
        Returns: (is_available, inventory_data)
        """
        inventory = PharmacyInventory.query.filter_by(
            hospital_id=hospital_id,
            atc_drug_id=atc_drug_id
        ).first()
        
        inventory_data = {
            'available': False,
            'stock_quantity': 0,
            'required_quantity': quantity,
            'shortage': quantity
        }
        
        if inventory and inventory.stock_quantity >= quantity:
            inventory_data['available'] = True
            inventory_data['stock_quantity'] = inventory.stock_quantity
            inventory_data['shortage'] = 0
        elif inventory:
            inventory_data['stock_quantity'] = inventory.stock_quantity
            inventory_data['shortage'] = quantity - inventory.stock_quantity
        
        return inventory_data['available'], inventory_data
    
    @staticmethod
    def validate_prescription(patient_id, hospital_id, atc_drug_id, dosage_mg, frequency, duration_days, quantity):
        """
        Comprehensive prescription validation
        Returns: (is_valid, validation_results)
        """
        validation_results = {
            'resistance_check': {},
            'dose_validation': {},
            'inventory_check': {},
            'overall_valid': True,
            'block_reason': None,
            'recommendations': []
        }
        
        # Check drug resistance
        is_blocked, resistance_data, resistance_recs = PrescriptionGuard.check_drug_resistance(
            patient_id, atc_drug_id
        )
        validation_results['resistance_check'] = {
            'is_blocked': is_blocked,
            'data': resistance_data,
            'recommendations': resistance_recs
        }
        validation_results['recommendations'].extend(resistance_recs)
        
        if is_blocked:
            validation_results['overall_valid'] = False
            validation_results['block_reason'] = 'Drug resistance detected'
        
        # Validate dose
        is_dose_valid, dose_data, dose_recs = PrescriptionGuard.validate_dose_guard(
            patient_id, atc_drug_id, dosage_mg, frequency, duration_days
        )
        validation_results['dose_validation'] = {
            'is_valid': is_dose_valid,
            'data': dose_data,
            'recommendations': dose_recs
        }
        validation_results['recommendations'].extend(dose_recs)
        
        # Check inventory
        is_available, inventory_data = PrescriptionGuard.check_inventory(
            hospital_id, atc_drug_id, quantity
        )
        validation_results['inventory_check'] = {
            'is_available': is_available,
            'data': inventory_data
        }
        
        if not is_available:
            validation_results['recommendations'].append({
                'priority': 'high',
                'action': 'Check alternative medication or restock',
                'reason': f'Insufficient inventory. Required: {quantity}, Available: {inventory_data["stock_quantity"]}'
            })
        
        return validation_results['overall_valid'], validation_results
