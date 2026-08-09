<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const staffList = ref([])
const loading = ref(true)
const actionError = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('')

const showAddModal = ref(false)
const showEditModal = ref(false)
const isSubmitting = ref(false)

const newStaff = ref({
  name: '',
  email: '',
  password: '',
  username: '',
  status: 'Active',
})

const editingStaff = ref({
  id: null,
  name: '',
  email: '',
  status: 'Active',
  active: true,
})

const loadData = async () => {
  loading.value = true
  actionError.value = ''
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value

    const data = await api.get('/api/admin/staff', params)
    staffList.value = data || []
  } catch (err) {
    actionError.value = err.message || 'Failed to load staff list.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const filteredStaff = computed(() => {
  return staffList.value.filter(s => {
    if (!searchQuery.value) return true
    const q = searchQuery.value.toLowerCase()
    return (
      (s.name && s.name.toLowerCase().includes(q)) ||
      (s.email && s.email.toLowerCase().includes(q))
    )
  })
})

const openAddModal = () => {
  newStaff.value = {
    name: '',
    email: '',
    password: '',
    username: '',
    status: 'Active',
  }
  showAddModal.value = true
}

const openEditModal = (staff) => {
  editingStaff.value = {
    id: staff.id,
    name: staff.name,
    email: staff.email,
    status: staff.status,
    active: staff.active,
  }
  showEditModal.value = true
}

const handleAddStaff = async () => {
  isSubmitting.value = true
  actionError.value = ''
  try {
    await api.post('/api/admin/staff', newStaff.value)
    successMessage.value = 'Trek staff member added successfully!'
    showAddModal.value = false
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to add staff member.'
  } finally {
    isSubmitting.value = false
  }
}

const handleUpdateStaff = async () => {
  isSubmitting.value = true
  actionError.value = ''
  try {
    await api.put(`/api/admin/staff/${editingStaff.value.id}`, {
      name: editingStaff.value.name,
      email: editingStaff.value.email,
      status: editingStaff.value.status,
    })
    successMessage.value = 'Staff member updated successfully!'
    showEditModal.value = false
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to update staff member.'
  } finally {
    isSubmitting.value = false
  }
}

const toggleStaffStatus = async (staff) => {
  actionError.value = ''
  const newActiveState = !staff.active
  const actionText = newActiveState ? 'activated' : 'blacklisted/deactivated'
  try {
    await api.put(`/api/admin/staff/${staff.id}/status`, {
      active: newActiveState,
      status: newActiveState ? 'Active' : 'Inactive',
    })
    successMessage.value = `Staff member ${staff.name} has been ${actionText}.`
    loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to update staff account status.'
  }
}
</script>

