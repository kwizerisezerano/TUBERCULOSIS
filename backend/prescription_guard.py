"""
Prescription Guard Module
Validates prescriptions against resistance patterns, DDD standards, and inventory.
"""
from models.models import db, Patient, ATCDrug, AntibioticResistance, PharmacyInventory

# Map ATC drug name fragments to AntibioticResistance columns
DRUG_COLUMN_MAP = {
    'amoxicillin': 'amx_amp',
    'ampicillin':  'amx_amp',
    'amoxicillin-clavulanate': 'amc',
    'clavulanate': 'amc',
    'cefazolin':   'cz',
    'cefoxitin':   'fox',
    'cefotaxime':  'ctx_cro',
    'ceftriaxone': 'ctx_cro',
    'imipenem':    'ipm',
    'gentamicin':  'gen',
    'amikacin':    'an',
    'nalidixic':   'nalidixic_acid',
    'ofloxacin':   'ofx',
    'ciprofloxacin': 'cip',
    'chloramphenicol': 'chloramphenicol',
    'trimethoprim': 'co_trimoxazole',
    'co-trimoxazole': 'co_trimoxazole',
    'nitrofurantoin': 'furanes',
    'colistin':    'colistine',
}


def _get_resistance_column(drug_name):
    """Return the AntibioticResistance column name for a drug, or None."""
    name_lower = (drug_name or '').lower()
    for fragment, col in DRUG_COLUMN_MAP.items():
        if fragment in name_lower:
            return col
    return None


class PrescriptionGuard:

    @staticmethod
    def check_drug_resistance(patient_id, atc_drug_id):
        patient = Patient.query.get(patient_id)
        atc_drug = ATCDrug.query.get(atc_drug_id)

        if not patient or not atc_drug:
            return False, {'has_resistance': False, 'resistance_level': 'none'}, []

        col = _get_resistance_column(atc_drug.drug_name)
        resistance_data = {
            'has_resistance': False,
            'resistance_level': 'none',
            'susceptibility': 'unknown',
        }

        if col:
            records = AntibioticResistance.query.filter_by(patient_id=patient_id).all()
            resistant = [r for r in records if getattr(r, col, None) == 'R']
            intermediate = [r for r in records if getattr(r, col, None) == 'I']

            if resistant:
                resistance_data['has_resistance'] = True
                resistance_data['resistance_level'] = 'high'
                resistance_data['susceptibility'] = 'resistant'
            elif intermediate:
                resistance_data['has_resistance'] = True
                resistance_data['resistance_level'] = 'medium'
                resistance_data['susceptibility'] = 'intermediate'

            # Hospital-wide resistance rate
            all_records = AntibioticResistance.query.limit(100).all()
            if all_records:
                r_count = sum(1 for r in all_records if getattr(r, col, None) == 'R')
                rate = (r_count / len(all_records)) * 100
                if rate > 30:
                    resistance_data['hospital_resistance_rate'] = round(rate, 1)
                    if resistance_data['resistance_level'] == 'none':
                        resistance_data['resistance_level'] = 'high'

        recommendations = []
        if resistance_data['resistance_level'] == 'high':
            recommendations.append({
                'priority': 'high',
                'action': 'Consider alternative antibiotic',
                'reason': f'Resistance detected for {atc_drug.drug_name}'
            })

        is_blocked = resistance_data['resistance_level'] == 'high' and resistance_data['has_resistance']
        return is_blocked, resistance_data, recommendations

    @staticmethod
    def validate_dose_guard(patient_id, atc_drug_id, dosage_mg, frequency, duration_days):
        patient = Patient.query.get(patient_id)
        atc_drug = ATCDrug.query.get(atc_drug_id)

        if not patient or not atc_drug:
            return True, {'is_valid': True, 'warnings': []}, []

        freq_str = (frequency or 'daily').lower()
        freq_map = {
            'once daily': 1, 'daily': 1, '1 time daily': 1,
            'twice daily': 2, '2 times daily': 2,
            'three times daily': 3, '3 times daily': 3,
            'four times daily': 4, '4 times daily': 4,
        }
        multiplier = freq_map.get(freq_str, 1)
        dosage_mg = dosage_mg or 0
        mg_per_day = dosage_mg * multiplier

        validation_data = {
            'is_valid': True,
            'ddd': atc_drug.ddd,
            'prescribed_mg_per_day': mg_per_day,
            'prescribed_ddds': 0,
            'within_standard_range': True,
            'warnings': []
        }

        if atc_drug.ddd and atc_drug.ddd > 0:
            # DDD is stored in grams, convert to mg
            ddd_mg = atc_drug.ddd * 1000
            ddds = mg_per_day / ddd_mg
            validation_data['prescribed_ddds'] = round(ddds, 2)
            if ddds < 0.3:
                validation_data['warnings'].append('Dose may be below therapeutic range')
            elif ddds > 3.0:
                validation_data['warnings'].append('Dose above standard DDD range')

        recommendations = [
            {'priority': 'medium', 'action': 'Review dosage', 'reason': w}
            for w in validation_data['warnings']
        ]
        validation_data['is_valid'] = len(validation_data['warnings']) == 0
        return validation_data['is_valid'], validation_data, recommendations

    @staticmethod
    def check_inventory(hospital_id, atc_drug_id, quantity):
        inventory = PharmacyInventory.query.filter_by(
            hospital_id=hospital_id,
            atc_drug_id=atc_drug_id
        ).first()

        qty = quantity or 1
        if inventory and inventory.stock_quantity >= qty:
            return True, {
                'available': True,
                'stock_quantity': inventory.stock_quantity,
                'required_quantity': qty,
                'shortage': 0
            }
        return False, {
            'available': False,
            'stock_quantity': inventory.stock_quantity if inventory else 0,
            'required_quantity': qty,
            'shortage': qty - (inventory.stock_quantity if inventory else 0)
        }

    @staticmethod
    def validate_prescription(patient_id, hospital_id, atc_drug_id, dosage_mg, frequency, duration_days, quantity):
        results = {
            'resistance_check': {},
            'dose_validation': {},
            'inventory_check': {},
            'overall_valid': True,
            'block_reason': None,
            'recommendations': []
        }

        is_blocked, res_data, res_recs = PrescriptionGuard.check_drug_resistance(patient_id, atc_drug_id)
        results['resistance_check'] = {'is_blocked': is_blocked, 'data': res_data, 'recommendations': res_recs}
        results['recommendations'].extend(res_recs)
        if is_blocked:
            results['overall_valid'] = False
            results['block_reason'] = 'Drug resistance detected'

        is_dose_valid, dose_data, dose_recs = PrescriptionGuard.validate_dose_guard(
            patient_id, atc_drug_id, dosage_mg, frequency, duration_days)
        results['dose_validation'] = {'is_valid': is_dose_valid, 'data': dose_data, 'recommendations': dose_recs}
        results['recommendations'].extend(dose_recs)

        is_available, inv_data = PrescriptionGuard.check_inventory(hospital_id, atc_drug_id, quantity)
        results['inventory_check'] = {'is_available': is_available, 'data': inv_data}
        if not is_available:
            results['recommendations'].append({
                'priority': 'high',
                'action': 'Restock or use alternative',
                'reason': f'Insufficient inventory. Required: {quantity}, Available: {inv_data["stock_quantity"]}'
            })

        return results['overall_valid'], results
