<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import AppLogo from '@/components/common/AppLogo.vue'
import ExploreTreksTab from '@/components/user/ExploreTreksTab.vue'
import MyBookingsTab from '@/components/user/MyBookingsTab.vue'
import TrekHistoryTab from '@/components/user/TrekHistoryTab.vue'
import UserProfileTab from '@/components/user/UserProfileTab.vue'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('explore')

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
  <div class="user-dashboard min-vh-100 bg-light">
    <!-- Top Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark-slate shadow-sm sticky-top">
      <div class="container-fluid px-4">
        <a class="navbar-brand d-flex align-items-center text-decoration-none" href="#">
          <AppLogo size="sm" badge-text="Trekker" />
        </a>

        <div class="d-flex align-items-center ms-auto">
          <!-- Trekker Profile Pill -->
          <div class="d-flex align-items-center text-white me-3 bg-white-10 px-3 py-1.5 rounded-pill">
            <i class="bi bi-person-circle fs-5 me-2 text-emerald"></i>
            <div>
              <div class="fw-semibold lh-1 fs-7">{{ authStore.userName }}</div>
              <small class="text-white-50 fs-8">Trekker Account</small>
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
                :class="{ 'active bg-emerald text-white': activeTab === 'explore' }"
                @click="activeTab = 'explore'"
              >
                <i class="bi bi-compass me-2"></i>Explore Treks
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'bookings' }"
                @click="activeTab = 'bookings'"
              >
                <i class="bi bi-journal-check me-2"></i>My Bookings
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'history' }"
                @click="activeTab = 'history'"
              >
                <i class="bi bi-clock-history me-2"></i>Trekking History
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-3 fw-semibold transition-all py-2.5"
                :class="{ 'active bg-emerald text-white': activeTab === 'profile' }"
                @click="activeTab = 'profile'"
              >
                <i class="bi bi-person-gear me-2"></i>My Profile
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- Tab Dynamic Content -->
      <transition name="fade" mode="out-in">
        <ExploreTreksTab v-if="activeTab === 'explore'" key="explore" />
        <MyBookingsTab v-else-if="activeTab === 'bookings'" key="bookings" />
        <TrekHistoryTab v-else-if="activeTab === 'history'" key="history" />
        <UserProfileTab v-else-if="activeTab === 'profile'" key="profile" />
      </transition>
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

.text-emerald {
  color: #10b981 !important;
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
