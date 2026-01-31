"""Classification module for basketball action recognition"""

from .base import ActionClassifier, ClassificationResult, ClassifierRegistry, ClassifierFactory
from .videomae_classifier import VideoMAEClassifier
from .yolo_classifier import YOLOBallTrackingClassifier
from .timesformer_classifier import TimesFormerClassifier
from .x3d_classifier import X3DClassifier
from .clip_classifier import CLIPZeroShotClassifier
from .vivit_classifier import ViViTClassifier
from .slowfast_classifier import SlowFastClassifier

from utils import config

# Register all classifiers
ClassifierRegistry.register('videomae', lambda: VideoMAEClassifier(model_name=config.VIDEOMAE_MODEL_NAME))
ClassifierRegistry.register('yolo', lambda: YOLOBallTrackingClassifier(model_path=config.YOLO_MODEL_PATH))
ClassifierRegistry.register('timesformer', TimesFormerClassifier)
ClassifierRegistry.register('x3d', X3DClassifier)
ClassifierRegistry.register('clip', CLIPZeroShotClassifier)
ClassifierRegistry.register('vivit', ViViTClassifier)
ClassifierRegistry.register('slowfast', SlowFastClassifier)

__all__ = [
    'ActionClassifier',
    'ClassificationResult',
    'ClassifierRegistry',
    'ClassifierFactory',
    'VideoMAEClassifier',
    'YOLOBallTrackingClassifier',
    'TimesFormerClassifier',
    'X3DClassifier',
    'CLIPZeroShotClassifier',
    'ViViTClassifier',
    'SlowFastClassifier',
]
