import React from 'react'

const COLORS = {
  Pending: { bg: '#fff4e5', text: '#b45309' },
  'In Progress': { bg: '#e5f0ff', text: '#1d4ed8' },
  Resolved: { bg: '#e6f7ec', text: '#15803d' },
}

export default function StatusBadge({ status }) {
  const c = COLORS[status] || COLORS.Pending
  return (
    <span
      className="status-badge"
      style={{ backgroundColor: c.bg, color: c.text }}
    >
      {status}
    </span>
  )
}
