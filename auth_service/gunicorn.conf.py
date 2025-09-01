# Gunicorn configuration file for Kubernetes deployment
# Using single worker since Kubernetes handles horizontal scaling

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes - single worker for Kubernetes scaling
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload application for better performance with single worker
preload_app = True

# Graceful shutdown
graceful_timeout = 30
