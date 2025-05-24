import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../DashboardView.vue'

// Mock child components
vi.mock('../../components/StatCard.vue', () => ({
  default: {
    name: 'StatCard',
    template: '<div class="stat-card-mock">{{ title }}: {{ value }}</div>',
    props: ['title', 'value', 'icon', 'type', 'trend']
  }
}))

vi.mock('../../components/ActivityLog.vue', () => ({
  default: {
    name: 'ActivityLog',
    template: '<div class="activity-log-mock">Activities: {{ activities.length }}</div>',
    props: ['activities']
  }
}))

describe('DashboardView', () => {
  let router
  
  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })
  })
  
  it('renders dashboard header', () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    expect(wrapper.find('h1').text()).toBe('ECHO Dashboard')
  })
  
  it('displays all stat cards', () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    const statCards = wrapper.findAll('.stat-card-mock')
    expect(statCards.length).toBeGreaterThan(0)
    
    // Check for specific stats
    const statTexts = statCards.map(card => card.text())
    expect(statTexts.some(text => text.includes('Messages Today'))).toBe(true)
    expect(statTexts.some(text => text.includes('Response Rate'))).toBe(true)
    expect(statTexts.some(text => text.includes('Active Agents'))).toBe(true)
  })
  
  it('shows activity log with activities', () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
        mocks: {
          activities: [
            { id: 1, type: 'message', details: 'Test activity' }
          ]
        }
      }
    })
    
    const activityLog = wrapper.find('.activity-log-mock')
    expect(activityLog.exists()).toBe(true)
  })
  
  it('updates stats periodically', async () => {
    vi.useFakeTimers()
    
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    const initialValue = wrapper.vm.stats.messagesProcessed
    
    // Simulate time passing
    vi.advanceTimersByTime(5000)
    await wrapper.vm.$nextTick()
    
    // Stats should update
    expect(wrapper.vm.stats.messagesProcessed).not.toBe(initialValue)
    
    vi.useRealTimers()
  })
  
  it('displays platform statistics', () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    const platformStats = wrapper.find('.platform-stats')
    expect(platformStats.exists()).toBe(true)
    
    // Should show stats for different platforms
    expect(platformStats.text()).toContain('Email')
    expect(platformStats.text()).toContain('Slack')
  })
  
  it('shows agent status section', () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    const agentStatus = wrapper.find('.agent-status')
    expect(agentStatus.exists()).toBe(true)
    
    // Should list active agents
    const agentItems = agentStatus.findAll('.agent-item')
    expect(agentItems.length).toBeGreaterThan(0)
  })
  
  it('handles refresh action', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    const refreshButton = wrapper.find('.refresh-button')
    expect(refreshButton.exists()).toBe(true)
    
    await refreshButton.trigger('click')
    
    // Should trigger data refresh
    expect(wrapper.vm.isLoading).toBe(false)
  })
  
  it('displays loading state', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router]
      }
    })
    
    // Set loading state
    wrapper.vm.isLoading = true
    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('.loading-overlay').exists()).toBe(true)
  })
})