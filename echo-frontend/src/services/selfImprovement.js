/**
 * Self-Improvement Module for ECHO Client API
 * Enables the client to learn, adapt, and optimize itself automatically
 */

import { api } from './api.js'

class SelfImprovementService {
  constructor() {
    this.performanceMetrics = new Map()
    this.interactionHistory = []
    this.learningQueue = []
    this.improvementThreshold = 0.8 // Trigger improvements when success rate drops below 80%
    this.isLearning = false
  }

  // Performance Tracking
  trackApiCall(endpoint, startTime, success, metadata = {}) {
    const duration = Date.now() - startTime
    const metric = {
      endpoint,
      duration,
      success,
      timestamp: new Date().toISOString(),
      ...metadata
    }

    // Store metrics by endpoint
    if (!this.performanceMetrics.has(endpoint)) {
      this.performanceMetrics.set(endpoint, [])
    }
    this.performanceMetrics.get(endpoint).push(metric)

    // Trigger learning if performance degrades
    this.checkPerformanceThresholds(endpoint)
  }

  // Interaction Tracking
  trackInteraction(action, context, outcome) {
    const interaction = {
      action,
      context,
      outcome,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    }

    this.interactionHistory.push(interaction)
    this.learningQueue.push(interaction)

    // Process learning queue periodically
    if (this.learningQueue.length >= 10 && !this.isLearning) {
      this.processLearningQueue()
    }
  }

  // Performance Analysis
  checkPerformanceThresholds(endpoint) {
    const metrics = this.performanceMetrics.get(endpoint) || []
    if (metrics.length < 10) return // Need sufficient data

    const recentMetrics = metrics.slice(-20) // Last 20 calls
    const successRate = recentMetrics.filter(m => m.success).length / recentMetrics.length
    const avgDuration = recentMetrics.reduce((sum, m) => sum + m.duration, 0) / recentMetrics.length

    if (successRate < this.improvementThreshold) {
      this.triggerImprovement(endpoint, { successRate, avgDuration })
    }
  }

  // Learning Pipeline
  async processLearningQueue() {
    if (this.isLearning || this.learningQueue.length === 0) return

    this.isLearning = true
    const batch = this.learningQueue.splice(0, 50) // Process in batches

    try {
      // Submit interactions for learning
      const learningData = {
        interactions: batch,
        context: {
          platform: 'web',
          clientVersion: '1.0.0',
          performanceMetrics: this.getAggregatedMetrics()
        }
      }

      const result = await api.submitLearning(learningData)
      
      // Apply learned improvements
      if (result.improvements) {
        await this.applyImprovements(result.improvements)
      }
    } catch (error) {
      console.error('Learning submission failed:', error)
      // Re-queue failed items
      this.learningQueue.unshift(...batch)
    } finally {
      this.isLearning = false
    }
  }

  // Improvement Application
  async triggerImprovement(endpoint, metrics) {
    try {
      const improvement = await api.getImprovement({
        message: `Performance issue on ${endpoint}`,
        response: `Success rate: ${metrics.successRate}, Avg duration: ${metrics.avgDuration}ms`,
        metadata: {
          endpoint,
          metrics,
          recentInteractions: this.interactionHistory.slice(-10)
        }
      })

      if (improvement.improvements_applied) {
        await this.applyImprovements([improvement.improvements_applied])
      }
    } catch (error) {
      console.error('Failed to get improvements:', error)
    }
  }

  async applyImprovements(improvements) {
    for (const improvement of improvements) {
      switch (improvement.type) {
        case 'api_optimization':
          this.optimizeApiCalls(improvement.config)
          break
        case 'caching_strategy':
          this.updateCachingStrategy(improvement.config)
          break
        case 'retry_policy':
          this.updateRetryPolicy(improvement.config)
          break
        case 'batching':
          this.enableRequestBatching(improvement.config)
          break
        case 'prefetching':
          this.configurePrefetching(improvement.config)
          break
      }
    }

    // Trigger evolution if significant improvements
    if (improvements.length > 3) {
      await api.triggerEvolution()
    }
  }

  // Optimization Strategies
  optimizeApiCalls(config) {
    // Implement request debouncing
    if (config.debounce) {
      this.debounceTimers = new Map()
    }

    // Implement request deduplication
    if (config.deduplicate) {
      this.pendingRequests = new Map()
    }
  }

  updateCachingStrategy(config) {
    this.cacheConfig = {
      ttl: config.ttl || 300000, // 5 minutes default
      maxSize: config.maxSize || 100,
      endpoints: config.endpoints || []
    }
    this.cache = new Map()
  }

  updateRetryPolicy(config) {
    this.retryConfig = {
      maxAttempts: config.maxAttempts || 3,
      backoffMultiplier: config.backoffMultiplier || 2,
      initialDelay: config.initialDelay || 1000
    }
  }

