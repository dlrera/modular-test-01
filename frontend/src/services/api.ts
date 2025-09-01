import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // For development, don't redirect on 401 errors if we have mock tokens
    if (error.response?.status === 401) {
      const mockToken = localStorage.getItem('access_token')
      if (mockToken === 'mock-token') {
        // Don't redirect if using mock authentication
        console.warn('API returned 401 but using mock auth, continuing...')
        return Promise.reject(error)
      }
      
      // Only redirect to login if we don't have any tokens
      if (!mockToken) {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api