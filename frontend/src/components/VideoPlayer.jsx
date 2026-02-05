export default function VideoPlayer({ videoUrl }) {
  if (!videoUrl) return null

  return (
    <div className="card video-card full-width">
      <div className="card-header">
        <h2>🎥 Video Preview</h2>
      </div>
      <div className="card-body">
        <video src={videoUrl} className="video-player" controls />
      </div>
    </div>
  )
}
