<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)
const role = computed(() => authStore.role)

const doctorLinks = [
  { name: 'Consultations', path: '/doctor' },
  { name: 'Admissions', path: '/doctor/admissions' },
]

const handleLogout = () => {
  authStore.logout()
}
</script>

<template>
  <header class="navbar">
    <div class="navbar-left">
      <h2 class="text-xl font-bold text-primary m-0" style="margin: 0;"></h2>
    </div>

    <nav v-if="role === 'doctor'" class="navbar-center doctor-nav">
      <router-link 
        v-for="link in doctorLinks" 
        :key="link.path" 
        :to="link.path"
        class="nav-link"
        exact-active-class="active"
      >
        {{ link.name }}
      </router-link>
    </nav>
    
    <div class="navbar-right">
      <div class="user-profile">
        <div class="avatar">
          {{ user?.name?.charAt(0) || 'U' }}
        </div>
        <div class="user-info">
          <span class="user-name">{{ user?.name || 'User' }}</span>
        </div>
      </div>
      
      <button @click="handleLogout" class="btn btn-outline btn-logout">
        Logout
      </button>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  height: var(--navbar-height);
  background-color: #f9f9f9;
  border-bottom: 0px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 5;
 
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9375rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

.nav-link:hover {
  background-color: var(--primary-light);
  color: var(--primary);
}

.nav-link.active {
  color: var(--primary);
  background-color: var(--primary-light);
  font-weight: 600;
}

.navbar-left {
  flex: 1;
}

.navbar-center {
  flex: 0 0 auto; /* don't grow/shrink, sit at natural size */
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.navbar-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end; /* push content to the right */
  gap: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 36px;
  height: 36px;
  background-color: var(--primary-light);
  color: var(--primary-dark);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--text-main);
}

.btn-logout {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .navbar-center {
    display: none;
  }
}
</style>

