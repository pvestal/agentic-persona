<template>
  <div class="priority-list">
    <h3>Priority Tasks</h3>
    <div class="task-list">
      <div v-for="task in tasks" :key="task.id" :class="['task', task.priority]">
        <input type="checkbox" :id="`task-${task.id}`" v-model="task.completed">
        <label :for="`task-${task.id}`">{{ task.title }}</label>
        <span class="priority-badge">{{ task.priority }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PriorityList',
  data() {
    return {
      tasks: [
        { id: 1, title: 'Review investment portfolio', priority: 'high', completed: false },
        { id: 2, title: 'Update API documentation', priority: 'medium', completed: false },
        { id: 3, title: 'Refactor authentication module', priority: 'high', completed: false },
        { id: 4, title: 'Team sync meeting', priority: 'low', completed: true }
      ]
    }
  }
}
</script>

<style scoped>
.priority-list {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 4px;
  background: #f5f5f5;
}

.task.high {
  border-left: 4px solid #f44336;
}

.task.medium {
  border-left: 4px solid #ff9800;
}

.task.low {
  border-left: 4px solid #4caf50;
}

input[type="checkbox"] {
  cursor: pointer;
}

label {
  flex: 1;
  cursor: pointer;
}

.priority-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  font-weight: bold;
}

.high .priority-badge {
  background: #ffebee;
  color: #f44336;
}

.medium .priority-badge {
  background: #fff3e0;
  color: #ff9800;
}

.low .priority-badge {
  background: #e8f5e9;
  color: #4caf50;
}
</style>