<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLogo from '@/components/common/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  if (!name.value || !email.value || !password.value) {
    errorMessage.value = 'Please fill out all required fields.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  if (password.value.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters long.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  try {
    await authStore.register(name.value, email.value, password.value, confirmPassword.value)
    router.push('/dashboard')
  } catch (err) {
    errorMessage.value = authStore.error || err.message || 'Registration failed. Email may already be registered.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="register-wrapper min-vh-100 bg-light d-flex align-items-center justify-content-center p-3">
    <div class="register-card card border-0 shadow-sm rounded-4 overflow-hidden">
      <!-- Card Header -->
      <div class="bg-dark-slate text-center p-4">
        <div class="d-flex justify-content-center mb-2">
          <AppLogo size="lg" :show-text="false" />
        </div>
        <h4 class="fw-bold text-white mb-1">Create Trekker Account</h4>
        <p class="text-white-50 small mb-0">Join expeditions & book your next trek</p>
      </div>

      <!-- Card Body -->
      <div class="card-body p-4">
        <div v-if="errorMessage" class="alert alert-danger py-2 px-3 small rounded-3 mb-3" role="alert">
          <i class="bi bi-exclamation-circle-fill me-1.5"></i>
          <span>{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label for="name" class="form-label small fw-semibold text-secondary">Full Name *</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-person text-muted"></i></span>
              <input
                id="name"
                v-model="name"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="e.g. Alex Harrison"
                required
              />
            </div>
          </div>

          <div class="mb-3">
            <label for="email" class="form-label small fw-semibold text-secondary">Email Address *</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-envelope text-muted"></i></span>
              <input
                id="email"
                v-model="email"
                type="email"
                class="form-control bg-light border-start-0"
                placeholder="alex@example.com"
                required
              />
            </div>
          </div>

          <div class="mb-3">
            <label for="password" class="form-label small fw-semibold text-secondary">Password *</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-lock text-muted"></i></span>
              <input
                id="password"
                v-model="password"
                type="password"
                class="form-control bg-light border-start-0"
                placeholder="At least 6 characters"
                required
              />
            </div>
          </div>

          <div class="mb-4">
            <label for="confirmPassword" class="form-label small fw-semibold text-secondary">Confirm Password *</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-shield-lock text-muted"></i></span>
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                type="password"
                class="form-control bg-light border-start-0"
                placeholder="Re-enter password"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-emerald text-white w-100 rounded-pill py-2.5 fw-semibold shadow-sm mb-3"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            Register Account
          </button>
        </form>

        <div class="text-center pt-2 border-top">
          <span class="small text-muted">Already have an account? </span>
          <router-link to="/login" class="small text-emerald fw-semibold text-decoration-none">
            Sign In Here
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-card {
  width: 100%;
  max-width: 440px;
}

.bg-dark-slate {
  background-color: #0f172a;
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

.text-emerald {
  color: #10b981 !important;
}
</style>
