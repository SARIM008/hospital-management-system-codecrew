<script setup>
import { ref, computed } from 'vue'

const activeTab = ref('BILLS')

const bills = ref([
  { id: 'B-001', patient: 'Rahul Sharma', age: 67, amount: 1200, category: 'Consultation', date: '24 Feb 2026', status: 'paid' },
  { id: 'B-002', patient: 'Sneha Patel', age: 34, amount: 450, category: 'Pharmacy', date: '24 Feb 2026', status: 'paid' },
  { id: 'B-003', patient: 'Amit Kumar', age: 52, amount: 5500, category: 'IPD Room', date: '23 Feb 2026', status: 'pending' },
  { id: 'B-004', patient: 'Priya Verma', age: 29, amount: 2800, category: 'Radiology', date: '23 Feb 2026', status: 'paid' },
  { id: 'B-005', patient: 'Rohan Mehta', age: 41, amount: 750, category: 'Pharmacy', date: '22 Feb 2026', status: 'voided' },
  { id: 'B-006', patient: 'Deepa Nair', age: 58, amount: 9200, category: 'Surgery', date: '22 Feb 2026', status: 'pending' },
  { id: 'B-007', patient: 'Suresh Iyer', age: 73, amount: 1600, category: 'Consultation', date: '21 Feb 2026', status: 'paid' },
  { id: 'B-008', patient: 'Anjali Singh', age: 25, amount: 350, category: 'Lab Tests', date: '21 Feb 2026', status: 'paid' },
])

const auditLogs = ref([
  { id: 'L-001', billId: 'B-002', staff: 'Receptionist Kavya', role: 'Receptionist', change: 'Added Paracetamol 500mg × 10', time: '10:45 AM', date: '24 Feb 2026', type: 'add' },
  { id: 'L-002', billId: 'B-001', staff: 'Admin Rajesh', role: 'Admin', change: 'Applied 10% senior citizen discount', time: '09:15 AM', date: '24 Feb 2026', type: 'discount' },
  { id: 'L-003', billId: 'B-005', staff: 'Dr. Meena Kapoor', role: 'Doctor', change: 'Voided bill — duplicate entry', time: '03:22 PM', date: '22 Feb 2026', type: 'void' },
  { id: 'L-004', billId: 'B-003', staff: 'Admin Rajesh', role: 'Admin', change: 'Extended IPD stay by 1 day', time: '11:00 AM', date: '23 Feb 2026', type: 'edit' },
  { id: 'L-005', billId: 'B-006', staff: 'Receptionist Kavya', role: 'Receptionist', change: 'Added OT charges ₹3,000', time: '08:55 AM', date: '22 Feb 2026', type: 'add' },
  { id: 'L-006', billId: 'B-004', staff: 'Admin Rajesh', role: 'Admin', change: 'Generated insurance claim receipt', time: '02:10 PM', date: '23 Feb 2026', type: 'edit' },
])

const totalRevenue = computed(() =>
  bills.value.filter(b => b.status !== 'voided').reduce((sum, b) => sum + b.amount, 0)
)
const consultationRevenue = computed(() =>
  bills.value.filter(b => b.category === 'Consultation' && b.status !== 'voided').reduce((sum, b) => sum + b.amount, 0)
)
const pendingRevenue = computed(() =>
  bills.value.filter(b => b.status === 'pending').reduce((sum, b) => sum + b.amount, 0)
)

const fmt = (n) => '₹' + n.toLocaleString('en-IN')

const statusMeta = {
  paid:    { label: 'Paid',    cls: 'status-paid' },
  pending: { label: 'Pending', cls: 'status-pending' },
  voided:  { label: 'Voided',  cls: 'status-voided' },
}

const auditTypeMeta = {
  add:      { icon: '+', cls: 'audit-add' },
  discount: { icon: '%', cls: 'audit-discount' },
  void:     { icon: '×', cls: 'audit-void' },
  edit:     { icon: '✎', cls: 'audit-edit' },
}
</script>

