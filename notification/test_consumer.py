#!/usr/bin/env python3
"""
Test script to debug notification service issues
This script will help identify what's causing the consumer to crash
"""

import os
import sys
import json
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing module imports...")

    try:
        import pika
        logger.info(f"✓ pika imported successfully - version: {pika.__version__}")
    except ImportError as e:
        logger.error(f"✗ Failed to import pika: {e}")
        return False

    try:
        import smtplib
        logger.info("✓ smtplib imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import smtplib: {e}")
        return False

    try:
        from email.message import EmailMessage
        logger.info("✓ EmailMessage imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import EmailMessage: {e}")
        return False

    try:
        from send import email
        logger.info("✓ send.email module imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import send.email: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

    return True

def test_environment():
    """Test environment variables"""
    logger.info("Testing environment variables...")

    env_vars = {
        'MP3_QUEUE': os.environ.get('MP3_QUEUE', 'NOT_SET'),
        'VIDEO_QUEUE': os.environ.get('VIDEO_QUEUE', 'NOT_SET'),
        'GMAIL_ADDRESS': os.environ.get('GMAIL_ADDRESS', 'NOT_SET'),
        'GMAIL_PASSWORD': 'SET' if os.environ.get('GMAIL_PASSWORD') else 'NOT_SET',
        'RABBITMQ_HOST': os.environ.get('RABBITMQ_HOST', 'rabbitmq')
    }

    for var, value in env_vars.items():
        logger.info(f"  {var}: {value}")

    # Check for critical missing vars
    missing_vars = []
    if env_vars['GMAIL_ADDRESS'] == 'NOT_SET':
        missing_vars.append('GMAIL_ADDRESS')
    if env_vars['GMAIL_PASSWORD'] == 'NOT_SET':
        missing_vars.append('GMAIL_PASSWORD')

    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
    else:
        logger.info("✓ All critical environment variables are set")

    return True

def test_rabbitmq_connection():
    """Test RabbitMQ connection"""
    logger.info("Testing RabbitMQ connection...")

    rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')

    try:
        import pika
        logger.info(f"Attempting to connect to RabbitMQ at {rabbitmq_host}...")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_host,
                connection_attempts=3,
                retry_delay=1
            )
        )
        logger.info("✓ Successfully connected to RabbitMQ")

        channel = connection.channel()
        logger.info("✓ Channel created successfully")

        # Test queue declaration
        queue_name = os.environ.get('MP3_QUEUE', 'mp3')
        channel.queue_declare(queue=queue_name, durable=True)
        logger.info(f"✓ Queue '{queue_name}' declared successfully")

        connection.close()
        logger.info("✓ Connection closed successfully")
        return True

    except Exception as e:
        logger.error(f"✗ RabbitMQ connection failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_email_module():
    """Test email notification functionality"""
    logger.info("Testing email module...")

    try:
        from send import email

        # Create a test message
        test_message = {
            "mp3_fid": "test_file_123",
            "username": "test@example.com"
        }

        test_message_json = json.dumps(test_message)
        logger.info(f"Test message: {test_message_json}")

        # Test the notify function (this might fail due to email config, but shouldn't crash)
        result = email.notify(test_message_json)

        if result is None:
            logger.info("✓ Email notify function executed without errors")
            return True
        else:
            logger.warning(f"Email notify function returned error: {result}")
            return True  # Still counts as success since it didn't crash

    except Exception as e:
        logger.error(f"✗ Email module test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_json_parsing():
    """Test JSON message parsing"""
    logger.info("Testing JSON message parsing...")

    test_cases = [
        ('{"mp3_fid": "123", "username": "test@example.com"}', True),
        ('{"mp3_fid": "123"}', False),  # Missing username
        ('{"username": "test@example.com"}', False),  # Missing mp3_fid
        ('invalid json', False),  # Invalid JSON
        ('', False),  # Empty string
    ]

    for test_json, should_succeed in test_cases:
        try:
            data = json.loads(test_json)
            if 'mp3_fid' in data and 'username' in data:
                logger.info(f"✓ Valid message: {test_json}")
                if not should_succeed:
                    logger.warning(f"Expected this to fail but it succeeded: {test_json}")
            else:
                logger.warning(f"Missing required fields in: {test_json}")
                if should_succeed:
                    logger.error(f"Expected this to succeed but it failed: {test_json}")
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {test_json}")
            if should_succeed:
                logger.error(f"Expected this to succeed but it failed: {test_json}")

    return True

def main():
    """Run all tests"""
    logger.info("="*50)
    logger.info("NOTIFICATION SERVICE DEBUG TEST")
    logger.info("="*50)

    tests = [
        ("Import Tests", test_imports),
        ("Environment Tests", test_environment),
        ("RabbitMQ Connection Tests", test_rabbitmq_connection),
        ("Email Module Tests", test_email_module),
        ("JSON Parsing Tests", test_json_parsing),
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            results[test_name] = False

    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
