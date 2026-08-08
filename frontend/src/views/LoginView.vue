<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLogo from '@/components/common/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!email.value || !password.value) {
    errorMessage.value = 'Please enter both email address and password.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  try {
    await authStore.login(email.value, password.value)
    if (authStore.isAdmin) {
      router.push('/admin')
    } else if (authStore.isStaff) {
      router.push('/staff')
    } else {
      router.push('/')
    }
  } catch (err) {
    errorMessage.value = authStore.error || 'Invalid credentials or inactive account.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="login-wrapper min-vh-100 bg-light d-flex align-items-center justify-content-center p-3">
    <div class="login-card card border-0 shadow-sm rounded-3 overflow-hidden">
      <!-- Header styled inline with dashboard navbar -->
      <div class="bg-dark-slate text-center p-4">
        <div class="d-flex justify-content-center mb-2">
          <AppLogo size="lg" :show-text="false" />
        </div>
        <h4 class="fw-bold text-white mb-1">Trekking Management App</h4>
        <p class="text-white-50 small mb-0">System Login</p>
      </div>

      <div class="card-body p-4">
        <div v-if="errorMessage" class="alert alert-danger py-2 px-3 small rounded-2 mb-3" role="alert">
          <i class="bi bi-exclamation-circle me-1"></i>
          <span>{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="email" class="form-label small fw-medium text-secondary">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              class="form-control"
              placeholder="name@example.com"
              required
              autocomplete="username"
            />
          </div>

          <div class="mb-4">
            <label for="password" class="form-label small fw-medium text-secondary">Password</label>
            <div class="input-group">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="form-control"
                placeholder="Enter password"
                required
                autocomplete="current-password"
              />
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-emerald w-100 py-2 fw-semibold text-white shadow-sm"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <span>{{ isSubmitting ? 'Signing In...' : 'Sign In' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-card {
  width: 100%;
  max-width: 400px;
}

.bg-dark-slate {
  background-color: #0f172a;
}

.brand-badge {
  width: 48px;
  height: 48px;
  background-color: #10b981;
}

.btn-emerald {
  background-color: #10b981;
  border-color: #10b981;
}

.btn-emerald:hover, .btn-emerald:focus {
  background-color: #059669;
  border-color: #059669;
  color: #fff;
}
</style>
