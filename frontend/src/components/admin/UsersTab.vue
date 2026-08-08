<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const users = ref([])
const loading = ref(true)
const actionError = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const activeFilter = ref('')
const roleFilter = ref('')

const loadData = async () => {
  loading.value = true
  actionError.value = ''
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (activeFilter.value !== '') params.active = activeFilter.value
    if (roleFilter.value) params.role = roleFilter.value

    const data = await api.get('/api/admin/users', params)
    users.value = data || []
  } catch (err) {
    actionError.value = err.message || 'Failed to load user directory.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const filteredUsers = computed(() => {
  return users.value.filter(u => {
    if (!searchQuery.value) return true
    const q = searchQuery.value.toLowerCase()
    return (
      u.id.toString().includes(q) ||
      (u.name && u.name.toLowerCase().includes(q)) ||
      (u.email && u.email.toLowerCase().includes(q))
    )
  })
})

const toggleUserActiveStatus = async (user) => {
  actionError.value = ''
  const newActiveState = !user.active
  const actionText = newActiveState ? 'activated' : 'blacklisted/deactivated'
  try {
    await api.put(`/api/admin/users/${user.id}/status`, {
      active: newActiveState
    })
    successMessage.value = `User ${user.name} has been ${actionText}.`
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to update user status.'
  }
}
</script>

<template>
  <div class="users-tab">
    <!-- Feedback Alerts -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <div v-if="actionError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ actionError }}
      <button type="button" class="btn-close" @click="actionError = ''"></button>
    </div>

    <!-- Filter Card -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-center">
          <div class="col-12 col-md-6">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Search user by Name, Email, or ID..."
                @input="loadData"
              />
            </div>
          </div>

          <div class="col-6 col-md-3">
            <select v-model="activeFilter" class="form-select bg-light" @change="loadData">
              <option value="">All Account States</option>
              <option value="true">Active Only</option>
              <option value="false">Blacklisted / Inactive Only</option>
            </select>
          </div>

          <div class="col-6 col-md-3">
            <select v-model="roleFilter" class="form-select bg-light" @change="loadData">
              <option value="">All System Roles</option>
              <option value="user">User Role</option>
              <option value="staff">Staff Role</option>
              <option value="admin">Admin Role</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table Card -->
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-people-fill me-2 text-primary"></i>System Users Directory
        </h5>
        <span class="badge bg-light text-dark border rounded-pill px-3">
          Total Users: {{ filteredUsers.length }}
        </span>
      </div>

      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">User ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>System Roles</th>
                <th>Total Bookings</th>
                <th>Status</th>
                <th class="pe-4 text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4">
                  <div class="spinner-border text-primary spinner-border-sm me-2"></div>
                  Loading user records...
                </td>
              </tr>
              <tr v-else-if="filteredUsers.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No users found matching your search filters.
                </td>
              </tr>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td class="ps-4 fw-bold text-muted">#{{ user.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ user.name }}</div>
                  <small v-if="user.username" class="text-muted">@{{ user.username }}</small>
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <div class="d-flex flex-wrap gap-1">
                    <span v-for="r in user.roles" :key="r" class="badge rounded-pill" :class="{
                      'bg-danger': r === 'admin',
                      'bg-purple text-white': r === 'staff',
                      'bg-info text-dark': r === 'user'
                    }">
                      {{ r }}
                    </span>
                  </div>
                </td>
                <td>
                  <span class="fw-bold">{{ user.bookings_count || 0 }}</span> bookings
                </td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="user.active ? 'bg-success' : 'bg-danger'"
                  >
                    <i :class="user.active ? 'bi bi-check-circle me-1' : 'bi bi-slash-circle me-1'"></i>
                    {{ user.active ? 'Active' : 'Blacklisted' }}
                  </span>
                </td>
                <td class="pe-4 text-end">
                  <button
                    class="btn btn-sm rounded-pill px-3"
                    :class="user.active ? 'btn-outline-danger' : 'btn-outline-success'"
                    @click="toggleUserActiveStatus(user)"
                  >
                    <i :class="user.active ? 'bi bi-slash-circle me-1' : 'bi bi-check-circle me-1'"></i>
                    {{ user.active ? 'Blacklist / Deactivate' : 'Reactivate User' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-purple {
  background-color: #8b5cf6;
}
</style>
