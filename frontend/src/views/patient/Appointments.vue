<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '../../services/api'
import { useRouter } from 'vue-router'

const appointments = ref([])
const doctors = ref([])
const availableSlots = ref([])
const isLoadingAppointments = ref(false)
const isLoadingDoctors = ref(false)
const isLoadingSlots = ref(false)
const isBooking = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const router = useRouter()
const newAppt = reactive({
  doctor_id: '',
  date: '',
  time: ''
})

const formatDoctorLabel = (doctor) => {
  if (!doctor) return ''
  return doctor.specialization
    ? `${doctor.name} (${doctor.specialization})`
    : doctor.name
}

const doctorMap = computed(() => {
  const map = {}
  for (const doctor of doctors.value) {
    map[doctor.id] = doctor
  }
  return map
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTimeForDisplay = (time24) => {
  if (!time24) return '-'
  const [hourStr, minute] = time24.split(':')
  let hour = Number(hourStr)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  hour = hour % 12 || 12
  return `${hour}:${minute} ${ampm}`
}

const mapStatus = (status) => {
  if (!status) return 'Upcoming'
  const normalized = status.toLowerCase()
  if (normalized === 'completed') return 'Completed'
  if (normalized === 'cancelled') return 'Cancelled'
  return 'Upcoming'
}

const fetchDoctors = async () => {
  isLoadingDoctors.value = true
  try {
    const res = await api.get('/admin/doctors')
    doctors.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    errorMessage.value = err?.response?.data?.error || 'Failed to load doctors.'
  } finally {
    isLoadingDoctors.value = false
  }
}

const fetchAppointments = async () => {
  isLoadingAppointments.value = true
  try {
    const res = await api.get('/appointments')
    const data = Array.isArray(res.data) ? res.data : []

    appointments.value = data.map((appt) => {
      const doctor = doctorMap.value[appt.doctor_id]

      return {
        id: appt.id,
        rawDate: appt.appointment_date,
        rawTime: appt.appointment_time,
        date: formatDate(appt.appointment_date),
        time: formatTimeForDisplay(appt.appointment_time),
        doc: appt.doctor_name || doctor?.name || '-',
        dept: doctor?.specialization || '-',
        status: mapStatus(appt.status)
      }
    })
  } catch (err) {
    errorMessage.value = err?.response?.data?.error || 'Failed to load appointments.'
  } finally {
    isLoadingAppointments.value = false
  }
}

const fetchAvailableSlots = async () => {
  availableSlots.value = []

  if (!newAppt.doctor_id || !newAppt.date) return

  isLoadingSlots.value = true
  try {
    const res = await api.get(`/doctors/${newAppt.doctor_id}/availability`, {
      params: { date: newAppt.date }
    })
    availableSlots.value = Array.isArray(res.data?.available_slots)
      ? res.data.available_slots
      : []
  } catch (err) {
    availableSlots.value = []
    errorMessage.value = err?.response?.data?.error || 'Failed to load available slots.'
  } finally {
    isLoadingSlots.value = false
  }
}

const handleBook = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isBooking.value = true

  try {
    const payload = {
      doctor_id: Number(newAppt.doctor_id),
      appointment_date: newAppt.date,
      appointment_time: newAppt.time
    }

    await api.post('/appointments/book', payload)

    successMessage.value = 'Appointment booked successfully.'

    newAppt.doctor_id = ''
    newAppt.date = ''
    newAppt.time = ''
    availableSlots.value = []

    await fetchAppointments()
  } catch (err) {
    errorMessage.value =
      err?.response?.data?.error || 'Failed to book appointment.'
  } finally {
    isBooking.value = false
  }
}

const cancelAppointment = async (appointmentId) => {
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.post(`/appointments/${appointmentId}/cancel`)
    successMessage.value = 'Appointment cancelled successfully.'
    await fetchAppointments()
  } catch (err) {
    errorMessage.value =
      err?.response?.data?.error || 'Failed to cancel appointment.'
  }
}

watch(() => doctorMap.value, async () => {
  if (doctors.value.length) {
    await fetchAppointments()
  }
})

watch(
  () => [newAppt.doctor_id, newAppt.date],
  async () => {
    newAppt.time = ''
    await fetchAvailableSlots()
  }
)

onMounted(async () => {
  await fetchDoctors()
  await fetchAppointments()
})
</script>

