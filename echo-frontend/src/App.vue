<template>
  <div id="app">
    <nav class="navbar">
      <div class="brand">
        <h1>ECHO</h1>
        <p class="tagline">Your voice, amplified with intelligence</p>
      </div>
      <div class="nav-links">
        <template v-if="user">
          <router-link to="/">Dashboard</router-link>
          <router-link to="/persona">AI Persona</router-link>
          <router-link to="/documentation">Doc Automator</router-link>
          <router-link to="/review">Code Review</router-link>
          <router-link to="/financial">Financial Planner</router-link>
          <router-link to="/opportunities">Opportunities</router-link>
          <div class="user-menu">
            <img :src="user.photoURL || '/default-avatar.png'" :alt="user.displayName" class="user-avatar">
            <span class="user-name">{{ user.displayName }}</span>
            <button @click="logout" class="logout-btn">Sign Out</button>
          </div>
        </template>
        <template v-else>
          <button @click="login" class="login-btn">Sign in with Google</button>
        </template>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view v-if="user || !requireAuth" />
      <div v-else class="auth-prompt">
        <div class="auth-card">
          <h2>Welcome to ECHO Personal AI</h2>
          <p>Your autonomous AI assistant that learns and evolves with you.</p>
          <div class="features">
            <div class="feature">
              <span class="icon">🤖</span>
              <h3>Autonomous Agents</h3>
              <p>AI agents that work on your behalf</p>
            </div>
            <div class="feature">
              <span class="icon">📧</span>
              <h3>Message Automation</h3>
              <p>Handle emails, Slack, and more</p>
            </div>
            <div class="feature">
              <span class="icon">🧠</span>
              <h3>Continuous Learning</h3>
              <p>Adapts to your communication style</p>
            </div>
          </div>
          <button @click="login" class="login-btn-large">
            <svg class="google-icon" viewBox="0 0 24 24" width="24" height="24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </button>
        </div>
      </div>
    </main>
    
    <AudioInterface v-if="audioEnabled && user" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AudioInterface from './components/AudioInterface.vue'
import { signInWithGoogle, signOut, onAuthStateChange } from './config/firebase'

const router = useRouter()
const audioEnabled = ref(true)
const user = ref(null)
const requireAuth = ref(true)

onMounted(() => {
  // Listen for auth state changes
  onAuthStateChange((authUser) => {
    user.value = authUser
    if (authUser) {
      // User is signed in
      console.log('User signed in:', authUser.email)
    } else {
      // User is signed out
      console.log('User signed out')
      // Redirect to home if on protected route
      if (requireAuth.value && router.currentRoute.value.path !== '/') {
        router.push('/')
      }
    }
  })
})

const login = async () => {
  try {
    await signInWithGoogle()
    // User will be set by auth state listener
  } catch (error) {
    console.error('Login error:', error)
    alert('Failed to sign in. Please try again.')
  }
}

const logout = async () => {
  try {
    await signOut()
    router.push('/')
  } catch (error) {
    console.error('Logout error:', error)
  }
}
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
  min-height: 100vh;
  background-color: var(--dark);
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
  align-items: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.nav-links a:hover {
  opacity: 0.8;
}

.nav-links a.router-link-active {
  color: var(--primary);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: 2rem;
  padding-left: 2rem;
  border-left: 1px solid #333;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.user-name {
  color: #ccc;
  font-size: 0.9rem;
}

.logout-btn, .login-btn {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover, .login-btn:hover {
  background: var(--primary);
  color: var(--dark);
}

.main-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.auth-prompt {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.auth-card {
  background: #1a1a1a;
  padding: 3rem;
  border-radius: 12px;
  text-align: center;
  max-width: 600px;
  border: 1px solid #333;
}

.auth-card h2 {
  color: var(--primary);
  margin-bottom: 1rem;
  font-size: 2rem;
}

.auth-card p {
  color: #ccc;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin: 2rem 0;
}

.feature {
  text-align: center;
}

.feature .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
}

.feature h3 {
  color: white;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.feature p {
  color: #888;
  font-size: 0.875rem;
}

.login-btn-large {
  background: white;
  color: #333;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s;
  margin-top: 2rem;
}

.login-btn-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.google-icon {
  width: 24px;
  height: 24px;
}
</style>