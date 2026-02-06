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

# Pre-download ML models so they're cached in the image
RUN python -c "\
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification; \
VideoMAEImageProcessor.from_pretrained('MCG-NJU/videomae-base-finetuned-kinetics'); \
VideoMAEForVideoClassification.from_pretrained('MCG-NJU/videomae-base-finetuned-kinetics'); \
from transformers import CLIPProcessor, CLIPModel; \
CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32'); \
CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); \
from transformers import AutoImageProcessor, TimesformerForVideoClassification; \
AutoImageProcessor.from_pretrained('facebook/timesformer-base-finetuned-k400'); \
TimesformerForVideoClassification.from_pretrained('facebook/timesformer-base-finetuned-k400'); \
from transformers import VivitImageProcessor, VivitForVideoClassification; \
VivitImageProcessor.from_pretrained('google/vivit-b-16x2-kinetics400'); \
VivitForVideoClassification.from_pretrained('google/vivit-b-16x2-kinetics400'); \
"

# Copy application structure
COPY app.py ./
COPY services/ ./services/
COPY utils/ ./utils/

# Expose Flask port
EXPOSE 8080

# Run the Flask application
CMD ["python", "app.py"]
