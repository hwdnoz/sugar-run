"""Video processing - extract clips from video files"""
import cv2
import numpy as np
import logging
from utils import config

logger = logging.getLogger(__name__)

def extract_clips(video_path):
    """Extract short clips from video for action recognition"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f"Video: {total_frames} frames at {fps:.2f} fps")

    frames_per_clip = int(fps * config.CLIP_DURATION)
    stride = int(frames_per_clip * (1 - config.CLIP_OVERLAP))

    clips = []
    frames_buffer = []
    frame_count = 0

    while cap.isOpened() and len(clips) < config.MAX_CLIPS:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames_buffer.append(frame_rgb)
        frame_count += 1

        if len(frames_buffer) == frames_per_clip:
            clips.append((frame_count - frames_per_clip, np.array(frames_buffer)))
            frames_buffer = frames_buffer[stride:]

            if len(clips) % 10 == 0:
                logger.info(f"Extracted {len(clips)} clips so far...")

    cap.release()
    logger.info(f"Total clips extracted: {len(clips)}")
    return clips, fps
