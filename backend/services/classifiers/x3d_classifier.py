"""X3D-based action classifier"""

import logging
import numpy as np
import torch
from typing import Optional
import json

from .base import ActionClassifier, ClassificationResult, register_classifier

logger = logging.getLogger(__name__)


@register_classifier('x3d')
class X3DClassifier(ActionClassifier):
    """Action classifier using X3D model from PyTorchVideo"""

    def __init__(self, model_name: str = "x3d_m"):
        super().__init__()
        self.model_name = model_name
        self.model: Optional[torch.nn.Module] = None
        self.labels: Optional[list] = None

    @property
    def name(self) -> str:
        return "X3D"

    def initialize(self) -> bool:
        """Initialize X3D model"""
        logger.info(f"Loading X3D model: {self.model_name}")
        try:
            # Import here to avoid dependency issues
            from pytorchvideo.models.hub import x3d_m

            self.model = x3d_m(pretrained=True)
            self.model.eval()

            # Load Kinetics-400 labels
            import urllib.request
            url = "https://raw.githubusercontent.com/facebookresearch/pytorchvideo/main/pytorchvideo/data/kinetics/classes.json"
            with urllib.request.urlopen(url) as f:
                self.labels = json.load(f)

            self._ready = True
            logger.info("X3D model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load X3D: {e}")
            self.model = None
            self.labels = None
            self._ready = False
            return False

    def is_ready(self) -> bool:
        """Check if model is ready"""
        return super().is_ready() and self.model is not None and self.labels is not None

    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify action using X3D

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with predicted action and confidence
        """
        if not self.is_ready():
            logger.warning("X3D classifier not ready")
            return ClassificationResult(action="unknown", confidence=0.0)

        try:
            # Sample 16 frames uniformly
            indices = np.linspace(0, len(frames) - 1, 16, dtype=int)
            sampled_frames = np.array([frames[i] for i in indices])

            # Convert to tensor: [T, H, W, C] -> [C, T, H, W]
            video = torch.from_numpy(sampled_frames).permute(3, 0, 1, 2).float()
            video = video / 255.0  # Normalize to [0, 1]

            # Normalize with ImageNet stats
            mean = torch.tensor([0.45, 0.45, 0.45]).view(3, 1, 1, 1)
            std = torch.tensor([0.225, 0.225, 0.225]).view(3, 1, 1, 1)
            video = (video - mean) / std

            # Add batch dimension: [C, T, H, W] -> [1, C, T, H, W]
            video = video.unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(video)
                probs = torch.nn.functional.softmax(outputs, dim=-1)
                predicted_class_idx = outputs.argmax(-1).item()
                confidence = probs[0][predicted_class_idx].item()

            predicted_label = self.labels[predicted_class_idx]

            return ClassificationResult(
                action=predicted_label,
                confidence=confidence,
                metadata={
                    'model': self.model_name,
                    'num_frames_sampled': 16,
                    'classifier': self.name
                }
            )

        except Exception as e:
            logger.error(f"Error in X3D classification: {e}")
            return ClassificationResult(action="error", confidence=0.0)
