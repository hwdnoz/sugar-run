import cv2
from ultralytics import YOLO
import numpy as np
import logging
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification
import torch
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Directory for storing detection frames
DETECTIONS_DIR = '/tmp/detections'
os.makedirs(DETECTIONS_DIR, exist_ok=True)

yolo_model = YOLO('yolov8n.pt')

logger.info("Loading VideoMAE action recognition model...")
try:
    processor = VideoMAEImageProcessor.from_pretrained("MCG-NJU/videomae-base-finetuned-kinetics")
    action_model = VideoMAEForVideoClassification.from_pretrained("MCG-NJU/videomae-base-finetuned-kinetics")
    action_model.eval()
    logger.info("VideoMAE model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load VideoMAE: {e}")
    processor = None
    action_model = None


def extract_video_clips(video_path, clip_duration=2.0, overlap=0.5, max_clips=30):
    """Extract short clips from video for action recognition"""

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f"Video: {total_frames} frames at {fps:.2f} fps")

    frames_per_clip = int(fps * clip_duration)
    stride = int(frames_per_clip * (1 - overlap))

    clips = []
    frames_buffer = []
    frame_count = 0

    while cap.isOpened() and len(clips) < max_clips:
        ret, frame = cap.read()
        if not ret:
            break

        # bgr to rgb conversion
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames_buffer.append(frame_rgb)
        frame_count += 1

        if len(frames_buffer) == frames_per_clip:
            # enough frames for clip
            clips.append((frame_count - frames_per_clip, np.array(frames_buffer)))
            frames_buffer = frames_buffer[stride:] # move buffer forward by stride

            if len(clips) % 10 == 0:
                logger.info(f"Extracted {len(clips)} clips so far...")

    cap.release()
    logger.info(f"Total clips extracted: {len(clips)}")
    return clips, fps


def classify_action(frames):
    """Classify action in video clip using VideoMAE"""
    if processor is None or action_model is None:
        return None, 0.0

    try:
        # sampe 16 frames uniformly from clip
        indices = np.linspace(0, len(frames) - 1, 16, dtype=int)
        sampled_frames = [frames[i] for i in indices]

        inputs = processor(sampled_frames, return_tensors="pt") # processing frames

        with torch.no_grad():
            # getting predictions

            outputs = action_model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class_idx = logits.argmax(-1).item()
            confidence = probs[0][predicted_class_idx].item()

        predicted_label = action_model.config.id2label[predicted_class_idx]
        return predicted_label, confidence

    except Exception as e:
        logger.error(f"Error in action classification: {e}")
        return None, 0.0


