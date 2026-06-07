<script setup>
import { reactive, ref } from 'vue'

const appointments = ref([
  { id: 1, time: '09:00 AM', patient: 'Rahul Sharma', doctor: 'Dr. Patil', status: 'Confirmed' },
  { id: 2, time: '10:30 AM', patient: 'Sneha Patel', doctor: 'Dr. Sharma', status: 'In Waiting' },
  { id: 3, time: '11:00 AM', patient: 'Amit Kumar', doctor: 'Dr. Patil', status: 'Confirmed' },
  { id: 4, time: '11:30 AM', patient: 'Priya Singh', doctor: 'Dr. Gupta', status: 'Confirmed' },
  { id: 5, time: '12:00 PM', patient: 'Vikram Malhotra', doctor: 'Dr. Patil', status: 'In Waiting' },
])

const isBooking = ref(false)
const newAppt = reactive({ search: '', date: '', time: '', dept: '', doc: '' })

const handleBook = () => {
  isBooking.value = false
  // trigger success toast here in real app
}
</script>

<template>
  <div class="staff-appointments">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1>Daily Appointments</h1>
      </div>
    </div>

    <!-- Daily Stats Overview -->
    <div class="grid grid-cols-4 gap-6 mb-6">
       <div class="card p-4 flex items-center gap-4 border border-color">
          <div class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl" style="color: var(--primary);">12</div>
          <div>
            <h4 class="text-xs text-muted uppercase tracking-wider font-bold mb-1">Total Today</h4>
            <p class="font-bold text-main" style="font-size: 1.125rem;">Appointments</p>
          </div>
       </div>
       <div class="card p-4 flex items-center gap-4 border border-color">
          <div class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl" style="color: #a16207;">4</div>
          <div>
            <h4 class="text-xs text-muted uppercase tracking-wider font-bold mb-1">Checked In</h4>
            <p class="font-bold text-main" style="font-size: 1.125rem;">Waiting</p>
          </div>
       </div>
       <div class="card p-4 flex items-center gap-4 border border-color">
          <div class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl" style="color: #166534;">6</div>
          <div>
            <h4 class="text-xs text-muted uppercase tracking-wider font-bold mb-1">Completed</h4>
            <p class="font-bold text-main" style="font-size: 1.125rem;">Consultations</p>
          </div>
       </div>
       <div class="card p-4 flex items-center gap-4 border border-color">
          <div class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl" style="color: #b91c1c;">1</div>
          <div>
            <h4 class="text-xs text-muted uppercase tracking-wider font-bold mb-1">Canceled</h4>
            <p class="font-bold text-main" style="font-size: 1.125rem;">No Shows</p>
          </div>
       </div>
    </div>

    <div class="grid grid-cols-3 gap-6">
      
      <!-- Main Schedule Area -->
      <div class="col-span-2">
        <!-- Booking Form Area (Top) -->
        <div class="card mb-6">
           <h2 class="text-xl mb-6 border-b border-color pb-4">Schedule New Appointment</h2>
           <form @submit.prevent="handleBook">
             <div class="form-group mb-4">
                <label class="form-label">Search Registered Patient</label>
                <input type="text" v-model="newAppt.search" class="form-control" placeholder="Search ID or Name" required />
             </div>
             <div class="grid grid-cols-2 gap-4 mb-4">
               <div class="form-group">
                 <label class="form-label">Department</label>
                 <select v-model="newAppt.dept" class="form-control" required>
                   <option>General Medicine</option>
                   <option>Orthopedics</option>
                 </select>
               </div>
               <div class="form-group">
                 <label class="form-label">Doctor</label>
                 <select v-model="newAppt.doc" class="form-control" required>
                   <option>General Available</option>
                   <option>Dr. Sharma</option>
                 </select>
               </div>
               <div class="form-group">
                 <label class="form-label">Date</label>
                 <input type="date" v-model="newAppt.date" class="form-control" required />
               </div>
               <div class="form-group">
                 <label class="form-label">Time</label>
                 <select v-model="newAppt.time" class="form-control" required>
                   <option>09:00 AM</option>
                   <option>11:00 AM</option>
                   <option>02:00 PM</option>
                 </select>
               </div>
             </div>
             
             <div class="flex justify-end gap-4 mt-6">
               <button type="submit" class="btn btn-primary px-8">Book Slot</button>
             </div>
           </form>
        </div>

        <div class="card p-0">
          <div class="p-4 border-b border-color flex justify-between items-center bg-background">
            <h2 class="text-lg">Today's Schedule (24 Feb)</h2>
            <div class="flex gap-2">
              <input type="text" class="form-control" placeholder="Search Patient..." />
              <button class="btn btn-outline">Filter by Doctor</button>
            </div>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Patient</th>
                <th>Assigned Doctor</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in appointments" :key="appt.id">
                <td class="font-medium text-main">{{ appt.time }}</td>
                <td class="font-bold">{{ appt.patient }}</td>
                <td class="text-muted">{{ appt.doctor }}</td>
                 <td>
                  <span class="badge" 
                    :class="appt.status === 'Confirmed' ? 'badge-success' : 'badge-pending'">
                    {{ appt.status }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline text-primary">Check-In</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Quick Actions Sidebar -->
      <div>
        <div class="card bg-primary-light border-primary mb-6 text-center">
           <h3 class="text-sm uppercase tracking-wider text-primary-dark font-bold mb-2">OPD Traffic Status</h3>
           <div class="text-4xl font-bold text-main my-2">Low</div>
           <p class="text-muted text-sm scale-90">Current average wait time: 10 mins</p>
        </div>
        
        <div class="card p-0 overflow-hidden text-sm">
          <div class="p-3 bg-background border-b border-color font-medium">Doctor Availability Today</div>
          <div class="p-3 flex justify-between items-center border-b border-color">
            <span class="text-main font-medium">Dr. Sharma</span>
            <span class="text-success">&bull; Available</span>
          </div>
          <div class="p-3 flex justify-between items-center border-b border-color">
            <span class="text-main font-medium">Dr. Patil</span>
            <span class="text-pending">&bull; In Surgery</span>
          </div>
          <div class="p-3 flex justify-between items-center">
            <span class="text-main font-medium">Dr. Iyer</span>
            <span class="text-danger">&bull; Off Duty</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.mb-6 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mt-6 { margin-top: 1.5rem; }
.my-2 { margin-top: 0.5rem; margin-bottom: 0.5rem; }
.pb-4 { padding-bottom: 1rem; }

.p-0 { padding: 0; }
.p-4 { padding: 1rem; }
.p-3 { padding: 0.75rem; }
.px-8 { padding-left: 2rem; padding-right: 2rem; }

.grid-cols-4 { grid-template-columns: repeat(4, 1fr); display: grid; }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); display: grid; }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); display: grid; }
.col-span-2 { grid-column: span 2 / span 2; }
.justify-end { justify-content: flex-end; }

.border-b { border-bottom: 1px solid var(--border-color); }
.border-primary { border-color: var(--primary); }
.bg-primary-light { background-color: var(--primary-light); }
.bg-background { background-color: var(--background); }
.overflow-hidden { overflow: hidden; }
.text-center { text-align: center; }

.text-danger { color: var(--danger); }
.text-primary { color: var(--primary); }
.text-primary-dark { color: var(--primary-dark); }
.text-muted { color: var(--text-muted); }
.text-main { color: var(--text-main); }
.text-success { color: #166534; }
.text-pending { color: #b45309; }

.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }
.text-4xl { font-size: 2.25rem; }
.text-xl { font-size: 1.25rem; }
.text-lg { font-size: 1.125rem; }
.text-sm { font-size: 0.875rem; }

.uppercase { text-transform: uppercase; }
.tracking-wider { letter-spacing: 0.05em; }
.scale-90 { transform: scale(0.9); }

.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; font-weight: 500;}
</style>
