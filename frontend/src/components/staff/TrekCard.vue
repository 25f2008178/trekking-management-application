<script setup>
import { computed } from 'vue'

const props = defineProps({
  trek: { type: Object, required: true }
})

const emit = defineEmits([
  'edit-slots',
  'view-participants',
  'update-status',
  'mark-completed'
])

const difficultyBadgeClass = computed(() => {
  const diff = (props.trek.difficulty || '').toLowerCase()
  if (diff === 'easy') return 'bg-emerald-subtle text-emerald border border-emerald'
  if (diff === 'moderate') return 'bg-warning-subtle text-warning-emphasis border border-warning'
  if (diff === 'hard') return 'bg-danger-subtle text-danger border border-danger'
  return 'bg-secondary-subtle text-secondary border border-secondary'
})

const statusBadgeClass = computed(() => {
  const status = (props.trek.status || '').toLowerCase()
  if (status === 'open') return 'bg-success text-white'
  if (status === 'closed') return 'bg-secondary text-white'
  if (status === 'completed') return 'bg-primary text-white'
  if (status === 'approved') return 'bg-info text-dark'
  return 'bg-warning text-dark'
})

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
</script>

<template>
  <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden hover-card transition-all">
    <!-- Card Top Header -->
    <div class="card-header bg-dark-slate text-white p-3 d-flex align-items-center justify-content-between">
      <div class="d-flex align-items-center gap-2">
        <span class="badge rounded-pill px-2.5 py-1.5 fs-8" :class="difficultyBadgeClass">
          <i class="bi bi-bar-chart-fill me-1"></i>{{ trek.difficulty }}
        </span>
        <span class="badge rounded-pill px-2.5 py-1.5 fs-8" :class="statusBadgeClass">
          {{ trek.status }}
        </span>
      </div>
      <span class="badge bg-white-10 text-white-50 fs-8 rounded-pill px-2.5 py-1">
        <i class="bi bi-shield-check me-1 text-emerald"></i>Assigned Guide
      </span>
    </div>

    <!-- Card Body -->
    <div class="card-body p-4 d-flex flex-column justify-content-between">
      <div>
        <!-- Trek Title & Location -->
        <h5 class="fw-bold text-dark mb-1 fs-5 card-title d-flex align-items-center">
          <i class="bi bi-mountain me-2 text-emerald"></i>
          {{ trek.trek_name }}
        </h5>
        <div class="text-secondary small mb-3">
          <i class="bi bi-geo-alt-fill me-1 text-danger opacity-75"></i>{{ trek.location }}
        </div>

        <!-- Details Grid -->
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

        <!-- Metrics Row: Available Slots & Registered Trekkers -->
        <div class="row g-2 mb-3">
          <!-- Slots Box -->
          <div class="col-6">
            <div class="p-3 border rounded-3 bg-white text-center h-100 d-flex flex-column justify-content-between">
              <div class="text-muted fs-8 fw-medium">Available Slots</div>
              <div class="fw-bold text-dark fs-4 my-1">
                {{ trek.available_slots }}
              </div>
              <button
                type="button"
                class="btn btn-sm btn-outline-emerald rounded-pill py-1 px-2 fs-8 w-100"
                @click="$emit('edit-slots', trek)"
              >
                <i class="bi bi-pencil-square me-1"></i>Edit Slots
              </button>
            </div>
          </div>

          <!-- Trekkers Box -->
          <div class="col-6">
            <div class="p-3 border rounded-3 bg-white text-center h-100 d-flex flex-column justify-content-between">
              <div class="text-muted fs-8 fw-medium">Registered Trekkers</div>
              <div class="fw-bold text-emerald fs-4 my-1">
                {{ trek.bookings_count || 0 }}
              </div>
              <button
                type="button"
                class="btn btn-sm btn-emerald text-white rounded-pill py-1 px-2 fs-8 w-100 shadow-xs"
                @click="$emit('view-participants', trek)"
              >
                <i class="bi bi-people-fill me-1"></i>View Roster
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Action Toolbar -->
      <div class="border-top pt-3 mt-2 d-flex flex-wrap gap-2 justify-content-between align-items-center">
        <!-- Status Dropdown Quick Toggle -->
        <div class="dropdown">
          <button
            class="btn btn-sm btn-light border dropdown-toggle rounded-pill px-3 fs-8 fw-semibold"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
            :disabled="trek.status === 'Completed'"
          >
            <i class="bi bi-toggle-on me-1 text-emerald"></i>Status: {{ trek.status }}
          </button>
          <ul class="dropdown-menu shadow-sm border-0 rounded-3 fs-8">
            <li>
              <button
                class="dropdown-item d-flex align-items-center py-2"
                :class="{ active: trek.status === 'Open' }"
                @click="$emit('update-status', trek, 'Open')"
              >
                <span class="badge bg-success me-2">&nbsp;</span>Set as Open
              </button>
            </li>
            <li>
              <button
                class="dropdown-item d-flex align-items-center py-2"
                :class="{ active: trek.status === 'Closed' }"
                @click="$emit('update-status', trek, 'Closed')"
              >
                <span class="badge bg-secondary me-2">&nbsp;</span>Set as Closed
              </button>
            </li>
          </ul>
        </div>

        <!-- Mark Completed Action -->
        <button
          v-if="trek.status !== 'Completed'"
          type="button"
          class="btn btn-sm btn-outline-primary rounded-pill px-3 fs-8 fw-semibold"
          @click="$emit('mark-completed', trek)"
        >
          <i class="bi bi-check2-circle me-1"></i>Mark Completed
        </button>
        <span v-else class="badge bg-primary-subtle text-primary border border-primary px-3 py-1.5 rounded-pill fs-8">
          <i class="bi bi-check-all me-1"></i>Trek Completed
        </span>
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

.btn-outline-emerald {
  color: #10b981;
  border-color: #10b981;
}

.btn-outline-emerald:hover {
  background-color: #10b981;
  color: #fff;
}

.bg-white-10 {
  background-color: rgba(255, 255, 255, 0.1);
}

.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04) !important;
}

.fs-7 {
  font-size: 0.85rem;
}

.fs-8 {
  font-size: 0.75rem;
}
</style>
