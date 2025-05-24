<template>
  <div id="app">
    <nav class="navbar">
      <div class="brand">
        <h1>ECHO</h1>
        <p class="tagline">Your voice, amplified with intelligence</p>
      </div>
      <div class="nav-links">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/persona">AI Persona</router-link>
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
  --primary: #00FFE5;
  --secondary: #6B46C1;
  --accent: #FF6B35;
  --dark: #0a0a0a;
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
  background: var(--dark);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary);
}

.brand h1 {
  color: var(--primary);
  margin: 0;
  font-size: 2rem;
  letter-spacing: 0.1em;
}

.tagline {
  color: #888;
  font-size: 0.875rem;
  margin: 0;
  font-style: italic;
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