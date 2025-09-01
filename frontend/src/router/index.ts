import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('../features/documents/components/DocumentRepository.vue')
        },
        {
          path: 'pm-templates',
          name: 'pm-templates',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'risk-inspections',
          name: 'risk-inspections',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'properties',
          name: 'properties',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'tenants',
          name: 'tenants',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'maintenance',
          name: 'maintenance',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'financial',
          name: 'financial',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('../views/ComingSoon.vue')
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ComingSoon.vue')
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    }
  ]
})

export default router