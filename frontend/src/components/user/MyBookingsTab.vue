<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const bookings = ref([])
const loading = ref(true)
const actionError = ref('')
const successMessage = ref('')
const cancellingId = ref(null)

const fetchBookings = async () => {
  loading.value = true
  actionError.value = ''
  try {
    const res = await api.get('/api/user/bookings')
    bookings.value = res || []
  } catch (err) {
    actionError.value = err.message || 'Failed to fetch your bookings.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBookings()
})

const activeBookings = computed(() => {
  return bookings.value.filter(b => (b.status || '').toLowerCase() === 'booked')
})

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A'
  try {
    const utcDateStr = isoStr.endsWith('Z') || isoStr.includes('+') ? isoStr : `${isoStr}Z`
    return new Date(utcDateStr).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return isoStr
  }
}

const handleCancelBooking = async (booking) => {
  cancellingId.value = booking.id
  actionError.value = ''
  successMessage.value = ''
  try {
    await api.put(`/api/user/bookings/${booking.id}/cancel`)
    successMessage.value = `Booking #${booking.id} for "${booking.trek?.trek_name || 'Expedition'}" has been cancelled.`
    await fetchBookings()
  } catch (err) {
    actionError.value = err.message || 'Failed to cancel booking.'
  } finally {
    cancellingId.value = null
  }
}
</script>

<template>
  <div class="my-bookings-tab">
    <!-- Alerts -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <div v-if="actionError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ actionError }}
      <button type="button" class="btn-close" @click="actionError = ''"></button>
    </div>

    <!-- Active Bookings Header Card -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-journal-bookmark-fill me-2 text-emerald"></i>Active Booked Expeditions
        </h5>
        <span class="badge bg-light text-dark border rounded-pill px-3">
          Total Booked: {{ activeBookings.length }}
        </span>
      </div>

      <div class="card-body p-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-emerald" role="status">
            <span class="visually-hidden">Loading bookings...</span>
          </div>
          <p class="text-muted small mt-2">Loading active trek bookings...</p>
        </div>

        <div v-else-if="activeBookings.length === 0" class="text-center py-5 bg-light rounded-4 border border-dashed">
          <i class="bi bi-journal-x text-muted display-5 d-block mb-2"></i>
          <h6 class="fw-semibold text-secondary mb-1">No Active Trek Bookings</h6>
          <p class="text-muted small mb-0">You do not have any upcoming booked expeditions. Head to "Explore Treks" to book a trip!</p>
        </div>

        <div v-else class="row g-3">
          <div v-for="booking in activeBookings" :key="booking.id" class="col-12 col-lg-6">
            <div class="card border border-emerald-subtle shadow-xs rounded-4 p-3 bg-white h-100 d-flex flex-column justify-content-between">
              <div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="badge bg-emerald text-white rounded-pill px-2.5 py-1 fs-8">
                    <i class="bi bi-check-circle-fill me-1"></i>Booking #{{ booking.id }}
                  </span>
                  <span class="badge rounded-pill px-2.5 py-1 fs-8" :class="{
                    'bg-success text-white': booking.trek?.status === 'Open',
                    'bg-primary text-white': booking.trek?.status === 'Completed',
                    'bg-secondary text-white': booking.trek?.status === 'Closed',
                    'bg-info text-dark': booking.trek?.status === 'Approved'
                  }">
                    Trek: {{ booking.trek?.status || 'Active' }}
                  </span>
                </div>

                <h6 class="fw-bold text-dark fs-5 mb-1">
                  <i class="bi bi-mountain me-1.5 text-emerald"></i>{{ booking.trek?.trek_name || 'Trek Expedition' }}
                </h6>
                <div class="text-secondary small mb-3">
                  <i class="bi bi-geo-alt-fill me-1 text-danger opacity-75"></i>{{ booking.trek?.location || 'TBD' }}
                </div>

                <div class="row g-2 py-2 px-3 bg-light rounded-3 mb-3">
                  <div class="col-6">
                    <div class="text-muted fs-8">Start Date</div>
                    <div class="fw-semibold text-dark fs-7">
                      <i class="bi bi-calendar-event me-1 text-emerald"></i>{{ formatDate(booking.trek?.start_date) }}
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="text-muted fs-8">Duration</div>
                    <div class="fw-semibold text-dark fs-7">
                      <i class="bi bi-clock me-1 text-primary"></i>{{ booking.trek?.duration || '-' }} Days
                    </div>
                  </div>
                </div>

                <div class="small text-muted mb-3">
                  <i class="bi bi-calendar-plus me-1"></i>Booked On: {{ formatDate(booking.booking_date) }}
                </div>
              </div>

              <!-- Footer Cancel Action -->
              <div class="border-top pt-3 d-flex justify-content-end">
                <button
                  class="btn btn-outline-danger btn-sm rounded-pill px-3 fw-semibold fs-8"
                  :disabled="cancellingId === booking.id"
                  @click="handleCancelBooking(booking)"
                >
                  <span v-if="cancellingId === booking.id" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-x-circle me-1"></i>Cancel Booking
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-emerald {
  background-color: #10b981 !important;
}

.text-emerald {
  color: #10b981 !important;
}

.border-emerald-subtle {
  border-color: rgba(16, 185, 129, 0.25) !important;
}

.fs-7 {
  font-size: 0.85rem;
}

.fs-8 {
  font-size: 0.75rem;
}
</style>
