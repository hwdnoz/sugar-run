import { useState, useEffect } from 'react'
import { api } from '../api'

export function useSessions(currentView) {
  const [sessions, setSessions] = useState([])
  const [selectedSession, setSelectedSession] = useState(null)

  useEffect(() => {
    if (currentView === 'admin') {
      fetchSessions()
    }
  }, [currentView])

  const fetchSessions = async () => {
    try {
      const data = await api.getSessions()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
    }
  }

  const selectSession = async (sessionId) => {
    if (selectedSession?.session_id === sessionId) {
      setSelectedSession(null)
      return
    }

    try {
      const data = await api.getSession(sessionId)
      setSelectedSession(data)
    } catch (error) {
      console.error('Error fetching session:', error)
    }
  }

  return { sessions, selectedSession, selectSession, fetchSessions }
}
