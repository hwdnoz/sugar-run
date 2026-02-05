import { useState, useEffect } from 'react'
import { api } from '../api'

export function useClassifiers() {
  const [classifiers, setClassifiers] = useState([])
  const [selectedClassifier, setSelectedClassifier] = useState('videomae')

  useEffect(() => {
    fetchClassifiers()
  }, [])

  const fetchClassifiers = async () => {
    try {
      const data = await api.getClassifiers()
      setClassifiers(data.classifiers || [])
      if (data.classifiers?.length > 0) {
        setSelectedClassifier(data.classifiers[0].id)
      }
    } catch (error) {
      console.error('Error fetching classifiers:', error)
      throw error
    }
  }

  return { classifiers, selectedClassifier, setSelectedClassifier }
}
