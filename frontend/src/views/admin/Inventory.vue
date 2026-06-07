<template>
  <div class="admin-inventory" style = "background:#ffffff; border-radius:30px;padding: 20px; ">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1>Inventory Management</h1>
        <p class="text-sm text-muted">Manage pharmacy stock, track expiry dates, and add new medicines.</p>
      </div>
      <div class="flex gap-4">
        
        <button class="btn btn-primary" @click="showAddModal = true">+ Add Medicine/Stock</button>
      </div>
    </div>

    <div class="card p-0 overflow-hidden mb-8">
      <div class="p-4 border-b border-color flex justify-between items-center bg-background flex-wrap gap-4">
        <div class="flex gap-2">
          <button class="btn btn-sm" :class="filterType === 'ALL' ? 'btn-secondary' : 'btn-outline'" @click="filterType = 'ALL'">All Stock</button>
          <button class="btn btn-sm" :class="filterType === 'LOW' ? 'btn-danger' : 'btn-outline text-danger'" @click="filterType = 'LOW'">Low Stock Alerts</button>
          <button class="btn btn-sm" :class="filterType === 'EXPIRING' ? 'btn-secondary' : 'btn-outline'" @click="filterType = 'EXPIRING'">Expiring &lt;= 30 Days</button>
        </div>
        <input type="text" v-model="searchQuery" class="form-control" style="width: 250px; margin: 0;" placeholder="Search item name or ID..." />
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>Item / Medicine</th>
            <th>Stock QTY</th>
            <th>Status Indicator</th>
            <th>Expiry Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="4" class="text-center text-muted py-4">Loading pharmacy inventory...</td>
          </tr>
          <tr v-else-if="filteredInventory.length === 0">
            <td colspan="4" class="text-center text-muted py-4">No inventory items matched your search.</td>
          </tr>
          <tr v-else v-for="item in filteredInventory" :key="item.id">
            <td>
              <div class="font-medium text-main">{{ item.medicine_name }} {{ item.strength }}</div>
              <div class="font-mono text-xs text-muted mt-1">MED-{{ String(item.id).padStart(3, '0') }} | {{ item.type }}</div>
            </td>
            <td class="font-medium text-lg" :class="{'text-danger': item.status === 'Critical'}">{{ item.qty }}</td>
            <td>
              <span class="badge" 
                :class="{ 
                  'badge-success': item.status === 'Healthy',
                  'badge-pending': item.status === 'Low',
                  'badge-danger': item.status === 'Critical'
                }">
                {{ item.status }}
              </span>
            </td>
            <td>
              <div class="flex items-center gap-2">
                <span :class="{'text-danger font-medium': item.isExpiringSoon}">{{ item.expiry }}</span>
                 <span v-if="item.isExpiringSoon" class="text-danger flex items-center" title="Expiring within 30 days">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content card">
        <div class="flex justify-between items-center border-b border-color pb-4 mb-4">
          <h2 class="text-xl">Add New Medicine</h2>
          <button class="btn btn-sm text-muted" @click="closeModal">✕</button>
        </div>

        <form @submit.prevent="submitMedicine" class="flex flex-col gap-4">
          <div class="bg-primary-light text-primary p-3 rounded text-sm border border-primary mb-2">
            Adding a medicine here makes it instantly available for Doctors to prescribe and Nurses to administer in the Active Ward.
          </div>
          
          <div>
            <label class="text-xs font-bold">Medicine Name *</label>
            <input type="text" v-model="newMedForm.medicine_name" required class="form-control" placeholder="e.g. Paracetamol">
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-bold">Strength</label>
              <input type="text" v-model="newMedForm.strength" class="form-control" placeholder="e.g. 500mg">
            </div>
            <div>
              <label class="text-xs font-bold">Category / Type *</label>
              <select v-model="newMedForm.type" class="form-control" required>
                <option value="Tablet">Tablet</option>
                <option value="Capsule">Capsule</option>
                <option value="Syrup">Syrup</option>
                <option value="Injection">Injection</option>
                <option value="IV Fluid">IV Fluid</option>
                <option value="Ointment">Ointment</option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-xs font-bold">Dispensing Unit *</label>
            <select v-model="newMedForm.unit" class="form-control" required>
              <option value="Strip">Strip (10/15 tabs)</option>
              <option value="Bottle">Bottle</option>
              <option value="Vial">Vial / Ampoule</option>
              <option value="Tube">Tube</option>
            </select>
          </div>

          <div class="flex gap-4 mt-4">
            <button type="submit" class="btn btn-primary flex-1" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : 'Add Medicine to Database' }}
            </button>
            <button type="button" class="btn btn-outline flex-1" @click="closeModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

