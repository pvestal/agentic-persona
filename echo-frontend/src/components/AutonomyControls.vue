<template>
  <div class="autonomy-controls">
    <h3>Autonomy Settings</h3>
    
    <div class="control-section">
      <h4>Global Autonomy Level</h4>
      <div class="autonomy-slider">
        <input 
          type="range" 
          min="0" 
          max="3" 
          v-model="globalAutonomy"
          @change="updateAutonomy"
        />
        <div class="autonomy-labels">
          <span :class="{ active: globalAutonomy == 0 }">Learn Only</span>
          <span :class="{ active: globalAutonomy == 1 }">Suggest</span>
          <span :class="{ active: globalAutonomy == 2 }">Draft</span>
          <span :class="{ active: globalAutonomy == 3 }">Auto-Send</span>
        </div>
      </div>
      <p class="description">{{ autonomyDescriptions[globalAutonomy] }}</p>
    </div>
    
    <div class="control-section">
      <h4>Platform-Specific Settings</h4>
      <div class="platform-grid">
        <div v-for="platform in platforms" :key="platform.id" class="platform-card">
          <div class="platform-header">
            <span class="platform-icon">{{ platform.icon }}</span>
            <span class="platform-name">{{ platform.name }}</span>
          </div>
          <select v-model="platform.autonomy" @change="updatePlatformAutonomy(platform)">
            <option value="learn">Learn Only</option>
            <option value="suggest">Suggest</option>
            <option value="draft">Draft</option>
            <option value="auto_send">Auto-Send</option>
          </select>
          <div class="platform-stats">
            <span>{{ platform.stats.processed }} processed</span>
            <span>{{ platform.stats.accuracy }}% accuracy</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="control-section">
      <h4>Response Preferences</h4>
      <div class="preference-grid">
        <div class="preference-item">
          <label>Tone</label>
          <select v-model="preferences.tone">
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
            <option value="formal">Formal</option>
            <option value="friendly">Friendly</option>
          </select>
        </div>
        <div class="preference-item">
          <label>Length</label>
          <select v-model="preferences.length">
            <option value="brief">Brief</option>
            <option value="concise">Concise</option>
            <option value="detailed">Detailed</option>
          </select>
        </div>
        <div class="preference-item">
          <label>Response Time</label>
          <select v-model="preferences.responseTime">
            <option value="immediate">Immediate</option>
            <option value="batched">Batched (hourly)</option>
            <option value="scheduled">Scheduled</option>
          </select>
        </div>
      </div>
    </div>
    
    <div class="control-section">
      <h4>VIP Contacts</h4>
      <div class="vip-list">
        <div v-for="vip in vipContacts" :key="vip.id" class="vip-item">
          <span>{{ vip.name }}</span>
          <select v-model="vip.override">
            <option value="">Use default</option>
            <option value="always_draft">Always draft</option>
            <option value="never_auto">Never auto-send</option>
          </select>
          <button @click="removeVIP(vip.id)" class="remove-btn">×</button>
        </div>
        <div class="add-vip">
          <input 
            v-model="newVIP" 
            placeholder="Add VIP contact..."
            @keyup.enter="addVIP"
          />
          <button @click="addVIP">Add</button>
        </div>
      </div>
    </div>
    
    <div class="control-section">
      <h4>Learning Progress</h4>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.totalProcessed }}</div>
          <div class="stat-label">Messages Processed</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.approvalRate }}%</div>
          <div class="stat-label">Approval Rate</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.patternsLearned }}</div>
          <div class="stat-label">Patterns Learned</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.timesSaved }}h</div>
          <div class="stat-label">Time Saved</div>
        </div>
      </div>
    </div>
    
    <div class="control-section">
      <h4>Safety Controls</h4>
      <div class="safety-options">
        <label>
          <input type="checkbox" v-model="safety.confirmFinancial" />
          Always confirm financial messages
        </label>
        <label>
          <input type="checkbox" v-model="safety.neverAutoPersonal" />
          Never auto-send personal messages
        </label>
        <label>
          <input type="checkbox" v-model="safety.requireApprovalNew" />
          Require approval for new contacts
        </label>
        <label>
          <input type="checkbox" v-model="safety.dailySummary" />
          Send daily summary of actions
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const globalAutonomy = ref(1)

