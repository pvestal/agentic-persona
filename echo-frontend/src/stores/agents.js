import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAgentsStore = defineStore('agents', {
  state: () => ({
    agents: {},
    status: {},
    autonomySettings: {
      email: 'suggest',
      sms: 'suggest',
      slack: 'draft',
      discord: 'suggest',
      twitter: 'suggest'
    },
    loading: false,
    error: null
  }),

  getters: {
    activeAgents: (state) => {
      return Object.values(state.agents).filter(agent => agent.active)
    },
    
    agentCount: (state) => {
      return Object.keys(state.agents).length
    },
    
    responderAgent: (state) => {
      return state.agents.responder || null
    }
  },

  actions: {
    async fetchAgents() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.getAgents()
        this.agents = response.agents || {}
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch agents:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchAgentStatus() {
      try {
        const response = await api.getAgentStatus()
        this.status = response
      } catch (error) {
        console.error('Failed to fetch agent status:', error)
      }
    },

    async updateAgentConfig(agentName, config) {
      try {
        const response = await api.updateAgentConfig(agentName, config)
        if (response.success) {
          // Update local state
          if (this.agents[agentName]) {
            this.agents[agentName] = { ...this.agents[agentName], ...config }
          }
        }
        return response
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async fetchAutonomySettings() {
      try {
        const response = await api.getAutonomySettings()
        this.autonomySettings = response.settings || this.autonomySettings
      } catch (error) {
        console.error('Failed to fetch autonomy settings:', error)
      }
    },

    async updateAutonomyLevel(platform, level) {
      try {
        const response = await api.updateAutonomyLevel(platform, level)
        if (response.success) {
          this.autonomySettings[platform] = level
        }
        return response
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // WebSocket message handler
    handleWebSocketMessage(data) {
      if (data.type === 'agent_update') {
        // Update agent data in real-time
        const { agentName, update } = data
        if (this.agents[agentName]) {
          this.agents[agentName] = { ...this.agents[agentName], ...update }
        }
      }
    }
  }
})