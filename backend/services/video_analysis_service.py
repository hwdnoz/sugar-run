"""Analysis orchestrator - coordinates video processing, classification, and stats"""
import cv2
import logging
from datetime import datetime

from services.classifiers import (
    VideoMAEClassifier,
    YOLOBallTrackingClassifier,
    TimesFormerClassifier,
    X3DClassifier,
    CLIPZeroShotClassifier,
    ViViTClassifier,
    SlowFastClassifier
)
from services import video_extraction_service, stats_calculation_service
from utils import config, storage

logger = logging.getLogger(__name__)

class ClassifierFactory:
    """Simple Factory for creating classifier instances (lazy initialization)"""

    _videomae = None
    _yolo = None
    _timesformer = None
    _x3d = None
    _clip = None
    _vivit = None
    _slowfast = None

    @classmethod
    def create(cls, classifier_type='videomae'):
        """Create or return cached classifier instance"""
        if classifier_type == 'yolo':
            if cls._yolo is None:
                logger.info("Initializing YOLO Ball Tracking classifier...")
                cls._yolo = YOLOBallTrackingClassifier(model_path=config.YOLO_MODEL_PATH)
                cls._yolo.initialize()
            return cls._yolo
        elif classifier_type == 'timesformer':
            if cls._timesformer is None:
                logger.info("Initializing TimesFormer classifier...")
                cls._timesformer = TimesFormerClassifier()
                cls._timesformer.initialize()
            return cls._timesformer
        elif classifier_type == 'x3d':
            if cls._x3d is None:
                logger.info("Initializing X3D classifier...")
                cls._x3d = X3DClassifier()
                cls._x3d.initialize()
            return cls._x3d
        elif classifier_type == 'clip':
            if cls._clip is None:
                logger.info("Initializing CLIP Zero-Shot classifier...")
                cls._clip = CLIPZeroShotClassifier()
                cls._clip.initialize()
            return cls._clip
        elif classifier_type == 'vivit':
            if cls._vivit is None:
                logger.info("Initializing ViViT classifier...")
                cls._vivit = ViViTClassifier()
                cls._vivit.initialize()
            return cls._vivit
        elif classifier_type == 'slowfast':
            if cls._slowfast is None:
                logger.info("Initializing SlowFast classifier...")
                cls._slowfast = SlowFastClassifier()
                cls._slowfast.initialize()
            return cls._slowfast
        else:  # default to videomae
            if cls._videomae is None:
                logger.info("Initializing VideoMAE classifier...")
                cls._videomae = VideoMAEClassifier(model_name=config.VIDEOMAE_MODEL_NAME)
                cls._videomae.initialize()
            return cls._videomae


def analyze_video(video_path, classifier_type='videomae'):
    """
    Orchestrate video analysis pipeline

    Steps:
    1. Extract clips from video
    2. Classify each clip
    3. Calculate basketball stats
    4. Save results
    """
    logger.info(f"Opening video file: {video_path}")
    logger.info(f"Using classifier: {classifier_type}")

    # Create classifier with factory
    classifier = ClassifierFactory.create(classifier_type)
    if not classifier.is_ready():
        raise RuntimeError(f"Classifier {classifier_type} failed to initialize")

    # Extract video clips
    logger.info("Extracting video clips...")
    clips, fps = video_extraction_service.extract_clips(video_path)
    logger.info(f"Extracted {len(clips)} clips (FPS: {fps:.2f})")

    # Process each clip
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    basketball_actions = classifier.get_basketball_stats_mapping()
    detected_actions = []

    for i, (start_frame, clip_frames) in enumerate(clips):
        if i % 5 == 0:
            logger.info(f"Processing clip {i+1}/{len(clips)} (frame {start_frame})")

        # Classify action
        result = classifier.classify(clip_frames)
        if result.action and result.confidence > config.CONFIDENCE_THRESHOLD_DETECTION:
            timestamp = start_frame / fps

            # Save middle frame
            middle_frame_idx = len(clip_frames) // 2
            middle_frame_bgr = cv2.cvtColor(clip_frames[middle_frame_idx], cv2.COLOR_RGB2BGR)
            frame_filename = storage.create_frame(session_id, start_frame, middle_frame_bgr)

            detected_actions.append({
                'frame': start_frame,
                'timestamp': timestamp,
                'action': result.action,
                'confidence': result.confidence,
                'frame_image': frame_filename,
            })

            logger.info(f"Detected '{result.action}' (confidence: {result.confidence:.2f}) at {timestamp:.2f}s")

    # Calculate stats
    stats, detected_actions = stats_calculation_service.calculate_stats(detected_actions, basketball_actions)

    # Format detection details
    detection_details = []
    for det in detected_actions:
        detection_details.append({
            'timestamp': round(det['timestamp'], 2),
            'frame': det['frame'],
            'detected_action': det['action'],
            'confidence': round(det['confidence'], 3),
            'classified_as': det['classified_as'],
            'frame_image': det['frame_image'],
            'session_id': session_id
        })

    # Save session
    session_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'video_duration': round(len(clips) * config.CLIP_DURATION / fps, 2) if fps > 0 else 0,
        'total_detections': len(detection_details),
        'classifier_used': classifier.name,
        'stats': stats,
        'detections': detection_details
    }
    storage.create_session(session_data)
    logger.info(f"Saved session {session_id}")

    # Log summary
    logger.info(f"Analysis complete. Detected {len(detected_actions)} events")
    logger.info(f"Stats: Points={stats['points']}, Assists={stats['assists']}, Blocks={stats['blocks']}")

    # Return for API response
    stats['detections'] = detection_details
    stats['session_id'] = session_id
    return stats