<template>
  <div class="billing-root">

    <!-- Header -->
    <div class="billing-header">
      <div class="header-left">
        
        <h1 class="header-title">Billing & Audit</h1>
      </div>
      <div class="header-actions">
        <button class="btn-ghost">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M2 4.5h11M4 7.5h7M6 10.5h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          Generate Report
        </button>
        <button class="btn-primary-action">
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M6.5 1v11M1 6.5h11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          New Bill
        </button>
      </div>
    </div>

    <!-- KPI Strip -->
    <div class="kpi-strip">
      <div class="kpi-card kpi-featured">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">{{ fmt(totalRevenue) }}</div>
        <div class="kpi-sub">Feb 2026</div>
        <div class="kpi-glow"></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Consultations</div>
        <div class="kpi-value kpi-value-sm">{{ fmt(consultationRevenue) }}</div>
        <div class="kpi-sub">{{ bills.filter(b => b.category === 'Consultation').length }} bills</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Pharmacy & Lab</div>
        <div class="kpi-value kpi-value-sm">{{ fmt(bills.filter(b => ['Pharmacy','Lab Tests'].includes(b.category) && b.status !== 'voided').reduce((s,b) => s+b.amount, 0)) }}</div>
        <div class="kpi-sub">{{ bills.filter(b => ['Pharmacy','Lab Tests'].includes(b.category)).length }} bills</div>
      </div>
      <div class="kpi-card kpi-warn">
        <div class="kpi-label">Pending Collection</div>
        <div class="kpi-value kpi-value-sm kpi-value-warn">{{ fmt(pendingRevenue) }}</div>
        <div class="kpi-sub">{{ bills.filter(b => b.status === 'pending').length }} unpaid bills</div>
      </div>
    </div>

    <!-- Main Panel -->
    <div class="main-panel">

      <!-- Tab Bar -->
      <div class="tab-bar">
        <button class="tab" :class="{ 'tab-active': activeTab === 'BILLS' }" @click="activeTab = 'BILLS'">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><rect x="1" y="1" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.4"/><path d="M4 5h6M4 7.5h6M4 10h3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          Generated Bills
          <span class="tab-count">{{ bills.length }}</span>
        </button>
        <button class="tab" :class="{ 'tab-active': activeTab === 'AUDIT' }" @click="activeTab = 'AUDIT'">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.4"/><path d="M7 4v3.5l2 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          Audit Logs
          <span class="tab-count tab-count-warn">{{ auditLogs.length }}</span>
        </button>
        <div class="tab-spacer"></div>
        <div v-if="activeTab === 'BILLS'" class="toolbar-right">
          <input type="date" class="date-filter" />
          <div class="results-pill">{{ bills.length }} records</div>
        </div>
      </div>

      <!-- Bills Table -->
      <div v-if="activeTab === 'BILLS'" class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Bill ID</th>
              <th>Patient</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bill in bills" :key="bill.id" class="data-row">
              <td><span class="mono-id">{{ bill.id }}</span></td>
              <td>
                <div class="patient-cell">
                  <div class="patient-avatar">{{ bill.patient.charAt(0) }}</div>
                  <div>
                    <div class="patient-name">{{ bill.patient }}</div>
                    <div class="patient-age">Age {{ bill.age }}</div>
                  </div>
                </div>
              </td>
              <td><span class="category-pill">{{ bill.category }}</span></td>
              <td><span class="amount-val">{{ fmt(bill.amount) }}</span></td>
              <td><span class="status-badge" :class="statusMeta[bill.status].cls">{{ statusMeta[bill.status].label }}</span></td>
              <td class="date-cell">{{ bill.date }}</td>
              <td>
                <div class="action-group">
                  <button class="action-btn action-edit" title="Edit">
                    <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M9.5 1.5l2 2L4 11H2v-2L9.5 1.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>
                  </button>
                  <button class="action-btn action-void" title="Void">
                    <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M2 2l9 9M11 2l-9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Audit Logs -->
      <div v-if="activeTab === 'AUDIT'" class="audit-container">
        <div class="security-notice">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M7.5 1L2 3.5v4c0 3.3 2.3 5.7 5.5 6.5C10.7 13.2 13 10.8 13 7.5v-4L7.5 1z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M5.5 7.5l1.5 1.5 3-3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span><strong>Immutable Audit Trail</strong> — All modifications are recorded automatically and cannot be deleted.</span>
        </div>

        <div class="audit-list">
          <div v-for="log in auditLogs" :key="log.id" class="audit-item">
            <div class="audit-icon-wrap" :class="auditTypeMeta[log.type].cls">
              <span class="audit-icon">{{ auditTypeMeta[log.type].icon }}</span>
            </div>
            <div class="audit-body">
              <div class="audit-top">
                <span class="audit-change">{{ log.change }}</span>
                <span class="audit-time">{{ log.date }} · {{ log.time }}</span>
              </div>
              <div class="audit-meta">
                <span class="audit-staff">{{ log.staff }}</span>
                <span class="audit-dot">·</span>
                <span class="audit-role">{{ log.role }}</span>
                <span class="audit-dot">·</span>
                <span class="audit-ref">ref: <span class="mono-id-sm">{{ log.billId }}</span></span>
              </div>
            </div>
            <span class="audit-log-id">{{ log.id }}</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ── Root ── */
.billing-root {
  max-width: 72rem;
  margin: 0 auto;
  padding: 0.5rem 0 2rem;
  font-family: 'DM Sans', 'Segoe UI', sans-serif;
  background:#ffffff; border-radius:30px;padding: 20px; 
}

/* ── Header ── */
.billing-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 1.75rem;
}

