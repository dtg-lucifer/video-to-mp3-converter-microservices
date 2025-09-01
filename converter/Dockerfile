# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get update \
    && apt-get install -y \
    build-essential ffmpeg \
    && pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir --requirement requirements.txt

COPY consumer.py .
COPY convert/ ./convert/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["python3", "consumer.py"]
