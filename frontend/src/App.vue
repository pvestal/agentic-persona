<template>
  <el-config-provider :locale="locale">
    <div id="app">
      <template v-if="!isAuthRoute">
        <AppHeader />
        <div class="main-container">
          <AppSidebar />
          <div class="content-wrapper">
            <router-view v-slot="{ Component }">
              <transition name="fade-transform" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </div>
      </template>
      <template v-else>
        <router-view />
      </template>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElConfigProvider } from 'element-plus'
import enUS from 'element-plus/es/locale/lang/en'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const locale = enUS

const isAuthRoute = computed(() => {
  return route.path.startsWith('/auth')
})

onMounted(() => {
  // Initialize auth state
  authStore.initializeAuth()
})
</script>

<style lang="scss">
#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-container {
  display: flex;
  height: calc(100vh - 60px);
  
  .content-wrapper {
    flex: 1;
    overflow-y: auto;
    background-color: var(--el-bg-page);
    padding: 20px;
  }
}

// Transition styles
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>