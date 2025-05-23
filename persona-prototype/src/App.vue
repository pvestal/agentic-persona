<template>
  <div id="app">
    <nav class="navbar">
      <h1>Patrick's Digital Deputy</h1>
      <div class="nav-links">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/documentation">Doc Automator</router-link>
        <router-link to="/review">Code Review</router-link>
        <router-link to="/financial">Financial Planner</router-link>
        <router-link to="/opportunities">Opportunities</router-link>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <AudioInterface v-if="audioEnabled" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AudioInterface from './components/AudioInterface.vue'

const audioEnabled = ref(true)
</script>

<style>
:root {
  --primary: #2c3e50;
  --accent: #3498db;
  --success: #27ae60;
  --warning: #f39c12;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--primary);
}

.navbar {
  background: var(--primary);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.nav-links a:hover {
  opacity: 0.8;
}

.main-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>