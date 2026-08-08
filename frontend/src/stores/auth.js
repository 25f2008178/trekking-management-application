import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    initialized: false,
    error: null,
  }),

  getters: {
    roles: (state) => state.user?.roles || [],
    isAdmin: (state) => state.user?.roles?.includes('admin') || false,
    isStaff: (state) => state.user?.roles?.includes('staff') || false,
    userName: (state) => state.user?.name || state.user?.email || 'User',
  },

  actions: {
    async fetchProfile() {
      this.loading = true
      try {
        const data = await api.get('/api/user/profile')
        this.user = data
        this.isAuthenticated = true
        this.error = null
        return data
      } catch (err) {
        this.user = null
        this.isAuthenticated = false
        // If unauthenticated (401), clear session silently
      } finally {
        this.loading = false
        this.initialized = true
      }
    },

    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        // Flask-Security JSON login endpoint
        const response = await api.post('/login', { email, password })
        
        // Fetch full user profile after login
        await this.fetchProfile()
        return response
      } catch (err) {
        this.user = null
        this.isAuthenticated = false
        this.error = err.message || 'Failed to sign in. Please check your credentials.'
        throw err
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      try {
        await api.post('/logout')
      } catch (err) {
        console.warn('Logout endpoint call failed, clearing state locally:', err)
      } finally {
        this.user = null
        this.isAuthenticated = false
        this.error = null
        this.loading = false
      }
    },
  },
})
