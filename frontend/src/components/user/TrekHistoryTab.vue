<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const bookings = ref([])
const loading = ref(true)
const fetchError = ref('')
const exporting = ref(false)
const exportError = ref('')
const exportSuccess = ref('')

const fetchHistory = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    const res = await api.get('/api/user/bookings')
    bookings.value = res || []
  } catch (err) {
    fetchError.value = err.message || 'Failed to fetch trek history.'
  } finally {
    loading.value = false
  }
}

const handleExportCSV = async () => {
  exporting.value = true
  exportError.value = ''
  exportSuccess.value = ''
  try {
    const startRes = await api.post('/api/user/export')
    const taskId = startRes.task_id

    if (!taskId) {
      throw new Error('Export task could not be initiated.')
    }

    let attempts = 0
    const maxAttempts = 30

    while (attempts < maxAttempts) {
      await new Promise(r => setTimeout(r, 1000))
      attempts++

      const statusRes = await api.get(`/api/user/export/${taskId}`)
      if (statusRes.status === 'SUCCESS') {
        const downloadUrl = `/api/user/export/${taskId}/download`
        const response = await fetch(downloadUrl, { credentials: 'include' })
        if (!response.ok) {
          throw new Error('Failed to download exported CSV file.')
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = statusRes.result?.filename || 'trekking_history.csv'
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)

        exportSuccess.value = 'Trekking history CSV downloaded successfully! An email copy has also been dispatched.'
        break
      } else if (statusRes.status === 'FAILURE') {
        throw new Error(statusRes.error || 'Export task failed on server.')
      }
    }

    if (attempts >= maxAttempts) {
      throw new Error('Export task timed out. Please try again.')
    }
  } catch (err) {
    exportError.value = err.message || 'Failed to export trekking history.'
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  fetchHistory()
})

const historyBookings = computed(() => {
  return bookings.value.filter(b => {
    const status = (b.status || '').toLowerCase()
    const trekStatus = (b.trek?.status || '').toLowerCase()
    return status === 'completed' || status === 'cancelled' || trekStatus === 'completed'
  })
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

const getStatusBadge = (status) => {
  const s = (status || '').toLowerCase()
  if (s === 'cancelled') return 'bg-secondary text-white'
  if (s === 'completed') return 'bg-primary text-white'
  return 'bg-info text-dark'
}
</script>

<template>
  <div class="trek-history-tab">
    <div v-if="exportSuccess" class="alert alert-success alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ exportSuccess }}
      <button type="button" class="btn-close" @click="exportSuccess = ''"></button>
    </div>

    <div v-if="exportError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ exportError }}
      <button type="button" class="btn-close" @click="exportError = ''"></button>
    </div>

    <div v-if="fetchError" class="alert alert-danger alert-dismissible fade show border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ fetchError }}
      <button type="button" class="btn-close" @click="fetchError = ''"></button>
    </div>

    <!-- History Header Card -->
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-transparent border-0 pt-4 px-4 d-flex align-items-center justify-content-between flex-wrap gap-2">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-clock-history me-2 text-primary"></i>Trekking History & Past Records
        </h5>
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-light text-dark border rounded-pill px-3 py-2">
            Total History Records: {{ historyBookings.length }}
          </span>
          <button
            class="btn btn-outline-success btn-sm rounded-pill px-3 fw-semibold d-inline-flex align-items-center"
            :disabled="exporting"
            @click="handleExportCSV"
          >
            <span v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <i v-else class="bi bi-file-earmark-arrow-down me-1.5 fs-6"></i>
            {{ exporting ? 'Exporting CSV...' : 'Export History (CSV)' }}
          </button>
        </div>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary spinner-border-sm me-2"></div>
          <span class="text-muted small">Loading history records...</span>
        </div>

        <div v-else-if="historyBookings.length === 0" class="text-center py-5 text-muted">
          <i class="bi bi-folder2-open display-5 d-block mb-2 text-secondary opacity-50"></i>
          <h6 class="fw-semibold text-secondary mb-1">No Past Trek History</h6>
          <p class="text-muted small mb-0">Completed expeditions and past booking records will appear here once finished.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">Booking ID</th>
                <th>Expedition Name</th>
                <th>Location</th>
                <th>Duration</th>
                <th>Booking Date</th>
                <th class="pe-4 text-end">Expedition Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in historyBookings" :key="record.id">
                <td class="ps-4 fw-bold text-muted">#{{ record.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ record.trek?.trek_name || 'Expedition' }}</div>
                  <small class="text-muted"><i class="bi bi-bar-chart me-1"></i>{{ record.trek?.difficulty || 'N/A' }}</small>
                </td>
                <td>{{ record.trek?.location || 'N/A' }}</td>
                <td>{{ record.trek?.duration || '-' }} Days</td>
                <td class="text-muted small">{{ formatDate(record.booking_date) }}</td>
                <td class="pe-4 text-end">
                  <span class="badge rounded-pill px-3 py-1.5 fs-8" :class="getStatusBadge(record.status)">
                    {{ record.status }}
                  </span>
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
.fs-8 {
  font-size: 0.75rem;
}
</style>
