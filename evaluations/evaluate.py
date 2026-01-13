#!/usr/bin/env python3
"""
Evaluation Tool for Basketball Action Recognition

Compares detection results against ground truth and provides accuracy scores.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple


class EvaluationResult:
    def __init__(self):
        self.true_positives = []
        self.false_positives = []
        self.false_negatives = []
        self.stats_correct = {}
        self.stats_errors = {}

    def add_true_positive(self, expected, actual):
        self.true_positives.append({
            'type': expected['type'],
            'expected_time': expected['timestamp'],
            'actual_time': actual['timestamp'],
            'time_error': abs(expected['timestamp'] - actual['timestamp'])
        })

    def add_false_positive(self, actual):
        self.false_positives.append({
            'type': actual['classified_as'],
            'timestamp': actual['timestamp']
        })

    def add_false_negative(self, expected):
        self.false_negatives.append({
            'type': expected['type'],
            'expected_time': expected['timestamp']
        })


def load_ground_truth(video_name: str) -> Dict:
    """Load ground truth for a video"""
    gt_path = f"ground_truth/{video_name.replace('.mp4', '')}.json"

    if not os.path.exists(gt_path):
        raise FileNotFoundError(f"Ground truth not found: {gt_path}")

    with open(gt_path, 'r') as f:
        return json.load(f)


def load_session_results(session_id: str) -> Dict:
    """Load detection results from a session"""
    # Check if running from backend container
    if os.path.exists('/tmp/detections'):
        detections_dir = '/tmp/detections'
    else:
        # Running from host, need to get from container
        import subprocess
        result = subprocess.run(
            ['docker', 'cp', f'basketball-tracker-backend:/tmp/detections/{session_id}_metadata.json', '/tmp/'],
            capture_output=True
        )
        detections_dir = '/tmp'

    metadata_path = os.path.join(detections_dir, f'{session_id}_metadata.json')

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Session metadata not found: {metadata_path}")

    with open(metadata_path, 'r') as f:
        return json.load(f)


def match_detection(expected: Dict, detections: List[Dict]) -> Tuple[bool, Dict]:
    """
    Try to match an expected detection with actual detections.
    Returns (matched, detection) tuple.
    """
    expected_type = expected['type'].upper()
    tolerance = expected['tolerance']
    expected_time = expected['timestamp']

    for detection in detections:
        classified_as = detection['classified_as'].upper()
        actual_time = detection['timestamp']

        # Check if type matches
        if expected_type in classified_as and '(+' in classified_as:
            # Check if within time tolerance
            time_diff = abs(expected_time - actual_time)
            if time_diff <= tolerance:
                return True, detection

    return False, None


def evaluate_detections(ground_truth: Dict, session_results: Dict) -> EvaluationResult:
    """Compare ground truth against actual detections"""
    result = EvaluationResult()

    expected_detections = ground_truth['expected_detections']
    actual_detections = session_results['detections']

    # Track which actual detections have been matched
    matched_indices = set()

    # Check each expected detection
    for expected in expected_detections:
        matched, detection = match_detection(expected, actual_detections)

        if matched:
            result.add_true_positive(expected, detection)
            # Find and mark the index
            for i, det in enumerate(actual_detections):
                if det == detection:
                    matched_indices.add(i)
                    break
        else:
            result.add_false_negative(expected)

    # Find false positives (actual detections that don't match any expected)
    for i, actual in enumerate(actual_detections):
        if i not in matched_indices:
            # Only count as false positive if it was classified as something (not IGNORED)
            if 'IGNORED' not in actual['classified_as']:
                result.add_false_positive(actual)

    # Compare stats
    expected_stats = ground_truth['expected_stats']
    actual_stats = session_results['stats']

    for stat_name, expected_value in expected_stats.items():
        actual_value = actual_stats.get(stat_name, 0)
        if expected_value == actual_value:
            result.stats_correct[stat_name] = expected_value
        else:
            result.stats_errors[stat_name] = {
                'expected': expected_value,
                'actual': actual_value
            }

    return result


def calculate_score(result: EvaluationResult, ground_truth: Dict) -> Dict:
    """Calculate overall accuracy score"""

    tp_count = len(result.true_positives)
    fp_count = len(result.false_positives)
    fn_count = len(result.false_negatives)

    # Precision: TP / (TP + FP)
    precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0

    # Recall: TP / (TP + FN)
    recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0

    # F1 Score: Harmonic mean of precision and recall
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Stats accuracy
    total_stats = len(ground_truth['expected_stats'])
    correct_stats = len(result.stats_correct)
    stats_accuracy = (correct_stats / total_stats * 100) if total_stats > 0 else 0

    # Timing accuracy (average time error for TPs)
    avg_time_error = 0
    if result.true_positives:
        avg_time_error = sum(tp['time_error'] for tp in result.true_positives) / len(result.true_positives)

    # Overall score (weighted combination)
    # 50% detection accuracy (F1), 30% stats accuracy, 20% timing accuracy
    timing_score = max(0, 100 - (avg_time_error * 20))  # Penalize timing errors
    overall_score = (f1_score * 50) + (stats_accuracy * 0.3) + (timing_score * 0.2)

    return {
        'overall_score': round(overall_score, 2),
        'precision': round(precision * 100, 2),
        'recall': round(recall * 100, 2),
        'f1_score': round(f1_score * 100, 2),
        'stats_accuracy': round(stats_accuracy, 2),
        'timing_accuracy': round(timing_score, 2),
        'avg_time_error_seconds': round(avg_time_error, 2),
        'true_positives': tp_count,
        'false_positives': fp_count,
        'false_negatives': fn_count
    }


def print_evaluation_report(ground_truth: Dict, session_results: Dict,
                           result: EvaluationResult, score: Dict):
    """Print a detailed evaluation report"""

    print("\n" + "="*80)
    print("EVALUATION REPORT")
    print("="*80)
    print(f"Video: {ground_truth['video_name']}")
    print(f"Session: {session_results['session_id']}")
    print(f"Timestamp: {session_results['timestamp']}")
    print("="*80)

    print(f"\n📊 OVERALL SCORE: {score['overall_score']}%")
    print("\n" + "-"*80)

    print("\n🎯 DETECTION METRICS:")
    print(f"  Precision:  {score['precision']}%")
    print(f"  Recall:     {score['recall']}%")
    print(f"  F1 Score:   {score['f1_score']}%")

    print(f"\n✅ TRUE POSITIVES: {score['true_positives']}")
    for tp in result.true_positives:
        print(f"  • {tp['type'].upper()}: Expected {tp['expected_time']}s, Detected {tp['actual_time']}s (error: {tp['time_error']:.2f}s)")

    print(f"\n❌ FALSE POSITIVES: {score['false_positives']}")
    for fp in result.false_positives:
        print(f"  • {fp['type']} at {fp['timestamp']}s (should not have been detected)")

    print(f"\n⚠️  FALSE NEGATIVES: {score['false_negatives']}")
    for fn in result.false_negatives:
        print(f"  • {fn['type'].upper()} at {fn['expected_time']}s (missed detection)")

    print(f"\n📈 STATS ACCURACY: {score['stats_accuracy']}%")
    if result.stats_correct:
        print("  Correct:")
        for stat, value in result.stats_correct.items():
            print(f"    • {stat}: {value} ✓")

    if result.stats_errors:
        print("  Errors:")
        for stat, values in result.stats_errors.items():
            print(f"    • {stat}: Expected {values['expected']}, Got {values['actual']} ✗")

    print(f"\n⏱️  TIMING ACCURACY: {score['timing_accuracy']}%")
    print(f"  Average time error: {score['avg_time_error_seconds']}s")

    print("\n" + "="*80 + "\n")


def save_evaluation_results(ground_truth: Dict, session_results: Dict,
                            result: EvaluationResult, score: Dict):
    """Save evaluation results to file"""

    results_file = "results/evaluation_history.jsonl"

    evaluation_record = {
        'timestamp': datetime.now().isoformat(),
        'video_name': ground_truth['video_name'],
        'session_id': session_results['session_id'],
        'score': score,
        'true_positives': result.true_positives,
        'false_positives': result.false_positives,
        'false_negatives': result.false_negatives,
        'stats_correct': result.stats_correct,
        'stats_errors': result.stats_errors
    }

    # Append to JSONL file
    with open(results_file, 'a') as f:
        f.write(json.dumps(evaluation_record) + '\n')

    print(f"📁 Results saved to: {results_file}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python evaluate.py <video_name> <session_id>")
        print("\nExample:")
        print("  python evaluate.py trim.mp4 20260113_053847")
        sys.exit(1)

    video_name = sys.argv[1]
    session_id = sys.argv[2]

    try:
        # Load data
        print(f"\n🔍 Loading ground truth for {video_name}...")
        ground_truth = load_ground_truth(video_name)

        print(f"📊 Loading session results for {session_id}...")
        session_results = load_session_results(session_id)

        # Evaluate
        print("⚙️  Evaluating...")
        result = evaluate_detections(ground_truth, session_results)
        score = calculate_score(result, ground_truth)

        # Report
        print_evaluation_report(ground_truth, session_results, result, score)

        # Save
        save_evaluation_results(ground_truth, session_results, result, score)

        return score['overall_score']

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