<template>
  <div class="patient-appointments max-w-7xl mx-auto" style = "background:#ffffff; border-radius:30px;padding: 28px; ">
    <div class="flex justify-between items-center mb-3">
      <div>
        <h1>Book Appointment</h1>
      </div>
    </div>

    <div
      v-if="errorMessage"
      class="mb-4 p-4 rounded"
      style="background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="mb-4 p-4 rounded"
      style="background:#dcfce7; color:#166534; border:1px solid #86efac;"
    >
      {{ successMessage }}
    </div>

    <div class="card mb-8">
      <h2 class="text-lg mb-4">Schedule Your Visit</h2>

      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="form-group">
          <label class="form-label">Preferred Doctor</label>
          <select v-model="newAppt.doctor_id" class="form-control bg-surface" required>
            <option value="">Select Doctor</option>
            <option
              v-for="doctor in doctors"
              :key="doctor.id"
              :value="doctor.id"
            >
              {{ formatDoctorLabel(doctor) }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Select Date</label>
          <input type="date" v-model="newAppt.date" class="form-control bg-surface" required />
        </div>

        <div class="form-group">
          <label class="form-label">Available Time Slots</label>
          <select v-model="newAppt.time" class="form-control bg-surface" required>
            <option value="">
              {{ isLoadingSlots ? 'Loading slots...' : 'Select Time' }}
            </option>
            <option
              v-for="slot in availableSlots"
              :key="slot"
              :value="slot"
            >
              {{ formatTimeForDisplay(slot) }}
            </option>
          </select>
        </div>
      </div>

      <div class="flex justify-end">
        <button
          class="btn btn-primary px-8"
          :disabled="!newAppt.doctor_id || !newAppt.date || !newAppt.time || isBooking"
          @click="handleBook"
        >
          {{ isBooking ? 'Booking...' : 'Confirm Appointment' }}
        </button>
      </div>
    </div>

    <div class="card p-0 overflow-hidden">
      <div class="p-4 border-b border-color bg-background">
        <h2 class="text-lg">Appointment History</h2>
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>Date & Time</th>
            <th>Doctor / Dept</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoadingAppointments">
            <td colspan="4" class="text-center py-6 text-muted">Loading appointments...</td>
          </tr>

          <tr v-else-if="appointments.length === 0">
            <td colspan="4" class="text-center py-6 text-muted">You have no appointment history.</td>
          </tr>

          <tr v-else v-for="appt in appointments" :key="appt.id">
            <td>
              <div class="font-bold text-main">{{ appt.date }}</div>
              <div class="text-sm text-muted mt-1">{{ appt.time }}</div>
            </td>
            <td>
              <div class="font-medium">{{ appt.doc }}</div>
              <div class="text-sm text-muted mt-1">{{ appt.dept }}</div>
            </td>
            <td>
              <span
                class="badge"
                :class="
                  appt.status === 'Completed'
                    ? 'badge-info'
                    : appt.status === 'Cancelled'
                    ? 'badge-danger'
                    : 'badge-success'
                "
              >
                {{ appt.status }}
              </span>
            </td>
            <td>
              <button
                class="btn btn-sm btn-outline text-danger"
                v-if="appt.status === 'Upcoming'"
                @click="cancelAppointment(appt.id)"
              >
                Cancel
              </button>
              
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-7xl { max-width: 80rem; }

.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }
.mb-4 { margin-bottom: 1rem; }
.mt-4 { margin-top: 1rem; }
.mt-1 { margin-top: 0.25rem; }
.py-6 { padding-top: 1.5rem; padding-bottom: 1.5rem; }
.p-0 { padding: 0; }
.p-4 { padding: 1rem; }

.grid-cols-2 { grid-template-columns: 1fr 1fr; display: grid; }
.col-span-2 { grid-column: span 2 / span 2; }
.text-right { text-align: right; }
.text-center { text-align: center; }

.border-b { border-bottom: 1px solid var(--border-color); }
.border-primary { border: 1px solid var(--primary); }
.bg-primary-light { background-color: var(--primary-light); }
.bg-background { background-color: var(--background); }
.bg-surface { background-color: var(--surface); }
.overflow-hidden { overflow: hidden; }

.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.text-xl { font-size: 1.25rem; }
.text-lg { font-size: 1.125rem; }
.text-sm { font-size: 0.875rem; }

.text-muted { color: var(--text-muted); }
.text-primary { color: var(--primary); }
.text-primary-dark { color: var(--primary-dark); }
.text-danger { color: var(--danger); }
.text-main { color: var(--text-main); }

.shadow { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 500;}
</style>