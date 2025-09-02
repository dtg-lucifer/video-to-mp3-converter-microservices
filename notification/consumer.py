import pika, sys, os, time, json
import logging
from send import email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_rabbitmq(host, max_retries=30, delay=2):
    """Wait for RabbitMQ to be available with retries"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to RabbitMQ at {host} (attempt {attempt + 1}/{max_retries})")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    connection_attempts=3,
                    retry_delay=1
                )
            )
            connection.close()
            logger.info("Successfully connected to RabbitMQ")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Max retries reached. RabbitMQ is not available.")
                return False
    return False

def setup_queue(channel, queue_name):
    """Setup queue with proper error handling"""
    try:
        channel.queue_declare(queue=queue_name, durable=True)
        logger.info(f"Queue '{queue_name}' declared successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to declare queue '{queue_name}': {e}")
        return False

def callback(ch, method, properties, body):
    """Process incoming messages with proper error handling"""
    try:
        logger.info(f"Received message: {body}")

        # Validate message format
        try:
            message_data = json.loads(body)
            logger.info(f"Parsed message: {message_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Validate required fields - handle both username and user_email
        if 'mp3_fid' not in message_data:
            logger.error("Missing required field 'mp3_fid' in message")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Check for either username or user_email
        if 'username' not in message_data and 'user_email' not in message_data:
            logger.error("Missing email field - neither 'username' nor 'user_email' found in message")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Attempt to send email notification
        try:
            err = email.notify(body)
            if err:
                logger.error(f"Email notification failed: {err}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                logger.info("Email notification sent successfully")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Exception during email notification: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    except Exception as e:
        logger.error(f"Unexpected error in callback: {e}")
        try:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except:
            logger.error("Failed to nack message")

def main():
    # Log startup information
    logger.info("Starting notification service...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Environment variables:")
    logger.info(f"  MP3_QUEUE: {os.environ.get('MP3_QUEUE', 'mp3')}")
    logger.info(f"  GMAIL_ADDRESS: {os.environ.get('GMAIL_ADDRESS', 'Not set')}")
    logger.info(f"  GMAIL_PASSWORD: {'Set' if os.environ.get('GMAIL_PASSWORD') else 'Not set'}")

    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    queue_name = os.environ.get("MP3_QUEUE", "mp3")

    logger.info(f"Configured RabbitMQ host: {rabbitmq_host}")
    logger.info(f"Configured queue name: {queue_name}")

    # Wait for RabbitMQ to be available
    if not wait_for_rabbitmq(rabbitmq_host):
        logger.error("Cannot connect to RabbitMQ. Exiting.")
        sys.exit(1)

    connection = None
    channel = None

    try:
        # Establish connection
        logger.info("Establishing RabbitMQ connection...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_host,
                connection_attempts=5,
                retry_delay=2,
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        channel = connection.channel()
        logger.info("RabbitMQ connection established")

        # Setup queue
        if not setup_queue(channel, queue_name):
            logger.error("Failed to setup queue. Exiting.")
            sys.exit(1)

        # Configure QoS
        channel.basic_qos(prefetch_count=1)
        logger.info("QoS configured: prefetch_count=1")

        # Setup consumer
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback
        )

        logger.info(f"Waiting for messages on queue '{queue_name}'. To exit press CTRL+C")

        # Start consuming
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Stopping consumer...")
            channel.stop_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"AMQP Connection Error: {e}")
        sys.exit(1)
    except pika.exceptions.AMQPChannelError as e:
        logger.error(f"AMQP Channel Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            if channel and not channel.is_closed:
                channel.close()
                logger.info("Channel closed")
            if connection and not connection.is_closed:
                connection.close()
                logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
