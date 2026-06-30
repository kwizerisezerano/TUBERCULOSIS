"""
Check current facilities and pharmacy inventory in database.
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

def check_data():
    try:
        with engine.connect() as conn:
            # Check facilities
            print("=== FACILITIES ===")
            result = conn.execute(text("SELECT id, hospital_id, name, facility_type FROM hospital LIMIT 20"))
            facilities = result.fetchall()
            print(f"Total facilities: {len(facilities)}")
            for fac in facilities:
                print(f"  ID: {fac[0]}, hospital_id: {fac[1]}, Name: {fac[2]}, Type: {fac[3]}")
            
            # Check facility types
            print("\n=== FACILITY TYPES ===")
            result = conn.execute(text("SELECT facility_type, COUNT(*) FROM hospital GROUP BY facility_type"))
            types = result.fetchall()
            for t in types:
                print(f"  {t[0]}: {t[1]}")
            
            # Check pharmacy inventory
            print("\n=== PHARMACY INVENTORY ===")
            result = conn.execute(text("SELECT COUNT(*) FROM pharmacy_inventory"))
            count = result.fetchone()[0]
            print(f"Total inventory records: {count}")
            
            if count > 0:
                result = conn.execute(text("""
                    SELECT pi.id, h.name as hospital, a.drug_name, pi.stock_quantity, pi.unit_type
                    FROM pharmacy_inventory pi
                    JOIN hospital h ON pi.hospital_id = h.id
                    JOIN atc_drug a ON pi.atc_drug_id = a.id
                    LIMIT 20
                """))
                inventory = result.fetchall()
                print("\nInventory details:")
                for inv in inventory:
                    print(f"  Hospital: {inv[1]}, Drug: {inv[2]}, Stock: {inv[3]}, Unit: {inv[4]}")
            
            # Check TB medicines
            print("\n=== TB MEDICINES ===")
            result = conn.execute(text("""
                SELECT drug_name, atc_code FROM atc_drug 
                WHERE drug_name IN ('Isoniazid', 'Rifampicin', 'Pyrazinamide', 'Ethambutol')
            """))
            tb_drugs = result.fetchall()
            print(f"TB medicines found: {len(tb_drugs)}")
            for drug in tb_drugs:
                print(f"  {drug[0]} ({drug[1]})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_data()
