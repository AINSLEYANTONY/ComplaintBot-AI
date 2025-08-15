import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import after path setup
from models.database import db, Ticket, User
from server.app import app

# Check if we should use the updated email service
try:
    # First try to import from the updated file if it exists
    import importlib.util
    email_service_path = os.path.join(os.path.dirname(__file__), 'server', 'utils', 'email_service.py.updated')
    notification_service_path = os.path.join(os.path.dirname(__file__), 'server', 'utils', 'notification_service.py.updated')
    
    if os.path.exists(email_service_path):
        logger.info("Using updated email_service.py")
        spec = importlib.util.spec_from_file_location("email_service", email_service_path)
        email_service_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(email_service_module)
        EmailService = email_service_module.EmailService
    else:
        from server.utils.email_service import EmailService
        
    if os.path.exists(notification_service_path):
        logger.info("Using updated notification_service.py")
        spec = importlib.util.spec_from_file_location("notification_service", notification_service_path)
        notification_service_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(notification_service_module)
        NotificationService = notification_service_module.NotificationService
    else:
        from server.utils.notification_service import NotificationService
        
except ImportError as e:
    logger.error(f"Import error: {e}")
    from server.utils.email_service import EmailService
    from server.utils.notification_service import NotificationService

def get_ticket_and_user(ticket_id=None, user_email=None):
    """Get a ticket and user for testing"""
    with app.app_context():
        # If ticket_id is provided, get that specific ticket
        if ticket_id:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                logger.error(f"Ticket with ID {ticket_id} not found")
                return None, None
            user = User.query.get(ticket.user_id)
            return ticket, user
            
        # If user_email is provided, get the first ticket for that user
        if user_email:
            user = User.query.filter_by(email=user_email).first()
            if not user:
                logger.error(f"User with email {user_email} not found")
                return None, None
            ticket = Ticket.query.filter_by(user_id=user.id).first()
            if not ticket:
                logger.error(f"No tickets found for user {user_email}")
                return None, None
            return ticket, user
            
        # Otherwise, get the first ticket in the system
        ticket = Ticket.query.first()
        if not ticket:
            logger.error("No tickets found in the system")
            return None, None
        user = User.query.get(ticket.user_id)
        return ticket, user

def get_agent_info(ticket):
    """Get assigned agent information if available"""
    with app.app_context():
        if ticket and ticket.assigned_to:
            agent = User.query.get(ticket.assigned_to)
            if agent:
                return agent
    return None

def test_direct_email_service(ticket, user, old_status="pending", agent=None):
    """Test sending an email directly using EmailService"""
    email_service = EmailService()
    
    # Prepare agent info if available
    agent_name = agent.full_name if agent else None
    
    logger.info(f"Testing direct email service for ticket {ticket.id} to {user.email}")
    result = email_service.send_status_update(
        user_email=user.email,
        ticket=ticket,
        old_status=old_status,
        user_name=user.full_name,
        assigned_agent=agent_name
    )
    
    if result:
        logger.info("✅ Email sent successfully using direct EmailService")
    else:
        logger.error("❌ Failed to send email using direct EmailService")
    
    return result

def test_notification_service(ticket, old_status="pending", agent=None):
    """Test sending an email through NotificationService"""
    notification_service = NotificationService()
    
    # Prepare agent info if available
    agent_name = agent.full_name if agent else None
    
    logger.info(f"Testing notification service for ticket {ticket.id}")
    result = notification_service.notify_status_update(
        ticket=ticket,
        old_status=old_status,
        assigned_agent=agent_name
    )
    
    if result:
        logger.info("✅ Notification sent successfully using NotificationService")
    else:
        logger.error("❌ Failed to send notification using NotificationService")
    
    return result

def update_ticket_status(ticket_id, new_status):
    """Update a ticket's status for testing"""
    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            logger.error(f"Ticket with ID {ticket_id} not found")
            return None
            
        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            logger.info(f"Updated ticket {ticket_id} status from {old_status} to {new_status}")
            return ticket, old_status
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update ticket status: {str(e)}")
            return None, None

def main():
    """Main function to run the email test"""
    # Get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test email notification for ticket status update')
    parser.add_argument('--ticket-id', type=str, help='Specific ticket ID to use')
    parser.add_argument('--user-email', type=str, help='User email to send notification to')
    parser.add_argument('--new-status', type=str, default='in_progress', 
                        choices=['pending', 'in_progress', 'resolved', 'closed', 'escalated'],
                        help='New status to set for the ticket')
    parser.add_argument('--old-status', type=str, default=None, 
                        help='Override the old status (default: current ticket status)')
    parser.add_argument('--direct', action='store_true', 
                        help='Test direct EmailService instead of NotificationService')
    
    args = parser.parse_args()
    
    # Get ticket and user
    ticket, user = get_ticket_and_user(args.ticket_id, args.user_email)
    if not ticket or not user:
        logger.error("Cannot proceed without valid ticket and user")
        return False
    
    # Get assigned agent if available
    agent = get_agent_info(ticket)
    
    # If we're not updating the status, just use the current status
    if args.old_status is None:
        old_status = ticket.status
    else:
        old_status = args.old_status
    
    # Update ticket status if requested
    if args.new_status != ticket.status:
        updated_ticket, actual_old_status = update_ticket_status(ticket.id, args.new_status)
        if updated_ticket:
            ticket = updated_ticket
            if args.old_status is None:  # Only use the actual old status if not explicitly provided
                old_status = actual_old_status
    
    # Test the appropriate service
    if args.direct:
        return test_direct_email_service(ticket, user, old_status, agent)
    else:
        return test_notification_service(ticket, old_status, agent)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)