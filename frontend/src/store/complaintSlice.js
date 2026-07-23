import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/api'

const emptyForm = {
  complaint_source: '',
  customer_name: '',
  product_name: '',
  product_strength: '',
  batch_number: '',
  manufacturing_date: '',
  expiry_date: '',
  quantity_affected: '',
  complaint_type: '',
  complaint_date: '',
  detailed_description: '',
  severity: '',
  priority: '',
  risk_assessment: '',
  suggested_action: '',
  corrective_action: '',
  preventive_action: '',
  investigation_scope: '',
  capa_priority: '',
}

export const saveComplaint = createAsyncThunk(
  'complaint/save',
  async (formData, { rejectWithValue }) => {
    try {
      const res = await api.post('/complaints', formData)
      return res.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to save complaint')
    }
  }
)

const complaintSlice = createSlice({
  name: 'complaint',
  initialState: {
    form: { ...emptyForm },
    status: 'Pending', // Pending | In Progress | Resolved
    saving: false,
    saveError: null,
    lastSavedId: null,
  },
  reducers: {
    updateField: (state, action) => {
      const { field, value } = action.payload
      state.form[field] = value
    },
    applyAIExtraction: (state, action) => {
      // Merge AI-extracted fields into the form; only overwrite fields the user
      // hasn't already got sitting in the box if you want to be conservative —
      // here we let AI updates win, since the form fields are still fully editable after.
      state.form = { ...state.form, ...action.payload }
    },
    resetForm: (state) => {
      state.form = { ...emptyForm }
      state.status = 'Pending'
      state.saveError = null
      state.lastSavedId = null
    },
    setStatus: (state, action) => {
      state.status = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(saveComplaint.pending, (state) => {
        state.saving = true
        state.saveError = null
      })
      .addCase(saveComplaint.fulfilled, (state, action) => {
        state.saving = false
        state.lastSavedId = action.payload.id
        state.status = action.payload.status
      })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.saving = false
        state.saveError = action.payload
      })
  },
})

export const { updateField, applyAIExtraction, resetForm, setStatus } = complaintSlice.actions
export default complaintSlice.reducer
