export default function SessionList({ sessions, selectedSession, classifiers, onSelectSession }) {
  const getScoreClass = (score) => {
    if (score >= 90) return 'excellent'
    if (score >= 70) return 'good'
    if (score >= 50) return 'fair'
    return 'poor'
  }

  return (
    <div className="sessions-list">
      <h3>📋 Recent Sessions</h3>
      <div className="sessions-scroll">
        {sessions.map((session, idx) => {
          const isSelected = selectedSession?.session_id === session.session_id

          return (
            <div
              key={idx}
              onClick={() => onSelectSession(session.session_id)}
              className={`session-item ${isSelected ? 'selected' : ''}`}
            >
              <div className="session-content">
                <div className="session-info">
                  <div className="session-title">
                    Session: {session.session_id}
                  </div>
                  <div className="session-meta">
                    <span>⏰ {new Date(session.timestamp).toLocaleString()}</span>
                    <span>📊 Detections: {session.total_detections}</span>
                    <span>🎯 Points: {session.stats.points}</span>
                    <span>🤝 Assists: {session.stats.assists}</span>
                    {session.classifier_used && (() => {
                      const classifier = classifiers.find(c =>
                        c.id === session.classifier_used ||
                        c.name === session.classifier_used ||
                        c.id.toLowerCase() === session.classifier_used.toLowerCase() ||
                        c.name.toLowerCase().includes(session.classifier_used.toLowerCase()) ||
                        session.classifier_used.toLowerCase().includes(c.id.toLowerCase())
                      )
                      const displayName = classifier ? classifier.name : session.classifier_used
                      return (
                        <span className="classifier-tag">
                          🔬 {displayName}
                          {classifier?.link && (
                            <a
                              href={classifier.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="classifier-link"
                              onClick={(e) => e.stopPropagation()}
                            >
                              📖
                            </a>
                          )}
                        </span>
                      )
                    })()}
                  </div>
                </div>
                {session.evaluation && (
                  <div className={`score-badge ${getScoreClass(session.evaluation.overall_score)}`}>
                    {session.evaluation.overall_score}%
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
