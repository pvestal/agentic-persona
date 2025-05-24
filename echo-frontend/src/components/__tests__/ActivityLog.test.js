import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ActivityLog from '../ActivityLog.vue'

describe('ActivityLog', () => {
  const mockActivities = [
    {
      id: 1,
      timestamp: '2025-01-23T12:00:00Z',
      type: 'message_processed',
      platform: 'email',
      details: 'Processed email from user@example.com',
      status: 'success'
    },
    {
      id: 2,
      timestamp: '2025-01-23T11:30:00Z',
      type: 'response_sent',
      platform: 'slack',
      details: 'Auto-responded to team channel',
      status: 'success'
    },
    {
      id: 3,
      timestamp: '2025-01-23T11:00:00Z',
      type: 'error',
      platform: 'discord',
      details: 'Failed to connect',
      status: 'error'
    }
  ]
  
  it('renders activities list', () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: mockActivities
      }
    })
    
    const items = wrapper.findAll('.activity-item')
    expect(items).toHaveLength(3)
  })
  
  it('displays activity details correctly', () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: [mockActivities[0]]
      }
    })
    
    const item = wrapper.find('.activity-item')
    expect(item.text()).toContain('Processed email from user@example.com')
    expect(item.find('.platform-badge').text()).toBe('email')
  })
  
  it('applies correct status classes', () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: mockActivities
      }
    })
    
    const items = wrapper.findAll('.activity-item')
    expect(items[0].classes()).toContain('status-success')
    expect(items[2].classes()).toContain('status-error')
  })
  
  it('shows empty state when no activities', () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: []
      }
    })
    
    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.text()).toContain('No activities yet')
  })
  
  it('emits activity-click event when item clicked', async () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: mockActivities
      }
    })
    
    await wrapper.find('.activity-item').trigger('click')
    
    expect(wrapper.emitted('activity-click')).toBeTruthy()
    expect(wrapper.emitted('activity-click')[0][0]).toEqual(mockActivities[0])
  })
  
  it('filters activities by platform', async () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: mockActivities,
        filterPlatform: 'email'
      }
    })
    
    const visibleItems = wrapper.findAll('.activity-item')
    expect(visibleItems).toHaveLength(1)
    expect(visibleItems[0].text()).toContain('email')
  })
  
  it('limits displayed activities when maxItems prop is set', () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: mockActivities,
        maxItems: 2
      }
    })
    
    const items = wrapper.findAll('.activity-item')
    expect(items).toHaveLength(2)
  })
  
  it('formats timestamps correctly', () => {
    const wrapper = mount(ActivityLog, {
      props: {
        activities: [mockActivities[0]]
      }
    })
    
    const timestamp = wrapper.find('.activity-timestamp')
    expect(timestamp.exists()).toBe(true)
    // Timestamp should be formatted (implementation dependent)
    expect(timestamp.text()).toBeTruthy()
  })
})