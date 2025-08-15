import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from sqlalchemy import text

# Migration script to add escalation_level column to tickets table
with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("SELECT * FROM pragma_table_info('tickets') WHERE name='escalation_level'")).fetchone()
        
        if not result:
            print("Adding escalation_level column to tickets table...")
            db.session.execute(text("ALTER TABLE tickets ADD COLUMN escalation_level INTEGER DEFAULT 0"))
            db.session.commit()
            print("Migration completed successfully!")
        else:
            print("Column escalation_level already exists in tickets table.")
    except Exception as e:
        print(f"Error during migration: {e}")
        db.session.rollback()