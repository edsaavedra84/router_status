# Use official Python runtime as base image (supports ARM for Raspberry Pi)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests

# Copy the application
COPY ../main.py .

# Create directory for logs
RUN mkdir -p /app/logs

# Set environment variable for log directory
ENV LOG_DIR=/app/logs

# Run the script with unbuffered output (-u flag for real-time logs)
CMD ["python", "-u", "main.py"]
