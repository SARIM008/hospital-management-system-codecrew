<template>
  <div class="active-ward-dashboard w-full">
    
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1>Active Ward (IPD)</h1>
        <p class="text-sm text-muted">Manage currently admitted patients and their treatments.</p>
      </div>
    </div>

    <div class="card p-0 mb-8">
      <table class="table w-full">
        <thead>
          <tr>
            <th>Admit ID</th>
            <th>Patient Name</th>
            <th>Admit Date</th>
            <th>Provisional Diagnosis</th>
            <th class="text-center">Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="6" class="text-center text-muted py-4">Loading active ward...</td>
          </tr>
          <tr v-else-if="activeAdmissions.length === 0">
            <td colspan="6" class="text-center text-muted py-4">No patients currently admitted.</td>
          </tr>
          <tr v-else v-for="admin in activeAdmissions" :key="admin.id">
            <td class="font-mono text-sm text-muted">AD-{{ String(admin.id).padStart(3, '0') }}</td>
            <td class="font-medium text-main">{{ admin.patient_name || 'Unknown' }}</td>
            <td>{{ formatDate(admin.admission_date) }}</td>
            <td>{{ admin.provisional_diagnosis || '-' }}</td>
            <td class="text-center"><span class="badge badge-pending">Admitted</span></td>
            <td>
              <button class="btn btn-sm btn-outline text-primary" @click="openActionModal(admin)">
                Manage
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAdmitModal" class="modal-overlay" @click.self="closeAdmitModal">
      <div class="modal-content card">
        <div class="flex justify-between items-center border-b border-color pb-4 mb-4">
          <h2 class="text-xl">Admit Patient to IPD</h2>
          <button class="btn btn-sm text-muted" @click="closeAdmitModal">✕</button>
        </div>

        <div v-if="modalError" class="error-alert mb-4">{{ modalError }}</div>

        <form v-if="!admitTargetPatient" @submit.prevent="searchPatientForAdmit">
          <p class="text-sm text-muted mb-4">Enter registered patient's phone number to admit.</p>
          <div class="form-group mb-4">
            <input type="text" v-model="searchPhone" required class="form-control" placeholder="Phone Number...">
          </div>
          <button type="submit" class="btn btn-primary w-full" :disabled="isSubmitting">Search Patient</button>
        </form>

        <form v-else @submit.prevent="submitAdmission">
          <div class="bg-secondary-light p-3 rounded text-sm text-secondary border border-secondary mb-4">
            <strong>Patient Found:</strong> {{ admitTargetPatient.name }} ({{ admitTargetPatient.phone }})
          </div>
          
          <div class="form-group mb-4">
            <label class="text-xs">Provisional Diagnosis *</label>
            <input type="text" v-model="admitDiagnosis" required class="form-control" placeholder="e.g. Severe Dengue, Appendicitis">
          </div>
          
          <div class="form-group mb-4">
            <label class="text-xs">Admission Date *</label>
            <input type="date" v-model="admitDate" required class="form-control">
          </div>

          <div class="flex gap-4 mt-4">
            <button type="submit" class="btn btn-primary flex-1" :disabled="isSubmitting">
              {{ isSubmitting ? 'Admitting...' : 'Confirm Admission' }}
            </button>
            <button type="button" class="btn btn-outline flex-1" @click="closeAdmitModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>


    <div v-if="showActionModal" class="modal-overlay" @click.self="closeActionModal">
      <div class="modal-content action-modal card p-0 flex flex-col">
        
        <div class="p-4 border-b border-color flex justify-between items-center bg-background">
          <div>
            <h2 class="text-xl text-primary">Ward Chart: {{ selectedAdmission?.patient_name }}</h2>
            <p class="text-xs text-muted mt-1">AD-{{ String(selectedAdmission?.id).padStart(3, '0') }} | Admitted: {{ formatDate(selectedAdmission?.admission_date) }}</p>
          </div>
          <button class="btn btn-sm text-muted" @click="closeActionModal">✕</button>
        </div>

        <div class="flex flex-1 overflow-hidden">
          
          <div class="w-1/4 border-r border-color bg-surface p-2 flex flex-col gap-1">
            <button class="tab-btn" :class="{'active': activeTab === 'overview'}" @click="activeTab = 'overview'">Overview</button>
            <button class="tab-btn" :class="{'active': activeTab === 'vitals'}" @click="activeTab = 'vitals'">Vitals</button>
            <button class="tab-btn" :class="{'active': activeTab === 'notes'}" @click="activeTab = 'notes'">Progress Notes</button>
            <button class="tab-btn" :class="{'active': activeTab === 'meds'}" @click="activeTab = 'meds'">Medications</button>
          </div>

          <div class="w-3/4 p-6 overflow-y-auto bg-background">
            <div v-if="isFetchingDetails" class="text-center text-muted mt-10">Loading chart data...</div>
            
            <template v-else>
              <div v-if="activeTab === 'overview'" class="fade-in">
                <h3 class="font-bold mb-4">Admission Overview</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div class="card bg-surface p-4 border border-color">
                    <p class="text-xs text-muted mb-1">PROVISIONAL DIAGNOSIS</p>
                    <p class="font-medium text-main">{{ admissionDetails?.admission?.provisional_diagnosis || '-' }}</p>
                  </div>
                  <div class="card bg-surface p-4 border border-color">
                    <p class="text-xs text-muted mb-1">CURRENT STATUS</p>
                    <span class="badge badge-pending">{{ admissionDetails?.admission?.status }}</span>
                  </div>
                </div>
              </div>

              <div v-if="activeTab === 'vitals'" class="fade-in">
                <h3 class="font-bold mb-4">Log Vitals</h3>
                <form @submit.prevent="submitVitals" class="card bg-surface p-4 border border-color mb-6">
                  <div class="grid grid-cols-4 gap-4 mb-4">
                    <div>
                      <label class="text-xs">BP (Sys/Dia)</label>
                      <div class="flex gap-1">
                        <input type="number" v-model="vitalForm.systolic_bp" class="form-control" placeholder="120" required>
                        <span class="mt-2">/</span>
                        <input type="number" v-model="vitalForm.diastolic_bp" class="form-control" placeholder="80" required>
                      </div>
                    </div>
                    <div>
                      <label class="text-xs">Pulse (bpm)</label>
                      <input type="number" v-model="vitalForm.pulse" class="form-control" placeholder="72">
                    </div>
                    <div>
                      <label class="text-xs">SpO2 (%)</label>
                      <input type="number" v-model="vitalForm.spo2" class="form-control" placeholder="98">
                    </div>
                    <div>
                      <label class="text-xs">Temp (°C)</label>
                      <input type="text" v-model="vitalForm.temperature" class="form-control" placeholder="37.5">
                    </div>
                  </div>
                  <button type="submit" class="btn btn-primary btn-sm" :disabled="isSubmitting">Save Vitals</button>
                </form>

                <h3 class="font-bold mb-2 text-sm text-muted">Vitals History</h3>
                <table class="table text-sm bg-surface">
                  <thead><tr><th>Date</th><th>BP</th><th>Pulse</th><th>SpO2</th><th>Temp</th></tr></thead>
                  <tbody>
                    <tr v-for="v in admissionDetails?.vitals" :key="v.id">
                      <td>{{ formatDate(v.record_date) }}</td>
                      <td>{{ v.systolic_bp }}/{{ v.diastolic_bp }}</td>
                      <td>{{ v.pulse }}</td>
                      <td>{{ v.spo2 }}%</td>
                      <td>{{ v.temperature }}</td>
                    </tr>
                    <tr v-if="!admissionDetails?.vitals?.length"><td colspan="5" class="text-center text-muted">No vitals recorded yet.</td></tr>
                  </tbody>
                </table>
              </div>

              <div v-if="activeTab === 'notes'" class="fade-in">
                <h3 class="font-bold mb-4">Add Progress Note</h3>
                <form @submit.prevent="submitNote" class="mb-6">
                  <textarea v-model="noteForm.text" class="form-control mb-2" rows="3" placeholder="Shift handover notes, patient updates..." required></textarea>
                  <button type="submit" class="btn btn-primary btn-sm" :disabled="isSubmitting">Post Note</button>
                </form>

                <h3 class="font-bold mb-2 text-sm text-muted">Note Feed</h3>
                <div class="flex flex-col gap-3">
                  <div v-for="note in admissionDetails?.progress_notes" :key="note.id" class="card bg-surface p-3 border border-color text-sm">
                    <div class="flex justify-between text-xs text-muted mb-2 border-b border-color pb-1">
                      <span>{{ formatDate(note.note_date) }}</span>
                    </div>
                    <p>{{ note.note_text }}</p>
                  </div>
                  <div v-if="!admissionDetails?.progress_notes?.length" class="text-center text-muted text-sm mt-4">No notes recorded yet.</div>
                </div>
              </div>

              <div v-if="activeTab === 'meds'" class="fade-in">
                <h3 class="font-bold mb-4">Log Medication Administration</h3>
                <form @submit.prevent="submitMedication" class="card bg-surface p-4 border border-color mb-6">
                  <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="col-span-2">
                      <label class="text-xs">Medicine *</label>
                      <select v-model="medForm.medicine_id" required class="form-control">
                        <option value="" disabled>Select Medicine...</option>
                        <option v-for="med in availableMedicines" :key="med.id" :value="med.id">
                          {{ med.medicine_name }} ({{ med.strength }} - {{ med.type }})
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="text-xs">Dosage *</label>
                      <input type="text" v-model="medForm.dosage" class="form-control" placeholder="e.g. 1 Tab, 5ml" required>
                    </div>
                    <div>
                      <label class="text-xs">Frequency *</label>
                      <select v-model="medForm.frequency" class="form-control" required>
                        <option value="OD (Once)">OD (Once a day)</option>
                        <option value="BD (Twice)">BD (Twice a day)</option>
                        <option value="TDS (Thrice)">TDS (Thrice a day)</option>
                        <option value="SOS (As needed)">SOS (As needed)</option>
                      </select>
                    </div>
                    <div>
                      <label class="text-xs">Start Date *</label>
                      <input type="date" v-model="medForm.start_date" class="form-control" required>
                    </div>
                  </div>
                  <button type="submit" class="btn btn-primary btn-sm" :disabled="isSubmitting">Add Medication</button>
                </form>

                <h3 class="font-bold mb-2 text-sm text-muted">Active Medication Chart</h3>
                <table class="table text-sm bg-surface">
                  <thead><tr><th>Medicine</th><th>Dosage</th><th>Freq</th><th>Start Date</th></tr></thead>
                  <tbody>
                    <tr v-for="m in admissionMeds" :key="m.id">
                      <td class="font-medium text-primary">{{ m.medicine_name }}</td>
                      <td>{{ m.dosage }}</td>
                      <td>{{ m.frequency }}</td>
                      <td>{{ formatDate(m.start_date) }}</td>
                    </tr>
                    <tr v-if="!admissionMeds.length"><td colspan="4" class="text-center text-muted">No medications logged.</td></tr>
                  </tbody>
                </table>
              </div>

              <div v-if="activeTab === 'discharge'" class="fade-in">
                <h3 class="font-bold mb-4 text-danger">Process Patient Discharge</h3>
                <div class="bg-secondary-light border border-secondary text-secondary p-3 rounded text-sm mb-4">
                  <strong>Warning:</strong> Discharging a patient will finalize their IPD stay and remove them from the Active Ward.
                </div>
                
                <form @submit.prevent="submitDischarge" class="flex flex-col gap-4">
                  <div>
                    <label class="text-xs font-bold text-main">Final Diagnosis *</label>
                    <input type="text" v-model="dischargeForm.final_diagnosis" required class="form-control">
                  </div>
                  <div>
                    <label class="text-xs font-bold text-main">Treatment Summary</label>
                    <textarea v-model="dischargeForm.treatment_summary" rows="3" class="form-control" placeholder="Brief summary of hospital stay..."></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="text-xs font-bold text-main">Discharge Date *</label>
                      <input type="date" v-model="dischargeForm.discharge_date" required class="form-control">
                    </div>
                    <div>
                      <label class="text-xs font-bold text-main">Medicine Days Prescribed</label>
                      <input type="number" v-model="dischargeForm.medicine_days" class="form-control" placeholder="e.g. 5">
                    </div>
                  </div>
                  <div>
                    <label class="text-xs font-bold text-main">Diet & Follow-up Instructions</label>
                    <textarea v-model="dischargeForm.instructions" rows="2" class="form-control" placeholder="Rest for 3 days, drink fluids..."></textarea>
                  </div>
                  
                  <button type="submit" class="btn btn-danger mt-4 py-2" :disabled="isSubmitting">
                    {{ isSubmitting ? 'Processing...' : 'Confirm Discharge' }}
                  </button>
                </form>
              </div>

            </template>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

