import { useState } from 'react'
import Header from './components/Header'
import TabNavigation from './components/TabNavigation'
import InstructionsCard from './components/InstructionsCard'
import VideoUpload from './components/VideoUpload'
import VideoPlayer from './components/VideoPlayer'
import StatsDisplay from './components/StatsDisplay'
import DetectionTimeline from './components/DetectionTimeline'
import AdminView from './components/AdminView'
import { useClassifiers } from './hooks/useClassifiers'
import { useVideoAnalysis } from './hooks/useVideoAnalysis'
import { useSessions } from './hooks/useSessions'
import './styles.css'

export default function App() {
  const [currentView, setCurrentView] = useState('upload')
  const { classifiers, selectedClassifier, setSelectedClassifier } = useClassifiers()
  const { loading, uploadProgress, stats, currentFile, videoUrl, handleUpload, handleReanalyze } = useVideoAnalysis()
  const { sessions, selectedSession, selectSession } = useSessions(currentView)

  const onFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) handleUpload(file, selectedClassifier)
  }

  return (
    <div className="app-container">
      <Header />
      <TabNavigation currentView={currentView} onViewChange={setCurrentView} />

      <div className="main-content">
        {currentView === 'upload' && (
          <div className="dashboard-grid">
            <InstructionsCard />
            <VideoUpload
              classifiers={classifiers}
              selectedClassifier={selectedClassifier}
              onClassifierChange={setSelectedClassifier}
              currentFile={currentFile}
              loading={loading}
              uploadProgress={uploadProgress}
              onFileSelect={onFileSelect}
              onReanalyze={() => handleReanalyze(selectedClassifier)}
            />
          </div>
        )}

        <VideoPlayer videoUrl={videoUrl} />

        {stats && (
          <div className="results-section full-width">
            <StatsDisplay stats={stats} selectedClassifier={selectedClassifier} />
            <DetectionTimeline detections={stats.detections} />
          </div>
        )}

        {currentView === 'admin' && (
          <AdminView
            sessions={sessions}
            selectedSession={selectedSession}
            classifiers={classifiers}
            onSelectSession={selectSession}
          />
        )}
      </div>
    </div>
  )
}