// --- STATE ---
const rawInventory = ref([])
const isLoading = ref(false)
const filterType = ref('ALL') // 'ALL', 'LOW', 'EXPIRING'
const searchQuery = ref('')

// Modal State
const showAddModal = ref(false)
const isSubmitting = ref(false)
const newMedForm = ref({ medicine_name: '', type: 'Tablet', strength: '', unit: 'Strip' })

// --- MOCK DATA GENERATOR ---
// This creates consistent fake stock/expiry data based on the real DB ID
const applyMockInventoryData = (medicine) => {
  // 1. Generate consistent pseudo-random stock between 0 and 200
  const baseStock = (medicine.id * 83) % 200; 
  
  // 2. Determine Status
  let status = 'Healthy';
  if (baseStock === 0 || baseStock < 10) status = 'Critical';
  else if (baseStock < 40) status = 'Low';

  // 3. Generate Expiry Date
  // Some will expire very soon to trigger the UI alert, others far in the future
  const monthsToAdd = (medicine.id * 17) % 36; // 0 to 36 months ahead
  const expiryDate = new Date();
  expiryDate.setMonth(expiryDate.getMonth() + monthsToAdd);
  
  const isExpiringSoon = monthsToAdd <= 1; // Expiring this month or next
  const formattedExpiry = expiryDate.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });

  return {
    ...medicine,
    qty: baseStock,
    status: status,
    expiry: formattedExpiry,
    isExpiringSoon: isExpiringSoon
  }
}

// --- FETCH DATA ---
const fetchInventory = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/medicines')
    // Map the real DB data through our mock function to add QTY and Expiry
    rawInventory.value = res.data.map(applyMockInventoryData)
  } catch (err) {
    console.error("Failed to load inventory", err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchInventory()
})

// --- FILTER & SEARCH COMPUTED PROPERTY ---
const filteredInventory = computed(() => {
  let result = rawInventory.value

  // Apply Top Filters
  if (filterType.value === 'LOW') {
    result = result.filter(item => item.status === 'Low' || item.status === 'Critical')
  } else if (filterType.value === 'EXPIRING') {
    result = result.filter(item => item.isExpiringSoon)
  }

  // Apply Search Bar
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(item => 
      item.medicine_name?.toLowerCase().includes(q) || 
      String(item.id).includes(q)
    )
  }

  return result
})

// --- MODAL LOGIC ---
const closeModal = () => {
  showAddModal.value = false
  newMedForm.value = { medicine_name: '', type: 'Tablet', strength: '', unit: 'Strip' }
}

const submitMedicine = async () => {
  isSubmitting.value = true
  try {
    await api.post('/medicines', newMedForm.value)
    alert('Medicine successfully added to inventory!')
    closeModal()
    fetchInventory() // Refresh the table
  } catch (err) {
    alert(err?.response?.data?.error || "Failed to add medicine")
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.mb-8 { margin-bottom: 2rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mt-1 { margin-top: 0.25rem; }
.p-0 { padding: 0; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.overflow-hidden { overflow: hidden; }


.admin-inventor{
  background: #ffffff;
  border-radius: 30px;
}
.flex-wrap { flex-wrap: wrap; }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); display: grid; }
.col-span-2 { grid-column: span 2 / span 2; }

.border-b { border-bottom: 1px solid var(--border-color); }
.border { border: 1px solid var(--border-color); }
.rounded { border-radius: var(--radius-md); }

.bg-background { background-color: var(--background); }
.bg-surface { background-color: var(--surface); }
.bg-primary-light { background-color: var(--primary-light); }

.border-danger { border-color: var(--danger); }
.border-primary { border-color: var(--primary); }

.text-danger { color: var(--danger); }
.text-primary { color: var(--primary); }
.text-muted { color: var(--text-muted); }
.text-main { color: var(--text-main); }
.text-center { text-align: center; }

.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; }
.text-xs { font-size: 0.75rem; }
.text-sm { font-size: 0.875rem; }
.text-lg { font-size: 1.125rem; }

.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 500;}
.hover-underline:hover { text-decoration: underline; }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 50; backdrop-filter: blur(2px); }
.modal-content { width: 100%; max-width: 500px; background-color: var(--surface); padding: 1.5rem; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.form-control { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background-color: var(--background); color: var(--text-main); margin-top: 0.25rem; }
.form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1); }

/* Status Badges */
.badge-success { background-color: #dcfce7; color: #166534; }
.badge-pending { background-color: #fef08a; color: #854d0e; }
.badge-danger { background-color: #fee2e2; color: #991b1b; }
</style>