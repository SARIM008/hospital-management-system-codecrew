<script setup>
const pendingFollowUps = [
  { id: 1, patient: 'Rahul Sharma', due: '25 Feb 2026', type: 'Discharge Check', status: 'PENDING' },
  { id: 2, patient: 'Amit Kumar', due: '26 Feb 2026', type: 'Chronic Meds', status: 'PENDING' },
]
</script>

<template>
  <div class="admin-reports">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1>Reports & Analytics</h1>

      </div>
      <div class="flex gap-2">
        <button class="btn btn-outline active-filter">Daily</button>
        <button class="btn btn-outline">Monthly</button>
        <button class="btn btn-outline">Custom Range</button>
      </div>
    </div>

    <!-- Top KPI Cards -->
    <div class="grid grid-cols-3 gap-6 mb-6">
       <div class="card flex items-center justify-between p-6">
         <div>
           <p class="text-sm tracking-wider uppercase text-muted mb-1">Total Revenue</p>
           <h2 class="text-3xl font-bold text-primary">₹24,500</h2>
         </div>
         <div class="trend-indicator up">+12%</div>
       </div>
       <div class="card flex items-center justify-between p-6">
         <div>
           <p class="text-sm tracking-wider uppercase text-muted mb-1">Total OPD Visits</p>
           <h2 class="text-3xl font-bold text-secondary">142</h2>
         </div>
         <div class="trend-indicator up">+5%</div>
       </div>
       <div class="card flex items-center justify-between p-6">
         <div>
           <p class="text-sm tracking-wider uppercase text-muted mb-1">New IPD Admits</p>
           <h2 class="text-3xl font-bold text-main">12</h2>
         </div>
         <div class="trend-indicator down">-2%</div>
       </div>
    </div>

    <!-- Mock Charts Grid -->
    <div class="grid grid-cols-2 gap-6 mb-6">
      
      <!-- Mock Bar Chart (CSS drawn) -->
      <div class="card">
        <h2 class="text-lg mb-6">Monthly Revenue Comparison</h2>
        <div class="chart-mockup bar-chart">
          <!-- Y Axis Labels -->
          <div class="y-axis">
            <span>₹30k</span><span>₹20k</span><span>₹10k</span><span>0</span>
          </div>
          <!-- Bars Area -->
          <div class="bars-area">
             <div class="bar-group">
               <div class="bar last hidden-month" style="height: 60%" title="Last Month"></div>
               <div class="bar current bg-primary" style="height: 75%" title="This Month"></div>
               <span class="x-label">Week 1</span>
             </div>
             <div class="bar-group">
               <div class="bar last hidden-month" style="height: 80%"></div>
               <div class="bar current bg-primary" style="height: 65%"></div>
               <span class="x-label">Week 2</span>
             </div>
             <div class="bar-group">
               <div class="bar last hidden-month" style="height: 50%"></div>
               <div class="bar current bg-primary" style="height: 85%"></div>
               <span class="x-label">Week 3</span>
             </div>
             <div class="bar-group">
               <div class="bar last hidden-month" style="height: 90%"></div>
               <div class="bar current bg-primary" style="height: 55%"></div>
               <span class="x-label">Week 4</span>
             </div>
          </div>
        </div>
        <div class="flex justify-center gap-4 mt-6 text-sm">
          <div class="flex items-center gap-2"><div class="legend-box hidden-month"></div> Last Month</div>
          <div class="flex items-center gap-2"><div class="legend-box bg-primary"></div> This Month</div>
        </div>
      </div>

      <!-- Mock Donut & Line -->
      <div class="flex flex-col gap-6">
        <div class="card flex-1 flex items-center justify-center relative">
           <div class="w-full text-center">
             <h2 class="text-lg mb-4 text-left absolute top-4 left-6">Revenue Breakdown</h2>
             <div class="donut-chart mx-auto">
               <div class="donut-hole">
                 <span class="font-bold text-xl">100%</span>
               </div>
             </div>
             <!-- Legend -->
             <div class="flex justify-center gap-4 mt-4 text-sm">
              <div class="flex items-center gap-2"><div class="legend-box bg-primary"></div> Consult (60%)</div>
              <div class="flex items-center gap-2"><div class="legend-box bg-secondary"></div> Pharmacy (25%)</div>
              <div class="flex items-center gap-2"><div class="legend-box" style="background:#f59e0b"></div> Other (15%)</div>
            </div>
           </div>
        </div>
      </div>
    </div>
    
    <!-- Pending Follow-ups Table -->
    <div class="card p-0">
      <div class="p-4 border-b border-color">
         <h2 class="text-lg text-danger">Action Required: Pending Follow-ups</h2>
      </div>
      <div class="table-wrapper border-0">
         <table class="table">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Due Date</th>
                <th>Reminder Type</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="follow in pendingFollowUps" :key="follow.id">
                <td class="font-medium text-main">{{ follow.patient }}</td>
                <td>{{ follow.due }}</td>
                <td>{{ follow.type }}</td>
                <td><span class="badge badge-pending">{{ follow.status }}</span></td>
                <td><button class="btn btn-sm btn-outline text-primary">Mark Contacted</button></td>
              </tr>
            </tbody>
         </table>
      </div>
    </div>
    
  </div>
