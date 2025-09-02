# 🎬➡️🎵 Video to MP3 Converter Microservices

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-enabled-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-ready-green.svg)](https://kubernetes.io/)

A **production-ready**, **scalable microservices architecture** that converts video files to MP3 audio format using Python, Flask, MongoDB, MySQL, RabbitMQ, and Kubernetes. Built with modern DevOps practices and cloud-native principles.

---

## 🏗️ Architecture Overview

```mermaid
graph TB
    Client[Client/User] --> Gateway[Gateway Service]
    Gateway --> Auth[Auth Service]
    Gateway --> MongoDB[(MongoDB)]
    Gateway --> RabbitMQ{RabbitMQ}

    Auth --> MySQL[(MySQL)]
    RabbitMQ --> Converter[Converter Service]
    Converter --> MongoDB
    Converter --> RabbitMQ
    RabbitMQ --> Notification[Notification Service]

    subgraph "Kubernetes Cluster"
        Gateway
        Auth
        Converter
        Notification
        RabbitMQ
    end

    subgraph "External Databases"
        MongoDB
        MySQL
    end
```

### 🎯 Microservices Components

| Service          | Purpose                          | Technology              | Port        |
| ---------------- | -------------------------------- | ----------------------- | ----------- |
| **Gateway**      | API Gateway & File Upload        | Flask, MongoDB          | 8000        |
| **Auth**         | Authentication & Authorization   | Flask, MySQL, JWT       | 5000        |
| **Converter**    | Video-to-MP3 Processing          | Python, FFmpeg, MoviePy | -           |
| **Notification** | Email Notifications              | Python, SMTP            | -           |
| **RabbitMQ**     | Message Queue & Async Processing | RabbitMQ                | 5672, 15672 |

---

## ✨ Features

- 🔐 **JWT-based Authentication** - Secure user authentication and authorization
- 📁 **File Upload & Storage** - GridFS-based video file storage with MongoDB
- ⚡ **Async Processing** - RabbitMQ for decoupled video conversion
- 📧 **Email Notifications** - Automated notifications when conversion completes
- 🔄 **Health Monitoring** - Built-in health check endpoints
- 🐳 **Containerized** - Docker containers for all services
- ☸️ **Kubernetes-ready** - Complete K8s manifests for production deployment
- 📊 **Scalable** - Horizontal scaling support
- 🛡️ **Production-ready** - Error handling, logging, and monitoring

---

## 🛠️ Technology Stack

### Backend

- **Python 3.13** - Core programming language
- **Flask** - Lightweight web framework
- **Gunicorn** - Production WSGI server

### Databases

- **MongoDB** - GridFS for large file storage
- **MySQL 8.0** - User authentication and metadata

### Message Queue

- **RabbitMQ 3.12** - Reliable message broker

### Processing

- **FFmpeg** - Video/audio processing engine
- **MoviePy** - Python video editing library

### DevOps & Deployment

- **Docker** - Application containerization
- **Kubernetes** - Container orchestration
- **Minikube** - Local Kubernetes development

---

## 🚀 Quick Start Guide

### Prerequisites

Make sure you have the following installed:

- ✅ **Docker** (v20.0+)
- ✅ **Kubernetes** (kubectl)
- ✅ **Minikube** (for local development)
- ✅ **Git**

### 🎯 Step-by-Step Deployment

#### 1️⃣ Start Minikube Cluster

```bash
# Start minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
```

#### 2️⃣ Clone the Repository

```bash
git clone <repository-url>
cd python-video-to-audio-microservices
```

#### 3️⃣ Setup External Databases

Start MySQL and MongoDB on your host machine (accessible via `host.minikube.internal`):

```bash
# Start databases with Docker Compose
docker-compose up -d

# Verify databases are running
docker ps
```

**Expected Output:**

```
CONTAINER ID   IMAGE     COMMAND                  STATUS         PORTS                    NAMES
xxxxx          mysql:8.0    "docker-entrypoint.s…"   Up 30 seconds   0.0.0.0:3306->3306/tcp   mysql_db
xxxxx          mongo:7.0    "docker-entrypoint.s…"   Up 30 seconds   0.0.0.0:27017->27017/tcp mongodb
```

#### 4️⃣ Deploy Kubernetes Resources (In Order)

> **⚠️ Important:** Deploy services in the following chronological order to ensure proper dependencies.

##### **Step 4.1: Deploy RabbitMQ (Message Broker)**

```bash
# Deploy RabbitMQ StatefulSet and Services
kubectl apply -f gateway/rabbitmq/manifests/

# Wait for RabbitMQ to be ready
kubectl wait --for=condition=ready pod -l app=rabbitmq --timeout=300s

# Verify RabbitMQ is running
kubectl get pods -l app=rabbitmq
```

##### **Step 4.2: Deploy Auth Service**

```bash
# Apply auth service manifests
kubectl apply -f auth_service/manifests/

# Wait for deployment to be ready
kubectl wait --for=condition=available deployment/auth-service --timeout=300s

# Verify auth service
kubectl get pods -l app=auth-service
```

##### **Step 4.3: Deploy Gateway Service**

```bash
# Apply gateway service manifests
kubectl apply -f gateway/manifests/

# Wait for deployment to be ready
kubectl wait --for=condition=available deployment/gateway --timeout=300s

# Verify gateway service
kubectl get pods -l app=gateway
```

##### **Step 4.4: Deploy Converter Service**

```bash
# Apply converter service manifests
kubectl apply -f converter/manifests/

# Wait for deployment to be ready
kubectl wait --for=condition=available deployment/converter --timeout=300s

# Verify converter service
kubectl get pods -l app=converter
```

##### **Step 4.5: Deploy Notification Service**

```bash
# Apply notification service manifests
kubectl apply -f notification/manifests/

# Wait for deployment to be ready
kubectl wait --for=condition=available deployment/notification --timeout=300s

# Verify notification service
kubectl get pods -l app=notification
```

#### 5️⃣ Verify Complete Deployment

```bash
# Check all pods are running
kubectl get pods

# Check all services
kubectl get services

# Check ingress
kubectl get ingress
```

**Expected Output:**

```
NAME                              READY   STATUS    RESTARTS   AGE
auth-service-xxx                  1/1     Running   0          5m
converter-xxx                     1/1     Running   0          3m
gateway-xxx                       1/1     Running   0          4m
notification-xxx                  1/1     Running   0          2m
rabbitmq-0                        1/1     Running   0          6m
```

#### 6️⃣ Setup Port Forwarding for Testing

```bash
# Forward gateway service to localhost:8000
kubectl port-forward service/gateway 8000:8000 &

# Forward auth service to localhost:5000
kubectl port-forward service/auth-service 5000:5000 &

# Forward RabbitMQ management UI to localhost:15672
kubectl port-forward service/rabbitmq 15672:15672 &
```

---

## 🧪 Testing the Complete Workflow

### 🔐 Step 1: User Authentication

#### Login to Get JWT Token

```bash
# Login with test credentials
curl -X POST http://localhost:5000/login \
  -u "piush@gmail.com:password" \
  -H "Content-Type: application/json" \
  -v

# Expected Response:
# {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
# }
```

**💡 Save the token for subsequent requests:**

```bash
export JWT_TOKEN="your_jwt_token_here"
```

#### Verify Authentication

```bash
# Test token validation
curl -X GET http://localhost:5000/validate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -v
```

### 📤 Step 2: Video Upload

Create a test video file or use an existing one:

```bash
# Upload video file for conversion
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@/path/to/your/video.mp4" \
  -v

# Expected Response:
# {
#   "message": "success",
#   "video_fid": "64a7b8c9d1e2f3a4b5c6d7e8"
# }
```

**💡 Save the video file ID:**

```bash
export VIDEO_FID="your_video_fid_here"
```

### 📥 Step 3: Download Converted MP3

```bash
# Check if conversion is complete and download MP3
curl -X GET "http://localhost:8000/download?fid=$VIDEO_FID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -O -J \
  -v

# This will download the converted MP3 file
```

### 🔍 Step 4: Monitor Processing

#### Check RabbitMQ Management UI

```bash
# Open RabbitMQ Management in browser
open http://localhost:15672

# Default credentials:
# Username: guest
# Password: guest
```

#### Check Service Logs

```bash
# View converter logs
kubectl logs -l app=converter -f

# View notification logs
kubectl logs -l app=notification -f

# View gateway logs
kubectl logs -l app=gateway -f
```

#### Health Checks

```bash
# Check all service health
curl http://localhost:8000/health
curl http://localhost:5000/health
```

---

## 📋 API Reference

### 🔐 Authentication Service (Port 5000)

| Method | Endpoint    | Description          | Auth Required | Request Body |
| ------ | ----------- | -------------------- | ------------- | ------------ |
| `POST` | `/login`    | User authentication  | Basic Auth    | -            |
| `GET`  | `/validate` | Validate JWT token   | Bearer Token  | -            |
| `GET`  | `/health`   | Service health check | None          | -            |

#### Login Example

```bash
curl -X POST http://localhost:5000/login \
  -u "piush@gmail.com:password"
```

### 🌐 Gateway Service (Port 8000)

| Method | Endpoint    | Description           | Auth Required | Request Body              |
| ------ | ----------- | --------------------- | ------------- | ------------------------- |
| `POST` | `/login`    | Proxy to auth service | Basic Auth    | -                         |
| `POST` | `/upload`   | Upload video file     | Bearer Token  | `multipart/form-data`     |
| `GET`  | `/download` | Download MP3 file     | Bearer Token  | Query: `?fid=<video_fid>` |
| `GET`  | `/health`   | Service health check  | None          | -                         |

#### Upload Example

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@video.mp4"
```

#### Download Example

```bash
curl -X GET "http://localhost:8000/download?fid=VIDEO_FILE_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -O -J
```

---

## 📊 Monitoring & Observability

### Health Endpoints

All services provide health check endpoints:

```bash
# Gateway health
curl http://localhost:8000/health

# Auth service health
curl http://localhost:5000/health
```

### Service Logs

```bash
# Real-time logs for all services
kubectl logs -l app=gateway -f
kubectl logs -l app=auth-service -f
kubectl logs -l app=converter -f
kubectl logs -l app=notification -f
```

### Resource Monitoring

```bash
# Pod resource usage
kubectl top pods

# Node resource usage
kubectl top nodes

# Detailed pod information
kubectl describe pod <pod-name>
```

---

## 🔧 Configuration

### Environment Variables

#### Gateway Service

- `MONGO_HOST` - MongoDB host (default: host.minikube.internal)
- `MONGO_PORT` - MongoDB port (default: 27017)
- `RABBITMQ_HOST` - RabbitMQ host (default: rabbitmq)
- `AUTH_SVC_ADDR` - Auth service address
- `MAX_CONTENT_LENGTH` - Max upload size (default: 100MB)

#### Auth Service

- `MYSQL_HOST` - MySQL host (default: host.minikube.internal)
- `MYSQL_USER` - MySQL username
- `MYSQL_PASSWORD` - MySQL password
- `SECRET_KEY` - JWT signing secret

#### Notification Service

- `GMAIL_ADDRESS` - SMTP email address
- `GMAIL_PASSWORD` - SMTP app password
- `MP3_QUEUE` - RabbitMQ queue name (default: mp3)

### Scaling Services

```bash
# Scale gateway service
kubectl scale deployment gateway --replicas=3

# Scale converter service for heavy processing
kubectl scale deployment converter --replicas=5

# Scale notification service
kubectl scale deployment notification --replicas=2
```

---

## 🗂️ Project Structure

```
python-video-to-audio-microservices/
├── 🔐 auth_service/                 # Authentication microservice
│   ├── manifests/                   # Kubernetes manifests
│   │   ├── configmap.yaml          # Environment configuration
│   │   ├── deployment.yaml         # Deployment specification
│   │   ├── secret.yaml             # Sensitive data
│   │   └── service.yaml            # Service definition
│   ├── Dockerfile                  # Container image definition
│   ├── server.py                   # Flask application
│   ├── requirements.txt            # Python dependencies
│   ├── init.sql                    # Database initialization
│   └── gunicorn.conf.py           # Production server config
├── 🌐 gateway/                      # API Gateway microservice
│   ├── auth/                       # Authentication utilities
│   │   ├── access.py              # Login functionality
│   │   └── validate.py            # JWT token validation
│   ├── storage/                    # File storage utilities
│   │   └── util.py                # GridFS upload/download
│   ├── manifests/                  # Kubernetes manifests
│   │   ├── config.yaml            # Configuration
│   │   ├── deployment.yaml        # Deployment spec
│   │   ├── ingress.yaml           # Ingress rules
│   │   └── service.yaml           # Service definition
│   ├── rabbitmq/                   # RabbitMQ deployment
│   │   └── manifests/             # RabbitMQ K8s manifests
│   ├── Dockerfile                  # Container definition
│   ├── server.py                   # Flask application
│   └── requirements.txt            # Dependencies
├── 🔄 converter/                    # Video conversion service
│   ├── convert/                    # Conversion utilities
│   │   └── to_mp3.py              # Video-to-MP3 logic
│   ├── manifests/                  # Kubernetes manifests
│   ├── consumer.py                 # RabbitMQ consumer
│   ├── Dockerfile                  # Container definition
│   └── requirements.txt            # Dependencies
├── 📧 notification/                 # Notification service
│   ├── send/                       # Email utilities
│   │   └── email.py               # SMTP email sending
│   ├── manifests/                  # Kubernetes manifests
│   ├── consumer.py                 # RabbitMQ consumer
│   ├── Dockerfile                  # Container definition
│   └── requirements.txt            # Dependencies
├── 🐳 docker-compose.yml           # Local development setup
├── 📋 Makefile                     # Build automation
└── 📖 README.md                    # This documentation
```

---

## 🛠️ Development Guide

### Local Development Setup

1. **Install Dependencies**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for each service
cd auth_service && pip install -r requirements.txt && cd ..
cd gateway && pip install -r requirements.txt && cd ..
cd converter && pip install -r requirements.txt && cd ..
cd notification && pip install -r requirements.txt && cd ..
```

2. **Environment Setup**

```bash
# Set required environment variables
export MYSQL_HOST=localhost
export MYSQL_USER=piush
export MYSQL_PASSWORD=password
export MYSQL_DB=auth_db
export SECRET_KEY=your_secret_key_here
export MONGO_URI=mongodb://piush:password@localhost:27017/gateway_db
```

3. **Run Services Locally**

```bash
# Terminal 1 - Auth Service
cd auth_service && python server.py

# Terminal 2 - Gateway Service
cd gateway && python server.py

# Terminal 3 - Converter Service
cd converter && python consumer.py

# Terminal 4 - Notification Service
cd notification && python consumer.py
```

### Building Docker Images

```bash
# Build all images with minikube docker environment
eval $(minikube docker-env)

# Build auth service
cd auth_service && docker build -t devpiush/python-microservice-auth:latest .

# Build gateway service
cd gateway && docker build -t devpiush/python-microservice-gateway:latest .

# Build converter service
cd converter && docker build -t devpiush/python-microservice-converter:latest .

# Build notification service
cd notification && docker build -t devpiush/python-microservice-notification:latest .
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 🔍 **Pods in CrashLoopBackOff**

```bash
# Check pod logs for errors
kubectl logs <pod-name> --previous

# Describe pod for detailed status
kubectl describe pod <pod-name>

# Check resource constraints
kubectl top pods
```

#### 🔍 **Database Connection Issues**

```bash
# Verify databases are accessible from minikube
kubectl run debug --image=busybox --rm -it --restart=Never -- sh
nslookup host.minikube.internal
```

#### 🔍 **RabbitMQ Connection Problems**

```bash
# Check RabbitMQ service and pod status
kubectl get pods -l app=rabbitmq
kubectl get svc rabbitmq

# Access RabbitMQ management UI
kubectl port-forward service/rabbitmq 15672:15672
```

#### 🔍 **File Upload Failures**

```bash
# Check gateway logs
kubectl logs -l app=gateway -f

# Verify MongoDB connection
kubectl exec -it <gateway-pod> -- python -c "import pymongo; print('MongoDB OK')"
```

#### 🔍 **Email Notifications Not Working**

```bash
# Check notification service logs
kubectl logs -l app=notification -f

# Verify SMTP credentials in secret
kubectl get secret notification-secret -o yaml
```

### Debug Commands

```bash
# Get all resources
kubectl get all

# Check ingress status
kubectl get ingress

# Port forward for debugging
kubectl port-forward <pod-name> <local-port>:<pod-port>

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

## 🔒 Security Considerations

### Production Recommendations

- 🔐 **Change Default Credentials** - Update all default passwords
- 🔑 **Secure JWT Secret** - Use strong, randomly generated secret keys
- 🛡️ **Network Policies** - Implement Kubernetes network policies
- 🔒 **TLS/SSL** - Enable HTTPS for all external endpoints
- 👥 **RBAC** - Configure Kubernetes role-based access control
- 📊 **Monitoring** - Set up comprehensive logging and monitoring
- 🔄 **Backup** - Regular database backups
- 🚫 **Resource Limits** - Set appropriate CPU/memory limits

---

## 📈 Performance Optimization

### Scaling Guidelines

```bash
# Scale based on load
kubectl scale deployment gateway --replicas=5      # API load
kubectl scale deployment converter --replicas=10   # CPU-intensive tasks
kubectl scale deployment notification --replicas=3 # I/O operations
```

### Resource Requests & Limits

Update deployment manifests with appropriate resource specifications:

```yaml
resources:
    requests:
        memory: "256Mi"
        cpu: "250m"
    limits:
        memory: "512Mi"
        cpu: "500m"
```

---

## 🎯 Future Enhancements

- [ ] **Multi-format Support** - Support for various audio formats (WAV, FLAC, etc.)
- [ ] **Progress Tracking** - Real-time conversion progress updates
- [ ] **Batch Processing** - Multiple file conversion support
- [ ] **Quality Selection** - Different quality/bitrate options
- [ ] **Metrics Dashboard** - Prometheus + Grafana monitoring
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **Rate Limiting** - API rate limiting and throttling
- [ ] **File Validation** - Enhanced file type and size validation
- [ ] **Webhook Support** - Callback URLs for completion notifications
- [ ] **Admin Dashboard** - Web UI for system administration

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code style
- Add comprehensive tests for new features
- Update documentation for any API changes
- Use conventional commit messages

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors & Acknowledgments

- **Development Team** - Initial work and architecture
- **Contributors** - See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of contributors
- **Community** - Thanks to the open-source community for inspiration

---

## 📞 Support

### Getting Help

- 🐛 **Bug Reports** - [Create an issue](https://github.com/your-repo/issues)
- 💡 **Feature Requests** - [Open a discussion](https://github.com/your-repo/discussions)
- 📧 **Email Support** - support@yourproject.com
- 💬 **Community Chat** - [Join our Discord](https://discord.gg/yourproject)

### FAQ

**Q: What video formats are supported?**
A: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V

**Q: What's the maximum file size?**
A: Default limit is 100MB, configurable via `MAX_CONTENT_LENGTH`

**Q: How long does conversion take?**
A: Depends on file size and server resources, typically 1-5 minutes

**Q: Can I self-host this?**
A: Yes! Follow the Kubernetes deployment guide for production setup

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

[🏠 Home](README.md) • [📖 Documentation](docs/) • [🐛 Issues](issues/) • [💬 Discussions](discussions/)

---

_Built with ❤️ using Python, Kubernetes, and modern DevOps practices_

</div>
