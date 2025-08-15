import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from models.database import User
from werkzeug.security import generate_password_hash

def create_admin_user(full_name, email, password):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            return False
        
        # Create new admin user
        admin_user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Full Name: {full_name}")
        print(f"Email: {email}")
        print(f"Role: admin")
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a new admin user')
    parser.add_argument('--name', required=True, help='Full name of the admin user')
    parser.add_argument('--email', required=True, help='Email of the admin user')
    parser.add_argument('--password', required=True, help='Password for the admin user')
    
    args = parser.parse_args()
    
    create_admin_user(args.name, args.email, args.password)