  enableRequestBatching(config) {
    this.batchConfig = {
      maxBatchSize: config.maxBatchSize || 10,
      batchDelay: config.batchDelay || 100,
      endpoints: config.endpoints || []
    }
    this.batchQueue = new Map()
  }

  configurePrefetching(config) {
    this.prefetchConfig = {
      patterns: config.patterns || [],
      maxPrefetch: config.maxPrefetch || 5
    }
  }

  // Feedback Collection
  collectFeedback(action, satisfied, details = {}) {
    const feedback = {
      action,
      satisfied,
      details,
      timestamp: new Date().toISOString()
    }

    // Submit feedback immediately for high-priority learning
    api.submitFeedback(feedback).catch(console.error)

    // Track for local analysis
    this.trackInteraction(action, details, { satisfied })
  }

  // Self-Modification
  async evolveClient() {
    const metrics = this.getAggregatedMetrics()
    const patterns = this.detectPatterns()

    try {
      const evolution = await api.requestEvolution({
        metrics,
        patterns,
        capabilities: this.getCurrentCapabilities()
      })

      if (evolution.newBehaviors) {
        await this.integrateNewBehaviors(evolution.newBehaviors)
      }

      return evolution
    } catch (error) {
      console.error('Evolution failed:', error)
      return null
    }
  }

  // Pattern Detection
  detectPatterns() {
    const patterns = {
      timeBasedUsage: this.analyzeTimePatterns(),
      frequentActions: this.analyzeActionFrequency(),
      errorPatterns: this.analyzeErrorPatterns(),
      performanceBottlenecks: this.identifyBottlenecks()
    }
    return patterns
  }

  analyzeTimePatterns() {
    const hourlyUsage = new Array(24).fill(0)
    this.interactionHistory.forEach(interaction => {
      const hour = new Date(interaction.timestamp).getHours()
      hourlyUsage[hour]++
    })
    return hourlyUsage
  }

  analyzeActionFrequency() {
    const frequency = {}
    this.interactionHistory.forEach(interaction => {
      frequency[interaction.action] = (frequency[interaction.action] || 0) + 1
    })
    return Object.entries(frequency)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
  }

  analyzeErrorPatterns() {
    const errors = {}
    this.performanceMetrics.forEach((metrics, endpoint) => {
      const failures = metrics.filter(m => !m.success)
      if (failures.length > 0) {
        errors[endpoint] = {
          count: failures.length,
          rate: failures.length / metrics.length,
          lastError: failures[failures.length - 1]
        }
      }
    })
    return errors
  }

  identifyBottlenecks() {
    const bottlenecks = []
    this.performanceMetrics.forEach((metrics, endpoint) => {
      const avgDuration = metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length
      if (avgDuration > 2000) { // Calls taking more than 2 seconds
        bottlenecks.push({ endpoint, avgDuration })
      }
    })
    return bottlenecks.sort((a, b) => b.avgDuration - a.avgDuration)
  }

  // Utility Methods
  getAggregatedMetrics() {
    const aggregated = {}
    this.performanceMetrics.forEach((metrics, endpoint) => {
      aggregated[endpoint] = {
        totalCalls: metrics.length,
        successRate: metrics.filter(m => m.success).length / metrics.length,
        avgDuration: metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length
      }
    })
    return aggregated
  }

  getCurrentCapabilities() {
    return {
      caching: !!this.cacheConfig,
      batching: !!this.batchConfig,
      prefetching: !!this.prefetchConfig,
      retryPolicy: !!this.retryConfig,
      performanceTracking: true,
      patternDetection: true,
      selfModification: true
    }
  }

  async integrateNewBehaviors(behaviors) {
    // Dynamically update client behavior based on evolution results
    for (const behavior of behaviors) {
      console.log(`Integrating new behavior: ${behavior.name}`)
      // This would involve dynamic code loading or configuration updates
      // For security, behaviors would be validated and sandboxed
    }
  }

  // Export metrics for monitoring
  exportMetrics() {
    return {
      performance: this.getAggregatedMetrics(),
      patterns: this.detectPatterns(),
      interactionCount: this.interactionHistory.length,
      learningQueueSize: this.learningQueue.length,
      capabilities: this.getCurrentCapabilities()
    }
  }
}

// Create and export singleton instance
export const selfImprovement = new SelfImprovementService()

// Auto-start learning cycle
if (typeof window !== 'undefined') {
  // Process learning queue every 5 minutes
  setInterval(() => {
    selfImprovement.processLearningQueue()
  }, 5 * 60 * 1000)

  // Export metrics every hour for monitoring
  setInterval(() => {
    const metrics = selfImprovement.exportMetrics()
    console.log('Self-improvement metrics:', metrics)
  }, 60 * 60 * 1000)
}