import smtplib, os, json
import logging
from email.message import EmailMessage
import socket
import ssl

# Configure logging
logger = logging.getLogger(__name__)

def validate_email_config():
    """Validate email configuration"""
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    if not gmail_address or gmail_address == "demo@demo.gmail":
        return False, "GMAIL_ADDRESS not configured or using demo value"

    if not gmail_password or gmail_password == "demopass":
        return False, "GMAIL_PASSWORD not configured or using demo value"

    return True, "Email configuration valid"

def notify(message):
    """Send email notification with comprehensive error handling"""
    try:
        logger.info("Starting email notification process")

        # Validate email configuration
        config_valid, config_message = validate_email_config()
        if not config_valid:
            logger.warning(f"Email configuration issue: {config_message}")
            logger.info("Skipping email notification due to configuration issues")
            return None  # Don't fail the message processing for config issues

        # Parse message
        try:
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            message_data = json.loads(message)
            logger.info(f"Parsed message data: {message_data}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            error_msg = f"Failed to parse message: {e}"
            logger.error(error_msg)
            return error_msg

        # Extract required fields
        try:
            mp3_fid = message_data["mp3_fid"]
            # Handle both username and user_email fields for backward compatibility
            receiver_address = message_data.get("username") or message_data.get("user_email")

            if not mp3_fid:
                return "mp3_fid is empty"
            if not receiver_address:
                return "neither username nor user_email (receiver address) is provided"

        except KeyError as e:
            error_msg = f"Missing required field: {e}"
            logger.error(error_msg)
            return error_msg

        # Get email credentials
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")

        logger.info(f"Sending notification to {receiver_address} for mp3_fid: {mp3_fid}")

        # Create email message
        try:
            msg = EmailMessage()
            msg.set_content(f"Your MP3 file (ID: {mp3_fid}) is now ready for download!")
            msg["Subject"] = "MP3 Download Ready"
            msg["From"] = sender_address
            msg["To"] = receiver_address
            logger.info("Email message created successfully")
        except Exception as e:
            error_msg = f"Failed to create email message: {e}"
            logger.error(error_msg)
            return error_msg

        # Send email
        session = None
        try:
            # Create SMTP session with timeout
            logger.info("Connecting to Gmail SMTP server...")
            session = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)

            # Enable TLS encryption
            logger.info("Starting TLS encryption...")
            session.starttls()

            # Login to Gmail
            logger.info("Logging in to Gmail...")
            session.login(sender_address, sender_password)

            # Send email
            logger.info("Sending email...")
            session.send_message(msg, sender_address, receiver_address)

            logger.info(f"Email sent successfully to {receiver_address}")
            return None  # Success

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed: {e}. Check Gmail credentials and app password."
            logger.error(error_msg)
            return error_msg
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient refused: {e}. Invalid recipient email address."
            logger.error(error_msg)
            return error_msg
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"SMTP server disconnected: {e}"
            logger.error(error_msg)
            return error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {e}"
            logger.error(error_msg)
            return error_msg
        except socket.timeout as e:
            error_msg = f"Connection timeout: {e}"
            logger.error(error_msg)
            return error_msg
        except socket.gaierror as e:
            error_msg = f"DNS resolution failed: {e}"
            logger.error(error_msg)
            return error_msg
        except ConnectionRefusedError as e:
            error_msg = f"Connection refused: {e}"
            logger.error(error_msg)
            return error_msg
        except ssl.SSLError as e:
            error_msg = f"SSL error: {e}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during email sending: {e}"
            logger.error(error_msg)
            return error_msg
        finally:
            # Always close the session
            if session:
                try:
                    session.quit()
                    logger.info("SMTP session closed")
                except Exception as e:
                    logger.warning(f"Error closing SMTP session: {e}")

    except Exception as e:
        error_msg = f"Unexpected error in notify function: {e}"
        logger.error(error_msg)
        return error_msg
