<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '@/services/api'

const props = defineProps({
  show: { type: Boolean, default: false },
  trek: { type: Object, default: null }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const errorMsg = ref('')
const searchQuery = ref('')
const registeredUsers = ref([])
const totalRegistered = ref(0)

const fetchTrekkers = async () => {
  if (!props.trek?.id) return
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await api.get(`/api/admin/treks/${props.trek.id}/users`)
    registeredUsers.value = res.registered_users || []
    totalRegistered.value = res.total_registered || 0
  } catch (err) {
    errorMsg.value = err.message || 'Failed to fetch registered trekkers for this route.'
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.show, props.trek],
  ([newShow, newTrek]) => {
    if (newShow && newTrek) {
      searchQuery.value = ''
      fetchTrekkers()
    }
  },
  { immediate: true }
)

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return registeredUsers.value
  const q = searchQuery.value.toLowerCase()
  return registeredUsers.value.filter(
    (u) =>
      (u.name && u.name.toLowerCase().includes(q)) ||
      (u.email && u.email.toLowerCase().includes(q))
  )
})

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A'
  try {
    const utcDateStr = isoStr.endsWith('Z') || isoStr.includes('+') ? isoStr : `${isoStr}Z`
    return new Date(utcDateStr).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return isoStr
  }
}

const getStatusBadge = (status) => {
  const s = (status || '').toLowerCase()
  if (s === 'booked') return 'bg-success text-white'
  if (s === 'completed') return 'bg-primary text-white'
  if (s === 'cancelled') return 'bg-secondary text-white'
  return 'bg-info text-dark'
}
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
    <div class="modal-dialog modal-dialog-centered modal-lg w-100 p-3">
      <div class="modal-content bg-white border-0 shadow-lg rounded-4 overflow-hidden">
        <!-- Header -->
        <div class="modal-header bg-dark-slate text-white py-3 px-4 d-flex align-items-center justify-content-between">
          <div>
            <h5 class="modal-title fs-6 fw-bold mb-0 d-flex align-items-center">
              <i class="bi bi-people-fill me-2 text-warning"></i>
              Admin Audit: Registered Trekkers Roster
            </h5>
            <small class="text-white-50" v-if="trek">
              {{ trek.trek_name }} &bull; <i class="bi bi-geo-alt me-0.5"></i>{{ trek.location }} (ID: #{{ trek.id }})
            </small>
          </div>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>

        <!-- Body -->
        <div class="modal-body p-4">
          <!-- Search & Counter Bar -->
          <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3 mb-4">
            <div class="position-relative flex-grow-1 max-w-sm">
              <i class="bi bi-search position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"></i>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control ps-5 rounded-pill shadow-sm"
                placeholder="Search participant by name or email..."
              />
            </div>
            <div class="badge bg-warning-subtle text-warning-emphasis border border-warning fs-7 py-2 px-3 rounded-pill text-nowrap">
              <i class="bi bi-person-check-fill me-1.5"></i>Active Registered Trekkers: <strong>{{ totalRegistered }}</strong>
            </div>
          </div>

          <!-- Alert error -->
          <div v-if="errorMsg" class="alert alert-danger py-2.5 px-3 rounded-3 mb-3">
            <i class="bi bi-exclamation-octagon-fill me-2"></i>{{ errorMsg }}
          </div>

          <!-- Loading state -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-warning" role="status">
              <span class="visually-hidden">Loading registered users...</span>
            </div>
            <p class="text-muted small mt-2">Fetching trekker booking records...</p>
          </div>

          <!-- Trekkers Table -->
          <div v-else-if="filteredUsers.length > 0" class="table-responsive rounded-3 border overflow-hidden">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col" class="ps-3 py-3 text-secondary small fw-semibold">#</th>
                  <th scope="col" class="py-3 text-secondary small fw-semibold">Trekker Name</th>
                  <th scope="col" class="py-3 text-secondary small fw-semibold">Email Contact</th>
                  <th scope="col" class="py-3 text-secondary small fw-semibold">Booking Date</th>
                  <th scope="col" class="pe-3 py-3 text-secondary small fw-semibold text-end">Booking Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, idx) in filteredUsers" :key="user.booking_id || idx">
                  <td class="ps-3 fw-semibold text-muted small">{{ idx + 1 }}</td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="avatar-circle bg-emerald text-white fw-bold me-2.5 rounded-circle d-flex align-items-center justify-content-center">
                        {{ (user.name || user.email || 'U').charAt(0).toUpperCase() }}
                      </div>
                      <span class="fw-semibold text-dark">{{ user.name || 'Unnamed Trekker' }}</span>
                    </div>
                  </td>
                  <td class="text-secondary small">{{ user.email || 'No email provided' }}</td>
                  <td class="text-secondary small">{{ formatDate(user.booking_date) }}</td>
                  <td class="pe-3 text-end">
                    <span class="badge rounded-pill px-2.5 py-1.5 fs-8" :class="getStatusBadge(user.status)">
                      {{ user.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-else-if="!loading" class="text-center py-5 bg-light rounded-4 border border-dashed">
            <i class="bi bi-person-x text-muted display-6 d-block mb-2"></i>
            <h6 class="fw-semibold text-secondary mb-1">No Trekkers Found</h6>
            <p class="text-muted small mb-0">
              {{ searchQuery ? 'No participants match your search criteria.' : 'No registered trekkers for this route yet.' }}
            </p>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer bg-light border-0 py-3 px-4 d-flex justify-content-between">
          <small class="text-muted fs-8"><i class="bi bi-shield-lock me-1"></i>Administrator System Audit Access</small>
          <button type="button" class="btn btn-secondary rounded-pill px-4" @click="$emit('close')">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 1050;
}

.modal-content,
.modal-body {
  background-color: #ffffff !important;
}

.max-w-sm {
  max-width: 340px;
}

.bg-dark-slate {
  background-color: #0f172a;
}

.bg-emerald {
  background-color: #10b981 !important;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  font-size: 0.85rem;
}

.fs-7 {
  font-size: 0.85rem;
}

.fs-8 {
  font-size: 0.75rem;
}
</style>