// --- GLOBAL STATE ---
const isLoading = ref(false)
const isSubmitting = ref(false)
const modalError = ref('')
const activeAdmissions = ref([])

// Helper: Today's date in YYYY-MM-DD
const getTodayDate = () => new Date().toISOString().split('T')[0]

// Helper: Format date for display
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

// --- FETCH ACTIVE WARD ---
const fetchActiveAdmissions = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/admissions', { params: { status: 'admitted' } })
    // We attach patient_name safely, depending on how serialize_admission sends it
    activeAdmissions.value = res.data.map(admin => ({
      ...admin,
      patient_name: admin.patient?.name || admin.patient_name || 'View Chart' 
    }))
  } catch (err) {
    console.error("Failed to load active ward", err)
  } finally {
    isLoading.value = false
  }
}

// --- 1. DIRECT ADMIT STATE & LOGIC ---
const showAdmitModal = ref(false)
const searchPhone = ref('')
const admitTargetPatient = ref(null)
const admitDiagnosis = ref('')
const admitDate = ref(getTodayDate())

const closeAdmitModal = () => {
  showAdmitModal.value = false
  searchPhone.value = ''
  admitTargetPatient.value = null
  admitDiagnosis.value = ''
  modalError.value = ''
}

const searchPatientForAdmit = async () => {
  if (!searchPhone.value) return
  isSubmitting.value = true
  modalError.value = ''
  try {
    const res = await api.get('/admin/patients')
    const found = res.data.find(p => p.phone === searchPhone.value)
    if (found) {
      admitTargetPatient.value = found
    } else {
      modalError.value = "Patient not found. Register them in the Patients tab first."
    }
  } catch (err) {
    modalError.value = "Failed to search patient database."
  } finally {
    isSubmitting.value = false
  }
}

