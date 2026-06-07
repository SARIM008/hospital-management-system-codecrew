<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { useRoute } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()


const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const route = useRoute()
const mode = ref(route.query.mode === 'signup' ? 'signup' : 'login')
const loginForm = reactive({ email: '', password: '' })

const signupForm = reactive({
  name: '',
  email: '',
  phone: '',
  password: '',
  age: '',
  gender: '',
  address: ''
})

const showPassword = ref(false)
const showSignupPassword = ref(false)

const switchMode = (m) => {
  mode.value = m
  errorMessage.value = ''
  successMessage.value = ''
}

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    await authStore.loginPatient(loginForm.email, loginForm.password)
    router.push('/dashboard')
  } catch (err) {
    errorMessage.value = err?.response?.data?.error || err?.message || 'Login failed.'
  } finally {
    isLoading.value = false
  }
}

const handleSignup = async () => {
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await api.post('/signup', {
      name: signupForm.name,
      email: signupForm.email,
      phone: signupForm.phone,
      password: signupForm.password,
      age: signupForm.age || null,
      gender: signupForm.gender || null,
      address: signupForm.address || null,
    })
    successMessage.value = 'Account created! You can now log in.'
    setTimeout(() => switchMode('login'), 1800)
  } catch (err) {
    errorMessage.value = err?.response?.data?.error || 'Registration failed.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="page">

    <!-- Left panel — branding -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="logo-mark">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M28 16h-5l-4 12L11 4 7 16H4" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="brand-name">Ward<span>Wizard</span></div>
        <p class="brand-tagline">Intelligent hospital management for the modern era.</p>

        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 20 20" fill="none"><path d="M9 12l2 2 4-4M5 10a5 5 0 1010 0A5 5 0 005 10z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <span>Seamless patient record access</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 20 20" fill="none"><rect x="3" y="4" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M13 2v4M7 2v4M3 10h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
            </div>
            <span>Smart appointment scheduling</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 20 20" fill="none"><path d="M10 2a8 8 0 100 16A8 8 0 0010 2z" stroke="currentColor" stroke-width="1.6"/><path d="M10 6v4l3 3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
            </div>
            <span>Real-time ward monitoring</span>
          </div>
        </div>
      </div>

      <div class="brand-footer">© 2026 WardWizard · All rights reserved</div>
    </div>

    <!-- Right panel — form -->
    <div class="form-panel">
      <div class="form-box">

        <!-- Mode toggle -->
        <div class="mode-toggle">
          <button :class="['toggle-btn', { active: mode === 'login' }]" @click="switchMode('login')">Sign in</button>
          <button :class="['toggle-btn', { active: mode === 'signup' }]" @click="switchMode('signup')">Create account</button>
        </div>

        <!-- ── LOGIN ── -->
        <transition name="fade" mode="out-in">
          <div v-if="mode === 'login'" key="login">
            <div class="form-heading">
              <h1>Welcome back</h1>
              <p>Sign in to your patient account</p>
            </div>

            <form @submit.prevent="handleLogin" class="form-fields">

              <div class="field">
                <label>Email address</label>
                <div class="input-wrap">
                  <span class="input-icon">
                    <svg viewBox="0 0 20 20" fill="none"><path d="M3 5h14a1 1 0 011 1v8a1 1 0 01-1 1H3a1 1 0 01-1-1V6a1 1 0 011-1z" stroke="currentColor" stroke-width="1.5"/><path d="M2 6l8 5 8-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </span>
                  <input type="email" v-model="loginForm.email" placeholder="you@example.com" required autocomplete="email" />
                </div>
              </div>

              <div class="field">
                <label>Password</label>
                <div class="input-wrap">
                  <span class="input-icon">
                    <svg viewBox="0 0 20 20" fill="none"><rect x="4" y="9" width="12" height="9" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M7 9V6a3 3 0 016 0v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </span>
                  <input :type="showPassword ? 'text' : 'password'" v-model="loginForm.password" placeholder="••••••••" required autocomplete="current-password" />
                  <button type="button" class="eye-btn" @click="showPassword = !showPassword" tabindex="-1">
                    <svg v-if="!showPassword" viewBox="0 0 20 20" fill="none"><path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>
                    <svg v-else viewBox="0 0 20 20" fill="none"><path d="M3 3l14 14M8.5 8.6A2.5 2.5 0 0013.4 13M6.2 6.3C4.5 7.4 3 10 3 10s3 6 7 6c1.5 0 2.9-.6 4-1.5M10 4c4.5 0 7 6 7 6s-.7 1.5-2 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </button>
                </div>
              </div>

              <div v-if="errorMessage" class="alert alert-error">
                <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.5"/><path d="M10 7v3M10 13h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                {{ errorMessage }}
              </div>

              <button type="submit" class="submit-btn" :disabled="isLoading">
                <span v-if="isLoading" class="spinner"></span>
                <span>{{ isLoading ? 'Signing in…' : 'Sign in' }}</span>
                <svg v-if="!isLoading" viewBox="0 0 20 20" fill="none"><path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>

            </form>

            <p class="switch-hint">
              New patient?
              <button class="link-btn" @click="switchMode('signup')">Create an account →</button>
            </p>
          </div>

          <!-- ── SIGNUP ── -->
          <div v-else key="signup">
            <div class="form-heading">
              <h1>Create account</h1>
              <p>Register as a new patient</p>
            </div>

            <form @submit.prevent="handleSignup" class="form-fields">

              <div class="field">
                <label>Full name <span class="req">*</span></label>
                <div class="input-wrap">
                  <span class="input-icon">
                    <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="currentColor" stroke-width="1.5"/><path d="M3 18c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </span>
                  <input type="text" v-model="signupForm.name" placeholder="John Doe" required />
                </div>
              </div>

              <div class="two-col">
                <div class="field">
                  <label>Email <span class="req">*</span></label>
                  <div class="input-wrap">
                    <span class="input-icon">
                      <svg viewBox="0 0 20 20" fill="none"><path d="M3 5h14a1 1 0 011 1v8a1 1 0 01-1 1H3a1 1 0 01-1-1V6a1 1 0 011-1z" stroke="currentColor" stroke-width="1.5"/><path d="M2 6l8 5 8-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                    </span>
                    <input type="email" v-model="signupForm.email" placeholder="you@example.com" required />
                  </div>
                </div>
                <div class="field">
                  <label>Phone <span class="req">*</span></label>
                  <div class="input-wrap">
                    <span class="input-icon">
                      <svg viewBox="0 0 20 20" fill="none"><path d="M6 2h8a1 1 0 011 1v14a1 1 0 01-1 1H6a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="15.5" r="0.75" fill="currentColor"/></svg>
                    </span>
                    <input type="tel" v-model="signupForm.phone" placeholder="9876543210" required />
                  </div>
                </div>
              </div>

              <div class="field">
                <label>Password <span class="req">*</span></label>
                <div class="input-wrap">
                  <span class="input-icon">
                    <svg viewBox="0 0 20 20" fill="none"><rect x="4" y="9" width="12" height="9" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M7 9V6a3 3 0 016 0v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </span>
                  <input :type="showSignupPassword ? 'text' : 'password'" v-model="signupForm.password" placeholder="Choose a strong password" required />
                  <button type="button" class="eye-btn" @click="showSignupPassword = !showSignupPassword" tabindex="-1">
                    <svg v-if="!showSignupPassword" viewBox="0 0 20 20" fill="none"><path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>
                    <svg v-else viewBox="0 0 20 20" fill="none"><path d="M3 3l14 14M8.5 8.6A2.5 2.5 0 0013.4 13M6.2 6.3C4.5 7.4 3 10 3 10s3 6 7 6c1.5 0 2.9-.6 4-1.5M10 4c4.5 0 7 6 7 6s-.7 1.5-2 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </button>
                </div>
              </div>

              <div class="two-col">
                <div class="field">
                  <label>Age</label>
                  <div class="input-wrap">
                    <span class="input-icon">
                      <svg viewBox="0 0 20 20" fill="none"><path d="M10 2a8 8 0 100 16A8 8 0 0010 2z" stroke="currentColor" stroke-width="1.5"/><path d="M10 6v4l2.5 2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                    </span>
                    <input type="number" v-model="signupForm.age" placeholder="30" min="0" max="120" />
                  </div>
                </div>
                <div class="field">
                  <label>Gender</label>
                  <div class="input-wrap select-wrap">
                    <span class="input-icon">
                      <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="currentColor" stroke-width="1.5"/><path d="M3 18c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                    </span>
                    <select v-model="signupForm.gender">
                      <option value="">Select…</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                    <span class="select-arrow">
                      <svg viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </span>
                  </div>
                </div>
              </div>

              <div class="field">
                <label>Address</label>
                <div class="input-wrap">
                  <span class="input-icon" style="top: 14px; align-items: flex-start;">
                    <svg viewBox="0 0 20 20" fill="none"><path d="M10 2C7.2 2 5 4.2 5 7c0 4 5 11 5 11s5-7 5-11c0-2.8-2.2-5-5-5z" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="7" r="1.5" stroke="currentColor" stroke-width="1.5"/></svg>
                  </span>
                  <textarea v-model="signupForm.address" placeholder="123 Main Street, City…" rows="2"></textarea>
                </div>
              </div>

              <div v-if="errorMessage" class="alert alert-error">
                <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.5"/><path d="M10 7v3M10 13h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                {{ errorMessage }}
              </div>
              <div v-if="successMessage" class="alert alert-success">
                <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.5"/><path d="M7 10l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {{ successMessage }}
              </div>

              <button type="submit" class="submit-btn" :disabled="isLoading">
                <span v-if="isLoading" class="spinner"></span>
                <span>{{ isLoading ? 'Creating account…' : 'Create account' }}</span>
                <svg v-if="!isLoading" viewBox="0 0 20 20" fill="none"><path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>

            </form>

            <p class="switch-hint">
              Already registered?
              <button class="link-btn" @click="switchMode('login')">Sign in →</button>
            </p>
          </div>
        </transition>

      </div>
    </div>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap');

/* ── Reset & Root ───────────────────────────────────── */
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  display: flex;
  min-height: 100vh;
  font-family: 'Geist', -apple-system, sans-serif;
  background: #f6f8f7;
}

