<template>
  <div class="control-center">
    <!-- Status Bar -->
    <div class="status-bar">
      <div class="status-item" :class="{ active: systemStatus.active }">
        <span class="status-indicator"></span>
        <span>{{ systemStatus.active ? 'ACTIVE' : 'STANDBY' }}</span>
      </div>
      <div class="status-item">
        <span class="metric">{{ stats.messagesProcessed }}</span>
        <span class="label">Processed Today</span>
      </div>
      <div class="status-item">
        <span class="metric">{{ stats.pendingActions }}</span>
        <span class="label">Pending Actions</span>
      </div>
      <div class="status-item">
        <span class="metric">{{ stats.avgResponseTime }}ms</span>
        <span class="label">Avg Response</span>
      </div>
      <div class="status-item llm-status">
        <span class="provider-badge" :class="currentProvider">{{ currentProvider }}</span>
        <span class="model">{{ currentModel }}</span>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="main-grid">
      <!-- Left Panel: Quick Actions -->
      <div class="panel quick-actions">
        <h3>Quick Actions</h3>
        <div class="action-grid">
          <button @click="processAllPending" class="action-btn primary">
            <span class="icon">⚡</span>
            Process All Pending
            <kbd>⌘P</kbd>
          </button>
          <button @click="toggleAutonomy" class="action-btn">
            <span class="icon">🤖</span>
            {{ autonomyEnabled ? 'Disable' : 'Enable' }} Auto Mode
            <kbd>⌘A</kbd>
          </button>
          <button @click="reviewQueue" class="action-btn">
            <span class="icon">📋</span>
            Review Queue
            <kbd>⌘R</kbd>
          </button>
          <button @click="openSettings" class="action-btn">
            <span class="icon">⚙️</span>
            Settings
            <kbd>⌘,</kbd>
          </button>
        </div>

        <!-- Platform Controls -->
        <h3>Platform Controls</h3>
        <div class="platform-controls">
          <div 
            v-for="platform in platforms" 
            :key="platform.id"
            class="platform-control"
            :class="{ active: platform.connected, processing: platform.processing }"
          >
            <div class="platform-header">
              <span class="platform-icon">{{ platform.icon }}</span>
              <span class="platform-name">{{ platform.name }}</span>
              <div class="platform-status">
                <span v-if="platform.connected" class="connected">●</span>
                <span v-else class="disconnected">○</span>
              </div>
            </div>
            
            <div class="platform-stats">
              <div class="stat">
                <span class="value">{{ platform.unread }}</span>
                <span class="label">unread</span>
              </div>
              <div class="stat">
                <span class="value">{{ platform.todayCount }}</span>
                <span class="label">today</span>
              </div>
            </div>

            <div class="autonomy-slider">
              <label>Autonomy Level</label>
              <input 
                type="range" 
                min="0" 
                max="4" 
                v-model="platform.autonomyLevel"
                @change="updateAutonomy(platform)"
              >
              <div class="level-labels">
                <span>Off</span>
                <span>Notify</span>
                <span>Draft</span>
                <span>Auto</span>
                <span>Full</span>
              </div>
            </div>

            <div class="platform-actions">
              <button @click="syncPlatform(platform)" :disabled="!platform.connected">
                Sync Now
              </button>
              <button @click="configurePlatform(platform)">
                Configure
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Center Panel: Live Feed -->
      <div class="panel live-feed">
        <div class="feed-header">
          <h3>Live Activity Feed</h3>
          <div class="feed-controls">
            <button 
              v-for="filter in feedFilters" 
              :key="filter"
              @click="toggleFilter(filter)"
              :class="{ active: activeFilters.includes(filter) }"
              class="filter-btn"
            >
              {{ filter }}
            </button>
          </div>
        </div>

        <div class="feed-list" ref="feedList">
          <transition-group name="feed">
            <div 
              v-for="item in filteredFeed" 
              :key="item.id"
              class="feed-item"
              :class="[item.type, { pending: item.pending }]"
              @click="selectItem(item)"
            >
              <div class="feed-time">{{ formatTime(item.timestamp) }}</div>
              <div class="feed-content">
                <div class="feed-header">
                  <span class="platform-badge">{{ item.platform }}</span>
                  <span class="sender">{{ item.sender }}</span>
                  <span v-if="item.vip" class="vip-badge">VIP</span>
                </div>
                <div class="feed-message">{{ item.preview }}</div>
                <div class="feed-actions" v-if="item.suggestedActions">
                  <span 
                    v-for="action in item.suggestedActions" 
                    :key="action"
                    class="suggested-action"
                  >
                    {{ action }}
                  </span>
                </div>
              </div>
              <div class="feed-status">
                <span v-if="item.processed" class="status-badge processed">✓</span>
                <span v-else-if="item.processing" class="status-badge processing">⟳</span>
                <span v-else class="status-badge pending">•</span>
              </div>
            </div>
          </transition-group>
        </div>
      </div>

      <!-- Right Panel: Details & Actions -->
      <div class="panel details-panel" v-if="selectedItem">
        <div class="details-header">
          <h3>Message Details</h3>
          <button @click="selectedItem = null" class="close-btn">×</button>
        </div>

        <div class="details-content">
          <div class="detail-section">
            <h4>Original Message</h4>
            <div class="message-box">{{ selectedItem.fullContent }}</div>
          </div>

          <div class="detail-section" v-if="selectedItem.aiAnalysis">
            <h4>AI Analysis</h4>
            <div class="analysis-box">
              <div class="confidence-meter">
                <span>Confidence:</span>
                <div class="meter">
                  <div 
                    class="meter-fill" 
                    :style="{ width: (selectedItem.aiAnalysis.confidence * 100) + '%' }"
                  ></div>
                </div>
                <span>{{ (selectedItem.aiAnalysis.confidence * 100).toFixed(0) }}%</span>
              </div>
              <div class="reasoning">
                <strong>Reasoning:</strong> {{ selectedItem.aiAnalysis.reasoning }}
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>Suggested Response</h4>
            <textarea 
              v-model="draftResponse" 
              class="response-editor"
              @input="onResponseEdit"
            ></textarea>
            <div class="response-actions">
              <button @click="sendResponse" class="send-btn primary">
                Send Now
                <kbd>⌘↵</kbd>
              </button>
              <button @click="scheduleResponse" class="schedule-btn">
                Schedule
              </button>
              <button @click="discardResponse" class="discard-btn">
                Discard
              </button>
            </div>
          </div>

          <div class="detail-section metadata">
            <h4>Metadata</h4>
            <div class="metadata-grid">
              <div class="meta-item">
                <span class="meta-label">Platform:</span>
                <span class="meta-value">{{ selectedItem.platform }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Thread ID:</span>
                <span class="meta-value">{{ selectedItem.threadId }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Processing Time:</span>
                <span class="meta-value">{{ selectedItem.processingTime }}ms</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: System Logs (when no item selected) -->
      <div class="panel system-logs" v-else>
        <h3>System Logs</h3>
        <div class="log-filters">
          <button 
            v-for="level in logLevels" 
            :key="level"
            @click="toggleLogLevel(level)"
            :class="{ active: activeLogLevels.includes(level) }"
            class="log-level-btn"
          >
            {{ level }}
          </button>
        </div>
        <div class="log-list">
          <div 
            v-for="log in filteredLogs" 
            :key="log.id"
            class="log-entry"
            :class="log.level"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-level">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced AI Head -->
    <div class="ai-head-container">
      <AIHead 
        :status="aiStatus" 
        :processing="processing"
        :mood="currentMood"
        @click="toggleVoiceMode"
      />
      <div class="ai-status-text">{{ aiStatusText }}</div>
    </div>

    <!-- Keyboard Shortcuts Modal -->
    <transition name="modal">
      <div v-if="showShortcuts" class="shortcuts-modal" @click="showShortcuts = false">
        <div class="shortcuts-content" @click.stop>
          <h3>Keyboard Shortcuts</h3>
          <div class="shortcuts-grid">
            <div class="shortcut">
              <kbd>⌘ P</kbd>
              <span>Process all pending</span>
            </div>
            <div class="shortcut">
              <kbd>⌘ A</kbd>
              <span>Toggle autonomy</span>
            </div>
            <div class="shortcut">
              <kbd>⌘ R</kbd>
              <span>Review queue</span>
            </div>
            <div class="shortcut">
              <kbd>⌘ ,</kbd>
              <span>Open settings</span>
            </div>
            <div class="shortcut">
              <kbd>⌘ ↵</kbd>
              <span>Send response</span>
            </div>
            <div class="shortcut">
              <kbd>?</kbd>
              <span>Show shortcuts</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/system'
import { useMessagesStore } from '../stores/messages'
import AIHead from '../components/AIHead.vue'

// Stores
const systemStore = useSystemStore()
const messagesStore = useMessagesStore()

// State
const selectedItem = ref(null)
const draftResponse = ref('')
const showShortcuts = ref(false)
const processing = ref(false)

// Computed
const systemStatus = computed(() => systemStore.status)
const stats = computed(() => systemStore.stats)
const platforms = computed(() => systemStore.platforms)
const feedItems = computed(() => messagesStore.feedItems)
const currentProvider = computed(() => systemStore.llmProvider)
const currentModel = computed(() => systemStore.llmModel)
const aiStatus = computed(() => systemStore.aiStatus)
const currentMood = computed(() => systemStore.aiMood)
const autonomyEnabled = computed(() => systemStore.globalAutonomy)

// Filters
const feedFilters = ['All', 'Unread', 'VIP', 'Pending', 'Processed']
const activeFilters = ref(['All'])
const logLevels = ['Info', 'Warning', 'Error', 'Debug']
const activeLogLevels = ref(['Info', 'Warning', 'Error'])

const filteredFeed = computed(() => {
  // Filter logic here
  return feedItems.value
})

const filteredLogs = computed(() => {
  // Filter logs
  return systemStore.logs.filter(log => activeLogLevels.value.includes(log.level))
})

const aiStatusText = computed(() => {
  if (processing.value) return "Processing..."
  if (autonomyEnabled.value) return "Autonomous Mode Active"
  return "Standing By"
})

// Methods
const processAllPending = async () => {
  processing.value = true
  await messagesStore.processAllPending()
  processing.value = false
}

const toggleAutonomy = () => {
  systemStore.toggleGlobalAutonomy()
}

const reviewQueue = () => {
  // Open queue review
}

const openSettings = () => {
  // Open settings
}

const updateAutonomy = (platform) => {
  systemStore.updatePlatformAutonomy(platform.id, platform.autonomyLevel)
}

const syncPlatform = async (platform) => {
  await systemStore.syncPlatform(platform.id)
}

const configurePlatform = (platform) => {
  // Open platform config
}

const toggleFilter = (filter) => {
  if (filter === 'All') {
    activeFilters.value = ['All']
  } else {
    activeFilters.value = activeFilters.value.includes(filter)
      ? activeFilters.value.filter(f => f !== filter)
      : [...activeFilters.value.filter(f => f !== 'All'), filter]
  }
}

const selectItem = (item) => {
  selectedItem.value = item
  draftResponse.value = item.suggestedResponse || ''
}

const sendResponse = async () => {
  if (selectedItem.value && draftResponse.value) {
    await messagesStore.sendResponse(selectedItem.value.id, draftResponse.value)
    selectedItem.value = null
  }
}

const scheduleResponse = () => {
  // Show scheduling UI
}

const discardResponse = () => {
  draftResponse.value = ''
  selectedItem.value = null
}

const toggleVoiceMode = () => {
  systemStore.toggleVoiceMode()
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return date.toLocaleDateString()
}

// Keyboard shortcuts
const handleKeyboard = (e) => {
  if (e.metaKey || e.ctrlKey) {
    switch (e.key) {
      case 'p':
        e.preventDefault()
        processAllPending()
        break
      case 'a':
        e.preventDefault()
        toggleAutonomy()
        break
      case 'r':
        e.preventDefault()
        reviewQueue()
        break
      case ',':
        e.preventDefault()
        openSettings()
        break
      case 'Enter':
        if (selectedItem.value) {
          e.preventDefault()
          sendResponse()
        }
        break
    }
  } else if (e.key === '?') {
    showShortcuts.value = true
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyboard)
  systemStore.startPolling()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyboard)
  systemStore.stopPolling()
})
</script>

