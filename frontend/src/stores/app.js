import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // State
  const sidebarCollapsed = ref(false)
  const theme = ref('light')
  const loading = ref(false)
  const settings = ref({
    autoRefresh: true,
    refreshInterval: 30000,
    notifications: true,
    compactMode: false
  })

  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed) {
    sidebarCollapsed.value = collapsed
  }

  function setTheme(newTheme) {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  function setLoading(isLoading) {
    loading.value = isLoading
  }

  function updateSettings(newSettings) {
    settings.value = { ...settings.value, ...newSettings }
    localStorage.setItem('app-settings', JSON.stringify(settings.value))
  }

  function initializeApp() {
    // Load theme
    const savedTheme = localStorage.getItem('theme') || 'light'
    setTheme(savedTheme)

    // Load settings
    const savedSettings = localStorage.getItem('app-settings')
    if (savedSettings) {
      try {
        settings.value = JSON.parse(savedSettings)
      } catch (e) {
        console.error('Failed to parse saved settings:', e)
      }
    }
  }

  return {
    // State
    sidebarCollapsed,
    theme,
    loading,
    settings,

    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    setTheme,
    setLoading,
    updateSettings,
    initializeApp
  }
})