/* ── Brand Panel (left) ─────────────────────────────── */
.brand-panel {
  width: 420px;
  flex-shrink: 0;
  background: linear-gradient(160deg, #059669 0%, #065f46 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 52px 48px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

/* subtle grid texture */
.brand-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

/* decorative circle */
.brand-panel::after {
  content: '';
  position: absolute;
  bottom: -120px;
  right: -120px;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  pointer-events: none;
}

.brand-inner { position: relative; z-index: 1; }

.logo-mark {
  width: 48px;
  height: 48px;
  background: rgba(255,255,255,0.15);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  border: 1px solid rgba(255,255,255,0.2);
}
.logo-mark svg { width: 22px; height: 22px; }

.brand-name {
  font-size: 26px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.04em;
  margin-bottom: 12px;
}
.brand-name span { color: rgba(255,255,255,0.65); }

.brand-tagline {
  font-size: 15px;
  color: rgba(255,255,255,0.65);
  line-height: 1.6;
  max-width: 280px;
  margin-bottom: 52px;
  font-weight: 400;
}

.feature-list { display: flex; flex-direction: column; gap: 20px; }
.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  color: rgba(255,255,255,0.85);
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.01em;
}
.feature-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(255,255,255,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(255,255,255,0.15);
}
.feature-icon svg { width: 16px; height: 16px; color: #fff; }

.brand-footer {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
  position: relative;
  z-index: 1;
}

/* ── Form Panel (right) ─────────────────────────────── */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  overflow-y: auto;
}

.form-box {
  width: 100%;
  max-width: 420px;
}

/* ── Mode Toggle ────────────────────────────────────── */
.mode-toggle {
  display: flex;
  background: #edf2f0;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 36px;
  gap: 2px;
}
.toggle-btn {
  flex: 1;
  padding: 9px 0;
  border: none;
  background: transparent;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  font-family: inherit;
  transition: all .2s;
}
.toggle-btn.active {
  background: #ffffff;
  color: #065f46;
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* ── Form Heading ───────────────────────────────────── */
.form-heading { margin-bottom: 28px; }
.form-heading h1 {
  font-size: 24px;
  font-weight: 700;
  color: #0d1f2d;
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 6px;
}
.form-heading p {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 400;
}

/* ── Fields ─────────────────────────────────────────── */
.form-fields { display: flex; flex-direction: column; gap: 16px; }

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.field { display: flex; flex-direction: column; gap: 6px; }
.field label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  letter-spacing: 0.01em;
}
.req { color: #10b981; }

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 13px;
  display: flex;
  align-items: center;
  color: #9ca3af;
  pointer-events: none;
}
.input-icon svg { width: 16px; height: 16px; }

.input-wrap input,
.input-wrap select,
.input-wrap textarea {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1.5px solid #d1dbd7;
  border-radius: 10px;
  background: #ffffff;
  color: #0d1f2d;
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  appearance: none;
  -webkit-appearance: none;
}
.input-wrap textarea {
  resize: none;
  line-height: 1.5;
  padding-top: 10px;
}
.input-wrap input::placeholder,
.input-wrap textarea::placeholder { color: #c0ccc8; }

.input-wrap input:focus,
.input-wrap select:focus,
.input-wrap textarea:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16,185,129,0.12);
}

