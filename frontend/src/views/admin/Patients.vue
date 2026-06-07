<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../services/api'

const patients = ref([])
const filterType = ref('ALL')
const searchQuery = ref('')
const selectedPatient = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

// --- ADD PATIENT MODAL STATE ---
const showAddModal = ref(false)
const isSubmitting = ref(false)
const modalError = ref('')

const newPatient = ref({
  name: '',
  email: '',
  phone: '',
  dob: '',
  age: null,
  gender: '',
  address: ''
})

const closeAddModal = () => {
  showAddModal.value = false
  modalError.value = ''
  newPatient.value = { name: '', email: '', phone: '', dob: '', age: null, gender: '', address: '' }
}

const handleAddPatient = async () => {
  modalError.value = ''
  if (!newPatient.value.name || !newPatient.value.email || !newPatient.value.phone || !newPatient.value.dob) {
    modalError.value = 'Name, email, phone, and DOB are required.'
    return
  }
  isSubmitting.value = true
  try {
    const dateParts = newPatient.value.dob.split('-')
    const formattedPassword = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`
    const payload = {
      name: newPatient.value.name,
      email: newPatient.value.email,
      phone: newPatient.value.phone,
      password: formattedPassword,
      age: newPatient.value.age,
      gender: newPatient.value.gender,
      address: newPatient.value.address
    }
    await api.post('/signup', payload)
    closeAddModal()
    fetchPatients()
  } catch (err) {
    modalError.value = err?.response?.data?.error || 'Failed to create patient.'
  } finally {
    isSubmitting.value = false
  }
}

const formatPatientId = (id) => {
  if (!id) return '-'
  return id.toString()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

const fetchPatients = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (searchQuery.value.trim()) params.name = searchQuery.value.trim()
    const res = await api.get('/admin/patients', { params })
    patients.value = (res.data || []).map((patient) => ({
      ...patient,
      displayId: formatPatientId(patient.id),
      type: (patient.status || 'OPD').toUpperCase(),
      lastVisit: formatDate(patient.created_at)
    }))
  } catch (err) {
    errorMessage.value = err?.response?.data?.error || 'Failed to load patients.'
  } finally {
    isLoading.value = false
  }
}

const filteredPatients = computed(() => {
  let result = [...patients.value]
  if (filterType.value !== 'ALL') {
    result = result.filter((pt) => pt.type === filterType.value)
  }
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.trim().toLowerCase()
    result = result.filter(
      (pt) =>
        String(pt.displayId).toLowerCase().includes(query) ||
        String(pt.name || '').toLowerCase().includes(query)
    )
  }
  return result
})

const counts = computed(() => ({
  all: patients.value.length,
  opd: patients.value.filter(p => p.type === 'OPD').length,
  ipd: patients.value.filter(p => p.type === 'IPD').length,
  discharged: patients.value.filter(p => p.type === 'DISCHARGED').length,
}))

const avatarColors = ['av-green', 'av-blue', 'av-amber', 'av-rose']
const getAvatarColor = (index) => avatarColors[index % avatarColors.length]
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

const viewPatient = (patient) => {
  selectedPatient.value = patient
}

const closePanel = () => {
  selectedPatient.value = null
}

let searchTimeout = null
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { fetchPatients() }, 300)
})

onMounted(() => { fetchPatients() })
</script>

<template>
  <div class="admin-patients">

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Patients</h1>
        <p class="page-sub">{{ counts.all }} total patients · Last updated just now</p>
      </div>
      <div class="header-actions">
        
        <button class="btn btn-primary" @click="showAddModal = true">
          <svg class="btn-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="8" y1="3" x2="8" y2="13"/><line x1="3" y1="8" x2="13" y2="8"/>
          </svg>
          Add Patient
        </button>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">Total Patients</div>
        <div class="stat-value">{{ counts.all }}</div>
        <div class="stat-delta">All registered</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">OPD</div>
        <div class="stat-value">{{ counts.opd }}</div>
        <div class="stat-delta">Active outpatients</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">IPD</div>
        <div class="stat-value">{{ counts.ipd }}</div>
        <div class="stat-delta">Currently admitted</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Discharged</div>
        <div class="stat-value">{{ counts.discharged }}</div>
        <div class="stat-delta stat-delta--muted">Completed stays</div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="errorMessage" class="error-alert">{{ errorMessage }}</div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="filter-group">
        <button
          class="filter-btn"
          :class="{ active: filterType === 'ALL' }"
          @click="filterType = 'ALL'"
        >All patients</button>
        <button
          class="filter-btn"
          :class="{ active: filterType === 'OPD' }"
          @click="filterType = 'OPD'"
        >OPD</button>
        <button
          class="filter-btn"
          :class="{ active: filterType === 'IPD' }"
          @click="filterType = 'IPD'"
        >IPD</button>
        <button
          class="filter-btn"
          :class="{ active: filterType === 'DISCHARGED' }"
          @click="filterType = 'DISCHARGED'"
        >Discharged</button>
      </div>
      <div class="search-wrap">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="6.5" cy="6.5" r="4.5"/><path d="M10 10l3.5 3.5"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search name or ID..."
        />
      </div>
    </div>

    <!-- Table + Detail Panel -->
    <div class="content-row">
      <div class="table-card" :class="{ 'panel-open': selectedPatient }">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Patient</th>
                <th>Age / Gender</th>
                <th>Type</th>
                <th>Contact</th>
                <th>Last Visit</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="isLoading">
                <td colspan="5" class="empty-cell">
                  <span class="loading-dots">Loading patients</span>
                </td>
              </tr>
              <tr v-else-if="filteredPatients.length === 0">
                <td colspan="5" class="empty-cell">No patients match your filters.</td>
              </tr>
              <tr
                v-else
                v-for="(pt, index) in filteredPatients"
                :key="pt.id"
              >
                <td>
                  <div class="patient-cell">
                    <div class="avatar" :class="getAvatarColor(index)">{{ getInitials(pt.name) }}</div>
                    <div>
                      <div class="patient-name">{{ pt.name }}</div>
                      <div class="patient-id">{{ pt.displayId }}</div>
                    </div>
                  </div>
                </td>
                <td class="text-secondary">{{ pt.age ?? '-' }} yrs &nbsp;·&nbsp; {{ pt.gender || '-' }}</td>
                <td>
                  <span class="badge" :class="{
                    'badge-opd': pt.type === 'OPD',
                    'badge-ipd': pt.type === 'IPD',
                    'badge-dis': pt.type === 'DISCHARGED',
                    'badge-reg': pt.type === 'REGISTERED'
                  }">
                    <span class="badge-dot"></span>{{ pt.type }}
                  </span>
                </td>
                <td class="text-mono text-secondary">{{ pt.phone || '-' }}</td>
                <td class="text-muted">{{ pt.lastVisit }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span class="footer-count">Showing <strong>{{ filteredPatients.length }}</strong> of <strong>{{ patients.length }}</strong> patients</span>
        </div>
      </div>

      <!-- Detail Panel -->
      <transition name="slide">
        <div v-if="selectedPatient" class="detail-panel">
          <div class="panel-header">
            <h2 class="panel-title">Patient Details</h2>
            <button class="close-btn" @click="closePanel">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 1l12 12M13 1L1 13"/>
              </svg>
            </button>
          </div>

          <div class="panel-avatar-row">
            <div class="avatar avatar-lg av-green">{{ getInitials(selectedPatient.name) }}</div>
            <div>
              <div class="panel-patient-name">{{ selectedPatient.name }}</div>
              <div class="panel-patient-id">{{ selectedPatient.displayId }}</div>
            </div>
          </div>

          <div class="panel-section">
            <div class="section-label">Personal Info</div>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-key">Age / Gender</div>
                <div class="info-val">{{ selectedPatient.age ?? '-' }} yrs / {{ selectedPatient.gender || '-' }}</div>
              </div>
              <div class="info-item">
                <div class="info-key">Contact</div>
                <div class="info-val">{{ selectedPatient.phone || '-' }}</div>
              </div>
              <div class="info-item">
                <div class="info-key">Status</div>
                <div class="info-val">
                  <span class="badge" :class="{
                    'badge-opd': selectedPatient.type === 'OPD',
                    'badge-ipd': selectedPatient.type === 'IPD',
                    'badge-dis': selectedPatient.type === 'DISCHARGED'
                  }">
                    <span class="badge-dot"></span>{{ selectedPatient.type }}
                  </span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-key">Last Visit</div>
                <div class="info-val">{{ selectedPatient.lastVisit }}</div>
              </div>
            </div>
          </div>

          <div class="panel-section">
            <div class="section-label">History</div>
            <div class="history-tabs">
              <div class="history-tab active">OPD History</div>
              <div class="history-tab">Prescriptions</div>
              <div class="history-tab">Discharge</div>
            </div>
            <div class="history-empty">History details will load here.</div>
          </div>

          <div class="panel-actions">
            <button class="btn btn-primary flex-1">Save Notes</button>
            <button class="btn btn-ghost flex-1" @click="closePanel">Cancel</button>
          </div>
        </div>
      </transition>
    </div>
  </div>

  <!-- Add Patient Modal -->
  <Teleport to="body">
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Add New Patient</h2>
          <button class="close-btn" @click="closeAddModal">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 1l12 12M13 1L1 13"/>
            </svg>
          </button>
        </div>

        <div v-if="modalError" class="error-alert modal-error">{{ modalError }}</div>

        <form @submit.prevent="handleAddPatient" class="form-grid">
          <div class="input-group">
            <label>Full Name <span class="required">*</span></label>
            <input type="text" v-model="newPatient.name" required class="form-control" placeholder="John Doe" />
          </div>
          <div class="input-group">
            <label>Email <span class="required">*</span></label>
            <input type="email" v-model="newPatient.email" required class="form-control" placeholder="john@example.com" />
          </div>
          <div class="input-group">
            <label>Phone <span class="required">*</span></label>
            <input type="text" v-model="newPatient.phone" required class="form-control" placeholder="9876543210" />
          </div>
          <div class="input-group">
            <label>
              Date of Birth <span class="required">*</span>
              <span class="label-hint">(used as initial password)</span>
            </label>
            <input type="date" v-model="newPatient.dob" required class="form-control" />
          </div>
          <div class="two-col">
            <div class="input-group">
              <label>Age</label>
              <input type="number" v-model="newPatient.age" class="form-control" placeholder="30" />
            </div>
            <div class="input-group">
              <label>Gender</label>
              <select v-model="newPatient.gender" class="form-control">
                <option value="" disabled>Select...</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
          <div class="input-group full-width">
            <label>Address</label>
            <textarea v-model="newPatient.address" rows="2" class="form-control" placeholder="123 Main St..."></textarea>
          </div>
          <div class="modal-actions full-width">
            <button type="submit" class="btn btn-primary flex-1" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : 'Register Patient' }}
            </button>
            <button type="button" class="btn btn-ghost flex-1" @click="closeAddModal" :disabled="isSubmitting">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap');

/* ── Tokens ─────────────────────────────────────────────── */
.admin-patients {
  --green:       #10b981;
  --green-50:    #ecfdf5;
  --green-100:   #d1fae5;
  --green-200:   #a7f3d0;
  --green-600:   #059669;
  --green-700:   #047857;
  --green-800:   #065f46;
  --surface:     #ffffff;
  --bg:          #f6f8f7;
  --border:      #e4eae7;
  --text-1:      #0d1f2d;
  --text-2:      #475569;
  --text-3:      #94a3b8;
  --danger:      #ef4444;
  --radius-sm:   8px;
  --radius-md:   12px;
  --radius-lg:   16px;
  --shadow:      0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  font-family: 'Geist', -apple-system, sans-serif;
  padding: 28px;
  background: var(--bg);
  min-height: 100vh;
  background: #ffffff;
  border-radius: 30px;
}


/* ── Page Header ─────────────────────────────────────────── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.03em;
  line-height: 1;
  margin: 0;
}
.page-sub {
  font-size: 13px;
  color: var(--text-3);
  margin: 5px 0 0;
  font-weight: 400;
}
.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* ── Buttons ─────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: all .15s;
  white-space: nowrap;
}
.btn-ghost {
  background: var(--surface);
  color: var(--text-2);
  border: 1px solid var(--border);
}
.btn-ghost:hover { border-color: #b0c4bb; color: var(--text-1); }
.btn-primary { background: var(--green); color: #fff; }
.btn-primary:hover { background: var(--green-600); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-icon { width: 15px; height: 15px; flex-shrink: 0; }
.flex-1 { flex: 1; }

/* ── Stats Row ───────────────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.04em;
  line-height: 1;
}
.stat-delta {
  font-size: 11px;
  font-weight: 500;
  color: var(--green-600);
  margin-top: 2px;
}
.stat-delta--muted { color: var(--text-3); }

/* ── Error ───────────────────────────────────────────────── */
.error-alert {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: var(--danger);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  font-size: 13px;
  margin-bottom: 16px;
}

/* ── Toolbar ─────────────────────────────────────────────── */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  gap: 12px;
}
.filter-group {
  display: flex;
  gap: 3px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 4px;
}
.filter-btn {
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--text-2);
  font-family: inherit;
  transition: all .15s;
  white-space: nowrap;
}
.filter-btn.active {
  background: var(--green-50);
  color: var(--green-800);
  font-weight: 600;
}
.filter-btn:hover:not(.active) {
  background: var(--bg);
  color: var(--text-1);
}
.search-wrap {
  position: relative;
  flex: 1;
  max-width: 280px;
}
.search-icon {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-3);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 8px 12px 8px 34px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: inherit;
  color: var(--text-1);
  background: var(--surface);
  outline: none;
  transition: border-color .15s;
}
.search-input:focus {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}
.search-input::placeholder { color: var(--text-3); }

/* ── Content Row ─────────────────────────────────────────── */
.content-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

/* ── Table Card ──────────────────────────────────────────── */
.table-card {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-width: 0;
  transition: all .3s ease;
}
.table-wrap { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
thead tr { border-bottom: 1px solid var(--border); }
th {
  padding: 11px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
  background: var(--bg);
}
td {
  padding: 13px 16px;
  color: var(--text-1);
  vertical-align: middle;
  border-bottom: 1px solid var(--border);
}
tbody tr:last-child td { border-bottom: none; }
tbody tr {
  transition: background .1s;
}
tbody tr:hover { background: #f0faf6; }
tbody tr.selected { background: var(--green-50); }

.text-secondary { color: var(--text-2); }
.text-muted { color: var(--text-3); }
.text-mono { font-family: monospace; font-size: 12px; }

/* ── Patient Cell ────────────────────────────────────────── */
.patient-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}
.avatar-lg { width: 44px; height: 44px; font-size: 14px; }
.av-green  { background: var(--green-100); color: var(--green-800); }
.av-blue   { background: #dbeafe; color: #1e40af; }
.av-amber  { background: #fef3c7; color: #92400e; }
.av-rose   { background: #ffe4e6; color: #9f1239; }

.patient-name  { font-weight: 600; color: var(--text-1); font-size: 13px; line-height: 1.2; }
.patient-id    { font-size: 11px; color: var(--text-3); font-family: monospace; margin-top: 1px; }

/* ── Badges ──────────────────────────────────────────────── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.badge-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.badge-opd { background: #dbeafe; color: #1e40af; }
.badge-opd .badge-dot { background: #3b82f6; }
.badge-ipd { background: var(--green-100); color: var(--green-800); }
.badge-ipd .badge-dot { background: var(--green); }
.badge-dis { background: #f1f5f9; color: #475569; }
.badge-dis .badge-dot { background: #94a3b8; }
.badge-reg { background: #fef9c3; color: #854d0e; }
.badge-reg .badge-dot { background: #ca8a04; }

/* ── Action Button ───────────────────────────────────────── */
.action-btn {
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-2);
  font-family: inherit;
  transition: all .15s;
}
.action-btn:hover {
  border-color: #b0c4bb;
  color: var(--text-1);
  background: var(--green-50);
}

/* ── Empty / Loading ─────────────────────────────────────── */
.empty-cell {
  text-align: center;
  padding: 52px;
  color: var(--text-3);
  font-size: 14px;
}

/* ── Table Footer ────────────────────────────────────────── */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 11px 16px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}
.footer-count { font-size: 12px; color: var(--text-3); }
.footer-count strong { color: var(--text-1); font-weight: 600; }

/* ── Detail Panel ────────────────────────────────────────── */
.detail-panel {
  width: 320px;
  flex-shrink: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  position: sticky;
  top: 24px;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}
.panel-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1);
  margin: 0;
  letter-spacing: -0.02em;
}
.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all .15s;
}
.close-btn:hover { background: var(--bg); color: var(--text-1); }

.panel-avatar-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.panel-patient-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.02em;
}
.panel-patient-id {
  font-size: 11px;
  color: var(--text-3);
  font-family: monospace;
  margin-top: 2px;
}

.panel-section { margin-bottom: 18px; }
.section-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}


.info-key {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 2px;
}
.info-val {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-1);
}

.history-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 10px;
}
.history-tab {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-3);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all .15s;
  white-space: nowrap;
}
.history-tab.active {
  color: var(--green-800);
  border-bottom-color: var(--green);
}
.history-tab:hover:not(.active) { color: var(--text-1); }

.history-empty {
  text-align: center;
  padding: 24px;
  font-size: 12px;
  color: var(--text-3);
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px dashed var(--border);
}

.panel-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

/* ── Slide Transition ────────────────────────────────────── */
.slide-enter-active, .slide-leave-active { transition: all .3s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateX(20px); }

/* ── Modal ───────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  backdrop-filter: blur(3px);
}
.modal-content {
  width: 100%;
  max-width: 480px;
  background: var(--surface);
  padding: 24px;
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  border: 1px solid var(--border);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.02em;
  margin: 0;
}
.modal-error { margin-top: 0; margin-bottom: 16px; }

/* ── Form ────────────────────────────────────────────────── */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.input-group { display: flex; flex-direction: column; gap: 5px; }
.input-group label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2);
  display: flex;
  align-items: center;
  gap: 4px;
}
.required { color: var(--danger); }
.label-hint { font-size: 11px; color: var(--text-3); font-weight: 400; }

.form-control {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #c8d5d0;
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-1);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color .15s;
  box-sizing: border-box;
}
.form-control:focus {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(16,185,129,0.1);
  background: var(--surface);
}
.form-control::placeholder { color: var(--text-3); }
select.form-control { cursor: pointer; }
textarea.form-control { resize: vertical; }

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.full-width { width: 100%; }

.modal-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.modal-content .btn-primary {
  background: #12a23f;
  color: #ffffff;
  border-radius: 20px;
}
.modal-content .btn-primary:hover {
  background: #0bb541;
}
</style>