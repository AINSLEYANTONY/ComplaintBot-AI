import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file before modifying it"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup of {file_path}: {str(e)}")
            return False
    else:
        logger.error(f"File not found: {file_path}")
        return False

def apply_update(updated_file, target_file):
    """Apply an updated file to the target location"""
    if not os.path.exists(updated_file):
        logger.error(f"Updated file not found: {updated_file}")
        return False
    
    # Create a backup of the original file
    if os.path.exists(target_file):
        if not backup_file(target_file):
            return False
    
    # Copy the updated file to the target location
    try:
        shutil.copy2(updated_file, target_file)
        logger.info(f"Applied update: {updated_file} -> {target_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to apply update: {str(e)}")
        return False

def main():
    # Define the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Define the paths to the updated files
    email_service_updated = os.path.join(project_root, 'server', 'utils', 'email_service.py.updated')
    notification_service_updated = os.path.join(project_root, 'server', 'utils', 'notification_service.py.updated')
    
    # Define the target paths
    email_service_target = os.path.join(project_root, 'server', 'utils', 'email_service.py')
    notification_service_target = os.path.join(project_root, 'server', 'utils', 'notification_service.py')
    
    # Apply the updates
    email_updated = False
    notification_updated = False
    
    if os.path.exists(email_service_updated):
        email_updated = apply_update(email_service_updated, email_service_target)
    else:
        logger.warning(f"Updated email service file not found: {email_service_updated}")
    
    if os.path.exists(notification_service_updated):
        notification_updated = apply_update(notification_service_updated, notification_service_target)
    else:
        logger.warning(f"Updated notification service file not found: {notification_service_updated}")
    
    # Summary
    if email_updated or notification_updated:
        logger.info("Updates applied successfully:")
        if email_updated:
            logger.info("- Email service updated")
        if notification_updated:
            logger.info("- Notification service updated")
        
        logger.info("\nTo restore the original files, you can use the .bak files created during the update.")
        return True
    else:
        logger.error("No updates were applied.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)