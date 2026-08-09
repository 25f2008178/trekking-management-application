<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const treks = ref([])
const myBookings = ref([])
const loading = ref(true)
const bookingInProgress = ref({})
const actionError = ref('')
const successMessage = ref('')

// Search and Filters
const searchQuery = ref('')
const difficultyFilter = ref('')
const locationFilter = ref('')
const durationFilter = ref('') // 'all', 'short' (1-3), 'medium' (4-7), 'long' (8+)

const loadData = async () => {
  loading.value = true
  actionError.value = ''
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (difficultyFilter.value) params.difficulty = difficultyFilter.value
    if (locationFilter.value) params.location = locationFilter.value

    if (durationFilter.value === 'short') {
      params.min_duration = 1
      params.max_duration = 3
    } else if (durationFilter.value === 'medium') {
      params.min_duration = 4
      params.max_duration = 7
    } else if (durationFilter.value === 'long') {
      params.min_duration = 8
    }

    const [treksRes, bookingsRes] = await Promise.all([
      api.get('/api/user/treks', params),
      api.get('/api/user/bookings').catch(() => [])
    ])

    treks.value = treksRes || []
    myBookings.value = bookingsRes || []
  } catch (err) {
    actionError.value = err.message || 'Failed to load available treks.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const userBookedTrekIds = computed(() => {
  return myBookings.value
    .filter(b => (b.status || '').toLowerCase() === 'booked')
    .map(b => b.trek_id || b.trek?.id)
})

const isBooked = (trekId) => {
  return userBookedTrekIds.value.includes(trekId)
}

const formatDate = (isoStr) => {
  if (!isoStr) return 'TBD'
  try {
    return new Date(isoStr).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return isoStr
  }
}

const getDifficultyBadgeClass = (diff) => {
  const d = (diff || '').toLowerCase()
  if (d === 'easy') return 'bg-emerald-subtle text-emerald border border-emerald'
  if (d === 'moderate') return 'bg-warning-subtle text-warning-emphasis border border-warning'
  if (d === 'hard') return 'bg-danger-subtle text-danger border border-danger'
  return 'bg-secondary-subtle text-secondary border border-secondary'
}

const handleBookTrek = async (trek) => {
  if (isBooked(trek.id)) {
    actionError.value = 'You already have an active booking for this trek.'
    return
  }

  if (trek.available_slots <= 0) {
    actionError.value = 'Sorry, there are no available slots left for this trek.'
    return
  }

  bookingInProgress.value[trek.id] = true
  actionError.value = ''
  successMessage.value = ''

  try {
    const res = await api.post('/api/user/bookings', { trek_id: trek.id })
    successMessage.value = `Successfully booked expedition for "${trek.trek_name}"!`
    await loadData()
  } catch (err) {
    actionError.value = err.message || 'Failed to book trek. Please try again.'
  } finally {
    bookingInProgress.value[trek.id] = false
  }
}
</script>

