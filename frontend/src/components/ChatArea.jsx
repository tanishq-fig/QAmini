import { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'

export default function ChatArea({ messages, isLoading, onSuggestedQuestion, dfInfo }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Generate smart suggestions from dataset info
  const suggestions = dfInfo ? [
    `What columns are in the dataset?`,
    `What are the main correlations?`,
    `What does the regression model show?`,
    `Do the columns follow a normal distribution?`,
    `What are the t-test results?`,
    `What sampling techniques were used?`,
  ] : []

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="chat-area">
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <h2>Ask about your analysis</h2>
          <p>
            All 8 experiments have been completed. Ask any question about the
            results — I'll search through the analysis using semantic similarity.
          </p>
          {suggestions.length > 0 && (
            <div className="suggested-questions">
              {suggestions.map((q, i) => (
                <button
                  key={i}
                  className="suggested-question"
                  onClick={() => onSuggestedQuestion(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="chat-area">
      <div className="chat-messages">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && (
          <div className="typing-indicator">
            <div className="message-avatar" style={{
              background: 'linear-gradient(135deg, #14b8a6, #06b6d4)',
              width: 36, height: 36, borderRadius: 12,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 16, color: 'white', flexShrink: 0,
            }}>📊</div>
            <div className="typing-dots">
              <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
