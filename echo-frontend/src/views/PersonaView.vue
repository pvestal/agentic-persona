<template>
  <div class="persona-view">
    <div class="persona-header">
      <h1>AI Persona Interface</h1>
      <p>Interactive AI assistant with voice and visual feedback</p>
    </div>
    
    <div class="persona-grid">
      <div class="head-section">
        <AIHead />
      </div>
      
      <div class="chat-section">
        <div class="chat-messages" ref="chatContainer">
          <div v-for="message in messages" :key="message.id" 
               :class="['message', message.sender]">
            <span class="sender">{{ message.sender }}:</span>
            <span class="content">{{ message.content }}</span>
            <span class="time">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>
        
        <div class="chat-input">
          <input 
            v-model="inputMessage" 
            @keyup.enter="sendMessage"
            placeholder="Type a message or use voice..."
            class="message-input"
          />
          <button @click="sendMessage" class="send-btn">Send</button>
        </div>
      </div>
      
      <div class="settings-section">
        <h3>Persona Settings</h3>
        <div class="setting-group">
          <label>Voice Speed</label>
          <input type="range" min="0.5" max="2" step="0.1" v-model="voiceSpeed" />
          <span>{{ voiceSpeed }}x</span>
        </div>
        <div class="setting-group">
          <label>Voice Pitch</label>
          <input type="range" min="0.5" max="2" step="0.1" v-model="voicePitch" />
          <span>{{ voicePitch }}</span>
        </div>
        <div class="setting-group">
          <label>Animation Speed</label>
          <input type="range" min="0.5" max="2" step="0.1" v-model="animationSpeed" />
          <span>{{ animationSpeed }}x</span>
        </div>
        <div class="setting-group">
          <label>Active Agent</label>
          <select v-model="activeAgent">
            <option value="general">General Assistant</option>
            <option value="documentation">Documentation Automator</option>
            <option value="code">Code Review Assistant</option>
            <option value="finance">Financial Planner</option>
            <option value="wealth">Wealth Builder</option>
            <option value="efficiency">Efficiency Expert</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import AIHead from '../components/AIHead.vue'

const messages = ref([])
const inputMessage = ref('')
const chatContainer = ref(null)
const voiceSpeed = ref(1.0)
const voicePitch = ref(1.0)
const animationSpeed = ref(1.0)
const activeAgent = ref('general')

let messageId = 0

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  // Add user message
  messages.value.push({
    id: messageId++,
    sender: 'You',
    content: inputMessage.value,
    timestamp: new Date()
  })
  
  const userInput = inputMessage.value
  inputMessage.value = ''
  
  // Simulate AI response (replace with actual backend call)
  setTimeout(() => {
    const response = generateResponse(userInput)
    messages.value.push({
      id: messageId++,
      sender: 'AI',
      content: response,
      timestamp: new Date()
    })
    
    // Scroll to bottom
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
    
    // Speak the response
    speakResponse(response)
  }, 1000)
}

const generateResponse = (input) => {
  // Simple response generation (replace with actual AI)
  const responses = {
    general: `I understand you said: "${input}". How can I assist you further?`,
    documentation: `I'll help document that. "${input}" will be processed and organized.`,
    code: `Analyzing code request: "${input}". Running review protocols...`,
    finance: `Processing financial query: "${input}". Calculating optimal strategies...`,
    wealth: `Scanning opportunities related to: "${input}". Identifying potential gains...`,
    efficiency: `Optimizing workflow for: "${input}". Finding automation possibilities...`
  }
  
  return responses[activeAgent.value] || responses.general
}

const speakResponse = (text) => {
  // This would connect to the AIHead component
  // For now, using browser speech synthesis
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = voiceSpeed.value
    utterance.pitch = voicePitch.value
    window.speechSynthesis.speak(utterance)
  }
}

const formatTime = (date) => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}
</script>

<style scoped>
.persona-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.persona-header {
  text-align: center;
  margin-bottom: 2rem;
}

.persona-header h1 {
  color: #00ff88;
  margin-bottom: 0.5rem;
}

.persona-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 2rem;
}

.head-section {
  grid-column: 1;
  grid-row: 1;
}

.chat-section {
  grid-column: 2;
  grid-row: 1 / 3;
  background: #1a1a1a;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.settings-section {
  grid-column: 1;
  grid-row: 2;
  background: #1a1a1a;
  border-radius: 1rem;
  padding: 1.5rem;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  max-height: 500px;
}

.message {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: #0a0a0a;
}

.message.You {
  background: #003d20;
  margin-left: 20%;
}

.message.AI {
  background: #1a1a3a;
  margin-right: 20%;
}

.sender {
  font-weight: bold;
  color: #00ff88;
  margin-right: 0.5rem;
}

.time {
  float: right;
  color: #666;
  font-size: 0.875rem;
}

.chat-input {
  display: flex;
  gap: 1rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 0.5rem;
  color: #fff;
}

.send-btn {
  padding: 0.75rem 1.5rem;
  background: #00ff88;
  color: #000;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: bold;
}

.send-btn:hover {
  background: #00cc66;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #888;
}

.setting-group input[type="range"] {
  width: 70%;
  margin-right: 1rem;
}

.setting-group select {
  width: 100%;
  padding: 0.5rem;
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 0.5rem;
  color: #fff;
}

@media (max-width: 1024px) {
  .persona-grid {
    grid-template-columns: 1fr;
  }
  
  .chat-section {
    grid-column: 1;
    grid-row: 2;
  }
  
  .settings-section {
    grid-row: 3;
  }
}
</style>