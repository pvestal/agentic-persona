import request from '@/utils/request'

export const healthAPI = {
  // Get system health status
  getHealth() {
    return request({
      url: '/health',
      method: 'get'
    })
  },

  // Check readiness
  checkReady() {
    return request({
      url: '/health/ready',
      method: 'get'
    })
  },

  // Check liveness
  checkAlive() {
    return request({
      url: '/health/live',
      method: 'get'
    })
  }
}