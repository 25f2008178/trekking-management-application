<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import OverviewTab from '@/components/admin/OverviewTab.vue'
import TreksTab from '@/components/admin/TreksTab.vue'
import StaffTab from '@/components/admin/StaffTab.vue'
import UsersTab from '@/components/admin/UsersTab.vue'
import BookingsTab from '@/components/admin/BookingsTab.vue'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('overview')

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchProfile()
  }
})
</script>

<template>
  <div class="admin-dashboard min-vh-100 bg-light">
    <!-- Top Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark-slate shadow-sm sticky-top">
      <div class="container-fluid px-4">
        <a class="navbar-brand d-flex align-items-center fw-bold" href="#">
          <div class="brand-badge me-2 rounded-circle d-flex align-items-center justify-content-center">
            <i class="bi bi-mountain-half text-white fs-5"></i>
          </div>
          <span class="tracking-tight text-white">Trekking Management App <span class="badge bg-emerald ms-1 fs-7">Admin</span></span>
        </a>

        <div class="d-flex align-items-center ms-auto">
          <!-- Admin User Badge -->
          <div class="d-flex align-items-center text-white me-3 bg-white-10 px-3 py-1.5 rounded-pill">
            <i class="bi bi-person-circle fs-5 me-2 text-emerald"></i>
            <div>
              <div class="fw-semibold lh-1 fs-7">{{ authStore.userName }}</div>
              <small class="text-white-50 fs-8">Administrator</small>
            </div>
          </div>

          <!-- Sign Out Button -->
          <button class="btn btn-outline-light btn-sm rounded-pill px-3" @click="handleLogout">
            <i class="bi bi-box-arrow-right me-1"></i>Sign Out
          </button>
        </div>
      </div>
    </nav>

    <div class="container-fluid px-4 py-4">
      <!-- Dashboard Navigation Tabs -->
      <div class="card border-0 shadow-sm rounded-4 mb-4">
        <div class="card-body p-2">
          <ul class="nav nav-pills nav-fill gap-2">
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'overview' }"
                @click="activeTab = 'overview'"
              >
                <i class="bi bi-speedometer2 me-2"></i>Overview & Stats
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'treks' }"
                @click="activeTab = 'treks'"
              >
                <i class="bi bi-map me-2"></i>Trek Routes
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'staff' }"
                @click="activeTab = 'staff'"
              >
                <i class="bi bi-person-workspace me-2"></i>Staff Guides
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'users' }"
                @click="activeTab = 'users'"
              >
                <i class="bi bi-people me-2"></i>Users Directory
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'bookings' }"
                @click="activeTab = 'bookings'"
              >
                <i class="bi bi-journal-bookmark me-2"></i>Bookings & History
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- Tab Dynamic Content -->
      <transition name="fade" mode="out-in">
        <OverviewTab v-if="activeTab === 'overview'" key="overview" />
        <TreksTab v-else-if="activeTab === 'treks'" key="treks" />
        <StaffTab v-else-if="activeTab === 'staff'" key="staff" />
        <UsersTab v-else-if="activeTab === 'users'" key="users" />
        <BookingsTab v-else-if="activeTab === 'bookings'" key="bookings" />
      </transition>
    </div>
  </div>
</template>

<style scoped>
.bg-dark-slate {
  background-color: #0f172a;
}

.brand-badge {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.bg-emerald {
  background-color: #10b981 !important;
}

.text-emerald {
  color: #10b981;
}

.bg-white-10 {
  background: rgba(255, 255, 255, 0.08);
}

.fs-7 {
  font-size: 0.85rem;
}

.fs-8 {
  font-size: 0.725rem;
}

.transition-all {
  transition: all 0.2s ease-in-out;
}

.nav-link {
  color: #64748b;
}

.nav-link:hover:not(.active) {
  background-color: #f1f5f9;
  color: #0f172a;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
