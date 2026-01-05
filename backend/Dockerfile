FROM python:3.11

WORKDIR /app

# Install system dependencies for OpenCV and YOLO
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py analyze.py ./
COPY yolov8n.pt ./

# Expose Flask port
EXPOSE 8080

# Run the Flask application
CMD ["python", "app.py"]