def analyze_video(video_path):
    logger.info(f"Opening video file: {video_path}")

    try:
        logger.info("Extracting video clips for action recognition...")
        clips, fps = extract_video_clips(video_path, clip_duration=2.0, overlap=0.5)
        logger.info(f"Extracted {len(clips)} clips from video (FPS: {fps:.2f})")
    except Exception as e:
        logger.error(f"Failed to extract video clips: {e}", exc_info=True)
        raise

    stats = {
        'points': 0,
        'assists': 0,
        'steals': 0,
        'blocks': 0,
        'rebounds': 0
    }

    basketball_actions = {
        'shooting': ['shooting', 'throw', 'toss'],
        'passing': ['passing', 'hand', 'throw'],
        'dribbling': ['dribbling', 'bounce'],
        'dunking': ['dunk', 'slam'],
        'blocking': ['block', 'defend'],
        'catching': ['catch', 'grab']
    }

    detected_actions = []

    # Generate unique session ID for this analysis
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    for i, (start_frame, clip_frames) in enumerate(clips):
        # clip processing

        if i % 5 == 0:
            logger.info(f"Processing clip {i+1}/{len(clips)} (frame {start_frame})")

        action_label, confidence = classify_action(clip_frames)

        if action_label and confidence > 0.3:
            timestamp = start_frame / fps

            # Save the middle frame from this clip for debugging
            middle_frame_idx = len(clip_frames) // 2
            middle_frame = clip_frames[middle_frame_idx]

            # Save frame as image
            frame_filename = f"{session_id}_frame_{start_frame:04d}.jpg"
            frame_path = os.path.join(DETECTIONS_DIR, frame_filename)
            # Convert RGB back to BGR for cv2.imwrite
            middle_frame_bgr = cv2.cvtColor(middle_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(frame_path, middle_frame_bgr)

            detected_actions.append({
                'frame': start_frame,
                'timestamp': timestamp,
                'action': action_label,
                'confidence': confidence,
                'frame_image': frame_filename,
                'session_id': session_id
            })

            logger.info(f"Clip {i}: Detected '{action_label}' (confidence: {confidence:.2f}) at {timestamp:.2f}s")

            action_lower = action_label.lower()
            classified_as = []

            # shots
            if any(keyword in action_lower for keyword in basketball_actions['shooting'] + basketball_actions['dunking']):
                if confidence > 0.5:
                    stats['points'] += 2
                    classified_as.append('SHOT (+2 points)')
                    logger.info(f"  -> Counted as SHOT! Total points: {stats['points']}")

            # assists
            if any(keyword in action_lower for keyword in basketball_actions['passing']):
                if confidence > 0.4:
                    stats['assists'] += 1
                    classified_as.append('ASSIST (+1)')
                    logger.info(f"  -> Counted as ASSIST! Total assists: {stats['assists']}")

            # blocks
            if any(keyword in action_lower for keyword in basketball_actions['blocking']):
                if confidence > 0.45:
                    stats['blocks'] += 1
                    classified_as.append('BLOCK (+1)')
                    logger.info(f"  -> Counted as BLOCK! Total blocks: {stats['blocks']}")

            # Store classification result back to detection
            detected_actions[-1]['classified_as'] = ', '.join(classified_as) if classified_as else 'IGNORED (below threshold or no match)'

    # Build detection details with saved frame info
    detection_details = []
    for det in detected_actions:
        detection_details.append({
            'timestamp': round(det['timestamp'], 2),
            'frame': det['frame'],
            'detected_action': det['action'],
            'confidence': round(det['confidence'], 3),
            'classified_as': det['classified_as'],
            'frame_image': det['frame_image'],
            'session_id': det['session_id']
        })

    # Save detection metadata to JSON file
    metadata_file = os.path.join(DETECTIONS_DIR, f"{session_id}_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump({
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'video_duration': round(len(clips) * 2.0 / fps, 2) if fps > 0 else 0,
            'total_detections': len(detection_details),
            'stats': stats,
            'detections': detection_details
        }, f, indent=2)
    logger.info(f"Saved detection metadata to {metadata_file}")

    logger.info("Running YOLO ball detection for additional analysis...")
    ball_detections = detect_ball_with_yolo(video_path)
    logger.info(f"YOLO detected ball in {ball_detections} frames")

    logger.info(f"Video analysis complete. Detected {len(detected_actions)} action events")
    logger.info(f"Final stats: Points={stats['points']}, Assists={stats['assists']}, Steals={stats['steals']}, Blocks={stats['blocks']}, Rebounds={stats['rebounds']}")

    # Log detection timeline summary
    logger.info("\n" + "="*80)
    logger.info("DETECTION TIMELINE SUMMARY")
    logger.info("="*80)
    for det in detection_details:
        logger.info(f"  [{det['timestamp']:6.2f}s] Frame {det['frame']:4d} | {det['detected_action']:30s} | Confidence: {det['confidence']:.3f} | Result: {det['classified_as']}")
    logger.info("="*80 + "\n")

    # Add detection details to stats
    stats['detections'] = detection_details
    stats['session_id'] = session_id

    return stats


def detect_ball_with_yolo(video_path):
    """Use YOLO to detect basketball for validation"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    ball_count = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % 10 == 0: # every 10th frame for speed
            results = yolo_model(frame, verbose=False)

            for box in results[0].boxes:
                cls = int(box.cls[0])
                label = yolo_model.names[cls]

                if label == 'sports ball':
                    ball_count += 1
                    break

        frame_count += 1

    cap.release()
    return ball_count
