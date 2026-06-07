<script setup>
import { reactive, ref } from 'vue'

const isSubmitting = ref(false)
const showSuccess = ref(false)

const form = reactive({
  type: 'OPD',
  fullName: '',
  dob: '',
  gender: 'Male',
  contact: '',
  address: '',
  emergencyContact: '',
  chiefComplaint: '',
  referredBy: '',
  consultationFee: '₹500',
  doctor: 'Any'
})

const handleRegistration = () => {
  isSubmitting.value = true
  // Mock API Save
  setTimeout(() => {
    isSubmitting.value = false
    showSuccess.value = true
    
    // Auto clear after 3 seconds
    setTimeout(() => {
      showSuccess.value = false
      Object.keys(form).forEach(key => form[key] = '')
      form.type = 'OPD'
      form.gender = 'Male'
      form.consultationFee = '₹500'
      form.doctor = 'Any'
    }, 3000)
  }, 1000)
}
</script>

<template>
  <div class="staff-patients w-full">
    <div class="mb-6">
      <h1>Register New Patient</h1>

    </div>

    <div v-if="showSuccess" class="bg-success-light text-success p-4 rounded mb-6 flex items-center gap-3 border border-success">
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      <div>
        <h3 class="font-bold">Registration Successful</h3>
        <p class="text-sm">Patient ID PT-005 generated successfully.</p>
      </div>
    </div>

    <form @submit.prevent="handleRegistration">
      
      <!-- Type Selection Card -->
      <div class="card mb-8">
        <div class="flex">
          <label class="radio-card flex-1 cursor-pointer">
            <input type="radio" v-model="form.type" value="OPD" class="hidden" />
            <div class="val-box p-3 text-center rounded border border-color font-medium" :class="{'bg-primary-light border-primary text-primary': form.type === 'OPD'}">OPD Registration</div>
          </label>
          <div class="w-4"></div> <!-- spacer -->
          <label class="radio-card flex-1 cursor-pointer">
            <input type="radio" v-model="form.type" value="IPD" class="hidden" />
            <div class="val-box p-3 text-center rounded border border-color font-medium" :class="{'bg-primary-light border-primary text-primary': form.type === 'IPD'}">IPD Admission</div>
          </label>
        </div>
      </div>

      <div class="flex gap-8 flex-col-mobile">
        <!-- Left Column: Personal Information Card -->
        <div class="card flex-1">
          <h3 class="text-sm uppercase tracking-wider text-muted font-bold mb-6">Personal Information</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="form-group col-span-2">
              <label class="form-label">Full Name</label>
              <input type="text" v-model="form.fullName" class="form-control" required />
            </div>
            <div class="form-group">
              <label class="form-label">Date of Birth</label>
              <input type="date" v-model="form.dob" class="form-control" required />
            </div>
            <div class="form-group">
              <label class="form-label">Gender</label>
              <select v-model="form.gender" class="form-control">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Contact Number</label>
              <input type="tel" v-model="form.contact" class="form-control" required maxlength="10" />
            </div>
            <div class="form-group">
              <label class="form-label">Emergency Contact (Optional)</label>
              <input type="tel" v-model="form.emergencyContact" class="form-control" maxlength="10" />
            </div>
            <div class="form-group col-span-2 mb-0">
              <label class="form-label">Address / Landmark</label>
              <input type="text" v-model="form.address" class="form-control" required />
            </div>
          </div>
        </div>

        <!-- Right Column: Visit Details Card -->
        <div class="card flex-1">
          <h3 class="text-sm uppercase tracking-wider text-muted font-bold mb-6">Visit Details ({{ form.type }})</h3>
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="form-group col-span-2">
              <label class="form-label">Chief Complaint / Reason for visit</label>
              <textarea v-model="form.chiefComplaint" class="form-control" rows="3" required></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Assign Doctor</label>
              <select v-model="form.doctor" class="form-control">
                <option value="Any">General Physician (Available)</option>
                <option value="Dr. Sharma">Dr. Sharma (Ortho)</option>
                <option value="Dr. Patil">Dr. Patil (Pediatrics)</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Initial Consultation Fee</label>
              <input type="text" v-model="form.consultationFee" class="form-control bg-background" disabled />
            </div>
          </div>

          <!-- Section 3 Optional Upload-->
          <div class="mb-0">
            <label class="form-label">Upload Previous Prescription (Optional)</label>
            <div class="upload-area p-8 border border-dashed border-color rounded text-center text-muted bg-background cursor-pointer hover:border-primary">
               <svg class="mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="32" height="32">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
               </svg>
               <p class="text-sm">Drag & Drop or <span class="text-primary hover-underline">Browse</span></p>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-4 justify-end" style="margin-top: 3rem;">
        <button type="button" class="btn btn-outline px-6 bg-surface" style="border-radius: var(--radius-lg); padding: 0.75rem 1.5rem;" @click="$router.push('/staff')">Cancel</button>
        <button type="submit" class="btn btn-primary px-8" style="border-radius: var(--radius-lg); padding: 0.75rem 2rem;" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : 'Register Patient' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-3xl { max-width: 48rem; }
.w-full { width: 100%; }

@media (max-width: 768px) {
  .flex-col-mobile { flex-direction: column; }
  .right-col { border-left: none; padding-left: 0; }
}

@media (min-width: 769px) {
  .right-col {
    border-left: 1px solid var(--border-color);
    padding-left: 2rem;
  }
}
.w-4 { width: 1rem; }
.mb-8 { margin-bottom: 2rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.pb-6 { padding-bottom: 1.5rem; }
.pt-6 { padding-top: 1.5rem; }
.p-8 { padding: 2rem; }
.p-4 { padding: 1rem; }
.p-3 { padding: 0.75rem; }
.px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
.px-8 { padding-left: 2rem; padding-right: 2rem; }
.flex-1 { flex: 1; }
.justify-end { justify-content: flex-end; }

.grid-cols-2 { grid-template-columns: 1fr 1fr; display: grid; }
.col-span-2 { grid-column: span 2 / span 2; }

.text-muted { color: var(--text-muted); }
.text-primary { color: var(--primary); }
.text-success { color: #166534; }
.bg-success-light { background-color: #dcfce7; }
.border-success { border-color: #86efac; }
.bg-primary-light { background-color: var(--primary-light); }
.border-primary { border-color: var(--primary); }
.bg-background { background-color: var(--background); }

.border-b { border-bottom: 1px solid var(--border-color); }
.border-t { border-top: 1px solid var(--border-color); }
.border-dashed { border-style: dashed; }
.rounded { border-radius: var(--radius-md); }

.uppercase { text-transform: uppercase; }
.tracking-wider { letter-spacing: 0.05em; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.text-sm { font-size: 0.875rem; }
.text-center { text-align: center; }

.hidden { display: none; }
.cursor-pointer { cursor: pointer; }
.hover-underline:hover { text-decoration: underline; }
.hover\:border-primary:hover { border-color: var(--primary); }

.val-box {
  transition: all 0.2s;
}
</style>
