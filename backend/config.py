"""Configuration for basketball tracker backend"""

import os

# VideoMAE settings
VIDEOMAE_MODEL_NAME = os.environ.get('VIDEOMAE_MODEL_NAME', 'MCG-NJU/videomae-base-finetuned-kinetics')

# YOLO settings
YOLO_MODEL_PATH = os.environ.get('YOLO_MODEL_PATH', 'yolov8n.pt')

# Video processing settings
CLIP_DURATION = float(os.environ.get('CLIP_DURATION', '2.0'))  # seconds
CLIP_OVERLAP = float(os.environ.get('CLIP_OVERLAP', '0.5'))  # 0.0 to 1.0
MAX_CLIPS = int(os.environ.get('MAX_CLIPS', '30'))

# Detection settings
DETECTIONS_DIR = os.environ.get('DETECTIONS_DIR', '/tmp/detections')

# Confidence thresholds
CONFIDENCE_THRESHOLD_SHOT = float(os.environ.get('CONFIDENCE_THRESHOLD_SHOT', '0.5'))
CONFIDENCE_THRESHOLD_ASSIST = float(os.environ.get('CONFIDENCE_THRESHOLD_ASSIST', '0.4'))
CONFIDENCE_THRESHOLD_BLOCK = float(os.environ.get('CONFIDENCE_THRESHOLD_BLOCK', '0.45'))
CONFIDENCE_THRESHOLD_DETECTION = float(os.environ.get('CONFIDENCE_THRESHOLD_DETECTION', '0.3'))
