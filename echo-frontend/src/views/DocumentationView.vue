<template>
  <div class="documentation-view">
    <div class="container">
      <div class="header">
        <h1>📝 Documentation Automator</h1>
        <p>Transform your codebase into comprehensive documentation instantly</p>
      </div>

      <div class="controls">
        <div class="card">
          <h3>Project Selection</h3>
          <div class="input-group">
            <label>Select Project to Document</label>
            <select v-model="selectedProject" @change="analyzeProject">
              <option value="">Choose a project...</option>
              <option value="cannabis-finder">Cannabis Finder</option>
              <option value="motorcycle-workshop">Motorcycle Workshop Manager</option>
              <option value="vuebudgetfire">Vue Budget Fire</option>
              <option value="ufc-betting">UFC Betting System</option>
              <option value="music-proxy">Music Service Proxy</option>
            </select>
          </div>

          <div class="input-group">
            <label>Documentation Type</label>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" v-model="docTypes.api"> API Documentation
              </label>
              <label>
                <input type="checkbox" v-model="docTypes.user"> User Guide
              </label>
              <label>
                <input type="checkbox" v-model="docTypes.developer"> Developer Guide
              </label>
              <label>
                <input type="checkbox" v-model="docTypes.deployment"> Deployment Guide
              </label>
            </div>
          </div>

          <div class="action-buttons">
            <button @click="scanProject" class="btn btn-primary" :disabled="!selectedProject">
              <span>🔍</span> Scan Project
            </button>
            <button @click="generateDocs" class="btn btn-secondary" :disabled="!projectScanned">
              <span>⚡</span> Generate Documentation
            </button>
          </div>
        </div>
      </div>

      <div v-if="scanning" class="scanning-indicator">
        <div class="spinner"></div>
        <p>Scanning project structure...</p>
      </div>

      <div v-if="projectData" class="project-analysis">
        <div class="grid grid-3">
          <div class="card stat-card">
            <h4>Files Found</h4>
            <p class="stat-number">{{ projectData.fileCount }}</p>
          </div>
          <div class="card stat-card">
            <h4>Components</h4>
            <p class="stat-number">{{ projectData.componentCount }}</p>
          </div>
          <div class="card stat-card">
            <h4>API Endpoints</h4>
            <p class="stat-number">{{ projectData.endpointCount }}</p>
          </div>
        </div>

        <div class="card" style="margin-top: 2rem;">
          <h3>Project Structure</h3>
          <div class="file-tree">
            <div v-for="item in projectData.structure" :key="item.path" class="tree-item">
              <span :style="{ paddingLeft: item.level * 20 + 'px' }">
                {{ item.type === 'folder' ? '📁' : '📄' }} {{ item.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="generatedDocs" class="generated-docs">
        <div class="card">
          <h3>Generated Documentation</h3>
          <div class="tabs">
            <button 
              v-for="doc in generatedDocs" 
              :key="doc.type"
              @click="activeDoc = doc.type"
              :class="['tab', { active: activeDoc === doc.type }]"
            >
              {{ doc.title }}
            </button>
          </div>
          
          <div class="doc-content">
            <pre>{{ getActiveDocContent() }}</pre>
          </div>

          <div class="export-options">
            <button @click="exportMarkdown" class="btn btn-outline">
              <span>📄</span> Export as Markdown
            </button>
            <button @click="exportHTML" class="btn btn-outline">
              <span>🌐</span> Export as HTML
            </button>
            <button @click="copyToClipboard" class="btn btn-outline">
              <span>📋</span> Copy to Clipboard
            </button>
          </div>
        </div>
      </div>

      <div class="quick-stats">
        <div class="card">
          <h3>⏱️ Time Saved</h3>
          <div class="time-saved">
            <p class="big-number">{{ timeSaved }}</p>
            <p class="subtitle">hours saved this month</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const selectedProject = ref('')
const scanning = ref(false)
const projectScanned = ref(false)
const projectData = ref(null)
const generatedDocs = ref(null)
const activeDoc = ref('api')
const timeSaved = ref(47)

const docTypes = ref({
  api: true,
  user: true,
  developer: true,
  deployment: false
})

const analyzeProject = () => {
  if (selectedProject.value) {
    projectScanned.value = false
    projectData.value = null
    generatedDocs.value = null
  }
}

const scanProject = async () => {
  scanning.value = true
  projectScanned.value = false
  
  // Simulate scanning
  setTimeout(() => {
    projectData.value = {
      fileCount: 142,
      componentCount: 28,
      endpointCount: 15,
      structure: [
        { path: 'src', name: 'src', type: 'folder', level: 0 },
        { path: 'src/components', name: 'components', type: 'folder', level: 1 },
        { path: 'src/components/Dashboard.vue', name: 'Dashboard.vue', type: 'file', level: 2 },
        { path: 'src/views', name: 'views', type: 'folder', level: 1 },
        { path: 'src/api', name: 'api', type: 'folder', level: 1 },
        { path: 'src/utils', name: 'utils', type: 'folder', level: 1 },
      ]
    }
    scanning.value = false
    projectScanned.value = true
  }, 2000)
}

const generateDocs = async () => {
  // Simulate doc generation
  setTimeout(() => {
    generatedDocs.value = [
      {
        type: 'api',
        title: 'API Documentation',
        content: `# API Documentation

## Authentication
All API endpoints require authentication using Bearer tokens.

### POST /api/auth/login
Authenticates user and returns access token.

**Request Body:**
\`\`\`json
{
  "email": "string",
  "password": "string"
}
\`\`\`

**Response:**
\`\`\`json
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  }
}
\`\`\`

## User Endpoints

### GET /api/users/:id
Retrieves user information by ID.

### PUT /api/users/:id
Updates user profile information.

## Data Endpoints

### GET /api/data
Retrieves paginated data list.

Query Parameters:
- page: number (default: 1)
- limit: number (default: 20)
- sort: string (default: "created_at")
`
      },
      {
        type: 'user',
        title: 'User Guide',
        content: `# User Guide

## Getting Started
Welcome to ${selectedProject.value}! This guide will help you get up and running quickly.

## Features
- Real-time data synchronization
- Intuitive dashboard interface
- Advanced filtering and search
- Export functionality

## Basic Usage
1. Log in with your credentials
2. Navigate to the dashboard
3. Use filters to find specific data
4. Click on items for detailed view
`
      },
      {
        type: 'developer',
        title: 'Developer Guide',
        content: `# Developer Guide

## Setup
\`\`\`bash
git clone https://github.com/yourusername/${selectedProject.value}.git
cd ${selectedProject.value}
npm install
npm run dev
\`\`\`

## Architecture
- Vue 3 with Composition API
- Vite for fast development
- Pinia for state management
- Firebase for backend

## Contributing
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request
`
      }
    ]
    
    timeSaved.value += 3
  }, 1500)
}

const getActiveDocContent = () => {
  const doc = generatedDocs.value?.find(d => d.type === activeDoc.value)
  return doc?.content || ''
}

const exportMarkdown = () => {
  const content = getActiveDocContent()
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedProject.value}-${activeDoc.value}.md`
  a.click()
}

const exportHTML = () => {
  alert('HTML export coming soon!')
}

const copyToClipboard = () => {
  navigator.clipboard.writeText(getActiveDocContent())
  alert('Copied to clipboard!')
}
</script>

<style scoped>
.documentation-view {
  padding: 2rem 0;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.header p {
  font-size: 1.25rem;
  color: var(--gray);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.scanning-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stat-card {
  text-align: center;
}

.stat-card h4 {
  color: var(--gray);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
}

.file-tree {
  font-family: monospace;
  background: var(--light);
  padding: 1rem;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
}

.tree-item {
  padding: 0.25rem 0;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--border);
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: var(--gray);
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.doc-content {
  background: var(--light);
  padding: 1.5rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}

.doc-content pre {
  white-space: pre-wrap;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}

.export-options {
  display: flex;
  gap: 1rem;
}

.quick-stats {
  margin-top: 3rem;
}

.time-saved {
  text-align: center;
  padding: 2rem;
}

.big-number {
  font-size: 4rem;
  font-weight: 700;
  color: var(--secondary);
}

.subtitle {
  color: var(--gray);
  font-size: 1.1rem;
}
</style>