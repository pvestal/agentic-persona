/**
 * AIHead - Open Source Animated AI Avatar
 * MIT License
 */

export class AIHead {
  constructor(config = {}) {
    this.config = {
      container: config.container || document.body,
      width: config.width || 400,
      height: config.height || 400,
      renderer: config.renderer || 'canvas2d',
      theme: config.theme || 'cyberpunk',
      fps: config.fps || 60,
      enableVoice: config.enableVoice !== false,
      enableListening: config.enableListening !== false,
      visualizeAudio: config.visualizeAudio !== false,
      idleAnimation: config.idleAnimation !== false,
      blinkInterval: config.blinkInterval || 4000,
      breathingEffect: config.breathingEffect !== false,
      interactive: config.interactive !== false,
      ...config
    }
    
    this.state = {
      isSpeaking: false,
      isListening: false,
      expression: 'neutral',
      mouthOpenness: 0,
      eyeBlink: 0,
      headRotation: { x: 0, y: 0, z: 0 },
      audioLevel: 0
    }
    
    this.animations = new Map()
    this.eventHandlers = new Map()
    this.recognition = null
    
    this.themes = {
      cyberpunk: {
        primary: '#00ff88',
        secondary: '#00ffff',
        background: '#000000',
        glow: true,
        glowIntensity: 10
      },
      matrix: {
        primary: '#00ff00',
        secondary: '#008800',
        background: '#000000',
        glow: true,
        glowIntensity: 15
      },
      hologram: {
        primary: '#00ccff',
        secondary: '#0088ff',
        background: '#000033',
        glow: true,
        glowIntensity: 20
      },
      retro: {
        primary: '#ff0080',
        secondary: '#8000ff',
        background: '#000040',
        glow: true,
        glowIntensity: 25
      },
      minimal: {
        primary: '#ffffff',
        secondary: '#cccccc',
        background: '#222222',
        glow: false,
        glowIntensity: 0
      }
    }
    
    this.expressions = {
      neutral: { mouth: { openness: 0, curve: 0 }, eyes: { openness: 1 }, eyebrows: { height: 0, angle: 0 } },
      happy: { mouth: { openness: 0.2, curve: 0.5 }, eyes: { openness: 0.8 }, eyebrows: { height: 5, angle: 5 } },
      sad: { mouth: { openness: 0, curve: -0.3 }, eyes: { openness: 0.7 }, eyebrows: { height: -5, angle: -10 } },
      surprised: { mouth: { openness: 0.6, curve: 0 }, eyes: { openness: 1.5 }, eyebrows: { height: 10, angle: 0 } },
      thinking: { mouth: { openness: 0, curve: -0.1 }, eyes: { openness: 0.9 }, eyebrows: { height: 0, angle: -5 } },
      angry: { mouth: { openness: 0.1, curve: -0.4 }, eyes: { openness: 0.6 }, eyebrows: { height: -10, angle: -15 } }
    }
    
    this.init()
  }
  
  init() {
    this.setupContainer()
    this.createRenderer()
    this.setupAudio()
    this.startAnimationLoop()
    this.setupEventListeners()
    
    if (this.config.idleAnimation) {
      this.startIdleAnimations()
    }
  }
  
  setupContainer() {
    const container = typeof this.config.container === 'string' 
      ? document.querySelector(this.config.container)
      : this.config.container
      
    if (!container) {
      throw new Error('AIHead: Container not found')
    }
    
    this.container = container
    this.container.style.position = 'relative'
  }
  
  createRenderer() {
    switch (this.config.renderer) {
      case 'webgl':
        this.createWebGLRenderer()
        break
      case 'ascii':
        this.createASCIIRenderer()
        break
      default:
        this.createCanvas2DRenderer()
    }
  }
  
  createCanvas2DRenderer() {
    this.canvas = document.createElement('canvas')
    this.canvas.width = this.config.width
    this.canvas.height = this.config.height
    this.canvas.style.width = '100%'
    this.canvas.style.height = '100%'
    this.container.appendChild(this.canvas)
    
    this.ctx = this.canvas.getContext('2d')
    
    // Set up theme
    const theme = typeof this.config.theme === 'string' 
      ? this.themes[this.config.theme] 
      : this.config.theme
    this.theme = theme
  }
  
