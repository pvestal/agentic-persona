<template>
  <div class="ai-head-wrapper" @click="$emit('click')">
    <div class="ai-head-container" :class="{ 
      'processing': processing,
      'active': status === 'active',
      'listening': status === 'listening',
      'thinking': status === 'thinking'
    }">
      <canvas ref="headCanvas" :width="canvasSize" :height="canvasSize"></canvas>
      
      <!-- Status Ring -->
      <div class="status-ring" :class="statusClass">
        <div class="pulse" v-if="processing"></div>
        <div class="pulse delay" v-if="processing"></div>
      </div>
      
      <!-- Mood Indicator -->
      <div class="mood-indicator" :title="moodDescription">
        {{ moodEmoji }}
      </div>
      
      <!-- Status Lights -->
      <div class="status-lights">
        <div 
          class="status-light"
          v-for="light in statusLights" 
          :key="light.name"
          :class="[light.name, { active: light.active }]"
          :title="light.label"
        >
          <span class="light-core"></span>
        </div>
      </div>
      
      <!-- Activity Display -->
      <transition name="activity">
        <div class="activity-display" v-if="currentActivity">
          <span class="activity-icon">{{ activityIcon }}</span>
          <span class="activity-text">{{ currentActivity }}</span>
        </div>
      </transition>
      
      <!-- Voice Visualizer -->
      <div class="voice-visualizer" v-if="isListening || isSpeaking">
        <div 
          v-for="i in 8" 
          :key="i"
          class="voice-bar"
          :style="{ height: voiceBars[i - 1] + 'px' }"
        ></div>
      </div>
    </div>
    
    <!-- Quick Stats -->
    <div class="quick-stats">
      <div class="stat" v-for="stat in quickStats" :key="stat.label">
        <span class="stat-value">{{ stat.value }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

// Props
const props = defineProps({
  status: {
    type: String,
    default: 'idle' // idle, active, listening, thinking, processing
  },
  processing: {
    type: Boolean,
    default: false
  },
  mood: {
    type: String,
    default: 'neutral' // happy, neutral, focused, tired, excited
  },
  stats: {
    type: Object,
    default: () => ({
      messagesProcessed: 0,
      responseTime: 0,
      accuracy: 0.95
    })
  }
})

const emit = defineEmits(['click', 'speak', 'listen'])

// Canvas and animation
const headCanvas = ref(null)
const canvasSize = 300
let ctx = null
let animationId = null

// Head animation state
const headState = ref({
  eyeOpenness: 1,
  eyeMovement: { x: 0, y: 0 },
  mouthOpenness: 0,
  headTilt: 0,
  headNod: 0,
  glowIntensity: 0.5,
  particleSystem: []
})

// Voice visualization
const isSpeaking = ref(false)
const isListening = ref(false)
const voiceBars = ref([0, 0, 0, 0, 0, 0, 0, 0])
const currentActivity = ref('')

// Computed properties
const statusClass = computed(() => ({
  idle: props.status === 'idle',
  active: props.status === 'active',
  listening: props.status === 'listening',
  thinking: props.status === 'thinking',
  processing: props.processing
}))

const moodEmoji = computed(() => {
  const moods = {
    happy: '😊',
    neutral: '🤖',
    focused: '🧐',
    tired: '😴',
    excited: '🤩',
    curious: '🤔',
    satisfied: '😌'
  }
  return moods[props.mood] || '🤖'
})

const moodDescription = computed(() => {
  const descriptions = {
    happy: 'Feeling great and ready to help!',
    neutral: 'Operating normally',
    focused: 'Deeply concentrated on your tasks',
    tired: 'Processing a lot, might need optimization',
    excited: 'Found something interesting!',
    curious: 'Analyzing patterns',
    satisfied: 'Tasks completed successfully'
  }
  return descriptions[props.mood] || 'Ready to assist'
})

const activityIcon = computed(() => {
  if (props.processing) return '⚡'
  if (props.status === 'listening') return '👂'
  if (props.status === 'thinking') return '🧠'
  if (isSpeaking.value) return '💬'
  return '✨'
})

const statusLights = computed(() => [
  {
    name: 'power',
    label: 'System Power',
    active: true
  },
  {
    name: 'network',
    label: 'Network Status',
    active: props.status !== 'idle'
  },
  {
    name: 'ai',
    label: 'AI Processing',
    active: props.processing || props.status === 'thinking'
  },
  {
    name: 'sync',
    label: 'Data Sync',
    active: props.status === 'active'
  }
])

const quickStats = computed(() => [
  {
    label: 'Messages',
    value: props.stats.messagesProcessed
  },
  {
    label: 'Speed',
    value: props.stats.responseTime + 'ms'
  },
  {
    label: 'Accuracy',
    value: Math.round(props.stats.accuracy * 100) + '%'
  }
])

// Animation functions
const drawHead = () => {
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvasSize, canvasSize)
  
  const centerX = canvasSize / 2
  const centerY = canvasSize / 2
  
  // Apply transformations
  ctx.save()
  ctx.translate(centerX, centerY)
  ctx.rotate(headState.value.headTilt * 0.1)
  ctx.translate(-centerX, -centerY)
  
  // Glow effect
  const glow = headState.value.glowIntensity
  ctx.shadowBlur = 20 * glow
  ctx.shadowColor = props.mood === 'excited' ? '#ff00ff' : '#00ff9f'
  
  // Neural network background
  drawNeuralNetwork()
  
  // Main head shape (more sophisticated)
  ctx.strokeStyle = '#00ff9f'
  ctx.lineWidth = 2
  
  // Head outline
  ctx.beginPath()
  ctx.moveTo(centerX - 60, centerY - 30)
  ctx.bezierCurveTo(
    centerX - 60, centerY - 80,
    centerX + 60, centerY - 80,
    centerX + 60, centerY - 30
  )
  ctx.bezierCurveTo(
    centerX + 60, centerY + 20,
    centerX + 30, centerY + 60,
    centerX, centerY + 70
  )
  ctx.bezierCurveTo(
    centerX - 30, centerY + 60,
    centerX - 60, centerY + 20,
    centerX - 60, centerY - 30
  )
  ctx.stroke()
  
  // Eyes (advanced with pupils)
  drawEyes(centerX, centerY)
  
  // Mouth (more expressive)
  drawMouth(centerX, centerY)
  
  // Activity indicators
  if (props.processing) {
    drawProcessingIndicators(centerX, centerY)
  }
  
  ctx.restore()
  
  // Particle effects
  updateParticles()
  drawParticles()
}

