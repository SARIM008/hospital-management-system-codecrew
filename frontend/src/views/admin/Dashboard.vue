<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'

const stats = ref(null)
const loading = ref(true)
const animatedBeds = ref(0)

onMounted(async () => {
  try {
    const res = await api.get('/admin/dashboard-stats')
    stats.value = res.data
    // Animate the bed counter
    const target = stats.value?.active_ipd ?? 0
    let current = 0
    const step = Math.ceil(target / 40)
    const interval = setInterval(() => {
      current = Math.min(current + step, target)
      animatedBeds.value = current
      if (current >= target) clearInterval(interval)
    }, 30)
  } catch (err) {
    console.error('Failed to fetch dashboard stats', err)
  } finally {
    loading.value = false
  }
})

const capacityPct = computed(() => stats.value?.ward_capacity_pct ?? 0)
const capacityColor = computed(() => {
  if (capacityPct.value > 85) return '#ef4444'
  if (capacityPct.value > 65) return '#f59e0b'
  return '#10b981'
})
const dummyInflow = [38, 52, 45, 67, 71, 58, 84]

// Dummy sparkline data for visual richness
const revenueSparkline = [42, 38, 55, 61, 48, 70, 85, 78, 92, 88, 76, 95]
const maxSparkline = Math.max(...revenueSparkline)

// Dummy radial gauge segments
const gaugeSegments = computed(() => {
  const pct = capacityPct.value / 100
  const circumference = 2 * Math.PI * 54
  return {
    filled: pct * circumference,
    total: circumference
  }
})

const criticalAlertsCount = computed(() => {
    return stats.value?.system_alerts?.filter(a => a.type === 'critical' || a.type === 'warning').length || 0;
})
</script>

