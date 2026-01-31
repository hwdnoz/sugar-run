"""Base class for action classifiers"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Type, Callable
import logging
import numpy as np

logger = logging.getLogger(__name__)


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


def register_classifier(name: str):
    """
    Decorator to register a classifier class with the registry.

    Usage:
        @register_classifier('videomae')
        class VideoMAEClassifier(ActionClassifier):
            ...
    """
    def decorator(cls: Type['ActionClassifier']) -> Type['ActionClassifier']:
        ClassifierRegistry.register(name, cls)
        return cls
    return decorator


class ClassifierRegistry:
    """
    Registry - stores mapping of classifier names to their factory functions.

    Responsibility: Know what classifiers exist and how to construct them.
    Does NOT create instances - that's the factory's job.
    """

    _registry: Dict[str, Callable[[], 'ActionClassifier']] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], 'ActionClassifier']) -> None:
        """
        Register a classifier factory function.

        Args:
            name: Unique identifier for the classifier (e.g., 'videomae', 'yolo')
            factory: Callable that returns a new classifier instance
        """
        cls._registry[name] = factory
        logger.debug(f"Registered classifier: {name}")

    @classmethod
    def get(cls, name: str) -> Callable[[], 'ActionClassifier']:
        """
        Get the factory function for a classifier type.

        Args:
            name: Classifier identifier

        Returns:
            Factory function that creates the classifier

        Raises:
            ValueError: If classifier type is not registered
        """
        if name not in cls._registry:
            available = ', '.join(cls._registry.keys())
            raise ValueError(f"Unknown classifier: '{name}'. Available: {available}")
        return cls._registry[name]

    @classmethod
    def available(cls) -> List[str]:
        """Return list of registered classifier names."""
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a classifier is registered."""
        return name in cls._registry


class ClassifierFactory:
    """
    Factory - creates and caches classifier instances.

    Responsibility: Create classifier instances on demand, with lazy initialization and caching.
    Uses ClassifierRegistry to look up how to construct each type.
    """

    _instances: Dict[str, 'ActionClassifier'] = {}
    _default: str = 'videomae'

    @classmethod
    def create(cls, classifier_type: Optional[str] = None) -> 'ActionClassifier':
        """
        Create or return cached classifier instance.

        Args:
            classifier_type: Type of classifier to create (defaults to 'videomae')

        Returns:
            Initialized classifier instance
        """
        if classifier_type is None:
            classifier_type = cls._default

        if classifier_type not in cls._instances:
            logger.info(f"Initializing {classifier_type} classifier...")
            factory_fn = ClassifierRegistry.get(classifier_type)
            instance = factory_fn()
            instance.initialize()
            cls._instances[classifier_type] = instance

        return cls._instances[classifier_type]

    @classmethod
    def set_default(cls, name: str) -> None:
        """Set the default classifier type."""
        if not ClassifierRegistry.is_registered(name):
            raise ValueError(f"Cannot set default to unregistered classifier: {name}")
        cls._default = name

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached instances (useful for testing)."""
        cls._instances.clear()
