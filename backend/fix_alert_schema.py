"""
Fixes the Alert table schema to allow NULL hospital_id
"""
# Prevent Flask app from starting
import os
os.environ['BOOTSTRAP_RUNNING'] = '1'  # Use the existing env var to skip server
os.environ['FLASK_APP'] = ''

from app import app, db

with app.app_context():
    try:
        # Try to alter Alert.hospital_id column to allow NULL
        print("Attempting to alter Alert table to allow NULL hospital_id...")
        
        # Check database type
        database_type = os.getenv('DATABASE_TYPE', '').lower()
        
        if database_type == 'mysql':
            from sqlalchemy import text
            stmt = text("ALTER TABLE alert MODIFY COLUMN hospital_id INT NULL")
            db.session.execute(stmt)
            db.session.commit()
            print("Success! Alert.hospital_id is now nullable in MySQL!")
        elif database_type == 'postgresql':
            from sqlalchemy import text
            stmt = text("ALTER TABLE alert ALTER COLUMN hospital_id DROP NOT NULL")
            db.session.execute(stmt)
            db.session.commit()
            print("Success! Alert.hospital_id is now nullable in PostgreSQL!")
        elif database_type == 'sqlite' or 'sqlite' in app.config.get('SQLALCHEMY_DATABASE_URI', '').lower():
            print("SQLite is flexible with NULLs, no schema change needed!")
        else:
            # Fallback: check URI
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '').lower()
            if 'mysql' in db_uri:
                from sqlalchemy import text
                stmt = text("ALTER TABLE alert MODIFY COLUMN hospital_id INT NULL")
                db.session.execute(stmt)
                db.session.commit()
                print("Success! Alert.hospital_id is now nullable in MySQL!")
            elif 'postgresql' in db_uri:
                from sqlalchemy import text
                stmt = text("ALTER TABLE alert ALTER COLUMN hospital_id DROP NOT NULL")
                db.session.execute(stmt)
                db.session.commit()
                print("Success! Alert.hospital_id is now nullable in PostgreSQL!")
            else:
                print("SQLite or unknown database type, no change needed!")
        
        print("Schema fix complete!")
        
    except Exception as e:
        print(f"Error during schema fix: {e}")
        db.session.rollback()
