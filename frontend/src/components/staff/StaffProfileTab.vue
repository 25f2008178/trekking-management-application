<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const actionError = ref('')
const successMessage = ref('')

const loadProfile = () => {
  if (authStore.user) {
    name.value = authStore.user.name || ''
    email.value = authStore.user.email || ''
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchProfile()
  }
  loadProfile()
})

const handleUpdateProfile = async () => {
  if (!name.value || !email.value) {
    actionError.value = 'Full Name and Email are required fields.'
    return
  }

  if (password.value) {
    if (password.value !== confirmPassword.value) {
      actionError.value = 'New passwords do not match.'
      return
    }
    if (password.value.length < 6) {
      actionError.value = 'New password must be at least 6 characters long.'
      return
    }
  }

  isSubmitting.value = true
  actionError.value = ''
  successMessage.value = ''

  try {
    const payload = {
      name: name.value,
      email: email.value
    }
    if (password.value) {
      payload.password = password.value
    }

    await api.put('/api/user/profile', payload)
    await authStore.fetchProfile()
    successMessage.value = 'Your staff profile and credentials have been updated successfully!'
    password.value = ''
    confirmPassword.value = ''
  } catch (err) {
    actionError.value = err.message || 'Failed to update profile details.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="staff-profile-tab">
    <!-- Action Alerts -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <div v-if="actionError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ actionError }}
      <button type="button" class="btn-close" @click="actionError = ''"></button>
    </div>

    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6">
        <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
          <!-- Card Header -->
          <div class="card-header bg-dark-slate text-white p-4">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <span class="badge bg-emerald text-white rounded-pill px-3 py-1 fs-8">
                <i class="bi bi-person-badge-fill me-1"></i>Staff Guide Account
              </span>
              <span class="badge bg-success-subtle text-success border border-success fs-8 rounded-pill px-2.5 py-1">
                Active Staff Profile
              </span>
            </div>
            <h5 class="fw-bold mb-1 d-flex align-items-center">
              <i class="bi bi-person-gear me-2 text-emerald"></i>Staff Guide Profile Settings
            </h5>
            <p class="text-white-50 small mb-0">Manage your personal profile details and security credentials</p>
          </div>

          <!-- Form Body -->
          <div class="card-body p-4">
            <form @submit.prevent="handleUpdateProfile">
              <div class="mb-3">
                <label class="form-label small fw-semibold text-secondary">Full Name *</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0"><i class="bi bi-person text-muted"></i></span>
                  <input
                    v-model="name"
                    type="text"
                    class="form-control bg-light border-start-0"
                    placeholder="Full Name"
                    required
                  />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold text-secondary">Email Address *</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0"><i class="bi bi-envelope text-muted"></i></span>
                  <input
                    v-model="email"
                    type="email"
                    class="form-control bg-light border-start-0"
                    placeholder="Email Address"
                    required
                  />
                </div>
              </div>

              <hr class="my-4" />

              <h6 class="fw-bold text-dark mb-1">Update Password (Optional)</h6>
              <p class="text-muted small mb-3">Leave blank if you do not wish to change your current password.</p>

              <div class="mb-3">
                <label class="form-label small fw-semibold text-secondary">New Password</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0"><i class="bi bi-lock text-muted"></i></span>
                  <input
                    v-model="password"
                    type="password"
                    class="form-control bg-light border-start-0"
                    placeholder="Enter new password (min. 6 characters)"
                  />
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label small fw-semibold text-secondary">Confirm New Password</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0"><i class="bi bi-shield-lock text-muted"></i></span>
                  <input
                    v-model="confirmPassword"
                    type="password"
                    class="form-control bg-light border-start-0"
                    placeholder="Re-enter new password"
                  />
                </div>
              </div>

              <div class="d-flex justify-content-end">
                <button
                  type="submit"
                  class="btn btn-emerald text-white rounded-pill px-4 py-2 fw-semibold shadow-sm"
                  :disabled="isSubmitting"
                >
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                  Save Profile Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-dark-slate {
  background-color: #0f172a;
}

.bg-emerald {
  background-color: #10b981 !important;
}

.text-emerald {
  color: #10b981 !important;
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

.fs-8 {
  font-size: 0.75rem;
}
</style>
