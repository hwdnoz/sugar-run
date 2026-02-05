export default function StatsDisplay({ stats, selectedClassifier }) {
  if (!stats) return null

  return (
    <div className="card stats-card">
      <div className="card-header">
        <h2>📊 Box Score</h2>
        <div className="classifier-badge">
          Classifier: {stats.classifier_used || selectedClassifier}
        </div>
      </div>
      <div className="card-body">
        <div className="stats-grid">
          <div className="stat-box points">
            <div className="stat-icon">🎯</div>
            <div className="stat-value">{stats.points}</div>
            <div className="stat-label">Points</div>
          </div>
          <div className="stat-box assists">
            <div className="stat-icon">🤝</div>
            <div className="stat-value">{stats.assists}</div>
            <div className="stat-label">Assists</div>
          </div>
          <div className="stat-box steals">
            <div className="stat-icon">👐</div>
            <div className="stat-value">{stats.steals}</div>
            <div className="stat-label">Steals</div>
          </div>
          <div className="stat-box blocks">
            <div className="stat-icon">🚫</div>
            <div className="stat-value">{stats.blocks}</div>
            <div className="stat-label">Blocks</div>
          </div>
          <div className="stat-box rebounds">
            <div className="stat-icon">↩️</div>
            <div className="stat-value">{stats.rebounds}</div>
            <div className="stat-label">Rebounds</div>
          </div>
        </div>
      </div>
    </div>
  )
}
