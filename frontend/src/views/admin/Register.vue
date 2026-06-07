<script setup>
import { ref, computed } from 'vue'
import api from '../../services/api' 

// --- ADMIN FORM STATE ---
const adminForm = ref({
  name: '',
  email: '',
  phone: '',
  password: ''
})
const isRegisteringAdmin = ref(false)
const adminSuccess = ref('')
const adminError = ref('')

// --- DOCTOR FORM STATE ---
const doctorForm = ref({
  name: '',
  email: '',
  phone: '',
  password: '',
  specialization: '',
  consultation_fee: null
})

// --- SCHEDULE STATE ---
const scheduleForm = ref({
  startDay: 1, // Default: Monday
  endDay: 5,   // Default: Friday
  startTime: '10:00',
  endTime: '16:00',
  slotDuration: 30 // Default: 30 mins
})

const daysOptions = [
  { value: 0, label: 'Sunday' },
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' }
]

// --- COMPUTED: days preview pill ---
const daysPreview = computed(() => {
  const from = parseInt(scheduleForm.value.startDay)
  const to   = parseInt(scheduleForm.value.endDay)
  if (from > to) return 'Invalid range'
  return daysOptions.slice(from, to + 1).map(d => d.label.slice(0, 3)).join(', ')
})

const isRegisteringDoctor = ref(false)
const doctorSuccess = ref('')
const doctorError = ref('')

// --- UTILS ---
// Generates an array of days [1, 2, 3, 4, 5] inclusive, handling weekend wrap-around
const getDaysArray = (start, end) => {
  let days = []
  let current = start
  while (true) {
    days.push(current)
    if (current === end) break
    current = (current + 1) % 7 // Wraps 6 back to 0
  }
  return days
}

// --- SUBMIT HANDLERS ---
const submitAdmin = async () => {
  isRegisteringAdmin.value = true
  adminSuccess.value = ''
  adminError.value = ''

  try {
    const response = await api.post('/admin/users/admin', adminForm.value)
    adminSuccess.value = response.data.message || 'Admin registered successfully!'
    
    adminForm.value = { name: '', email: '', phone: '', password: '' }
  } catch (err) {
    adminError.value = err.response?.data?.error || 'Failed to register admin. Please try again.'
  } finally {
    isRegisteringAdmin.value = false
  }
}

const submitDoctor = async () => {
  isRegisteringDoctor.value = true
  doctorSuccess.value = ''
  doctorError.value = ''

  try {
    // 1. Create the Doctor
    const docResponse = await api.post('/admin/doctors', doctorForm.value)
    
    // CRITICAL: Your backend POST /admin/doctors must return the new doctor's ID!
    const doctorId = docResponse.data.id || docResponse.data.doctor?.id 

    if (!doctorId) {
      throw new Error("Doctor created, but backend did not return the doctor ID to attach the schedule.")
    }

    // 2. Generate schedule array and post to schedule endpoint
    const days_of_week = getDaysArray(scheduleForm.value.startDay, scheduleForm.value.endDay)
    
    const schedulePayload = {
      days_of_week: days_of_week,
      start_time: scheduleForm.value.startTime, 
      end_time: scheduleForm.value.endTime,
      slot_duration: scheduleForm.value.slotDuration
    }

    await api.post(`/admin/doctors/${doctorId}/schedules`, schedulePayload)

    doctorSuccess.value = 'Doctor and schedule registered successfully!'
    
    // Reset forms
    doctorForm.value = { 
      name: '', email: '', phone: '', password: '', specialization: '', consultation_fee: null 
    }
    scheduleForm.value = { startDay: 1, endDay: 5, startTime: '10:00', endTime: '16:00', slotDuration: 30 }

  } catch (err) {
    doctorError.value = err.response?.data?.error || err.message || 'Failed to register doctor or schedule.'
  } finally {
    isRegisteringDoctor.value = false
  }
}
</script>

