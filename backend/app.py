"""Flask app - HTTP routes only"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
from datetime import datetime

from services import request_service
from utils import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Upload and analyze video"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video = request.files['video']
        classifier_type = request.form.get('classifier', 'videomae')

        result = request_service.process_video_upload(
            video,
            video.filename,
            classifier_type
        )
        return jsonify(result)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/classifiers', methods=['GET'])
def list_classifiers():
    """List available classifiers"""
    try:
        classifiers = request_service.get_classifiers()
        return jsonify({'classifiers': classifiers})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/detections', methods=['GET'])
def list_detections():
    """List all sessions"""
    try:
        sessions = storage.list_sessions()
        return jsonify({'sessions': sessions})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/detections/<session_id>', methods=['GET'])
def get_detection_session(session_id):
    """Get specific session"""
    try:
        session = storage.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(session)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/detections/image/<filename>', methods=['GET'])
def get_detection_image(filename):
    """Serve frame image"""
    try:
        image_path = storage.get_frame_path(filename)
        return send_file(image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Basketball Tracker on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
