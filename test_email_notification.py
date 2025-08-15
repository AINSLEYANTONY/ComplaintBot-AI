import sys
import os
from datetime import datetime
from models.database import db, User, Ticket
from utils.email_service import EmailService
from server.utils.notification_service import NotificationService

def setup_test_environment():
    # Check if we're using the updated email service
    if os.path.exists('utils/email_service.py.updated'):
        print("Using updated email service...")
        # Rename the original file to .bak if it doesn't exist already
        if not os.path.exists('utils/email_service.py.bak'):
            os.rename('utils/email_service.py', 'utils/email_service.py.bak')
        # Rename the updated file to the original name
        os.rename('utils/email_service.py.updated', 'utils/email_service.py')
        print("Email service updated successfully.")

def test_ticket_status_email(ticket_id=None, new_status=None):
    """Test sending a ticket status update email"""
    # Initialize services
    email_service = EmailService()
    notification_service = NotificationService()
    
    # Get or create a test ticket
    if ticket_id:
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            print(f"Error: Ticket with ID {ticket_id} not found.")
            return False
    else:
        # Get the first ticket from the database
        ticket = Ticket.query.first()
        if not ticket:
            print("Error: No tickets found in the database.")
            return False
    
    # Get the user associated with the ticket
    user = User.query.get(ticket.user_id)
    if not user:
        print(f"Error: User with ID {ticket.user_id} not found.")
        return False
    
    print(f"\nTest ticket information:")
    print(f"Ticket ID: {ticket.id}")
    print(f"Title: {ticket.title}")
    print(f"Current Status: {ticket.status}")
    print(f"User: {user.full_name} ({user.email})")
    
    # Determine old and new status
    old_status = ticket.status
    if new_status and new_status != old_status:
        # Update the ticket status in the database
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()
        if new_status == 'resolved':
            ticket.resolved_at = datetime.utcnow()
        db.session.commit()
        print(f"Updated ticket status from '{old_status}' to '{new_status}'")
    else:
        # For testing purposes, use a different status
        new_status = 'in-progress' if old_status != 'in-progress' else 'resolved'
        print(f"Using test status change from '{old_status}' to '{new_status}' (not saved to database)")
    
    # Test direct email service
    print("\nTesting direct email service...")
    email_result = email_service.send_status_update(
        user_email=user.email,
        ticket=ticket,
        old_status=old_status,
        user_name=user.full_name
    )
    print(f"Email service result: {'Success' if email_result else 'Failed'}")
    
    # Test notification service
    print("\nTesting notification service...")
    notification_result = notification_service.notify_status_update(
        ticket=ticket,
        old_status=old_status
    )
    print(f"Notification service result: {'Success' if notification_result else 'Failed'}")
    
    return email_result or notification_result

def main():
    # Setup test environment
    setup_test_environment()
    
    # Parse command line arguments
    ticket_id = None
    new_status = None
    
    if len(sys.argv) > 1:
        ticket_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        new_status = sys.argv[2]
    
    # Run the test
    result = test_ticket_status_email(ticket_id, new_status)
    
    # Print summary
    if result:
        print("\nTest completed successfully. Check your email configuration to see if emails were actually sent.")
        print("Note: If using default email settings, emails won't be delivered without proper SMTP configuration.")
    else:
        print("\nTest failed. Check the error messages above.")

if __name__ == "__main__":
    main()