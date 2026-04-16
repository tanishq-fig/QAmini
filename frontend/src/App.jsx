import { useState, useEffect, useCallback, useRef } from 'react'
import UploadScreen from './components/UploadScreen'
import Sidebar from './components/Sidebar'
import ExperimentView from './components/ExperimentView'
import ChatArea from './components/ChatArea'
import InputBar from './components/InputBar'

const API_BASE = 'http://localhost:8000'

function App() {
  const [theme, setTheme] = useState(() =>
    localStorage.getItem('qamini-theme') || 'dark'
  )

  // App phases: upload | analyzing | dashboard
  const [phase, setPhase] = useState('upload')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Analysis state
  const [experiments, setExperiments] = useState([])
  const [activeTab, setActiveTab] = useState(null) // experiment id or 'chat'
  const [expResults, setExpResults] = useState({})
  const [chatReady, setChatReady] = useState(false)
  const [dfInfo, setDfInfo] = useState(null)
  const [filename, setFilename] = useState('')
  const [uploadError, setUploadError] = useState(null)

  // Chat state
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('qamini-theme', theme)
  }, [theme])

  // Poll status during analysis
  useEffect(() => {
    if (phase !== 'analyzing') return

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status`)
        const data = await res.json()
        setExperiments(data.experiments || [])
        setDfInfo(data.df_info)

        if (data.phase === 'ready') {
          setChatReady(true)
          setPhase('dashboard')
          if (!activeTab) setActiveTab(data.experiments[0]?.id || 'exp2')
          clearInterval(interval)
        } else if (data.phase === 'error') {
          setUploadError(data.error || 'Analysis failed')
          setPhase('upload')
          clearInterval(interval)
        }

        // Fetch completed or failed experiment results
        for (const exp of data.experiments) {
          if ((exp.status === 'done' || exp.status === 'failed') && !expResults[exp.id]) {
            fetchExpResult(exp.id)
          }
        }
      } catch {
        /* retry */
      }
    }, 1500)

    return () => clearInterval(interval)
  }, [phase, activeTab, expResults])

  const fetchExpResult = async (expId, retries = 3) => {
    for (let i = 0; i < retries; i++) {
      try {
        const res = await fetch(`${API_BASE}/api/experiment/${expId}`)
        if (res.ok) {
          const data = await res.json()
          setExpResults(prev => ({ ...prev, [expId]: data }))
          return // Success!
        }
        
        // If it's a 404/500, wait a bit and retry
        if (i < retries - 1) await new Promise(r => setTimeout(r, 1000 * (i + 1)))
      } catch (err) {
        if (i === retries - 1) {
          console.error(`Failed to fetch ${expId} after ${retries} attempts:`, err)
          // Set a failure state so we don't spin forever
          setExpResults(prev => ({ 
            ...prev, 
            [expId]: { status: 'failed', error: 'Network Error: Failed to fetch results from server.' } 
          }))
        }
        await new Promise(r => setTimeout(r, 1000 * (i + 1)))
      }
    }
  }

  // Ensure active tab result is fetched if missing
  useEffect(() => {
    if (activeTab && activeTab !== 'chat' && !expResults[activeTab]) {
      const exp = experiments.find(e => e.id === activeTab)
      if (exp && (exp.status === 'done' || exp.status === 'failed')) {
        fetchExpResult(activeTab)
      }
    }
  }, [activeTab, experiments, expResults])

  const handleUpload = useCallback(async (file) => {
    setUploadError(null)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Upload failed')

      setFilename(data.message)
      setPhase('analyzing')
      setExpResults({})
      setChatReady(false)
      setMessages([])
      setActiveTab(null)
    } catch (err) {
      setUploadError(err.message)
    }
  }, [])

  const handleChat = useCallback(async (question) => {
    if (!question.trim() || isLoading) return

    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: question.trim(),
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      })
      if (!res.ok) throw new Error('Chat query failed')
      const data = await res.json()
      const top = data.results?.[0]

      const botMsg = {
        id: Date.now() + 1,
        type: 'bot',
        content: top?.answer || 'No relevant answer found.',
        matchedQuestion: top?.matched_question || '',
        similarity: top?.similarity || 0,
        processingTime: data.processing_time,
        allResults: data.results || [],
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      const errMsg = {
        id: Date.now() + 1,
        type: 'bot',
        content: `Error: ${err.message}`,
        isError: true,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }, [isLoading])

  const handleNewDataset = () => {
    setPhase('upload')
    setExperiments([])
    setExpResults({})
    setChatReady(false)
    setMessages([])
    setActiveTab(null)
    setDfInfo(null)
    setFilename('')
  }

  const toggleTheme = () => setTheme(p => p === 'dark' ? 'light' : 'dark')

  // ─── Upload Phase ────────────────────────────────
  if (phase === 'upload') {
    return (
      <div className="app-container upload-phase">
        <UploadScreen
          onUpload={handleUpload}
          error={uploadError}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </div>
    )
  }

  // ─── Analyzing + Dashboard Phase ─────────────────
  return (
    <div className="app-container">
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(p => !p)}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? '✕' : '☰'}
      </button>

      <Sidebar
        isOpen={sidebarOpen}
        experiments={experiments}
        activeTab={activeTab}
        onSelectTab={(id) => { setActiveTab(id); setSidebarOpen(false) }}
        chatReady={chatReady}
        dfInfo={dfInfo}
        filename={filename}
        theme={theme}
        onToggleTheme={toggleTheme}
        onNewDataset={handleNewDataset}
        phase={phase}
        messageCount={messages.length}
      />

      <main className="main-content">
        {activeTab === 'chat' ? (
          <>
            <ChatArea
              messages={messages}
              isLoading={isLoading}
              onSuggestedQuestion={handleChat}
              dfInfo={dfInfo}
            />
            <InputBar
              onSubmit={handleChat}
              isLoading={isLoading}
              isReady={chatReady}
            />
          </>
        ) : phase === 'analyzing' && !activeTab ? (
          <div className="analyzing-screen">
            <div className="analyzing-spinner" />
            <h2>Analyzing your dataset...</h2>
            <p>Running {experiments.length} experiments. Results will appear as they complete.</p>
            <div className="analyzing-progress">
              {experiments.map(exp => (
                <div key={exp.id} className={`progress-item ${exp.status}`}>
                  <span className="progress-icon">
                    {exp.status === 'done' ? '✅' : exp.status === 'running' ? '⚙️' : '⏳'}
                  </span>
                  <span>{exp.name}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <ExperimentView
            experiment={expResults[activeTab]}
            expMeta={experiments.find(e => e.id === activeTab)}
          />
        )}
      </main>
    </div>
  )
}

export default App
