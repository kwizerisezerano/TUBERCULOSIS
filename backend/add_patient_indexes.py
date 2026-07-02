"""
Add database indexes to improve patient query performance
"""
import os
import sys
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app
from models.models import db
from sqlalchemy import text

def add_indexes():
    with app.app_context():
        # Add indexes to Patient table for faster queries
        sys.stdout.write("Adding indexes to Patient table...\n")
        sys.stdout.flush()
        
        try:
            # Index on patient_id (already unique, but ensure it's indexed)
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_patient_id ON patient(patient_id)"))
            sys.stdout.write("✓ Added index on patient_id\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"Note: patient_id index may already exist: {e}\n")
            sys.stdout.flush()
        
        try:
            # Index on first_name for search
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_first_name ON patient(first_name)"))
            sys.stdout.write("✓ Added index on first_name\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"Note: first_name index may already exist: {e}\n")
            sys.stdout.flush()
        
        try:
            # Index on last_name for search
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_last_name ON patient(last_name)"))
            sys.stdout.write("✓ Added index on last_name\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"Note: last_name index may already exist: {e}\n")
            sys.stdout.flush()
        
        try:
            # Index on otp_expires_at for OTP cleanup
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_otp_expires_at ON patient(otp_expires_at)"))
            sys.stdout.write("✓ Added index on otp_expires_at\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"Note: otp_expires_at index may already exist: {e}\n")
            sys.stdout.flush()
        
        try:
            # Index on created_at for sorting
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_created_at ON patient(created_at)"))
            sys.stdout.write("✓ Added index on created_at\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"Note: created_at index may already exist: {e}\n")
            sys.stdout.flush()
        
        db.session.commit()
        sys.stdout.write("\n✅ All indexes added successfully!\n")
        sys.stdout.flush()

if __name__ == "__main__":
    add_indexes()
