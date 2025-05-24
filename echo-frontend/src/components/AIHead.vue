<template>
  <div class="ai-head-container">
    <canvas ref="headCanvas" :width="canvasSize" :height="canvasSize"></canvas>
    <div class="controls">
      <button @click="speak('Hello, I am your AI assistant')" class="control-btn">
        Test Speech
      </button>
      <button @click="toggleListening" class="control-btn" :class="{ active: isListening }">
        {{ isListening ? 'Stop Listening' : 'Start Listening' }}
      </button>
    </div>
    <div class="status">
      <span :class="['status-indicator', { active: isSpeaking }]"></span>
      {{ currentStatus }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const headCanvas = ref(null)
const canvasSize = 400
const isSpeaking = ref(false)
const isListening = ref(false)
const currentStatus = ref('Ready')

let ctx = null
let animationId = null
let mouthOpenness = 0
let eyeBlink = 0
let headTilt = 0

const drawHead = () => {
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvasSize, canvasSize)
  
  // Head outline (skull shape)
  ctx.strokeStyle = '#00ff88'
  ctx.lineWidth = 2
  ctx.shadowBlur = 10
  ctx.shadowColor = '#00ff88'
  
  // Skull
  ctx.beginPath()
  ctx.ellipse(200, 180, 80, 100, 0, 0, Math.PI * 2)
  ctx.stroke()
  
  // Jaw
  ctx.beginPath()
  ctx.moveTo(120, 180)
  ctx.quadraticCurveTo(200, 280 + mouthOpenness * 20, 280, 180)
  ctx.stroke()
  
  // Eyes
  const eyeY = 150 + eyeBlink * 10
  const eyeHeight = 20 - eyeBlink * 15
  
  // Left eye
  ctx.beginPath()
  ctx.ellipse(170, eyeY, 15, eyeHeight, 0, 0, Math.PI * 2)
  ctx.stroke()
  
  // Right eye
  ctx.beginPath()
  ctx.ellipse(230, eyeY, 15, eyeHeight, 0, 0, Math.PI * 2)
  ctx.stroke()
  
  // Nose (simple line)
  ctx.beginPath()
  ctx.moveTo(200, 170)
  ctx.lineTo(200, 190)
  ctx.stroke()
  
  // Mouth
  ctx.beginPath()
  if (isSpeaking.value) {
    // Animated mouth
    ctx.ellipse(200, 230, 30, 10 + mouthOpenness * 15, 0, 0, Math.PI * 2)
  } else {
    // Closed mouth
    ctx.moveTo(170, 230)
    ctx.quadraticCurveTo(200, 235, 230, 230)
  }
  ctx.stroke()
  
  // Audio visualization bars
  if (isSpeaking.value) {
    for (let i = 0; i < 5; i++) {
      const height = Math.random() * 30 + 10
      ctx.fillStyle = `rgba(0, 255, 136, ${0.3 + Math.random() * 0.7})`
      ctx.fillRect(150 + i * 20, 320 - height, 15, height)
    }
  }
}

const animate = () => {
  // Mouth animation
  if (isSpeaking.value) {
    mouthOpenness = Math.sin(Date.now() * 0.01) * 0.5 + 0.5
  } else {
    mouthOpenness *= 0.9
  }
  
  // Random blink
  if (Math.random() < 0.01) {
    eyeBlink = 1
  } else {
    eyeBlink *= 0.9
  }
  
  // Subtle head movement
  headTilt = Math.sin(Date.now() * 0.001) * 0.1
  
  drawHead()
  animationId = requestAnimationFrame(animate)
}

const speak = async (text) => {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel()
    
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1.1
    
    utterance.onstart = () => {
      isSpeaking.value = true
      currentStatus.value = 'Speaking...'
    }
    
    utterance.onend = () => {
      isSpeaking.value = false
      currentStatus.value = 'Ready'
    }
    
    window.speechSynthesis.speak(utterance)
  }
}

const toggleListening = () => {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    alert('Speech recognition not supported in this browser')
    return
  }
  
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

let recognition = null

const startListening = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SpeechRecognition()
  
  recognition.continuous = true
  recognition.interimResults = true
  
  recognition.onstart = () => {
    isListening.value = true
    currentStatus.value = 'Listening...'
  }
  
  recognition.onresult = (event) => {
    const last = event.results.length - 1
    const transcript = event.results[last][0].transcript
    
    if (event.results[last].isFinal) {
      console.log('User said:', transcript)
      // Here you would send to backend
      speak(`I heard you say: ${transcript}`)
    }
  }
  
  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error)
    stopListening()
  }
  
  recognition.start()
}

const stopListening = () => {
  if (recognition) {
    recognition.stop()
    recognition = null
  }
  isListening.value = false
  currentStatus.value = 'Ready'
}

onMounted(() => {
  ctx = headCanvas.value.getContext('2d')
  animate()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  stopListening()
})
</script>

<style scoped>
.ai-head-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background: #0a0a0a;
  border-radius: 1rem;
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.2);
}

canvas {
  background: #000;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.control-btn {
  padding: 0.75rem 1.5rem;
  background: #1a1a1a;
  border: 1px solid #00ff88;
  color: #00ff88;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: #00ff88;
  color: #000;
}

.control-btn.active {
  background: #00ff88;
  color: #000;
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #888;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #333;
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: #00ff88;
  box-shadow: 0 0 10px #00ff88;
}
</style>