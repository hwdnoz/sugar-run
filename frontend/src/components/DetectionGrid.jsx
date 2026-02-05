import { api } from '../api'

export default function DetectionGrid({ detections }) {
  return (
    <div className="card detections-card">
      <div className="card-header">
        <h3>🎬 Detection Frames</h3>
      </div>
      <div className="card-body">
        <div className="detections-grid">
          {detections.map((det, idx) => (
            <div
              key={idx}
              className={`detection-card ${
                det.classified_as.includes('IGNORED') ? 'ignored' :
                det.classified_as.includes('SHOT') ? 'shot' :
                det.classified_as.includes('ASSIST') ? 'assist' :
                det.classified_as.includes('BLOCK') ? 'block' : ''
              }`}
            >
              <img
                src={api.getImageUrl(det.frame_image)}
                alt={`Detection at ${det.timestamp}s`}
                className="detection-image"
              />
              <div className="detection-info">
                <div className="detection-result">{det.classified_as}</div>
                <div className="detection-details">
                  <div>⏱️ {det.timestamp}s (Frame {det.frame})</div>
                  <div>🔍 {det.detected_action}</div>
                  <div>📊 Confidence: {det.confidence}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