const drawNeuralNetwork = () => {
  ctx.strokeStyle = 'rgba(0, 255, 159, 0.1)'
  ctx.lineWidth = 1
  
  // Draw connecting lines
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      const x1 = 50 + i * 50
      const y1 = 50 + j * 50
      const x2 = 50 + (i + 1) * 50
      const y2 = 50 + j * 50 + Math.sin(Date.now() * 0.001 + i) * 10
      
      ctx.beginPath()
      ctx.moveTo(x1, y1)
      ctx.lineTo(x2, y2)
      ctx.stroke()
    }
  }
}

const drawEyes = (centerX, centerY) => {
  const eyeY = centerY - 30
  const eyeSpacing = 35
  const eyeOpenness = headState.value.eyeOpenness
  const { x: eyeX, y: eyeYOffset } = headState.value.eyeMovement
  
  // Left eye
  drawEye(centerX - eyeSpacing + eyeX, eyeY + eyeYOffset, eyeOpenness)
  
  // Right eye
  drawEye(centerX + eyeSpacing + eyeX, eyeY + eyeYOffset, eyeOpenness)
}

const drawEye = (x, y, openness) => {
  // Eye socket
  ctx.strokeStyle = '#00ff9f'
  ctx.beginPath()
  ctx.ellipse(x, y, 20, 20 * openness, 0, 0, Math.PI * 2)
  ctx.stroke()
  
  // Pupil (follows cursor or looks around)
  if (openness > 0.3) {
    ctx.fillStyle = '#00ff9f'
    ctx.beginPath()
    ctx.arc(x, y, 8, 0, Math.PI * 2)
    ctx.fill()
    
    // Inner pupil
    ctx.fillStyle = '#000'
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
  }
}

