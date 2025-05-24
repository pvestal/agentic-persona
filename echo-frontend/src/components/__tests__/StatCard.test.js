import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatCard from '../StatCard.vue'

describe('StatCard', () => {
  it('renders title and value correctly', () => {
    const wrapper = mount(StatCard, {
      props: {
        title: 'Test Title',
        value: '42',
        icon: '📊'
      }
    })
    
    expect(wrapper.find('h3').text()).toBe('Test Title')
    expect(wrapper.find('.stat-value').text()).toBe('42')
    expect(wrapper.find('.stat-icon').text()).toBe('📊')
  })
  
  it('applies type classes correctly', () => {
    const wrapper = mount(StatCard, {
      props: {
        title: 'Success Rate',
        value: '95%',
        type: 'success'
      }
    })
    
    expect(wrapper.find('.stat-card').classes()).toContain('stat-card-success')
  })
  
  it('shows trend when provided', () => {
    const wrapper = mount(StatCard, {
      props: {
        title: 'Messages',
        value: '150',
        trend: '+10%'
      }
    })
    
    const trend = wrapper.find('.stat-trend')
    expect(trend.exists()).toBe(true)
    expect(trend.text()).toBe('+10%')
  })
  
  it('hides trend when not provided', () => {
    const wrapper = mount(StatCard, {
      props: {
        title: 'Messages',
        value: '150'
      }
    })
    
    expect(wrapper.find('.stat-trend').exists()).toBe(false)
  })
})