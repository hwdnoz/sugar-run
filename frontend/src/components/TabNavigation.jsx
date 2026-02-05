export default function TabNavigation({ currentView, onViewChange }) {
  return (
    <div className="tab-navigation">
      <button
        onClick={() => onViewChange('upload')}
        className={`tab-button ${currentView === 'upload' ? 'active' : ''}`}
      >
        <span className="tab-icon">📤</span>
        Upload & Analyze
      </button>
      <button
        onClick={() => onViewChange('admin')}
        className={`tab-button ${currentView === 'admin' ? 'active' : ''}`}
      >
        <span className="tab-icon">📊</span>
        Admin Logs
      </button>
    </div>
  )
}
