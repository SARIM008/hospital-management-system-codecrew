<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../services/api'

const authStore = useAuthStore()

const myAppointments = ref([])
const recentOpd = ref([])
const recentIpd = ref([])
const availableDoctors = ref([])
const loading = ref(true)

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const [apptsRes, admsRes, drsRes] = await Promise.all([
      api.get('/appointments'),
      api.get('/my/admissions'),
      api.get('/doctors')
    ])
    
    const allAppts = apptsRes.data || []
    const now = new Date()
    now.setHours(0,0,0,0)
    
    // Upcoming Appointments (Only Scheduled)
    myAppointments.value = allAppts
      .filter(a => a.status === 'scheduled' && new Date(a.appointment_date) >= now)
      .sort((a,b) => new Date(a.appointment_date + 'T' + a.appointment_time) - new Date(b.appointment_date + 'T' + b.appointment_time))
    
    // Recent OPD Visits (Completed Appointments)
    recentOpd.value = allAppts
      .filter(a => a.status === 'completed' || a.opd_visit)
      .sort((a,b) => new Date(b.appointment_date) - new Date(a.appointment_date))
      .slice(0, 3)
      
    // Recent IPD Visits
    recentIpd.value = (admsRes.data || [])
      .sort((a,b) => new Date(b.admission_date) - new Date(a.admission_date))
      .slice(0, 3)

    // Available Doctors
    availableDoctors.value = (drsRes.data || []).slice(0, 3)
      
  } catch (err) {
    console.error('Dashboard data error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<template>
  <div class="patient-dashboard-container">
    <!-- Clean Header -->
    <header class="page-intro">
      <div class="flex items-center gap-4">
        <div>
          <h1 class="text-3xl font-extrabold tracking-tight text-slate-900 leading-none mb-1">
            Hello, {{ authStore.user?.name ? authStore.user.name.split(' ')[0] : 'Patient' }}
          </h1>
          <p class="text-slate-500 font-medium">Welcome back to your healthcare portal.</p>
        </div>
      </div>
    </header>

    <div class="dashboard-content-grid">
      
      <!-- COLUMN 1: ACTIVE AGENDA -->
      <section class="dashboard-section">
       <!--  <div class="section-header">
           <div class="flex items-center gap-2">
             <div class="header-indicator bg-primary"></div>
             <h2 class="section-title">Active Agenda</h2>
           </div>
        </div> -->

        <div class="card glass-card">
           <div class="flex justify-between items-center">
              <h3 class="flex items-center gap-2 m-0 p-0">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                Upcoming Appointments
              </h3>
              <router-link to="/patient/appointments" class="book-link font-bold">+ New Booking</router-link>
           </div>

           <div v-if="loading" class="skeleton-loader py-10">
              <div class="spinner-sm mx-auto"></div>
           </div>

           <div v-else-if="myAppointments.length > 0" class="appt-stack">
              <div v-for="appt in myAppointments.slice(0, 3)" :key="appt.id" class="stack-item">
                 <div class="flex justify-between items-start">
                    <div class="flex-1 pr-4">
                       <h4 class="font-bold text-slate-800 m-0 text-base">{{ appt.doctor_name || 'Hospital Visit' }}</h4>
                       <p class="text-xs font-semibold text-primary uppercase tracking-wide mt-1">{{ appt.specialization || 'Consultation' }}</p>
                       
                       <div class="flex items-center gap-3 mt-2">
                          <div class="info-pill">
                             <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="12" height="12"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                             {{ formatDate(appt.appointment_date) }}
                          </div>
                          <div class="info-pill">
                             <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="12" height="12"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                             {{ appt.appointment_time }}
                          </div>
                       </div>
                    </div>
                    <div class="status-badge-container">
                       <span class="modern-badge" :class="appt.status">{{ appt.status }}</span>
                    </div>
                 </div>
              </div>
           </div>

           <div v-else class="empty-state">
              <p>No upcoming schedules.</p>
           </div>
        </div>
      </section>

      <!-- COLUMN 2: DOCTOR DIRECTORY -->
      <section class="dashboard-section">
        <!-- <div class="section-header">
           <div class="flex items-center gap-2">
             <div class="header-indicator bg-indigo-500"></div>
             <h2 class="section-title">Medical Directory</h2>
           </div>
        </div> -->

        <div class="card glass-card">
           <div class="flex justify-between items-center">
              <h3 class="flex items-center gap-2 m-0 p-0 border-0">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                Available Specialists
              </h3>
              <router-link to="/patient/appointments" class="text-sm font-bold text-slate-400 hover:text-indigo-500 transition-colors">View All</router-link>
           </div>

           <div class="dr-stack">
              <div v-if="availableDoctors.length > 0">
                 <div v-for="dr in availableDoctors" :key="dr.id" class="dr-item mb-2 last:mb-0">
                    <div class="dr-item-content">
                       
                       <div class="dr-info">
                          <h4 class="dr-name">{{ dr.name }}</h4>
                          <p class="dr-meta">{{ dr.specialization || 'General' }} • <span class="dr-status text-emerald-500">Active</span></p>
                       </div>
                    </div>
                    <router-link :to="'/patient/appointments?doctor=' + dr.id" class="dr-book-btn text-center no-underline">Book</router-link>
                 </div>
              </div>
              <div v-else class="empty-state">No specialists available currently.</div>
           </div>
        </div>
      </section>

      <!-- HISTORY SECTION: FULL WIDTH -->
      <section class="dashboard-section history-section full-span">
        <!-- <div class="section-header no-border mb-4">
           <div class="flex items-center gap-2">
             <div class="header-indicator bg-slate-800"></div>
             <h2 class="section-title">Patient Journal & Medical History</h2>
           </div>
        </div>-->

        <div class="history-grid-inner">
           <!-- OPD COLUMN -->
           <div class="card glass-card history-subcard">
              <div class="flex justify-between items-center">
                 <h3 class="flex items-center gap-2 m-0 p-0 border-0">
                   <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18" class="text-blue-500"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                   Recent OPD Visits
                 </h3>
                 <router-link to="/patient/records" class="book-link font-bold">View All</router-link>
              </div>

              <div v-if="recentOpd.length > 0" class="history-list">
                 <div v-for="opd in recentOpd" :key="opd.id" class="history-item">
                    <div class="history-marker"></div>
                    <div class="history-body">
                       <p class="history-subject">{{ opd.opd_visit?.diagnosis || opd.opd_visit?.complaints || 'Outpatient Consultation' }}</p>
                       <p class="history-footer">{{ formatDate(opd.appointment_date) }} • {{ opd.doctor_name }}</p>
                    </div>
                 </div>
              </div>
              <div v-else class="empty-state-history">No past OPD records.</div>
           </div>

           <!-- IPD COLUMN -->
           <div class="card glass-card history-subcard">
              <div class="flex justify-between items-center">
                 <h3 class="flex items-center gap-2 m-0 p-0 border-0">
                   <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18" class="text-purple-500"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                   Recent IPD Admissions
                 </h3>
                 <router-link to="/patient/records" class="book-link font-bold">View All</router-link>
              </div>

              <div v-if="recentIpd.length > 0" class="history-list">
                 <div v-for="ipd in recentIpd" :key="ipd.id" class="history-item border-l-purple-200">
                    <div class="history-marker bg-purple-500"></div>
                    <div class="history-body">
                       <template v-if="ipd.discharge_record">
                          <p class="history-subject line-clamp-1">{{ ipd.discharge_record.treatment_summary || 'Admission Recovery' }}</p>
                          <p class="history-footer">Discharged: {{ formatDate(ipd.discharge_record.discharge_date) }} • {{ ipd.discharge_record.medicine_days_prescribed || 0 }} Days Meds</p>
                       </template>
                       <template v-else>
                          <p class="history-subject">{{ ipd.provisional_diagnosis || 'In-Patient Care' }}</p>
                          <p class="history-footer">Admitted: {{ formatDate(ipd.admission_date) }} • <span class="font-bold text-primary">{{ ipd.status }}</span></p>
                       </template>
                    </div>
                 </div>
              </div>
              <div v-else class="empty-state-history">No past IPD records.</div>
           </div>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
/* Page Layout */
.patient-dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 1.7rem;
  border-radius: 30px;
  background-color: #ffffff;
  min-height: 100vh;
}

.dashboard-content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2.5rem;
}

