<script setup>
import { reactive, ref, computed } from 'vue'

const isSubmitting = ref(false)
const showPrint = ref(false)

const searchInput = ref('')
const selectedPatient = ref(null)
const searched = ref(false)

// Line Items array (dynamic)
const billItems = ref([
  { id: 1, item: '', category: 'Consultation', qty: 1, rate: null }
])

const handleSearch = () => {
  searched.value = true
  if (searchInput.value.length > 2) {
    // Mock user find
    setTimeout(() => {
      selectedPatient.value = { id: 'PT-001', name: 'Rahul Sharma', age: 45, type: 'OPD' }
      billItems.value[0].item = 'General OPD Consult'
      billItems.value[0].rate = 500
    }, 400)
  }
}

const addLineItem = () => {
  const newId = billItems.value.length > 0 ? billItems.value[billItems.value.length - 1].id + 1 : 1
  billItems.value.push({ id: newId, item: '', category: 'Pharmacy', qty: 1, rate: null })
}

const removeLineItem = (index) => {
  billItems.value.splice(index, 1)
}

const totalAmount = computed(() => {
  let total = 0
  billItems.value.forEach(row => {
    const rate = parseFloat(row.rate) || 0
    const qty = parseInt(row.qty) || 0
    total += (rate * qty)
  })
  return total
})

const generateBill = () => {
  isSubmitting.value = true
  setTimeout(() => {
    isSubmitting.value = false
    showPrint.value = true
  }, 1000)
}

const resetPage = () => {
  showPrint.value = false
  selectedPatient.value = null
  searched.value = false
  searchInput.value = ''
  billItems.value = [{ id: 1, item: '', category: 'Consultation', qty: 1, rate: null }]
}
</script>

