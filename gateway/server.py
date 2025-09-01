import os, gridfs, pika, json, logging
from flask import Flask, request, jsonify
from typing import Tuple
from flask_pymongo import PyMongo
from auth import validate, access
from storage import util

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://piush:password@host.minikube.internal:27017/gateway_db")
app.config["RABBITMQ_HOST"] = os.getenv("RABBITMQ_HOST", "rabbitmq")

mongo = PyMongo(app)

if mongo.db == None:
    raise Exception("Could not connect to MongoDB")

fs = gridfs.GridFS(mongo.db)

# Initialize RabbitMQ connection and channel
try:
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=app.config["RABBITMQ_HOST"],
            heartbeat=600,
            blocked_connection_timeout=300,
        )
    )
    channel = conn.channel()
    # Declare the queue to ensure it exists
    channel.queue_declare(queue='video', durable=True)
    print("Successfully connected to RabbitMQ")
except Exception as e:
    print(f"Failed to connect to RabbitMQ: {e}")
    # Initialize as None to handle gracefully
    conn = None
    channel = None

@app.route('/login', methods=['POST'])
def login() -> Tuple[str, int]:
    try:
        logger.info("Login attempt received")
        token, err = access.login(request)

        if not err and token:
            logger.info("Login successful")
            return token, 200
        else:
            if err:
                logger.error(f"Login failed: {err[0]} (status: {err[1]})")
                return str(err[0]), err[1]
            else:
                logger.error("Login failed with unknown error")
                return "Unknown error", 500
    except Exception as e:
        logger.error(f"Unexpected error in login route: {e}")
        return f"Internal server error: {str(e)}", 500

@app.route('/upload', methods=['POST'])
def upload():
    token, err = validate.token(request)
    access_data = json.loads(token) if token else None

    if err:
        return str(err[0]), err[1]

    if not access_data:
        return "Unknown error", 500

    # Check if RabbitMQ is available
    if not channel:
        return "Message queue service unavailable", 503

    if access_data["is_admin"]:
        if not len(request.files) == 1:
            return "Only one file is allowed", 400

        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access_data)

            if err:
                return str(err[0]), err[1]

        return "File uploaded successfully", 200
    else:
        return "Unauthorized", 403

@app.route("/download", methods=["GET"])
def download() -> Tuple[str, int]:
    return "Download endpoint not implemented", 501

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "mongodb": "connected" if not mongo.db == None else "disconnected",
        "rabbitmq": "connected" if channel else "disconnected"
    }
    return jsonify(status), 200

@app.route("/test-auth", methods=["GET"])
def test_auth():
    """Test auth service connectivity"""
    import requests
    auth_service_url = f"http://{os.environ.get('AUTH_SVC_ADDR')}/health"
    try:
        response = requests.get(auth_service_url, timeout=5)
        return jsonify({
            "auth_service_url": auth_service_url,
            "status_code": response.status_code,
            "response": response.text,
            "connectivity": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "auth_service_url": auth_service_url,
            "error": str(e),
            "connectivity": "failed"
        }), 500

# Graceful shutdown
import atexit

def close_connections():
    if conn and not conn.is_closed:
        conn.close()
        print("RabbitMQ connection closed")

atexit.register(close_connections)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
