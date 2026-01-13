import cv2
from ultralytics import YOLO
import numpy as np
import logging
import os
import json
from datetime import datetime

from classification import VideoMAEClassifier, YOLOBallTrackingClassifier
import config

logger = logging.getLogger(__name__)

# Directory for storing detection frames
DETECTIONS_DIR = config.DETECTIONS_DIR
os.makedirs(DETECTIONS_DIR, exist_ok=True)

# Initialize YOLO for ball detection (still used separately)
yolo_model = YOLO(config.YOLO_MODEL_PATH)

# Lazy-load classifiers on first use
_videomae_classifier = None
_yolo_classifier = None


def get_classifier(classifier_type='videomae'):
    """
    Get classifier instance (lazy initialization)

    Args:
        classifier_type: 'videomae' or 'yolo'

    Returns:
        ActionClassifier instance
    """
    global _videomae_classifier, _yolo_classifier

    if classifier_type == 'yolo':
        if _yolo_classifier is None:
            logger.info("Initializing YOLO Ball Tracking classifier...")
            _yolo_classifier = YOLOBallTrackingClassifier(model_path=config.YOLO_MODEL_PATH)
            _yolo_classifier.initialize()
        return _yolo_classifier
    else:  # default to videomae
        if _videomae_classifier is None:
            logger.info("Initializing VideoMAE classifier...")
            _videomae_classifier = VideoMAEClassifier(model_name=config.VIDEOMAE_MODEL_NAME)
            _videomae_classifier.initialize()
        return _videomae_classifier


def extract_video_clips(video_path, clip_duration=None, overlap=None, max_clips=None):
    """Extract short clips from video for action recognition"""
    # Use config defaults if not specified
    if clip_duration is None:
        clip_duration = config.CLIP_DURATION
    if overlap is None:
        overlap = config.CLIP_OVERLAP
    if max_clips is None:
        max_clips = config.MAX_CLIPS

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


def analyze_video(video_path, classifier_type='videomae'):
    logger.info(f"Opening video file: {video_path}")
    logger.info(f"Using classifier: {classifier_type}")

    # Get the classifier
    classifier = get_classifier(classifier_type)
    if not classifier.is_ready():
        raise RuntimeError(f"Classifier {classifier_type} failed to initialize")

    try:
        logger.info("Extracting video clips for action recognition...")
        clips, fps = extract_video_clips(video_path)
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

    # Get basketball action mappings from the classifier
    basketball_actions = classifier.get_basketball_stats_mapping()

    detected_actions = []

    # Generate unique session ID for this analysis
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    for i, (start_frame, clip_frames) in enumerate(clips):
        # clip processing

        if i % 5 == 0:
            logger.info(f"Processing clip {i+1}/{len(clips)} (frame {start_frame})")

        # Classify the action using the selected classifier
        result = classifier.classify(clip_frames)
        action_label = result.action
        confidence = result.confidence

        if action_label and confidence > config.CONFIDENCE_THRESHOLD_DETECTION:
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
                if confidence > config.CONFIDENCE_THRESHOLD_SHOT:
                    stats['points'] += 2
                    classified_as.append('SHOT (+2 points)')
                    logger.info(f"  -> Counted as SHOT! Total points: {stats['points']}")

            # assists
            if any(keyword in action_lower for keyword in basketball_actions['passing']):
                if confidence > config.CONFIDENCE_THRESHOLD_ASSIST:
                    stats['assists'] += 1
                    classified_as.append('ASSIST (+1)')
                    logger.info(f"  -> Counted as ASSIST! Total assists: {stats['assists']}")

            # blocks
            if any(keyword in action_lower for keyword in basketball_actions['blocking']):
                if confidence > config.CONFIDENCE_THRESHOLD_BLOCK:
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
            'video_duration': round(len(clips) * config.CLIP_DURATION / fps, 2) if fps > 0 else 0,
            'total_detections': len(detection_details),
            'classifier_used': classifier.name,
            'classification_method': classifier_type,
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
