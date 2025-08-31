import os, gridfs, pika, json
from flask import Flask, request, jsonify, Response
from typing import Union, Tuple
from flask_pymongo import PyMongo
from auth import validate, access
from storage import util

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://piush:password@host.minikube.internal:27017/gateway_db")
app.config["RABBITMQ_HOST"] = os.getenv("RABBITMQ_HOST", "host.minikube.internal")
app.config["RABBITMQ_PORT"] = int(os.getenv("RABBITMQ_PORT", 5672))
app.config["RABBITMQ_USER"] = os.getenv("RABBITMQ_USER", "piush")
app.config["RABBITMQ_PASSWORD"] = os.getenv("RABBITMQ_PASSWORD", "password")

mongo = PyMongo(app)

if mongo.db == None:
    raise Exception("Could not connect to MongoDB")

fs = gridfs.GridFS(mongo.db)

# Initialize RabbitMQ connection and channel
try:
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=app.config["RABBITMQ_HOST"],
            port=app.config["RABBITMQ_PORT"],
            credentials=pika.PlainCredentials(
                app.config["RABBITMQ_USER"],
                app.config["RABBITMQ_PASSWORD"]
            ),
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
    token, err = access.login(request)

    if not err and token:
        return token, 200
    else:
        if err:
            return str(err[0]), err[1]
        else:
            return "Unknown error", 500

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

# Graceful shutdown
import atexit

def close_connections():
    if conn and not conn.is_closed:
        conn.close()
        print("RabbitMQ connection closed")

atexit.register(close_connections)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
