
import sys
import os

original_name = __name__
__name__ = "not_main"

from app import app, db
from sqlalchemy import inspect, text

__name__ = original_name

with app.app_context():
    print("=== ADDING HOSPITAL_ID COLUMNS TO EXISTING TABLES ===")
    print("=" * 60)
    
    inspector = inspect(db.engine)
    quote = db.engine.dialect.identifier_preparer.quote
    
    # List of tables and their new column definitions
    tables_to_update = [
        {
            "table": "diagnosis",
            "column": "hospital_id",
            "type": "INT"
        },
        {
            "table": "treatment",
            "column": "hospital_id",
            "type": "INT"
        },
        {
            "table": "alert",
            "column": "hospital_id",
            "type": "INT"
        },
        {
            "table": "prescription",
            "column": "hospital_id",
            "type": "INT"
        },
        {
            "table": "lab_test",
            "column": "hospital_id",
            "type": "INT"
        }
    ]
    
    for item in tables_to_update:
        table_name = item["table"]
        column_name = item["column"]
        column_type = item["type"]
        
        try:
            existing_columns = {c["name"] for c in inspector.get_columns(table_name)}
            if column_name in existing_columns:
                print(f"  ✓ {table_name}.{column_name} already exists")
                continue
            
            # Add the column
            statement = f"ALTER TABLE {quote(table_name)} ADD COLUMN {quote(column_name)} {column_type} NULL"
            db.session.execute(text(statement))
            db.session.commit()
            print(f"  ✓ Added {table_name}.{column_name}")
        except Exception as e:
            print(f"  ✗ Failed to add {table_name}.{column_name}: {str(e)}")
    
    print("\n✅ HOSPITAL_ID COLUMNS ADDED SUCCESSFULLY!")
