<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'

const appointments = ref([])
const activeTab = ref('upcoming')
const isRecording = ref(false)
const recordingAppointmentId = ref(null)
const isUploading = ref(false)
const transcriptionStatus = ref('')
const showTranscriptModal = ref(false)
const selectedTranscript = ref('')
const selectedSummary = ref(null)
const selectedPatientName = ref('')
const selectedAppointmentId = ref(null)
const isSummarizing = ref(false)
const showSummaryTab = ref(true)

// FIX: Declare these as standard variables, NOT Vue refs! 
// This prevents Vue from wrapping them in Proxies and breaking native events.
let mediaRecorder = null
let audioChunks = []

const fetchAppointments = async () => {
  try {
    const response = await api.get('/doctor/appointments')
    appointments.value = response.data
  } catch (error) {
    console.error('Error fetching appointments:', error)
  }
}

const upcomingAppointments = computed(() => {
  return appointments.value.filter(a => a.status === 'scheduled' || a.status === 'checked_in')
})

const completedAppointments = computed(() => {
  return appointments.value.filter(a => a.status === 'completed')
})

const startRecording = async (appointmentId) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    // Assign directly without .value
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      // Small safeguard to ensure we only push chunks that actually contain data
      if (event.data && event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      // Safely create the Blob from a standard JS array
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      await uploadRecording(appointmentId, audioBlob)
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.start()
    isRecording.value = true
    recordingAppointmentId.value = appointmentId
  } catch (error) {
    console.error('Error starting recording:', error)
    alert('Could not access microphone. Please ensure permissions are granted.')
  }
}

const stopRecording = () => {
  // Check the standard variable instead of mediaRecorder.value
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    recordingAppointmentId.value = null
  }
}

