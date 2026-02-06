import { useState } from 'react'
import { api as defaultApi } from '../api'

export function useVideoAnalysis(api = defaultApi) {
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [stats, setStats] = useState(null)
  const [currentFile, setCurrentFile] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)

  const analyzeFile = async (file, classifier) => {
    setLoading(true)
    setUploadProgress(0)

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => prev >= 90 ? 90 : prev + 10)
    }, 200)

    try {
      const result = await api.analyzeVideo(file, classifier)
      setUploadProgress(100)
      clearInterval(progressInterval)
      setTimeout(() => {
        setStats(result)
        setLoading(false)
        setUploadProgress(0)
      }, 500)
    } catch (error) {
      clearInterval(progressInterval)
      setLoading(false)
      setUploadProgress(0)
      throw error
    }
  }

  const handleUpload = async (file, classifier) => {
    setCurrentFile(file)
    setVideoUrl(URL.createObjectURL(file))
    await analyzeFile(file, classifier)
  }

  const handleReanalyze = async (classifier) => {
    if (currentFile) {
      await analyzeFile(currentFile, classifier)
    }
  }

  return {
    loading,
    uploadProgress,
    stats,
    currentFile,
    videoUrl,
    handleUpload,
    handleReanalyze
  }
}
