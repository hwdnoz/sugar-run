from flask import Flask, request, jsonify
from flask_cors import CORS
from analyze import analyze_video
import os
import logging
from datetime import datetime

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

if __name__ == '__main__':
    logger.info("Starting Basketball Tracker Backend on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
