<script setup>
import { ref, watch } from 'vue'
import { api } from '@/services/api'

const props = defineProps({
  show: { type: Boolean, default: false },
  trek: { type: Object, default: null }
})

const emit = defineEmits(['close', 'updated'])

const slots = ref(0)
const isSubmitting = ref(false)
const errorMsg = ref('')

watch(
  () => props.trek,
  (newTrek) => {
    if (newTrek) {
      slots.value = newTrek.available_slots || 0
      errorMsg.value = ''
    }
  },
  { immediate: true }
)

const handleIncrement = () => {
  slots.value += 1
}

const handleDecrement = () => {
  if (slots.value > 0) {
    slots.value -= 1
  }
}

const handleSubmit = async () => {
  if (slots.value < 0) {
    errorMsg.value = 'Available slots cannot be negative.'
    return
  }

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    const res = await api.put(`/api/staff/treks/${props.trek.id}`, {
      available_slots: parseInt(slots.value, 10)
    })
    emit('updated', res.trek || { ...props.trek, available_slots: slots.value })
    emit('close')
  } catch (err) {
    errorMsg.value = err.message || 'Failed to update available slots.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
    <div class="modal-dialog modal-dialog-centered w-100 max-w-md p-3">
      <div class="modal-content bg-white border-0 shadow-lg rounded-4 overflow-hidden">
        <!-- Header -->
        <div class="modal-header bg-dark-slate text-white py-3 px-4">
          <h5 class="modal-title fs-6 fw-bold mb-0 d-flex align-items-center">
            <i class="bi bi-ticket-perforated me-2 text-emerald"></i>
            Update Trek Slots
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>

        <!-- Body -->
        <div class="modal-body p-4">
          <div v-if="trek" class="mb-3">
            <div class="text-secondary small fw-medium">Trek Name</div>
            <div class="fw-bold text-dark fs-6">{{ trek.trek_name }}</div>
            <div class="small text-muted"><i class="bi bi-geo-alt me-1"></i>{{ trek.location }}</div>
          </div>

          <div v-if="errorMsg" class="alert alert-danger py-2 px-3 small rounded-3 mb-3">
            <i class="bi bi-exclamation-triangle-fill me-1"></i>{{ errorMsg }}
          </div>

          <form @submit.prevent="handleSubmit">
            <label class="form-label small fw-semibold text-secondary">Available Slots Count</label>
            <div class="input-group input-group-lg mb-4">
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="slots <= 0 || isSubmitting"
                @click="handleDecrement"
              >
                <i class="bi bi-dash-lg"></i>
              </button>
              <input
                v-model.number="slots"
                type="number"
                min="0"
                class="form-control text-center fw-bold fs-5"
                placeholder="0"
                required
                :disabled="isSubmitting"
              />
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="isSubmitting"
                @click="handleIncrement"
              >
                <i class="bi bi-plus-lg"></i>
              </button>
            </div>

            <div class="d-flex justify-content-end gap-2">
              <button
                type="button"
                class="btn btn-light rounded-pill px-4"
                :disabled="isSubmitting"
                @click="$emit('close')"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="btn btn-emerald text-white rounded-pill px-4 fw-semibold shadow-sm"
                :disabled="isSubmitting"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
                Save Slots
              </button>
            </div>
          </form>
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

.max-w-md {
  max-width: 440px;
}

.bg-dark-slate {
  background-color: #0f172a;
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

.text-emerald {
  color: #10b981;
}
</style>
