<template>
  <div class="admin-appointments" style = "background:#ffffff; border-radius:30px;padding: 20px; ">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1>Appointments & Schedule</h1>
        <p class="text-sm text-muted">Manage today's walk-ins, schedule limits, and doctor availability.</p>
      </div>
      <button class="btn btn-primary" @click="showModal = true">+ Create Appointment</button>
    </div>

    <div class="grid grid-cols-3 gap-8">
      
      <div class="col-span-2 flex flex-col gap-8">
        
        <div class="card p-0">
          <div class="p-4 border-b border-color flex justify-between items-center bg-surface">
            <h2 class="text-lg">Doctor Roster</h2>
            <div class="flex gap-4">
              <input type="date" v-model="rosterDate" class="form-control text-sm" style="width: auto; margin: 0;">
              <select v-model="rosterDoctor" class="form-control text-sm" style="width: auto; margin: 0;">
                <option value="">Select Doctor...</option>
                <option v-for="doc in doctors" :key="doc.id" :value="doc.id">{{ doc.name }}</option>
              </select>
            </div>
          </div>
          <div class="p-6">
            <div v-if="!rosterDoctor" class="text-center text-muted text-sm py-4">Select a doctor and date to view their schedule.</div>
            <div v-else-if="isLoadingRoster" class="text-center text-muted text-sm py-4">Loading schedule...</div>
            <div v-else-if="rosterSlots.length === 0" class="text-center text-muted text-sm py-4">Doctor is not scheduled or fully booked on this date.</div>
            <div class="flex flex-wrap gap-2">
              <div v-for="slot in rosterSlots" :key="slot" 
                   class="badge px-3 py-2 text-sm font-medium border"
                   :class="rosterBooked.includes(slot) ? 'bg-danger text-white border-danger opacity-75 line-through' : 'bg-secondary-light text-secondary border-secondary'">
                {{ slot }}
              </div>
            </div>
          </div>
        </div>

        <div class="card p-0">
          <div class="p-4 border-b border-color flex justify-between items-center bg-surface">
            <h2 class="text-lg">Today's Appointments ({{ todayAppointments.length }})</h2>
            <button class="btn btn-sm btn-outline text-muted" @click="fetchTodayAppointments">↻ Refresh</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="isLoadingToday">
                <td colspan="4" class="text-center text-muted py-4">Loading appointments...</td>
              </tr>
              <tr v-else-if="todayAppointments.length === 0">
                <td colspan="4" class="text-center text-muted py-4">No appointments scheduled for today.</td>
              </tr>
              <tr v-else v-for="appt in todayAppointments" :key="appt.id">
                <td class="font-medium text-main">{{ formatTime(appt.appointment_time) }}</td>
                <td>{{ appt.patient?.user?.name || appt.patient_name || 'Patient' }}</td>
                <td class="text-sm text-muted">{{ getDoctorName(appt.doctor_id) }}</td>
                <td>
                  <span
                    class="badge"
                    :class="
                      appt.status === 'scheduled'
                        ? 'badge-success'
                        : appt.status === 'cancelled'
                        ? 'badge-cancelled'
                        : 'badge-pending'
                    "
                  >
                    {{ appt.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div>
        <div class="card bg-secondary-light border-secondary mb-6">
          <div class="flex items-center gap-2 text-secondary mb-4">
             <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
            <h2 class="text-lg">Crowd Control</h2>
          </div>
          <p class="text-sm mb-4 text-secondary">Limit the total number of patients allowed to book within a single hour across the clinic.</p>
          
          <div class="form-group mb-4">
            <label class="form-label text-xs text-secondary font-bold">MAX PATIENTS PER HOUR</label>
            <input type="number" v-model="peakConfig.max_hourly_patients" class="form-control bg-surface" />
          </div>
          
          <button class="btn w-full" style="background-color: var(--secondary); color: white;" @click="savePeakConfig" :disabled="isSavingConfig">
            {{ isSavingConfig ? 'Saving...' : 'Update Limit' }}
          </button>
        </div>
      </div>

    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content card">
        <div class="flex justify-between items-center border-b border-color pb-4 mb-4">
          <h2 class="text-xl">
            <span v-if="modalStep === 1">Find Patient</span>
            <span v-else-if="modalStep === 2">Book Appointment</span>
            <span v-else>New Patient Registration</span>
          </h2>
          <button class="btn btn-sm text-muted" @click="closeModal">✕</button>
        </div>
        <div v-if="modalError" class="error-alert mb-4 text-sm">{{ modalError }}</div>
        <form v-if="modalStep === 1" @submit.prevent="handleSearch">
          <p class="text-sm text-muted mb-4">Enter patient phone number to check records.</p>
          <div class="form-group mb-4">
            <input type="text" v-model="searchPhone" required class="form-control" placeholder="Phone Number...">
          </div>
          <button type="submit" class="btn btn-primary w-full" :disabled="isSubmitting">Search</button>
        </form>
        <form v-if="modalStep > 1" @submit.prevent="handleBooking" class="flex flex-col gap-4">
          <div v-if="modalStep === 2" class="bg-secondary-light p-3 rounded text-sm text-secondary border border-secondary mb-2">
            <strong>Patient Found:</strong> {{ selectedPatient.name }} ({{ selectedPatient.phone }})
          </div>
          <div v-if="modalStep === 3" class="grid grid-cols-2 gap-4 border-b border-color pb-4 mb-2">
            <div class="col-span-2 text-sm text-main font-bold">Patient Details</div>
            <div><label class="text-xs">Name *</label><input type="text" v-model="newPatient.name" required class="form-control"></div>
            <div><label class="text-xs">Email *</label><input type="email" v-model="newPatient.email" required class="form-control"></div>
            <div><label class="text-xs">DOB *</label><input type="date" v-model="newPatient.dob" required class="form-control"></div>
            <div><label class="text-xs">Age</label><input type="number" v-model="newPatient.age" class="form-control" placeholder="e.g. 34"></div>
            <div class="col-span-2"><label class="text-xs">Gender</label><select v-model="newPatient.gender" class="form-control"><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option></select></div>
          </div>
          <div class="text-sm text-main font-bold">Appointment Details</div>
          <div><label class="text-xs">Doctor *</label><select v-model="appointmentForm.doctor_id" required class="form-control"><option value="" disabled>Select Doctor...</option><option v-for="doc in doctors" :key="doc.id" :value="doc.id">{{ doc.name }}</option></select></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="text-xs">Date *</label><input type="date" v-model="appointmentForm.appointment_date" required class="form-control"></div>
            <div><label class="text-xs">Time *</label><select v-model="appointmentForm.appointment_time" required class="form-control" :disabled="isLoadingSlots || availableSlots.length === 0"><option value="" disabled>{{ isLoadingSlots ? 'Loading slots...' : (availableSlots.length === 0 ? 'Select Doctor & Date first' : 'Select Time...') }}</option><option v-for="slot in availableSlots" :key="slot" :value="slot">{{ slot }}</option></select></div>
          </div>
          <div class="flex gap-4 mt-4">
            <button type="submit" class="btn btn-primary flex-1" :disabled="isSubmitting">{{ isSubmitting ? 'Processing...' : 'Confirm Appointment' }}</button>
            <button type="button" class="btn btn-outline flex-1" @click="closeModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../../services/api'

// --- HELPER: GET TODAY ---
const getTodayDate = () => {
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, '0')
  const dd = String(today.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}
const formatTime = (timeStr) => {
  if(!timeStr) return '-'
  return timeStr.substring(0, 5) // Cuts HH:MM:SS to HH:MM
}

const getDoctorName = (id) => {
  if (!id) return '-'
  const found = doctors.value.find(d => d.id === id)
  return found ? found.name : 'Unknown Doctor'
}

// --- STATE ---
const doctors = ref([])
const todayAppointments = ref([])
const isLoadingToday = ref(false)

const peakConfig = ref({ max_hourly_patients: 10 })
const isSavingConfig = ref(false)

// Roster State
const rosterDate = ref(getTodayDate())
const rosterDoctor = ref('')
const rosterSlots = ref([])
const rosterBooked = ref([]) // <-- Add this
const isLoadingRoster = ref(false)

// Modal State
const showModal = ref(false)
const modalStep = ref(1)
const isSubmitting = ref(false)
const newlyCreatedPatientId = ref(null)
const modalError = ref('')
const searchPhone = ref('')
const selectedPatient = ref(null)
const appointmentForm = ref({ doctor_id: '', appointment_date: '', appointment_time: '' })
const newPatient = ref({ name: '', email: '', phone: '', dob: '', age: '', gender: 'Male' })
const availableSlots = ref([])
const isLoadingSlots = ref(false)


// --- INIT FETCH ---
onMounted(() => {
  fetchDoctors()
  fetchTodayAppointments()
  fetchPeakConfig()
})

// --- API CALLS ---
const fetchDoctors = async () => {
  try {
    const res = await api.get('/admin/doctors') 
    doctors.value = res.data.map(doc => ({
      id: doc.id,
      name: `Dr. ${doc.name || doc.user?.name || 'Unknown'} (${doc.specialization || 'General'})` 
    }))
  } catch (err) { console.error("Failed to load doctors", err) }
}

const fetchTodayAppointments = async () => {
  isLoadingToday.value = true
  try {
    const res = await api.get('/admin/appointments', { params: { date: getTodayDate() } })
    todayAppointments.value = res.data
  } catch (err) { console.error("Failed to load today's appointments", err) }
  finally { isLoadingToday.value = false }
}

const fetchPeakConfig = async () => {
  try {
    const res = await api.get('/admin/config')
    peakConfig.value = res.data
  } catch (err) { console.error("Failed to load config", err) }
}

const savePeakConfig = async () => {
  isSavingConfig.value = true
  try {
    await api.post('/admin/config', peakConfig.value)
    alert("Crowd control limit updated!")
  } catch (err) { alert("Failed to save limit") }
  finally { isSavingConfig.value = false }
}

// --- DOCTOR ROSTER LOGIC ---
const fetchRoster = async () => {
  if (!rosterDoctor.value || !rosterDate.value) return
  isLoadingRoster.value = true
  try {
    const res = await api.get(`/doctors/${rosterDoctor.value}/availability`, { params: { date: rosterDate.value } })
    // Now we use all_slots to draw the board, and keep track of booked_slots
    rosterSlots.value = res.data?.all_slots || []
    rosterBooked.value = res.data?.booked_slots || []
  } catch (err) { 
    rosterSlots.value = []
    rosterBooked.value = []
  } 
  finally { isLoadingRoster.value = false }
}

// Watchers
watch([rosterDoctor, rosterDate], fetchRoster)

watch([() => appointmentForm.value.doctor_id, () => appointmentForm.value.appointment_date], async () => {
  availableSlots.value = []
  if (!appointmentForm.value.doctor_id || !appointmentForm.value.appointment_date) return
  isLoadingSlots.value = true
  try {
    const res = await api.get(`/doctors/${appointmentForm.value.doctor_id}/availability`, { params: { date: appointmentForm.value.appointment_date } })
    availableSlots.value = Array.isArray(res.data?.available_slots) ? res.data.available_slots : []
  } catch (err) { availableSlots.value = [] }
  finally { isLoadingSlots.value = false }
})

// --- BOOKING LOGIC (UNCHANGED) ---
const closeModal = () => {
  showModal.value = false; modalStep.value = 1; searchPhone.value = '';
  selectedPatient.value = null; modalError.value = ''; newlyCreatedPatientId.value = null;
}

const handleSearch = async () => {
  if (!searchPhone.value) return
  isSubmitting.value = true; modalError.value = ''
  try {
    const res = await api.get('/admin/patients')
    const found = res.data.find(p => p.phone === searchPhone.value)
    if (found) { selectedPatient.value = found; modalStep.value = 2 } 
    else { newPatient.value.phone = searchPhone.value; modalStep.value = 3 }
  } catch (err) { modalError.value = "Failed to search patient." } 
  finally { isSubmitting.value = false }
}

const handleBooking = async () => {
  isSubmitting.value = true; modalError.value = ''; let targetPatientId = null
  try {
    if (modalStep.value === 3) {
      if (newlyCreatedPatientId.value) targetPatientId = newlyCreatedPatientId.value
      else {
        const dateParts = newPatient.value.dob.split('-')
        const payload = { ...newPatient.value, password: `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`, age: newPatient.value.age ? Number(newPatient.value.age) : null }
        const signupRes = await api.post('/signup', payload)
        targetPatientId = signupRes.data.patient.id; newlyCreatedPatientId.value = targetPatientId 
      }
    } else { targetPatientId = selectedPatient.value.id }

    await api.post('/appointments/book', { patient_id: targetPatientId, ...appointmentForm.value })
    alert("Appointment successfully booked!")
    closeModal()
    fetchTodayAppointments() // Refresh list automatically
    if(rosterDoctor.value === appointmentForm.value.doctor_id && rosterDate.value === appointmentForm.value.appointment_date) {
      fetchRoster() // Refresh the roster visually if it affects the current view
    }
  } catch (err) { modalError.value = err?.response?.data?.error || "Failed to complete booking." } 
  finally { isSubmitting.value = false }
}
</script>

<style scoped>
/* Keep your exact existing CSS block here from your previous code */
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mt-2 { margin-top: 0.5rem; }
.p-0 { padding: 0; }
.p-2 { padding: 0.5rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.px-3 { padding-left: 0.75rem; padding-right: 0.75rem; }
.py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.ml-2 { margin-left: 0.5rem; }
.w-full { width: 100%; }

.flex-wrap { flex-wrap: wrap; }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); display: grid; }
.col-span-2 { grid-column: span 2 / span 2; }
.flex-col { flex-direction: column; }

.border-b { border-bottom: 1px solid var(--border-color); }
.border { border: 1px solid var(--border-color); }
.rounded { border-radius: var(--radius-md); }

.bg-primary-light { background-color: var(--primary-light); }
.border-primary { border-color: var(--primary); }
.text-primary { color: var(--primary); }

.bg-secondary-light { background-color: #f0fdf4; }
.border-secondary { border-color: #bbf7d0; }
.text-secondary { color: var(--secondary); }

.bg-background { background-color: var(--background); }
.bg-surface { background-color: var(--surface); }

.text-danger { color: var(--danger); }
.text-muted { color: var(--text-muted); }
.text-main { color: var(--text-main); }
.opacity-50 { opacity: 0.5; }
.cursor-pointer { cursor: pointer; }

.text-lg { font-size: 1.125rem; font-weight: 600; }
.text-xs { font-size: 0.75rem; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.text-center { text-align: center; }

.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; font-weight: 500;}

.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 50; backdrop-filter: blur(2px); }
.modal-content { width: 100%; max-width: 500px; background-color: var(--surface); padding: 1.5rem; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.form-control { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background-color: var(--background); color: var(--text-main); margin-top: 0.25rem; }
.form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1); }
.error-alert { color: var(--danger); background-color: #fee2e2; padding: 0.75rem; border-radius: var(--radius-sm); border: 1px solid #f87171; }
.badge-success { background-color: #fef08a; color: #854d0e;}
.badge-pending { background-color: #dcfce7; color: #166534; }

/* --- Missing Red Status Colors --- */
.bg-danger { background-color: #ab0000; }
.border-danger { border-color: #ef4444; }
.line-through { text-decoration: line-through; }
.text-white { color: #ffffff; }
.opacity-75 { opacity: 0.75; }

.badge-cancelled {
  background-color: #fee2e2; /* light red */
  color: #991b1b;           /* dark red text */
}
</style>