import React, { useState, useEffect } from 'react'
import config from './config'

export default function App() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [videoUrl, setVideoUrl] = useState(null)
  const [currentView, setCurrentView] = useState('upload') // 'upload' or 'admin'
  const [sessions, setSessions] = useState([])
  const [selectedSession, setSelectedSession] = useState(null)
  const [classifiers, setClassifiers] = useState([])
  const [selectedClassifier, setSelectedClassifier] = useState('videomae')
  const [currentFile, setCurrentFile] = useState(null)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    setCurrentFile(file)
    setVideoUrl(URL.createObjectURL(file))

    const formData = new FormData()
    formData.append('video', file)
    formData.append('classifier', selectedClassifier)

    setLoading(true)
    const res = await fetch(`${config.API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData
    })
    const result = await res.json()
    setStats(result)
    setLoading(false)
  }

  const handleReanalyze = async () => {
    if (!currentFile) return

    const formData = new FormData()
    formData.append('video', currentFile)
    formData.append('classifier', selectedClassifier)

    setLoading(true)
    const res = await fetch(`${config.API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData
    })
    const result = await res.json()
    setStats(result)
    setLoading(false)
  }

  const fetchClassifiers = async () => {
    try {
      const res = await fetch(`${config.API_BASE_URL}/classifiers`)
      const data = await res.json()
      setClassifiers(data.classifiers || [])
    } catch (error) {
      console.error('Error fetching classifiers:', error)
    }
  }

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${config.API_BASE_URL}/detections`)
      const data = await res.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
    }
  }

  const selectSession = async (sessionId) => {
    try {
      const res = await fetch(`${config.API_BASE_URL}/detections/${sessionId}`)
      const data = await res.json()
      setSelectedSession(data)
    } catch (error) {
      console.error('Error fetching session:', error)
    }
  }

  useEffect(() => {
    fetchClassifiers()
  }, [])

  useEffect(() => {
    if (currentView === 'admin') {
      fetchSessions()
    }
  }, [currentView])

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Basketball Box Score Analyzer</h1>

      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px', borderBottom: '2px solid #e0e0e0' }}>
        <button
          onClick={() => setCurrentView('upload')}
          style={{
            padding: '10px 20px',
            marginRight: '10px',
            border: 'none',
            borderBottom: currentView === 'upload' ? '3px solid #2196F3' : 'none',
            background: 'none',
            cursor: 'pointer',
            fontWeight: currentView === 'upload' ? 'bold' : 'normal',
            fontSize: '16px'
          }}
        >
          Upload & Analyze
        </button>
        <button
          onClick={() => setCurrentView('admin')}
          style={{
            padding: '10px 20px',
            border: 'none',
            borderBottom: currentView === 'admin' ? '3px solid #2196F3' : 'none',
            background: 'none',
            cursor: 'pointer',
            fontWeight: currentView === 'admin' ? 'bold' : 'normal',
            fontSize: '16px'
          }}
        >
          Admin Logs
        </button>
      </div>

      {/* Upload View */}
      {currentView === 'upload' && (
        <div>
          {/* Classifier Selection */}
          <div style={{ marginBottom: '20px' }}>
            <label htmlFor="classifier" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Classification Method:
            </label>
            <select
              id="classifier"
              value={selectedClassifier}
              onChange={(e) => setSelectedClassifier(e.target.value)}
              style={{
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                width: '100%',
                maxWidth: '500px',
                cursor: 'pointer'
              }}
            >
              {classifiers.map((classifier) => (
                <option key={classifier.id} value={classifier.id}>
                  {classifier.name} - {classifier.description}
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
            <input type="file" accept="video/*" onChange={handleUpload} />

            {currentFile && (
              <button
                onClick={handleReanalyze}
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  fontSize: '16px',
                  backgroundColor: loading ? '#ccc' : '#2196F3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold'
                }}
              >
                {loading ? 'Analyzing...' : 'Re-analyze with Selected Classifier'}
              </button>
            )}
          </div>

      {loading && <p>Analyzing video with {classifiers.find(c => c.id === selectedClassifier)?.name || 'classifier'}...</p>}

      {videoUrl && (
        <div style={{ marginTop: '20px' }}>
          <video src={videoUrl} width="100%" controls />
        </div>
      )}

      {stats && (
        <div style={{ marginTop: '30px' }}>
          <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <strong>Classifier Used:</strong> {stats.classifier_used || selectedClassifier}
          </div>
          <h2>Box Score</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000' }}>
                <th style={{ padding: '10px', textAlign: 'left' }}>Stat</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid #ccc' }}>
                <td style={{ padding: '10px' }}>Points</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>{stats.points}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #ccc' }}>
                <td style={{ padding: '10px' }}>Assists</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>{stats.assists}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #ccc' }}>
                <td style={{ padding: '10px' }}>Steals</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>{stats.steals}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #ccc' }}>
                <td style={{ padding: '10px' }}>Blocks</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>{stats.blocks}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #ccc' }}>
                <td style={{ padding: '10px' }}>Rebounds</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>{stats.rebounds}</td>
              </tr>
            </tbody>
          </table>

          {stats.detections && stats.detections.length > 0 && (
            <div style={{ marginTop: '40px' }}>
              <h2>Detection Timeline (Debug)</h2>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000', backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Time</th>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Frame</th>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Detected Action</th>
                    <th style={{ padding: '8px', textAlign: 'right' }}>Confidence</th>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.detections.map((det, idx) => (
                    <tr
                      key={idx}
                      style={{
                        borderBottom: '1px solid #e0e0e0',
                        backgroundColor: det.classified_as.includes('IGNORED') ? '#fff8f0' :
                                       det.classified_as.includes('SHOT') ? '#e8f5e9' :
                                       det.classified_as.includes('ASSIST') ? '#e3f2fd' :
                                       det.classified_as.includes('BLOCK') ? '#fce4ec' : '#fff'
                      }}
                    >
                      <td style={{ padding: '8px' }}>{det.timestamp}s</td>
                      <td style={{ padding: '8px' }}>{det.frame}</td>
                      <td style={{ padding: '8px' }}>{det.detected_action}</td>
                      <td style={{ padding: '8px', textAlign: 'right' }}>{det.confidence}</td>
                      <td style={{ padding: '8px', fontWeight: det.classified_as.includes('IGNORED') ? 'normal' : 'bold' }}>
                        {det.classified_as}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
        </div>
      )}

      {/* Admin View */}
      {currentView === 'admin' && (
        <div>
          <h2>Detection Logs</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            View all detection sessions with saved frames showing what the model detected
          </p>

          {sessions.length === 0 ? (
            <p style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              No detection sessions yet. Upload a video to create a session.
            </p>
          ) : (
            <div>
              {/* Session List */}
              <div style={{ marginBottom: '30px' }}>
                <h3>Recent Sessions</h3>
                {sessions.map((session, idx) => {
                  const getScoreColor = (score) => {
                    if (score >= 90) return '#4caf50'  // Green
                    if (score >= 70) return '#ff9800'  // Orange
                    if (score >= 50) return '#ff5722'  // Red-Orange
                    return '#f44336'  // Red
                  }

                  return (
                    <div
                      key={idx}
                      onClick={() => selectSession(session.session_id)}
                      style={{
                        padding: '15px',
                        marginBottom: '10px',
                        border: selectedSession?.session_id === session.session_id ? '2px solid #2196F3' : '1px solid #e0e0e0',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        backgroundColor: selectedSession?.session_id === session.session_id ? '#f5f9ff' : '#fff',
                        transition: 'all 0.2s',
                        position: 'relative'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                            Session: {session.session_id}
                          </div>
                          <div style={{ fontSize: '14px', color: '#666' }}>
                            Time: {new Date(session.timestamp).toLocaleString()} |
                            Detections: {session.total_detections} |
                            Points: {session.stats.points} |
                            Assists: {session.stats.assists}
                            {session.classifier_used && (
                              <span> | Classifier: <strong>{session.classifier_used}</strong></span>
                            )}
                          </div>
                        </div>
                        {session.evaluation && (
                          <div style={{
                            padding: '8px 16px',
                            borderRadius: '20px',
                            backgroundColor: getScoreColor(session.evaluation.overall_score),
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '16px',
                            marginLeft: '10px'
                          }}>
                            {session.evaluation.overall_score}%
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Selected Session Details */}
              {selectedSession && (
                <div>
                  {/* Evaluation Score Card */}
                  {selectedSession.evaluation && (
                    <div style={{
                      backgroundColor: '#f5f5f5',
                      padding: '20px',
                      borderRadius: '8px',
                      marginBottom: '20px',
                      border: '1px solid #e0e0e0'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                        <h3 style={{ margin: 0, marginRight: '15px' }}>📊 Evaluation Metrics</h3>
                        <span style={{
                          padding: '8px 20px',
                          borderRadius: '20px',
                          backgroundColor: selectedSession.evaluation.overall_score >= 90 ? '#4caf50' :
                                          selectedSession.evaluation.overall_score >= 70 ? '#ff9800' :
                                          selectedSession.evaluation.overall_score >= 50 ? '#ff5722' : '#f44336',
                          color: 'white',
                          fontWeight: 'bold',
                          fontSize: '18px'
                        }}>
                          {selectedSession.evaluation.overall_score}%
                        </span>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
                        <div>
                          <div style={{ fontSize: '12px', color: '#666' }}>Precision</div>
                          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{selectedSession.evaluation.precision}%</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '12px', color: '#666' }}>Recall</div>
                          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{selectedSession.evaluation.recall}%</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '12px', color: '#666' }}>F1 Score</div>
                          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{selectedSession.evaluation.f1_score}%</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '12px', color: '#666' }}>Stats Accuracy</div>
                          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{selectedSession.evaluation.stats_accuracy}%</div>
                        </div>
                      </div>
                      <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
                        <span style={{ color: '#4caf50', fontWeight: 'bold' }}>✓ {selectedSession.evaluation.true_positives} TP</span>
                        {' | '}
                        <span style={{ color: '#ff5722', fontWeight: 'bold' }}>✗ {selectedSession.evaluation.false_positives} FP</span>
                        {' | '}
                        <span style={{ color: '#ff9800', fontWeight: 'bold' }}>⚠ {selectedSession.evaluation.false_negatives} FN</span>
                      </div>
                    </div>
                  )}

                  <h3>Detection Frames</h3>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: '20px',
                    marginTop: '20px'
                  }}>
                    {selectedSession.detections.map((det, idx) => (
                      <div
                        key={idx}
                        style={{
                          border: '1px solid #e0e0e0',
                          borderRadius: '8px',
                          overflow: 'hidden',
                          backgroundColor: det.classified_as.includes('IGNORED') ? '#fff8f0' :
                                         det.classified_as.includes('SHOT') ? '#e8f5e9' :
                                         det.classified_as.includes('ASSIST') ? '#e3f2fd' :
                                         det.classified_as.includes('BLOCK') ? '#fce4ec' : '#fff'
                        }}
                      >
                        {/* Frame Image */}
                        <img
                          src={`${config.API_BASE_URL}/detections/image/${det.frame_image}`}
                          alt={`Detection at ${det.timestamp}s`}
                          style={{ width: '100%', height: 'auto', display: 'block' }}
                        />

                        {/* Detection Info */}
                        <div style={{ padding: '12px' }}>
                          <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '16px' }}>
                            {det.classified_as}
                          </div>
                          <div style={{ fontSize: '14px', color: '#666' }}>
                            <div><strong>Time:</strong> {det.timestamp}s (Frame {det.frame})</div>
                            <div><strong>Detected:</strong> {det.detected_action}</div>
                            <div><strong>Confidence:</strong> {det.confidence}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
