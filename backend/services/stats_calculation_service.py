"""Basketball stats calculation - scoring logic for different actions"""
import logging
from utils import config

logger = logging.getLogger(__name__)

def calculate_stats(detections, basketball_actions):
    """
    Calculate basketball stats from detected actions

    Args:
        detections: List of detected actions with 'action' and 'confidence'
        basketball_actions: Mapping of action types to keywords from classifier

    Returns:
        tuple: (stats dict, detections with 'classified_as' added)
    """
    stats = {
        'points': 0,
        'assists': 0,
        'steals': 0,
        'blocks': 0,
        'rebounds': 0
    }

    for detection in detections:
        action_label = detection['action']
        confidence = detection['confidence']
        action_lower = action_label.lower()
        classified_as = []

        # Check for shots
        if any(keyword in action_lower for keyword in basketball_actions['shooting'] + basketball_actions['dunking']):
            if confidence > config.CONFIDENCE_THRESHOLD_SHOT:
                stats['points'] += 2
                classified_as.append('SHOT (+2 points)')
                logger.info(f"  -> Counted as SHOT! Total points: {stats['points']}")

        # Check for assists
        if any(keyword in action_lower for keyword in basketball_actions['passing']):
            if confidence > config.CONFIDENCE_THRESHOLD_ASSIST:
                stats['assists'] += 1
                classified_as.append('ASSIST (+1)')
                logger.info(f"  -> Counted as ASSIST! Total assists: {stats['assists']}")

        # Check for blocks
        if any(keyword in action_lower for keyword in basketball_actions['blocking']):
            if confidence > config.CONFIDENCE_THRESHOLD_BLOCK:
                stats['blocks'] += 1
                classified_as.append('BLOCK (+1)')
                logger.info(f"  -> Counted as BLOCK! Total blocks: {stats['blocks']}")

        detection['classified_as'] = ', '.join(classified_as) if classified_as else 'IGNORED (below threshold or no match)'

    return stats, detections
