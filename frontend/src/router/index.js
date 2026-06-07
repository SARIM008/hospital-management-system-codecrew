import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        // FIX 1: Safely redirect the root to login (Solves the missing Home.vue Vite error)
                {
        path: '/',
        component: () => import('../layouts/PublicLayout.vue'),
        children: [
            {
            path: '',
            name: 'home',
            component: () => import('../views/public/Home.vue') // you'll create this
            }
        ]
        },

        {
            path: '/dashboard',
            redirect: () => {
                const auth = useAuthStore()

                if (!auth.isAuthenticated) return '/login'
                if (auth.role === 'admin') return '/admin'
                // FIX 2: Correctly map the doctor role to the /doctor path
                if (auth.role === 'doctor') return '/doctor' 
                if (auth.role === 'patient') return '/patient'
                return '/login'
            }
        },

        {
            path: '/login',
            name: 'login',
            component: () => import('../views/Login.vue'),
            meta: { requiresGuest: true }
        },

        {
            path: '/admin',
            component: () => import('../layouts/MainLayout.vue'),
            meta: { requiresAuth: true, role: 'admin' },
            children: [
                { path: '', name: 'admin-dashboard', component: () => import('../views/admin/Dashboard.vue') },
                { path: 'patients', name: 'admin-patients', component: () => import('../views/admin/Patients.vue') },
                { path: 'appointments', name: 'admin-appointments', component: () => import('../views/admin/Appointments.vue') },
                { path: 'admissions', name: 'admin-admission', component: () => import('../views/admin/Admissions.vue') },
                { path: 'SOP', name: 'admin-SOP', component: () => import('../views/admin/SOP_docs.vue') },
                { path: 'Register', name: 'admin-register', component: () => import('../views/admin/Register.vue') },
                { path: 'billing', name: 'admin-billing', component: () => import('../views/admin/Billing.vue') },
                { path: 'inventory', name: 'admin-inventory', component: () => import('../views/admin/Inventory.vue') },
                
            ]
        },

        // FIX 3: The dedicated Doctor route block with the correct 'doctor' role meta
        {
            path: '/doctor',
            component: () => import('../layouts/MainLayout.vue'),
            meta: { requiresAuth: true, role: 'doctor' }, 
            children: [
                // Ensure this filename matches what your teammate named it!
                { path: '', name: 'doctor-dashboard', component: () => import('../views/doctor/Dashboard.vue') },
                { path: 'admissions', name: 'doctor-admissions', component: () => import('../views/doctor/Admissions.vue') }

            ]
        },

        {
            path: '/patient',
            component: () => import('../layouts/MainLayout.vue'),
            meta: { requiresAuth: true, role: 'patient' },
            children: [
                { path: '', name: 'patient-dashboard', component: () => import('../views/patient/Dashboard.vue') },
                { path: 'appointments', name: 'patient-appointments', component: () => import('../views/patient/Appointments.vue') },
                { path: 'records', name: 'patient-records', component: () => import('../views/patient/MyRecords.vue') },
                
            ]
        },

        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        }
    ]
})

// The Security Guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()
    const isAuthenticated = authStore.isAuthenticated
    const currentRole = authStore.role

    if (to.meta.requiresAuth && !isAuthenticated) {
        next({ name: 'login' })
    } else if (to.meta.requiresGuest && isAuthenticated) {
        next('/dashboard')
    } else if (to.meta.requiresAuth && to.meta.role && to.meta.role !== currentRole) {
        next('/dashboard')
    } else {
        next()
    }
})

export default router