<template>
  <div class="dashboard">

    <div class="time-strip">
      <span class="time-strip-clock">{{ new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</span>
    </div>


    <div v-if="loading" class="loading-screen">
      <div class="loading-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
      </div>
      <div class="loading-bar-track"><div class="loading-bar-fill"></div></div>
      <p class="loading-text">Syncing hospital telemetry…</p>
    </div>

    <main v-else class="main-content">

      <div class="page-title-row">
        <div>
          <h1 class="page-title">Hospital Overview</h1>
          <p class="page-sub">Real-time floor metrics · {{ new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
        </div>
        <div class="ai-mini-chip" :class="{ 'ai-mini-offline': stats.ai_engine !== 'online' }">
          <div class="ai-mini-rings" aria-hidden="true">
            <span class="ai-ring r1"></span>
            <span class="ai-ring r2"></span>
            <div class="ai-mini-dot" :class="stats.ai_engine === 'online' ? 'dot-on' : 'dot-off'"></div>
          </div>
          <div class="ai-mini-text">
            <span class="ai-mini-label">Ward-Wizard AI</span>
            <span class="ai-mini-status" :class="stats.ai_engine === 'online' ? 'status-on' : 'status-off'">
              {{ stats.ai_engine === 'online' ? 'Engine Online' : 'Engine Offline' }}
            </span>
          </div>
          <div class="ai-mini-wave" v-if="stats.ai_engine === 'online'" aria-hidden="true">
            <span v-for="n in 5" :key="n" class="ai-wave-bar" :style="{ animationDelay: n * 0.12 + 's' }"></span>
          </div>
        </div>
      </div>

      <div class="kpi-strip">

        <div class="kpi-card">
          <div class="kpi-icon-wrap blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-label">Appointments Today</div>
            <div class="kpi-value">{{ stats.today_appointments }}</div>
            <div class="kpi-delta positive">↑ 12% vs yesterday</div>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 60 28" preserveAspectRatio="none">
              <polyline points="0,24 10,18 20,22 30,12 40,16 50,8 60,4" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
            </svg>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-label">Active Doctors</div>
            <div class="kpi-value">{{ stats.active_doctors }}</div>
            <div class="kpi-delta neutral">All wards covered</div>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 60 28" preserveAspectRatio="none">
              <polyline points="0,14 10,12 20,14 30,10 40,12 50,10 60,10" fill="none" stroke="#10b981" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
            </svg>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap amber">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-label">Patients Healed</div>
            <div class="kpi-value">{{ stats.total_healed }}</div>
            <div class="kpi-delta positive">↑ 8% this month</div>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 60 28" preserveAspectRatio="none">
              <polyline points="0,20 10,18 20,15 30,12 40,10 50,7 60,4" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
            </svg>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap rose">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-label">Avg. Length of Stay</div>
            <div class="kpi-value">{{ stats.alos }}<span class="kpi-unit">d</span></div>
            <div class="kpi-delta negative">↑ 0.3d vs last week</div>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 60 28" preserveAspectRatio="none">
              <polyline points="0,10 10,12 20,10 30,14 40,12 50,15 60,17" fill="none" stroke="#f43f5e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
            </svg>
          </div>
        </div>

      </div>

      <div class="main-grid">

        <div class="left-col">

          <div class="panel capacity-panel">
            <div class="panel-header">
              <div>
                <div class="panel-title">Ward Capacity</div>
                <div class="panel-sub">Live bed occupancy</div>
              </div>
              <div class="status-chip" :class="capacityPct > 85 ? 'danger' : capacityPct > 65 ? 'warn' : 'ok'">
                {{ capacityPct > 85 ? 'Critical' : capacityPct > 65 ? 'High' : 'Normal' }}
              </div>
            </div>

            <div class="capacity-visual">
              <div class="gauge-wrap">
                <svg class="gauge-svg" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#e6eeea" stroke-width="10"/>
                  <circle
                    cx="60" cy="60" r="54"
                    fill="none"
                    :stroke="capacityColor"
                    stroke-width="10"
                    stroke-linecap="round"
                    :stroke-dasharray="`${gaugeSegments.filled} ${gaugeSegments.total}`"
                    stroke-dashoffset="85"
                    transform="rotate(-90 60 60)"
                    style="transition: stroke-dasharray 1.5s cubic-bezier(.4,0,.2,1)"
                    filter="url(#glow)"
                  />
                  <defs>
                    <filter id="glow"><feGaussianBlur stdDeviation="2" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter>
                  </defs>
                  <text x="60" y="55" text-anchor="middle" class="gauge-pct-text" :fill="capacityColor">{{ capacityPct }}%</text>
                  <text x="60" y="72" text-anchor="middle" class="gauge-sub-text" fill="#7a9a87">occupied</text>
                </svg>
              </div>

              <div class="capacity-stats">
                <div class="cap-stat">
                  <div class="cap-stat-val" :style="{ color: capacityColor }">{{ stats.active_ipd }}</div>
                  <div class="cap-stat-lbl">Occupied</div>
                </div>
                <div class="cap-divider"></div>
                <div class="cap-stat">
                  <div class="cap-stat-val">{{ stats.total_beds - stats.active_ipd }}</div>
                  <div class="cap-stat-lbl">Available</div>
                </div>
                <div class="cap-divider"></div>
                <div class="cap-stat">
                  <div class="cap-stat-val">{{ stats.total_beds }}</div>
                  <div class="cap-stat-lbl">Total Beds</div>
                </div>
              </div>
            </div>

            <div class="ward-breakdown">
              <div class="ward-row" v-for="ward in [
                { name: 'ICU', pct: 92, color: '#ef4444' },
                { name: 'General', pct: 71, color: '#f59e0b' },
                { name: 'Pediatric', pct: 48, color: '#10b981' },
                { name: 'Maternity', pct: 55, color: '#3b82f6' },
              ]" :key="ward.name">
                <div class="ward-name">{{ ward.name }}</div>
                <div class="ward-track">
                  <div class="ward-fill" :style="{ width: ward.pct + '%', background: ward.color }"></div>
                </div>
                <div class="ward-pct" :style="{ color: ward.color }">{{ ward.pct }}%</div>
              </div>
            </div>
          </div>

          <div class="panel inflow-panel">
            <div class="panel-header">
              <div>
                <div class="panel-title">7-Day Patient Inflow</div>
                <div class="panel-sub">Daily admission trend</div>
              </div>
              <div class="inflow-total">
                <span class="inflow-num">{{ stats.today_appointments }}</span>
                <span class="inflow-lbl">today</span>
              </div>
            </div>

            <div class="bar-chart-area">
              <div class="bar-chart">
                <div
                  v-for="(val, i) in dummyInflow"
                  :key="i"
                  class="bar-col"
                >
                  <div class="bar-tooltip">{{ val }} patients</div>
                  <div
  class="bar-fill"
  :style="{
    height: Math.max(8, (val / Math.max(...dummyInflow)) * 100) + '%',
    background: i % 2 === 0 ? '#e8f4f0' : '#3d9b7a'
  }"
></div>
                  <div class="bar-day">{{ ['M','T','W','T','F','S','S'][i] }}</div>
                </div>
              </div>
              <div class="chart-guides" aria-hidden="true">
                <div class="guide-line" v-for="n in 4" :key="n"></div>
              </div>
            </div>
          </div>

        </div>

        <div class="right-col">

          <div class="panel revenue-panel">
            <div class="panel-header">
              <div>
                <div class="panel-title">Revenue</div>
                <div class="panel-sub">Estimated today</div>
              </div>
              <div class="revenue-badge">+18.4%</div>
            </div>

            <div class="revenue-main">
              <div class="revenue-amount">₹{{ stats.today_revenue }}</div>
              <div class="revenue-sub">vs ₹{{ Math.round(Number(String(stats.today_revenue).replace(/,/g,'')) * 0.84).toLocaleString('en-IN') }} yesterday</div>
            </div>

            <div class="revenue-chart">
              <svg viewBox="0 0 300 80" preserveAspectRatio="none" class="rev-svg">
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#10b981" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <path
                  :d="`M ${revenueSparkline.map((v, i) => `${i * (300 / (revenueSparkline.length - 1))},${80 - (v / maxSparkline) * 70}`).join(' L ')} L 300,80 L 0,80 Z`"
                  fill="url(#revGrad)"
                />
                <polyline
                  :points="revenueSparkline.map((v, i) => `${i * (300 / (revenueSparkline.length - 1))},${80 - (v / maxSparkline) * 70}`).join(' ')"
                  fill="none"
                  stroke="#10b981"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <circle
                  :cx="300"
                  :cy="80 - (revenueSparkline[revenueSparkline.length-1] / maxSparkline) * 70"
                  r="4"
                  fill="#10b981"
                />
              </svg>
              <div class="rev-labels">
                <span>12h ago</span>
                <span>Now</span>
              </div>
            </div>

            <div class="rev-breakdown">
              <div class="rev-item" v-for="item in [
                { label: 'OPD Consultations', val: '₹1,24,000', pct: 38 },
                { label: 'IPD Billing', val: '₹2,10,000', pct: 64 },
                { label: 'Lab & Diagnostics', val: '₹67,500', pct: 21 },
              ]" :key="item.label">
                <div class="rev-item-top">
                  <span class="rev-item-lbl">{{ item.label }}</span>
                  <span class="rev-item-val">{{ item.val }}</span>
                </div>
                <div class="rev-item-track">
                  <div class="rev-item-fill" :style="{ width: item.pct + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Alerts Panel -->
          <div class="panel alerts-panel">
            <div class="panel-header">
              <div class="panel-title">System Alerts</div>
              <div class="alert-count">3 active</div>
            </div>
            <div class="alert-list">
              <div class="alert-item crit">
                <div class="alert-dot"></div>
                <div class="alert-body">
                  <div class="alert-msg">ICU capacity at 92% — consider overflow protocol</div>
                  <div class="alert-time">2 min ago</div>
                </div>
              </div>
              <div class="alert-item warn">
                <div class="alert-dot"></div>
                <div class="alert-body">
                  <div class="alert-msg">Dr. Sharma has 8 pending prescriptions</div>
                  <div class="alert-time">14 min ago</div>
                </div>
              </div>
              <div class="alert-item info">
                <div class="alert-dot"></div>
                <div class="alert-body">
                  <div class="alert-msg">Lab report batch ready for review (24 reports)</div>
                  <div class="alert-time">31 min ago</div>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </main>

  </div>
</template>



<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─── TOKENS ─────────────────────────────────────────────── */
.dashboard {
  --bg:          #ffffff;
  --surface-1:   #ffffff;
  --surface-2:   #f0f5f2;
  --surface-3:   #e6eeea;
  --border:      #ffffff;
  --border-hi:   rgba(16,185,129,0.35);
  --text-1:      #0f1f18;
  --text-2:      #3d5a4a;
  --text-3:      #7a9a87;
  --green:       #10b981;
  --green-dim:   rgba(16,185,129,0.10);
  --blue:        #3b82f6;
  --amber:       #f59e0b;
  --rose:        #f43f5e;
  --gold:        #fbbf24;
  --radius-sm:   10px;
  --radius-md:   16px;
  --radius-lg:   22px;
  
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  min-height: 100vh; /* Crucial: Use min-height instead of fixed height */
  color: var(--text-1);
  position: relative;
  overflow-x: hidden;
  border-radius: 30px;
}

/* 5. Hide scrollbar for Chrome, Safari and Opera */
.dashboard::-webkit-scrollbar {
  display: none;
}

/* ─── BACKGROUND ──────────────────────────────────────────── */
.dashboard {
  background: #ffffff;
  border-radius: 30px;
}

/* ─── TIME STRIP ──────────────────────────────────────────── */
.time-strip {
  display: flex;
  justify-content: flex-end;
  padding: 14px 32px 0;
}
.time-strip-clock {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-3);
  letter-spacing: 0.04em;
}

