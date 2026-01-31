"""Request handling service - business logic for API requests"""
import os
import logging
from services.video_analysis_service import analyze_video
from services.results_evaluation_service import run_evaluation
from utils import config

logger = logging.getLogger(__name__)

VALID_CLASSIFIERS = ['videomae', 'yolo', 'timesformer', 'x3d', 'clip', 'vivit', 'slowfast']

CLASSIFIER_INFO = [
    {
        'id': 'videomae',
        'name': 'VideoMAE',
        'description': 'Video Masked Autoencoder for action recognition using pre-trained Kinetics model'
    },
    {
        'id': 'yolo',
        'name': 'YOLO Ball Tracking',
        'description': 'Tracks basketball position and infers actions from ball trajectory patterns'
    },
    {
        'id': 'timesformer',
        'name': 'TimesFormer',
        'description': 'Space-time attention transformer for video classification'
    },
    {
        'id': 'x3d',
        'name': 'X3D',
        'description': 'Efficient 3D CNN for mobile/edge video recognition'
    },
    {
        'id': 'clip',
        'name': 'CLIP Zero-Shot',
        'description': 'Zero-shot classification using vision-language model'
    },
    {
        'id': 'vivit',
        'name': 'ViViT',
        'description': 'Video Vision Transformer with temporal modeling'
    },
    {
        'id': 'slowfast',
        'name': 'SlowFast',
        'description': 'Dual-pathway network for spatial and temporal recognition'
    }
]

def validate_classifier(classifier_type):
    """Validate classifier type"""
    if classifier_type not in VALID_CLASSIFIERS:
        raise ValueError(f'Invalid classifier: {classifier_type}. Must be {" or ".join(VALID_CLASSIFIERS)}')

def process_video_upload(video_file, filename, classifier_type):
    """
    Process uploaded video: save, analyze, evaluate, cleanup

    Returns: analysis results dict
    """
    logger.info("=" * 60)
    logger.info(f"Processing video: {filename}")
    logger.info(f"Classifier: {classifier_type}")

    # Validate
    validate_classifier(classifier_type)

    # Save video temporarily
    video_path = '/tmp/upload.mp4'
    video_file.save(video_path)
    file_size = os.path.getsize(video_path)
    logger.info(f"Saved video: {file_size / (1024*1024):.2f} MB")

    try:
        # Analyze
        logger.info("Starting analysis...")
        result = analyze_video(video_path, classifier_type=classifier_type)
        logger.info("Analysis complete")

        # Evaluate if enabled
        if config.ENABLE_EVALUATION and filename and result.get('session_id'):
            logger.info("Running evaluation...")
            try:
                eval_result = run_evaluation(filename, result['session_id'], silent=True)
                if eval_result.get('success'):
                    logger.info(f"✅ Score: {eval_result['score']['overall_score']}%")
                    result['evaluation'] = eval_result['score']
            except Exception as e:
                logger.error(f"Evaluation error: {e}")

        return result

    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
            logger.info("Cleaned up temp file")
        logger.info("=" * 60)

def get_classifiers():
    """Get list of available classifiers"""
    return CLASSIFIER_INFO
