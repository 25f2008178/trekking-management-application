<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const loading = ref(true)
const treks = ref([])
const users = ref([])
const staff = ref([])
const bookings = ref([])
const fetchError = ref('')

const loadData = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    const [treksData, usersData, staffData] = await Promise.all([
      api.get('/api/admin/treks'),
      api.get('/api/admin/users'),
      api.get('/api/admin/staff'),
    ])

    treks.value = treksData || []
    users.value = usersData || []
    staff.value = staffData || []

    // Calculate total bookings from treks and users
    let totalBookingsList = []
    treks.value.forEach(t => {
      if (t.bookings_count) {
        // Collect trek booking info if present
      }
    })
    bookings.value = totalBookingsList
  } catch (err) {
    fetchError.value = err.message || 'Failed to load dashboard metrics'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// Metrics
const totalTreks = computed(() => treks.value.length)
const totalUsers = computed(() => users.value.filter(u => u.roles?.includes('user')).length)
const totalStaff = computed(() => staff.value.length)
const totalBookingsCount = computed(() => {
  return treks.value.reduce((acc, t) => acc + (t.bookings_count || 0), 0)
})

// Statistics calculations
const activeTreksCount = computed(() => treks.value.filter(t => t.status === 'Open' || t.status === 'Approved').length)
const completedTreksCount = computed(() => treks.value.filter(t => t.status === 'Completed').length)

const slotsStats = computed(() => {
  const totalSlots = treks.value.reduce((sum, t) => sum + (t.available_slots || 0), 0)
  return { totalSlots }
})

const difficultyBreakdown = computed(() => {
  const counts = { Easy: 0, Moderate: 0, Hard: 0 }
  treks.value.forEach(t => {
    if (counts[t.difficulty] !== undefined) {
      counts[t.difficulty]++
    }
  })
  return counts
})

const statusBreakdown = computed(() => {
  const counts = { Pending: 0, Approved: 0, Open: 0, Closed: 0, Completed: 0 }
  treks.value.forEach(t => {
    if (counts[t.status] !== undefined) {
      counts[t.status]++
    }
  })
  return counts
})

const activeUsersCount = computed(() => users.value.filter(u => u.active).length)
const inactiveUsersCount = computed(() => users.value.filter(u => !u.active).length)

const activeStaffCount = computed(() => staff.value.filter(s => s.status === 'Active' && s.active).length)
</script>

<template>
  <div class="overview-tab">
    <div v-if="fetchError" class="alert alert-danger d-flex align-items-center mb-4 shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
      <div>{{ fetchError }}</div>
      <button class="btn btn-outline-danger btn-sm ms-auto" @click="loadData">Retry</button>
    </div>

    <!-- Quick Stats Cards Row -->
    <div class="row g-3 mb-4">
      <div class="col-12 col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 metric-card bg-gradient-emerald text-white h-100">
          <div class="card-body p-3 d-flex align-items-center justify-content-between">
            <div>
              <span class="text-white-50 small fw-semibold text-uppercase tracking-wider">Total Treks</span>
              <h2 class="display-6 fw-bold mb-0 mt-1">{{ loading ? '-' : totalTreks }}</h2>
              <span class="badge bg-white text-emerald rounded-pill mt-2">
                <i class="bi bi-check-circle-fill me-1"></i>{{ activeTreksCount }} Active / Open
              </span>
            </div>
            <div class="metric-icon rounded-circle bg-white-20 p-3">
              <i class="bi bi-compass-fill fs-1"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 metric-card bg-gradient-blue text-white h-100">
          <div class="card-body p-3 d-flex align-items-center justify-content-between">
            <div>
              <span class="text-white-50 small fw-semibold text-uppercase tracking-wider">Total Users</span>
              <h2 class="display-6 fw-bold mb-0 mt-1">{{ loading ? '-' : totalUsers }}</h2>
              <span class="badge bg-white text-primary rounded-pill mt-2">
                <i class="bi bi-person-check-fill me-1"></i>{{ activeUsersCount }} Active Accounts
              </span>
            </div>
            <div class="metric-icon rounded-circle bg-white-20 p-3">
              <i class="bi bi-people-fill fs-1"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 metric-card bg-gradient-purple text-white h-100">
          <div class="card-body p-3 d-flex align-items-center justify-content-between">
            <div>
              <span class="text-white-50 small fw-semibold text-uppercase tracking-wider">Total Staff</span>
              <h2 class="display-6 fw-bold mb-0 mt-1">{{ loading ? '-' : totalStaff }}</h2>
              <span class="badge bg-white text-purple rounded-pill mt-2">
                <i class="bi bi-person-badge-fill me-1"></i>{{ activeStaffCount }} Active Guides
              </span>
            </div>
            <div class="metric-icon rounded-circle bg-white-20 p-3">
              <i class="bi bi-person-workspace fs-1"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 metric-card bg-gradient-amber text-white h-100">
          <div class="card-body p-3 d-flex align-items-center justify-content-between">
            <div>
              <span class="text-white-50 small fw-semibold text-uppercase tracking-wider">Total Bookings</span>
              <h2 class="display-6 fw-bold mb-0 mt-1">{{ loading ? '-' : totalBookingsCount }}</h2>
              <span class="badge bg-white text-warning rounded-pill mt-2">
                <i class="bi bi-ticket-detailed-fill me-1"></i>{{ slotsStats.totalSlots }} Open Slots
              </span>
            </div>
            <div class="metric-icon rounded-circle bg-white-20 p-3">
              <i class="bi bi-journal-bookmark-fill fs-1"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports and Statistics Charts/Breakdown section -->
    <div class="row g-4 mb-4">
      <!-- Trek Route Difficulty Distribution -->
      <div class="col-12 col-lg-6">
        <div class="card border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
            <h5 class="fw-bold mb-0 text-dark">
              <i class="bi bi-bar-chart-line-fill text-emerald me-2"></i>Trek Difficulty Breakdown
            </h5>
            <span class="badge bg-light text-secondary rounded-pill px-3 py-2">Total Routes: {{ totalTreks }}</span>
          </div>
          <div class="card-body px-4 pb-4">
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-semibold text-secondary"><i class="bi bi-circle-fill text-success me-2 fs-7"></i>Easy</span>
                <span class="fw-bold">{{ difficultyBreakdown.Easy }} routes</span>
              </div>
              <div class="progress rounded-pill style-progress" style="height: 10px;">
                <div
                  class="progress-bar bg-success rounded-pill"
                  role="progressbar"
                  :style="{ width: totalTreks ? (difficultyBreakdown.Easy / totalTreks * 100) + '%' : '0%' }"
                ></div>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-semibold text-secondary"><i class="bi bi-circle-fill text-warning me-2 fs-7"></i>Moderate</span>
                <span class="fw-bold">{{ difficultyBreakdown.Moderate }} routes</span>
              </div>
              <div class="progress rounded-pill style-progress" style="height: 10px;">
                <div
                  class="progress-bar bg-warning rounded-pill"
                  role="progressbar"
                  :style="{ width: totalTreks ? (difficultyBreakdown.Moderate / totalTreks * 100) + '%' : '0%' }"
                ></div>
              </div>
            </div>

            <div class="mb-2">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-semibold text-secondary"><i class="bi bi-circle-fill text-danger me-2 fs-7"></i>Hard</span>
                <span class="fw-bold">{{ difficultyBreakdown.Hard }} routes</span>
              </div>
              <div class="progress rounded-pill style-progress" style="height: 10px;">
                <div
                  class="progress-bar bg-danger rounded-pill"
                  role="progressbar"
                  :style="{ width: totalTreks ? (difficultyBreakdown.Hard / totalTreks * 100) + '%' : '0%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Trek Route Status Distribution -->
      <div class="col-12 col-lg-6">
        <div class="card border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
            <h5 class="fw-bold mb-0 text-dark">
              <i class="bi bi-pie-chart-fill text-primary me-2"></i>Trek Lifecycle Status
            </h5>
            <span class="badge bg-light text-secondary rounded-pill px-3 py-2">Updated Live</span>
          </div>
          <div class="card-body px-4 pb-4">
            <div class="row text-center g-2 mb-3">
              <div class="col">
                <div class="p-3 bg-light rounded-3">
                  <span class="text-secondary small d-block">Pending</span>
                  <span class="fs-4 fw-bold text-secondary">{{ statusBreakdown.Pending }}</span>
                </div>
              </div>
              <div class="col">
                <div class="p-3 bg-info-subtle rounded-3 text-info-emphasis">
                  <span class="small d-block">Approved</span>
                  <span class="fs-4 fw-bold">{{ statusBreakdown.Approved }}</span>
                </div>
              </div>
              <div class="col">
                <div class="p-3 bg-success-subtle rounded-3 text-success-emphasis">
                  <span class="small d-block">Open</span>
                  <span class="fs-4 fw-bold">{{ statusBreakdown.Open }}</span>
                </div>
              </div>
              <div class="col">
                <div class="p-3 bg-danger-subtle rounded-3 text-danger-emphasis">
                  <span class="small d-block">Closed</span>
                  <span class="fs-4 fw-bold">{{ statusBreakdown.Closed }}</span>
                </div>
              </div>
              <div class="col">
                <div class="p-3 bg-primary-subtle rounded-3 text-primary-emphasis">
                  <span class="small d-block">Completed</span>
                  <span class="fs-4 fw-bold">{{ statusBreakdown.Completed }}</span>
                </div>
              </div>
            </div>

            <div class="d-flex align-items-center justify-content-between p-3 bg-light rounded-3 mt-3">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-emerald text-white p-2 me-3">
                  <i class="bi bi-flag-fill fs-5"></i>
                </div>
                <div>
                  <h6 class="mb-0 fw-bold">Completed Expeditions</h6>
                  <small class="text-muted">Successfully organized treks</small>
                </div>
              </div>
              <h4 class="mb-0 fw-bold text-emerald">{{ completedTreksCount }}</h4>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Trek Summary Table -->
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-card-checklist me-2 text-purple"></i>System Overview & Trek Routes Snapshot
        </h5>
        <button class="btn btn-sm btn-light border rounded-pill px-3" @click="loadData">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">Trek Name & ID</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Slots</th>
                <th>Assigned Guide</th>
                <th>Status</th>
                <th class="pe-4 text-end">Total Bookings</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4">
                  <div class="spinner-border text-primary spinner-border-sm me-2"></div>
                  Loading metrics data...
                </td>
              </tr>
              <tr v-else-if="treks.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">No trekking routes found.</td>
              </tr>
              <tr v-for="trek in treks.slice(0, 5)" :key="trek.id">
                <td class="ps-4">
                  <div class="fw-bold text-dark">{{ trek.trek_name }}</div>
                  <small class="text-muted">ID: #{{ trek.id }}</small>
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
                <td>
                  <span class="fw-semibold">{{ trek.available_slots }}</span> slots
                </td>
                <td>
                  <span v-if="trek.assigned_staff" class="badge bg-light text-dark border">
                    <i class="bi bi-person-fill text-primary me-1"></i>{{ trek.assigned_staff.name }}
                  </span>
                  <span v-else class="badge bg-light text-muted border border-dashed">Unassigned</span>
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
                <td class="pe-4 text-end fw-bold text-dark">
                  {{ trek.bookings_count || 0 }}
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
.bg-gradient-emerald {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.bg-gradient-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.bg-gradient-purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
}

.bg-gradient-amber {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.bg-white-20 {
  background: rgba(255, 255, 255, 0.2);
}

.text-emerald {
  color: #10b981;
}

.text-purple {
  color: #8b5cf6;
}

.tracking-wider {
  letter-spacing: 0.05em;
}

.metric-card {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15) !important;
}

.fs-7 {
  font-size: 0.75rem;
}

.border-dashed {
  border-style: dashed !important;
}
</style>
