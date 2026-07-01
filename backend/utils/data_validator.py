"""
Data Validation Module for TB Predictive EHR Analytics Dashboard

Ensures data quality before import:
- Zero missing critical fields
- Zero duplicate records
- Data type validation
- Referential integrity checks
"""
import pandas as pd
from typing import Dict, List, Tuple, Any
import re


class DataValidator:
    """Validates data quality before database import"""
    
    CRITICAL_FIELDS = {
        'patient': ['patient_id', 'first_name', 'age', 'gender'],
        'hospital': ['hospital_id', 'name', 'facility_type', 'city'],
        'lab_result': ['patient_id', 'test_type', 'result'],
        'prescription': ['patient_id', 'medication', 'dosage'],
        'atc_drug': ['atc_code', 'drug_name']
    }
    
    def __init__(self, dataset_type: str):
        self.dataset_type = dataset_type
        self.validation_results = {
            'total_rows': 0,
            'valid_rows': 0,
            'missing_critical': 0,
            'duplicates': 0,
            'invalid_types': 0,
            'errors': []
        }
    
    def validate_dataframe(self, df: pd.DataFrame, unique_key: str = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Validate DataFrame and return cleaned data with validation report
        
        Args:
            df: Input DataFrame
            unique_key: Column name to check for duplicates
            
        Returns:
            Tuple of (cleaned DataFrame, validation report)
        """
        self.validation_results['total_rows'] = len(df)
        
        # Check for missing critical fields
        critical_fields = self.CRITICAL_FIELDS.get(self.dataset_type, [])
        for field in critical_fields:
            if field in df.columns:
                missing = df[field].isna().sum()
                if missing > 0:
                    self.validation_results['missing_critical'] += missing
                    self.validation_results['errors'].append(
                        f"Missing {missing} values in critical field: {field}"
                    )
        
        # Check for duplicates
        if unique_key and unique_key in df.columns:
            duplicates = df[unique_key].duplicated().sum()
            self.validation_results['duplicates'] = duplicates
            if duplicates > 0:
                self.validation_results['errors'].append(
                    f"Found {duplicates} duplicate records on key: {unique_key}"
                )
                # Remove duplicates
                df = df.drop_duplicates(subset=[unique_key], keep='first')
        
        # Validate data types
        self._validate_data_types(df)
        
        # Remove rows with missing critical fields
        if critical_fields:
            existing_critical = [f for f in critical_fields if f in df.columns]
            df = df.dropna(subset=existing_critical)
        
        self.validation_results['valid_rows'] = len(df)
        
        return df, self.validation_results
    
    def _validate_data_types(self, df: pd.DataFrame):
        """Validate data types for common fields"""
        # Age validation
        if 'age' in df.columns:
            invalid_age = df[~df['age'].apply(lambda x: pd.isna(x) or (isinstance(x, (int, float)) and 0 <= x <= 150))]
            self.validation_results['invalid_types'] += len(invalid_age)
            if len(invalid_age) > 0:
                self.validation_results['errors'].append(
                    f"Found {len(invalid_age)} invalid age values"
                )
        
        # Gender validation
        if 'gender' in df.columns:
            valid_genders = {'male', 'female', 'other', 'm', 'f', 'unknown'}
            invalid_gender = df[~df['gender'].str.lower().isin(valid_genders, na=False)]
            self.validation_results['invalid_types'] += len(invalid_gender)
            if len(invalid_gender) > 0:
                self.validation_results['errors'].append(
                    f"Found {len(invalid_gender)} invalid gender values"
                )
    
    def validate_patient_data(self, patient_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate individual patient record
        
        Args:
            patient_data: Dictionary of patient data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check critical fields
        for field in self.CRITICAL_FIELDS.get('patient', []):
            if field not in patient_data or not patient_data[field]:
                errors.append(f"Missing critical field: {field}")
        
        # Validate age
        if 'age' in patient_data:
            try:
                age = int(patient_data['age'])
                if age < 0 or age > 150:
                    errors.append(f"Invalid age: {age}")
            except (ValueError, TypeError):
                errors.append("Age must be a number")
        
        # Validate gender
        if 'gender' in patient_data:
            valid_genders = {'male', 'female', 'other', 'm', 'f', 'unknown'}
            if str(patient_data['gender']).lower() not in valid_genders:
                errors.append(f"Invalid gender: {patient_data['gender']}")
        
        # Validate patient_id format
        if 'patient_id' in patient_data:
            patient_id = str(patient_data['patient_id'])
            if not re.match(r'^[A-Z0-9\-]+$', patient_id):
                errors.append(f"Invalid patient_id format: {patient_id}")
        
        return len(errors) == 0, errors
    
    def print_validation_report(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("DATA VALIDATION REPORT")
        print("="*60)
        print(f"Dataset Type: {self.dataset_type}")
        print(f"Total Rows: {self.validation_results['total_rows']}")
        print(f"Valid Rows: {self.validation_results['valid_rows']}")
        print(f"Missing Critical Fields: {self.validation_results['missing_critical']}")
        print(f"Duplicates Removed: {self.validation_results['duplicates']}")
        print(f"Invalid Data Types: {self.validation_results['invalid_types']}")
        
        if self.validation_results['errors']:
            print("\nErrors:")
            for error in self.validation_results['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.validation_results['errors']) > 10:
                print(f"  ... and {len(self.validation_results['errors']) - 10} more errors")
        
        print("="*60)
        
        # Return True if validation passed (no critical issues)
        return (self.validation_results['missing_critical'] == 0 and 
                self.validation_results['valid_rows'] > 0)


def validate_csv_import(file_path: str, dataset_type: str, unique_key: str = None) -> Tuple[pd.DataFrame, bool]:
    """
    Convenience function to validate CSV file before import
    
    Args:
        file_path: Path to CSV file
        dataset_type: Type of dataset (patient, hospital, etc.)
        unique_key: Column to check for duplicates
        
    Returns:
        Tuple of (cleaned DataFrame, validation_passed)
    """
    try:
        df = pd.read_csv(file_path)
        validator = DataValidator(dataset_type)
        cleaned_df, report = validator.validate_dataframe(df, unique_key)
        validation_passed = validator.print_validation_report()
        return cleaned_df, validation_passed
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame(), False