/* ─── AI MINI CHIP (page title row) ──────────────────────── */
.ai-mini-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border: 1px solid var(--border-hi);
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(16,185,129,0.08);
  position: relative;
  overflow: hidden;
}
.ai-mini-chip.ai-mini-offline {
  border-color: rgba(244,63,94,0.3);
  box-shadow: 0 2px 12px rgba(244,63,94,0.06);
}

/* Concentric pulsing rings */
.ai-mini-rings {
  position: relative;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ai-ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(16,185,129,0.35);
  animation: ringPulse 2s ease-out infinite;
}
.ai-ring.r1 { width: 28px; height: 28px; animation-delay: 0s; }
.ai-ring.r2 { width: 20px; height: 20px; animation-delay: 0.5s; }
@keyframes ringPulse {
  0%   { transform: scale(0.7); opacity: 0.7; }
  70%  { transform: scale(1.2); opacity: 0; }
  100% { transform: scale(1.2); opacity: 0; }
}
.ai-mini-dot {
  width: 9px; height: 9px;
  border-radius: 50%;
  position: relative; z-index: 1;
}
.ai-mini-dot.dot-on {
  background: var(--green);
  box-shadow: 0 0 0 3px rgba(16,185,129,0.2);
  animation: dotGlow 1.8s ease-in-out infinite alternate;
}
.ai-mini-dot.dot-off {
  background: var(--rose);
}
@keyframes dotGlow {
  0%  { box-shadow: 0 0 0 2px rgba(16,185,129,0.15); }
  100%{ box-shadow: 0 0 0 5px rgba(16,185,129,0.05); }
}