<template>
  <div class="explore-treks-tab">
    <!-- Alerts -->
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
          <!-- Search Bar -->
          <div class="col-12 col-md-5">
            <label class="form-label small fw-semibold text-secondary mb-1">Search Expedition</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Search by trek name or location..."
                @input="loadData"
              />
            </div>
          </div>

          <!-- Difficulty Filter -->
          <div class="col-6 col-md-2.5">
            <label class="form-label small fw-semibold text-secondary mb-1">Difficulty Level</label>
            <select v-model="difficultyFilter" class="form-select bg-light" @change="loadData">
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Moderate">Moderate</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <!-- Duration Filter -->
          <div class="col-6 col-md-2.5">
            <label class="form-label small fw-semibold text-secondary mb-1">Trek Duration</label>
            <select v-model="durationFilter" class="form-select bg-light" @change="loadData">
              <option value="">Any Duration</option>
              <option value="short">Short (1 - 3 Days)</option>
              <option value="medium">Medium (4 - 7 Days)</option>
              <option value="long">Long (8+ Days)</option>
            </select>
          </div>

          <!-- Clear Filters Button -->
          <div class="col-12 col-md-2 d-flex align-items-end pt-3 pt-md-0">
            <button
              class="btn btn-outline-secondary w-100 rounded-3 btn-sm py-2"
              @click="searchQuery = ''; difficultyFilter = ''; locationFilter = ''; durationFilter = ''; loadData()"
            >
              <i class="bi bi-x-circle me-1"></i>Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Treks Grid -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-emerald" role="status">
        <span class="visually-hidden">Loading expeditions...</span>
      </div>
      <p class="text-muted small mt-2">Discovering available trek routes...</p>
    </div>

    <div v-else-if="treks.length === 0" class="card border-0 shadow-sm rounded-4 text-center p-5">
      <i class="bi bi-compass text-muted display-4 mb-3"></i>
      <h5 class="fw-bold text-dark mb-1">No Expeditions Found</h5>
      <p class="text-muted small mb-0">Try clearing or adjusting your search filters to view open trek routes.</p>
    </div>

    <div v-else class="row g-4">
      <div v-for="trek in treks" :key="trek.id" class="col-12 col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden trek-card transition-all">
          <!-- Card Header -->
          <div class="card-header bg-dark-slate text-white p-3 d-flex align-items-center justify-content-between">
            <span class="badge rounded-pill px-2.5 py-1.5 fs-8" :class="getDifficultyBadgeClass(trek.difficulty)">
              <i class="bi bi-bar-chart-fill me-1"></i>{{ trek.difficulty }}
            </span>
            <span
              class="badge rounded-pill px-2.5 py-1.5 fs-8"
              :class="trek.available_slots > 0 ? 'bg-success text-white' : 'bg-danger text-white'"
            >
              <i :class="trek.available_slots > 0 ? 'bi bi-ticket-perforated me-1' : 'bi bi-slash-circle me-1'"></i>
              {{ trek.available_slots > 0 ? `${trek.available_slots} Slots Left` : 'Fully Booked' }}
            </span>
          </div>

          <!-- Card Body -->
          <div class="card-body p-4 d-flex flex-column justify-content-between">
            <div>
              <h5 class="fw-bold text-dark mb-1 fs-5 d-flex align-items-center">
                <i class="bi bi-mountain me-2 text-emerald"></i>
                {{ trek.trek_name }}
              </h5>
              <div class="text-secondary small mb-3">
                <i class="bi bi-geo-alt-fill me-1 text-danger opacity-75"></i>{{ trek.location }}
              </div>

              <!-- Specs Row -->
              <div class="row g-2 mb-3 py-2 px-3 bg-light rounded-3">
                <div class="col-6">
                  <div class="text-muted fs-8">Duration</div>
                  <div class="fw-semibold text-dark fs-7">
                    <i class="bi bi-clock me-1 text-primary"></i>{{ trek.duration }} Days
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-muted fs-8">Start Date</div>
                  <div class="fw-semibold text-dark fs-7">
                    <i class="bi bi-calendar-event me-1 text-emerald"></i>{{ formatDate(trek.start_date) }}
                  </div>
                </div>
              </div>

              <!-- End Date & Guide -->
              <div class="d-flex justify-content-between align-items-center small text-muted mb-3">
                <span><i class="bi bi-calendar-check me-1"></i>End: {{ formatDate(trek.end_date) }}</span>
                <span v-if="trek.assigned_staff"><i class="bi bi-person-badge me-1"></i>Guide: {{ trek.assigned_staff.name }}</span>
              </div>
            </div>

            <!-- Booking Button Action -->
            <div class="border-top pt-3 mt-2">
              <button
                v-if="!isBooked(trek.id)"
                class="btn btn-emerald text-white w-100 rounded-pill py-2 fw-semibold shadow-sm"
                :disabled="trek.available_slots <= 0 || bookingInProgress[trek.id]"
                @click="handleBookTrek(trek)"
              >
                <span v-if="bookingInProgress[trek.id]" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-journal-check me-1.5"></i>
                {{ trek.available_slots > 0 ? 'Book This Expedition' : 'Fully Booked' }}
              </button>

              <button v-else class="btn btn-success-subtle text-success border border-success w-100 rounded-pill py-2 fw-semibold" disabled>
                <i class="bi bi-check-circle-fill me-1.5"></i>Already Booked
              </button>
            </div>
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

.bg-emerald-subtle {
  background-color: rgba(16, 185, 129, 0.12) !important;
}

.text-emerald {
  color: #10b981 !important;
}

.border-emerald {
  border-color: rgba(16, 185, 129, 0.3) !important;
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

.btn-success-subtle {
  background-color: rgba(16, 185, 129, 0.1);
}

.trek-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.trek-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08) !important;
}

.fs-7 {
  font-size: 0.85rem;
}

.fs-8 {
  font-size: 0.75rem;
}
</style>
