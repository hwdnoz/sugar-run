const STAT_ICONS = {
  points: '🎯',
  assists: '🤝',
  blocks: '🚫',
}

const KNOWN_NON_STAT_KEYS = new Set([
  'detections', 'session_id', 'classifier_used',
])

export default function StatsDisplay({ stats, selectedClassifier }) {
  if (!stats) return null

  const statEntries = Object.entries(stats).filter(
    ([key]) => !KNOWN_NON_STAT_KEYS.has(key) && typeof stats[key] === 'number'
  )

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
          {statEntries.map(([key, value]) => (
            <div key={key} className={`stat-box ${key}`}>
              <div className="stat-icon">{STAT_ICONS[key] || '📈'}</div>
              <div className="stat-value">{value}</div>
              <div className="stat-label">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
