<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

import TrekCard from '@/components/staff/TrekCard.vue'
import EditSlotsModal from '@/components/staff/EditSlotsModal.vue'
import ParticipantListModal from '@/components/staff/ParticipantListModal.vue'
import AppLogo from '@/components/common/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const treks = ref([])
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('')

// Modal States
const showSlotsModal = ref(false)
const showParticipantsModal = ref(false)
const showCompleteConfirmModal = ref(false)

const selectedTrek = ref(null)
const isSubmittingAction = ref(false)

const fetchAssignedTreks = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (searchQuery.value) params.search = searchQuery.value

    const data = await api.get('/api/staff/treks', params)
    treks.value = data || []
  } catch (err) {
    if (err.status === 403) {
      errorMessage.value = 'Access Denied: You are not authorized as active staff.'
    } else {
      errorMessage.value = err.message || 'Failed to fetch assigned treks.'
    }
  } finally {
    loading.value = false
  }
}

// KPI Stats
const totalAssignedTreks = computed(() => treks.value.length)
const totalRegisteredTrekkers = computed(() =>
  treks.value.reduce((sum, t) => sum + (t.bookings_count || 0), 0)
)
const openTreksCount = computed(() =>
  treks.value.filter((t) => (t.status || '').toLowerCase() === 'open').length
)
const completedTreksCount = computed(() =>
  treks.value.filter((t) => (t.status || '').toLowerCase() === 'completed').length
)

// Filtered Treks list (client-side backup filtering)
const filteredTreks = computed(() => {
  return treks.value.filter((t) => {
    const matchesSearch = !searchQuery.value.trim() ||
      t.trek_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      t.location.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesStatus = !statusFilter.value ||
      t.status.toLowerCase() === statusFilter.value.toLowerCase()

    return matchesSearch && matchesStatus
  })
})

// Handlers
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const openEditSlotsModal = (trek) => {
  selectedTrek.value = trek
  showSlotsModal.value = true
}

const openParticipantsModal = (trek) => {
  selectedTrek.value = trek
  showParticipantsModal.value = true
}

const handleTrekSlotsUpdated = (updatedTrek) => {
  const index = treks.value.findIndex((t) => t.id === updatedTrek.id)
  if (index !== -1) {
    treks.value[index] = { ...treks.value[index], ...updatedTrek }
  }
  showToastSuccess('Available trek slots updated successfully.')
}

const handleUpdateStatus = async (trek, newStatus) => {
  try {
    const res = await api.put(`/api/staff/treks/${trek.id}`, { status: newStatus })
    const updated = res.trek || { ...trek, status: newStatus }
    const index = treks.value.findIndex((t) => t.id === trek.id)
    if (index !== -1) {
      treks.value[index] = { ...treks.value[index], ...updated }
    }
    showToastSuccess(`Trek status updated to "${newStatus}".`)
  } catch (err) {
    if (err.status === 403) {
      errorMessage.value = 'Forbidden. This trek is not assigned to you.'
    } else {
      errorMessage.value = err.message || 'Failed to update trek status.'
    }
  }
}

const openCompleteConfirmation = (trek) => {
  selectedTrek.value = trek
  showCompleteConfirmModal.value = true
}

const handleConfirmMarkCompleted = async () => {
  if (!selectedTrek.value) return
  isSubmittingAction.value = true
  errorMessage.value = ''
  try {
    const res = await api.put(`/api/staff/treks/${selectedTrek.value.id}/complete`)
    const updated = res.trek || { ...selectedTrek.value, status: 'Completed' }
    const index = treks.value.findIndex((t) => t.id === selectedTrek.value.id)
    if (index !== -1) {
      treks.value[index] = { ...treks.value[index], ...updated }
    }
    showToastSuccess(`Trek "${selectedTrek.value.trek_name}" marked as Completed!`)
    showCompleteConfirmModal.value = false
  } catch (err) {
    if (err.status === 403) {
      errorMessage.value = 'Forbidden. This trek is not assigned to you.'
    } else {
      errorMessage.value = err.message || 'Failed to mark trek as completed.'
    }
  } finally {
    isSubmittingAction.value = false
  }
}

const showToastSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => {
    if (successMessage.value === msg) {
      successMessage.value = ''
    }
  }, 4000)
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchProfile()
  }
  fetchAssignedTreks()
})
</script>

