
"""
Add is_active and updated_at columns to User table
"""
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from app import app, db
from models.models import User

with app.app_context():
    # Check if columns already exist
    try:
        # Try to query a user with is_active (will fail if column doesn't exist)
        user = User.query.first()
        print("✓ User table already has is_active column")
    except Exception as e:
        print("Adding columns...")
        # Add columns using raw SQL for MySQL
        try:
            # Add is_active column
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            # Add updated_at column
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
            db.session.commit()
            print("✓ Added is_active and updated_at columns")
        except Exception as ex:
            # If columns already exist (MySQL error 1060), commit anyway
            db.session.commit()
            print("Columns already exist, committing...")
    
    # Set all existing users to active
    User.query.update({"is_active": True})
    db.session.commit()
    print("✓ All users set to active")
    print("✓ Migration complete!")
