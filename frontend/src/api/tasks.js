import request from '@/utils/request'

export const tasksAPI = {
  // List tasks with filters
  list(params = {}) {
    return request({
      url: '/tasks',
      method: 'get',
      params
    })
  },

  // Get single task
  get(taskId) {
    return request({
      url: `/tasks/${taskId}`,
      method: 'get'
    })
  },

  // Create new task
  create(taskData) {
    return request({
      url: '/tasks',
      method: 'post',
      data: taskData
    })
  },

  // Update task
  update(taskId, taskData) {
    return request({
      url: `/tasks/${taskId}`,
      method: 'put',
      data: taskData
    })
  },

  // Delete task
  delete(taskId) {
    return request({
      url: `/tasks/${taskId}`,
      method: 'delete'
    })
  },

  // Execute task
  execute(taskId, executionData = {}) {
    return request({
      url: `/tasks/${taskId}/execute`,
      method: 'post',
      data: executionData
    })
  },

  // Cancel task
  cancel(taskId) {
    return request({
      url: `/tasks/${taskId}/cancel`,
      method: 'post'
    })
  },

  // Get task statistics
  getStats(params = {}) {
    return request({
      url: '/tasks/stats/summary',
      method: 'get',
      params
    })
  },

  // Bulk create tasks
  bulkCreate(tasksData) {
    return request({
      url: '/tasks/bulk',
      method: 'post',
      data: tasksData
    })
  }
}