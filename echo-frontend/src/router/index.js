import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import DocumentationView from '../views/DocumentationView.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView
  },
  {
    path: '/documentation',
    name: 'documentation',
    component: DocumentationView
  },
  {
    path: '/persona',
    name: 'persona',
    component: () => import('../views/PersonaView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router