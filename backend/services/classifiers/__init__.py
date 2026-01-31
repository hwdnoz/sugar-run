"""Classification module for basketball action recognition"""

import importlib
import pkgutil

from .base import ActionClassifier, ClassificationResult, ClassifierRegistry, ClassifierFactory

# Auto-discover and import all classifier modules
# Each classifier self-registers via @register_classifier decorator
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name != 'base':
        importlib.import_module(f'.{module_name}', __package__)

__all__ = [
    'ActionClassifier',
    'ClassificationResult',
    'ClassifierRegistry',
    'ClassifierFactory',
]
