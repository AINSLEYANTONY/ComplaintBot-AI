import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from models.database import User

with app.app_context():
    # Check for new admin user
    admin = User.query.filter_by(email='newadmin@example.com').first()
    print(f'New admin user exists: {admin is not None}')
    if admin:
        print(f'Email: {admin.email}')
        print(f'Full Name: {admin.full_name}')
        print(f'Role: {admin.role}')
        print(f'Password hash: {admin.password_hash}')