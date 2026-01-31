"""TimesFormer-based action classifier"""

import logging
import numpy as np
import torch
from typing import Optional
from transformers import AutoImageProcessor, TimesformerForVideoClassification

from .base import ActionClassifier, ClassificationResult

logger = logging.getLogger(__name__)


class TimesFormerClassifier(ActionClassifier):
    """Action classifier using TimesFormer model"""

    def __init__(self, model_name: str = "facebook/timesformer-base-finetuned-k400"):
        super().__init__()
        self.model_name = model_name
        self.processor: Optional[AutoImageProcessor] = None
        self.model: Optional[TimesformerForVideoClassification] = None

    @property
    def name(self) -> str:
        return "TimesFormer"

    def initialize(self) -> bool:
        """Initialize TimesFormer model"""
        logger.info(f"Loading TimesFormer model: {self.model_name}")
        try:
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = TimesformerForVideoClassification.from_pretrained(self.model_name)
            self.model.eval()
            self._ready = True
            logger.info("TimesFormer model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load TimesFormer: {e}")
            self.processor = None
            self.model = None
            self._ready = False
            return False

    def is_ready(self) -> bool:
        """Check if model is ready"""
        return super().is_ready() and self.processor is not None and self.model is not None

    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify action using TimesFormer

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with predicted action and confidence
        """
        if not self.is_ready():
            logger.warning("TimesFormer classifier not ready")
            return ClassificationResult(action="unknown", confidence=0.0)

        try:
            # Sample 8 frames uniformly from clip
            indices = np.linspace(0, len(frames) - 1, 8, dtype=int)
            sampled_frames = [frames[i] for i in indices]

            # Process frames
            inputs = self.processor(sampled_frames, return_tensors="pt")

            with torch.no_grad():
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
                    'num_frames_sampled': 8,
                    'classifier': self.name
                }
            )

        except Exception as e:
            logger.error(f"Error in TimesFormer classification: {e}")
            return ClassificationResult(action="error", confidence=0.0)
