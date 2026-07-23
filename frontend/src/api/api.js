import axios from 'axios'

// In development, Vite's dev server proxies '/api' -> http://localhost:8000 (see vite.config.js).
// In production (e.g. deployed on Render), set VITE_API_BASE_URL to your deployed backend's
// full URL (e.g. https://pharma-complaint-backend.onrender.com) as a build-time environment
// variable, and requests will go straight there instead of through the dev proxy.
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL,
  timeout: 30000,
})

export default api
