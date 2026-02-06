export default function InstructionsCard() {
  return (
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
            <p>View detailed box scores with detected basketball statistics</p>
          </li>
        </ol>
        <div className="demo-hint">
          <span className="hint-icon">💡</span>
          <p>Tip: Higher resolution videos provide more accurate results!</p>
        </div>
      </div>
    </div>
  )
}
