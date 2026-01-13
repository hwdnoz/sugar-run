from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from analyze import analyze_video, DETECTIONS_DIR
import os
import logging
from datetime import datetime
import json
import glob

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
    try:
        logger.info("=" * 60)
        logger.info("Received video upload request")

        if 'video' not in request.files:
            logger.error("No video file in request")
            return jsonify({'error': 'No video file provided'}), 400

        video = request.files['video']
        logger.info(f"Video filename: {video.filename}")
        logger.info(f"Video content type: {video.content_type}")

        video_path = '/tmp/upload.mp4'
        logger.info(f"Saving video to: {video_path}")
        video.save(video_path)

        file_size = os.path.getsize(video_path)
        logger.info(f"Video saved successfully. Size: {file_size / (1024*1024):.2f} MB")

        logger.info("Starting video analysis with YOLO...")
        result = analyze_video(video_path)

        logger.info(f"Analysis complete. Results: {result}")
        logger.info("Cleaning up temporary file...")
        os.remove(video_path)
        logger.info("Temporary file removed")
        logger.info("=" * 60)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check endpoint called")
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

def load_evaluation_for_session(session_id):
    """Load evaluation results for a session if they exist"""
    eval_history_path = '/app/evaluations/results/evaluation_history.jsonl'

    if not os.path.exists(eval_history_path):
        logger.warning(f"Evaluation history file not found at {eval_history_path}")
        return None

    try:
        with open(eval_history_path, 'r') as f:
            # Read all lines and find matching session_id
            for line in f:
                try:
                    eval_record = json.loads(line)
                    if eval_record.get('session_id') == session_id:
                        logger.info(f"Found evaluation for session {session_id}: {eval_record.get('score', {}).get('overall_score')}%")
                        return eval_record.get('score')
                except Exception as e:
                    logger.error(f"Error parsing evaluation line: {e}")
                    continue
    except Exception as e:
        logger.error(f"Error loading evaluation for {session_id}: {e}")

    return None

@app.route('/detections', methods=['GET'])
def list_detections():
    """List all detection sessions with metadata"""
    try:
        logger.info("Fetching all detection sessions")

        # Find all metadata files
        metadata_files = glob.glob(os.path.join(DETECTIONS_DIR, '*_metadata.json'))
        metadata_files.sort(reverse=True)  # Most recent first

        sessions = []
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                    # Try to load evaluation score for this session
                    eval_score = load_evaluation_for_session(metadata['session_id'])
                    if eval_score:
                        metadata['evaluation'] = eval_score

                    sessions.append(metadata)
            except Exception as e:
                logger.error(f"Error reading {metadata_file}: {e}")
                continue

        logger.info(f"Found {len(sessions)} detection sessions")
        return jsonify({'sessions': sessions})

    except Exception as e:
        logger.error(f"Error listing detections: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/detections/<session_id>', methods=['GET'])
def get_detection_session(session_id):
    """Get metadata for a specific detection session"""
    try:
        metadata_file = os.path.join(DETECTIONS_DIR, f"{session_id}_metadata.json")

        if not os.path.exists(metadata_file):
            return jsonify({'error': 'Session not found'}), 404

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        return jsonify(metadata)

    except Exception as e:
        logger.error(f"Error getting detection session: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/detections/image/<filename>', methods=['GET'])
def get_detection_image(filename):
    """Serve a detection frame image"""
    try:
        image_path = os.path.join(DETECTIONS_DIR, filename)

        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404

        return send_file(image_path, mimetype='image/jpeg')

    except Exception as e:
        logger.error(f"Error serving image: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Basketball Tracker Backend on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
