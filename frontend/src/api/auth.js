import request from '@/utils/request'

export const authAPI = {
  login(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    return request({
      url: '/auth/login',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  register(userData) {
    return request({
      url: '/auth/register',
      method: 'post',
      data: userData
    })
  },

  logout() {
    return request({
      url: '/auth/logout',
      method: 'post'
    })
  },

  refreshToken(refreshToken) {
    return request({
      url: '/auth/refresh',
      method: 'post',
      data: { refresh_token: refreshToken }
    })
  },

  getCurrentUser() {
    return request({
      url: '/auth/me',
      method: 'get'
    })
  },

  changePassword(passwordData) {
    return request({
      url: '/auth/change-password',
      method: 'post',
      data: passwordData
    })
  },

  resetPassword(email) {
    return request({
      url: '/auth/reset-password',
      method: 'post',
      data: { email }
    })
  },

  confirmPasswordReset(resetData) {
    return request({
      url: '/auth/reset-password/confirm',
      method: 'post',
      data: resetData
    })
  }
}