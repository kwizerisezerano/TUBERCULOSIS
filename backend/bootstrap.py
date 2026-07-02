"""
One-command backend bootstrap for the TB Diagnostic System.

Drops and recreates the database schema, imports datasets, seeds users,
trains models, and can start the API server.
"""
import argparse
import os
import subprocess
import sys


def _use_project_venv_when_available():
    # Allow `python bootstrap.py ...` to work from the backend folder without
    # requiring the user to activate the virtual environment first.
    current_prefix = os.path.abspath(sys.prefix)
    base_prefix = os.path.abspath(getattr(sys, "base_prefix", sys.prefix))
    running_inside_venv = current_prefix != base_prefix
    if running_inside_venv:
        return

    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        return

    current_python = os.path.normcase(os.path.abspath(sys.executable))
    target_python = os.path.normcase(os.path.abspath(venv_python))
    if current_python == target_python:
        return

    env = os.environ.copy()
    env["TB_BACKEND_AUTO_VENV"] = "1"
    completed = subprocess.run(
        [target_python, os.path.abspath(__file__), *sys.argv[1:]],
        env=env,
        check=False,
    )
    raise SystemExit(completed.returncode)


_use_project_venv_when_available()

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from app import app, db, load_models
from import_data import main as import_data_main, get_or_create_default_hospital
from import_new_datasets import import_healthcare_dataset, import_medicine_dataset, import_amr_dataset
from models.models import Alert, Diagnosis, ExternalDatasetRow, Patient, Treatment, User, LabTest, Prescription, AuditLog, ATCDrug, DetailedLabResult, AntibioticResistance, Hospital, PharmacyInventory, PatientConsent
from models.train_model import train_models_from_database
from seed_users import seed_all
from seed_facilities_and_inventory import seed_facilities, seed_pharmacy_inventory
from add_prescription_dosage_fields import add_prescription_fields
from seed_lab_tests import seed_lab_tests
from seed_patient_phones import main as seed_patient_phones_main
from add_patient_indexes import add_indexes


MANAGED_MODELS = [Hospital, User, Patient, Diagnosis, Treatment, Alert, ExternalDatasetRow, LabTest, Prescription, AuditLog, ATCDrug, DetailedLabResult, AntibioticResistance, PharmacyInventory, PatientConsent]


