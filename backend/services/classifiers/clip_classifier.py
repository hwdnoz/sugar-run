"""CLIP-based zero-shot action classifier"""

import logging
import numpy as np
import torch
from typing import Optional, List
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

from .base import ActionClassifier, ClassificationResult, register_classifier

logger = logging.getLogger(__name__)


@register_classifier(
    'clip',
    'OpenAI CLIP',
    'Zero-shot vision-language model',
    'https://huggingface.co/docs/transformers/model_doc/clip'
)
class CLIPZeroShotClassifier(ActionClassifier):
    """Zero-shot action classifier using CLIP"""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        super().__init__()
        self.model_name = model_name
        self.processor: Optional[CLIPProcessor] = None
        self.model: Optional[CLIPModel] = None

        # Basketball action text prompts
        self.action_prompts = [
            "a person shooting a basketball",
            "a person passing a basketball",
            "a person dribbling a basketball",
            "a person dunking a basketball",
            "a person blocking a basketball shot",
            "a person catching a basketball",
            "a person playing basketball",
        ]

    @property
    def name(self) -> str:
        return "CLIP Zero-Shot"

    def initialize(self) -> bool:
        """Initialize CLIP model"""
        logger.info(f"Loading CLIP model: {self.model_name}")
        try:
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.model.eval()
            self._ready = True
            logger.info("CLIP model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load CLIP: {e}")
            self.processor = None
            self.model = None
            self._ready = False
            return False

    def is_ready(self) -> bool:
        """Check if model is ready"""
        return super().is_ready() and self.processor is not None and self.model is not None

    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify action using CLIP zero-shot

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with predicted action and confidence
        """
        if not self.is_ready():
            logger.warning("CLIP classifier not ready")
            return ClassificationResult(action="unknown", confidence=0.0)

        try:
            # Sample 4 frames uniformly (CLIP is image-based, we'll average)
            indices = np.linspace(0, len(frames) - 1, 4, dtype=int)
            sampled_frames = [Image.fromarray(frames[i]) for i in indices]

            # Process inputs
            inputs = self.processor(
                text=self.action_prompts,
                images=sampled_frames,
                return_tensors="pt",
                padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)

                # Get image and text features
                image_embeds = outputs.image_embeds  # [num_frames, embed_dim]
                text_embeds = outputs.text_embeds    # [num_prompts, embed_dim]

                # Average frame embeddings
                avg_image_embed = image_embeds.mean(dim=0, keepdim=True)

                # Calculate similarity scores
                similarity = torch.nn.functional.cosine_similarity(
                    avg_image_embed.unsqueeze(1),
                    text_embeds.unsqueeze(0),
                    dim=2
                )

                probs = torch.nn.functional.softmax(similarity * 100, dim=-1)
                predicted_idx = probs.argmax(-1).item()
                confidence = probs[0][predicted_idx].item()

            predicted_label = self.action_prompts[predicted_idx]

            return ClassificationResult(
                action=predicted_label,
                confidence=confidence,
                metadata={
                    'model': self.model_name,
                    'num_frames_sampled': 4,
                    'classifier': self.name,
                    'all_scores': {prompt: float(probs[0][i]) for i, prompt in enumerate(self.action_prompts)}
                }
            )

        except Exception as e:
            logger.error(f"Error in CLIP classification: {e}")
            return ClassificationResult(action="error", confidence=0.0)
