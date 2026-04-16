import { useState, useRef, useCallback } from 'react'

export default function UploadScreen({ onUpload, error, theme, onToggleTheme }) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef(null)

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setIsDragging(true)
    else if (e.type === 'dragleave') setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const file = e.dataTransfer?.files[0]
    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file)
    }
  }, [])

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) setSelectedFile(file)
  }

  const handleSubmit = async () => {
    if (!selectedFile || uploading) return
    setUploading(true)
    await onUpload(selectedFile)
    setUploading(false)
  }

  return (
    <div className="upload-screen">
      {/* Theme toggle */}
      <button className="upload-theme-btn" onClick={onToggleTheme} aria-label="Toggle theme">
        {theme === 'dark' ? '☀️' : '🌙'}
      </button>

      <div className="upload-content">
        {/* Logo */}
        <div className="upload-logo">
          <div className="upload-logo-icon">📊</div>
          <h1>QAMini</h1>
          <p className="upload-subtitle">Statistical Analysis Dashboard</p>
        </div>

        {/* Description */}
        <div className="upload-description">
          <p>Upload any CSV dataset and get a comprehensive statistical analysis including:</p>
          <div className="upload-features">
            <span>📈 Data Visualization</span>
            <span>🎯 Sampling Techniques</span>
            <span>🔗 Correlation & SLR</span>
            <span>📐 Multiple Regression</span>
            <span>📊 MLE Estimation</span>
            <span>🧪 T-Tests & Z-Tests</span>
          </div>
          <p className="upload-chat-note">
            💬 After analysis, ask questions about your results using AI-powered semantic search
          </p>
        </div>

        {/* Drop zone */}
        <div
          className={`upload-dropzone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !selectedFile && fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {selectedFile ? (
            <div className="upload-file-info">
              <div className="upload-file-icon">📄</div>
              <div className="upload-file-details">
                <span className="upload-file-name">{selectedFile.name}</span>
                <span className="upload-file-size">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>
              <button
                className="upload-file-remove"
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null) }}
              >
                ✕
              </button>
            </div>
          ) : (
            <>
              <div className="upload-drop-icon">
                {isDragging ? '📥' : '📂'}
              </div>
              <p className="upload-drop-text">
                {isDragging ? 'Drop your CSV here' : 'Drag & drop a CSV file here'}
              </p>
              <p className="upload-drop-hint">or click to browse</p>
            </>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="upload-error">
            ❌ {error}
          </div>
        )}

        {/* Submit button */}
        {selectedFile && (
          <button
            className="upload-submit-btn"
            onClick={handleSubmit}
            disabled={uploading}
          >
            {uploading ? (
              <>
                <span className="upload-spinner" />
                Uploading...
              </>
            ) : (
              <>🚀 Analyze Dataset</>
            )}
          </button>
        )}
      </div>
    </div>
  )
}