const uploadRecording = async (appointmentId, blob) => {
  isUploading.value = true
  transcriptionStatus.value = 'Transcribing consultation...'
  
  const formData = new FormData()
  formData.append('audio', blob, 'consultation.webm')

  try {
    const response = await api.post(`/doctor/appointments/${appointmentId}/record`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // Update appointment status in local list
    const index = appointments.value.findIndex(a => a.id === appointmentId)
    if (index !== -1) {
      appointments.value[index].status = 'completed'
    }
    
    alert('Consultation recorded and transcribed successfully!')
  } catch (error) {
    console.error('Error uploading recording:', error)
    alert('Failed to save consultation record.')
  } finally {
    isUploading.value = false
    transcriptionStatus.value = ''
  }
}

const viewTranscript = async (appointment) => {
  selectedPatientName.value = appointment.patient_name
  selectedAppointmentId.value = appointment.id
  selectedTranscript.value = 'Loading transcript...'
  selectedSummary.value = null
  showTranscriptModal.value = true
  
  try {
    const response = await api.get(`/doctor/appointments/${appointment.id}/transcript`)
    selectedTranscript.value = response.data.transcript || 'No transcript generated.'
    selectedSummary.value = response.data.summary || null
    
    if (!selectedSummary.value) {
      showSummaryTab.value = false
    } else {
      showSummaryTab.value = true
    }
    
    if (!selectedSummary.value) {
       try {
         const opdRes = await api.get('/opd/history', { params: { appointment_id: appointment.id } })
         if (opdRes.data && opdRes.data.length > 0) {
           selectedSummary.value = opdRes.data[0]
           showSummaryTab.value = true 
         }
       } catch (e) { console.log("No OPD visit found") }
    }
  } catch (error) {
    console.error('Error fetching transcript:', error)
    selectedTranscript.value = 'Error loading transcript. It might not have been generated yet.'
  }
}

const triggerReSummarize = async () => {
  if (!selectedAppointmentId.value) return
  
  isSummarizing.value = true
  try {
    const response = await api.post(`/doctor/appointments/${selectedAppointmentId.value}/summarize`)
    selectedSummary.value = response.data.opd_visit
    alert('AI summary updated successfully!')
  } catch (error) {
    console.error('Error re-summarizing:', error)
    alert('Failed to generate AI summary.')
  } finally {
    isSummarizing.value = false
  }
}

const closeTranscriptModal = () => {
  showTranscriptModal.value = false
  selectedTranscript.value = ''
  selectedSummary.value = null
  selectedAppointmentId.value = null
}

onMounted(() => {
  fetchAppointments()
})
</script>

<template>
  <div class="doctor-dashboard">
    <header class="dashboard-header mb-6">
      <div class="header-content">
        <h1>OPD Consultations</h1>
        <p class="text-muted">Manage your daily consultations and recordings</p>
      </div>
      <div class="header-actions">
        <button @click="fetchAppointments" class="btn btn-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
            <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
          </svg>
          Refresh
        </button>
      </div>
    </header>

    <!-- Stats Overview -->
    <div class="stats-grid mb-6">
      <div class="card stat-card">
        <div class="stat-icon bg-primary-light text-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
        <div class="stat-info">
          <h3>{{ upcomingAppointments.length }}</h3>
          <p>Upcoming</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon bg-success-light text-success">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        </div>
        <div class="stat-info">
          <h3>{{ completedAppointments.length }}</h3>
          <p>Completed</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-container mb-4">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'upcoming' }"
        @click="activeTab = 'upcoming'"
      >
        Upcoming Appointments
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'completed' }"
        @click="activeTab = 'completed'"
      >
        Recent Consultations
      </button>
    </div>

    <!-- Content -->
    <div class="card list-card">
      <div v-if="isUploading" class="upload-overlay">
        <div class="spinner"></div>
        <p>{{ transcriptionStatus }}</p>
      </div>

      <div v-if="activeTab === 'upcoming'">
        <div v-if="upcomingAppointments.length === 0" class="empty-state">
          <p>No upcoming appointments found.</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Patient Name</th>
                <th class="text-center">Status</th>
                <th class="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in upcomingAppointments" :key="appt.id">
                <td>
                  <div class="time-cell">
                    <span class="date">{{ appt.appointment_date }}</span>
                    <span class="time">{{ appt.appointment_time }}</span>
                  </div>
                </td>
                <td>
                  <div class="patient-cell">
                    <strong>{{ appt.patient_name }}</strong>
                    <span class="subtext">PID: #{{ appt.patient_id }}</span>
                  </div>
                </td>
                <td class="text-center">
                  <span :class="['badge', 'badge-' + appt.status]">
                    {{ appt.status.replace('_', ' ') }}
                  </span>
                </td>
                <td class="text-right">
                  <div v-if="isRecording && recordingAppointmentId === appt.id" class="recording-badge">
                    <span class="dot"></span>
                    Recording...
                    <button @click="stopRecording" class="btn btn-danger btn-sm ml-2">Stop</button>
                  </div>
                  <button 
                    v-else 
                    @click="startRecording(appt.id)" 
                    class="btn btn-primary btn-sm"
                    :disabled="isRecording"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
                    Record Consultation
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab === 'completed'">
        <div v-if="completedAppointments.length === 0" class="empty-state">
          <p>No completed consultations yet.</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Date/Time</th>
                <th>Patient Name</th>
                <th class="text-center">Status</th>
                <th class="text-right">History</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in completedAppointments" :key="appt.id">
                <td>{{ appt.appointment_date }} {{ appt.appointment_time }}</td>
                <td><strong>{{ appt.patient_name }}</strong></td>
                <td class="text-center"><span class="badge badge-success">Completed</span></td>
                <td class="text-right">
                  <button @click="viewTranscript(appt)" class="btn btn-outline btn-sm">View Transcript</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Transcript Modal -->
    <div v-if="showTranscriptModal" class="modal-overlay" @click.self="closeTranscriptModal">
      <div class="modal-content card">
        <div class="modal-header border-b mb-4">
          <h2>Transcription: {{ selectedPatientName }}</h2>
          <button @click="closeTranscriptModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="modal-tabs mb-4">
            <button class="modal-tab-btn" :class="{ active: !showSummaryTab }" @click="showSummaryTab = false">Raw Transcript</button>
            <button class="modal-tab-btn" :class="{ active: showSummaryTab }" @click="showSummaryTab = true">AI Summary</button>
          </div>

          <div v-if="!showSummaryTab" class="transcript-container">
            <p class="transcript-text">{{ selectedTranscript }}</p>
          </div>

          <div v-else class="summary-container">
            <div v-if="isSummarizing" class="loading-summary py-8 text-center">
              <div class="spinner mx-auto mb-2"></div>
              <p>Analyzing consultation...</p>
            </div>
            <div v-else-if="selectedSummary">
              <div class="summary-section mb-4">
                <h4 class="text-xs font-bold text-muted uppercase tracking-wider mb-1">Complaints</h4>
                <p class="text-main bg-background p-3 rounded">{{ selectedSummary.complaints || 'None listed' }}</p>
              </div>
              <div class="summary-section mb-4">
                <h4 class="text-xs font-bold text-muted uppercase tracking-wider mb-1">Diagnosis</h4>
                <p class="text-main bg-background p-3 rounded font-medium">{{ selectedSummary.diagnosis || 'Undiagnosed' }}</p>
              </div>
              <div class="summary-section mb-4">
                <h4 class="text-xs font-bold text-muted uppercase tracking-wider mb-1">Clinical Notes</h4>
                <p class="text-main bg-background p-3 rounded whitespace-pre-wrap">{{ selectedSummary.doctor_notes || 'No extra notes' }}</p>
              </div>
            </div>
            <div v-else class="empty-summary text-center py-8">
              <p class="text-muted mb-4">No AI summary available for this consultation.</p>
              <button @click="triggerReSummarize" class="btn btn-primary btn-sm">Generate AI Summary Now</button>
            </div>
          </div>
        </div>
        <div class="modal-footer mt-6 flex justify-between items-center">
          <button v-if="showSummaryTab && selectedSummary" @click="triggerReSummarize" class="btn btn-outline btn-sm" :disabled="isSummarizing">
            {{ isSummarizing ? 'Processing...' : 'Re-summarize' }}
          </button>
          <div v-else></div>
          <button @click="closeTranscriptModal" class="btn btn-primary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.doctor-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-main);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: var(--radius-lg);
  background-color: var(--surface);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
}