</template>

<style scoped>
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-1 { margin-bottom: 0.25rem; }
.mt-6 { margin-top: 1.5rem; }
.mt-4 { margin-top: 1rem; }
.p-6 { padding: 1.5rem; }
.p-4 { padding: 1rem; }
.p-0 { padding: 0; }
.mx-auto { margin-left: auto; margin-right: auto; }

.grid-cols-3 { grid-template-columns: repeat(3, 1fr); display: grid; }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); display: grid; }
.flex-col { flex-direction: column; }
.flex-1 { flex: 1; }
.w-full { width: 100%; }
.relative { position: relative; }
.absolute { position: absolute; }
.top-4 { top: 1rem; }
.left-6 { left: 1.5rem; }

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-lg { font-size: 1.125rem; font-weight: 600; }
.text-3xl { font-size: 1.875rem; }
.text-xl { font-size: 1.25rem; }
.text-sm { font-size: 0.875rem; }

.text-primary { color: var(--primary); }
.text-secondary { color: var(--secondary); }
.text-main { color: var(--text-main); }
.text-muted { color: var(--text-muted); }
.text-danger { color: var(--danger); }
.bg-primary { background-color: var(--primary); }
.bg-secondary { background-color: var(--secondary); }
.hidden-month { background-color: var(--border-color); }

.border-b { border-bottom: 1px solid var(--border-color); }
.tracking-wider { letter-spacing: 0.05em; }
.uppercase { text-transform: uppercase; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }

.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; font-weight: 500;}

.active-filter {
  background-color: var(--background);
  color: var(--text-main);
  border-color: var(--text-muted);
}

.trend-indicator {
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}
.trend-indicator.up { background: #dcfce7; color: #166534; }
.trend-indicator.down { background: #fee2e2; color: #991b1b; }

.legend-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* --- MOCK CSS CHARTS --- */

.chart-mockup {
  height: 250px;
  display: flex;
  margin-top: 1rem;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 1rem;
  text-align: right;
  color: var(--text-muted);
  font-size: 0.75rem;
  border-right: 1px solid var(--border-color);
  width: 50px;
}

.bars-area {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding-left: 1rem;
  position: relative;
}

/* Background grid lines */
.bars-area::before, .bars-area::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  border-top: 1px dashed var(--border-color);
  z-index: 0;
}
.bars-area::before { top: 33%; }
.bars-area::after { top: 66%; }

.bar-group {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 100%;
  position: relative;
  z-index: 1;
  width: 40px;
}

.bar {
  width: 18px;
  border-radius: 3px 3px 0 0;
  transition: opacity 0.2s;
}
.bar:hover { opacity: 0.8; cursor: pointer; }

.x-label {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  white-space: nowrap;
  color: var(--text-muted);
}

/* Simple CSS Donut Chart logic via conic-gradient */
.donut-chart {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: conic-gradient(
    var(--primary) 0deg 216deg, /* 60% */
    var(--secondary) 216deg 306deg, /* 25% */
    #f59e0b 306deg 360deg /* 15% */
  );
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-hole {
  width: 120px;
  height: 120px;
  background-color: var(--surface);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
</style>
