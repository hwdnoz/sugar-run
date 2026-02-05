export default function VideoUpload({
  classifiers,
  selectedClassifier,
  onClassifierChange,
  currentFile,
  loading,
  uploadProgress,
  onFileSelect,
  onReanalyze
}) {
  return (
    <div className="card upload-card">
      <div className="card-header">
        <h2>📤 Upload & Configure</h2>
      </div>
      <div className="card-body">
        <div className="form-group">
          <label htmlFor="classifier" className="form-label">
            Classification Method:
          </label>
          <select
            id="classifier"
            value={selectedClassifier}
            onChange={(e) => onClassifierChange(e.target.value)}
            className="form-select"
          >
            {classifiers.map((classifier) => (
              <option key={classifier.id} value={classifier.id}>
                {classifier.name} - {classifier.description}
              </option>
            ))}
          </select>
        </div>

        <div className="upload-section">
          <label className="file-upload-label">
            <input
              type="file"
              accept="video/*"
              onChange={onFileSelect}
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
            <button onClick={onReanalyze} className="reanalyze-button">
              <span>🔄</span>
              Re-analyze with Selected Classifier
            </button>
          )}
        </div>

        {loading && (
          <div className="progress-section">
            <div className="progress-header">
              <span className="analyzing-text">
                Analyzing video with {classifiers.find(c => c.id === selectedClassifier)?.name || 'classifier'}...
              </span>
              <span className="progress-percentage">{uploadProgress}%</span>
            </div>
            <div className="progress-bar-container">
              <div className="progress-bar" style={{ width: `${uploadProgress}%` }}></div>
            </div>
            <div className="progress-animation">
              <span className="bouncing-ball">🏀</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
