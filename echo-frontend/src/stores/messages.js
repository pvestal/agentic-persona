import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useMessagesStore = defineStore('messages', {
  state: () => ({
    messages: [],
    processingStats: {
      total: 0,
      successful: 0,
      failed: 0,
      avgResponseTime: 0
    },
    currentMessage: null,
    isProcessing: false,
    error: null
  }),

  getters: {
    recentMessages: (state) => {
      return state.messages.slice(-10).reverse()
    },
    
    successRate: (state) => {
      if (state.processingStats.total === 0) return 0
      return (state.processingStats.successful / state.processingStats.total * 100).toFixed(1)
    }
  },

  actions: {
    async processMessage(text, platform = 'web', context = {}) {
      this.isProcessing = true
      this.error = null
      this.currentMessage = { text, platform, context, timestamp: new Date() }
      
      try {
        const response = await api.processMessage(text, platform, context)
        
        // Add to messages history
        this.messages.push({
          id: response.id || Date.now(),
          input: text,
          output: response.response,
          platform,
          timestamp: new Date(),
          success: response.success,
          duration: response.duration_ms,
          autonomyAction: response.action
        })
        
        // Update stats
        this.processingStats.total++
        if (response.success) {
          this.processingStats.successful++
        } else {
          this.processingStats.failed++
        }
        
        // Update average response time
        this.updateAverageResponseTime(response.duration_ms)
        
        return response
      } catch (error) {
        this.error = error.message
        this.processingStats.failed++
        throw error
      } finally {
        this.isProcessing = false
        this.currentMessage = null
      }
    },

    async sendRealtimeMessage(data) {
      try {
        await api.sendRealtimeMessage(data)
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    updateAverageResponseTime(newTime) {
      const total = this.processingStats.total
      const current = this.processingStats.avgResponseTime
      this.processingStats.avgResponseTime = ((current * (total - 1)) + newTime) / total
    },

    // WebSocket message handler
    handleWebSocketMessage(data) {
      if (data.type === 'message_processed') {
        // Add processed message to history
        this.messages.push({
          id: data.result.id,
          input: data.result.input,
          output: data.result.response,
          platform: data.result.platform,
          timestamp: new Date(),
          success: data.result.success,
          duration: data.result.duration_ms,
          autonomyAction: data.result.action
        })
        
        // Update stats
        this.processingStats.total++
        if (data.result.success) {
          this.processingStats.successful++
        } else {
          this.processingStats.failed++
        }
      }
    },

    clearMessages() {
      this.messages = []
    }
  }
})