  setupAudio() {
    if (this.config.enableVoice && 'speechSynthesis' in window) {
      this.synthesis = window.speechSynthesis
    }
    
    if (this.config.enableListening && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      this.recognitionAvailable = true
    }
    
    if (this.config.visualizeAudio) {
      this.setupAudioAnalyzer()
    }
  }
  
  setupAudioAnalyzer() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 256
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount)
    } catch (e) {
      console.warn('Audio visualization not available:', e)
    }
  }
  
  startAnimationLoop() {
    const animate = () => {
      this.update()
      this.render()
      this.animationFrame = requestAnimationFrame(animate)
    }
    animate()
  }
  
  update() {
    // Update mouth animation when speaking
    if (this.state.isSpeaking) {
      this.state.mouthOpenness = Math.sin(Date.now() * 0.01) * 0.5 + 0.5
      
      // Update audio level if analyzing
      if (this.analyser && this.dataArray) {
        this.analyser.getByteFrequencyData(this.dataArray)
        const average = this.dataArray.reduce((a, b) => a + b) / this.dataArray.length
        this.state.audioLevel = average / 255
      }
    } else {
      this.state.mouthOpenness *= 0.9
    }
    
    // Eye blink animation
    if (this.state.eyeBlink > 0) {
      this.state.eyeBlink *= 0.85
    }
    
    // Breathing effect
    if (this.config.breathingEffect) {
      const breathe = Math.sin(Date.now() * 0.001) * 0.02
      this.state.headRotation.y = breathe
    }
  }
  
  render() {
    if (!this.ctx) return
    
    const { width, height } = this.canvas
    const centerX = width / 2
    const centerY = height / 2
    
    // Clear canvas
    this.ctx.clearRect(0, 0, width, height)
    
    // Apply theme
    this.ctx.strokeStyle = this.theme.primary
    this.ctx.lineWidth = 2
    
    if (this.theme.glow) {
      this.ctx.shadowBlur = this.theme.glowIntensity
      this.ctx.shadowColor = this.theme.primary
    }
    
    // Save context for transformations
    this.ctx.save()
    
    // Apply head rotation
    this.ctx.translate(centerX, centerY)
    this.ctx.rotate(this.state.headRotation.z)
    this.ctx.translate(-centerX, -centerY)
    
    // Draw skull
    this.drawSkull(centerX, centerY)
    
    // Draw face features
    this.drawEyes(centerX, centerY)
    this.drawNose(centerX, centerY)
    this.drawMouth(centerX, centerY)
    
    // Draw jaw
    this.drawJaw(centerX, centerY)
    
    // Audio visualization
    if (this.config.visualizeAudio && this.state.isSpeaking) {
      this.drawAudioVisualization(centerX, centerY + 120)
    }
    
    this.ctx.restore()
  }
  
  drawSkull(x, y) {
    const expression = this.expressions[this.state.expression]
    
    this.ctx.beginPath()
    this.ctx.ellipse(x, y - 20, 80, 100, 0, 0, Math.PI * 2)
    this.ctx.stroke()
  }
  
  drawEyes(x, y) {
    const expression = this.expressions[this.state.expression]
    const eyeY = y - 50 + this.state.eyeBlink * 10
    const eyeHeight = (20 * expression.eyes.openness) - this.state.eyeBlink * 15
    
    // Left eye
    this.ctx.beginPath()
    this.ctx.ellipse(x - 30, eyeY, 15, Math.max(eyeHeight, 2), 0, 0, Math.PI * 2)
    this.ctx.stroke()
    
    // Right eye
    this.ctx.beginPath()
    this.ctx.ellipse(x + 30, eyeY, 15, Math.max(eyeHeight, 2), 0, 0, Math.PI * 2)
    this.ctx.stroke()
    
    // Eyebrows
    const browY = eyeY - 25 + expression.eyebrows.height
    this.ctx.beginPath()
    this.ctx.moveTo(x - 45, browY - expression.eyebrows.angle)
    this.ctx.lineTo(x - 15, browY + expression.eyebrows.angle)
    this.ctx.stroke()
    
    this.ctx.beginPath()
    this.ctx.moveTo(x + 15, browY + expression.eyebrows.angle)
    this.ctx.lineTo(x + 45, browY - expression.eyebrows.angle)
    this.ctx.stroke()
  }
  
  drawNose(x, y) {
    this.ctx.beginPath()
    this.ctx.moveTo(x, y - 30)
    this.ctx.lineTo(x, y - 10)
    this.ctx.stroke()
  }
  
  drawMouth(x, y) {
    const expression = this.expressions[this.state.expression]
    const mouthY = y + 30
    const openness = expression.mouth.openness + this.state.mouthOpenness * 0.3
    const curve = expression.mouth.curve
    
    this.ctx.beginPath()
    if (openness > 0.1) {
      // Open mouth
      this.ctx.ellipse(x, mouthY, 30, 10 + openness * 20, 0, 0, Math.PI * 2)
    } else {
      // Closed mouth with curve
      this.ctx.moveTo(x - 30, mouthY)
      this.ctx.quadraticCurveTo(x, mouthY + curve * 20, x + 30, mouthY)
    }
    this.ctx.stroke()
  }
  
  drawJaw(x, y) {
    const jawY = y + 60 + this.state.mouthOpenness * 10
    
    this.ctx.beginPath()
    this.ctx.moveTo(x - 80, y - 20)
    this.ctx.quadraticCurveTo(x - 90, y + 40, x - 60, jawY)
    this.ctx.quadraticCurveTo(x, jawY + 20, x + 60, jawY)
    this.ctx.quadraticCurveTo(x + 90, y + 40, x + 80, y - 20)
    this.ctx.stroke()
  }
  
  drawAudioVisualization(x, y) {
    const barCount = 8
    const barWidth = 15
    const maxHeight = 40
    
    for (let i = 0; i < barCount; i++) {
      const barX = x - (barCount * barWidth) / 2 + i * barWidth * 1.5
      const height = Math.random() * maxHeight * this.state.audioLevel
      
      this.ctx.fillStyle = this.theme.secondary
      this.ctx.globalAlpha = 0.3 + Math.random() * 0.7
      this.ctx.fillRect(barX, y - height, barWidth, height)
    }
    this.ctx.globalAlpha = 1
  }
  
  startIdleAnimations() {
    // Random blinks
    setInterval(() => {
      if (Math.random() < 0.3) {
        this.state.eyeBlink = 1
      }
    }, this.config.blinkInterval)
    
    // Subtle head movements
    setInterval(() => {
      if (!this.state.isSpeaking) {
        this.state.headRotation.x = (Math.random() - 0.5) * 0.1
        this.state.headRotation.z = (Math.random() - 0.5) * 0.05
      }
    }, 3000)
  }
  
  setupEventListeners() {
    if (this.config.interactive) {
      this.canvas.addEventListener('click', () => {
        this.emit('click')
      })
      
      this.canvas.addEventListener('mousemove', (e) => {
        if (this.config.followMouse) {
          const rect = this.canvas.getBoundingClientRect()
          const x = (e.clientX - rect.left) / rect.width - 0.5
          const y = (e.clientY - rect.top) / rect.height - 0.5
          this.state.headRotation.x = y * 0.2
          this.state.headRotation.z = x * 0.1
        }
      })
    }
  }
  
  // Public API Methods
  
  speak(text, options = {}) {
    if (!this.synthesis) {
      console.warn('Speech synthesis not available')
      return Promise.reject('Speech synthesis not available')
    }
    
    return new Promise((resolve, reject) => {
      this.synthesis.cancel()
      
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = options.rate || this.config.voice?.rate || 1.0
      utterance.pitch = options.pitch || this.config.voice?.pitch || 1.0
      utterance.volume = options.volume || this.config.voice?.volume || 1.0
      
      if (options.voice) {
        const voices = this.synthesis.getVoices()
        const voice = voices.find(v => v.name === options.voice || v.lang === options.voice)
        if (voice) utterance.voice = voice
      }
      
      utterance.onstart = () => {
        this.state.isSpeaking = true
        this.emit('speaking', { text })
      }
      
      utterance.onend = () => {
        this.state.isSpeaking = false
        this.emit('speechEnd')
        resolve()
      }
      
      utterance.onerror = (error) => {
        this.state.isSpeaking = false
        this.emit('error', { type: 'speech', error })
        reject(error)
      }
      
      this.synthesis.speak(utterance)
    })
  }
  
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel()
      this.state.isSpeaking = false
    }
  }
  
  startListening(options = {}) {
    if (!this.recognitionAvailable) {
      console.warn('Speech recognition not available')
      return
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    this.recognition = new SpeechRecognition()
    
    this.recognition.continuous = options.continuous || false
    this.recognition.interimResults = options.interimResults || true
    this.recognition.lang = options.lang || 'en-US'
    
    this.recognition.onstart = () => {
      this.state.isListening = true
      this.emit('listening')
    }
    
    this.recognition.onresult = (event) => {
      const last = event.results.length - 1
      const transcript = event.results[last][0].transcript
      const isFinal = event.results[last].isFinal
      
      this.emit('transcript', { transcript, isFinal })
      
      if (options.onResult) {
        options.onResult(transcript, isFinal)
      }
    }
    
    this.recognition.onerror = (error) => {
      this.state.isListening = false
      this.emit('error', { type: 'recognition', error })
    }
    
    this.recognition.onend = () => {
      this.state.isListening = false
      this.emit('listeningEnd')
    }
    
    this.recognition.start()
  }
  
  stopListening() {
    if (this.recognition) {
      this.recognition.stop()
      this.recognition = null
      this.state.isListening = false
    }
  }
  
  setExpression(expression) {
    if (typeof expression === 'string' && this.expressions[expression]) {
      this.state.expression = expression
    } else if (typeof expression === 'object') {
      // Custom expression
      this.expressions.custom = expression
      this.state.expression = 'custom'
    }
    this.emit('expressionChange', { expression: this.state.expression })
  }
  
  setTheme(theme) {
    if (typeof theme === 'string' && this.themes[theme]) {
      this.theme = this.themes[theme]
    } else if (typeof theme === 'object') {
      this.theme = { ...this.themes.cyberpunk, ...theme }
    }
  }
  
  animate(animation) {
    if (typeof animation === 'string' && this.animations.has(animation)) {
      return this.playAnimation(this.animations.get(animation))
    } else if (Array.isArray(animation)) {
      return this.playAnimation(animation)
    }
  }
  
  addAnimation(name, frames) {
    this.animations.set(name, frames)
  }
  
  playAnimation(frames) {
    return new Promise((resolve) => {
      let frameIndex = 0
      
      const playFrame = () => {
        if (frameIndex >= frames.length) {
          resolve()
          return
        }
        
        const frame = frames[frameIndex]
        
        // Apply frame properties
        if (frame.rotation) {
          this.state.headRotation = { ...this.state.headRotation, ...frame.rotation }
        }
        if (frame.expression) {
          this.setExpression(frame.expression)
        }
        
        frameIndex++
        setTimeout(playFrame, frame.duration || 100)
      }
      
      playFrame()
    })
  }
  
  // Event system
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, [])
    }
    this.eventHandlers.get(event).push(handler)
  }
  
  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }
  
  emit(event, data) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach(handler => {
        handler(data)
      })
    }
  }
  
  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
    }
    
    this.stopSpeaking()
    this.stopListening()
    
    if (this.audioContext) {
      this.audioContext.close()
    }
    
    if (this.canvas && this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas)
    }
    
    this.eventHandlers.clear()
  }
}

// Default export
export default AIHead