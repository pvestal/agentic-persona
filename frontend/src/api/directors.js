import request from '@/utils/request'

export const directorsAPI = {
  // List directors
  list(params = {}) {
    return request({
      url: '/directors',
      method: 'get',
      params
    })
  },

  // Get single director
  get(directorId) {
    return request({
      url: `/directors/${directorId}`,
      method: 'get'
    })
  },

  // Create new director (admin only)
  create(directorData) {
    return request({
      url: '/directors',
      method: 'post',
      data: directorData
    })
  },

  // Update director (admin only)
  update(directorId, directorData) {
    return request({
      url: `/directors/${directorId}`,
      method: 'put',
      data: directorData
    })
  },

  // Delete director (admin only)
  delete(directorId) {
    return request({
      url: `/directors/${directorId}`,
      method: 'delete'
    })
  },

  // Get director performance
  getPerformance(directorId, params = {}) {
    return request({
      url: `/directors/${directorId}/performance`,
      method: 'get',
      params
    })
  },

  // Reset director metrics (admin only)
  resetMetrics(directorId) {
    return request({
      url: `/directors/${directorId}/reset-metrics`,
      method: 'post'
    })
  },

  // Get all director specialties
  getSpecialties() {
    return request({
      url: '/directors/specialties',
      method: 'get'
    })
  }
}