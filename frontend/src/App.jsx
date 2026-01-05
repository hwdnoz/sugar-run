import React, { useState } from 'react'

export default function App() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [videoUrl, setVideoUrl] = useState(null)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    setVideoUrl(URL.createObjectURL(file))

    const formData = new FormData()
    formData.append('video', file)

    setLoading(true)
    const res = await fetch('http://localhost:8080/analyze', {
      method: 'POST',
      body: formData
    })
    const result = await res.json()
    setStats(result)
    setLoading(false)
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Basketball Box Score Analyzer</h1>
      <input type="file" accept="video/*" onChange={handleUpload} />

      {loading && <p>Analyzing video with YOLO...</p>}

      {videoUrl && (
        <div style={{ marginTop: '20px' }}>
          <video src={videoUrl} width="100%" controls />
        </div>
      )}

      {stats && (
        <div style={{ marginTop: '30px' }}>
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
        </div>
      )}
    </div>
  )
}
