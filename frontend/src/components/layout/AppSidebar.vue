<template>
  <el-aside :width="sidebarWidth" class="app-sidebar">
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapsed"
      router
      class="sidebar-menu"
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <span>Dashboard</span>
      </el-menu-item>
      
      <el-sub-menu index="directors">
        <template #title>
          <el-icon><UserFilled /></el-icon>
          <span>Directors</span>
        </template>
        <el-menu-item index="/directors">
          <span>All Directors</span>
        </el-menu-item>
        <el-menu-item index="/directors/performance">
          <span>Performance</span>
        </el-menu-item>
        <el-menu-item index="/directors/create" v-if="authStore.isSuperuser">
          <span>Add Director</span>
        </el-menu-item>
      </el-sub-menu>
      
      <el-sub-menu index="tasks">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>Tasks</span>
        </template>
        <el-menu-item index="/tasks">
          <span>All Tasks</span>
        </el-menu-item>
        <el-menu-item index="/tasks/create">
          <span>Create Task</span>
        </el-menu-item>
        <el-menu-item index="/tasks/sessions">
          <span>Sessions</span>
        </el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="/monitoring">
        <el-icon><Monitor /></el-icon>
        <span>Monitoring</span>
      </el-menu-item>
      
      <el-menu-item index="/settings" v-if="authStore.isSuperuser">
        <el-icon><Setting /></el-icon>
        <span>Settings</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Odometer,
  UserFilled,
  Document,
  Monitor,
  Setting
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const authStore = useAuthStore()
const appStore = useAppStore()

const isCollapsed = computed(() => appStore.sidebarCollapsed)
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '240px')

const activeMenu = computed(() => {
  const path = route.path
  
  // Handle nested routes
  if (path.startsWith('/directors')) {
    return path
  } else if (path.startsWith('/tasks')) {
    return path
  }
  
  return path
})
</script>

<style lang="scss" scoped>
.app-sidebar {
  transition: width 0.3s;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  
  .sidebar-menu {
    height: 100%;
    border-right: none;
    
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      height: 50px;
      line-height: 50px;
      
      &:hover {
        background-color: var(--el-menu-hover-bg-color);
      }
    }
    
    :deep(.el-menu-item.is-active) {
      background-color: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: var(--el-color-primary);
      }
    }
  }
}
</style>