import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/api'

function genSessionId() {
  return 'session-' + Math.random().toString(36).slice(2) + Date.now()
}

export const sendChatMessage = createAsyncThunk(
  'chat/send',
  async ({ sessionId, message }, { rejectWithValue }) => {
    try {
      const res = await api.post('/chat', { session_id: sessionId, message })
      return res.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Something went wrong contacting the AI assistant.')
    }
  }
)

export const sendChatFile = createAsyncThunk(
  'chat/sendFile',
  async ({ sessionId, file }, { rejectWithValue }) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post(`/upload?session_id=${sessionId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to process the uploaded file.')
    }
  }
)

const initialMessage = {
  role: 'assistant',
  text: "Upload a complaint document or paste the details above. I'll automatically extract the details and populate the form for you.",
}

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    sessionId: genSessionId(),
    messages: [initialMessage],
    stage: 'idle', // idle | extracting | awaiting_info | reasoning | done
    error: null,
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', text: action.payload })
    },
  },
  extraReducers: (builder) => {
    const handlePending = (state) => {
      state.stage = 'extracting'
      state.error = null
    }
    const handleFulfilled = (state, action) => {
      state.stage = action.payload.processing_stage || 'done'
      state.messages.push({ role: 'assistant', text: action.payload.ai_message })
    }
    const handleRejected = (state, action) => {
      state.stage = 'idle'
      state.error = action.payload
      state.messages.push({ role: 'assistant', text: `Sorry — ${action.payload}` })
    }

    builder
      .addCase(sendChatMessage.pending, handlePending)
      .addCase(sendChatMessage.fulfilled, handleFulfilled)
      .addCase(sendChatMessage.rejected, handleRejected)
      .addCase(sendChatFile.pending, handlePending)
      .addCase(sendChatFile.fulfilled, handleFulfilled)
      .addCase(sendChatFile.rejected, handleRejected)
  },
})

export const { addUserMessage } = chatSlice.actions
export default chatSlice.reducer
