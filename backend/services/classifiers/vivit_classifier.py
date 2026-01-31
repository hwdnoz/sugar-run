"""ViViT-based action classifier"""

import logging
import numpy as np
import torch
from typing import Optional
from transformers import VivitImageProcessor, VivitForVideoClassification

from .base import ActionClassifier, ClassificationResult, register_classifier

logger = logging.getLogger(__name__)


@register_classifier('vivit')
class ViViTClassifier(ActionClassifier):
    """Action classifier using ViViT (Video Vision Transformer) model"""

    def __init__(self, model_name: str = "google/vivit-b-16x2-kinetics400"):
        super().__init__()
        self.model_name = model_name
        self.processor: Optional[VivitImageProcessor] = None
        self.model: Optional[VivitForVideoClassification] = None

    @property
    def name(self) -> str:
        return "ViViT"

    def initialize(self) -> bool:
        """Initialize ViViT model"""
        logger.info(f"Loading ViViT model: {self.model_name}")
        try:
            self.processor = VivitImageProcessor.from_pretrained(self.model_name)
            self.model = VivitForVideoClassification.from_pretrained(self.model_name)
            self.model.eval()
            self._ready = True
            logger.info("ViViT model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load ViViT: {e}")
            self.processor = None
            self.model = None
            self._ready = False
            return False

    def is_ready(self) -> bool:
        """Check if model is ready"""
        return super().is_ready() and self.processor is not None and self.model is not None

    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify action using ViViT

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with predicted action and confidence
        """
        if not self.is_ready():
            logger.warning("ViViT classifier not ready")
            return ClassificationResult(action="unknown", confidence=0.0)

        try:
            # Sample 32 frames uniformly (ViViT uses 32 frames)
            num_frames = min(32, len(frames))
            indices = np.linspace(0, len(frames) - 1, num_frames, dtype=int)
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
                    'num_frames_sampled': num_frames,
                    'classifier': self.name
                }
            )

        except Exception as e:
            logger.error(f"Error in ViViT classification: {e}")
            return ClassificationResult(action="error", confidence=0.0)
