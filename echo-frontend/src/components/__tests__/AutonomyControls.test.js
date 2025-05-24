import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AutonomyControls from '../AutonomyControls.vue'

describe('AutonomyControls', () => {
  const platforms = [
    { id: 'email', name: 'Email', level: 0.5 },
    { id: 'slack', name: 'Slack', level: 0.3 }
  ]
  
  it('renders all platform controls', () => {
    const wrapper = mount(AutonomyControls, {
      props: { platforms }
    })
    
    const controls = wrapper.findAll('.platform-control')
    expect(controls).toHaveLength(2)
    expect(controls[0].find('h4').text()).toBe('Email')
    expect(controls[1].find('h4').text()).toBe('Slack')
  })
  
  it('displays correct autonomy levels', () => {
    const wrapper = mount(AutonomyControls, {
      props: { platforms }
    })
    
    const levelDisplays = wrapper.findAll('.level-display')
    expect(levelDisplays[0].text()).toContain('50%')
    expect(levelDisplays[1].text()).toContain('30%')
  })
  
  it('emits update-level event when slider changes', async () => {
    const wrapper = mount(AutonomyControls, {
      props: { platforms }
    })
    
    const slider = wrapper.find('input[type="range"]')
    await slider.setValue(0.8)
    
    expect(wrapper.emitted('update-level')).toBeTruthy()
    expect(wrapper.emitted('update-level')[0]).toEqual(['email', 0.8])
  })
  
  it('applies correct class based on autonomy level', () => {
    const wrapper = mount(AutonomyControls, {
      props: {
        platforms: [
          { id: 'email', name: 'Email', level: 0.1 },  // Low
          { id: 'slack', name: 'Slack', level: 0.5 },  // Medium
          { id: 'teams', name: 'Teams', level: 0.9 }   // High
        ]
      }
    })
    
    const levelDisplays = wrapper.findAll('.level-display')
    expect(levelDisplays[0].classes()).toContain('level-low')
    expect(levelDisplays[1].classes()).toContain('level-medium')
    expect(levelDisplays[2].classes()).toContain('level-high')
  })
  
  it('disables controls when disabled prop is true', () => {
    const wrapper = mount(AutonomyControls, {
      props: {
        platforms,
        disabled: true
      }
    })
    
    const sliders = wrapper.findAll('input[type="range"]')
    sliders.forEach(slider => {
      expect(slider.attributes('disabled')).toBeDefined()
    })
  })
})