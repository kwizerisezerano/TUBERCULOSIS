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
from import_data import main as import_data_main
from models.models import Alert, Diagnosis, ExternalDatasetRow, Patient, Treatment, User, LabTest, Prescription, AuditLog, ATCDrug, DetailedLabResult, AntibioticResistance
from models.train_model import train_models_from_database
from seed_users import seed_all


MANAGED_MODELS = [User, Patient, Diagnosis, Treatment, Alert, ExternalDatasetRow, LabTest, Prescription, AuditLog, ATCDrug, DetailedLabResult, AntibioticResistance]


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

    for model in MANAGED_MODELS:
        table = model.__table__
        if table.name not in existing_tables:
            continue

        existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_columns or column.primary_key:
                continue

            compiled_type = column.type.compile(dialect=db.engine.dialect)
            nullable_sql = "" if column.nullable else " NOT NULL"
            statement = (
                f"ALTER TABLE {quote(table.name)} "
                f"ADD COLUMN {quote(column.name)} {compiled_type}{nullable_sql}"
            )
            db.session.execute(text(statement))
            db.session.commit()

        inspector = inspect(db.engine)


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

    if import_data_enabled:
        print("[2/4] Importing and preprocessing datasets...")
        import_data_main()
        print("      Dataset import finished.")
    else:
        print("[2/4] Skipping dataset import.")

    if seed_enabled:
        print("[3/4] Seeding users, roles, and sample data...")
        seed_result = seed_all()
        print(f"      Users in database: {seed_result['users']['total']} (added {seed_result['users']['added']}).")
        print(f"      Sample data added: {seed_result['sample_data']}")
    else:
        print("[3/4] Skipping user/sample data seeding.")

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
            "patients": Patient.query.count(),
            "users": User.query.count(),
            "training_result": training_result,
            "detailed_lab_results": DetailedLabResult.query.count(),
            "antibiotic_resistance_records": AntibioticResistance.query.count(),
        }

    print("=" * 60)
    print(f"Database type: {summary['database']}")
    print(f"Patients available: {summary['patients']}")
    print(f"Users available: {summary['users']}")
    print(f"Detailed lab results: {summary['detailed_lab_results']}")
    print(f"Antibiotic resistance records: {summary['antibiotic_resistance_records']}")
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
        app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
