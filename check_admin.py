import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from models.database import User

with app.app_context():
    # Check for admin user
    admin = User.query.filter_by(email='admin@example.com').first()
    print(f'Admin user exists: {admin is not None}')
    if admin:
        print(f'Email: {admin.email}')
        print(f'Role: {admin.role}')
        print(f'Password hash: {admin.password_hash}')
    
    # Also check for admin@complaintbot.ai
    admin2 = User.query.filter_by(email='admin@complaintbot.ai').first()
    print(f'\nAdmin2 user exists: {admin2 is not None}')
    if admin2:
        print(f'Email: {admin2.email}')
        print(f'Role: {admin2.role}')
        print(f'Password hash: {admin2.password_hash}')