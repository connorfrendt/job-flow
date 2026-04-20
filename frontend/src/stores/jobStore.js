import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

export const useJobStore = defineStore('jobs', () => {
    const jobs = ref([])
    const loading = ref(false)
    const error = ref(null)
    const searchQuery = ref('')

    // Filter client-side so search doesn't require a round-trip per keystroke
    const jobsByStatus = computed(() => {
        const query = searchQuery.value.toLowerCase()
        const visible = query
            ? jobs.value.filter(j =>
                j.title?.toLowerCase().includes(query) ||
                j.company?.toLowerCase().includes(query) ||
                j.location?.toLowerCase().includes(query)
            )
            : jobs.value

        return visible.reduce((acc, job) => {
            if (!acc[job.status]) acc[job.status] = []
            acc[job.status].push(job)
            return acc
        }, {})
    })

    async function fetchJobs() {
        loading.value = true
        error.value = null
        try {
            const { data } = await api.get('/jobs')
            jobs.value = data
        } catch {
            error.value = 'Failed to load jobs.'
        } finally {
            loading.value = false
        }
    }

    async function createJob(payload) {
        const { data } = await api.post('/jobs', payload)
        jobs.value.unshift(data)
    }

    async function updateJob(id, payload) {
        const { data } = await api.put(`/jobs/${id}`, payload)
        const index = jobs.value.findIndex(j => j.id === id)
        if (index !== -1) jobs.value[index] = data
    }

    async function deleteJob(id) {
        await api.delete(`/jobs/${id}`)
        jobs.value = jobs.value.filter(j => j.id !== id)
    }

    async function updateStatus(id, status) {
        const job = jobs.value.find(j => j.id === id)
        if (!job || job.status === status) return
        const previous = job.status
        job.status = status  // optimistic update
        try {
            await api.patch(`/jobs/${id}/status`, { status })
        } catch {
            job.status = previous  // revert on failure
        }
    }

    async function toggleStar(id) {
        const job = jobs.value.find(j => j.id === id)
        if (!job) return
        const newValue = !job.starred
        job.starred = newValue  // optimistic update
        try {
            await api.patch(`/jobs/${id}/star`, { starred: newValue })
        } catch {
            job.starred = !newValue  // revert on failure
        }
    }

    return { jobs, loading, error, searchQuery, jobsByStatus, fetchJobs, createJob, updateJob, deleteJob, updateStatus, toggleStar }
})