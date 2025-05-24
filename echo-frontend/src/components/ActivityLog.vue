<template>
  <div class="activity-log">
    <h3>Recent Activity</h3>
    <ul>
      <li v-for="activity in activities" :key="activity.id">
        <span class="time">{{ activity.time }}</span>
        <span class="description">{{ activity.description }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ActivityLog',
  data() {
    return {
      activities: [
        { id: 1, time: '10:30 AM', description: 'Completed financial review' },
        { id: 2, time: '9:15 AM', description: 'Updated project documentation' },
        { id: 3, time: '8:45 AM', description: 'Reviewed code changes' },
        { id: 4, time: 'Yesterday', description: 'Deployed to production' }
      ]
    }
  }
}
</script>

<style scoped>
.activity-log {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h3 {
  margin: 0 0 15px 0;
  color: #333;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 15px;
}

li:last-child {
  border-bottom: none;
}

.time {
  color: #666;
  font-size: 12px;
  min-width: 70px;
}

.description {
  color: #333;
  flex: 1;
}
</style>