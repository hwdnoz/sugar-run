"""Storage operations for sessions and frames"""
import json
import os
import cv2

STORAGE_DIR = '/app/data'
SESSIONS_FILE = os.path.join(STORAGE_DIR, 'sessions.jsonl')
FRAMES_DIR = os.path.join(STORAGE_DIR, 'frames')

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# Session CRUD operations
def create_session(session_data):
    """Create new session"""
    with open(SESSIONS_FILE, 'a') as f:
        f.write(json.dumps(session_data) + '\n')

def get_session(session_id):
    """Get session by ID"""
    if not os.path.exists(SESSIONS_FILE):
        return None
    with open(SESSIONS_FILE, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data['session_id'] == session_id:
                return data
    return None

def list_sessions():
    """Get all sessions (newest first)"""
    if not os.path.exists(SESSIONS_FILE):
        return []
    sessions = []
    with open(SESSIONS_FILE, 'r') as f:
        for line in f:
            sessions.append(json.loads(line))
    return list(reversed(sessions))

def update_session(session_id, updates):
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

# Frame operations
def create_frame(session_id, frame_num, image):
    """Save frame image, return filename"""
    filename = f"{session_id}_frame_{frame_num:04d}.jpg"
    path = os.path.join(FRAMES_DIR, filename)
    cv2.imwrite(path, image)
    return filename

def get_frame_path(filename):
    """Get full path to frame"""
    return os.path.join(FRAMES_DIR, filename)