.eye-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  display: flex;
  align-items: center;
  padding: 2px;
  transition: color .15s;
}
.eye-btn:hover { color: #4b5563; }
.eye-btn svg { width: 16px; height: 16px; }

/* select arrow */
.select-wrap { position: relative; }
.select-arrow {
  position: absolute;
  right: 12px;
  pointer-events: none;
  color: #9ca3af;
  display: flex;
  align-items: center;
}
.select-arrow svg { width: 14px; height: 14px; }

/* ── Alerts ─────────────────────────────────────────── */
.alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}
.alert svg { width: 16px; height: 16px; flex-shrink: 0; }
.alert-error  { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.alert-success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }

/* ── Submit Button ──────────────────────────────────── */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 20px;
  background: #10b981;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  letter-spacing: -0.01em;
  transition: background .15s, transform .1s;
  margin-top: 4px;
}
.submit-btn svg { width: 16px; height: 16px; }
.submit-btn:hover:not(:disabled) { background: #059669; }
.submit-btn:active:not(:disabled) { transform: scale(0.99); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* spinner */
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Switch hint ────────────────────────────────────── */
.switch-hint {
  text-align: center;
  font-size: 13px;
  color: #94a3b8;
  margin-top: 24px;
}
.link-btn {
  background: none;
  border: none;
  color: #10b981;
  font-weight: 600;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  padding: 0;
  margin-left: 4px;
  transition: color .15s;
}
.link-btn:hover { color: #059669; }

/* ── Transition ─────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease, transform .18s ease; }
.fade-enter-from { opacity: 0; transform: translateY(8px); }
.fade-leave-to   { opacity: 0; transform: translateY(-8px); }

/* ── Responsive ─────────────────────────────────────── */
@media (max-width: 768px) {
  .brand-panel { display: none; }
  .form-panel { padding: 32px 20px; }
}
</style>