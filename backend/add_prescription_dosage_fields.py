"""
Add new dosage calculation fields to Prescription table.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection - MySQL
DATABASE_URL = 'mysql+pymysql://root:@localhost:3306/tb_diagnostic'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def add_prescription_fields():
    """Add new dosage calculation fields to prescription table"""
    try:
        with engine.connect() as conn:
            print("=== Adding Prescription Dosage Fields ===")
            
            # Check if columns already exist
            inspector = engine.dialect.get_columns(conn, 'prescription')
            existing_columns = [col['name'] for col in inspector]
            
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
                conn.execute(text(sql))
                print(f"+ Added {column_name} ({column_type})")
            
            conn.commit()
            print("\n✓ Prescription table updated successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_prescription_fields()