<style scoped>
.control-center {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0a0a0a;
  color: #e0e0e0;
  font-family: 'SF Mono', 'Monaco', monospace;
}

/* Status Bar */
.status-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  background: #1a1a1a;
  border-bottom: 1px solid #333;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
}

.status-item.active .status-indicator {
  background: #00ff9f;
  box-shadow: 0 0 10px #00ff9f;
}

.metric {
  font-size: 1.2rem;
  font-weight: bold;
  color: #00ff9f;
}

.label {
  font-size: 0.8rem;
  color: #888;
}

.llm-status {
  margin-left: auto;
}

.provider-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.provider-badge.anthropic {
  background: #c9aa88;
  color: #1a1a1a;
}

.provider-badge.openai {
  background: #10a37f;
  color: white;
}

.model {
  font-size: 0.8rem;
  color: #888;
  margin-left: 0.5rem;
}

/* Main Grid */
.main-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr 400px;
  gap: 1px;
  background: #333;
  overflow: hidden;
}

.panel {
  background: #1a1a1a;
  overflow-y: auto;
  padding: 1.5rem;
}

/* Quick Actions */
.action-grid {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  color: #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #333;
  border-color: #444;
}

.action-btn.primary {
  background: #00ff9f20;
  border-color: #00ff9f;
  color: #00ff9f;
}

