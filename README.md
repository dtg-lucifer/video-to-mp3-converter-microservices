# Video to MP3 Converter Microservices

A scalable microservices-based application that converts video files to MP3 audio format using Python, Flask, MongoDB, MySQL, RabbitMQ, and Kubernetes.

## 🏗️ Architecture Overview

This project implements a distributed microservices architecture with the following components:

- **Gateway Service**: Main entry point for file uploads and API requests
- **Auth Service**: User authentication and authorization using JWT tokens
- **MongoDB**: GridFS storage for video and audio files
- **MySQL**: User credentials and authentication data
- **RabbitMQ**: Message queue for asynchronous video processing
- **Kubernetes**: Container orchestration and deployment

## 📋 Features

- ✅ User authentication with JWT tokens
- ✅ Secure file upload via REST API
- ✅ Video file storage using MongoDB GridFS
- ✅ Asynchronous processing with RabbitMQ
- ✅ Microservices architecture
- ✅ Kubernetes deployment
- ✅ Health check endpoints
- ✅ Docker containerization

## 🛠️ Tech Stack

### Backend

- **Python 3.x** - Core programming language
- **Flask** - Web framework
- **Gunicorn** - WSGI HTTP Server

### Databases

- **MongoDB** - GridFS for file storage
- **MySQL 8.0** - User authentication data

### Message Queue

- **RabbitMQ 3.12** - Asynchronous message processing

### Deployment

- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **Docker Compose** - Local development

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (minikube for local development)
- Python 3.x (for local development)

### Local Development with Docker Compose

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd python-video-to-audio-microservices
    ```

2. **Start the infrastructure services**

    ```bash
    docker-compose up -d
    ```

    This will start:
    - MySQL database on port 3306
    - MongoDB on port 27017
    - RabbitMQ on ports 5672 (AMQP) and 15672 (Management UI)

3. **Build and run the auth service**

    ```bash
    make build-auth
    make run-auth
    ```

4. **Build and run the gateway service**
    ```bash
    cd gateway
    docker build -t gateway .
    docker run -p 8000:8000 \
      -e MONGO_URI=mongodb://piush:password@localhost:27017/gateway_db \
      -e RABBITMQ_HOST=localhost \
      -e RABBITMQ_USER=piush \
      -e RABBITMQ_PASSWORD=password \
      gateway:latest
    ```

### Kubernetes Deployment

1. **Deploy the auth service**

    ```bash
    kubectl apply -f auth_service/manifests/
    ```

2. **Deploy the gateway service**
    ```bash
    kubectl apply -f gateway/manifests/
    ```

## 📁 Project Structure

```
python-video-to-audio-microservices/
├── auth_service/                 # Authentication microservice
│   ├── manifests/               # Kubernetes deployment files
│   │   ├── configmap.yaml
│   │   ├── deployment.yaml
│   │   ├── secrets_demo.yaml
│   │   └── sevice.yaml
│   ├── Dockerfile              # Docker configuration
│   ├── server.py               # Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── init.sql               # Database initialization
│   └── gunicorn.conf.py       # Gunicorn configuration
├── gateway/                     # API Gateway microservice
│   ├── auth/                   # Authentication utilities
│   │   ├── access.py          # Login functionality
│   │   └── validate.py        # Token validation
│   ├── storage/               # Storage utilities
│   │   └── util.py           # File upload utilities
│   ├── manifests/            # Kubernetes deployment files
│   │   ├── config.yaml
│   │   ├── deployment.yaml
│   │   ├── ingress.yaml
│   │   └── service.yaml
│   ├── Dockerfile           # Docker configuration
│   ├── server.py           # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── gunicorn.conf.py   # Gunicorn configuration
├── docker-compose.yml     # Local development setup
├── Makefile              # Build automation
└── README.md            # Project documentation
```

## 🔧 API Endpoints

### Authentication Service (Port 5000)

| Method | Endpoint  | Description   | Authentication |
| ------ | --------- | ------------- | -------------- |
| POST   | `/login`  | User login    | Basic Auth     |
| GET    | `/me`     | Get user info | Bearer Token   |
| GET    | `/health` | Health check  | None           |

### Gateway Service (Port 8000)

| Method | Endpoint    | Description           | Authentication |
| ------ | ----------- | --------------------- | -------------- |
| POST   | `/login`    | Proxy to auth service | Basic Auth     |
| POST   | `/upload`   | Upload video file     | Bearer Token   |
| GET    | `/download` | Download MP3 file     | Bearer Token   |
| GET    | `/health`   | Health check          | None           |

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for authentication:

1. **Login**: Send POST request to `/login` with Basic Auth credentials
2. **Token**: Receive JWT token in response
3. **API Calls**: Include token in `Authorization: Bearer <token>` header

### Example Login Request

```bash
curl -X POST http://localhost:5000/login \
  -u "user@example.com:password" \
  -H "Content-Type: application/json"
