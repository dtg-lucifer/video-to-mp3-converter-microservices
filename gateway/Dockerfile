# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY gunicorn.conf.py .
COPY auth/ ./auth/
COPY storage/ ./storage/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port (matching gunicorn config)
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "server:app"]
