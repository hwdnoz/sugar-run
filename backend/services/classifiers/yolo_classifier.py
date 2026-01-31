"""YOLO ball tracking-based action classifier"""

import logging
import numpy as np
import cv2
from typing import Optional, List, Tuple
from ultralytics import YOLO

from .base import ActionClassifier, ClassificationResult, register_classifier
from utils import config

logger = logging.getLogger(__name__)


@register_classifier('yolo')
class YOLOBallTrackingClassifier(ActionClassifier):
    """
    Action classifier using YOLO ball tracking and position analysis

    This classifier tracks the basketball position across frames and infers
    actions based on ball movement patterns:
    - Shooting: Upward trajectory followed by downward arc
    - Passing: Horizontal movement with acceleration
    - Dribbling: Repeated up-down motion
    - Catching: Sudden stop in ball movement
    """

    def __init__(self, model_path: str = None):
        super().__init__()
        if model_path is None:
            model_path = config.YOLO_MODEL_PATH
        self.model_path = model_path
        self.model: Optional[YOLO] = None

    @property
    def name(self) -> str:
        return "YOLO Ball Tracking"

    def initialize(self) -> bool:
        """Initialize YOLO model"""
        logger.info(f"Loading YOLO model: {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
            self._ready = True
            logger.info("YOLO model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
            self.model = None
            self._ready = False
            return False

    def is_ready(self) -> bool:
        """Check if model is ready - includes model-specific checks"""
        return super().is_ready() and self.model is not None

    def _detect_ball_positions(self, frames: np.ndarray) -> List[Tuple[float, float]]:
        """
        Detect ball positions in each frame

        Args:
            frames: numpy array of frames

        Returns:
            List of (x, y) positions (normalized 0-1), empty tuple if not detected
        """
        positions = []

        for frame in frames:
            # Convert RGB to BGR for YOLO
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            results = self.model(frame_bgr, verbose=False)

            ball_detected = False
            for box in results[0].boxes:
                cls = int(box.cls[0])
                label = self.model.names[cls]

                if label == 'sports ball':
                    # Get box center (normalized coordinates)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    center_x = (x1 + x2) / 2 / frame.shape[1]  # Normalize by width
                    center_y = (y1 + y2) / 2 / frame.shape[0]  # Normalize by height
                    positions.append((float(center_x), float(center_y)))
                    ball_detected = True
                    break

            if not ball_detected:
                positions.append((None, None))

        return positions

    def _analyze_trajectory(self, positions: List[Tuple[float, float]]) -> ClassificationResult:
        """
        Analyze ball trajectory to classify action

        Args:
            positions: List of (x, y) ball positions

        Returns:
            ClassificationResult with inferred action
        """
        # Filter out None positions
        valid_positions = [(x, y) for x, y in positions if x is not None and y is not None]

        if len(valid_positions) < 3:
            return ClassificationResult(
                action="no_ball_detected",
                confidence=0.0,
                metadata={'valid_detections': len(valid_positions)}
            )

        # Calculate movement vectors
        x_coords = [x for x, y in valid_positions]
        y_coords = [y for x, y in valid_positions]

        # Calculate deltas
        dx = x_coords[-1] - x_coords[0]
        dy = y_coords[-1] - y_coords[0]

        # Calculate velocity and acceleration patterns
        x_velocity = np.diff(x_coords)
        y_velocity = np.diff(y_coords)

        avg_x_vel = np.mean(np.abs(x_velocity))
        avg_y_vel = np.mean(np.abs(y_velocity))

        # Calculate vertical movement pattern
        y_direction_changes = np.sum(np.diff(np.sign(y_velocity)) != 0)

        # Calculate total movement
        total_movement = np.sqrt(dx**2 + dy**2)

        # Classification logic based on ball movement
        action = "unknown"
        confidence = 0.0

        # Shooting: Upward movement (y decreases in image coords) then down
        if dy < -0.1 and len(valid_positions) > 5:
            # Check for arc pattern
            mid_y = y_coords[len(y_coords)//2]
            if mid_y < y_coords[0] and mid_y < y_coords[-1]:
                action = "shooting basketball"
                confidence = min(0.9, 0.5 + abs(dy) * 2)

        # Dribbling: Repeated up-down motion
        elif y_direction_changes >= 2 and avg_y_vel > 0.02:
            action = "dribbling basketball"
            confidence = min(0.85, 0.4 + y_direction_changes * 0.15)

        # Passing: Horizontal movement with speed
        elif avg_x_vel > avg_y_vel * 1.5 and total_movement > 0.15:
            action = "passing basketball"
            confidence = min(0.8, 0.4 + total_movement * 2)

        # Catching: Ball present but minimal movement
        elif total_movement < 0.05 and len(valid_positions) > 5:
            action = "catching basketball"
            confidence = 0.6

        # Default: general basketball activity
        else:
            action = "playing basketball"
            confidence = 0.5

        return ClassificationResult(
            action=action,
            confidence=confidence,
            metadata={
                'valid_detections': len(valid_positions),
                'total_frames': len(positions),
                'detection_rate': len(valid_positions) / len(positions),
                'total_movement': float(total_movement),
                'dx': float(dx),
                'dy': float(dy),
                'y_direction_changes': int(y_direction_changes),
                'classifier': self.name
            }
        )

    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify action based on ball tracking

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with inferred action
        """
        if not self.is_ready():
            logger.warning("YOLO classifier not ready")
            return ClassificationResult(action="unknown", confidence=0.0)

        try:
            # Detect ball positions across frames
            positions = self._detect_ball_positions(frames)

            # Analyze trajectory to classify action
            result = self._analyze_trajectory(positions)

            return result

        except Exception as e:
            logger.error(f"Error in YOLO classification: {e}")
            return ClassificationResult(action="error", confidence=0.0)

    def get_basketball_stats_mapping(self):
        """Override with YOLO-specific action keywords"""
        return {
            'shooting': ['shooting basketball', 'throw', 'shot'],
            'passing': ['passing basketball', 'pass'],
            'dribbling': ['dribbling basketball', 'dribble'],
            'dunking': ['dunk', 'slam'],
            'blocking': ['block', 'defend'],
            'catching': ['catching basketball', 'catch']
        }
