import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(null)
  const refreshToken = ref(null)
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const currentUser = computed(() => user.value)
  const isSuperuser = computed(() => user.value?.is_superuser || false)

  // Actions
  async function login(credentials) {
    isLoading.value = true
    try {
      const response = await authAPI.login(credentials)
      
      // Store tokens
      accessToken.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      // Get user info
      await fetchCurrentUser()
      
      // Redirect to dashboard or intended route
      const redirect = router.currentRoute.value.query.redirect || '/dashboard'
      router.push(redirect)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    } finally {
      isLoading.value = false
    }
  }

  async function register(userData) {
    isLoading.value = true
    try {
      const response = await authAPI.register(userData)
      
      // Auto-login after registration
      return await login({
        username: userData.username,
        password: userData.password
      })
    } catch (error) {
      console.error('Registration error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
    
    // Clear auth state
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    
    // Clear localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Redirect to login
    router.push('/auth/login')
  }

  async function fetchCurrentUser() {
    try {
      const response = await authAPI.getCurrentUser()
      user.value = response.data
    } catch (error) {
      console.error('Failed to fetch user:', error)
      // If fetching user fails, clear auth state
      await logout()
    }
  }

  async function refreshAccessToken() {
    try {
      const response = await authAPI.refreshToken(refreshToken.value)
      
      // Update tokens
      accessToken.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      
      // Update localStorage
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      await logout()
      return false
    }
  }

  function initializeAuth() {
    // Check for stored tokens
    const storedAccessToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    
    if (storedAccessToken && storedRefreshToken) {
      accessToken.value = storedAccessToken
      refreshToken.value = storedRefreshToken
      
      // Verify token and fetch user
      fetchCurrentUser()
    }
  }

  async function changePassword(passwordData) {
    try {
      await authAPI.changePassword(passwordData)
      return { success: true, message: 'Password changed successfully' }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to change password' 
      }
    }
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    
    // Getters
    isAuthenticated,
    currentUser,
    isSuperuser,
    
    // Actions
    login,
    register,
    logout,
    fetchCurrentUser,
    refreshAccessToken,
    initializeAuth,
    changePassword
  }
})