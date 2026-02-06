"""Basketball stats calculation - scoring logic for different actions"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Callable
from utils import config

logger = logging.getLogger(__name__)

DEFAULT_ACTION_KEYWORDS = {
    'shooting': ['shooting', 'throw', 'toss'],
    'passing': ['passing', 'hand', 'throw'],
    'dribbling': ['dribbling', 'bounce'],
    'dunking': ['dunk', 'slam'],
    'blocking': ['block', 'defend'],
    'catching': ['catch', 'grab'],
}


@dataclass
class ScoringRule:
    """Rule for matching actions and calculating stats"""
    stat_name: str
    points_value: int
    label: str
    confidence_threshold: float
    keyword_getter: Callable[[dict], List[str]]

    def matches(self, action_lower: str, basketball_actions: dict) -> bool:
        """Check if action matches this rule's keywords"""
        keywords = self.keyword_getter(basketball_actions)
        return any(keyword in action_lower for keyword in keywords)

    def apply(self, stats: dict, classified_as: list) -> None:
        """Apply rule: update stats and add classification label"""
        stats[self.stat_name] += self.points_value
        classified_as.append(self.label)
        logger.info(f"  -> Counted as {self.label}! Total {self.stat_name}: {stats[self.stat_name]}")


# Define scoring rules (open for extension - just add new rules!)
SCORING_RULES = [
    ScoringRule(
        stat_name='points',
        points_value=2,
        label='SHOT (+2 points)',
        confidence_threshold=config.CONFIDENCE_THRESHOLD_SHOT,
        keyword_getter=lambda ba: ba['shooting'] + ba['dunking']
    ),
    ScoringRule(
        stat_name='assists',
        points_value=1,
        label='ASSIST (+1)',
        confidence_threshold=config.CONFIDENCE_THRESHOLD_ASSIST,
        keyword_getter=lambda ba: ba['passing']
    ),
    ScoringRule(
        stat_name='blocks',
        points_value=1,
        label='BLOCK (+1)',
        confidence_threshold=config.CONFIDENCE_THRESHOLD_BLOCK,
        keyword_getter=lambda ba: ba['blocking']
    ),
]


def _build_initial_stats():
    """Build zeroed stats dict from SCORING_RULES (single source of truth)"""
    return {rule.stat_name: 0 for rule in SCORING_RULES}


def calculate_stats(detections, basketball_actions):
    """
    Calculate basketball stats from detected actions using scoring rules

    Args:
        detections: List of detected actions with 'action' and 'confidence'
        basketball_actions: Mapping of action types to keywords from classifier

    Returns:
        tuple: (stats dict, detections with 'classified_as' added)
    """
    stats = _build_initial_stats()

    for detection in detections:
        action_lower = detection['action'].lower()
        confidence = detection['confidence']
        classified_as = []

        for rule in SCORING_RULES:
            if rule.matches(action_lower, basketball_actions):
                if confidence > rule.confidence_threshold:
                    rule.apply(stats, classified_as)

        detection['classified_as'] = ', '.join(classified_as) if classified_as else 'IGNORED (below threshold or no match)'

    return stats, detections
