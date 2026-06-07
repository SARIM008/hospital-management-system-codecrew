<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const step = ref(1) // 1: Phone, 2: OTP, 3: Details, 4: Success
const isLoading = ref(false)
const errorMessage = ref('')

// Form data
const bookingData = reactive({
  phone: '',
  otp: '',
  department: '',
  doctor: '',
  date: '',
  time: ''
})

// Mock Data
const departments = ['General Medicine', 'Orthopedics', 'Cardiology', 'Pediatrics']
const doctors = {
  'General Medicine': ['Dr. Sharma', 'Dr. Patil'],
  'Orthopedics': ['Dr. Iyer'],
  'Cardiology': ['Dr. Menon'],
  'Pediatrics': ['Dr. Gupta']
}

const handlePhoneSubmit = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    if (bookingData.phone.length !== 10) throw new Error("Enter a valid 10-digit mobile number")
    await authStore.sendOtp(bookingData.phone)
    step.value = 2
  } catch (err) {
    errorMessage.value = err.message
  } finally {
    isLoading.value = false
  }
}

const handleOtpSubmit = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    // Authenticate the user behind the scenes
    await authStore.loginPatientWithOtp(bookingData.phone, bookingData.otp)
    step.value = 3
  } catch (err) {
    errorMessage.value = err.message || "Invalid OTP"
  } finally {
    isLoading.value = false
  }
}

const handleDetailsSubmit = async () => {
  isLoading.value = true
  // Mock API call to save appointment
  setTimeout(() => {
    isLoading.value = false
    step.value = 4
  }, 800)
}

const finishBooking = () => {
  // They are already logged in from Step 2! Send them to their new dashboard.
  router.push('/dashboard')
}
</script>