<template>
  <div class="registration-dashboard">
    <div class="page-header">
      <h1>Staff Registration</h1>
      <p class="subtitle">Securely onboard new administrators and medical professionals.</p>
    </div>

    <div class="forms-grid">
      
      <div class="registration-card">
        <h2 class="card-heading">Register a new Admin</h2>
        
        <div v-if="adminSuccess" class="alert alert-success">{{ adminSuccess }}</div>
        <div v-if="adminError" class="alert alert-error">{{ adminError }}</div>

        <form @submit.prevent="submitAdmin" class="sleek-form">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input type="text" v-model="adminForm.name" class="form-input" placeholder="e.g. Kashish Rathore" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input type="email" v-model="adminForm.email" class="form-input" placeholder="kashish@gmail.com" required />
          </div>
          <div class="form-group">
            <label class="form-label">Phone Number</label>
            <input type="tel" v-model="adminForm.phone" class="form-input" placeholder="0000-0000" required />
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" v-model="adminForm.password" class="form-input" placeholder="••••" required />
          </div>

          <button type="submit" class="btn-submit" :disabled="isRegisteringAdmin">
            {{ isRegisteringAdmin ? 'Registering...' : 'Create Admin Account' }}
          </button>
        </form>
      </div>

      <div class="registration-card">
        <h2 class="card-heading">Register a new Doctor</h2>
        
        <div v-if="doctorSuccess" class="alert alert-success">{{ doctorSuccess }}</div>
        <div v-if="doctorError" class="alert alert-error">{{ doctorError }}</div>

        <form @submit.prevent="submitDoctor" class="sleek-form">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input type="text" v-model="doctorForm.name" class="form-input" placeholder="e.g. Dr. Aman Kumar" required />
          </div>

          <div class="form-row">
            <div class="form-group half-width">
              <label class="form-label">Email Address</label>
              <input type="email" v-model="doctorForm.email" class="form-input" placeholder="doctor@hospital.com" required />
            </div>
            <div class="form-group half-width">
              <label class="form-label">Phone Number</label>
              <input type="tel" v-model="doctorForm.phone" class="form-input" placeholder="0000-0000" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group half-width">
              <label class="form-label">Specialization</label>
              <input type="text" v-model="doctorForm.specialization" class="form-input" placeholder="e.g. Cardiology" required />
            </div>
            <div class="form-group half-width">
              <label class="form-label">Consultation Fee (₹)</label>
              <input type="number" v-model="doctorForm.consultation_fee" class="form-input" placeholder="800" required />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" v-model="doctorForm.password" class="form-input" placeholder="••••" required />
          </div>

          <!-- ── Schedule Section ── -->
          <div class="schedule-section">
            <div class="schedule-header">
              <div class="schedule-title-row">
                <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="2" y="3" width="14" height="13" rx="2" stroke="currentColor" stroke-width="1.4"/>
                  <path d="M6 1.5v3M12 1.5v3M2 7h14" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                  <circle cx="6" cy="11" r="1" fill="currentColor"/>
                  <circle cx="9" cy="11" r="1" fill="currentColor"/>
                  <circle cx="12" cy="11" r="1" fill="currentColor"/>
                </svg>
                <span>Weekly Schedule</span>
              </div>
              <div v-if="daysPreview !== 'Invalid range'" class="days-preview-pill">
                {{ daysPreview }}
              </div>
              <div v-else class="days-preview-pill days-preview-error">Invalid range</div>
            </div>

            <div class="schedule-body">

              <!-- Day range -->
              <div class="form-row">
                <div class="form-group half-width">
                  <label class="form-label">Working Days (From)</label>
                  <select v-model="scheduleForm.startDay" class="form-input" required>
                    <option v-for="day in daysOptions" :key="'start-'+day.value" :value="day.value">
                      {{ day.label }}
                    </option>
                  </select>
                </div>
                <div class="form-group half-width">
                  <label class="form-label">Working Days (To)</label>
                  <select v-model="scheduleForm.endDay" class="form-input" required>
                    <option v-for="day in daysOptions" :key="'end-'+day.value" :value="day.value">
                      {{ day.label }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Time range -->
              <div class="form-row">
                <div class="form-group half-width">
                  <label class="form-label">Shift Start Time</label>
                  <input type="time" v-model="scheduleForm.startTime" class="form-input" required />
                </div>
                <div class="form-group half-width">
                  <label class="form-label">Shift End Time</label>
                  <input type="time" v-model="scheduleForm.endTime" class="form-input" required />
                </div>
              </div>

              <!-- Slot duration chips -->
              <div class="form-group">
                <label class="form-label">Slot Duration (Minutes)</label>
                <div class="slot-options">
                  <label v-for="min in [15, 20, 30, 45, 60]" :key="min" class="slot-chip" :class="{ active: scheduleForm.slotDuration === min }">
                    <input type="radio" :value="min" v-model="scheduleForm.slotDuration" style="display:none" />
                    {{ min }} min
                  </label>
                </div>
              </div>

            </div>
          </div>

          <button type="submit" class="btn-submit" :disabled="isRegisteringDoctor">
            {{ isRegisteringDoctor ? 'Registering...' : 'Create Doctor & Schedule' }}
          </button>
        </form>
      </div>

    </div>
  </div>
</template>

<style scoped>
.registration-dashboard { max-width: 80rem; margin: 0 auto; padding: 1rem 0; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 1.75rem; color: #1e293b; margin: 0 0 0.5rem 0; }
.subtitle { color: #64748b; margin: 0; font-size: 0.95rem; }
.forms-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; max-width: 1000px; margin: 0 auto; align-items: start; }
.registration-card { background-color: #ffffff; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01); border: 1px solid #f1f5f9; display: flex; flex-direction: column; }
.card-heading { color: #10b981; font-size: 1.35rem; font-weight: 500; margin: 0 0 2rem 0; letter-spacing: -0.01em; }
.sleek-form { display: flex; flex-direction: column; flex: 1; }
.form-row { display: flex; gap: 1rem; }
.form-group { margin-bottom: 1.25rem; width: 100%; }
.half-width { flex: 1; }
.form-label { display: block; font-size: 0.79rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 400; text-transform: uppercase; letter-spacing: 0.03em; }
.form-input { width: 100%; padding: 0.85rem 1rem; border-radius: 12px; border: 1px solid #e2e8f0; background-color: #f8fafc; font-size: 0.95rem; color: #1e293b; font-family: inherit; transition: all 0.2s ease; box-sizing: border-box; appearance: none; -webkit-appearance: none; }
.form-input::placeholder { color: #94a3b8; }
.form-input:focus { outline: none; border-color: #10b981; background-color: #ffffff; box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1); }

/* ── Schedule Section ── */
.schedule-section {
  border: 1.5px solid #d1fae5;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 1.25rem;
}

.schedule-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ecfdf5;
  padding: 10px 14px;
  gap: 10px;
}

.schedule-title-row {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #065f46;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.schedule-title-row svg {
  width: 15px;
  height: 15px;
  color: #10b981;
  flex-shrink: 0;
}

.days-preview-pill {
  font-size: 0.72rem;
  font-weight: 600;
  background: #d1fae5;
  color: #065f46;
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.days-preview-error {
  background: #fee2e2;
  color: #991b1b;
}

.schedule-body {
  padding: 16px 14px 4px;
}

/* Slot chips */
.slot-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.slot-chip {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1.5px solid #e2e8f0;
  font-size: 0.8rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  background: #f8fafc;
  transition: all 0.15s;
  user-select: none;
}

.slot-chip:hover {
  border-color: #10b981;
  color: #065f46;
  background: #ecfdf5;
}

.slot-chip.active {
  background: #10b981;
  border-color: #10b981;
  color: #ffffff;
  font-weight: 600;
}

/* ── Submit ── */
.btn-submit { margin-top: auto; padding: 1rem; border-radius: 12px; background-color: #117c54; color: #ffffff; border: none; font-size: 1rem; font-weight: 500; cursor: pointer; transition: background-color 0.2s ease, transform 0.1s ease; }
.btn-submit:hover:not(:disabled) { background-color: #059669; }
.btn-submit:active:not(:disabled) { transform: scale(0.98); }
.btn-submit:disabled { background-color: #94a3b8; cursor: not-allowed; opacity: 0.7; }

/* ── Alerts ── */
.alert { padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; font-size: 0.9rem; font-weight: 500; }
.alert-success { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.alert-error { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

@media (max-width: 768px) {
  .form-row { flex-direction: column; gap: 0; }
  .registration-card { padding: 1.5rem; }
  .slot-options { gap: 6px; }
}
</style>