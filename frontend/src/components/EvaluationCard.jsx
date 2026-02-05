export default function EvaluationCard({ evaluation }) {
  if (!evaluation) return null

  const getScoreClass = (score) => {
    if (score >= 90) return 'excellent'
    if (score >= 70) return 'good'
    if (score >= 50) return 'fair'
    return 'poor'
  }

  return (
    <div className="card evaluation-card">
      <div className="card-header">
        <h3>📊 Evaluation Metrics</h3>
        <div className={`score-badge large ${getScoreClass(evaluation.overall_score)}`}>
          {evaluation.overall_score}%
        </div>
      </div>
      <div className="card-body">
        <div className="metrics-grid">
          <div className="metric-item">
            <div className="metric-label">Precision</div>
            <div className="metric-value">{evaluation.precision}%</div>
          </div>
          <div className="metric-item">
            <div className="metric-label">Recall</div>
            <div className="metric-value">{evaluation.recall}%</div>
          </div>
          <div className="metric-item">
            <div className="metric-label">F1 Score</div>
            <div className="metric-value">{evaluation.f1_score}%</div>
          </div>
          <div className="metric-item">
            <div className="metric-label">Stats Accuracy</div>
            <div className="metric-value">{evaluation.stats_accuracy}%</div>
          </div>
        </div>
        <div className="confusion-matrix">
          <span className="tp">✓ {evaluation.true_positives} TP</span>
          <span className="fp">✗ {evaluation.false_positives} FP</span>
          <span className="fn">⚠ {evaluation.false_negatives} FN</span>
        </div>
      </div>
    </div>
  )
}
