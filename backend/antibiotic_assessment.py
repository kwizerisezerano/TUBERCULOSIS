"""
Antibiotic Usage Assessment Module
Analyzes patient antibiotic history to detect misuse, overuse, and resistance risks
"""
from datetime import datetime, timedelta
from models.models import db, Patient, Prescription, AntibioticResistance

class AntibioticUsageAssessment:
    """
    Analyzes antibiotic usage patterns to identify:
    - Antibiotic misuse
    - Overuse
    - Incomplete treatment
    - Self-medication behavior
    """
    
    @staticmethod
    def assess_antibiotic_usage(patient_id, assessment_data):
        """
        Assess antibiotic usage based on patient responses
        
        assessment_data should include:
        - used_antibiotics_before: boolean
        - which_antibiotics: list of antibiotic names
        - duration_days: number of days taken
        - completed_treatment: boolean
        - stopped_early: boolean
        - self_medicated: boolean
        """
        risk_factors = {
            'antibiotic_misuse': False,
            'overuse': False,
            'incomplete_treatment': False,
            'self_medication': False,
            'resistance_risk': 'low',
            'recommendations': []
        }
        
        # Check for antibiotic misuse
        if assessment_data.get('self_medicated', False):
            risk_factors['self_medication'] = True
            risk_factors['antibiotic_misuse'] = True
            risk_factors['resistance_risk'] = 'high'
            risk_factors['recommendations'].append(
                "Patient has history of self-medication. Increased risk of antimicrobial resistance."
            )
        
        # Check for incomplete treatment
        if assessment_data.get('stopped_early', False):
            risk_factors['incomplete_treatment'] = True
            risk_factors['antibiotic_misuse'] = True
            risk_factors['resistance_risk'] = 'high'
            risk_factors['recommendations'].append(
                "Patient has history of incomplete antibiotic treatment. Increased risk of resistance development."
            )
        
        # Check for overuse (multiple antibiotics without proper indication)
        antibiotics_used = assessment_data.get('which_antibiotics', [])
        if len(antibiotics_used) > 2:
            risk_factors['overuse'] = True
            risk_factors['resistance_risk'] = 'high'
            risk_factors['recommendations'].append(
                "Patient has used multiple antibiotics. Consider antimicrobial stewardship review."
            )
        
        # Check duration (too short or too long)
        duration = assessment_data.get('duration_days', 0)
        if duration > 0 and duration < 5:
            risk_factors['incomplete_treatment'] = True
            risk_factors['recommendations'].append(
                "Short antibiotic duration may indicate incomplete treatment."
            )
        elif duration > 21:
            risk_factors['overuse'] = True
            risk_factors['recommendations'].append(
                "Prolonged antibiotic use may indicate overuse. Review indication."
            )
        
        # Check historical prescription data if available
        patient = Patient.query.get(patient_id)
        if patient:
            # Get recent antibiotic prescriptions (last 6 months)
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_prescriptions = Prescription.query.filter(
                Prescription.patient_id == patient_id,
                Prescription.created_at >= six_months_ago
            ).all()
            
            if len(recent_prescriptions) > 3:
                risk_factors['overuse'] = True
                risk_factors['resistance_risk'] = 'high'
                risk_factors['recommendations'].append(
                    f"Patient has {len(recent_prescriptions)} antibiotic prescriptions in the last 6 months. Review for stewardship compliance."
                )
            
            # Check for repeated antibiotics (potential resistance)
            antibiotic_counts = {}
            for presc in recent_prescriptions:
                med = presc.medication
                if med:
                    antibiotic_counts[med] = antibiotic_counts.get(med, 0) + 1
            
            for antibiotic, count in antibiotic_counts.items():
                if count >= 2:
                    risk_factors['resistance_risk'] = 'high'
                    risk_factors['recommendations'].append(
                        f"Patient has received {antibiotic} {count} times recently. Consider resistance testing."
                    )
        
        # Update risk score based on assessment
        risk_score = 0
        if risk_factors['self_medication']:
            risk_score += 30
        if risk_factors['incomplete_treatment']:
            risk_score += 25
        if risk_factors['overuse']:
            risk_score += 20
        if risk_factors['resistance_risk'] == 'high':
            risk_score += 25
        
        risk_factors['risk_score'] = min(risk_score, 100)
        
        return risk_factors
    
    @staticmethod
    def get_antibiotic_recommendations(risk_factors):
        """
        Generate treatment recommendations based on antibiotic usage assessment
        """
        recommendations = []
        
        if risk_factors['resistance_risk'] == 'high':
            recommendations.append({
                'priority': 'high',
                'action': 'Order Drug Susceptibility Testing (DST)',
                'reason': 'High resistance risk detected from antibiotic history'
            })
            recommendations.append({
                'priority': 'high',
                'action': 'Consider alternative first-line antibiotics',
                'reason': 'Potential resistance to commonly used antibiotics'
            })
        
        if risk_factors['incomplete_treatment']:
            recommendations.append({
                'priority': 'medium',
                'action': 'Provide patient education on treatment adherence',
                'reason': 'History of incomplete antibiotic treatment'
            })
        
        if risk_factors['self_medication']:
            recommendations.append({
                'priority': 'high',
                'action': 'Counsel patient on dangers of self-medication',
                'reason': 'Self-medication contributes to antimicrobial resistance'
            })
        
        if risk_factors['overuse']:
            recommendations.append({
                'priority': 'medium',
                'action': 'Review antibiotic indication and duration',
                'reason': 'Potential antibiotic overuse detected'
            })
        
        return recommendations
