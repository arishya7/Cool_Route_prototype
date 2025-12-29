# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Verify trees data file is present and not a pointer
RUN echo "Verifying trees data file in Docker image..." && \
    ls -lh data/trees_downloaded.csv && \
    head -n 2 data/trees_downloaded.csv || echo "Warning: Trees file not found or invalid"

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 simple_server:app