.ai-mini-text {
  display: flex; flex-direction: column; gap: 1px;
}
.ai-mini-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-2);
  letter-spacing: 0.01em;
}
.ai-mini-status {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.ai-mini-status.status-on  { color: var(--green); }
.ai-mini-status.status-off { color: var(--rose); }

/* Mini waveform bars */
.ai-mini-wave {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 16px;
  padding-left: 4px;
  border-left: 1px solid var(--border);
}
.ai-wave-bar {
  display: block;
  width: 3px;
  border-radius: 2px;
  background: var(--green);
  animation: waveAnim 1s ease-in-out infinite alternate;
}
.ai-wave-bar:nth-child(1) { height: 6px;  animation-delay: 0.0s; }
.ai-wave-bar:nth-child(2) { height: 12px; animation-delay: 0.15s; }
.ai-wave-bar:nth-child(3) { height: 8px;  animation-delay: 0.3s; }
.ai-wave-bar:nth-child(4) { height: 14px; animation-delay: 0.1s; }
.ai-wave-bar:nth-child(5) { height: 6px;  animation-delay: 0.25s; }
@keyframes waveAnim {
  0%   { transform: scaleY(0.4); opacity: 0.4; }
  100% { transform: scaleY(1);   opacity: 1; }
}


/* ─── LOADING ─────────────────────────────────────────────── */
.loading-screen {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 16px; min-height: calc(100vh - 60px);
  position: relative; z-index: 1;
}
.loading-logo {
  width: 48px; height: 48px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 30px rgba(16,185,129,0.4);
  animation: float 2s ease-in-out infinite;
}
.loading-logo svg { width: 24px; height: 24px; color: white; }
@keyframes float { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-6px);} }
.loading-bar-track {
  width: 200px; height: 2px; background: var(--surface-3); border-radius: 2px; overflow: hidden;
}
.loading-bar-fill {
  height: 100%; width: 0%; background: var(--green);
  border-radius: 2px;
  animation: load 2s ease-in-out infinite;
}
@keyframes load { 0%{width:0%} 80%{width:100%} 100%{width:100%;opacity:0} }
.loading-text { font-size: 13px; color: var(--text-3); font-family: 'JetBrains Mono', monospace; }

