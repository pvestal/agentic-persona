import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AIHead from '../AIHead.vue'

// Mock the Canvas API
const mockCanvas = {
  getContext: vi.fn(() => ({
    clearRect: vi.fn(),
    fillStyle: '',
    fillRect: vi.fn(),
    beginPath: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
    closePath: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    translate: vi.fn(),
    rotate: vi.fn()
  }))
}

describe('AIHead', () => {
  beforeEach(() => {
    // Mock canvas element
    HTMLCanvasElement.prototype.getContext = mockCanvas.getContext
  })
  
  it('renders canvas element', () => {
    const wrapper = mount(AIHead)
    
    const canvas = wrapper.find('canvas')
    expect(canvas.exists()).toBe(true)
    expect(canvas.attributes('width')).toBe('400')
    expect(canvas.attributes('height')).toBe('400')
  })
  
  it('applies expression classes', async () => {
    const wrapper = mount(AIHead, {
      props: {
        expression: 'happy'
      }
    })
    
    expect(wrapper.find('.ai-head').classes()).toContain('expression-happy')
    
    await wrapper.setProps({ expression: 'thinking' })
    expect(wrapper.find('.ai-head').classes()).toContain('expression-thinking')
  })
  
  it('toggles speaking state', async () => {
    const wrapper = mount(AIHead, {
      props: {
        isSpeaking: false
      }
    })
    
    expect(wrapper.find('.ai-head').classes()).not.toContain('speaking')
    
    await wrapper.setProps({ isSpeaking: true })
    expect(wrapper.find('.ai-head').classes()).toContain('speaking')
  })
  
  it('applies activity level animations', async () => {
    const wrapper = mount(AIHead, {
      props: {
        activityLevel: 'idle'
      }
    })
    
    expect(wrapper.find('.ai-head').classes()).toContain('activity-idle')
    
    await wrapper.setProps({ activityLevel: 'active' })
    expect(wrapper.find('.ai-head').classes()).toContain('activity-active')
    
    await wrapper.setProps({ activityLevel: 'processing' })
    expect(wrapper.find('.ai-head').classes()).toContain('activity-processing')
  })
  
  it('emits click event when clicked', async () => {
    const wrapper = mount(AIHead)
    
    await wrapper.find('.ai-head').trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })
  
  it('updates canvas on expression change', async () => {
    const wrapper = mount(AIHead, {
      props: {
        expression: 'neutral'
      }
    })
    
    const ctx = mockCanvas.getContext()
    
    // Initial render
    expect(ctx.clearRect).toHaveBeenCalled()
    expect(ctx.beginPath).toHaveBeenCalled()
    
    // Clear mock calls
    vi.clearAllMocks()
    
    // Change expression
    await wrapper.setProps({ expression: 'happy' })
    
    // Canvas should be redrawn
    expect(ctx.clearRect).toHaveBeenCalled()
    expect(ctx.beginPath).toHaveBeenCalled()
  })
  
  it('handles color prop', () => {
    const wrapper = mount(AIHead, {
      props: {
        color: '#FF0000'
      }
    })
    
    const ctx = mockCanvas.getContext()
    // Color should be applied to fillStyle
    expect(wrapper.vm.primaryColor).toBe('#FF0000')
  })
  
  it('animates when enabled', async () => {
    const wrapper = mount(AIHead, {
      props: {
        animate: true
      }
    })
    
    expect(wrapper.find('.ai-head').classes()).toContain('animated')
    
    await wrapper.setProps({ animate: false })
    expect(wrapper.find('.ai-head').classes()).not.toContain('animated')
  })
})