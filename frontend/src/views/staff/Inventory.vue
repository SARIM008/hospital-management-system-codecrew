<script setup>
import { ref } from 'vue'

const inventory = ref([
  { id: 'MED-101', item: 'Paracetamol 500mg', qty: 450, status: 'Healthy', expiry: 'Dec 2027' },
  { id: 'MED-102', item: 'Azithromycin 250mg', qty: 12, status: 'Low', expiry: 'Aug 2026' },
  { id: 'CON-001', item: 'Syringes 5ml', qty: 5, status: 'Critical', expiry: 'N/A' },
  { id: 'MED-205', item: 'Cough Syrup 100ml', qty: 30, status: 'Healthy', expiry: 'Mar 2026' }, // Expiring soon (<30 days)
])

const filterType = ref('ALL') // 'ALL', 'LOW'
const showUpdateModal = ref(false)
const updateForm = ref({ item: '', amount: 0 })

const openUpdate = (item) => {
  updateForm.value = { item: item.item, amount: 0 }
  showUpdateModal.value = true
}

const saveUpdate = () => {
  // Mock save
  showUpdateModal.value = false
}
</script>

<template>
  <div class="staff-inventory">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1>Stock Overview</h1>

      </div>
      <div class="flex gap-4">
        <button class="btn btn-outline" @click="showUpdateModal = true">Record Delivery</button>
      </div>
    </div>

    <div class="card p-0 overflow-hidden relative">
      <!-- Header Actions -->
      <div class="p-4 border-b border-color flex justify-between items-center bg-background">
        <div class="flex gap-2">
          <button class="btn btn-sm" :class="filterType === 'ALL' ? 'btn-secondary' : 'btn-outline'" @click="filterType = 'ALL'">All Stock</button>
          <button class="btn btn-sm" :class="filterType === 'LOW' ? 'btn-danger' : 'btn-outline text-danger'" @click="filterType = 'LOW'">Low Stock Alerts</button>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-sm text-primary flex items-center gap-1">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            Staff can only update quantities. Contact Admin to add/remove items.
          </div>
          <input type="text" class="form-control" style="width: 250px" placeholder="Search item name or ID..." />
        </div>
      </div>

      <!-- Inventory Table -->
      <table class="table">
        <thead>
          <tr>
            <th>Item / Medicine</th>
            <th>Stock QTY</th>
            <th>Status Indicator</th>
            <th>Expiry Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventory" :key="item.id">
            <td>
              <div class="font-medium text-main">{{ item.item }}</div>
              <div class="font-mono text-xs text-muted mt-1">{{ item.id }}</div>
            </td>
            <td class="font-medium text-lg">{{ item.qty }}</td>
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
                <span>{{ item.expiry }}</span>
                 <!-- Expiry Alert Logic Mock -->
                <span v-if="item.expiry === 'Mar 2026' || item.expiry === 'Jan 2026'" class="text-danger flex items-center" title="Expiring within 30 days">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                </span>
              </div>
            </td>
            <td>
              <button class="btn btn-sm btn-outline text-primary" @click="openUpdate(item)">Update QTY</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Update Modal Overlay -->
      <div v-if="showUpdateModal" class="absolute inset-0 bg-black/50 flex items-center justify-center z-10 backdrop-blur-sm">
         <div class="card w-full max-w-sm m-auto">
           <h3 class="text-lg font-bold mb-4">Update Quantity</h3>
           <p class="text-sm text-muted mb-4" v-if="updateForm.item">Modifying stock for <strong class="text-main">{{ updateForm.item }}</strong></p>
           
           <div class="form-group mb-4">
             <label class="form-label">Add/Remove Amount</label>
             <input type="number" v-model="updateForm.amount" class="form-control" placeholder="+50 or -10" />
           </div>
           
           <div class="flex gap-4">
             <button class="btn btn-outline flex-1" @click="showUpdateModal = false">Cancel</button>
             <button class="btn btn-primary flex-1" @click="saveUpdate">Save</button>
           </div>
         </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mt-1 { margin-top: 0.25rem; }
.p-0 { padding: 0; }
.p-4 { padding: 1rem; }
.m-auto { margin: auto; }
.w-full { width: 100%; }
.max-w-sm { max-width: 24rem; }
.flex-1 { flex: 1; }
.overflow-hidden { overflow: hidden; }

.border-b { border-bottom: 1px solid var(--border-color); }
.bg-background { background-color: var(--background); }
.text-danger { color: var(--danger); }
.text-primary { color: var(--primary); }
.text-muted { color: var(--text-muted); }
.text-main { color: var(--text-main); }

.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; }
.text-xs { font-size: 0.75rem; }
.text-sm { font-size: 0.875rem; }
.text-lg { font-size: 1.125rem; }

.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 500;}

.relative { position: relative; }
.absolute { position: absolute; }
.inset-0 { top: 0; right: 0; bottom: 0; left: 0; }
.bg-black\/50 { background-color: rgba(0, 0, 0, 0.5); }
.backdrop-blur-sm { backdrop-filter: blur(4px); }
.z-10 { z-index: 10; }
</style>