/* ─── MAIN ────────────────────────────────────────────────── */
.main-content {
  position: relative; z-index: 1;
  max-width: 1360px;
  margin: 0 auto;
  padding: 20px 28px 48px;
}

/* Page Title */
.page-title-row {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 28px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  letter-spacing: -0.03em; color: var(--text-1);
  margin: 0 0 4px 0;
}
.page-sub { font-size: 13px; color: var(--text-3); margin: 0; }


/* ─── PAGE TITLE ──────────────────────────────────────────── */

/* ─── KPI STRIP ───────────────────────────────────────────── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}

.kpi-card {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 18px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.kpi-card:hover { border-color: var(--border-hi); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16,185,129,0.08); }

.kpi-icon-wrap {
  width: 40px; height: 40px; min-width: 40px;
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.kpi-icon-wrap svg { width: 18px; height: 18px; }
.kpi-icon-wrap.blue  { background: rgba(59,130,246,0.15); color: var(--blue); }
.kpi-icon-wrap.green { background: var(--green-dim); color: var(--green); }
.kpi-icon-wrap.amber { background: rgba(245,158,11,0.12); color: var(--amber); }
.kpi-icon-wrap.rose  { background: rgba(244,63,94,0.12); color: var(--rose); }

.kpi-body { flex: 1; min-width: 0; }
.kpi-label { font-size: 11px; color: var(--text-3); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.kpi-value { font-size: 26px; font-weight: 700; letter-spacing: -0.04em; color: var(--text-1); line-height: 1; }
.kpi-unit { font-size: 14px; font-weight: 500; color: var(--text-2); }
.kpi-delta { font-size: 11px; margin-top: 5px; font-weight: 500; }
.kpi-delta.positive { color: var(--green); }
.kpi-delta.negative { color: var(--rose); }
.kpi-delta.neutral  { color: var(--text-3); }

.kpi-sparkline {
  position: absolute; bottom: 0; right: 0;
  width: 80px; height: 40px; opacity: 0.7;
}
.kpi-sparkline svg { width: 100%; height: 100%; }

/* ─── MAIN GRID ───────────────────────────────────────────── */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 20px;
  align-items: start;
}
.left-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

/* ─── PANELS ──────────────────────────────────────────────── */
.panel {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.03);
}
.panel-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 20px;
}
.panel-title { font-size: 14px; font-weight: 700; color: var(--text-1); letter-spacing: -0.01em; }
.panel-sub { font-size: 11px; color: var(--text-3); margin-top: 2px; }

.status-chip {
  font-size: 11px; font-weight: 600;
  padding: 4px 10px; border-radius: 20px;
  letter-spacing: 0.04em;
}
.status-chip.ok     { background: var(--green-dim); color: var(--green); border: 1px solid var(--border-hi); }
.status-chip.warn   { background: rgba(245,158,11,0.12); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }
.status-chip.danger { background: rgba(244,63,94,0.12); color: var(--rose); border: 1px solid rgba(244,63,94,0.3); }

