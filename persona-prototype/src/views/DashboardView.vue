<template>
  <div class="dashboard">
    <h2>Mission Control</h2>
    
    <div class="stats-grid">
      <StatCard 
        title="Time Saved Today"
        :value="stats.timeSaved"
        unit="hours"
        :trend="stats.timeTrend"
        color="success"
      />
      <StatCard 
        title="Days to Retirement"
        :value="stats.daysToRetirement"
        unit="days"
        :trend="-1"
        color="primary"
      />
      <StatCard 
        title="Monthly Passive Income"
        :value="stats.passiveIncome"
        unit="$"
        :trend="stats.incomeTrend"
        color="warning"
      />
      <StatCard 
        title="Code Reviews Automated"
        :value="stats.reviewsAutomated"
        unit="PRs"
        :trend="stats.reviewTrend"
        color="accent"
      />
    </div>

    <div class="activity-grid">
      <div class="activity-panel">
        <h3>🤖 Recent Agent Activity</h3>
        <ActivityLog :activities="recentActivities" />
      </div>
      
      <div class="activity-panel">
        <h3>🎯 Today's Priorities</h3>
        <PriorityList :priorities="todaysPriorities" />
      </div>
    </div>

    <div class="quick-actions">
      <h3>Quick Actions</h3>
      <div class="action-buttons">
        <button @click="generateDocs" class="action-btn">
          📝 Generate Documentation
        </button>
        <button @click="scanOpportunities" class="action-btn">
          🔍 Scan DoD Contracts
        </button>
        <button @click="reviewCode" class="action-btn">
          👀 Review Pending PRs
        </button>
        <button @click="updateFinancials" class="action-btn">
          💰 Update Financial Plan
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import StatCard from '../components/StatCard.vue'
import ActivityLog from '../components/ActivityLog.vue'
import PriorityList from '../components/PriorityList.vue'

// Simulated data - will connect to real services
const stats = ref({
  timeSaved: 3.5,
  timeTrend: 12,
  daysToRetirement: 5844, // 16 years
  passiveIncome: 450,
  incomeTrend: 8,
  reviewsAutomated: 12,
  reviewTrend: 3
})

const recentActivities = ref([
  { time: '10:32', agent: 'Doc', action: 'Generated API docs for TaskStore' },
  { time: '09:45', agent: 'Rex', action: 'Pre-reviewed PR #234' },
  { time: '08:15', agent: 'Finn', action: 'Found 3 new contract opportunities' },
  { time: '07:30', agent: 'Opti', action: 'Identified 2 automation opportunities' }
])

const todaysPriorities = ref([
  { priority: 'high', task: 'Review vuebudgetfire security updates' },
  { priority: 'medium', task: 'Update cannabis-finder documentation' },
  { priority: 'medium', task: 'Analyze Q2 financial projections' },
  { priority: 'low', task: 'Optimize build process for MotorcycleApp' }
])

const generateDocs = () => {
  console.log('Generating documentation...')
}

const scanOpportunities = () => {
  console.log('Scanning for opportunities...')
}

const reviewCode = () => {
  console.log('Reviewing code...')
}

const updateFinancials = () => {
  console.log('Updating financial plan...')
}
</script>

<style scoped>
.dashboard {
  padding: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.activity-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin: 2rem 0;
}

.activity-panel {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.quick-actions {
  margin-top: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.action-btn:hover {
  background: #2980b9;
}
</style>