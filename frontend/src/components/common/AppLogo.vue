<script setup>
defineProps({
  size: { type: String, default: 'md' }, // 'sm', 'md', 'lg'
  showText: { type: Boolean, default: true },
  badgeText: { type: String, default: '' },
  textColor: { type: String, default: 'text-white' }
})
</script>

<template>
  <div class="app-logo d-inline-flex align-items-center">
    <!-- Mountain Emblem Badge -->
    <div class="app-logo-badge rounded-3 d-flex align-items-center justify-content-center me-2.5" :class="`size-${size}`">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="mountain-svg">
        <!-- Back Mountain Peak -->
        <path d="M13 18L17.5 11L22 18H13Z" fill="#A7F3D0" opacity="0.9"/>
        <!-- Main Front Mountain Peak -->
        <path d="M2 18L10 6L18 18H2Z" fill="#FFFFFF"/>
        <!-- Mountain Snow Cap -->
        <path d="M10 6L12.2 9.3L10 10.5L7.8 9.3L10 6Z" fill="#047857"/>
        <!-- Golden Sun -->
        <circle cx="18.5" cy="6.5" r="2.5" fill="#F59E0B"/>
      </svg>
    </div>

    <!-- App Title Text & Sub-Badge -->
    <div v-if="showText" class="d-flex align-items-center">
      <span class="fw-bold tracking-tight" :class="textColor" :style="{ fontSize: size === 'lg' ? '1.25rem' : '1.1rem' }">
        Trekking Management App
      </span>
      <span v-if="badgeText" class="badge bg-emerald ms-2 fs-7 px-2.5 py-1 rounded-pill">
        {{ badgeText }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.app-logo-badge {
  background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.app-logo-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.45);
}

.size-sm {
  width: 32px;
  height: 32px;
  padding: 5px;
}

.size-md {
  width: 40px;
  height: 40px;
  padding: 6px;
}

.size-lg {
  width: 52px;
  height: 52px;
  padding: 8px;
}

.mountain-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.15));
}

.bg-emerald {
  background-color: #10b981 !important;
}

.fs-7 {
  font-size: 0.775rem;
}
</style>
