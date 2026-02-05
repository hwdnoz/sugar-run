import React, { useState, useEffect } from 'react'
import config from './config'
import './styles.css'

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
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    setCurrentFile(file)
    setVideoUrl(URL.createObjectURL(file))

    const formData = new FormData()
    formData.append('video', file)
    formData.append('classifier', selectedClassifier)

    setLoading(true)
    setUploadProgress(0)

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    const res = await fetch(`${config.API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData
    })
    const result = await res.json()

    setUploadProgress(100)
    clearInterval(progressInterval)
    setTimeout(() => {
      setStats(result)
      setLoading(false)
      setUploadProgress(0)
    }, 500)
  }

  const handleReanalyze = async () => {
    if (!currentFile) return

    const formData = new FormData()
    formData.append('video', currentFile)
    formData.append('classifier', selectedClassifier)

    setLoading(true)
    setUploadProgress(0)

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    const res = await fetch(`${config.API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData
    })
    const result = await res.json()

    setUploadProgress(100)
    clearInterval(progressInterval)
    setTimeout(() => {
      setStats(result)
      setLoading(false)
      setUploadProgress(0)
    }, 500)
  }

  const fetchClassifiers = async () => {
    try {
      const res = await fetch(`${config.API_BASE_URL}/classifiers`)
      if (!res.ok) {
        throw new Error(`Failed to fetch classifiers: ${res.status} ${res.statusText}`)
      }
      const data = await res.json()
      console.log('Fetched classifiers:', data.classifiers)
      setClassifiers(data.classifiers || [])

      // Set first classifier as default if available
      if (data.classifiers && data.classifiers.length > 0) {
        setSelectedClassifier(data.classifiers[0].id)
      }
    } catch (error) {
      console.error('Error fetching classifiers:', error)
      throw error
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
    // If clicking on already selected session, deselect it
    if (selectedSession?.session_id === sessionId) {
      setSelectedSession(null)
      return
    }

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
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="basketball-icon">🏀</span>
            <h1>Basketball Box Score Analyzer</h1>
          </div>
          <div className="tagline">AI-Powered Game Analysis</div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          onClick={() => setCurrentView('upload')}
          className={`tab-button ${currentView === 'upload' ? 'active' : ''}`}
        >
          <span className="tab-icon">📤</span>
          Upload & Analyze
        </button>
        <button
          onClick={() => setCurrentView('admin')}
          className={`tab-button ${currentView === 'admin' ? 'active' : ''}`}
        >
          <span className="tab-icon">📊</span>
          Admin Logs
        </button>
      </div>

      <div className="main-content">

      {/* Upload View */}
      {currentView === 'upload' && (
        <div className="dashboard-grid">
          {/* Instructions Card */}
          <div className="card instructions-card">
            <div className="card-header">
              <h2>🎯 How It Works</h2>
            </div>
            <div className="card-body">
              <ol className="instructions-list">
                <li>
                  <strong>Select a Classifier</strong>
                  <p>Choose the AI model that will analyze your video</p>
                </li>
                <li>
                  <strong>Upload Your Video</strong>
                  <p>Select a basketball game video from your device</p>
                </li>
                <li>
                  <strong>Get Analysis</strong>
                  <p>View detailed box scores including points, assists, steals, blocks, and rebounds</p>
                </li>
              </ol>
              <div className="demo-hint">
                <span className="hint-icon">💡</span>
                <p>Tip: Higher resolution videos provide more accurate results!</p>
              </div>
            </div>
          </div>

          {/* Upload Card */}
          <div className="card upload-card">
            <div className="card-header">
              <h2>📤 Upload & Configure</h2>
            </div>
            <div className="card-body">
              {/* Classifier Selection */}
              <div className="form-group">
                <label htmlFor="classifier" className="form-label">
                  Classification Method:
                </label>
                <select
                  id="classifier"
                  value={selectedClassifier}
                  onChange={(e) => setSelectedClassifier(e.target.value)}
                  className="form-select"
                >
                  {classifiers.map((classifier) => (
                    <option key={classifier.id} value={classifier.id}>
                      {classifier.name} - {classifier.description}
                    </option>
                  ))}
                </select>
              </div>

              {/* File Upload */}
              <div className="upload-section">
                <label className="file-upload-label">
                  <input
                    type="file"
                    accept="video/*"
                    onChange={handleUpload}
                    className="file-input"
                  />
                  <div className="file-upload-button">
                    <span className="upload-icon">📁</span>
                    <span>Choose Video File</span>
                  </div>
                </label>

                {currentFile && (
                  <div className="current-file">
                    <span className="file-icon">🎥</span>
                    <span className="file-name">{currentFile.name}</span>
                  </div>
                )}

                {currentFile && !loading && (
                  <button
                    onClick={handleReanalyze}
                    className="reanalyze-button"
                  >
                    <span>🔄</span>
                    Re-analyze with Selected Classifier
                  </button>
                )}
              </div>

              {/* Upload Progress */}
              {loading && (
                <div className="progress-section">
                  <div className="progress-header">
                    <span className="analyzing-text">
                      Analyzing video with {classifiers.find(c => c.id === selectedClassifier)?.name || 'classifier'}...
                    </span>
                    <span className="progress-percentage">{uploadProgress}%</span>
                  </div>
                  <div className="progress-bar-container">
                    <div
                      className="progress-bar"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <div className="progress-animation">
                    <span className="bouncing-ball">🏀</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recent Analyses Card */}
          {sessions.length > 0 && (
            <div className="card recent-card">
              <div className="card-header">
                <h2>📋 Recent Analyses</h2>
              </div>
              <div className="card-body">
                <div className="recent-list">
                  {sessions.slice(0, 3).map((session, idx) => (
                    <div key={idx} className="recent-item" onClick={() => {
                      setCurrentView('admin')
                      selectSession(session.session_id)
                    }}>
                      <div className="recent-time">
                        {new Date(session.timestamp).toLocaleTimeString()}
                      </div>
                      <div className="recent-stats">
                        Points: {session.stats.points} | Assists: {session.stats.assists}
                      </div>
                      {session.evaluation && (
                        <div className="recent-score">
                          {session.evaluation.overall_score}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Video Player */}
      {videoUrl && (
        <div className="card video-card full-width">
          <div className="card-header">
            <h2>🎥 Video Preview</h2>
          </div>
          <div className="card-body">
            <video src={videoUrl} className="video-player" controls />
          </div>
        </div>
      )}

      {/* Results */}
      {stats && (
        <div className="results-section full-width">
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

          {/* Detection Timeline */}
          {stats.detections && stats.detections.length > 0 && (
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
                      {stats.detections.map((det, idx) => (
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
          )}
        </div>
      )}

      {/* Admin View */}
      {currentView === 'admin' && (
        <div className="admin-view">
          <div className="admin-header">
            <h2>🔍 Detection Logs</h2>
            <p className="admin-subtitle">
              View all detection sessions with saved frames showing what the model detected
            </p>
          </div>

          {sessions.length === 0 ? (
            <div className="card empty-state">
              <div className="empty-icon">📂</div>
              <p>No detection sessions yet. Upload a video to create a session.</p>
            </div>
          ) : (
            <div className="admin-content-2col">
              {/* Left Column: Sessions List */}
              <div className="sessions-list">
                <h3>📋 Recent Sessions</h3>
                <div className="sessions-scroll">
                  {sessions.map((session, idx) => {
                    const getScoreClass = (score) => {
                      if (score >= 90) return 'excellent'
                      if (score >= 70) return 'good'
                      if (score >= 50) return 'fair'
                      return 'poor'
                    }

                    const isSelected = selectedSession?.session_id === session.session_id

                    return (
                      <div
                        key={idx}
                        onClick={() => selectSession(session.session_id)}
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
                                // Try to find classifier by ID or name (case-insensitive)
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

              {/* Right Column: Session Details */}
              <div className="session-details-panel">
                {!selectedSession ? (
                  <div className="empty-state">
                    <div className="empty-icon">👈</div>
                    <p>Select a session to view detection details</p>
                  </div>
                ) : (
                  <div className="session-details-content">
                    {/* Evaluation Score Card */}
                    {selectedSession.evaluation && (
                      <div className="card evaluation-card">
                        <div className="card-header">
                          <h3>📊 Evaluation Metrics</h3>
                          <div className={`score-badge large ${
                            selectedSession.evaluation.overall_score >= 90 ? 'excellent' :
                            selectedSession.evaluation.overall_score >= 70 ? 'good' :
                            selectedSession.evaluation.overall_score >= 50 ? 'fair' : 'poor'
                          }`}>
                            {selectedSession.evaluation.overall_score}%
                          </div>
                        </div>
                        <div className="card-body">
                          <div className="metrics-grid">
                            <div className="metric-item">
                              <div className="metric-label">Precision</div>
                              <div className="metric-value">{selectedSession.evaluation.precision}%</div>
                            </div>
                            <div className="metric-item">
                              <div className="metric-label">Recall</div>
                              <div className="metric-value">{selectedSession.evaluation.recall}%</div>
                            </div>
                            <div className="metric-item">
                              <div className="metric-label">F1 Score</div>
                              <div className="metric-value">{selectedSession.evaluation.f1_score}%</div>
                            </div>
                            <div className="metric-item">
                              <div className="metric-label">Stats Accuracy</div>
                              <div className="metric-value">{selectedSession.evaluation.stats_accuracy}%</div>
                            </div>
                          </div>
                          <div className="confusion-matrix">
                            <span className="tp">✓ {selectedSession.evaluation.true_positives} TP</span>
                            <span className="fp">✗ {selectedSession.evaluation.false_positives} FP</span>
                            <span className="fn">⚠ {selectedSession.evaluation.false_negatives} FN</span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="card detections-card">
                      <div className="card-header">
                        <h3>🎬 Detection Frames</h3>
                      </div>
                      <div className="card-body">
                        <div className="detections-grid">
                          {selectedSession.detections.map((det, idx) => (
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
                                src={`${config.API_BASE_URL}/detections/image/${det.frame_image}`}
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
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      </div>
    </div>
  )
}
