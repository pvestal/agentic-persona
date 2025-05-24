import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useSystemStore = defineStore('system', {
  state: () => ({
    stats: {
      totalMessagesProcessed: 0,
      activeAgents: 0,
      evolutionCycles: 0,
      learningProgress: {}
    },
    evolutionMetrics: {
      totalEvolutions: 0,
      lastEvolution: null,
      successRate: 0,
      improvements: []
    },
    wsConnected: false,
    loading: false,
    error: null
  }),

  getters: {
    isOperational: (state) => {
      return state.wsConnected && state.stats.activeAgents > 0
    }
  },

  actions: {
    async fetchSystemStats() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.getSystemStats()
        this.stats = {
          totalMessagesProcessed: response.total_messages_processed || 0,
          activeAgents: response.active_agents || 0,
          evolutionCycles: response.evolution_cycles || 0,
          learningProgress: response.learning_progress || {}
        }
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch system stats:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchEvolutionMetrics() {
      try {
        const response = await api.getEvolutionMetrics()
        this.evolutionMetrics = response
      } catch (error) {
        console.error('Failed to fetch evolution metrics:', error)
      }
    },

    async triggerEvolution() {
      try {
        const response = await api.triggerEvolution()
        
        // Update metrics
        if (response.success) {
          this.evolutionMetrics.totalEvolutions++
          this.evolutionMetrics.lastEvolution = new Date()
        }
        
        return response
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    setWebSocketStatus(connected) {
      this.wsConnected = connected
    },

    // Initialize WebSocket listeners
    initializeWebSocket() {
      // Listen for WebSocket connection status
      api.onWebSocketMessage('system-store', (data) => {
        this.handleWebSocketMessage(data)
      })
    },

    // WebSocket message handler
    handleWebSocketMessage(data) {
      if (data.type === 'stats_update') {
        // Update stats in real-time
        this.stats = { ...this.stats, ...data.stats }
      } else if (data.type === 'evolution_complete') {
        // Update evolution metrics
        this.evolutionMetrics.totalEvolutions++
        this.evolutionMetrics.lastEvolution = new Date()
        this.evolutionMetrics.improvements.push(data.improvement)
      }
    },

    // Cleanup
    cleanup() {
      api.offWebSocketMessage('system-store')
    }
  }
})