/* ─── CAPACITY ────────────────────────────────────────────── */
.capacity-visual {
  display: flex; align-items: center; gap: 24px;
  margin-bottom: 24px;
}
.gauge-wrap { flex-shrink: 0; width: 120px; height: 120px; }
.gauge-svg { width: 100%; height: 100%; }
.gauge-pct-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px; font-weight: 700;
}
.gauge-sub-text {
  font-size: 9px; font-family: 'DM Sans', sans-serif;
  font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em;
}
.capacity-stats { display: flex; gap: 0; align-items: center; flex: 1; }
.cap-stat { text-align: center; flex: 1; }
.cap-stat-val { font-size: 22px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-1); }
.cap-stat-lbl { font-size: 10px; color: var(--text-3); margin-top: 3px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.cap-divider { width: 1px; height: 40px; background: var(--border); flex-shrink: 0; }

.ward-breakdown { display: flex; flex-direction: column; gap: 10px; }
.ward-row { display: grid; grid-template-columns: 72px 1fr 36px; align-items: center; gap: 10px; }
.ward-name { font-size: 12px; color: var(--text-2); font-weight: 500; }
.ward-track { height: 5px; background: var(--surface-3); border-radius: 10px; overflow: hidden; }
.ward-fill { height: 100%; border-radius: 10px; transition: width 1.2s cubic-bezier(.4,0,.2,1); }
.ward-pct { font-size: 11px; font-weight: 600; font-family: 'JetBrains Mono', monospace; text-align: right; }

/* ─── INFLOW ──────────────────────────────────────────────── */
.inflow-total { text-align: right; }
.inflow-num { font-size: 28px; font-weight: 700; letter-spacing: -0.04em; color: var(--text-1); display: block; }
.inflow-lbl { font-size: 11px; color: var(--text-3); }

.bar-chart-area {
  position: relative; height: 100px;
}
.bar-chart {
  display: flex; align-items: flex-end; gap: 8px;
  height: 88px; padding-bottom: 0;
}
.bar-col {
  flex: 1;
  height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  gap: 4px;
  position: relative;
}
.bar-col:hover .bar-tooltip { opacity: 1; transform: translateY(0); }
.bar-tooltip {
  position: absolute; top: -26px;
  background: var(--text-1); border: 1px solid var(--text-1);
  color: #fff; font-size: 10px; font-weight: 600;
  padding: 2px 7px; border-radius: 5px;
  opacity: 0; transform: translateY(4px);
  transition: all 0.15s; pointer-events: none;
  white-space: nowrap;
}
.bar-fill {
  width: 90%;
  min-height: 8px;
  flex-shrink: 0;
  background: #e8f4f0;
  border-radius: 5px 5px 0 0;
  transition: height 1s cubic-bezier(.4,0,.2,1);
}
.bar-fill.bar-today {
  background: linear-gradient(180deg, #3d9b7a, #e8f4f0);
  box-shadow: 0 -6px 14px rgba(61,155,122,0.3);
}
.bar-day { font-size: 10px; color: var(--text-3); font-family: 'JetBrains Mono', monospace; }



.chart-guides {
  position: absolute; inset: 0 0 20px 0;
  display: none;
  pointer-events: none;
}
.guide-line { width: 100%; height: 1px; background: var(--border); opacity: 0.5; }

/* ─── REVENUE ─────────────────────────────────────────────── */
.revenue-badge {
  background: var(--green-dim); color: var(--green);
  border: 1px solid var(--border-hi);
  font-size: 12px; font-weight: 700;
  padding: 4px 10px; border-radius: 20px;
}
.revenue-main { margin-bottom: 16px; }
.revenue-amount {
  font-size: 34px; font-weight: 700;
  letter-spacing: -0.04em; color: var(--text-1);
  font-family: 'JetBrains Mono', monospace;
}
.revenue-sub { font-size: 12px; color: var(--text-3); margin-top: 3px; }

.revenue-chart { margin-bottom: 18px; }
.rev-svg { width: 100%; height: 70px; display: block; }
.rev-labels {
  display: flex; justify-content: space-between;
  font-size: 10px; color: var(--text-3);
  font-family: 'JetBrains Mono', monospace;
  margin-top: 4px;
}

.rev-breakdown { display: flex; flex-direction: column; gap: 12px; }
.rev-item-top { display: flex; justify-content: space-between; margin-bottom: 5px; }
.rev-item-lbl { font-size: 12px; color: var(--text-2); font-weight: 500; }
.rev-item-val { font-size: 12px; color: var(--text-1); font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.rev-item-track { height: 4px; background: var(--surface-3); border-radius: 10px; overflow: hidden; }
.rev-item-fill {
  height: 100%; border-radius: 10px;
  background: linear-gradient(90deg, var(--green), rgba(16,185,129,0.5));
  transition: width 1.2s ease;
}

/* ─── AI PANEL ────────────────────────────────────────────── */
.ai-panel {
  border-color: var(--border-hi);
  background: linear-gradient(135deg, #ffffff, rgba(16,185,129,0.03));
}
.ai-panel.ai-offline { border-color: rgba(244,63,94,0.3); background: linear-gradient(135deg, #ffffff, rgba(244,63,94,0.03)); }

.ai-glow {
  position: absolute; top: -40px; right: -40px;
  width: 120px; height: 120px;
  background: radial-gradient(circle, rgba(16,185,129,0.08), transparent 70%);
  pointer-events: none;
}
.ai-brand { display: flex; align-items: center; gap: 10px; }
.ai-logo {
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--green-dim); border: 1px solid var(--border-hi);
  display: flex; align-items: center; justify-content: center;
  color: var(--green);
}
.ai-logo svg { width: 16px; height: 16px; }

.ai-status-pill {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; font-weight: 600;
  padding: 5px 12px; border-radius: 20px;
}
.ai-status-pill.online { background: var(--green-dim); color: var(--green); border: 1px solid var(--border-hi); }
.ai-status-pill.offline { background: rgba(244,63,94,0.1); color: var(--rose); border: 1px solid rgba(244,63,94,0.3); }
.ai-pulse {
  width: 7px; height: 7px; border-radius: 50%; background: currentColor;
  animation: blink 1s infinite;
}

.ai-metrics {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 0; border: 1px solid var(--border);
  border-radius: var(--radius-sm); overflow: hidden;
  margin-bottom: 16px;
}
.ai-metric {
  padding: 12px; text-align: center;
  border-right: 1px solid var(--border);
  background: var(--surface-2);
}
.ai-metric:last-child { border-right: none; }
.ai-metric-val {
  font-size: 18px; font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--green); letter-spacing: -0.02em;
}
.ai-metric-lbl { font-size: 10px; color: var(--text-3); margin-top: 3px; font-weight: 500; }

.activity-label { font-size: 11px; color: var(--text-3); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.activity-bars {
  display: flex; gap: 3px; align-items: flex-end;
  height: 32px;
}
.activity-bar {
  flex: 1; background: var(--green);
  border-radius: 2px;
  opacity: 0.45;
  animation: wave 1.5s ease-in-out infinite alternate;
}
@keyframes wave { 0%{opacity:0.15;transform:scaleY(0.4);} 100%{opacity:0.65;transform:scaleY(1);} }

.ai-footer {
  display: flex; gap: 16px;
  border-top: 1px solid var(--border);
  margin-top: 14px; padding-top: 14px;
}
.ai-footer-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-3); }
.ai-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px var(--green); }

.ai-offline-msg {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--rose);
  background: rgba(244,63,94,0.08);
  border: 1px solid rgba(244,63,94,0.2);
  border-radius: 9px; padding: 10px 14px;
}

/* ─── ALERTS ──────────────────────────────────────────────── */
.alert-count {
  font-size: 11px; font-weight: 600; color: var(--rose);
  background: rgba(244,63,94,0.1);
  border: 1px solid rgba(244,63,94,0.25);
  padding: 3px 9px; border-radius: 20px;
}
.alert-count-success {
  font-size: 11px; font-weight: 600; color: var(--green);
  background: var(--green-dim);
  border: 1px solid var(--border-hi);
  padding: 3px 9px; border-radius: 20px;
}
.alert-list { display: flex; flex-direction: column; gap: 0; }
.alert-item {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.alert-item:last-child { border-bottom: none; padding-bottom: 0; }
.alert-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.alert-item.crit .alert-dot { background: var(--rose); box-shadow: 0 0 6px var(--rose); }
.alert-item.warn .alert-dot { background: var(--amber); box-shadow: 0 0 6px var(--amber); }
.alert-item.info .alert-dot { background: var(--blue); box-shadow: 0 0 6px var(--blue); }
.alert-item.success .alert-dot { background: var(--green); box-shadow: 0 0 6px var(--green); }

.alert-msg { font-size: 13px; color: var(--text-1); font-weight: 500; line-height: 1.4; }
.alert-time { font-size: 11px; color: var(--text-3); margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

/* ─── HIDE SCROLLBAR GLOBALLY ─── */
:global(::-webkit-scrollbar) {
  display: none !important; /* Chrome, Safari, Opera */
}

:global(*) {
  scrollbar-width: none !important; /* Firefox */
  -ms-overflow-style: none !important; /* IE and Edge */
}

/* ─── RESPONSIVE ──────────────────────────────────────────── */
@media (max-width: 1100px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .main-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .main-content { padding: 20px 16px; }
  .time-strip { padding: 10px 16px 0; }
  .kpi-strip { grid-template-columns: 1fr 1fr; }
  .page-title-row { flex-direction: column; gap: 14px; align-items: flex-start; }
  .ai-mini-chip { align-self: flex-start; }
}
</style>