const autonomyDescriptions = [
  'AI observes and learns from your responses but takes no action',
  'AI suggests response options for you to choose from',
  'AI drafts responses but waits for your approval before sending',
  'AI automatically sends appropriate responses based on learned patterns'
]

const platforms = ref([
  { 
    id: 'email', 
    name: 'Email', 
    icon: '📧', 
    autonomy: 'draft',
    stats: { processed: 1234, accuracy: 94 }
  },
  { 
    id: 'sms', 
    name: 'SMS', 
    icon: '💬', 
    autonomy: 'suggest',
    stats: { processed: 567, accuracy: 89 }
  },
  { 
    id: 'slack', 
    name: 'Slack', 
    icon: '💼', 
    autonomy: 'auto_send',
    stats: { processed: 2345, accuracy: 97 }
  },
  { 
    id: 'discord', 
    name: 'Discord', 
    icon: '🎮', 
    autonomy: 'suggest',
    stats: { processed: 123, accuracy: 85 }
  }
])

const preferences = ref({
  tone: 'professional',
  length: 'concise',
  responseTime: 'immediate'
})

const vipContacts = ref([
  { id: 1, name: 'Boss', override: 'always_draft' },
  { id: 2, name: 'Client A', override: 'never_auto' }
])

const newVIP = ref('')

const stats = ref({
  totalProcessed: 4269,
  approvalRate: 92,
  patternsLearned: 156,
  timesSaved: 42
})

const safety = ref({
  confirmFinancial: true,
  neverAutoPersonal: true,
  requireApprovalNew: true,
  dailySummary: false
})

const updateAutonomy = () => {
  console.log('Global autonomy updated:', globalAutonomy.value)
}

const updatePlatformAutonomy = (platform) => {
  console.log('Platform autonomy updated:', platform.name, platform.autonomy)
}

const addVIP = () => {
  if (newVIP.value.trim()) {
    vipContacts.value.push({
      id: Date.now(),
      name: newVIP.value,
      override: ''
    })
    newVIP.value = ''
  }
}

const removeVIP = (id) => {
  vipContacts.value = vipContacts.value.filter(v => v.id !== id)
}
</script>

<style scoped>
.autonomy-controls {
  max-width: 800px;
  margin: 0 auto;
}

h3 {
  color: #00ff88;
  margin-bottom: 2rem;
}

h4 {
  color: #00cc66;
  margin-bottom: 1rem;
}

.control-section {
  background: #1a1a1a;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.autonomy-slider {
  margin: 1rem 0;
}

.autonomy-slider input {
  width: 100%;
  margin-bottom: 1rem;
}

.autonomy-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.autonomy-labels span {
  color: #666;
  transition: color 0.3s ease;
}

.autonomy-labels span.active {
  color: #00ff88;
  font-weight: bold;
}

.description {
  color: #888;
  font-style: italic;
  margin-top: 1rem;
}

.platform-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.platform-card {
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 0.5rem;
  padding: 1rem;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.platform-icon {
  font-size: 1.5rem;
}

.platform-card select {
  width: 100%;
  padding: 0.5rem;
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.platform-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #666;
}

.preference-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.preference-item label {
  display: block;
  margin-bottom: 0.5rem;
  color: #888;
}

.preference-item select {
  width: 100%;
  padding: 0.5rem;
  background: #0a0a0a;
  border: 1px solid #333;
  color: #fff;
  border-radius: 0.25rem;
}

.vip-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.vip-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background: #0a0a0a;
  border-radius: 0.25rem;
}

.vip-item span {
  flex: 1;
}

.vip-item select {
  padding: 0.25rem;
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  border-radius: 0.25rem;
}

.remove-btn {
  background: #ff4444;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
}

.add-vip {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.add-vip input {
  flex: 1;
  padding: 0.5rem;
  background: #0a0a0a;
  border: 1px solid #333;
  color: #fff;
  border-radius: 0.25rem;
}

.add-vip button {
  padding: 0.5rem 1rem;
  background: #00ff88;
  color: #000;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: bold;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #00ff88;
}

.stat-label {
  color: #666;
  font-size: 0.875rem;
}

.safety-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.safety-options label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.safety-options input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}
</style>