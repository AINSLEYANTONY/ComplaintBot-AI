import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from models.database import User
from werkzeug.security import generate_password_hash

def reset_admin_password(email, new_password):
    with app.app_context():
        # Find the admin user
        admin = User.query.filter_by(email=email).first()
        
        if not admin:
            print(f"No user found with email: {email}")
            return False
        
        if admin.role != 'admin':
            print(f"User {email} is not an admin (role: {admin.role})")
            return False
        
        # Update the password
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        print(f"Password reset successfully for admin: {admin.full_name}")
        print(f"Email: {admin.email}")
        print(f"New password hash: {admin.password_hash[:20]}...")
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Reset admin password')
    parser.add_argument('--email', required=True, help='Admin email')
    parser.add_argument('--password', required=True, help='New password')
    
    args = parser.parse_args()
    
    reset_admin_password(args.email, args.password)