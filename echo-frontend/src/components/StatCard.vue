<template>
  <div class="stat-card">
    <h3>{{ title }}</h3>
    <div class="value">{{ value }}</div>
    <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  font-size: 32px;
  font-weight: bold;
  color: #4CAF50;
  margin: 10px 0;
}

.subtitle {
  font-size: 12px;
  color: #666;
}
</style>