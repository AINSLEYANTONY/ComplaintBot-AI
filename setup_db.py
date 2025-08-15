import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created successfully")