import { useState, useRef, useEffect } from 'react'

export default function InputBar({ onSubmit, isLoading, isReady }) {
  const [value, setValue] = useState('')
  const inputRef = useRef(null)

  // Auto focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!value.trim() || isLoading || !isReady) return
    onSubmit(value.trim())
    setValue('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="input-bar-container">
      <div className="input-bar">
        <form className="input-bar-inner" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            className="input-field"
            placeholder={
              isReady
                ? "Ask about your analysis results..."
                : "Waiting for analysis to complete..."
            }
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!isReady || isLoading}
            id="query-input"
            autoComplete="off"
          />
          <button
            type="submit"
            className="input-bar-send"
            disabled={!value.trim() || isLoading || !isReady}
            id="send-btn"
            aria-label="Send question"
          >
            {isLoading ? (
              <div className="spinner" />
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            )}
          </button>
        </form>
        <div className="input-disclaimer">
          Answers are based on your dataset's analysis results via semantic similarity
        </div>
      </div>
    </div>
  )
}
