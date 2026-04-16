export default function Sidebar({
  isOpen,
  experiments,
  activeTab,
  onSelectTab,
  chatReady,
  dfInfo,
  filename,
  theme,
  onToggleTheme,
  onNewDataset,
  phase,
  messageCount,
}) {
  const statusIcon = (status) => {
    if (status === 'done') return '✅'
    if (status === 'running') return '⚙️'
    if (status === 'error') return '❌'
    return '⏳'
  }

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">📊</div>
          <h1>QAMini</h1>
        </div>
        <p className="sidebar-logo-subtitle">Statistical Analysis</p>
      </div>

      {/* Dataset info */}
      <div className="sidebar-content">
        {dfInfo && (
          <div className="sidebar-card">
            <div className="sidebar-card-title">📁 Dataset</div>
            <div className="sidebar-card-value">{dfInfo.rows?.toLocaleString()}</div>
            <div className="sidebar-card-detail">
              rows × {dfInfo.columns} columns
            </div>
          </div>
        )}

        {/* Experiment nav */}
        <div className="sidebar-card">
          <div className="sidebar-card-title">🧪 Experiments</div>
          <nav className="experiment-nav">
            {experiments.map(exp => (
              <button
                key={exp.id}
                className={`experiment-nav-item ${activeTab === exp.id ? 'active' : ''} ${exp.status}`}
                onClick={() => exp.status === 'done' && onSelectTab(exp.id)}
                disabled={exp.status !== 'done'}
              >
                <span className="experiment-nav-icon">{statusIcon(exp.status)}</span>
                <span className="experiment-nav-label">
                  <span className="experiment-nav-name">{exp.name}</span>
                </span>
              </button>
            ))}
          </nav>
        </div>

        {/* Chat nav item */}
        <button
          className={`chat-nav-item ${activeTab === 'chat' ? 'active' : ''} ${chatReady ? '' : 'disabled'}`}
          onClick={() => chatReady && onSelectTab('chat')}
          disabled={!chatReady}
        >
          <span className="chat-nav-icon">{chatReady ? '💬' : '🔒'}</span>
          <span className="chat-nav-text">
            Ask Questions
            {chatReady && messageCount > 0 && (
              <span className="chat-msg-count">{messageCount}</span>
            )}
          </span>
          {!chatReady && <span className="chat-nav-hint">Complete analysis first</span>}
        </button>
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <button className="sidebar-btn" onClick={onNewDataset}>
          📤 New Dataset
        </button>
        <button className="theme-toggle" onClick={onToggleTheme}>
          <span>{theme === 'dark' ? '🌙 Dark Mode' : '☀️ Light Mode'}</span>
          <div className="theme-toggle-track">
            <div className="theme-toggle-thumb" />
          </div>
        </button>
      </div>
    </aside>
  )
}
