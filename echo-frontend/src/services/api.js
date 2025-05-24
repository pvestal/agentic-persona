/**
 * API Service for ECHO Frontend
 * Handles all communication with the backend
 */

import { selfImprovement } from './selfImprovement.js'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

class ApiService {
  constructor() {
    this.ws = null
    this.wsCallbacks = new Map()
    this.requestCache = new Map()
    this.pendingRequests = new Map()
  }

  // WebSocket Management
  connectWebSocket() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(WS_URL)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        resolve(this.ws)
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleWebSocketMessage(data)
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        // Attempt to reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000)
      }
    })
  }
  
  handleWebSocketMessage(data) {
    // Notify all registered callbacks
    this.wsCallbacks.forEach((callback) => {
      callback(data)
    })
  }
  
  onWebSocketMessage(id, callback) {
    this.wsCallbacks.set(id, callback)
  }
  
  offWebSocketMessage(id) {
    this.wsCallbacks.delete(id)
  }
  
  // Agent Endpoints
  async getAgents() {
    const response = await fetch(`${API_URL}/agents`)
    if (!response.ok) throw new Error('Failed to fetch agents')
    return response.json()
  }
  
  async getAgentStatus() {
    const response = await fetch(`${API_URL}/agents/status`)
    if (!response.ok) throw new Error('Failed to fetch agent status')
    return response.json()
  }
  
  async updateAgentConfig(agentName, config) {
    const response = await fetch(`${API_URL}/agents/${agentName}/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })
    if (!response.ok) throw new Error('Failed to update agent config')
    return response.json()
  }
  
  // Message Processing
  async processMessage(message, platform = 'web', context = {}) {
    const response = await fetch(`${API_URL}/messages/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, platform, context })
    })
    if (!response.ok) throw new Error('Failed to process message')
    return response.json()
  }
  
  async sendRealtimeMessage(data) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected')
    }
    this.ws.send(JSON.stringify(data))
  }
  
  // Autonomy Settings
  async getAutonomySettings() {
    const response = await fetch(`${API_URL}/agents/autonomy`)
    if (!response.ok) throw new Error('Failed to fetch autonomy settings')
    return response.json()
  }
  
  async updateAutonomyLevel(platform, level) {
    const response = await fetch(`${API_URL}/agents/autonomy/${platform}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ level })
    })
    if (!response.ok) throw new Error('Failed to update autonomy level')
    return response.json()
  }
  
  // Behavior Management
  async getBehaviors() {
    const response = await fetch(`${API_URL}/behaviors`)
    if (!response.ok) throw new Error('Failed to fetch behaviors')
    return response.json()
  }
  
  async triggerBehavior(behaviorName) {
    const response = await fetch(`${API_URL}/behaviors/trigger/${behaviorName}`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to trigger behavior')
    return response.json()
  }
  
  async updateBehaviorContext(updates) {
    const response = await fetch(`${API_URL}/behaviors/context`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    })
    if (!response.ok) throw new Error('Failed to update behavior context')
    return response.json()
  }
  
  async simulateEvent(eventType, additionalData = {}) {
    const response = await fetch(`${API_URL}/behaviors/simulate-event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: eventType, ...additionalData })
    })
    if (!response.ok) throw new Error('Failed to simulate event')
    return response.json()
  }
  
  // Evolution Metrics
  async getEvolutionMetrics() {
    const response = await fetch(`${API_URL}/evolution/metrics`)
    if (!response.ok) throw new Error('Failed to fetch evolution metrics')
    return response.json()
  }
  
  async triggerEvolution() {
    const response = await fetch(`${API_URL}/evolution/trigger`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to trigger evolution')
    return response.json()
  }
  
  // Style Morphing
  async morphStyle(text, style, mood = 'neutral') {
    const response = await fetch(`${API_URL}/style/morph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, style, mood })
    })
    if (!response.ok) throw new Error('Failed to morph style')
    return response.json()
  }
  
  // Audio Processing
  async synthesizeSpeech(text, voice = 'echo') {
    const response = await fetch(`${API_URL}/audio/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice })
    })
    if (!response.ok) throw new Error('Failed to synthesize speech')
    return response.json()
  }
  
  async transcribeAudio(audioBlob) {
    const formData = new FormData()
    formData.append('audio', audioBlob)
    
    const response = await fetch(`${API_URL}/audio/transcribe`, {
      method: 'POST',
      body: formData
    })
    if (!response.ok) throw new Error('Failed to transcribe audio')
    return response.json()
  }
  
  // System Stats
  async getSystemStats() {
    const response = await fetch(`${API_URL}/stats`)
    if (!response.ok) throw new Error('Failed to fetch system stats')
    return response.json()
  }

  // Self-Improvement Integration
  async makeRequest(endpoint, options = {}, metadata = {}) {
    const startTime = Date.now()
    const cacheKey = `${options.method || 'GET'}-${endpoint}`
    
    // Check cache if enabled
    if (this.requestCache.has(cacheKey) && !options.skipCache) {
      const cached = this.requestCache.get(cacheKey)
      if (Date.now() - cached.timestamp < 300000) { // 5 min cache
        return cached.data
      }
    }

    // Deduplicate concurrent requests
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey)
    }

    const requestPromise = fetch(`${API_URL}${endpoint}`, options)
      .then(async response => {
        const success = response.ok
        const data = await response.json()
        
        // Track performance
        selfImprovement.trackApiCall(endpoint, startTime, success, {
          status: response.status,
          method: options.method || 'GET',
          ...metadata
        })

        if (success && options.cache !== false) {
          this.requestCache.set(cacheKey, { data, timestamp: Date.now() })
        }

        this.pendingRequests.delete(cacheKey)
        return data
      })
      .catch(error => {
        selfImprovement.trackApiCall(endpoint, startTime, false, {
          error: error.message,
          ...metadata
        })
        this.pendingRequests.delete(cacheKey)
        throw error
      })

    this.pendingRequests.set(cacheKey, requestPromise)
    return requestPromise
  }

  // Learning & Evolution Endpoints
  async submitLearning(learningData) {
    return this.makeRequest('/evolution/learn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(learningData)
    })
  }

  async submitFeedback(feedback) {
    // Transform feedback to match backend API expectations
    const transformedFeedback = {
      message_id: feedback.responseId || Date.now().toString(),
      feedback_type: feedback.rating >= 4 ? 'approved' : 'rating',
      original_response: feedback.originalResponse || '',
      rating: feedback.rating,
      context: {
        feedback: feedback.feedback,
        timestamp: feedback.timestamp
      }
    }
    
    return this.makeRequest('/learning/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(transformedFeedback)
    })
  }

  async getImprovement(context) {
    // Transform context to match backend API expectations
    const payload = {
      message: context.message || '',
      initial_response: context.response || '',
      context: context.metadata || {}
    }
    
    return this.makeRequest('/learning/improve-response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  }

  async requestEvolution(data) {
    return this.makeRequest('/evolution/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
  }

  // Enhanced methods with self-improvement tracking
  async processMessageEnhanced(message, platform = 'web', context = {}) {
    const interactionId = Date.now().toString()
    
    selfImprovement.trackInteraction('process_message', {
      message: message.substring(0, 100), // Truncate for privacy
      platform,
      context
    }, { started: true })

    try {
      const result = await this.processMessage(message, platform, context)
      
      selfImprovement.trackInteraction('process_message', {
        interactionId,
        responseLength: result.response?.length
      }, { success: true })

      return result
    } catch (error) {
      selfImprovement.trackInteraction('process_message', {
        interactionId,
        error: error.message
      }, { success: false })
      
      throw error
    }
  }

  // Collect user feedback on responses
  async rateResponse(responseId, rating, feedback = '') {
    selfImprovement.collectFeedback('response_rating', rating >= 4, {
      responseId,
      rating,
      feedback
    })

    return this.submitFeedback({
      responseId,
      rating,
      feedback,
      timestamp: new Date().toISOString()
    })
  }
}

// Export singleton instance
export const api = new ApiService()

// Auto-connect WebSocket on load
if (typeof window !== 'undefined') {
  api.connectWebSocket().catch(console.error)
  
  // Set up periodic self-improvement checks
  setInterval(() => {
    const metrics = selfImprovement.exportMetrics()
    if (metrics.interactionCount > 100) {
      selfImprovement.evolveClient().catch(console.error)
    }
  }, 30 * 60 * 1000) // Every 30 minutes
}