<template>
  <div class="booking-page py-10 px-4">
    <div class="container mx-auto max-w-2xl">
      
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-main">Book Appointment</h1>
        <p class="text-muted mt-2">Schedule your visit in 3 easy steps</p>
      </div>

      <div class="card booking-card mx-auto">
        <!-- Progress Bar -->
        <div class="stepper flex justify-between mb-8 relative">
          <div class="step" :class="{ 'active': step >= 1, 'completed': step > 1 }"><span>1</span> Mobile</div>
          <div class="step" :class="{ 'active': step >= 2, 'completed': step > 2 }"><span>2</span> Verify</div>
          <div class="step" :class="{ 'active': step >= 3, 'completed': step > 3 }"><span>3</span> Details</div>
        </div>

        <!-- Step 1: Phone -->
        <form v-if="step === 1" @submit.prevent="handlePhoneSubmit">
          <h3 class="font-bold text-lg mb-4">Enter Mobile Number</h3>
          <p class="text-sm text-muted mb-4">We will send an OTP to verify your identity.</p>
          
          <div class="form-group mb-6">
            <div class="flex items-center">
              <span class="country-code border border-color border-r-0 rounded-l px-3 py-2 bg-background text-muted">+91</span>
              <input 
                type="tel" 
                v-model="bookingData.phone" 
                class="form-control rounded-l-none" 
                placeholder="10-digit mobile number"
                maxlength="10"
                required
              />
            </div>
          </div>
          
          <div v-if="errorMessage" class="error-alert mb-4">{{ errorMessage }}</div>
          
          <button type="submit" class="btn btn-primary w-full" :disabled="isLoading">
            {{ isLoading ? 'Sending...' : 'Get OTP' }}
          </button>
        </form>

        <!-- Step 2: OTP -->
        <form v-if="step === 2" @submit.prevent="handleOtpSubmit">
          <h3 class="font-bold text-lg mb-4">Verify OTP</h3>
          <p class="text-sm text-muted mb-4">Enter the 4-digit code sent to +91 {{ bookingData.phone }}.</p>
          
          <div class="form-group mb-6">
            <input 
              type="text" 
              v-model="bookingData.otp" 
              class="form-control text-center tracking-widest text-xl" 
              placeholder="• • • •"
              maxlength="4"
              required
            />
          </div>
          
          <div v-if="errorMessage" class="error-alert mb-4">{{ errorMessage }}</div>
          
          <div class="flex gap-4">
            <button type="button" @click="step = 1" class="btn btn-outline flex-1" :disabled="isLoading">Back</button>
            <button type="submit" class="btn btn-primary flex-1" :disabled="isLoading">
              {{ isLoading ? 'Verifying...' : 'Verify' }}
            </button>
          </div>
        </form>

        <!-- Step 3: Details -->
        <form v-if="step === 3" @submit.prevent="handleDetailsSubmit">
          <h3 class="font-bold text-lg mb-4">Select Details</h3>
          
          <div class="form-group mb-4">
            <label class="form-label">Department</label>
            <select v-model="bookingData.department" class="form-control" required @change="bookingData.doctor = ''">
              <option value="" disabled>Select Department</option>
              <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
            </select>
          </div>

          <div class="form-group mb-4" v-if="bookingData.department">
            <label class="form-label">Doctor (Optional)</label>
            <select v-model="bookingData.doctor" class="form-control">
              <option value="">Any Available Doctor</option>
              <option v-for="doc in doctors[bookingData.department]" :key="doc" :value="doc">{{ doc }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="form-group">
              <label class="form-label">Preferred Date</label>
              <input type="date" v-model="bookingData.date" class="form-control" required />
            </div>
            <div class="form-group">
              <label class="form-label">Time Slot</label>
              <select v-model="bookingData.time" class="form-control" required>
                <option value="" disabled>Select Time</option>
                <option value="09:00 AM">09:00 AM</option>
                <option value="11:00 AM">11:00 AM</option>
                <option value="02:00 PM">02:00 PM</option>
                <option value="04:00 PM">04:00 PM</option>
              </select>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-full" :disabled="isLoading">
             {{ isLoading ? 'Booking...' : 'Confirm Appointment' }}
          </button>
        </form>

        <!-- Step 4: Success -->
        <div v-if="step === 4" class="text-center py-4">
          <div class="success-icon bg-success-light text-success mx-auto mb-4">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="48" height="48">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="font-bold text-xl mb-2">Appointment Confirmed!</h3>
          <p class="text-muted mb-6">Your appointment for {{ bookingData.department }} on {{ bookingData.date }} at {{ bookingData.time }} is confirmed. You have been automatically logged in to your Patient Portal.</p>
          <button @click="finishBooking" class="btn btn-primary w-full">Go to My Dashboard</button>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.mx-auto { margin-left: auto; margin-right: auto; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.py-10 { padding-top: 2.5rem; padding-bottom: 2.5rem; }
.px-4 { padding-left: 1rem; padding-right: 1rem; }
.pt-10 { padding-top: 2.5rem; }
.max-w-2xl { max-width: 42rem; }
.w-full { width: 100%; }
.flex-1 { flex: 1; }

.text-3xl { font-size: 1.875rem; }
.text-xl { font-size: 1.25rem; font-weight: 500; }
.text-lg { font-size: 1.125rem; }
.text-sm { font-size: 0.875rem; }
.font-bold { font-weight: 700; }
.text-muted { color: var(--text-muted); }
.text-center { text-align: center; }

.booking-card {
  max-width: 500px;
  padding: 2rem;
}

/* Stepper CSS */
.stepper {
  position: relative;
}
.stepper::before {
  content: '';
  position: absolute;
  top: 14px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--border-color);
  z-index: 1;
}
.step {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--surface); /* cover the line */
  padding: 0 0.5rem;
}
.step span {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--background);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}
.step.active { color: var(--primary); }
.step.active span {
  border-color: var(--primary);
  color: var(--primary);
}
.step.completed span {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* Input Styles */
.border-r-0 { border-right: 0; }
.rounded-l { border-top-left-radius: var(--radius-md); border-bottom-left-radius: var(--radius-md); }
.rounded-l-none { border-top-left-radius: 0; border-bottom-left-radius: 0; }
.tracking-widest { letter-spacing: 0.25em; }

.grid-cols-2 { grid-template-columns: 1fr 1fr; }

.error-alert {
  padding: 0.75rem;
  background-color: var(--danger-light);
  color: var(--danger);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bg-success-light { background-color: #dcfce7; }
.text-success { color: #166534; }
</style>
