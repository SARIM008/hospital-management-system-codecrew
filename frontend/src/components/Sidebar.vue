<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const role = computed(() => authStore.role)

const adminLinks = [
  { name: 'Dashboard', path: '/admin' },
  { name: 'Patients', path: '/admin/patients' },
  
  { name: 'Appointments', path: '/admin/appointments' },
  { name: 'Admissions', path: '/admin/admissions' },
  { name: 'SOP', path: '/admin/SOP' },
  { name: 'Register', path: '/admin/register' },
  { name: 'Billing', path: '/admin/billing' },
  { name: 'Inventory', path: '/admin/inventory' },
]

const staffLinks = [
  { name: 'Dashboard', path: '/staff' },
  { name: 'Patients', path: '/staff/patients' },
  { name: 'Billing', path: '/staff/billing' },
  { name: 'Inventory', path: '/staff/inventory' },
  { name: 'Appointments', path: '/staff/appointments' },
]

const patientLinks = [
  { name: 'Dashboard', path: '/patient' },
  { name: 'Appointments', path: '/patient/appointments' },
  { name: 'My Records', path: '/patient/records' },
]

const doctorLinks = [
  { name: 'Consultations', path: '/doctor' },
  { name: 'Admissions', path: '/doctor/admissions' },
]

const navLinks = computed(() => {
  if (role.value === 'admin') return adminLinks
  if (role.value === 'staff') return staffLinks
  if (role.value === 'patient') return patientLinks
  if (role.value === 'doctor') return doctorLinks
  return []
})

const navIcons = {
  'Dashboard': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>`,
  'Patients': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  'Billing': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`,
  'Inventory': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`,
  'Appointments': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  'Admissions': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
  'SOP': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
  'Register': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>`,
  'My Records': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
  'Consultations': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`,
}

const roleSectionLabel = computed(() => {
  if (role.value === 'admin') return 'Administration'
  if (role.value === 'staff') return 'Staff Portal'
  if (role.value === 'patient') return 'My Health'
  if (role.value === 'doctor') return 'Clinical'
  return 'Navigation'
})
</script>

<template>
  <aside class="sidebar">

    <!-- Logo / Brand -->
    <div class="sidebar-logo">
      <div class="logo-mark">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
      </div>
      <div class="logo-copy">
        <span class="logo-text">Ward<span class="logo-accent">Wizard</span></span>
        <span class="logo-sub">Command Center</span>
      </div>
    </div>

    <!-- Nav -->
    <nav class="sidebar-nav">
      <div class="nav-section-label">{{ roleSectionLabel }}</div>
      <ul>
        <li v-for="link in navLinks" :key="link.path">
          <router-link
            :to="link.path"
            class="nav-item"
            exact-active-class="active"
          >
            <span class="nav-icon" v-html="navIcons[link.name] || navIcons['Dashboard']"></span>
            {{ link.name }}
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <div class="sidebar-avatar">
        <div class="avatar-circle">{{ role ? role[0].toUpperCase() : 'U' }}</div>
        <div class="avatar-info">
          <div class="avatar-name">{{ role ? role.charAt(0).toUpperCase() + role.slice(1) : 'User' }}</div>
          <div class="avatar-role">
            <span class="role-dot"></span>
            {{ role ? role.toUpperCase() : '' }}
          </div>
        </div>
      </div>
    </div>

  </aside>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap');

/* ─── TOKENS ─────────────────────────────────────── */
.sidebar {
  --green:        #10b981;
  --green-light:  #d1fae5;
  --green-dark:   #065f46;
  --white:        #ffffff;
  --surface:      #f8fafc;
  --border:       #e8edf3;
  --text-1:       #0d1f2d;
  --text-2:       #475569;
  --text-3:       #94a3b8;
  font-family: 'Geist', -apple-system, sans-serif;
}

/* ─── SHELL ──────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-width, 220px);
  background: #f9f9f9;
  border-right: 0px solid var(--border);
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  z-index: 10;
  padding: 24px 16px;
}

/* ─── LOGO ───────────────────────────────────────── */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
  margin-bottom: 32px;
}

.logo-mark {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.3);
}

.logo-mark svg {
  width: 15px;
  height: 15px;
}

.logo-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.02em;
  line-height: 1;
}

.logo-accent {
  color: var(--green);
}

.logo-sub {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.07em;
}

/* ─── NAV ────────────────────────────────────────── */
.nav-section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-3);
  padding: 0 8px;
  margin-bottom: 8px;
}

.sidebar-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 10px;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 440;
  color: var(--text-2);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.nav-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: inherit;
}

.nav-icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.nav-item:hover {
  background: var(--surface);
  color: var(--text-1);
}

.nav-item.active {
  background: var(--green-light);
  color: var(--green-dark);
  font-weight: 600;
}

/* ─── FOOTER ─────────────────────────────────────── */
.sidebar-footer {
  margin-top: auto;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.sidebar-avatar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--green-light);
  color: var(--green-dark);
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.avatar-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
  line-height: 1;
}

.avatar-role {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.role-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--green);
  display: inline-block;
}
</style>