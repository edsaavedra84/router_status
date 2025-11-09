# Use official Python runtime as base image (supports ARM for Raspberry Pi)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (tzdata for timezone support)
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy the application
COPY requirements.txt .
COPY main.py .

# Install Python dependencies
RUN pip install -r requirements.txt

# Create directory for logs
RUN mkdir -p /app/logs

# Set environment variable for log directory
ENV LOG_DIR=/app/logs

# Run the script with unbuffered output (-u flag for real-time logs)
CMD ["python", "-u", "main.py"]
