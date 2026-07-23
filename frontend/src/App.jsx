import React from 'react'
import ComplaintForm from './components/ComplaintForm'
import AIAssistant from './components/AIAssistant'
import ToastHost from './components/Toast'
import './styles/App.css'

export default function App() {
  return (
    <div className="app-shell">
      <div className="panel panel-left">
        <ComplaintForm />
      </div>
      <div className="panel panel-right">
        <AIAssistant />
      </div>
      <ToastHost />
    </div>
  )
}