```

## 📤 File Upload

Upload video files for conversion to MP3:

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@video.mp4"
```

## 🗄️ Database Schema

### MySQL (Auth Service)

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
```

### MongoDB (Gateway Service)

- **GridFS**: Stores video and audio files
- **Collections**: Automatically managed by GridFS

## 🔄 Message Queue

RabbitMQ is used for asynchronous processing:

- **Queue**: `video` (durable)
- **Message Format**:
    ```json
    {
        "video_fid": "mongodb_file_id",
        "mp3_fid": null,
        "user_email": "user@example.com"
    }
    ```

## 🐳 Docker Configuration

### Environment Variables

#### Auth Service

- `MYSQL_HOST`: MySQL host (default: localhost)
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DB`: Database name
- `SECRET_KEY`: JWT secret key

#### Gateway Service

- `MONGO_URI`: MongoDB connection string
- `RABBITMQ_HOST`: RabbitMQ host
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USER`: RabbitMQ username
- `RABBITMQ_PASSWORD`: RabbitMQ password

## ☸️ Kubernetes Deployment

The application is designed for Kubernetes deployment with:

- **ConfigMaps**: Environment configuration
- **Secrets**: Sensitive data (passwords, keys)
- **Deployments**: Service replicas and rolling updates
- **Services**: Internal service discovery
- **Ingress**: External traffic routing

### Scaling

Scale services based on load:

```bash
kubectl scale deployment gateway --replicas=5
kubectl scale deployment auth-service --replicas=3
```

## 🏥 Health Monitoring

Health check endpoints are available for monitoring:

- Auth Service: `GET /health`
- Gateway Service: `GET /health`

Example health check response:

```json
{
    "status": "healthy",
    "mongodb": "connected",
    "rabbitmq": "connected"
}
```

## 🔧 Development

### Local Setup

1. **Install dependencies**

    ```bash
    cd auth_service
    pip install -r requirements.txt

    cd ../gateway
    pip install -r requirements.txt
    ```

2. **Set environment variables**

    ```bash
    export MYSQL_HOST=localhost
    export MYSQL_USER=piush
    export MYSQL_PASSWORD=password
    export MYSQL_DB=auth_db
    export SECRET_KEY=your_secret_key
    ```

3. **Run services**

    ```bash
    # Terminal 1 - Auth Service
    cd auth_service
    python server.py

    # Terminal 2 - Gateway Service
    cd gateway
    python server.py
    ```

### Testing

Test the services using curl or any HTTP client:

```bash
# Health checks
curl http://localhost:5000/health
curl http://localhost:8000/health

# Authentication
curl -X POST http://localhost:5000/login -u "user@example.com:password"
```

## 🚧 Future Enhancements

- [ ] Converter service implementation for actual video-to-MP3 processing
- [ ] Download endpoint implementation
- [ ] File format validation
- [ ] Processing status tracking
- [ ] Rate limiting
- [ ] Metrics and logging
- [ ] Automated testing
- [ ] CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:

- Create an issue in the repository
- Contact the development team

---

**Note**: This is a demonstration project for microservices architecture. For production use, implement additional security measures, error handling, and monitoring.
