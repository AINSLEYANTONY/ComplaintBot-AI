# Email Notification System for Ticket Status Updates

This document provides instructions on how to send email notifications to users regarding ticket status updates in the Complaint Management System.

## Overview

The system includes two main components for sending email notifications:

1. **EmailService**: Handles the actual email sending functionality, including formatting and delivery.
2. **NotificationService**: Coordinates notifications, including creating database records and triggering emails.

## Updated Files

We've created updated versions of the email and notification services to fix parameter mismatches and improve functionality:

- `server/utils/email_service.py.updated`: Updated email service with improved parameter handling
- `server/utils/notification_service.py.updated`: Updated notification service to match the email service parameters

## How to Apply Updates

To apply the updated files to your system, run the `apply_updates.py` script:

```bash
python apply_updates.py
```

This will:
1. Create backups of your existing files (.bak extension)
2. Replace them with the updated versions
3. Log the changes made

## Sending Email Notifications

### Option 1: Using the Test Script

We've created a test script to easily send email notifications for ticket status updates:

```bash
python send_status_email.py --ticket-id <ID> --new-status <STATUS> --use-updated
```

Parameters:
- `--ticket-id`: The ID of the ticket to update (optional, uses first ticket if not specified)
- `--user-email`: Override the recipient email address (optional)
- `--new-status`: New status to set for the ticket (optional, choices: pending, in_progress, resolved, closed, escalated)
- `--use-updated`: Flag to use the updated service files instead of the originals

### Option 2: Using the API

You can also trigger email notifications by updating a ticket's status through the API:

```bash
curl -X PUT http://localhost:5000/api/tickets/<ticket_id>/status \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

## Email Templates

The system uses HTML templates for email notifications, located in `server/templates/`:

- `ticket_created.html`: Sent when a new ticket is created
- `ticket_updated.html`: Sent when a ticket's status is updated
- `escalation_alert.html`: Sent to administrators when a ticket is escalated

## Environment Configuration

Email sending requires proper SMTP configuration in your environment variables:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM_NAME=ComplaintBot AI Support
```

## Troubleshooting

If emails are not being sent:

1. Check your SMTP configuration in environment variables
2. Verify that the email templates exist in the correct location
3. Check the application logs for specific error messages
4. Make sure your SMTP server allows the application to send emails (may require app-specific password for Gmail)
5. Verify that the user email addresses in the database are valid

## Advanced Testing

For more comprehensive testing, you can use the `test_send_email.py` script which provides additional options:

```bash
python test_send_email.py --ticket-id <ID> --user-email <EMAIL> --new-status <STATUS> --direct
```

The `--direct` flag tests the EmailService directly, bypassing the NotificationService.