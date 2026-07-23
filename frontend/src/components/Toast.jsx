import React, { useEffect, useState } from 'react'

let listeners = []

export function toast(message, type = 'info') {
  listeners.forEach((fn) => fn({ id: Date.now() + Math.random(), message, type }))
}

export default function ToastHost() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    const handler = (t) => {
      setToasts((prev) => [...prev, t])
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== t.id))
      }, 3500)
    }
    listeners.push(handler)
    return () => {
      listeners = listeners.filter((l) => l !== handler)
    }
  }, [])

  return (
    <div className="toast-host">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.message}
        </div>
      ))}
    </div>
  )
}
