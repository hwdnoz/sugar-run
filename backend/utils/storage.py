"""Storage operations for sessions and frames"""
import json
import os
import cv2

STORAGE_DIR = '/app/data'
SESSIONS_FILE = os.path.join(STORAGE_DIR, 'sessions.jsonl')
FRAMES_DIR = os.path.join(STORAGE_DIR, 'frames')

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)


class SessionStorage:
    """Handle session persistence operations"""

    @staticmethod
    def create(session_data):
        """Create new session"""
        with open(SESSIONS_FILE, 'a') as f:
            f.write(json.dumps(session_data) + '\n')

    @staticmethod
    def get(session_id):
        """Get session by ID"""
        if not os.path.exists(SESSIONS_FILE):
            return None
        with open(SESSIONS_FILE, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data['session_id'] == session_id:
                    return data
        return None

    @staticmethod
    def list_all():
        """Get all sessions (newest first)"""
        if not os.path.exists(SESSIONS_FILE):
            return []
        sessions = []
        with open(SESSIONS_FILE, 'r') as f:
            for line in f:
                sessions.append(json.loads(line))
        return list(reversed(sessions))

    @staticmethod
    def update(session_id, updates):
        """Update session with new data"""
        if not os.path.exists(SESSIONS_FILE):
            return

        sessions = []
        with open(SESSIONS_FILE, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data['session_id'] == session_id:
                    data.update(updates)
                sessions.append(data)

        with open(SESSIONS_FILE, 'w') as f:
            for session in sessions:
                f.write(json.dumps(session) + '\n')


class FrameStorage:
    """Handle frame image operations"""

    @staticmethod
    def create(session_id, frame_num, image):
        """Save frame image, return filename"""
        filename = f"{session_id}_frame_{frame_num:04d}.jpg"
        path = os.path.join(FRAMES_DIR, filename)
        cv2.imwrite(path, image)
        return filename

    @staticmethod
    def get_path(filename):
        """Get full path to frame"""
        return os.path.join(FRAMES_DIR, filename)
