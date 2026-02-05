import config from './config'

export const api = {
  async analyzeVideo(file, classifier) {
    const formData = new FormData()
    formData.append('video', file)
    formData.append('classifier', classifier)
    const res = await fetch(`${config.API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData
    })
    return res.json()
  },

  async getClassifiers() {
    const res = await fetch(`${config.API_BASE_URL}/classifiers`)
    if (!res.ok) throw new Error(`Failed to fetch classifiers: ${res.status}`)
    return res.json()
  },

  async getSessions() {
    const res = await fetch(`${config.API_BASE_URL}/detections`)
    return res.json()
  },

  async getSession(sessionId) {
    const res = await fetch(`${config.API_BASE_URL}/detections/${sessionId}`)
    return res.json()
  },

  getImageUrl(filename) {
    return `${config.API_BASE_URL}/detections/image/${filename}`
  }
}
