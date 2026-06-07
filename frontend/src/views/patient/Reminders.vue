<script setup>
import { ref } from 'vue'

const medicineReminders = ref([
  { id: 1, name: 'Ibuprofen 400mg', time: '09:00 AM', instruction: 'After breakfast', taken: true },
  { id: 2, name: 'Calcimax D3', time: '02:00 PM', instruction: 'After lunch', taken: false },
  { id: 3, name: 'Pain Relief Spray', time: 'As needed', instruction: 'Every 6 hours', taken: false },
  { id: 4, name: 'Ibuprofen 400mg', time: '09:00 PM', instruction: 'Before bed', taken: false },
])

const appointmentReminders = ref([
  { id: 101, type: 'Follow-up', doctor: 'Dr. Sharma', date: 'Mar 22, 2026', time: '11:30 AM', location: 'Orthopedics Dept, Floor 3' },
])

const labReminders = ref([
  { id: 201, test: 'X-Ray (Right Knee)', date: 'Mar 20, 2026', time: '10:00 AM', status: 'Scheduled' },
])

const toggleTaken = (id) => {
  const med = medicineReminders.value.find(m => m.id === id)
  if (med) med.taken = !med.taken
}
</script>

<template>
  <div class="patient-reminders max-w-7xl mx-auto">
    <div class="header mb-6">
      <h1>My Reminders</h1>
      <p class="text-muted">Stay on track with your medications and appointments.</p>
    </div>

    <div class="grid lg-grid-cols-3 gap-6">
      <!-- Medications Section -->
      <div class="lg-col-span-2">
        <div class="card h-full">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl m-0">Daily Medication Schedule</h2>
            <span class="text-sm text-primary font-medium">Today, 19 Mar</span>
          </div>

          <div class="med-list flex flex-col gap-3">
            <div v-for="med in medicineReminders" :key="med.id" 
              class="med-item p-4 border rounded border-color flex items-center justify-between"
              :class="{ 'taken': med.taken }">
              <div class="flex items-center gap-4">
                <div class="time-slot font-bold text-primary-dark w-20">{{ med.time }}</div>
                <div>
                  <h3 class="font-bold text-main m-0">{{ med.name }}</h3>
                  <p class="text-sm text-muted m-0">{{ med.instruction }}</p>
                </div>
              </div>
              <button 
                class="btn btn-sm" 
                :class="med.taken ? 'btn-success' : 'btn-outline border-primary text-primary'"
                @click="toggleTaken(med.id)">
                {{ med.taken ? 'Taken ✓' : 'Mark as Taken' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments & Labs Section -->
      <div class="flex flex-col gap-6">
        <!-- Next Appointment -->
        <div class="card border-primary bg-primary-light">
          <h2 class="text-lg mb-3 text-primary-dark">Next Appointment</h2>
          <div v-for="appt in appointmentReminders" :key="appt.id">
            <div class="flex justify-between items-start mb-2">
              <span class="badge badge-info">{{ appt.type }}</span>
              <span class="text-sm font-bold text-primary">{{ appt.date }}</span>
            </div>
            <h3 class="m-0 text-main">{{ appt.doctor }}</h3>
            <p class="text-sm text-muted mb-3">{{ appt.location }}</p>
            <div class="flex items-center gap-2 text-sm font-medium text-main">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              {{ appt.time }}
            </div>
          </div>
        </div>

        <!-- Pending Labs -->
        <div class="card">
          <h2 class="text-lg mb-3">Pending Lab Tests</h2>
          <div v-for="lab in labReminders" :key="lab.id" class="p-3 bg-background border border-color rounded mb-2">
            <div class="flex justify-between items-center">
              <h3 class="text-sm font-bold m-0 text-main">{{ lab.test }}</h3>
              <span class="text-xs font-mono text-muted">{{ lab.status }}</span>
            </div>
            <p class="text-xs text-muted mt-1">{{ lab.date }} at {{ lab.time }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-7xl { max-width: 80rem; }
.grid { display: grid; }
.gap-6 { gap: 1.5rem; }
.gap-4 { gap: 1rem; }
.gap-3 { gap: 0.75rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mt-1 { margin-top: 0.25rem; }
.m-0 { margin: 0; }
.p-4 { padding: 1rem; }
.p-3 { padding: 0.75rem; }
.w-20 { width: 5rem; }
.h-full { height: 100%; }

.lg-grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.lg-col-span-2 { grid-column: span 2 / span 2; }

.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.justify-between { justify-content: space-between; }

.text-muted { color: var(--text-muted); }
.text-primary { color: var(--primary); }
.text-primary-dark { color: var(--primary-dark); }
.text-main { color: var(--text-main); }
.text-sm { font-size: 0.875rem; }
.text-xs { font-size: 0.75rem; }
.text-xl { font-size: 1.25rem; }
.text-lg { font-size: 1.125rem; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.font-mono { font-family: monospace; }

.border { border: 1px solid var(--border-color); }
.border-color { border-color: var(--border-color); }
.border-primary { border-color: var(--primary); }
.rounded { border-radius: var(--radius-md); }
.bg-primary-light { background-color: var(--primary-light); }
.bg-background { background-color: var(--background); }

.med-item { transition: all 0.2s; }
.med-item.taken { background-color: var(--background); border-color: #dcfce7; opacity: 0.8; }
.btn-success { background-color: #10a37f; color: white; border: none; }
.btn-success:hover { background-color: #0d8063; }

@media (max-width: 1024px) {
  .lg-grid-cols-3 { grid-template-columns: 1fr; }
  .lg-col-span-2 { grid-column: auto; }
}
</style>
