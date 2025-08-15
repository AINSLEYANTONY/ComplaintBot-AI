import os
import sys
import logging
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Parse command line arguments
parser = argparse.ArgumentParser(description='Send a ticket status update email notification')
parser.add_argument('--ticket-id', type=str, help='Ticket ID to send notification for')
parser.add_argument('--user-email', type=str, help='Override the user email to send to')
parser.add_argument('--new-status', type=str, choices=['pending', 'in_progress', 'resolved', 'closed', 'escalated'],
                    help='New status to set for the ticket')
parser.add_argument('--use-updated', action='store_true', help='Use the updated email and notification services')
args = parser.parse_args()

# Import after path setup
from models.database import db, Ticket, User
from server.app import app

# Check if we should use the updated services
if args.use_updated:
    try:
        # Try to import from the updated files if they exist
        import importlib.util
        email_service_path = os.path.join(os.path.dirname(__file__), 'server', 'utils', 'email_service.py.updated')
        notification_service_path = os.path.join(os.path.dirname(__file__), 'server', 'utils', 'notification_service.py.updated')
        
        if os.path.exists(email_service_path):
            logger.info("Using updated email_service.py")
            # Use direct import with exec instead of importlib
            email_service_module = {}
            with open(email_service_path, 'r', encoding='utf-8') as f:
                exec(f.read(), email_service_module)
            EmailService = email_service_module['EmailService']
        else:
            logger.warning("Updated email_service.py not found, using original")
            from server.utils.email_service import EmailService
            
        if os.path.exists(notification_service_path):
            logger.info("Using updated notification_service.py")
            # Use direct import with exec instead of importlib
            notification_service_module = {}
            with open(notification_service_path, 'r', encoding='utf-8') as f:
                exec(f.read(), notification_service_module)
            NotificationService = notification_service_module['NotificationService']
        else:
            logger.warning("Updated notification_service.py not found, using original")
            from server.utils.notification_service import NotificationService
    except ImportError as e:
        logger.error(f"Import error: {e}")
        from server.utils.email_service import EmailService
        from server.utils.notification_service import NotificationService
else:
    # Use the original services
    from server.utils.email_service import EmailService
    from server.utils.notification_service import NotificationService

def get_ticket(ticket_id=None):
    """Get a ticket for testing"""
    with app.app_context():
        if ticket_id:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                logger.error(f"Ticket with ID {ticket_id} not found")
                return None
            return ticket
        
        # If no ticket ID provided, get the first ticket
        ticket = Ticket.query.first()
        if not ticket:
            logger.error("No tickets found in the system")
            return None
        return ticket

def get_user_for_ticket(ticket, override_email=None):
    """Get the user associated with a ticket"""
    with app.app_context():
        user = User.query.get(ticket.user_id)
        if not user:
            logger.error(f"User with ID {ticket.user_id} not found")
            return None
        
        # If an override email is provided, create a temporary user object
        if override_email:
            from types import SimpleNamespace
            return SimpleNamespace(id=user.id, email=override_email, full_name=user.full_name)
        
        return user

def get_assigned_agent(ticket):
    """Get the assigned agent for a ticket if available"""
    if not ticket.assigned_to:
        return None
        
    with app.app_context():
        agent = User.query.get(ticket.assigned_to)
        if not agent:
            return None
        return agent

def update_ticket_status(ticket, new_status):
    """Update a ticket's status"""
    old_status = ticket.status
    
    with app.app_context():
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            logger.info(f"Updated ticket {ticket.id} status from {old_status} to {new_status}")
            return old_status
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update ticket status: {str(e)}")
            return None

def send_notification(ticket, old_status, user, agent=None):
    """Send a status update notification"""
    notification_service = NotificationService()
    
    logger.info(f"Sending status update notification for ticket {ticket.id} to {user.email}")
    
    # Use app context for database operations
    with app.app_context():
        result = notification_service.notify_status_update(
            ticket=ticket,
            old_status=old_status
        )
    
    if result:
        logger.info("✅ Status update notification sent successfully")
    else:
        logger.error("❌ Failed to send status update notification")
    
    return result

def send_direct_email(ticket, old_status, user, agent=None):
    """Send a status update email directly using EmailService"""
    email_service = EmailService()
    
    # Get agent name if available
    agent_name = agent.full_name if agent else None
    
    logger.info(f"Sending direct status update email for ticket {ticket.id} to {user.email}")
    
    # Use app context for database operations
    with app.app_context():
        result = email_service.send_status_update(
            user.email,
            ticket,
            old_status,
            user_name=user.full_name,
            assigned_agent=agent_name
        )
    
    if result:
        logger.info("✅ Status update email sent successfully")
    else:
        logger.error("❌ Failed to send status update email")
    
    return result

def main():
    # Get the ticket
    ticket = get_ticket(args.ticket_id)
    if not ticket:
        return False
    
    # Get the user
    user = get_user_for_ticket(ticket, args.user_email)
    if not user:
        return False
    
    # Get the assigned agent if available
    agent = get_assigned_agent(ticket)
    
    # Update ticket status if requested
    old_status = None
    if args.new_status and args.new_status != ticket.status:
        old_status = update_ticket_status(ticket, args.new_status)
        if old_status is None:
            return False
    else:
        # If not updating status, use a dummy old status
        old_status = "pending" if ticket.status != "pending" else "in_progress"
    
    # Send the notification through NotificationService
    notification_result = send_notification(ticket, old_status, user, agent)
    
    # Also try direct email for comparison
    email_result = send_direct_email(ticket, old_status, user, agent)
    
    return notification_result or email_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)