<template>
  <div class="staff-billing w-full pt-4">

    <!-- Page Header -->
    <div class="mb-3 flex justify-between items-center">
      <div>
        <h1>Billing</h1>
      </div>
    </div>

    <!-- Print overlay shown when invoice is generated -->
    <div v-if="showPrint" class="card p-10 text-center max-w-2xl mx-auto border-dashed border-2 border-primary">
       <div class="text-success mb-4 flex justify-center">
         <svg class="border-success text-success border-2 rounded-full p-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="64" height="64"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
       </div>
       <h2 class="text-3xl font-bold mb-2">Invoice Generated</h2>
       <p class="text-muted mb-6">Bill ID: <strong>B-004</strong> for {{ selectedPatient?.name }} has been saved to the database. Total: ₹{{ totalAmount.toFixed(2) }}</p>
       
       <div class="flex justify-center gap-4">
         <button class="btn btn-outline" @click="resetPage">Create New Bill</button>
         <button class="btn btn-primary">Print Invoice (PDF)</button>
       </div>
    </div>

    <!-- Main Billing Content -->
    <div v-else>
      <!-- Patient Lookup Block -->
      <div class="card mb-6 p-6">
        <h3 class="text-sm font-bold text-muted uppercase tracking-wider mb-4 border-b border-color pb-2">Patient Lookup</h3>
        <div class="flex-1 form-group mb-0">
          <div class="flex gap-4">
            <input type="text" v-model="searchInput" @keyup.enter="handleSearch" class="form-control flex-1" placeholder="Search by name or patient ID" />
            <button class="btn btn-primary px-8" @click="handleSearch">Find</button>
          </div>
          <p class="text-xs text-muted mt-2">Search by name or patient ID</p>
        </div>

        <!-- Found Patient Box -->
        <div v-if="selectedPatient" class="mt-4 p-4 border border-color rounded bg-primary-light border-primary flex justify-between items-center">
           <div>
             <span class="text-sm text-primary-dark font-medium">Found Record:</span>
             <strong class="ml-2 text-lg text-main">{{ selectedPatient.name }}</strong>
             <span class="badge badge-info ml-3">{{ selectedPatient.id }}</span>
           </div>
           <span class="badge badge-pending">{{ selectedPatient.type }}</span>
        </div>
        <div v-else-if="searched && !selectedPatient" class="mt-4 text-sm text-danger">No patient found matching your query.</div>
      </div>

      <!-- Bill Items Block -->
      <div class="card p-0 overflow-hidden mb-6">
        <h3 class="text-sm font-bold text-muted uppercase tracking-wider p-4 pb-2 border-b border-color bg-surface">Bill Items</h3>
        
        <table class="table mb-0 w-full no-highlight">
          <thead>
            <tr>
              <th width="35%" class="text-xs">Item</th>
              <th width="20%" class="text-xs">Category</th>
              <th width="10%" class="text-xs text-center">Qty</th>
              <th width="15%" class="text-xs text-right">Rate</th>
              <th width="15%" class="text-xs text-right">Amount</th>
              <th width="5%"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in billItems" :key="row.id">
              <td><input type="text" v-model="row.item" class="form-control form-control-sm" placeholder="e.g. Consultation" /></td>
              <td>
                <select v-model="row.category" class="form-control form-control-sm">
                   <option>Consultation</option>
                   <option>Pharmacy</option>
                   <option>Lab Test</option>
                   <option>Room Rent</option>
                </select>
              </td>
              <td><input type="number" min="1" v-model="row.qty" class="form-control form-control-sm text-center" /></td>
              <td><input type="number" min="0" step="0.01" v-model="row.rate" class="form-control form-control-sm text-right" placeholder="0" /></td>
              <td class="text-right align-middle">
                 <div class="font-medium text-main">₹{{ (row.qty * (row.rate||0)).toFixed(2) }}</div>
              </td>
              <td class="text-center align-middle">
                 <button class="btn-icon text-muted hover-danger" @click="removeLineItem(index)">&times;</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="p-4 border-b border-color flex items-center justify-between">
           <button class="btn btn-sm btn-outline text-primary" @click="addLineItem">+ Add Line Item</button>
        </div>

        <div class="p-6 text-right border-t border-color shadow-inner flex justify-end items-center gap-4 bg-background">
           <span class="font-bold text-muted text-sm tracking-wider uppercase">Auto-Calc Total:</span>
           <span class="text-2xl font-bold text-main">₹{{ totalAmount.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Alert & Action bar -->
      <div class="flex justify-between items-center mb-6">
        <div class="text-xs text-muted flex items-center gap-1 px-2 py-2 bg-background border border-color rounded w-max">
          <div style="width: 10px; height: 8px; border-radius: 50%;" class="bg-primary"></div>
          All edits auto-recorded in Billing Audit Log&nbsp;&nbsp;</div>
        <button class="btn btn-primary px-8 py-3 font-bold" :disabled="isSubmitting || totalAmount === 0" @click="generateBill">
          {{ isSubmitting ? 'Processing...' : 'Generate Invoice' }}
        </button>
      </div>

    </div>

  </div>
</template>

<style scoped>
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-4xl { max-width: 56rem; }
.max-w-2xl { max-width: 42rem; }
.w-full { width: 100%; }

.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-1 { margin-bottom: 0.25rem; }
.mb-0 { margin-bottom: 0; }
.mt-4 { margin-top: 1rem; }
.m-0 { margin: 0; }
.mr-4 { margin-right: 1rem; }
.mr-1 { margin-right: 0.25rem; }
.ml-2 { margin-left: 0.5rem; }

.p-10 { padding: 2.5rem; }
.p-6 { padding: 1.5rem; }
.p-4 { padding: 1rem; }
.px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
.px-8 { padding-left: 2rem; padding-right: 2rem; }
.p-2 { padding: 0.5rem; }
.p-0 { padding: 0; }

.flex-1 { flex: 1; }
.grid { display: grid; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.items-end { align-items: flex-end; }

.border-b { border-bottom: 1px solid var(--border-color); }
.border { border: 1px solid var(--border-color); }
.border-2 { border-width: 2px; }
.border-dashed { border-style: dashed; }
.rounded { border-radius: var(--radius-md); }
.rounded-full { border-radius: 9999px; }
.overflow-hidden { overflow: hidden; }

.font-bold { font-weight: 700; }
.text-3xl { font-size: 1.875rem; }
.text-2xl { font-size: 1.5rem; }
.text-xl { font-size: 1.25rem; font-weight: 600; }
.text-lg { font-size: 1.125rem; }
.text-sm { font-size: 0.875rem; }
.text-xs { font-size: 0.75rem; }
.uppercase { text-transform: uppercase; }
.tracking-wider { letter-spacing: 0.05em; }

.text-muted { color: var(--text-muted); }
.text-main { color: var(--text-main); }
.text-primary { color: var(--primary); }
.text-primary-dark { color: var(--primary-dark); }
.text-danger { color: var(--danger); }
.text-success { color: #166534; }
.bg-background { background-color: var(--background); }
.bg-primary-light { background-color: var(--primary-light); }
.border-primary { border-color: var(--primary); }
.border-success { border-color: #166534; }

.form-control-sm { padding: 0.375rem 0.5rem; font-size: 0.875rem; }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; }
.btn-icon { background: none; border: none; font-size: 1.5rem; cursor: pointer; transition: color 0.2s;}
.hover-danger:hover { color: var(--danger); }
.inline-block { display: inline-block; }

/* Remove table row hover highlight and borders for Bill Items */
table.no-highlight tbody tr:hover {
  background-color: transparent !important;
}
table.no-highlight tbody tr td {
  border-bottom: none !important;
  padding-bottom: 0.5rem;
}
</style>
