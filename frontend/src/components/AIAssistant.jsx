import React, { useRef, useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendChatMessage, sendChatFile, addUserMessage } from '../store/chatSlice'
import { applyAIExtraction, setStatus } from '../store/complaintSlice'
import { toast } from './Toast'

const STAGE_LABELS = {
  idle: '',
  extracting: 'Analyzing document content and extracting key details...',
  awaiting_info: 'Waiting for additional details...',
  reasoning: 'Applying QMS reasoning to assess severity & risk...',
  done: 'Extraction complete',
}

const STAGE_PROGRESS = {
  idle: 0,
  extracting: 45,
  awaiting_info: 60,
  reasoning: 85,
  done: 100,
}

export default function AIAssistant() {
  const dispatch = useDispatch()
  const { sessionId, messages, stage } = useSelector((s) => s.chat)
  const [inputText, setInputText] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const isBusy = stage === 'extracting' || stage === 'reasoning'

  const applyExtractionToForm = (extraction) => {
    const mapped = {}
    Object.entries(extraction).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') mapped[k] = v
    })
    if (Object.keys(mapped).length) {
      dispatch(applyAIExtraction(mapped))
    }
  }

  const handleSend = async () => {
    if (!inputText.trim()) return
    dispatch(addUserMessage(inputText))
    const text = inputText
    setInputText('')

    const result = await dispatch(sendChatMessage({ sessionId, message: text }))
    if (sendChatMessage.fulfilled.match(result)) {
      applyExtractionToForm(result.payload.extraction)
      if (result.payload.is_complete) {
        dispatch(setStatus('Pending'))
        toast('AI finished analyzing the complaint', 'success')
      }
    } else {
      toast(result.payload || 'AI request failed', 'error')
    }
  }

  const handleFile = async (file) => {
    if (!file) return
    const allowed = ['pdf', 'docx', 'eml', 'txt']
    const ext = file.name.split('.').pop().toLowerCase()
    if (!allowed.includes(ext)) {
      toast(`Unsupported file type: .${ext}`, 'error')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      toast('File exceeds 10MB limit', 'error')
      return
    }

    dispatch(addUserMessage(`📎 Uploaded: ${file.name}`))
    const result = await dispatch(sendChatFile({ sessionId, file }))
    if (sendChatFile.fulfilled.match(result)) {
      applyExtractionToForm(result.payload.extraction)
      if (result.payload.is_complete) {
        toast('AI finished analyzing the complaint', 'success')
      }
    } else {
      toast(result.payload || 'File processing failed', 'error')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    handleFile(file)
  }

  return (
    <div className="ai-assistant">
      <div className="ai-header">
        <span className="ai-title">🧪 AI Complaint Intake Assistant</span>
        <span className="beta-tag">BETA</span>
      </div>

      <div
        className={`dropzone ${dragOver ? 'dropzone-active' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="dropzone-icon">⬆</div>
        <p>Drag & drop complaint document here</p>
        <p className="dropzone-sub">or click to browse</p>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept=".pdf,.docx,.eml,.txt"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>
      <p className="format-note">Supported formats: PDF, DOCX, EML, TXT · Max file size: 10MB</p>

      {isBusy && (
        <div className="progress-wrap">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${STAGE_PROGRESS[stage]}%` }} />
          </div>
          <p className="progress-label">{STAGE_LABELS[stage]}</p>
        </div>
      )}

      <div className="chat-window" ref={scrollRef}>
        {messages.map((m, idx) => (
          <div key={idx} className={`chat-bubble chat-${m.role}`}>
            {m.role === 'assistant' && <span className="chat-avatar">🤖</span>}
            <span className="chat-text">{m.text}</span>
          </div>
        ))}
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Ask me anything about this complaint, or paste complaint text / email..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="btn btn-icon" onClick={() => fileInputRef.current?.click()} title="Attach file">
          📎
        </button>
        <button className="btn btn-send" onClick={handleSend} disabled={isBusy}>
          ➤
        </button>
      </div>
    </div>
  )
}
