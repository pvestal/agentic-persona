import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Create axios instance
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
request.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    
    // Add auth token to requests
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    const authStore = useAuthStore()
    const originalRequest = error.config
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Try to refresh token
      const refreshed = await authStore.refreshAccessToken()
      
      if (refreshed) {
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`
        return request(originalRequest)
      } else {
        // Refresh failed, redirect to login
        router.push('/auth/login')
      }
    }
    
    // Handle other errors
    if (error.response) {
      const message = error.response.data?.detail || error.response.data?.message || 'Request failed'
      
      // Show error message
      ElMessage.error({
        message,
        duration: 5000
      })
    } else if (error.request) {
      ElMessage.error({
        message: 'No response from server',
        duration: 5000
      })
    } else {
      ElMessage.error({
        message: 'Request configuration error',
        duration: 5000
      })
    }
    
    return Promise.reject(error)
  }
)

export default request

// Export setup function for main.js
export function setupInterceptors() {
  // Additional setup if needed
}