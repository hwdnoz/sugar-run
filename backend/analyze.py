import cv2
from ultralytics import YOLO
import numpy as np
import logging

logger = logging.getLogger(__name__)

model = YOLO('yolov8n.pt')

def analyze_video(video_path):
    logger.info(f"Opening video file: {video_path}")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        logger.error(f"Failed to open video file: {video_path}")
        raise ValueError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    logger.info(f"Video info - FPS: {fps:.2f}, Total frames: {total_frames}, Duration: {duration:.2f}s")

    stats = {
        'points': 0,
        'assists': 0,
        'steals': 0,
        'blocks': 0,
        'rebounds': 0
    }

    ball_positions = []
    prev_ball_holder = None
    frame_count = 0
    processed_frames = 0

    logger.info("Starting frame-by-frame analysis...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % int(fps // 2) == 0:
            processed_frames += 1
            if processed_frames % 10 == 0:
                logger.info(f"Processing frame {frame_count}/{total_frames} ({(frame_count/total_frames*100):.1f}%)")

            results = model(frame, verbose=False)

            ball = None
            people = []

            for box in results[0].boxes:
                cls = int(box.cls[0])
                label = model.names[cls]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                if label == 'sports ball':
                    ball = {'x': center_x, 'y': center_y}
                elif label == 'person':
                    people.append({'x': center_x, 'y': center_y})

            if ball:
                ball_positions.append(ball)

                if len(ball_positions) >= 4:
                    if is_shot_made(ball_positions[-4:]):
                        stats['points'] += 2

                    if is_block(ball_positions[-4:]):
                        stats['blocks'] += 1

                    if is_rebound(ball_positions[-4:]):
                        stats['rebounds'] += 1

                if people:
                    current_holder = find_closest_person(ball, people)

                    if prev_ball_holder and current_holder != prev_ball_holder:
                        if is_steal(ball_positions[-2:] if len(ball_positions) >= 2 else []):
                            stats['steals'] += 1

                        if len(ball_positions) >= 3 and is_pass(ball_positions[-3:]):
                            stats['assists'] += 1

                    prev_ball_holder = current_holder

        frame_count += 1

    cap.release()
    logger.info(f"Video analysis complete. Processed {processed_frames} frames out of {total_frames} total frames")
    logger.info(f"Final stats: Points={stats['points']}, Assists={stats['assists']}, Steals={stats['steals']}, Blocks={stats['blocks']}, Rebounds={stats['rebounds']}")
    return stats

def is_shot_made(positions):
    if len(positions) < 4:
        return False

    y_vals = [p['y'] for p in positions]

    if y_vals[0] > y_vals[1] and y_vals[1] < y_vals[2] and y_vals[2] < y_vals[3]:
        if y_vals[1] < y_vals[0] - 50:
            return True

    return False

def is_block(positions):
    if len(positions) < 4:
        return False

    y_vals = [p['y'] for p in positions]

    if y_vals[0] > y_vals[1] > y_vals[2] < y_vals[3]:
        return True

    return False

def is_rebound(positions):
    if len(positions) < 4:
        return False

    y_vals = [p['y'] for p in positions]

    if y_vals[0] < y_vals[1] and y_vals[1] > y_vals[2] > y_vals[3]:
        return True

    return False

def is_steal(positions):
    if len(positions) < 2:
        return False

    x_vals = [p['x'] for p in positions]

    if abs(x_vals[1] - x_vals[0]) > 100:
        return True

    return False

def is_pass(positions):
    if len(positions) < 3:
        return False

    x_vals = [p['x'] for p in positions]

    if abs(x_vals[2] - x_vals[0]) > 150:
        return True

    return False

def find_closest_person(ball, people):
    min_dist = float('inf')
    closest = None

    for i, person in enumerate(people):
        dist = ((ball['x'] - person['x'])**2 + (ball['y'] - person['y'])**2)**0.5
        if dist < min_dist:
            min_dist = dist
            closest = i

    return closest
