"""
Add new dosage calculation fields to Prescription table.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.models import db
from sqlalchemy import text, inspect

def add_prescription_fields():
    """Add new dosage calculation fields to prescription table"""
    try:
        print("=== Adding Prescription Dosage Fields ===")
        
        # Check if table exists first
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'prescription' not in existing_tables:
            print("- Prescription table doesn't exist yet, skipping")
            return
        
        # Check if columns already exist
        existing_columns = [col['name'] for col in inspector.get_columns('prescription')]
        
        columns_to_add = [
            ('frequency', 'VARCHAR(50)'),
            ('tablets_per_dose', 'INT'),
            ('total_tablets', 'INT')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name in existing_columns:
                print(f"- {column_name} already exists, skipping")
                continue
            
            sql = f"ALTER TABLE prescription ADD COLUMN {column_name} {column_type}"
            db.session.execute(text(sql))
            print(f"+ Added {column_name} ({column_type})")
        
        db.session.commit()
        print("\n✓ Prescription table updated successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_prescription_fields()
