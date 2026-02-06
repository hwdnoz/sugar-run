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


def register_classifier(name: str, display_name: str = None, description: str = None, link: str = None, action_keywords: Dict[str, List[str]] = None):
    """
    Decorator to register a classifier class with the registry.

    Usage:
        @register_classifier('videomae', 'Meta VideoMAE', 'Video Masked Autoencoder')
        class VideoMAEClassifier(ActionClassifier):
            ...
    """
    def decorator(cls: Type['ActionClassifier']) -> Type['ActionClassifier']:
        metadata = {
            'name': display_name or name,
            'description': description or '',
            'link': link or '',
        }
        ClassifierRegistry.register(name, cls, metadata, action_keywords)
        return cls
    return decorator


class ClassifierRegistry:
    """
    Registry - stores mapping of classifier names to their factory functions.

    Responsibility: Know what classifiers exist and how to construct them.
    Does NOT create instances - that's the factory's job.
    """

    _registry: Dict[str, Callable[[], 'ActionClassifier']] = {}
    _metadata: Dict[str, Dict[str, str]] = {}
    _action_keywords: Dict[str, Dict[str, List[str]]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], 'ActionClassifier'], metadata: Dict[str, str] = None, action_keywords: Dict[str, List[str]] = None) -> None:
        """
        Register a classifier factory function.

        Args:
            name: Unique identifier for the classifier (e.g., 'videomae', 'yolo')
            factory: Callable that returns a new classifier instance
            metadata: Optional metadata (name, description, link)
            action_keywords: Optional classifier-specific action keyword mapping
        """
        cls._registry[name] = factory
        cls._metadata[name] = metadata or {}
        if action_keywords:
            cls._action_keywords[name] = action_keywords
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

    @classmethod
    def get_info(cls) -> List[Dict[str, str]]:
        """Return list of classifier info with metadata."""
        return [
            {'id': name, **cls._metadata.get(name, {})}
            for name in cls._registry.keys()
        ]

    @classmethod
    def get_action_keywords(cls, name: str) -> Optional[Dict[str, List[str]]]:
        """Get classifier-specific action keywords, or None for defaults."""
        return cls._action_keywords.get(name)


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
            if not instance.initialize():
                raise RuntimeError(f"Classifier '{classifier_type}' failed to initialize")
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
