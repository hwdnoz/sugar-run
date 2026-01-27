"""Base class for action classifiers"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class ClassificationResult:
    """Result of action classification"""
    action: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ActionClassifier(ABC):
    """Abstract base class for action classification strategies"""

    def __init__(self):
        """Initialize classifier with ready state"""
        self._ready = False

    @abstractmethod
    def classify(self, frames: np.ndarray) -> ClassificationResult:
        """
        Classify the action in a video clip

        Args:
            frames: numpy array of frames (shape: [num_frames, height, width, channels])

        Returns:
            ClassificationResult with action label and confidence
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the classifier (load models, etc.)

        Returns:
            True if initialization succeeded, False otherwise
        """
        pass

    def is_ready(self) -> bool:
        """
        Check if classifier is ready to use

        Returns:
            True if ready, False otherwise
        """
        return self._ready

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the classifier"""
        pass

    def get_basketball_stats_mapping(self) -> Dict[str, List[str]]:
        """
        Get mapping of basketball actions to keywords
        Can be overridden by subclasses for custom mappings

        Returns:
            Dictionary mapping action types to keyword lists
        """
        return {
            'shooting': ['shooting', 'throw', 'toss'],
            'passing': ['passing', 'hand', 'throw'],
            'dribbling': ['dribbling', 'bounce'],
            'dunking': ['dunk', 'slam'],
            'blocking': ['block', 'defend'],
            'catching': ['catch', 'grab']
        }
