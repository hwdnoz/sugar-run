FROM python:3.11-bookworm

WORKDIR /app

# Install system dependencies for OpenCV and YOLO
# Use --fix-missing to handle mirror issues
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends --fix-missing \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    || (apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    libgl1 \
    libglib2.0-0 \
    libgomp1) && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application structure
COPY app.py ./
COPY services/ ./services/
COPY utils/ ./utils/

# Expose Flask port
EXPOSE 8080

# Run the Flask application
CMD ["python", "app.py"]
