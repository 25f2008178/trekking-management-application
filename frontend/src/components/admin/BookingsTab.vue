<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'
import AdminTrekUsersModal from '@/components/admin/AdminTrekUsersModal.vue'

const treks = ref([])
const users = ref([])
const loading = ref(true)
const fetchError = ref('')

const searchQuery = ref('')
const statusFilter = ref('')

// Modal state
const showUsersModal = ref(false)
const selectedTrek = ref(null)

const openTrekUsersModal = (trek) => {
  selectedTrek.value = trek
  showUsersModal.value = true
}

const loadData = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    const [treksData, usersData] = await Promise.all([
      api.get('/api/admin/treks'),
      api.get('/api/admin/users'),
    ])

    treks.value = treksData || []
    users.value = usersData || []
  } catch (err) {
    fetchError.value = err.message || 'Failed to load booking records.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// Summary metrics
const totalBookings = computed(() => {
  return treks.value.reduce((acc, t) => acc + (t.bookings_count || 0), 0)
})

const completedBookings = computed(() => {
  return treks.value.filter(t => t.status === 'Completed')
    .reduce((acc, t) => acc + (t.bookings_count || 0), 0)
})

const activeBookings = computed(() => {
  return treks.value.filter(t => t.status === 'Open' || t.status === 'Approved')
    .reduce((acc, t) => acc + (t.bookings_count || 0), 0)
})

const filteredTreksWithBookings = computed(() => {
  return treks.value.filter(t => {
    if (!searchQuery.value) return true
    const q = searchQuery.value.toLowerCase()
    return (
      t.id.toString().includes(q) ||
      t.trek_name.toLowerCase().includes(q) ||
      t.location.toLowerCase().includes(q)
    )
  })
})
</script>

<template>
  <div class="bookings-tab">
    <div v-if="fetchError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ fetchError }}
      <button type="button" class="btn-close" @click="fetchError = ''"></button>
    </div>

    <!-- Booking Summary Cards -->
    <div class="row g-3 mb-4">
      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm rounded-4 bg-white p-3 border-start border-warning border-4">
          <div class="d-flex align-items-center">
            <div class="rounded-circle bg-warning-subtle text-warning-emphasis p-3 me-3">
              <i class="bi bi-journal-bookmark-fill fs-3"></i>
            </div>
            <div>
              <span class="text-muted small fw-semibold text-uppercase">Total Trek Bookings</span>
              <h3 class="fw-bold mb-0 text-dark">{{ loading ? '-' : totalBookings }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm rounded-4 bg-white p-3 border-start border-success border-4">
          <div class="d-flex align-items-center">
            <div class="rounded-circle bg-success-subtle text-success p-3 me-3">
              <i class="bi bi-check-circle-fill fs-3"></i>
            </div>
            <div>
              <span class="text-muted small fw-semibold text-uppercase">Active Expeditions</span>
              <h3 class="fw-bold mb-0 text-dark">{{ loading ? '-' : activeBookings }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4">
        <div class="card border-0 shadow-sm rounded-4 bg-white p-3 border-start border-primary border-4">
          <div class="d-flex align-items-center">
            <div class="rounded-circle bg-primary-subtle text-primary p-3 me-3">
              <i class="bi bi-trophy-fill fs-3"></i>
            </div>
            <div>
              <span class="text-muted small fw-semibold text-uppercase">Completed Trek History</span>
              <h3 class="fw-bold mb-0 text-dark">{{ loading ? '-' : completedBookings }}</h3>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Card -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-center">
          <div class="col-12 col-md-8">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Search booking records by Trek Name, Location, or ID..."
              />
            </div>
          </div>

          <div class="col-12 col-md-4 text-md-end">
            <button class="btn btn-outline-secondary rounded-pill px-4" @click="loadData">
              <i class="bi bi-arrow-clockwise me-2"></i>Refresh Booking Log
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bookings & Trek History Table -->
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-ticket-perforated-fill me-2 text-warning"></i>Booking Records & Trek History Overview
        </h5>
        <span class="badge bg-light text-dark border rounded-pill px-3">
          Showing {{ filteredTreksWithBookings.length }} treks
        </span>
      </div>

      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">Trek Route</th>
                <th>Location</th>
                <th>Slots Available</th>
                <th>Assigned Guide</th>
                <th>Trek Lifecycle</th>
                <th class="pe-4 text-end">Active Bookings</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="6" class="text-center py-4">
                  <div class="spinner-border text-warning spinner-border-sm me-2"></div>
                  Loading booking records...
                </td>
              </tr>
              <tr v-else-if="filteredTreksWithBookings.length === 0">
                <td colspan="6" class="text-center py-4 text-muted">
                  No booking records found matching search parameters.
                </td>
              </tr>
              <tr v-for="trek in filteredTreksWithBookings" :key="trek.id">
                <td class="ps-4">
                  <div class="fw-bold text-dark">{{ trek.trek_name }}</div>
                  <small class="text-muted">ID: #{{ trek.id }} | Duration: {{ trek.duration }} days</small>
                </td>
                <td>
                  <i class="bi bi-geo-alt-fill text-danger me-1"></i>{{ trek.location }}
                </td>
                <td>
                  <span class="fw-bold">{{ trek.available_slots }}</span> slots left
                </td>
                <td>
                  <span v-if="trek.assigned_staff" class="badge bg-light text-dark border">
                    <i class="bi bi-person-fill text-primary me-1"></i>{{ trek.assigned_staff.name }}
                  </span>
                  <span v-else class="text-muted small">Unassigned</span>
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
                  <button
                    class="btn btn-sm btn-outline-warning text-dark rounded-pill px-3 py-1.5 fw-semibold fs-7 shadow-xs"
                    @click="openTrekUsersModal(trek)"
                    title="Click to view booked users roster"
                  >
                    <i class="bi bi-people-fill me-1.5 text-warning"></i>
                    {{ trek.bookings_count || 0 }} Booked &bull; View Users
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Admin Trek Users Roster Modal -->
    <AdminTrekUsersModal
      :show="showUsersModal"
      :trek="selectedTrek"
      @close="showUsersModal = false"
    />
  </div>
</template>

<style scoped>
.fs-7 {
  font-size: 0.85rem;
}
</style>
