<template>
  <el-header class="app-header">
    <div class="header-left">
      <el-button
        circle
        @click="toggleSidebar"
        :icon="Fold"
        class="sidebar-toggle"
      />
      <h1 class="app-title">Board of Directors AI</h1>
    </div>
    
    <div class="header-right">
      <!-- Notifications -->
      <el-badge :value="notifications" class="notification-badge">
        <el-button circle :icon="Bell" @click="showNotifications" />
      </el-badge>
      
      <!-- Health Status -->
      <el-tooltip :content="healthStatus.message">
        <el-tag
          :type="healthStatus.type"
          class="health-status"
        >
          <el-icon><CircleCheck /></el-icon>
          {{ healthStatus.text }}
        </el-tag>
      </el-tooltip>
      
      <!-- User Menu -->
      <el-dropdown @command="handleCommand" class="user-menu">
        <div class="user-info">
          <el-avatar :size="32">
            {{ userInitials }}
          </el-avatar>
          <span class="username">{{ currentUser?.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              Profile
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              Settings
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              Logout
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Fold,
  Bell,
  CircleCheck,
  ArrowDown,
  User,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { healthAPI } from '@/api/health'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const notifications = ref(0)
const healthStatus = ref({
  type: 'success',
  text: 'Healthy',
  message: 'All systems operational'
})

const currentUser = computed(() => authStore.currentUser)
const userInitials = computed(() => {
  const user = currentUser.value
  if (!user) return '?'
  
  const names = (user.full_name || user.username).split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const showNotifications = () => {
  // TODO: Implement notifications panel
  ElMessageBox.alert('Notifications coming soon!', 'Notifications')
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      ElMessageBox.confirm(
        'Are you sure you want to logout?',
        'Confirm Logout',
        {
          confirmButtonText: 'Logout',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }
      ).then(() => {
        authStore.logout()
      }).catch(() => {
        // User cancelled
      })
      break
  }
}

const checkHealth = async () => {
  try {
    const response = await healthAPI.getHealth()
    const health = response.data
    
    if (health.status === 'healthy') {
      healthStatus.value = {
        type: 'success',
        text: 'Healthy',
        message: 'All systems operational'
      }
    } else if (health.status === 'degraded') {
      healthStatus.value = {
        type: 'warning',
        text: 'Degraded',
        message: 'Some services are experiencing issues'
      }
    } else {
      healthStatus.value = {
        type: 'danger',
        text: 'Unhealthy',
        message: 'System is experiencing problems'
      }
    }
  } catch (error) {
    healthStatus.value = {
      type: 'danger',
      text: 'Error',
      message: 'Failed to check system health'
    }
  }
}

let healthCheckInterval

onMounted(() => {
  checkHealth()
  // Check health every 30 seconds
  healthCheckInterval = setInterval(checkHealth, 30000)
})

onUnmounted(() => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval)
  }
})
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .sidebar-toggle {
      border: none;
    }
    
    .app-title {
      font-size: 20px;
      font-weight: 600;
      margin: 0;
      color: var(--el-text-color-primary);
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .notification-badge {
      :deep(.el-badge__content) {
        top: 5px;
        right: 5px;
      }
    }
    
    .health-status {
      display: flex;
      align-items: center;
      gap: 5px;
    }
    
    .user-menu {
      .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        padding: 5px;
        border-radius: 4px;
        transition: background-color 0.3s;
        
        &:hover {
          background-color: var(--el-fill-color-light);
        }
        
        .username {
          font-weight: 500;
          color: var(--el-text-color-primary);
        }
      }
    }
  }
}
</style>