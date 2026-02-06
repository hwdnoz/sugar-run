"""Request handling service - business logic for API requests"""
import os
import logging
from services.video_analysis_service import analyze_video
from services.results_evaluation_service import run_evaluation
from services.classifiers import ClassifierRegistry
from utils import config

logger = logging.getLogger(__name__)

def validate_classifier(classifier_type):
    """Validate classifier type"""
    if not ClassifierRegistry.is_registered(classifier_type):
        available = ', '.join(ClassifierRegistry.available())
        raise ValueError(f'Invalid classifier: {classifier_type}. Available: {available}')

def save_temp_video(video_file):
    """Save uploaded video to temporary location, return path"""
    video_path = '/tmp/upload.mp4'
    video_file.save(video_path)
    file_size = os.path.getsize(video_path)
    logger.info(f"Saved video: {file_size / (1024*1024):.2f} MB")
    return video_path

def cleanup_temp_video(video_path):
    """Remove temporary video file"""
    if os.path.exists(video_path):
        os.remove(video_path)
        logger.info("Cleaned up temp file")

def evaluate_result(filename, session_id):
    """Run evaluation on analysis result, return evaluation data or None"""
    if not config.ENABLE_EVALUATION or not filename or not session_id:
        return None

    logger.info("Running evaluation...")
    try:
        eval_result = run_evaluation(filename, session_id, silent=True)
        if eval_result.get('success'):
            logger.info(f"✅ Score: {eval_result['score']['overall_score']}%")
            return eval_result['score']
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
    return None

def process_video_upload(video_file, filename, classifier_type):
    """Orchestrate video upload processing"""
    logger.info("=" * 60)
    logger.info(f"Processing video: {filename}")
    logger.info(f"Classifier: {classifier_type}")

    validate_classifier(classifier_type)
    video_path = save_temp_video(video_file)

    try:
        logger.info("Starting analysis...")
        result = analyze_video(video_path, classifier_type=classifier_type)
        logger.info("Analysis complete")

        evaluation = evaluate_result(filename, result.get('session_id'))
        if evaluation:
            result['evaluation'] = evaluation

        return result
    finally:
        cleanup_temp_video(video_path)
        logger.info("=" * 60)

def get_classifiers():
    """Get list of available classifiers"""
    return ClassifierRegistry.get_info()