const drawMouth = (centerX, centerY) => {
  const mouthY = centerY + 20
  const openness = headState.value.mouthOpenness
  
  ctx.strokeStyle = '#00ff9f'
  ctx.beginPath()
  
  if (isSpeaking.value || openness > 0.1) {
    // Open mouth (speaking)
    ctx.ellipse(centerX, mouthY, 30, 15 * openness, 0, 0, Math.PI)
    
    // Teeth hint
    if (openness > 0.5) {
      ctx.moveTo(centerX - 20, mouthY)
      ctx.lineTo(centerX - 20, mouthY - 5)
      ctx.moveTo(centerX, mouthY)
      ctx.lineTo(centerX, mouthY - 5)
      ctx.moveTo(centerX + 20, mouthY)
      ctx.lineTo(centerX + 20, mouthY - 5)
    }
  } else {
    // Slight smile
    ctx.moveTo(centerX - 25, mouthY)
    ctx.quadraticCurveTo(centerX, mouthY + 10, centerX + 25, mouthY)
  }
  ctx.stroke()
}

const drawProcessingIndicators = (centerX, centerY) => {
  const time = Date.now() * 0.001
  
  // Rotating indicators around head
  for (let i = 0; i < 6; i++) {
    const angle = (i / 6) * Math.PI * 2 + time
    const radius = 100
    const x = centerX + Math.cos(angle) * radius
    const y = centerY + Math.sin(angle) * radius
    
    ctx.fillStyle = `rgba(0, 255, 159, ${0.5 + Math.sin(time + i) * 0.5})`
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, Math.PI * 2)
    ctx.fill()
  }
}

const updateParticles = () => {
  // Add new particles when active
  if (props.status === 'active' || props.processing) {
    if (Math.random() < 0.1) {
      headState.value.particleSystem.push({
        x: Math.random() * canvasSize,
        y: canvasSize,
        vx: (Math.random() - 0.5) * 2,
        vy: -Math.random() * 3 - 1,
        life: 1,
        size: Math.random() * 3 + 1
      })
    }
  }
  
  // Update existing particles
  headState.value.particleSystem = headState.value.particleSystem
    .filter(p => p.life > 0)
    .map(p => ({
      ...p,
      x: p.x + p.vx,
      y: p.y + p.vy,
      life: p.life - 0.02
    }))
}

const drawParticles = () => {
  headState.value.particleSystem.forEach(p => {
    ctx.fillStyle = `rgba(0, 255, 159, ${p.life * 0.5})`
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
    ctx.fill()
  })
}

const animate = () => {
  // Eye blinking
  if (Math.random() < 0.005) {
    headState.value.eyeOpenness = 0.1
  } else {
    headState.value.eyeOpenness = Math.min(1, headState.value.eyeOpenness + 0.1)
  }
  
  // Eye movement
  if (Math.random() < 0.02) {
    headState.value.eyeMovement = {
      x: (Math.random() - 0.5) * 10,
      y: (Math.random() - 0.5) * 5
    }
  } else {
    headState.value.eyeMovement.x *= 0.9
    headState.value.eyeMovement.y *= 0.9
  }
  
  // Mouth animation
  if (isSpeaking.value) {
    headState.value.mouthOpenness = 0.5 + Math.sin(Date.now() * 0.01) * 0.5
  } else {
    headState.value.mouthOpenness *= 0.9
  }
  
  // Head movement
  headState.value.headTilt = Math.sin(Date.now() * 0.0005) * 0.1
  headState.value.headNod = Math.sin(Date.now() * 0.0007) * 0.05
  
  // Glow intensity based on activity
  const targetGlow = props.processing ? 1 : 0.3
  headState.value.glowIntensity += (targetGlow - headState.value.glowIntensity) * 0.1
  
  // Voice visualization
  if (isSpeaking.value || isListening.value) {
    voiceBars.value = voiceBars.value.map(() => 
      10 + Math.random() * 30
    )
  } else {
    voiceBars.value = voiceBars.value.map(v => v * 0.8)
  }
  
  drawHead()
  animationId = requestAnimationFrame(animate)
}

