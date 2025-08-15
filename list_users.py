import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from models.database import User

with app.app_context():
    # Get all users
    users = User.query.all()
    
    print(f"Total users: {len(users)}")
    print("\nUser List:")
    print("-" * 80)
    print(f"{'ID':<5} {'Full Name':<20} {'Email':<30} {'Role':<10}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<5} {user.full_name:<20} {user.email:<30} {user.role:<10}")