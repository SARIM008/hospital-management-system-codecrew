import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(JSON.parse(localStorage.getItem('hms_user')) || null)
    const token = ref(localStorage.getItem('hms_token') || null)
    const role = ref(localStorage.getItem('hms_role') || null)

    const isAuthenticated = computed(() => !!token.value)

    const setUser = (data) => {
        user.value = data.user
        token.value = data.token
        role.value = data.user?.role || null

        localStorage.setItem('hms_user', JSON.stringify(data.user))
        localStorage.setItem('hms_token', data.token)
        localStorage.setItem('hms_role', data.user?.role || '')
    }

    const loginPatient = async (email, password) => {
        const res = await api.post('/login', {
            email,
            password
        })
        setUser(res.data)
        return res.data
    }

    const loginAdminOrDoctor = async (email, password) => {
        const res = await api.post('/login', {
            email,
            password
        })
        setUser(res.data)
        return res.data
    }

    const logout = () => {
        user.value = null
        token.value = null
        role.value = null

        localStorage.removeItem('hms_user')
        localStorage.removeItem('hms_token')
        localStorage.removeItem('hms_role')

        window.location.href = '/login'
    }

    return {
        user,
        token,
        role,
        isAuthenticated,
        loginPatient,
        loginAdminOrDoctor,
        logout
    }
})