// Activity updates
watch(() => props.status, (newStatus) => {
  switch (newStatus) {
    case 'listening':
      currentActivity.value = 'Listening to your input...'
      break
    case 'thinking':
      currentActivity.value = 'Processing your request...'
      break
    case 'active':
      currentActivity.value = 'Monitoring messages'
      break
    default:
      currentActivity.value = ''
  }
})

watch(() => props.processing, (isProcessing) => {
  if (isProcessing) {
    currentActivity.value = 'Working on it...'
  }
})

onMounted(() => {
  ctx = headCanvas.value.getContext('2d')
  animate()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.ai-head-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.ai-head-container {
  position: relative;
  padding: 1rem;
  background: radial-gradient(circle at center, #1a1a1a, #0a0a0a);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.ai-head-container:hover {
  transform: scale(1.05);
}

.ai-head-container.processing {
  animation: pulse 2s infinite;
}

.ai-head-container.active {
  box-shadow: 0 0 40px rgba(0, 255, 159, 0.4);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

canvas {
  display: block;
  border-radius: 50%;
}

/* Status Ring */
.status-ring {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border: 2px solid transparent;
  border-radius: 50%;
  pointer-events: none;
}

.status-ring.idle {
  border-color: #333;
}

.status-ring.active {
  border-color: #00ff9f;
}

.status-ring.listening {
  border-color: #00d4ff;
  animation: rotate 3s linear infinite;
}

.status-ring.thinking {
  border-color: #ff9f00;
  animation: rotate 1s linear infinite reverse;
}

.status-ring.processing {
  border-color: #ff00ff;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pulse {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border: 2px solid #00ff9f;
  border-radius: 50%;
  animation: pulse-expand 2s infinite;
}

.pulse.delay {
  animation-delay: 1s;
}

@keyframes pulse-expand {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

/* Mood Indicator */
.mood-indicator {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 1.5rem;
  background: #1a1a1a;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #333;
}

/* Status Lights */
.status-lights {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.5rem;
}

.status-light {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1a1a1a;
  border: 1px solid #333;
  position: relative;
  transition: all 0.3s;
}

.status-light.active {
  border-color: currentColor;
}

.status-light.active .light-core {
  opacity: 1;
}

.light-core {
  position: absolute;
  top: 2px;
  left: 2px;
  right: 2px;
  bottom: 2px;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
}

.status-light.power.active {
  color: #00ff9f;
}

.status-light.power .light-core {
  background: #00ff9f;
  box-shadow: 0 0 6px #00ff9f;
}

.status-light.network.active {
  color: #00d4ff;
}

.status-light.network .light-core {
  background: #00d4ff;
  box-shadow: 0 0 6px #00d4ff;
}

.status-light.ai.active {
  color: #ff9f00;
}

.status-light.ai .light-core {
  background: #ff9f00;
  box-shadow: 0 0 6px #ff9f00;
}

.status-light.sync.active {
  color: #ff00ff;
}

.status-light.sync .light-core {
  background: #ff00ff;
  box-shadow: 0 0 6px #ff00ff;
}

/* Activity Display */
.activity-display {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  font-size: 0.8rem;
  color: #aaa;
}

.activity-icon {
  font-size: 1rem;
}

.activity-enter-active,
.activity-leave-active {
  transition: all 0.3s ease;
}

.activity-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

.activity-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* Voice Visualizer */
.voice-visualizer {
  position: absolute;
  bottom: -50px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 3px;
  align-items: flex-end;
  height: 30px;
}

.voice-bar {
  width: 4px;
  background: linear-gradient(to top, #00ff9f, #00d4ff);
  border-radius: 2px;
  transition: height 0.1s ease;
  min-height: 4px;
}

/* Quick Stats */
.quick-stats {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #00ff9f;
}

.stat-label {
  font-size: 0.7rem;
  color: #666;
  text-transform: uppercase;
}
</style>