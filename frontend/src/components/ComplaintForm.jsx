import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { resetForm, saveComplaint } from '../store/complaintSlice'
import FormField from './FormField'
import StatusBadge from './StatusBadge'
import { toast } from './Toast'

export default function ComplaintForm() {
  const dispatch = useDispatch()
  const { form, status, saving, saveError } = useSelector((s) => s.complaint)

  const handleReset = () => {
    dispatch(resetForm())
    toast('Form reset', 'info')
  }

  const handleSave = async () => {
    const required = [
      'customer_name', 'product_name', 'batch_number', 'manufacturing_date',
      'expiry_date', 'quantity_affected', 'complaint_type', 'complaint_date',
      'detailed_description',
    ]
    const missing = required.filter((f) => !form[f])
    if (missing.length) {
      toast(`Please fill in: ${missing.join(', ')}`, 'error')
      return
    }

    const payload = { ...form, quantity_affected: parseInt(form.quantity_affected, 10) }
    const result = await dispatch(saveComplaint(payload))
    if (saveComplaint.fulfilled.match(result)) {
      toast('Complaint saved successfully', 'success')
    } else {
      toast(result.payload || 'Failed to save complaint', 'error')
    }
  }

  return (
    <div className="complaint-form">
      <div className="form-header">
        <div>
          <h2>Log Customer Complaint</h2>
          <p className="subtitle">API & FDF Quality Assurance Module</p>
        </div>
        <StatusBadge status={status} />
      </div>

      <section className="form-section">
        <h3>1. Origin & Customer Details</h3>
        <div className="field-grid">
          <FormField label="Complaint Source" field="complaint_source" value={form.complaint_source} />
          <FormField label="Customer Name" field="customer_name" value={form.customer_name} />
        </div>
      </section>

      <section className="form-section">
        <h3>2. Product & Batch Identification</h3>
        <div className="field-grid">
          <FormField label="Product Name" field="product_name" value={form.product_name} />
          <FormField label="Product Strength/Grade" field="product_strength" value={form.product_strength} />
          <FormField label="Batch/Lot Number" field="batch_number" value={form.batch_number} />
          <FormField label="Manufacturing Date" field="manufacturing_date" type="date" value={form.manufacturing_date} />
          <FormField label="Expiry Date" field="expiry_date" type="date" value={form.expiry_date} />
          <FormField label="Quantity Affected" field="quantity_affected" type="number" value={form.quantity_affected} />
        </div>
      </section>

      <section className="form-section">
        <h3>3. Complaint Details</h3>
        <div className="field-grid">
          <FormField label="Complaint Type" field="complaint_type" value={form.complaint_type} />
          <FormField label="Complaint Date" field="complaint_date" type="date" value={form.complaint_date} />
          <FormField
            label="Detailed Complaint Description"
            field="detailed_description"
            type="textarea"
            value={form.detailed_description}
            span={2}
          />
        </div>
      </section>

      <section className="form-section">
        <h3>4. Initial Assessment & Priority</h3>
        <div className="field-grid">
          <FormField
            label="Initial Severity"
            field="severity"
            value={form.severity}
            options={['Critical', 'Major', 'Minor']}
          />
          <FormField
            label="Priority"
            field="priority"
            value={form.priority}
            options={['High', 'Medium', 'Low']}
          />
          <FormField
            label="Initial Risk Assessment"
            field="risk_assessment"
            type="textarea"
            value={form.risk_assessment}
            span={2}
          />
        </div>
      </section>

      <section className="form-section">
        <h3>5. Preliminary CAPA Recommendation</h3>
        <div className="field-grid">
          <FormField
            label="CAPA Priority"
            field="capa_priority"
            value={form.capa_priority}
            options={['Immediate', 'Standard', 'Routine']}
          />
          <FormField
            label="Corrective Action"
            field="corrective_action"
            type="textarea"
            value={form.corrective_action}
            span={2}
          />
          <FormField
            label="Preventive Action"
            field="preventive_action"
            type="textarea"
            value={form.preventive_action}
            span={2}
          />
          <FormField
            label="Investigation Scope"
            field="investigation_scope"
            type="textarea"
            value={form.investigation_scope}
            span={2}
          />
        </div>
      </section>

      <div className="form-actions">
        <button className="btn btn-secondary" onClick={handleReset}>
          ↺ Reset Form
        </button>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : '✓ Save Complaint'}
        </button>
      </div>
      {saveError && <p className="error-text">{saveError}</p>}
    </div>
  )
}
