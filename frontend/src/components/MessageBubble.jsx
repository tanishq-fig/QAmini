import { useState } from 'react'

export default function MessageBubble({ message }) {
  const [contextOpen, setContextOpen] = useState(false)
  const { type, content, matchedQuestion, similarity, isError, processingTime, allResults } = message

  const getSimilarityClass = (score) => {
    if (score >= 70) return 'high'
    if (score >= 40) return 'medium'
    return 'low'
  }

  const getSimilarityLabel = (score) => {
    if (score >= 70) return 'High match'
    if (score >= 40) return 'Moderate match'
    return 'Low match'
  }

  if (type === 'user') {
    return (
      <div className="message user">
        <div className="message-avatar">👤</div>
        <div className="message-content">
          <div className="message-bubble">{content}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="message bot">
      <div className="message-avatar">📊</div>
      <div className="message-content">
        <div className={`message-bubble ${isError ? 'no-result' : ''}`}>
          {content}
        </div>

        {/* Matched question */}
        {matchedQuestion && (
          <div className="message-matched">
            <div className="message-matched-label">Matched query:</div>
            {matchedQuestion}
          </div>
        )}

        {/* Similarity badge */}
        {similarity > 0 && !isError && (
          <span className={`similarity-badge ${getSimilarityClass(similarity)}`}>
            ● {similarity.toFixed(1)}% — {getSimilarityLabel(similarity)}
            {processingTime && (
              <span style={{ opacity: 0.7, marginLeft: 6 }}>
                ({(processingTime * 1000).toFixed(0)}ms)
              </span>
            )}
          </span>
        )}

        {/* Additional results toggle */}
        {allResults && allResults.length > 1 && (
          <>
            <button
              className="context-toggle"
              onClick={() => setContextOpen(prev => !prev)}
            >
              <span className={`context-toggle-arrow ${contextOpen ? 'open' : ''}`}>▼</span>
              {contextOpen ? 'Hide other matches' : `Show ${allResults.length - 1} more match(es)`}
            </button>

            {contextOpen && (
              <div className="context-panel">
                <div className="context-panel-title">Other Matching Results</div>
                {allResults.slice(1).map((r, i) => (
                  <div key={i} style={{ marginBottom: 8, paddingBottom: 8, borderBottom: '1px solid var(--border-primary)' }}>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: 2 }}>
                      ({r.similarity?.toFixed(1)}%) {r.matched_question}
                    </div>
                    <div style={{ fontSize: '0.82rem' }}>{r.answer}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
