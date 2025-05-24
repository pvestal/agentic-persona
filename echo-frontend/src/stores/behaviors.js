import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useBehaviorsStore = defineStore('behaviors', {
  state: () => ({
    behaviors: [],
    context: {},
    engineRunning: false,
    notifications: [],
    loading: false,
    error: null
  }),

  getters: {
    activeBehaviors: (state) => {
      return state.behaviors.filter(b => b.trigger_count > 0)
    },
    
    behaviorsByType: (state) => {
      return state.behaviors.reduce((acc, behavior) => {
        const type = behavior.type
        if (!acc[type]) acc[type] = []
        acc[type].push(behavior)
        return acc
      }, {})
    },
    
    recentNotifications: (state) => {
      return state.notifications.slice(-5).reverse()
    }
  },

  actions: {
    async fetchBehaviors() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.getBehaviors()
        this.behaviors = response.behaviors || []
        this.engineRunning = response.engine_running || false
        this.context = response.context || {}
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch behaviors:', error)
      } finally {
        this.loading = false
      }
    },

    async triggerBehavior(behaviorName) {
      try {
        const response = await api.triggerBehavior(behaviorName)
        
        // Update local state
        const behavior = this.behaviors.find(b => b.name === behaviorName)
        if (behavior) {
          behavior.trigger_count++
          behavior.last_triggered = response.timestamp
        }
        
        // Add notification
        if (response.result) {
          this.addNotification(response.result)
        }
        
        return response
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async updateContext(updates) {
      try {
        const response = await api.updateBehaviorContext(updates)
        this.context = response.context || this.context
        return response
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async simulateEvent(eventType, additionalData = {}) {
      try {
        const response = await api.simulateEvent(eventType, additionalData)
        
        // Refresh behaviors to see updated state
        setTimeout(() => this.fetchBehaviors(), 500)
        
        return response
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    addNotification(notification) {
      this.notifications.push({
        ...notification,
        id: Date.now(),
        timestamp: new Date()
      })
      
      // Keep only last 20 notifications
      if (this.notifications.length > 20) {
        this.notifications = this.notifications.slice(-20)
      }
    },

    // WebSocket message handler
    handleWebSocketMessage(data) {
      if (data.type === 'reactive_notification') {
        this.addNotification(data.notification)
        
        // Update behaviors if needed
        this.fetchBehaviors()
      }
    },

    clearNotifications() {
      this.notifications = []
    }
  }
})