const submitAdmission = async () => {
  isSubmitting.value = true
  modalError.value = ''
  try {
    await api.post('/admissions', {
      patient_id: admitTargetPatient.value.id,
      admission_date: admitDate.value,
      provisional_diagnosis: admitDiagnosis.value,
      status: 'admitted'
    })
    closeAdmitModal()
    fetchActiveAdmissions() // Refresh table
  } catch (err) {
    modalError.value = err?.response?.data?.error || "Failed to admit patient."
  } finally {
    isSubmitting.value = false
  }
}


// --- 2. ACTION MODAL STATE & LOGIC ---
const showActionModal = ref(false)
const activeTab = ref('overview')
const selectedAdmission = ref(null)
const admissionDetails = ref(null)
const admissionMeds = ref([])
const isFetchingDetails = ref(false)
const availableMedicines = ref([])

// Forms for tabs
const vitalForm = ref({ systolic_bp: '', diastolic_bp: '', pulse: '', spo2: '', temperature: '' })
const noteForm = ref({ text: '' })
const medForm = ref({ medicine_id: '', dosage: '', frequency: 'BD (Twice)', start_date: getTodayDate() })
const dischargeForm = ref({ final_diagnosis: '', treatment_summary: '', discharge_date: getTodayDate(), medicine_days: null, instructions: '' })