.header-eyebrow {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #10b981;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.header-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.03em;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-ghost {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.1rem;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  font-size: 0.85rem;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-ghost:hover { border-color: #10b981; color: #065f46; background: #f0fdf4; }

.btn-primary-action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.2rem;
  border-radius: 10px;
  border: none;
  background: #10b981;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 2px 8px rgba(16,185,129,0.3);
}
.btn-primary-action:hover { background: #059669; box-shadow: 0 4px 12px rgba(16,185,129,0.35); }

/* ── KPI Strip ── */
.kpi-strip {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
}

.kpi-featured {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-color: #a7f3d0;
}

.kpi-warn {
  background: #fffbeb;
  border-color: #fde68a;
}

.kpi-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.kpi-featured .kpi-label { color: #065f46; }
.kpi-warn .kpi-label { color: #92400e; }

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  color: #065f46;
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 0.35rem;
}

.kpi-value-sm { font-size: 1.5rem; color: #0f172a; }
.kpi-value-warn { color: #d97706; }

.kpi-sub {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}
.kpi-featured .kpi-sub { color: #6ee7b7; }
.kpi-warn .kpi-sub { color: #b45309; }

.kpi-glow {
  position: absolute;
  right: -20px;
  bottom: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(16,185,129,0.15);
}

/* ── Main Panel ── */
.main-panel {
  background: #fff;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  overflow: hidden;
}

/* ── Tab Bar ── */
.tab-bar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  background: #fafafa;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.1rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #94a3b8;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.15s;
}
.tab:hover { color: #475569; }
.tab-active { color: #10b981; border-bottom-color: #10b981; }

.tab-count {
  background: #f1f5f9;
  color: #64748b;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 20px;
}
.tab-active .tab-count { background: #d1fae5; color: #065f46; }
.tab-count-warn { background: #fef3c7; color: #92400e; }

.tab-spacer { flex: 1; }

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.date-filter {
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 0.8rem;
  color: #475569;
  font-family: inherit;
}
.date-filter:focus { outline: none; border-color: #10b981; }

.results-pill {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.3rem 0.85rem;
  border-radius: 20px;
}

/* ── Data Table ── */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead tr {
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}

.data-table th {
  padding: 0.85rem 1.25rem;
  text-align: left;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #94a3b8;
}

.data-row {
  border-bottom: 1px solid #f8fafc;
  transition: background 0.1s;
}
.data-row:last-child { border-bottom: none; }
.data-row:hover { background: #fafffe; }

.data-table td {
  padding: 0.9rem 1.25rem;
  vertical-align: middle;
}

.mono-id {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.78rem;
  font-weight: 600;
  color: #94a3b8;
  background: #f8fafc;
  padding: 2px 8px;
  border-radius: 6px;
}

.patient-cell {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.patient-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.patient-name { font-size: 0.875rem; font-weight: 600; color: #1e293b; }
.patient-age  { font-size: 0.72rem; color: #94a3b8; margin-top: 1px; }

.category-pill {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  background: #f1f5f9;
  color: #475569;
}

.amount-val {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.01em;
}

.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.status-paid    { background: #d1fae5; color: #065f46; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-voided  { background: #f1f5f9; color: #94a3b8; text-decoration: line-through; }

.date-cell { font-size: 0.82rem; color: #64748b; }

.action-group { display: flex; gap: 0.4rem; }

.action-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  color: #64748b;
}
.action-edit:hover  { background: #ecfdf5; border-color: #10b981; color: #10b981; }
.action-void:hover  { background: #fee2e2; border-color: #fca5a5; color: #dc2626; }

/* ── Audit Logs ── */
.audit-container {
  padding: 1.25rem 1.5rem;
}

.security-notice {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  font-size: 0.82rem;
  color: #065f46;
  margin-bottom: 1.25rem;
}

.audit-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.audit-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  background: #fafafa;
  transition: all 0.15s;
}
.audit-item:hover { background: #fff; border-color: #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

.audit-icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.9rem;
  font-weight: 700;
}
.audit-add      { background: #d1fae5; color: #065f46; }
.audit-discount { background: #dbeafe; color: #1e40af; }
.audit-void     { background: #fee2e2; color: #991b1b; }
.audit-edit     { background: #fef3c7; color: #92400e; }

.audit-body { flex: 1; min-width: 0; }

.audit-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
}

.audit-change {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
}

.audit-time {
  font-size: 0.72rem;
  color: #94a3b8;
  white-space: nowrap;
  flex-shrink: 0;
}

.audit-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.2rem;
  font-size: 0.75rem;
  color: #64748b;
}

.audit-dot { color: #cbd5e1; }
.audit-staff { font-weight: 600; }
.audit-role  { color: #94a3b8; }

.mono-id-sm {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.72rem;
  color: #10b981;
  font-weight: 600;
}

.audit-log-id {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.68rem;
  color: #cbd5e1;
  flex-shrink: 0;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .kpi-strip { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  .kpi-strip { grid-template-columns: 1fr; }
  .billing-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .tab-bar { flex-wrap: wrap; gap: 0; }
  .toolbar-right { width: 100%; padding: 0.5rem 0; }
}
</style>