<template>
  <div class="staff-dashboard min-vh-100 bg-light">
    <!-- Top Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark-slate shadow-sm sticky-top">
      <div class="container-fluid px-4">
        <a class="navbar-brand d-flex align-items-center text-decoration-none" href="#">
          <AppLogo size="sm" badge-text="Staff Guide" />
        </a>

        <div class="d-flex align-items-center ms-auto">
          <!-- Staff Profile Pill -->
          <div class="d-flex align-items-center text-white me-3 bg-white-10 px-3 py-1.5 rounded-pill">
            <i class="bi bi-person-badge fs-5 me-2 text-emerald"></i>
            <div>
              <div class="fw-semibold lh-1 fs-7">{{ authStore.userName }}</div>
              <small class="text-white-50 fs-8">Assigned Staff Guide</small>
            </div>
          </div>

          <!-- Logout Button -->
          <button class="btn btn-outline-light btn-sm rounded-pill px-3" @click="handleLogout">
            <i class="bi bi-box-arrow-right me-1"></i>Sign Out
          </button>
        </div>
      </div>
    </nav>

    <div class="container-fluid px-4 py-4">
      <!-- Success / Error Toast Alerts -->
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show rounded-3 shadow-sm mb-4" role="alert">
        <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>

      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show rounded-3 shadow-sm mb-4" role="alert">
        <i class="bi bi-exclamation-octagon-fill me-2"></i>{{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Staff Scope Banner -->
      <div class="card border-0 shadow-sm rounded-4 bg-gradient-emerald text-white mb-4 overflow-hidden position-relative">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-lg-8">
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge bg-white text-emerald fw-bold rounded-pill px-3 py-1 fs-8">
                  <i class="bi bi-lock-fill me-1"></i>Restricted Staff Portal
                </span>
              </div>
              <h3 class="fw-bold mb-1">Trek Staff Management Console</h3>
              <p class="text-white-80 mb-0 fs-7">
                You are currently viewing treks assigned specifically to your staff guide profile. Manage slots, trek status, and trekker rosters securely.
              </p>
            </div>
            <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
              <button class="btn btn-light text-emerald fw-semibold rounded-pill px-4 shadow-sm" @click="fetchAssignedTreks">
                <i class="bi bi-arrow-clockwise me-1.5"></i>Refresh Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Overview Cards -->
      <div class="row g-3 mb-4">
        <!-- Total Assigned Treks -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-emerald-subtle text-emerald rounded-4 p-3 me-3">
                <i class="bi bi-map-fill fs-3"></i>
              </div>
              <div>
                <div class="text-muted small fw-medium">Assigned Treks</div>
                <h3 class="fw-bold mb-0 text-dark">{{ totalAssignedTreks }}</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Registered Trekkers -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-primary-subtle text-primary rounded-4 p-3 me-3">
                <i class="bi bi-people-fill fs-3"></i>
              </div>
              <div>
                <div class="text-muted small fw-medium">Registered Trekkers</div>
                <h3 class="fw-bold mb-0 text-dark">{{ totalRegisteredTrekkers }}</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Open Treks -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-success-subtle text-success rounded-4 p-3 me-3">
                <i class="bi bi-door-open-fill fs-3"></i>
              </div>
              <div>
                <div class="text-muted small fw-medium">Active / Open Treks</div>
                <h3 class="fw-bold mb-0 text-dark">{{ openTreksCount }}</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Completed Treks -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-info-subtle text-info-emphasis rounded-4 p-3 me-3">
                <i class="bi bi-check-circle-fill fs-3"></i>
              </div>
              <div>
                <div class="text-muted small fw-medium">Completed Treks</div>
                <h3 class="fw-bold mb-0 text-dark">{{ completedTreksCount }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls Toolbar (Search & Filter) -->
      <div class="card border-0 shadow-sm rounded-4 mb-4">
        <div class="card-body p-3">
          <div class="row g-3 align-items-center">
            <!-- Search Bar -->
            <div class="col-12 col-md-6 col-lg-5">
              <div class="position-relative">
                <i class="bi bi-search position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"></i>
                <input
                  v-model="searchQuery"
                  type="text"
                  class="form-control ps-5 rounded-pill border"
                  placeholder="Search assigned treks by name or location..."
                  @input="fetchAssignedTreks"
                />
              </div>
            </div>

            <!-- Status Filter -->
            <div class="col-12 col-md-4 col-lg-4 ms-auto d-flex align-items-center gap-2">
              <label class="form-label mb-0 text-nowrap small fw-semibold text-secondary">Filter Status:</label>
              <select
                v-model="statusFilter"
                class="form-select rounded-pill border"
                @change="fetchAssignedTreks"
              >
                <option value="">All Statuses</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
                <option value="Completed">Completed</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Treks Grid / Loading / Empty State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-emerald" role="status">
          <span class="visually-hidden">Loading assigned treks...</span>
        </div>
        <p class="text-muted small mt-2">Fetching your assigned treks...</p>
      </div>

      <div v-else-if="filteredTreks.length > 0" class="row g-4">
        <div v-for="trek in filteredTreks" :key="trek.id" class="col-12 col-md-6 col-xl-4">
          <TrekCard
            :trek="trek"
            @edit-slots="openEditSlotsModal"
            @view-participants="openParticipantsModal"
            @update-status="handleUpdateStatus"
            @mark-completed="openCompleteConfirmation"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-5 bg-white rounded-4 shadow-sm border">
        <div class="mb-3">
          <i class="bi bi-compass text-muted display-4"></i>
        </div>
        <h5 class="fw-bold text-dark mb-1">No Assigned Treks Found</h5>
        <p class="text-muted small max-w-md mx-auto mb-3">
          {{ searchQuery || statusFilter
            ? 'No assigned treks match your current search or filter criteria.'
            : 'You have not been assigned to manage any treks yet. Please contact your system administrator.' }}
        </p>
        <button v-if="searchQuery || statusFilter" class="btn btn-outline-secondary rounded-pill px-4" @click="searchQuery = ''; statusFilter = ''; fetchAssignedTreks();">
          Reset Filters
        </button>
      </div>
    </div>

    <!-- Modals -->
    <EditSlotsModal
      :show="showSlotsModal"
      :trek="selectedTrek"
      @close="showSlotsModal = false"
      @updated="handleTrekSlotsUpdated"
    />

    <ParticipantListModal
      :show="showParticipantsModal"
      :trek="selectedTrek"
      @close="showParticipantsModal = false"
    />

    <!-- Mark Trek Completed Confirmation Modal -->
    <div v-if="showCompleteConfirmModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-dialog modal-dialog-centered w-100 max-w-md p-3">
        <div class="modal-content bg-white border-0 shadow-lg rounded-4 overflow-hidden">
          <div class="modal-header bg-dark-slate text-white py-3 px-4">
            <h5 class="modal-title fs-6 fw-bold mb-0 d-flex align-items-center">
              <i class="bi bi-exclamation-triangle-fill me-2 text-warning"></i>
              Confirm Trek Completion
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="showCompleteConfirmModal = false"></button>
          </div>
          <div class="modal-body p-4 text-center">
            <div class="mb-3">
              <i class="bi bi-check-circle text-primary display-5"></i>
            </div>
            <h6 class="fw-bold text-dark mb-2">
              Mark "{{ selectedTrek?.trek_name }}" as Completed?
            </h6>
            <p class="text-muted small mb-0">
              This action will set the trek status to <strong>Completed</strong> and mark all active bookings for this trek as <strong>Completed</strong>.
            </p>
          </div>
          <div class="modal-footer bg-light border-0 py-3 px-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-light rounded-pill px-4" :disabled="isSubmittingAction" @click="showCompleteConfirmModal = false">
              Cancel
            </button>
            <button type="button" class="btn btn-primary rounded-pill px-4 fw-semibold" :disabled="isSubmittingAction" @click="handleConfirmMarkCompleted">
              <span v-if="isSubmittingAction" class="spinner-border spinner-border-sm me-1"></span>
              Confirm Completion
            </button>
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

.brand-badge {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.bg-emerald {
  background-color: #10b981 !important;
}

.bg-gradient-emerald {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #064e3b 100%);
}

.text-emerald {
  color: #10b981 !important;
}

.bg-emerald-subtle {
  background-color: rgba(16, 185, 129, 0.12) !important;
}

.bg-white-10 {
  background: rgba(255, 255, 255, 0.08);
}

.text-white-80 {
  color: rgba(255, 255, 255, 0.8);
}

.stat-icon {
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
}

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

.max-w-md {
  max-width: 440px;
}

.fs-7 {
  font-size: 0.85rem;
}

.fs-8 {
  font-size: 0.725rem;
}
</style>
