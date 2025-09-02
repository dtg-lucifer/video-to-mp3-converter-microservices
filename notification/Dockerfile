# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set work directory
WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
    build-essential ffmpeg \
    && pip install --no-cache-dir --upgrade pip

# Copy requirements first for better layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY consumer.py .
COPY send ./send

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["python3", "consumer.py"]
