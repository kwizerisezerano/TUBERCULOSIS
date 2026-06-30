
import sys
import os

original_name = __name__
__name__ = "not_main"

from app import app, db
from bootstrap import ensure_schema_compatibility

__name__ = original_name

with app.app_context():
    print("=== APPLYING DATABASE SCHEMA UPDATES ===")
    ensure_schema_compatibility()
    print("\n✅ Schema updates complete!")
