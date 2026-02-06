"""VideoMAE-based action classifier"""

import logging
import numpy as np
import torch
from typing import Optional
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification

from .base import ActionClassifier, ClassificationResult, register_classifier
from utils import config

logger = logging.getLogger(__name__)


@register_classifier(
    'videomae',
    'Meta VideoMAE',
    'Video Masked Autoencoder',
    'https://huggingface.co/docs/transformers/model_doc/videomae'
)
class VideoMAEClassifier(ActionClassifier):
    """Action classifier using VideoMAE model"""

    def __init__(self, model_name: str = None):
        super().__init__()
        if model_name is None:
            model_name = config.VIDEOMAE_MODEL_NAME
        self.model_name = model_name
        self.processor: Optional[VideoMAEImageProcessor] = None
        self.model: Optional[VideoMAEForVideoClassification] = None

    @property
    def name(self) -> str:
        return "VideoMAE"

    def initialize(self) -> bool:
        """Initialize VideoMAE model"""
        logger.info(f"Loading VideoMAE model: {self.model_name}")
        try:
            self.processor = VideoMAEImageProcessor.from_pretrained(self.model_name)
            self.model = VideoMAEForVideoClassification.from_pretrained(self.model_name)
            self.model.eval()
            self._ready = True
            logger.info("VideoMAE model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load VideoMAE: {e}")
            self.processor = None
            self.model = None
            self._ready = False
            return False

    def is_ready(self) -> bool:
        """Check if model is ready - includes model-specific checks"""
        return super().is_ready() and self.processor is not None and self.model is not None

    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify action using VideoMAE

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with predicted action and confidence
        """
        if not self.is_ready():
            logger.warning("VideoMAE classifier not ready")
            return ClassificationResult(action="unknown", confidence=0.0)

        try:
            # Sample 16 frames uniformly from clip
            indices = np.linspace(0, len(frames) - 1, 16, dtype=int)
            sampled_frames = [frames[i] for i in indices]

            # Process frames
            inputs = self.processor(sampled_frames, return_tensors="pt")

            with torch.no_grad():
                # Get predictions
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                predicted_class_idx = logits.argmax(-1).item()
                confidence = probs[0][predicted_class_idx].item()

            predicted_label = self.model.config.id2label[predicted_class_idx]

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
            logger.error(f"Error in VideoMAE classification: {e}")
            return ClassificationResult(action="error", confidence=0.0)
