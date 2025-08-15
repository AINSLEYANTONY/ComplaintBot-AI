import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app import app, db
from models.database import User, Category, Agent, Ticket

with app.app_context():
    # Create categories
    categories = [
        Category(name="Technical Issue", description="Problems with software or hardware"),
        Category(name="Billing", description="Questions about billing or payments"),
        Category(name="Account", description="Account-related issues"),
        Category(name="General Inquiry", description="General questions about services")
    ]
    
    for category in categories:
        db.session.add(category)
    
    # Create users
    users = [
        User(full_name="Admin User", email="admin@example.com", password_hash="$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnpY0o58unSvIPxddLxGystU.O", role="admin"),
        User(full_name="Customer One", email="customer1@example.com", password_hash="$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnpY0o58unSvIPxddLxGystU.O", role="user"),
        User(full_name="Customer Two", email="customer2@example.com", password_hash="$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnpY0o58unSvIPxddLxGystU.O", role="user")
    ]
    
    for user in users:
        db.session.add(user)
    
    # Commit to create IDs
    db.session.commit()
    
    # Create agents
    agents = [
        Agent(user_id=users[0].id, specialization="Technical", max_tickets=10, current_tickets=0, is_available=True),
        Agent(user_id=users[0].id, specialization="Billing", max_tickets=10, current_tickets=0, is_available=True)
    ]
    
    for agent in agents:
        db.session.add(agent)
    
    # Commit to create IDs
    db.session.commit()
    
    # Create tickets with unique IDs
    ticket1 = Ticket(
        id=f"TCK-{int(time.time())}",
        title="Cannot access my account",
        description="I'm unable to log in to my account since yesterday",
        user_id=users[1].id,
        category="Account",
        category_id=categories[2].id,
        priority="medium",
        status="open",
        assigned_to=agents[0].id
    )
    db.session.add(ticket1)
    db.session.commit()
    
    # Wait a second to ensure unique timestamp
    time.sleep(1)
    
    ticket2 = Ticket(
        id=f"TCK-{int(time.time())}",
        title="Billing discrepancy",
        description="I was charged twice for my last payment",
        user_id=users[2].id,
        category="Billing",
        category_id=categories[1].id,
        priority="high",
        status="in_progress",
        assigned_to=agents[1].id
    )
    db.session.add(ticket2)
    
    # Commit all changes
    db.session.commit()
    
    print("Sample data added successfully")