.action-btn .icon {
  font-size: 1.2rem;
}

.action-btn kbd {
  margin-left: auto;
  padding: 0.2rem 0.4rem;
  background: #333;
  border-radius: 3px;
  font-size: 0.7rem;
  color: #888;
}

/* Platform Controls */
.platform-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.platform-control {
  padding: 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 8px;
  transition: all 0.2s;
}

.platform-control.active {
  border-color: #00ff9f40;
}

.platform-control.processing {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
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

.platform-name {
  font-weight: bold;
}

.platform-status {
  margin-left: auto;
}

.connected {
  color: #00ff9f;
}

.disconnected {
  color: #666;
}

.platform-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat .value {
  font-size: 1.2rem;
  font-weight: bold;
}

.stat .label {
  font-size: 0.7rem;
  color: #888;
}

/* Autonomy Slider */
.autonomy-slider {
  margin-bottom: 1rem;
}

.autonomy-slider label {
  display: block;
  font-size: 0.8rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.autonomy-slider input[type="range"] {
  width: 100%;
  height: 4px;
  background: #333;
  outline: none;
  -webkit-appearance: none;
}

.autonomy-slider input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #00ff9f;
  border-radius: 50%;
  cursor: pointer;
}

.level-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #666;
  margin-top: 0.25rem;
}

