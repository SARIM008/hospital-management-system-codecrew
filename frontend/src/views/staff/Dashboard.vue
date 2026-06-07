<script setup>
const todayAppointments = [
  { id: 101, time: '09:00 AM', patient: 'Anil Gupta', type: 'OPD consult' },
  { id: 102, time: '10:00 AM', patient: 'Meera Rajput', type: 'OPD follow-up' },
  { id: 103, time: '11:30 AM', patient: 'Suresh Kumar', type: 'IPD rounds' },
]

const recentAlerts = [
  { type: 'critical', message: 'Syringes 5ml running empty in Ward A.' },
  { type: 'low', message: 'Ibuprofen stocks below 15% threshold.' }
]
</script>

<template>
  <div class="staff-dashboard">
    <div class="dashboard-header mb-4">
      <h1>Staff Dashboard</h1>
      <p>Quick Actions and Overview</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions grid mb-4 gap-4">
      <router-link to="/staff/patients" class="card action-card">
        <div class="icon-wrapper bg-primary-light text-primary">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
        </div>
        <h3 class="mt-2">Register Patient</h3>
        <p class="text-sm">New OPD or IPD Registration</p>
      </router-link>

      <router-link to="/staff/billing" class="card action-card">
        <div class="icon-wrapper bg-secondary-light text-secondary">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 class="mt-2">Generate Bill</h3>
        <p class="text-sm">Consultation or Pharmacy Billing</p>
      </router-link>

      <div class="card action-card search-card">
        <h3>Patient Lookup</h3>
        <div class="search-form flex mt-2">
          <input type="text" class="form-control" placeholder="Search by ID or Name..." />
          <button class="btn btn-primary" style="margin-left: 0.5rem">Go</button>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid grid gap-4">
      <!-- Appointments -->
      <div class="card col-span-2">
        <div class="flex justify-between items-center mb-4">
          <h2>Today's Appointments</h2>
          <router-link to="/staff/appointments" class="text-primary font-medium text-sm">View Calendar &rarr;</router-link>
        </div>
        
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Patient</th>
                <th>Type</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in todayAppointments" :key="appt.id">
                <td>{{ appt.time }}</td>
                <td class="font-medium">{{ appt.patient }}</td>
                <td>{{ appt.type }}</td>
                <td>
                  <button class="btn btn-outline btn-sm">Process</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Alerts Sidebar -->
      <div class="flex-col gap-4">
        <div class="card mb-4">
          <h2 class="text-danger">Stock Alerts</h2>
          <ul class="mt-4 alert-list">
            <li v-for="(alert, index) in recentAlerts" :key="index" class="alert-item">
              <span class="badge" :class="alert.type === 'critical' ? 'badge-danger' : 'badge-pending'">{{ alert.type.toUpperCase() }}</span>
              <p class="mt-1 text-sm text-main font-medium">{{ alert.message }}</p>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quick-actions {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary);
}

.search-card {
  cursor: default;
}

.search-card:hover {
  transform: none;
  border-color: var(--border-color);
  box-shadow: var(--shadow-sm);
}

.icon-wrapper {
  padding: 0.75rem;
  border-radius: var(--radius-lg);
  display: inline-flex;
}

.bg-primary-light { background-color: var(--primary-light); }
.text-primary { color: var(--primary); display: flex; align-items: center; }

.bg-secondary-light { background-color: #d1fae5; }
.text-secondary { color: var(--secondary); display: flex; align-items: center; }

h3 { margin-bottom: 0.25rem; font-size: 1.125rem; }
.text-sm { font-size: 0.875rem; }

.content-grid {
  grid-template-columns: 2fr 1fr;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
