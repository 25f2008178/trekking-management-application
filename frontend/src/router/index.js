import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/LoginView.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import StaffDashboard from '@/views/staff/StaffDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/staff',
      name: 'staff',
      component: StaffDashboard,
      meta: { requiresAuth: true, requiresStaff: true },
    },
    {
      path: '/',
      redirect: (to) => {
        const authStore = useAuthStore()
        if (authStore.isAdmin) return '/admin'
        if (authStore.isStaff) return '/staff'
        return '/login'
      },
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Initialize auth profile state if not already initialized
  if (!authStore.initialized) {
    await authStore.fetchProfile()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'login' })
  }

  if (to.meta.requiresStaff && !authStore.isStaff) {
    return next({ name: 'login' })
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      return next({ name: 'admin' })
    }
    if (authStore.isStaff) {
      return next({ name: 'staff' })
    }
  }

  next()
})

export default router