.full-span {
  grid-column: span 2;
}

/* User Avatar */
.user-avatar-lg {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary), #4f46e5);
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
}

/* Sections */
.dashboard-section {
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
  padding-bottom: 0.5rem;
}

.header-indicator {
  width: 4px;
  height: 18px;
  border-radius: 10px;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

/* Cards */
.glass-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 1.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
  height: 100%;
}

.card-subtitle {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.75rem;
}

.subtitle-wrapper {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.75rem;
}

/* Stack Items (Upcoming Appts) */
.stack-item {
  padding: 1.25rem;
  background: #ffffff;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  margin-bottom: 1rem;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.stack-item:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.03);
}

.info-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  background: #f8fafc;
  padding: 0.15rem 0.75rem;
  border-radius: 8px;
}

/* Badges */
.modern-badge {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  padding: 0.35rem 0.75rem;
  border-radius: 99px;
}
.modern-badge.scheduled { background: #eff6ff; color: #1d4ed8; }
.modern-badge.confirmed { background: #ecfdf5; color: #059669; }

/* Doctor List */
.dr-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}
.dr-item:hover { border-color: #e2e8f0; }

.dr-item-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dr-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.875rem;
}

.dr-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.dr-meta {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
  margin-top: 2px;
}

.dr-book-btn {
  background: white;
  border: 2px solid #e2e8f0;
  color: #1e293b;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.dr-book-btn:hover {
  background: #1e293b;
  color: white;
  border-color: #1e293b;
}

/* History Styles */
.history-grid-inner {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

.history-item {
  position: relative;
  padding-left: 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 2px solid #e2e8f0;
}
.history-item:last-child { margin-bottom: 0.5rem; }

.history-marker {
  position: absolute;
  left: -5px;
  top: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--primary);
  border: 2px solid white;
}

.history-subject {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.history-footer {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
}

/* Utils */
.mb-10 { margin-bottom: 2.5rem; }
.mb-8 { margin-bottom: 2rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mt-4 { margin-top: 1rem; }
.text-primary { color: var(--primary); }
.spinner-sm { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state, .empty-state-history {
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  font-style: italic;
}

.book-link {
  font-size: 0.875rem;
  color: var(--primary);
  text-decoration: none;
  transition: opacity 0.2s;
}
.book-link:hover { opacity: 0.8; }

</style>
