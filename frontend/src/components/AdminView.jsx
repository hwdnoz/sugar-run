import SessionList from './SessionList'
import EvaluationCard from './EvaluationCard'
import DetectionGrid from './DetectionGrid'

export default function AdminView({ sessions, selectedSession, classifiers, onSelectSession }) {
  if (sessions.length === 0) {
    return (
      <div className="admin-view">
        <div className="card empty-state">
          <div className="empty-icon">📂</div>
          <p>No detection sessions yet. Upload a video to create a session.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-view">
      <div className="admin-header">
        <h2>🔍 Detection Logs</h2>
        <p className="admin-subtitle">
          View all detection sessions with saved frames showing what the model detected
        </p>
      </div>

      <div className="admin-content-2col">
        <SessionList
          sessions={sessions}
          selectedSession={selectedSession}
          classifiers={classifiers}
          onSelectSession={onSelectSession}
        />

        <div className="session-details-panel">
          {!selectedSession ? (
            <div className="empty-state">
              <div className="empty-icon">👈</div>
              <p>Select a session to view detection details</p>
            </div>
          ) : (
            <div className="session-details-content">
              <EvaluationCard evaluation={selectedSession.evaluation} />
              <DetectionGrid detections={selectedSession.detections} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
