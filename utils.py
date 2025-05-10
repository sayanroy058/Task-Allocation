from flask import current_app
from flask_mail import Mail, Message
import logging

# Initialize mail extension
mail = Mail()

def send_task_notification(user_email, task_id, description, deadline):
    """Send email notification when a new task is assigned to a user"""
    try:
        with current_app.app_context():
            msg = Message(
                subject=f"New Task Assigned - {task_id}",
                recipients=[user_email],
                sender="krishnajayanth418@gmail.com"
            )
            deadline_str = deadline.strftime('%d-%m-%Y')
            msg.body = f"""
Hello,

A new task has been assigned to you in the Task Management System.

Task ID: {task_id}
Deadline: {deadline_str}
Description: 
{description}

Please log in to your account to view the task details and attached files.

Thank you,
Task Management System
            """
            mail.send(msg)
            logging.info(f"Task notification email sent to {user_email} for {task_id}")
    except Exception as e:
        logging.error(f"Failed to send task notification email: {e}")

def send_completion_notification(task_id, user_name, is_edit=False):
    """Send email notification when a task is completed"""
    try:
        with current_app.app_context():
            admin_emails = current_app.config.get('ADMIN_EMAILS', [])
            if not admin_emails:
                logging.warning("No admin emails configured for notifications")
                return
                
            action = "edited" if is_edit else "completed"
            msg = Message(
                subject=f"Task {action.capitalize()} - {task_id}",
                recipients=admin_emails,
                sender="krishnajayanth418@gmail.com"
            )
            msg.body = f"""
Hello,

Task {task_id} has been {action} by {user_name}.

Please log in to the admin dashboard to review the submission.

Thank you,
Task Management System
            """
            mail.send(msg)
            logging.info(f"Task completion notification email sent to admins for {task_id}")
    except Exception as e:
        logging.error(f"Failed to send task completion notification email: {e}")

def send_edit_notification(user_email, task_id, instructions):
    """Send email notification when an edit is requested for a task"""
    try:
        with current_app.app_context():
            msg = Message(
                subject=f"Edit Requested - {task_id}",
                recipients=[user_email],
                sender="krishnajayanth418@gmail.com"
            )
            msg.body = f"""
Hello,

An edit has been requested for your task {task_id}.

Instructions:
{instructions}

Please log in to your account to review the edit instructions and attached files.

Thank you,
Task Management System
            """
            mail.send(msg)
            logging.info(f"Edit notification email sent to {user_email} for {task_id}")
    except Exception as e:
        logging.error(f"Failed to send edit notification email: {e}")