.platform-actions {
  display: flex;
  gap: 0.5rem;
}

.platform-actions button {
  flex: 1;
  padding: 0.5rem;
  background: #333;
  border: 1px solid #444;
  color: #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.platform-actions button:hover:not(:disabled) {
  background: #444;
}

.platform-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Live Feed */
.feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.feed-controls {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.25rem 0.75rem;
  background: #2a2a2a;
  border: 1px solid #333;
  color: #888;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.filter-btn.active {
  background: #00ff9f20;
  border-color: #00ff9f;
  color: #00ff9f;
}

.feed-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.feed-item {
  display: grid;
  grid-template-columns: 80px 1fr auto;
  gap: 1rem;
  padding: 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.feed-item:hover {
  background: #333;
  border-color: #444;
}

.feed-item.pending {
  border-left: 3px solid #ff9f00;
}

.feed-time {
  font-size: 0.8rem;
  color: #666;
}

.feed-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.feed-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.platform-badge {
  padding: 0.2rem 0.5rem;
  background: #333;
  border-radius: 3px;
  font-size: 0.7rem;
  text-transform: uppercase;
}

.sender {
  font-weight: bold;
}

.vip-badge {
  padding: 0.2rem 0.5rem;
  background: #ff6b35;
  color: white;
  border-radius: 3px;
  font-size: 0.7rem;
}

.feed-message {
  color: #aaa;
  font-size: 0.9rem;
}

.feed-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.suggested-action {
  padding: 0.2rem 0.5rem;
  background: #00ff9f20;
  border: 1px solid #00ff9f40;
  color: #00ff9f;
  border-radius: 3px;
  font-size: 0.7rem;
}

.status-badge {
  font-size: 1.2rem;
}

.status-badge.processed {
  color: #00ff9f;
}

.status-badge.processing {
  color: #ff9f00;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-badge.pending {
  color: #666;
}

/* Details Panel */
.details-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 1.5rem;
  cursor: pointer;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section h4 {
  margin-bottom: 0.5rem;
  color: #00ff9f;
}

.message-box {
  padding: 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 6px;
  white-space: pre-wrap;
}

.analysis-box {
  padding: 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 6px;
}

.confidence-meter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.meter {
  flex: 1;
  height: 8px;
  background: #333;
  border-radius: 4px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b35, #ff9f00, #00ff9f);
  transition: width 0.3s;
}

.reasoning {
  font-size: 0.9rem;
  color: #aaa;
}

.response-editor {
  width: 100%;
  min-height: 150px;
  padding: 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 6px;
  color: #e0e0e0;
  font-family: inherit;
  resize: vertical;
}

.response-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.response-actions button {
  padding: 0.5rem 1rem;
  border: 1px solid #333;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.send-btn {
  background: #00ff9f;
  color: #0a0a0a;
  border-color: #00ff9f;
  font-weight: bold;
}

.schedule-btn {
  background: #2a2a2a;
  color: #e0e0e0;
}

.discard-btn {
  background: #2a2a2a;
  color: #ff6b35;
  border-color: #ff6b35;
}

.metadata-grid {
  display: grid;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  gap: 0.5rem;
}

.meta-label {
  color: #666;
}

.meta-value {
  color: #e0e0e0;
  font-family: monospace;
}

/* System Logs */
.log-filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.log-level-btn {
  padding: 0.25rem 0.75rem;
  background: #2a2a2a;
  border: 1px solid #333;
  color: #888;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.log-level-btn.active {
  background: #333;
  color: #e0e0e0;
}

.log-list {
  font-size: 0.8rem;
  font-family: monospace;
}

.log-entry {
  display: flex;
  gap: 1rem;
  padding: 0.25rem 0;
  border-bottom: 1px solid #2a2a2a;
}

.log-time {
  color: #666;
}

.log-level {
  font-weight: bold;
  text-transform: uppercase;
}

.log-entry.Info .log-level {
  color: #00ff9f;
}

.log-entry.Warning .log-level {
  color: #ff9f00;
}

.log-entry.Error .log-level {
  color: #ff6b35;
}

.log-entry.Debug .log-level {
  color: #6b46c1;
}

.log-message {
  flex: 1;
  color: #aaa;
}

/* AI Head Container */
.ai-head-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.ai-status-text {
  padding: 0.5rem 1rem;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 20px;
  font-size: 0.8rem;
  color: #00ff9f;
}

/* Shortcuts Modal */
.shortcuts-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.shortcuts-content {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

.shortcut {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.shortcut kbd {
  padding: 0.5rem 1rem;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 6px;
  font-family: 'SF Mono', monospace;
  min-width: 80px;
  text-align: center;
}

/* Transitions */
.feed-enter-active,
.feed-leave-active {
  transition: all 0.3s;
}

.feed-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.feed-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-from {
  opacity: 0;
}
</style>