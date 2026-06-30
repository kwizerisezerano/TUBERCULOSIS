"""
Add new columns to Hospital table for healthcare, laboratory, pharmacy features.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection - MySQL
DATABASE_URL = 'mysql+pymysql://root:@localhost:3306/tb_diagnostic'
engine = create_engine(DATABASE_URL)

def add_facility_columns():
    try:
        with engine.connect() as conn:
            # Healthcare columns
            print("Adding healthcare columns...")
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_emergency BOOLEAN DEFAULT FALSE"))
                print("+ has_emergency")
            except Exception as e:
                print(f"- has_emergency (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_surgery BOOLEAN DEFAULT FALSE"))
                print("+ has_surgery")
            except Exception as e:
                print(f"- has_surgery (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_maternity BOOLEAN DEFAULT FALSE"))
                print("+ has_maternity")
            except Exception as e:
                print(f"- has_maternity (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_pediatrics BOOLEAN DEFAULT FALSE"))
                print("+ has_pediatrics")
            except Exception as e:
                print(f"- has_pediatrics (may exist): {e}")
            
            # Laboratory columns
            print("\nAdding laboratory columns...")
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN lab_capacity INT"))
                print("+ lab_capacity")
            except Exception as e:
                print(f"- lab_capacity (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_genexpert BOOLEAN DEFAULT FALSE"))
                print("+ has_genexpert")
            except Exception as e:
                print(f"- has_genexpert (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_culture BOOLEAN DEFAULT FALSE"))
                print("+ has_culture")
            except Exception as e:
                print(f"- has_culture (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_xray BOOLEAN DEFAULT FALSE"))
                print("+ has_xray")
            except Exception as e:
                print(f"- has_xray (may exist): {e}")
            
            # Pharmacy columns
            print("\nAdding pharmacy columns...")
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN pharmacy_capacity INT"))
                print("+ pharmacy_capacity")
            except Exception as e:
                print(f"- pharmacy_capacity (may exist): {e}")
            
            try:
                conn.execute(text("ALTER TABLE hospital ADD COLUMN has_cold_storage BOOLEAN DEFAULT FALSE"))
                print("+ has_cold_storage")
            except Exception as e:
                print(f"- has_cold_storage (may exist): {e}")
            
            conn.commit()
            print("\n✓ Facility columns updated successfully!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_facility_columns()