.stat-info h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.stat-info p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.tabs-container {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  margin-bottom: -1px;
}

.tab-btn:hover {
  color: var(--primary);
  border-color: var(--primary-light);
}

.tab-btn.active {
  color: var(--primary);
  border-color: var(--primary);
}

.list-card {
  min-height: 400px;
  position: relative;
}

.badge-scheduled { background-color: var(--primary-light); color: var(--primary-dark); }
.badge-checked_in { background-color: #fef3c7; color: #92400e; }
.badge-completed { background-color: #d1fae5; color: #065f46; }

.time-cell {
  display: flex;
  flex-direction: column;
}

.time-cell .date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.patient-cell {
  display: flex;
  flex-direction: column;
}

.patient-cell .subtext {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.recording-badge {
  display: inline-flex;
  align-items: center;
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  margin-right: 0.5rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.upload-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 5;
  border-radius: var(--radius-lg);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  color: var(--text-muted);
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.875rem;
}

.mr-1 { margin-right: 0.25rem; }
.mr-2 { margin-right: 0.5rem; }
.ml-2 { margin-left: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }
.text-right { text-align: right; }
.font-bold { font-weight: 700; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-content {
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  background-color: var(--surface);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-muted);
}

.transcript-text {
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--text-main);
}

.btn-outline {
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background-color: var(--primary-light);
  color: var(--primary-dark);
}

.header-actions button {
  cursor: pointer;
}

.modal-tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-tab-btn {
  flex: 1;
  padding: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.modal-tab-btn:not(.active):hover {
  color: var(--text-main);
  background-color: var(--background);
}

.summary-section h4 {
  font-size: 0.7rem;
}

.loading-summary .spinner {
  width: 30px;
  height: 30px;
}

.mx-auto { margin-left: auto; margin-right: auto; }
.py-8 { padding-top: 2rem; padding-bottom: 2rem; }
.uppercase { text-transform: uppercase; }
.tracking-wider { letter-spacing: 0.05em; }
.whitespace-pre-wrap { white-space: pre-wrap; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
</style>
