# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Build arguments with defaults
ARG STREAMLIT_PORT=8501
ARG STREAMLIT_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for .env file (user will mount or provide)
RUN mkdir -p /app/config

# Expose Streamlit port (can be overridden at runtime)
EXPOSE ${STREAMLIT_PORT}

# Health check
HEALTHCHECK CMD curl --fail http://localhost:${STREAMLIT_PORT}/_stcore/health || exit 1

# Set Streamlit configuration (can be overridden at runtime via environment variables)
ENV STREAMLIT_SERVER_PORT=${STREAMLIT_PORT} \
    STREAMLIT_SERVER_ADDRESS=${STREAMLIT_ADDRESS} \
    STREAMLIT_SERVER_HEADLESS=true

# Run the Streamlit application
CMD ["streamlit", "run", "app.py"]
