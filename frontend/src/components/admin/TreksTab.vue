<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { api } from '@/services/api'
import AdminTrekUsersModal from '@/components/admin/AdminTrekUsersModal.vue'

const treks = ref([])
const staffList = ref([])
const loading = ref(true)
const actionError = ref('')
const successMessage = ref('')

// Search and Filters
const searchQuery = ref('')
const difficultyFilter = ref('')
const statusFilter = ref('')

// Modal state
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showAssignModal = ref(false)
const showDeleteModal = ref(false)
const showUsersModal = ref(false)
const trekForUsersModal = ref(null)
const isSubmitting = ref(false)

const openUsersModal = (trek) => {
  trekForUsersModal.value = trek
  showUsersModal.value = true
}

const currentTrek = ref({
  id: null,
  trek_name: '',
  location: '',
  difficulty: 'Easy',
  duration: 0,
  available_slots: 10,
  status: 'Open',
  start_date: '',
  end_date: '',
  assigned_staff_id: null,
})

const todayStr = computed(() => {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

const minEndDate = computed(() => {
  if (!currentTrek.value.start_date) return todayStr.value
  const parts = currentTrek.value.start_date.split('-')
  if (parts.length === 3) {
    const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
    d.setDate(d.getDate() + 1)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  return todayStr.value
})

watch(
  [() => currentTrek.value.start_date, () => currentTrek.value.end_date],
  ([start, end]) => {
    if (start && end) {
      if (end <= start) {
        currentTrek.value.end_date = minEndDate.value
        return
      }
      const startDate = new Date(start)
      const endDate = new Date(end)
      const diffMs = endDate.getTime() - startDate.getTime()
      const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))
      currentTrek.value.duration = diffDays > 0 ? diffDays : 0
    } else {
      currentTrek.value.duration = 0
    }
  }
)

// Assign modal state
const trekToAssign = ref(null)
const selectedStaffId = ref('')

const loadData = async () => {
  loading.value = true
  actionError.value = ''
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (difficultyFilter.value) params.difficulty = difficultyFilter.value
    if (statusFilter.value) params.status = statusFilter.value

    const [treksData, staffData] = await Promise.all([
      api.get('/api/admin/treks', params),
      api.get('/api/admin/staff'),
    ])

    treks.value = treksData || []
    staffList.value = staffData || []
  } catch (err) {
    actionError.value = err.message || 'Failed to fetch treks.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// Client search & ID filter fallback
const filteredTreks = computed(() => {
  return treks.value.filter(t => {
    if (!searchQuery.value) return true
    const q = searchQuery.value.toLowerCase().trim().replace(/^#/, '')
    return (
      (t.id && t.id.toString().includes(q)) ||
      (t.trek_name && t.trek_name.toLowerCase().includes(q)) ||
      (t.location && t.location.toLowerCase().includes(q))
    )
  })
})

const resetForm = () => {
  currentTrek.value = {
    id: null,
    trek_name: '',
    location: '',
    difficulty: 'Easy',
    duration: 0,
    available_slots: 10,
    status: 'Open',
    start_date: '',
    end_date: '',
    assigned_staff_id: null,
  }
}

const openCreate = () => {
  resetForm()
  showCreateModal.value = true
}

const openEdit = (trek) => {
  currentTrek.value = {
    id: trek.id,
    trek_name: trek.trek_name,
    location: trek.location,
    difficulty: trek.difficulty,
    duration: trek.duration,
    available_slots: trek.available_slots,
    status: trek.status,
    start_date: trek.start_date ? trek.start_date.substring(0, 10) : '',
    end_date: trek.end_date ? trek.end_date.substring(0, 10) : '',
    assigned_staff_id: trek.assigned_staff_id,
  }
  showEditModal.value = true
}

const openAssignModal = (trek) => {
  trekToAssign.value = trek
  selectedStaffId.value = trek.assigned_staff_id || ''
  showAssignModal.value = true
}

const openDeleteConfirm = (trek) => {
  currentTrek.value = { ...trek }
  showDeleteModal.value = true
}

const handleCreate = async () => {
  if (currentTrek.value.start_date && currentTrek.value.start_date < todayStr.value) {
    actionError.value = 'Start date cannot be in the past (before today).'
    return
  }
  if (currentTrek.value.start_date && currentTrek.value.end_date && currentTrek.value.end_date <= currentTrek.value.start_date) {
    actionError.value = 'End date must be strictly after the start date.'
    return
  }

  isSubmitting.value = true
  actionError.value = ''
  try {
    const payload = {
      ...currentTrek.value,
      duration: parseInt(currentTrek.value.duration),
      available_slots: parseInt(currentTrek.value.available_slots),
      assigned_staff_id: currentTrek.value.assigned_staff_id ? parseInt(currentTrek.value.assigned_staff_id) : null,
    }
    await api.post('/api/admin/treks', payload)
    successMessage.value = 'Trek route created successfully!'
    showCreateModal.value = false
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to create trek route.'
  } finally {
    isSubmitting.value = false
  }
}

const handleUpdate = async () => {
  if (currentTrek.value.start_date && currentTrek.value.start_date < todayStr.value) {
    actionError.value = 'Start date cannot be in the past (before today).'
    return
  }
  if (currentTrek.value.start_date && currentTrek.value.end_date && currentTrek.value.end_date <= currentTrek.value.start_date) {
    actionError.value = 'End date must be strictly after the start date.'
    return
  }

  isSubmitting.value = true
  actionError.value = ''
  try {
    const payload = {
      ...currentTrek.value,
      duration: parseInt(currentTrek.value.duration),
      available_slots: parseInt(currentTrek.value.available_slots),
      assigned_staff_id: currentTrek.value.assigned_staff_id ? parseInt(currentTrek.value.assigned_staff_id) : null,
    }
    await api.put(`/api/admin/treks/${currentTrek.value.id}`, payload)
    successMessage.value = 'Trek route updated successfully!'
    showEditModal.value = false
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to update trek route.'
  } finally {
    isSubmitting.value = false
  }
}

const handleAssignStaff = async () => {
  isSubmitting.value = true
  actionError.value = ''
  try {
    const staffId = selectedStaffId.value ? parseInt(selectedStaffId.value) : null
    await api.put(`/api/admin/treks/${trekToAssign.value.id}/assign`, { staff_id: staffId })
    successMessage.value = 'Staff assignment updated successfully!'
    showAssignModal.value = false
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to assign staff.'
  } finally {
    isSubmitting.value = false
  }
}

const handleDelete = async () => {
  isSubmitting.value = true
  actionError.value = ''
  try {
    await api.delete(`/api/admin/treks/${currentTrek.value.id}`)
    successMessage.value = 'Trek route removed successfully!'
    showDeleteModal.value = false
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to delete trek route.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="treks-tab">
    <!-- Action Alerts -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <div v-if="actionError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ actionError }}
      <button type="button" class="btn-close" @click="actionError = ''"></button>
    </div>

    <!-- Header Controls & Search Card -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-center">
          <!-- Search input -->
          <div class="col-12 col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Search trek by Name, Location, or ID..."
                @input="loadData"
              />
            </div>
          </div>

          <!-- Difficulty Filter -->
          <div class="col-6 col-md-2">
            <select v-model="difficultyFilter" class="form-select bg-light" @change="loadData">
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Moderate">Moderate</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <!-- Status Filter -->
          <div class="col-6 col-md-2">
            <select v-model="statusFilter" class="form-select bg-light" @change="loadData">
              <option value="">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Open">Open</option>
              <option value="Closed">Closed</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <!-- Add Trek Button -->
          <div class="col-12 col-md-3 text-md-end">
            <button class="btn btn-emerald text-white rounded-pill px-4 fw-semibold w-100 w-md-auto" @click="openCreate">
              <i class="bi bi-plus-lg me-2"></i>Create Trek Route
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Treks Table Card -->
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-map me-2 text-emerald"></i>Trekking Routes Management
        </h5>
        <span class="badge bg-light text-dark border rounded-pill px-3">
          Showing {{ filteredTreks.length }} routes
        </span>
      </div>

      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">ID</th>
                <th>Route Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Duration</th>
                <th>Available Slots</th>
                <th>Assigned Staff</th>
                <th>Status</th>
                <th class="pe-4 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="9" class="text-center py-4">
                  <div class="spinner-border text-emerald spinner-border-sm me-2"></div>
                  Loading trekking routes...
                </td>
              </tr>
              <tr v-else-if="filteredTreks.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">
                  No trek routes found matching your criteria.
                </td>
              </tr>
              <tr v-for="trek in filteredTreks" :key="trek.id">
                <td class="ps-4 fw-bold text-muted">#{{ trek.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ trek.trek_name }}</div>
                  <small v-if="trek.start_date" class="text-muted">
                    <i class="bi bi-calendar-event me-1"></i>{{ trek.start_date.substring(0, 10) }}
                  </small>
                </td>
                <td>
                  <i class="bi bi-geo-alt-fill text-danger me-1"></i>{{ trek.location }}
                </td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="{
                      'bg-success-subtle text-success': trek.difficulty === 'Easy',
                      'bg-warning-subtle text-warning-emphasis': trek.difficulty === 'Moderate',
                      'bg-danger-subtle text-danger': trek.difficulty === 'Hard'
                    }"
                  >
                    {{ trek.difficulty }}
                  </span>
                </td>
                <td><i class="bi bi-clock me-1 text-muted"></i>{{ trek.duration }} days</td>
                <td>
                  <span class="fw-bold">{{ trek.available_slots }}</span> slots
                </td>
                <td>
                  <div v-if="trek.assigned_staff" class="d-flex align-items-center">
                    <span class="badge bg-light text-dark border me-2">
                      <i class="bi bi-person-badge text-emerald me-1"></i>{{ trek.assigned_staff.name }}
                    </span>
                    <button class="btn btn-link btn-sm p-0 text-muted" @click="openAssignModal(trek)" title="Reassign">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                  </div>
                  <button v-else class="btn btn-outline-primary btn-sm rounded-pill px-3 py-1 text-nowrap" @click="openAssignModal(trek)">
                    <i class="bi bi-person-plus me-1"></i>Assign Staff
                  </button>
                </td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="{
                      'bg-secondary': trek.status === 'Pending',
                      'bg-info': trek.status === 'Approved',
                      'bg-success': trek.status === 'Open',
                      'bg-danger': trek.status === 'Closed',
                      'bg-primary': trek.status === 'Completed'
                    }"
                  >
                    {{ trek.status }}
                  </span>
                </td>
                <td class="pe-4 text-end">
                  <button class="btn btn-sm btn-light border me-2" @click="openUsersModal(trek)" title="View Booked Trekkers Roster">
                    <i class="bi bi-people-fill text-warning"></i>
                  </button>
                  <button class="btn btn-sm btn-light border me-2" @click="openEdit(trek)" title="Edit Trek">
                    <i class="bi bi-pencil-fill text-primary"></i>
                  </button>
                  <button class="btn btn-sm btn-light border" @click="openDeleteConfirm(trek)" title="Delete Trek">
                    <i class="bi bi-trash-fill text-danger"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showCreateModal || showEditModal" class="modal d-block fade show" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content bg-white border-0 shadow-lg rounded-4">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-header-title fw-bold text-dark">
              <i class="bi bi-compass-fill me-2 text-emerald"></i>
              {{ showCreateModal ? 'Create New Trek Route' : 'Edit Trek Route #' + currentTrek.id }}
            </h5>
            <button type="button" class="btn-close" @click="showCreateModal = false; showEditModal = false"></button>
          </div>

          <form @submit.prevent="showCreateModal ? handleCreate() : handleUpdate()">
            <div class="modal-body p-4">
              <div class="row g-3">
                <div class="col-12 col-md-6">
                  <label class="form-label fw-semibold">Trek Name *</label>
                  <input v-model="currentTrek.trek_name" type="text" class="form-control" placeholder="e.g. Everest Base Camp" required />
                </div>

                <div class="col-12 col-md-6">
                  <label class="form-label fw-semibold">Location *</label>
                  <input v-model="currentTrek.location" type="text" class="form-control" placeholder="e.g. Solukhumbu, Nepal" required />
                </div>

                <div class="col-6 col-md-4">
                  <label class="form-label fw-semibold">Difficulty *</label>
                  <select v-model="currentTrek.difficulty" class="form-select" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>

                <div class="col-6 col-md-4">
                  <label class="form-label fw-semibold">Duration (Days)</label>
                  <input
                    v-model="currentTrek.duration"
                    type="number"
                    class="form-control bg-light"
                    readonly
                    disabled
                  />
                  <small class="text-muted fs-8">Auto-calculated (excl. end day)</small>
                </div>

                <div class="col-6 col-md-4">
                  <label class="form-label fw-semibold">Available Slots *</label>
                  <input v-model="currentTrek.available_slots" type="number" min="0" class="form-control" required />
                </div>

                <div class="col-6 col-md-4">
                  <label class="form-label fw-semibold">Status *</label>
                  <select v-model="currentTrek.status" class="form-select" required>
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>

                <div class="col-6 col-md-4">
                  <label class="form-label fw-semibold">Start Date</label>
                  <input
                    v-model="currentTrek.start_date"
                    type="date"
                    :min="todayStr"
                    class="form-control"
                  />
                </div>

                <div class="col-6 col-md-4">
                  <label class="form-label fw-semibold">End Date</label>
                  <input
                    v-model="currentTrek.end_date"
                    type="date"
                    :min="minEndDate"
                    class="form-control"
                  />
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold">Assigned Staff Guide</label>
                  <select v-model="currentTrek.assigned_staff_id" class="form-select">
                    <option :value="null">-- None (Unassigned) --</option>
                    <option
                      v-for="s in staffList"
                      :key="s.id"
                      :value="s.id"
                      :disabled="s.status !== 'Active'"
                    >
                      {{ s.name }} ({{ s.email }}) - Status: {{ s.status }}{{ s.status !== 'Active' ? ' (Disabled - Inactive)' : '' }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div class="modal-footer border-0 pt-0 pb-4 px-4">
              <button type="button" class="btn btn-light rounded-pill px-4" @click="showCreateModal = false; showEditModal = false">
                Cancel
              </button>
              <button type="submit" class="btn btn-emerald text-white rounded-pill px-4" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ showCreateModal ? 'Save Trek Route' : 'Update Trek Route' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Assign Staff Modal -->
    <div v-if="showAssignModal" class="modal-backdrop fade show"></div>
    <div v-if="showAssignModal" class="modal d-block fade show" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content bg-white border-0 shadow-lg rounded-4">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-header-title fw-bold text-dark">
              <i class="bi bi-person-check-fill me-2 text-primary"></i>Assign Staff Guide
            </h5>
            <button type="button" class="btn-close" @click="showAssignModal = false"></button>
          </div>
          <div class="modal-body p-4">
            <p class="text-muted">
              Select a staff member to assign to <strong>{{ trekToAssign?.trek_name }}</strong>.
            </p>
            <div class="mb-3">
              <label class="form-label fw-semibold">Select Staff</label>
              <select v-model="selectedStaffId" class="form-select">
                <option value="">-- Unassign Staff --</option>
                <option
                  v-for="s in staffList"
                  :key="s.id"
                  :value="s.id"
                  :disabled="s.status !== 'Active'"
                >
                  {{ s.name }} - {{ s.email }} ({{ s.status }}){{ s.status !== 'Active' ? ' (Disabled - Inactive)' : '' }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer border-0 pt-0 pb-4 px-4">
            <button type="button" class="btn btn-light rounded-pill px-4" @click="showAssignModal = false">Cancel</button>
            <button type="button" class="btn btn-primary rounded-pill px-4" :disabled="isSubmitting" @click="handleAssignStaff">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              Save Assignment
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <div v-if="showDeleteModal" class="modal-backdrop fade show"></div>
    <div v-if="showDeleteModal" class="modal d-block fade show" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content bg-white border-0 shadow-lg rounded-4">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-header-title fw-bold text-danger">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>Confirm Removal
            </h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body p-4">
            Are you sure you want to remove the trek route <strong>{{ currentTrek.trek_name }}</strong> (#{{ currentTrek.id }})? This action cannot be undone.
          </div>
          <div class="modal-footer border-0 pt-0 pb-4 px-4">
            <button type="button" class="btn btn-light rounded-pill px-4" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger rounded-pill px-4" :disabled="isSubmitting" @click="handleDelete">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              Remove Route
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Admin Trek Users Modal -->
    <AdminTrekUsersModal
      :show="showUsersModal"
      :trek="trekForUsersModal"
      @close="showUsersModal = false"
    />
  </div>
</template>

<style scoped>
.btn-emerald {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.btn-emerald:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.text-emerald {
  color: #10b981;
}
</style>
