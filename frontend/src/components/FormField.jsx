import React from 'react'
import { useDispatch } from 'react-redux'
import { updateField } from '../store/complaintSlice'

export default function FormField({ label, field, value, type = 'text', options = null, span = 1 }) {
  const dispatch = useDispatch()

  const handleChange = (e) => {
    dispatch(updateField({ field, value: e.target.value }))
  }

  return (
    <div className={`form-field ${span === 2 ? 'span-2' : ''}`}>
      <label>{label}</label>
      {options ? (
        <select value={value || ''} onChange={handleChange}>
          <option value="" disabled>
            Awaiting AI extraction...
          </option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : type === 'textarea' ? (
        <textarea
          value={value || ''}
          onChange={handleChange}
          placeholder="Awaiting AI extraction..."
          rows={4}
        />
      ) : (
        <input
          type={type}
          value={value || ''}
          onChange={handleChange}
          placeholder={type === 'date' ? undefined : 'Awaiting AI extraction...'}
        />
      )}
    </div>
  )
}