const closeActionModal = () => {
  showActionModal.value = false
  selectedAdmission.value = null
  admissionDetails.value = null
  admissionMeds.value = []
  activeTab.value = 'overview'
}

const fetchMedicines = async () => {
  try {
    const res = await api.get('/medicines')
    availableMedicines.value = res.data
  } catch (err) { console.error("Failed to load medicines", err) }
}

const openActionModal = async (admission) => {
  selectedAdmission.value = admission
  showActionModal.value = true
  isFetchingDetails.value = true
  activeTab.value = 'overview'
  
  try {
    // Fetch details AND medications concurrently
    const [detailsRes, medsRes] = await Promise.all([
      api.get(`/admissions/${admission.id}`),
      api.get(`/admissions/${admission.id}/medications`)
    ])
    admissionDetails.value = detailsRes.data
    admissionMeds.value = medsRes.data
  } catch (err) {
    console.error("Failed to fetch full chart data", err)
  } finally {
    isFetchingDetails.value = false
  }
}

// Tab 2 Submit
const submitVitals = async () => {
  isSubmitting.value = true
  try {
    await api.post(`/admissions/${selectedAdmission.value.id}/vitals`, {
      record_date: getTodayDate(),
      ...vitalForm.value
    })
    // Refresh modal data
    const res = await api.get(`/admissions/${selectedAdmission.value.id}`)
    admissionDetails.value = res.data
    // Clear form
    vitalForm.value = { systolic_bp: '', diastolic_bp: '', pulse: '', spo2: '', temperature: '' }
  } catch (err) { alert("Failed to save vitals") } finally { isSubmitting.value = false }
}

// Tab 3 Submit
const submitNote = async () => {
  isSubmitting.value = true
  try {
    await api.post(`/admissions/${selectedAdmission.value.id}/progress-notes`, {
      note_date: getTodayDate(),
      note_text: noteForm.value.text
    })
    const res = await api.get(`/admissions/${selectedAdmission.value.id}`)
    admissionDetails.value = res.data
    noteForm.value.text = ''
  } catch (err) { alert("Failed to post note") } finally { isSubmitting.value = false }
}

