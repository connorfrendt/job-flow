import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

export const useProfileStore = defineStore('profile', () => {
    const profile = ref(null)
    const loading = ref(false)
    const saving = ref(false)

    async function fetchProfile() {
        loading.value = true
        try {
            const { data } = await api.get('/profile')
            profile.value = data
        } finally {
            loading.value = false
        }
    }

    async function saveProfile(payload) {
        saving.value = true
        try {
            const { data } = await api.put('/profile', payload)
            profile.value = data
        } finally {
            saving.value = false
        }
    }

    return { profile, loading, saving, fetchProfile, saveProfile }
})