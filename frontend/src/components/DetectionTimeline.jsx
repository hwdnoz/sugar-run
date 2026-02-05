export default function DetectionTimeline({ detections }) {
  if (!detections?.length) return null

  return (
    <div className="card timeline-card">
      <div className="card-header">
        <h2>⏱️ Detection Timeline (Debug)</h2>
      </div>
      <div className="card-body">
        <div className="timeline-table-wrapper">
          <table className="timeline-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Frame</th>
                <th>Detected Action</th>
                <th>Confidence</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {detections.map((det, idx) => (
                <tr
                  key={idx}
                  className={`timeline-row ${
                    det.classified_as.includes('IGNORED') ? 'ignored' :
                    det.classified_as.includes('SHOT') ? 'shot' :
                    det.classified_as.includes('ASSIST') ? 'assist' :
                    det.classified_as.includes('BLOCK') ? 'block' : ''
                  }`}
                >
                  <td>{det.timestamp}s</td>
                  <td>{det.frame}</td>
                  <td>{det.detected_action}</td>
                  <td>{det.confidence}</td>
                  <td className="result-cell">{det.classified_as}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