// Tab 4 Submit
const submitMedication = async () => {
  isSubmitting.value = true
  try {
    await api.post(`/admissions/${selectedAdmission.value.id}/medications`, medForm.value)
    const res = await api.get(`/admissions/${selectedAdmission.value.id}/medications`)
    admissionMeds.value = res.data
    medForm.value = { medicine_id: '', dosage: '', frequency: 'BD (Twice)', start_date: getTodayDate() }
  } catch (err) { alert("Failed to log medication") } finally { isSubmitting.value = false }
}

// Tab 5 Submit
const submitDischarge = async () => {
  isSubmitting.value = true
  try {
    await api.post(`/admissions/${selectedAdmission.value.id}/discharge`, dischargeForm.value)
    alert("Patient successfully discharged!")
    closeActionModal()
    fetchActiveAdmissions() // Removes them from active ward table
  } catch (err) { alert("Failed to discharge patient") } finally { isSubmitting.value = false }
}

onMounted(() => {
  fetchActiveAdmissions()
  fetchMedicines() // Load dropdown data once
})
</script>

<style scoped>
/* Core Spacing & Fonts */
.active-ward-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 0;
}

.w-full { width: 100%; }
.w-1\/4 { width: 25%; }
.w-3\/4 { width: 75%; }
.mb-8 { margin-bottom: 2rem; }
.mb-6 { margin-bottom: 1.5rem; margin-left: 10px;}
.mb-4 { margin-bottom: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-1 { margin-bottom: 0.25rem; }
.mt-4 { margin-top: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-1 { margin-top: 0.25rem; }
.mt-10 { margin-top: 2.5rem; }
.mt-auto { margin-top: auto; }
.p-0 { padding: 0; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
.pb-4 { padding-bottom: 1rem; }
.pb-1 { padding-bottom: 0.25rem; }
.flex-1 { flex: 1; }
.overflow-hidden { overflow: hidden; }
.overflow-y-auto { overflow-y: auto; }

.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); display: grid; }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); display: grid; }
.col-span-2 { grid-column: span 2 / span 2; }

/* Colors */
.text-main { color: var(--text-main); }
.text-muted { color: var(--text-muted); }
.text-primary { color: var(--primary); }
.text-danger { color: var(--danger); }
.text-secondary { color: var(--secondary); }
.text-white { color: #fff; }
.bg-surface { background-color: var(--surface); }
.bg-background { background-color: var(--background); }
.bg-danger { background-color: var(--danger); }
.bg-secondary-light { background-color: #f0fdf4; }
.border-secondary { border-color: #bbf7d0; }
.border-color { border-color: var(--border-color); }

.border { border-width: 1px; border-style: solid; }
.border-b { border-bottom-width: 1px; border-style: solid; }
.border-r { border-right-width: 1px; border-style: solid; }
.rounded { border-radius: var(--radius-md); }

/* Typography */
.text-xl { font-size: 1.25rem; font-weight: 600; }
.text-sm { font-size: 0.875rem; }
.text-xs { font-size: 0.75rem; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.font-mono { font-family: monospace; }
.text-center { text-align: center; }

/* Modal & UI Elements */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.5); backdrop-filter: blur(2px);
  display: flex; justify-content: center; align-items: center; z-index: 50; 
}
.modal-content {
  width: 100%; max-width: 500px;
  background-color: var(--surface); padding: 1.5rem;
  border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);
}
.action-modal {
  max-width: 900px; /* Much wider for the split view */
  height: 80vh; /* Fixed height so tabs scroll internally */
}

.form-control {
  width: 100%; padding: 0.5rem 0.75rem; border: 1px solid var(--border-color);
  border-radius: var(--radius-sm); background-color: var(--background);
  color: var(--text-main); margin-top: 0.25rem;
}
.form-control:focus { outline: none; border-color: var(--primary); }

.error-alert {
  color: var(--danger); background-color: #fee2e2; padding: 0.75rem;
  border-radius: var(--radius-sm); border: 1px solid #f87171;
}

.badge-pending { background-color: #fef08a; color: #854d0e; }

/* Custom Tab Buttons */
.tab-btn {
  width: 100%; text-align: left; padding: 0.75rem 1rem;
  border-radius: var(--radius-sm); color: var(--text-muted);
  font-weight: 500; transition: all 0.2s; border: none; background: transparent; cursor: pointer;
}
.tab-btn:hover { background-color: var(--background); color: var(--text-main); }
.tab-btn.active { background-color: var(--primary-light); color: var(--primary); font-weight: 600; border-right: 3px solid var(--primary); border-top-right-radius: 0; border-bottom-right-radius: 0;}

/* Animations */
.fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>