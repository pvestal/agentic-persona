<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <h2>Dashboard</h2>
      <el-button @click="refreshData" :loading="isRefreshing">
        <el-icon><Refresh /></el-icon>
        Refresh
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon tasks">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalTasks }}</div>
              <div class="stat-label">Total Tasks</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon directors">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeDirectors }}</div>
              <div class="stat-label">Active Directors</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.successRate }}%</div>
              <div class="stat-label">Success Rate</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon quality">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avgQuality }}</div>
              <div class="stat-label">Avg Quality Score</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Task Status Distribution</span>
            </div>
          </template>
          <TaskStatusChart :data="taskStatusData" />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Director Performance</span>
            </div>
          </template>
          <DirectorPerformanceChart :data="directorPerformanceData" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Activity -->
    <el-card class="recent-activity">
      <template #header>
        <div class="card-header">
          <span>Recent Tasks</span>
          <el-button link @click="goToTasks">View All</el-button>
        </div>
      </template>
      
      <el-table
        :data="recentTasks"
        v-loading="isLoadingTasks"
        style="width: 100%"
      >
        <el-table-column prop="title" label="Title" min-width="200">
          <template #default="{ row }">
            <el-link @click="viewTask(row.id)" type="primary">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="assigned_director.name" label="Director" width="150" />
        
        <el-table-column prop="created_at" label="Created" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Refresh,
  Document,
  UserFilled,
  CircleCheck,
  TrendCharts
} from '@element-plus/icons-vue'
import { tasksAPI } from '@/api/tasks'
import { directorsAPI } from '@/api/directors'
import TaskStatusChart from '@/components/charts/TaskStatusChart.vue'
import DirectorPerformanceChart from '@/components/charts/DirectorPerformanceChart.vue'
import { formatDate, getStatusType, getPriorityType } from '@/utils/formatters'

const router = useRouter()

// State
const isRefreshing = ref(false)
const isLoadingTasks = ref(false)
const stats = ref({
  totalTasks: 0,
  activeDirectors: 0,
  successRate: 0,
  avgQuality: 0
})
const recentTasks = ref([])
const taskStatusData = ref({})
const directorPerformanceData = ref([])

// Methods
const fetchDashboardData = async () => {
  try {
    // Fetch task statistics
    const statsResponse = await tasksAPI.getStats({ days: 30 })
    const taskStats = statsResponse.data
    
    // Fetch directors
    const directorsResponse = await directorsAPI.list({ is_available: true })
    const directors = directorsResponse.data.data
    
    // Update stats
    stats.value = {
      totalTasks: taskStats.total_tasks,
      activeDirectors: directors.length,
      successRate: Math.round(taskStats.success_rate * 100),
      avgQuality: taskStats.average_quality_score.toFixed(2)
    }
    
    // Update chart data
    taskStatusData.value = taskStats.tasks_by_status
    
    // Process director performance data
    directorPerformanceData.value = directors.map(d => ({
      name: d.name,
      tasksCompleted: d.tasks_completed,
      successRate: d.success_rate,
      overallScore: d.overall_score
    }))
    
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

const fetchRecentTasks = async () => {
  isLoadingTasks.value = true
  try {
    const response = await tasksAPI.list({
      page: 1,
      page_size: 10
    })
    recentTasks.value = response.data.data
  } catch (error) {
    console.error('Failed to fetch recent tasks:', error)
  } finally {
    isLoadingTasks.value = false
  }
}

const refreshData = async () => {
  isRefreshing.value = true
  await Promise.all([
    fetchDashboardData(),
    fetchRecentTasks()
  ])
  isRefreshing.value = false
}

const goToTasks = () => {
  router.push('/tasks')
}

const viewTask = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>

<style lang="scss" scoped>
.dashboard-view {
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }
  
  .statistics-row {
    margin-bottom: 20px;
    
    .stat-card {
      height: 100%;
      
      .stat-content {
        display: flex;
        align-items: center;
        gap: 20px;
        
        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          
          &.tasks {
            background-color: var(--el-color-primary-light-9);
            color: var(--el-color-primary);
          }
          
          &.directors {
            background-color: var(--el-color-success-light-9);
            color: var(--el-color-success);
          }
          
          &.success {
            background-color: var(--el-color-info-light-9);
            color: var(--el-color-info);
          }
          
          &.quality {
            background-color: var(--el-color-warning-light-9);
            color: var(--el-color-warning);
          }
        }
        
        .stat-info {
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            line-height: 1;
            margin-bottom: 5px;
          }
          
          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-regular);
          }
        }
      }
    }
  }
  
  .charts-row {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
  
  .recent-activity {
    :deep(.el-table) {
      .el-link {
        font-weight: 500;
      }
    }
  }
}
</style>