<template>
  <div class="audio-interface">
    <h3>Voice Assistant</h3>
    <button @click="toggleRecording" :class="{ recording: isRecording }">
      {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
    </button>
    <div v-if="transcript" class="transcript">
      <p>{{ transcript }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AudioInterface',
  data() {
    return {
      isRecording: false,
      transcript: ''
    }
  },
  methods: {
    toggleRecording() {
      this.isRecording = !this.isRecording
      if (this.isRecording) {
        this.transcript = 'Listening...'
      } else {
        this.transcript = 'Recording stopped'
      }
    }
  }
}
</script>

<style scoped>
.audio-interface {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  background: #4CAF50;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #45a049;
}

button.recording {
  background: #f44336;
}

.transcript {
  margin-top: 20px;
  padding: 10px;
  background: white;
  border-radius: 4px;
}
</style>