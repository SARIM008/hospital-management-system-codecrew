<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'

const appointments = ref([])
const admissions = ref([])
const activeTab = ref('OPD') // 'OPD', 'IPD', 'LAB'

const loading = ref(false)
const error = ref(null)

// --- MODAL STATE ---
const showOpdModal = ref(false)
const showIpdModal = ref(false)
const isLoadingModal = ref(false)
const selectedOpdData = ref(null)
const selectedIpdData = ref(null)

const fetchRecords = async () => {
  loading.value = true
  error.value = null
  try {
    const [apptsRes, admsRes] = await Promise.all([
      api.get('/appointments'),
      api.get('/my/admissions') 
    ])
    appointments.value = apptsRes.data
    admissions.value = admsRes.data
  } catch (err) {
    console.error('Error fetching records:', err)
    error.value = 'Failed to load health records. Please try again later.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})

const statusStyle = (status) => {
  const s = status?.toLowerCase()
  if (s === 'completed' || s === 'discharged') return { backgroundColor: '#dcfce7', color: '#15803d' }
  if (s === 'scheduled' || s === 'admitted') return { backgroundColor: '#dbeafe', color: '#1d4ed8' }
  if (s === 'cancelled') return { backgroundColor: '#fee2e2', color: '#b91c1c' }
  return { backgroundColor: '#f3f4f6', color: '#374151' }
}

const filteredRecords = computed(() => {
  if (activeTab.value === 'OPD') {
    return appointments.value.filter(appt => appt.opd_visit).map(appt => ({
      id: `OPD-${appt.id}`,
      actualId: typeof appt.opd_visit === 'object' ? appt.opd_visit.id : appt.opd_visit,
      date: new Date(appt.appointment_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: appt.appointment_time,
      type: 'OPD Visit',
      doctor: appt.doctor_name,
      status: appt.status,
      notes: appt.opd_visit?.diagnosis || appt.opd_visit?.complaints,
      rawType: 'OPD'
    }))
  } else if (activeTab.value === 'IPD') {
    return admissions.value.map(adm => ({
      id: `IPD-${adm.id}`,
      actualId: adm.id,
      date: new Date(adm.admission_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      type: 'IPD Admission',
      doctor: 'Assigned Physician',
      status: adm.status,
      notes: adm.provisional_diagnosis,
      rawType: 'IPD'
    }))
  }
  return []
})

// --- MODAL TRIGGER LOGIC ---
const openRecordModal = async (rec) => {
  if (rec.rawType === 'OPD') {
    showOpdModal.value = true
    isLoadingModal.value = true
    try {
      const res = await api.get(`/opd_visits/${rec.actualId}`)
      selectedOpdData.value = res.data
    } catch (err) {
      console.error(err)
      alert('Failed to load OPD details')
      showOpdModal.value = false
    } finally {
      isLoadingModal.value = false
    }
  } else if (rec.rawType === 'IPD') {
    showIpdModal.value = true
    isLoadingModal.value = true
    try {
      const [admRes, vitalsRes, medsRes] = await Promise.all([
        api.get(`/admissions/${rec.actualId}`),
        api.get(`/admissions/${rec.actualId}/vitals/latest`).catch(() => ({ data: null })),
        api.get(`/admissions/${rec.actualId}/medications`).catch(() => ({ data: [] }))
      ])
      
      selectedIpdData.value = {
        details: admRes.data.admission,
        discharge: admRes.data.discharge_record,
        vitals: vitalsRes.data,
        medications: medsRes.data
      }
    } catch (err) {
      console.error(err)
      alert('Failed to load IPD details')
      showIpdModal.value = false
    } finally {
      isLoadingModal.value = false
    }
  }
}
</script>

<template>
  <div class="patient-records-container" style = "background:#ffffff; border-radius:30px;padding: 28px;">
    <div class="page-header">
      <h1>My Health Records</h1>
    </div>

    <div class="tabs-container">
      <button class="record-tab" :class="{'active': activeTab === 'OPD'}" @click="activeTab = 'OPD'">OPD Records</button>
      <button class="record-tab" :class="{'active': activeTab === 'IPD'}" @click="activeTab = 'IPD'">IPD Records</button>
    </div>

    <div v-if="loading" class="state-container">
      <div class="loading-spinner"></div>
      <p class="text-muted">Loading your records...</p>
    </div>
    
    <div v-else-if="error" class="error-alert">
      <span>{{ error }}</span>
      <button @click="fetchRecords" class="retry-btn">Retry</button>
    </div>

    <div v-else class="records-grid">
       <div v-if="filteredRecords.length === 0" class="empty-state">
         <p class="text-muted empty-text">No health records found for this category.</p>
         <button @click="fetchRecords" class="btn btn-primary btn-sm">Refresh</button>
       </div>
       
       <div v-for="rec in filteredRecords" :key="rec.id" 
            @click="openRecordModal(rec)"
            class="record-card card">
            
          <div class="record-icon">
             <svg v-if="rec.rawType === 'OPD'" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
             <svg v-else-if="rec.rawType === 'IPD'" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
          </div>
          
          <div class="record-details">
             <div class="record-header">
                <h3 class="record-title">{{ rec.type }} <span class="record-id">{{ rec.id }}</span></h3>
                <span class="record-date">{{ rec.date }}</span>
             </div>
             
             <div class="record-meta-list">
                <div class="record-meta-item">
                  <span class="meta-label">Consultant:</span> 
                  <span class="meta-value">{{ rec.doctor }}</span>
                </div>
                <div v-if="rec.rawType === 'OPD'" class="record-meta-item">
                  <span class="meta-label">Time:</span> 
                  <span class="meta-value">{{ rec.time }}</span>
                </div>
                <div class="record-meta-item">
                   <span class="meta-label">Status:</span>
                   <span class="status-badge" :style="statusStyle(rec.status)">{{ rec.status }}</span>
                </div>
             </div>
          </div>
       </div>
    </div>

    <div v-if="showOpdModal" class="modal-overlay" @click.self="showOpdModal = false">
      <div class="modal-content opd-modal">
        
        <div class="modal-header">
          <h2>OPD Consultation Summary</h2>
          <button @click="showOpdModal = false" class="close-modal-btn">&times;</button>
        </div>

        <div v-if="isLoadingModal" class="state-container text-muted">Retrieving records...</div>
        
        <div v-else-if="selectedOpdData" class="modal-body">
          
          <div class="modal-overview-grid">
            <div class="overview-item">
              <span class="overview-label">Date</span>
              <span class="overview-value">{{ selectedOpdData.visit_date }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">Time</span>
              <span class="overview-value">{{ selectedOpdData.time }}</span>
            </div>
            <div class="overview-item full-width">
              <span class="overview-label">Consulting Doctor</span>
              <span class="overview-value">{{ selectedOpdData.doctor_name }}</span>
            </div>
          </div>

          <div v-if="selectedOpdData.complaints" class="clinical-note-box">
             <h4 class="note-heading">Patient Complaints</h4>
             <p class="note-content">{{ selectedOpdData.complaints }}</p>
          </div>

          <div v-if="selectedOpdData.diagnosis" class="clinical-note-box highlight-primary">
             <h4 class="note-heading text-primary">Diagnosis</h4>
             <p class="note-content">{{ selectedOpdData.diagnosis }}</p>
          </div>

          <div v-if="selectedOpdData.doctor_notes" class="clinical-note-box bg-background">
             <h4 class="note-heading">Doctor's Notes</h4>
             <p class="note-content">{{ selectedOpdData.doctor_notes }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showIpdModal" class="modal-overlay" @click.self="showIpdModal = false">
      <div class="modal-content ipd-modal">
        
        <div class="modal-header sticky-header">
          <h2>IPD Admission Record</h2>
          <button @click="showIpdModal = false" class="close-modal-btn">&times;</button>
        </div>

        <div v-if="isLoadingModal" class="state-container text-muted">Retrieving hospital records...</div>
        
        <div v-else-if="selectedIpdData" class="modal-body">
          
          <div class="modal-overview-grid ipd-overview">
            <div class="overview-item">
              <span class="overview-label">Admitted</span>
              <span class="overview-value">{{ selectedIpdData.details.admission_date }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">Discharged</span>
              <span class="overview-value">{{ selectedIpdData.discharge ? selectedIpdData.discharge.discharge_date : 'Currently Admitted' }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">Status</span>
              <span class="status-badge status-mt" :style="statusStyle(selectedIpdData.details.status)">{{ selectedIpdData.details.status }}</span>
            </div>
            <div class="overview-item full-width top-border mt-half">
              <span class="overview-label">Diagnosis (At Admission)</span>
              <span class="overview-value">{{ selectedIpdData.details.provisional_diagnosis || 'Not specified' }}</span>
            </div>
          </div>

          <div v-if="selectedIpdData.discharge" class="clinical-note-box highlight-primary bg-primary-light">
             <h4 class="note-heading text-primary">Final Diagnosis & Discharge Summary</h4>
             <p class="note-content font-medium mb-half">{{ selectedIpdData.discharge.final_diagnosis }}</p>
             <p class="note-content">{{ selectedIpdData.discharge.treatment_summary }}</p>
          </div>

          <div v-if="selectedIpdData.vitals && !selectedIpdData.vitals.error" class="section-container">
            <h4 class="section-title">Latest Recorded Vitals</h4>
            
            <div class="vitals-grid">
              <div class="vitals-card">
                <div class="vital-label">BP</div>
                <div class="vital-value">{{ selectedIpdData.vitals.systolic_bp }}/{{ selectedIpdData.vitals.diastolic_bp }}</div>
              </div>
              <div class="vitals-card">
                <div class="vital-label">Pulse</div>
                <div class="vital-value">{{ selectedIpdData.vitals.pulse }}</div>
              </div>
              <div class="vitals-card">
                <div class="vital-label">SpO2</div>
                <div class="vital-value">{{ selectedIpdData.vitals.spo2 }}%</div>
              </div>
              <div class="vitals-card">
                <div class="vital-label">Temp (°C)</div>
                <div class="vital-value">{{ selectedIpdData.vitals.temperature }}</div>
              </div>
            </div>
          </div>

          <div v-if="selectedIpdData.medications && selectedIpdData.medications.length > 0" class="section-container">
            <h4 class="section-title">Administered Medications</h4>
            
            <ul class="medication-list">
              <li v-for="med in selectedIpdData.medications" :key="med.id" class="medication-item">
                <span class="med-name">{{ med.medicine_name }}</span>
                <span class="med-dosage">{{ med.dosage }} ({{ med.frequency }})</span>
              </li>
            </ul>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ==========================================================================
   GLOBAL LAYOUT & STATES
   ========================================================================== */
.patient-records-container {
  max-width: 80rem;
  margin-left: auto;
  margin-right: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.page-header h1 {
  margin: 0;
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  margin-top: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.record-tab {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  font-weight: 500;
  transition: color 0.2s;
  border-bottom: 2px solid transparent; 
  margin-bottom: -1px;
}

.record-tab:hover {
  color: var(--text-main);
}

.record-tab.active {
  color: var(--primary);
  border-bottom: 2px solid var(--primary);
}

/* States */
.state-container {
  text-align: center;
  padding: 2.5rem 0;
}

.loading-spinner {
  border: 4px solid var(--border-color);
  border-top-color: transparent;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  margin: 0 auto 0.5rem auto;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-alert {
  background-color: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  border: 1px solid #fecaca;
  display: flex;
  align-items: center;
}

.retry-btn {
  background: none;
  border: none;
  color: inherit;
  margin-left: 1rem;
  text-decoration: underline;
  font-weight: 500;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 3rem 0;
  background-color: var(--background);
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border-color);
}

.empty-text {
  margin-bottom: 1rem;
}

/* ==========================================================================
   RECORD CARDS (GRID VIEW)
   ========================================================================== */
.records-grid {
  display: grid;
  gap: 1rem;
}

.record-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  cursor: pointer;
  border: 1px solid var(--border-color);
  min-height:170px;
  border-radius: 18px;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.record-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.record-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  background-color: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-details {
  flex: 1;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.record-title {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--text-main);
  margin: 0;
}

.record-id {
  color: var(--text-muted);
  font-family: monospace;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.record-date {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.record-meta-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.record-meta-item {
  font-size: 0.875rem;
}

.meta-label {
  color: var(--text-muted);
  margin-right: 0.25rem;
  display: inline-block;
  margin-top: 5px;
}

.meta-value {
  font-weight: 500;
  color: var(--text-main);
}

.status-badge {
  padding: 0.2rem 0.65rem;
  align-self: flex-start;
  border-radius: 35px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

/* ==========================================================================
   MODALS
   ========================================================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 50;
  padding: 1rem;
}

.modal-content {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  
  /* TWEAK THIS: This is the internal padding of the entire modal */
  padding: 1.5rem; 
}

.opd-modal {
  max-width: 42rem;
}

.ipd-modal {
  max-width: 48rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.sticky-header {
  position: sticky;
  top: -1.5rem; /* Matches modal padding to snap to top */
  background-color: var(--surface);
  z-index: 10;
  padding-top: 1.5rem; /* Restores padding lost to sticky */
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.close-modal-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
}

.close-modal-btn:hover {
  color: var(--text-main);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Space between sections in modal */
}

/* Modal Overview Box */
.modal-overview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  
  /* TWEAK THESE: Padding and gaps for the top summary box */
  gap: 1rem;
  padding: 1.25rem;
  
  background-color: var(--background);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.ipd-overview {
  grid-template-columns: repeat(3, 1fr);
}

.overview-item {
  display: flex;
  flex-direction: column;
}

.full-width {
  grid-column: 1 / -1;
}

.overview-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  display: block;
}

.overview-value {
  font-weight: 500;
  color: var(--text-main);
}

/* Clinical Notes Boxes */
.clinical-note-box {
  border-left: 3px solid var(--border-color);
  
  /* TWEAK THIS: Pushes the text away from the left border */
  padding-left: 1rem; 
}

.clinical-note-box.bg-background {
  background-color: var(--background);
  padding: 1rem; /* Give it full padding if it has a background color */
  border-radius: var(--radius-md);
}

.clinical-note-box.highlight-primary {
  border-color: var(--primary);
}

.clinical-note-box.bg-primary-light {
  background-color: var(--primary-light);
  padding: 1rem;
  border-radius: var(--radius-md);
}

.note-heading {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}

.note-heading.text-primary {
  color: var(--primary);
}

.note-content {
  font-size: 0.875rem;
  color: var(--text-main);
  white-space: pre-wrap;
  margin: 0;
}

/* Section Grouping (Vitals & Meds) */
.section-container {
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 700;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-bottom: 0.75rem;
}

/* Vitals Grid */
.vitals-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem; /* Space between vital boxes */
  text-align: center;
}

.vitals-card {
  background-color: var(--background);
  
  /* TWEAK THESE: Padding and borders for vital boxes */
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.vital-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.vital-value {
  font-weight: 700;
  color: var(--text-main);
}

/* Medication List */
.medication-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* Space between medicines */
}

.medication-item {
  display: flex;
  justify-content: space-between;
  background-color: var(--background);
  
  /* TWEAK THESE: Padding and borders for medicine list */
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  font-size: 0.875rem;
}

.med-name {
  font-weight: 500;
  color: var(--text-main);
}

.med-dosage {
  color: var(--text-muted);
}

/* Utility Helpers for layout overrides */
.top-border { 
  border-top: 1px solid var(--border-color); 
  margin-top: 1rem;    /* Pushes the thin line down from the items above */
  padding-top: 1rem;   /* Pushes the text down from the line */
}
.mt-half { margin-top: 0.5rem; }
.mb-half { margin-bottom: 0.5rem; }
.pt-half { padding-top: 0.5rem; }
.status-mt { margin-top: 0.25rem; display: inline-block; }
.text-muted { color: var(--text-muted); }
.text-primary { color: var(--primary); }
.font-medium { font-weight: 500; }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 500; }
</style>