def recreate_database():
    database_type = os.getenv("DATABASE_TYPE", "sqlite").lower()

    db.session.remove()

    if database_type == "mysql":
        db_name = os.getenv("DB_NAME", "tb_diagnostic")
        db.engine.dispose()
        admin_url = (
            f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:{int(os.getenv('DB_PORT', 3306))}/mysql"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        quoted_name = f"`{db_name}`"
        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {quoted_name}"))
            conn.execute(text(f"CREATE DATABASE {quoted_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        admin_engine.dispose()
        return

    if database_type == "postgresql":
        db_name = os.getenv("DB_NAME", "tb_diagnostic")
        db.engine.dispose()
        admin_url = (
            f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', '')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 5432)}/postgres"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        quoted_name = f'"{db_name}"'
        with admin_engine.connect() as conn:
            conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :db_name AND pid <> pg_backend_pid()"
                ),
                {"db_name": db_name},
            )
            conn.execute(text(f"DROP DATABASE IF EXISTS {quoted_name}"))
            conn.execute(text(f"CREATE DATABASE {quoted_name}"))
        admin_engine.dispose()
        return

    db.engine.dispose()
    sqlite_url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    sqlite_path = sqlite_url.database or "tb_data.db"
    candidate_paths = [sqlite_path]
    if not os.path.isabs(sqlite_path):
        candidate_paths.append(os.path.join(app.instance_path, sqlite_path))
        candidate_paths.append(os.path.join(os.path.dirname(__file__), sqlite_path))

    for candidate in candidate_paths:
        normalized = os.path.abspath(candidate)
        if os.path.exists(normalized):
            os.remove(normalized)
            break


def ensure_schema_compatibility():
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())
    quote = db.engine.dialect.identifier_preparer.quote
    
    # Determine database type from dialect
    database_type = os.getenv("DATABASE_TYPE", "").lower()
    if not database_type:
        if "mysql" in db.engine.dialect.name:
            database_type = "mysql"
        elif "postgres" in db.engine.dialect.name:
            database_type = "postgresql"
        else:
            database_type = "sqlite"

    for model in MANAGED_MODELS:
        table = model.__table__
        if table.name not in existing_tables:
            continue

        existing_columns = {column["name"]: column for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name not in existing_columns and not column.primary_key:
                compiled_type = column.type.compile(dialect=db.engine.dialect)
                nullable_sql = "" if column.nullable else " NOT NULL"
                statement = (
                    f"ALTER TABLE {quote(table.name)} "
                    f"ADD COLUMN {quote(column.name)} {compiled_type}{nullable_sql}"
                )
                db.session.execute(text(statement))
                db.session.commit()
            
            # Special case: Ensure Alert.hospital_id is nullable
            if table.name == "alert" and column.name == "hospital_id":
                existing_col = existing_columns.get("hospital_id")
                if existing_col and existing_col.get("nullable") is False:
                    print(f"      Updating {table.name}.{column.name} to be nullable...")
                    if database_type == "mysql":
                        statement = f"ALTER TABLE {quote(table.name)} MODIFY COLUMN {quote(column.name)} INT NULL"
                    elif database_type == "postgresql":
                        statement = f"ALTER TABLE {quote(table.name)} ALTER COLUMN {quote(column.name)} DROP NOT NULL"
                    else:  # sqlite
                        # SQLite doesn't support ALTER COLUMN MODIFY, we'd need to recreate table
                        # But for simplicity, we'll skip for sqlite as it's more flexible
                        pass
                    if database_type in ["mysql", "postgresql"]:
                        db.session.execute(text(statement))
                        db.session.commit()
            
            # Special case: Ensure patient.otp_code column exists and is large enough for encryption
            if table.name == "patient" and column.name == "otp_code":
                existing_col = existing_columns.get("otp_code")
                existing_col_old = existing_columns.get("_otp_code")
                
                if existing_col_old and not existing_col:
                    # Old column _otp_code exists, rename it to otp_code
                    print(f"      Renaming {table.name}._otp_code to {table.name}.otp_code...")
                    if database_type == "mysql":
                        statement = f"ALTER TABLE {quote(table.name)} CHANGE COLUMN {quote('_otp_code')} {quote('otp_code')} VARCHAR(200)"
                    elif database_type == "postgresql":
                        statement = f"ALTER TABLE {quote(table.name)} RENAME COLUMN {quote('_otp_code')} TO {quote('otp_code')}"
                    else:  # sqlite
                        statement = f"ALTER TABLE {quote(table.name)} RENAME COLUMN {quote('_otp_code')} TO {quote('otp_code')}"
                    db.session.execute(text(statement))
                    db.session.commit()
                elif not existing_col and not existing_col_old:
                    # Column doesn't exist at all, add it
                    print(f"      Adding missing {table.name}.{column.name} column...")
                    if database_type == "mysql":
                        statement = f"ALTER TABLE {quote(table.name)} ADD COLUMN {quote(column.name)} VARCHAR(200)"
                    elif database_type == "postgresql":
                        statement = f"ALTER TABLE {quote(table.name)} ADD COLUMN {quote(column.name)} VARCHAR(200)"
                    else:  # sqlite
                        statement = f"ALTER TABLE {quote(table.name)} ADD COLUMN {quote(column.name)} VARCHAR(200)"
                    db.session.execute(text(statement))
                    db.session.commit()
                elif existing_col:
                    # Column exists, check if it's too small (encrypted data needs more space)
                    # Always update to VARCHAR(200) for OTP encryption compatibility
                    print(f"      Updating {table.name}.{column.name} to VARCHAR(200) for encryption...")
                    if database_type == "mysql":
                        statement = f"ALTER TABLE {quote(table.name)} MODIFY COLUMN {quote(column.name)} VARCHAR(200)"
                    elif database_type == "postgresql":
                        statement = f"ALTER TABLE {quote(table.name)} ALTER COLUMN {quote(column.name)} TYPE VARCHAR(200)"
                    else:  # sqlite
                        # SQLite doesn't support ALTER COLUMN MODIFY, we'd need to recreate table
                        # For sqlite, we'll skip as it's more flexible with column sizes
                        print(f"      Skipping column size update for SQLite (flexible sizing)")
                        pass
                    if database_type in ["mysql", "postgresql"]:
                        db.session.execute(text(statement))
                        db.session.commit()

        inspector = inspect(db.engine)


def seed_alerts():
    """Seed sample alerts for testing purposes."""
    with app.app_context():
        # Get first hospital and patient
        hospital = Hospital.query.first()
        patient = Patient.query.first()
        
        if not hospital or not patient:
            print("      Skipping alert seeding: no hospital or patient available.")
            return 0
        
        # Check if alerts already exist
        existing_alerts = Alert.query.count()
        if existing_alerts > 0:
            print(f"      Found {existing_alerts} existing alerts. Skipping seeding.")
            return 0
        
        # Create sample alerts
        alerts_data = [
            {
                "patient_id": patient.id,
                "hospital_id": hospital.id,
                "alert_type": "mdr_tb_suspected",
                "message": f"MDR-TB Suspected: Patient {patient.patient_id} shows signs of multidrug-resistant TB. Immediate DST and treatment review required.",
                "severity": "critical",
                "is_read": False
            },
            {
                "patient_id": patient.id,
                "hospital_id": hospital.id,
                "alert_type": "treatment_failure_risk",
                "message": f"Treatment Failure Risk Alert: Patient {patient.patient_id} has 85.2% probability of treatment failure. Consider regimen adjustment.",
                "severity": "critical",
                "is_read": False
            },
            {
                "patient_id": patient.id,
                "hospital_id": hospital.id,
                "alert_type": "critical_lab_result",
                "message": f"Critical Lab Result Available: GeneXpert for patient {patient.patient_id}. Results: MTB DETECTED, RIF RESISTANCE DETECTED.",
                "severity": "critical",
                "is_read": True
            },
            {
                "patient_id": patient.id,
                "hospital_id": hospital.id,
                "alert_type": "antibiotic_misuse",
                "message": f"Antibiotic Misuse Detected: Overprescription for patient {patient.patient_id}. Review medication history.",
                "severity": "high",
                "is_read": False
            },
            {
                "patient_id": None,
                "hospital_id": hospital.id,
                "alert_type": "low_stock",
                "message": f"Low Stock Alert: Isoniazid at {hospital.name}. Current: 5, Threshold: 10",
                "severity": "high",
                "is_read": False
            }
        ]
        
        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            db.session.add(alert)
        
        db.session.commit()
        return len(alerts_data)


def ensure_patients_have_hospitals():
    """Ensure every patient is associated with at least one hospital"""
    with app.app_context():
        hospitals = Hospital.query.all()
        if not hospitals:
            default_hospital = get_or_create_default_hospital()
            hospitals = [default_hospital]
        
        patients_without_hospitals = Patient.query.filter(~Patient.hospitals.any()).all()
        if patients_without_hospitals:
            import random
            for patient in patients_without_hospitals:
                # Assign to 1-3 random hospitals
                num_hospitals = random.randint(1, min(3, len(hospitals)))
                assigned_hospitals = random.sample(hospitals, num_hospitals)
                for hospital in assigned_hospitals:
                    patient.hospitals.append(hospital)
            
            db.session.commit()
            return len(patients_without_hospitals)
        return 0


def bootstrap(import_data_enabled=True, seed_enabled=True, train_enabled=True, reset_database=True):
    print("=" * 60)
    print("TB DIAGNOSTIC SYSTEM - BACKEND BOOTSTRAP")
    print("=" * 60)

    with app.app_context():
        print("[1/4] Resetting database from scratch...")
        if reset_database:
            recreate_database()
            print("      Existing database dropped and recreated.")
        else:
            print("      Database reset skipped.")

        print("      Creating database tables...")
        db.create_all()
        ensure_schema_compatibility()
        print("      Tables ready.")
        
        print("      Adding performance indexes...")
        add_indexes()
        print("      Performance indexes added.")
        
        print("      Adding prescription dosage fields...")
        add_prescription_fields()
        print("      Prescription dosage fields added.")

    alerts_added = 0
    if seed_enabled:
        print("[2/4] Seeding healthcare centers, laboratories, pharmacies...")
        with app.app_context():
            seed_facilities()
            seed_pharmacy_inventory()
        print("      Facilities and inventory seeded.")
        
        print("[2.5/4] Seeding users, roles, and sample data...")
        seed_result = seed_all()
        print(f"      Users in database: {seed_result['users']['total']} (added {seed_result['users']['added']}).")
        print(f"      Sample data added: {seed_result['sample_data']}")
        
        print("[2.75/4] Seeding sample alerts...")
        alerts_added = seed_alerts()
        if alerts_added > 0:
            print(f"      Alerts added: {alerts_added}")
        
        print("[2.85/4] Seeding lab tests...")
        seed_lab_tests()
        
        print("[2.88/4] Ensuring patients from seeding have hospital associations...")
        with app.app_context():
            patients_fixed_seed = ensure_patients_have_hospitals()
            if patients_fixed_seed > 0:
                print(f"      Fixed {patients_fixed_seed} patients without hospital associations.")
        
        print("[2.9/4] Setting patient phone numbers for demo...")
        seed_patient_phones_main()
    else:
        print("[2/4] Skipping user/sample data seeding.")

    if import_data_enabled:
        print("[3/4] Importing and preprocessing datasets...")
        import_data_main()
        print("      Dataset import finished.")
        
        print("[3.5/4] Importing new multi-hospital datasets...")
        with app.app_context():
            import_healthcare_dataset()
            import_medicine_dataset()
            import_amr_dataset()
        print("      New dataset import finished.")
        
        print("[3.75/4] Ensuring patients have hospital associations...")
        patients_fixed = ensure_patients_have_hospitals()
        if patients_fixed > 0:
            print(f"      Fixed {patients_fixed} patients without hospital associations.")
        
        print("[3.8/4] Setting patient phone numbers...")
        seed_patient_phones_main()
    else:
        print("[3/4] Skipping dataset import.")
        print("[3.5/4] Ensuring patients have hospital associations...")
        with app.app_context():
            patients_fixed = ensure_patients_have_hospitals()
            if patients_fixed > 0:
                print(f"      Fixed {patients_fixed} patients without hospital associations.")
    
    print("[3.9/4] Ensuring all patients have phone numbers and verifying table structure...")
    with app.app_context():
        # Verify OTP columns exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('patient')]
        otp_code_exists = 'otp_code' in columns or '_otp_code' in columns
        otp_expires_at_exists = 'otp_expires_at' in columns
        
        if otp_code_exists:
            print("      ✓ OTP code column exists")
        else:
            print("      ⚠ OTP code column missing!")
        
        if otp_expires_at_exists:
            print("      ✓ OTP expires column exists")
        else:
            print("      ⚠ OTP expires column missing!")
        
        # Ensure all patients have phone numbers
        seed_patient_phones_main()

    training_result = None
    if train_enabled:
        print("[4/4] Training ML models from database...")
        with app.app_context():
          training_result = train_models_from_database()
          load_models()
        print("      Model training finished.")
    else:
        print("[4/4] Skipping model training.")

    with app.app_context():
        summary = {
            "database": os.getenv("DATABASE_TYPE", "sqlite"),
            "hospitals": Hospital.query.count(),
            "patients": Patient.query.count(),
            "users": User.query.count(),
            "training_result": training_result,
            "detailed_lab_results": DetailedLabResult.query.count(),
            "antibiotic_resistance_records": AntibioticResistance.query.count(),
            "alerts": Alert.query.count(),
        }

    print("=" * 60)
    print(f"Database type: {summary['database']}")
    print(f"Hospitals available: {summary['hospitals']}")
    print(f"Patients available: {summary['patients']}")
    print(f"Users available: {summary['users']}")
    print(f"Detailed lab results: {summary['detailed_lab_results']}")
    print(f"Antibiotic resistance records: {summary['antibiotic_resistance_records']}")
    print(f"Alerts available: {summary['alerts']}")
    print("=" * 60)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Bootstrap the TB Diagnostic backend.")
    parser.add_argument("--no-reset", action="store_true", help="Keep existing tables instead of dropping and recreating them.")
    parser.add_argument("--skip-import", action="store_true", help="Skip CSV import into the database.")
    parser.add_argument("--skip-seed", action="store_true", help="Skip user/role seeding.")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training.")
    parser.add_argument("--runserver", action="store_true", help="Start the Flask API after setup.")
    parser.add_argument("--host", default="0.0.0.0", help="Host for the Flask server.")
    parser.add_argument("--port", type=int, default=5000, help="Port for the Flask server.")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode.")
    args = parser.parse_args()

    bootstrap(
        reset_database=not args.no_reset,
        import_data_enabled=not args.skip_import,
        seed_enabled=not args.skip_seed,
        train_enabled=not args.skip_train,
    )

    if args.runserver:
        print("Starting backend API server...")
        from app import socketio
        socketio.run(app, host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
