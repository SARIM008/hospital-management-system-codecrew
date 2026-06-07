<script setup>
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Sidebar from '../components/Sidebar.vue'
import Navbar from '../components/Navbar.vue'

const authStore = useAuthStore()
const role = computed(() => authStore.role)
</script>

<template>
  <div class="main-layout">
    <Sidebar v-if="role !== 'doctor'" />
    <div class="content-wrapper" :class="{ 'no-sidebar': role === 'doctor' }">
      <Navbar />
      <main class="page-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--background);
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

.content-wrapper.no-sidebar {
  margin-left: 0;
}

.page-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .content-wrapper {
    margin-left: 0;
  }
}
</style>