<template>
  <div class="staff-tab">
    <!-- Feedback Alerts -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <div v-if="actionError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ actionError }}
      <button type="button" class="btn-close" @click="actionError = ''"></button>
    </div>

    <!-- Filter & Action Card -->
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
                placeholder="Search staff by Name or Email..."
                @input="loadData"
              />
            </div>
          </div>

          <div class="col-6 col-md-3">
            <select v-model="statusFilter" class="form-select bg-light" @change="loadData">
              <option value="">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="On Leave">On Leave</option>
            </select>
          </div>

          <div class="col-12 col-md-3 text-md-end">
            <button class="btn btn-purple text-white rounded-pill px-4 fw-semibold w-100 w-md-auto" @click="openAddModal">
              <i class="bi bi-person-plus-fill me-2"></i>Add Staff Member
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Staff Table Card -->
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-person-workspace me-2 text-purple"></i>Trek Staff & Guides Directory
        </h5>
        <span class="badge bg-light text-dark border rounded-pill px-3">
          Total: {{ filteredStaff.length }} staff members
        </span>
      </div>

      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">Staff ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Staff Status</th>
                <th>Account Status</th>
                <th>Assigned Treks</th>
                <th class="pe-4 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4">
                  <div class="spinner-border text-purple spinner-border-sm me-2"></div>
                  Loading staff directory...
                </td>
              </tr>
              <tr v-else-if="filteredStaff.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No staff members found matching your search.
                </td>
              </tr>
              <tr v-for="staff in filteredStaff" :key="staff.id">
                <td class="ps-4 fw-bold text-muted">#{{ staff.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ staff.name }}</div>
                  <small v-if="staff.username" class="text-muted">@{{ staff.username }}</small>
                </td>
                <td>{{ staff.email }}</td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="{
                      'bg-success-subtle text-success': staff.status === 'Active',
                      'bg-danger-subtle text-danger': staff.status === 'Inactive',
                      'bg-warning-subtle text-warning-emphasis': staff.status === 'On Leave'
                    }"
                  >
                    {{ staff.status }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="staff.active ? 'bg-success' : 'bg-danger'"
                  >
                    {{ staff.active ? 'Active' : 'Blacklisted / Deactivated' }}
                  </span>
                </td>
                <td>
                  <div v-if="staff.assigned_treks && staff.assigned_treks.length > 0">
                    <span v-for="t in staff.assigned_treks" :key="t.id" class="badge bg-light text-dark border me-1">
                      {{ t.trek_name }}
                    </span>
                  </div>
                  <span v-else class="text-muted small">No treks assigned</span>
                </td>
                <td class="pe-4 text-end">
                  <button class="btn btn-sm btn-light border me-2" @click="openEditModal(staff)" title="Edit Staff Details">
                    <i class="bi bi-pencil-fill text-primary"></i>
                  </button>
                  <button
                    class="btn btn-sm rounded-pill px-3"
                    :class="staff.active ? 'btn-outline-danger' : 'btn-outline-success'"
                    @click="toggleStaffStatus(staff)"
                  >
                    <i :class="staff.active ? 'bi bi-slash-circle me-1' : 'bi bi-check-circle me-1'"></i>
                    {{ staff.active ? 'Blacklist' : 'Activate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Staff Modal -->
    <div v-if="showAddModal" class="modal-backdrop fade show"></div>
    <div v-if="showAddModal" class="modal d-block fade show" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content bg-white border-0 shadow-lg rounded-4">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-header-title fw-bold text-dark">
              <i class="bi bi-person-plus-fill me-2 text-purple"></i>Add New Trek Staff Member
            </h5>
            <button type="button" class="btn-close" @click="showAddModal = false"></button>
          </div>
          <form @submit.prevent="handleAddStaff">
            <div class="modal-body p-4">
              <div class="mb-3">
                <label class="form-label fw-semibold">Full Name *</label>
                <input v-model="newStaff.name" type="text" class="form-control" placeholder="e.g. Tenzing Norgay" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Email Address *</label>
                <input v-model="newStaff.email" type="email" class="form-control" placeholder="staff@example.com" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Initial Password *</label>
                <input v-model="newStaff.password" type="password" class="form-control" placeholder="Password for login" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Username (Optional)</label>
                <input v-model="newStaff.username" type="text" class="form-control" placeholder="guide_tenzing" />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Status *</label>
                <select v-model="newStaff.status" class="form-select" required>
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                  <option value="On Leave">On Leave</option>
                </select>
              </div>
            </div>
            <div class="modal-footer border-0 pt-0 pb-4 px-4">
              <button type="button" class="btn btn-light rounded-pill px-4" @click="showAddModal = false">Cancel</button>
              <button type="submit" class="btn btn-purple text-white rounded-pill px-4" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                Save Staff
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Staff Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showEditModal" class="modal d-block fade show" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content bg-white border-0 shadow-lg rounded-4">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-header-title fw-bold text-dark">
              <i class="bi bi-pencil-square me-2 text-primary"></i>Edit Staff Member #{{ editingStaff.id }}
            </h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <form @submit.prevent="handleUpdateStaff">
            <div class="modal-body p-4">
              <div class="mb-3">
                <label class="form-label fw-semibold">Full Name</label>
                <input v-model="editingStaff.name" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Email Address</label>
                <input v-model="editingStaff.email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Staff Status</label>
                <select v-model="editingStaff.status" class="form-select" required>
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                  <option value="On Leave">On Leave</option>
                </select>
              </div>
            </div>
            <div class="modal-footer border-0 pt-0 pb-4 px-4">
              <button type="button" class="btn btn-light rounded-pill px-4" @click="showEditModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary rounded-pill px-4" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border: none;
}

.btn-purple:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
}

.text-purple {
  color: #8b5cf6;
}
</style>
