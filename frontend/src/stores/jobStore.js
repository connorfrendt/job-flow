import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export const useJobStore = defineStore('jobs', () => {
    const jobs = ref([
        {
            id: '1',
            title: 'Data Engineer',
            company: 'TechCorp',
            location: 'Remote',
            salary_min: 130000,
            salary_max: 160000,
            status: 'new_leads',
            starred: false,
            source: 'manual',
        },
        {
            id: '2',
            title: 'ETL Developer',
            company: 'DataFlow Inc',
            location: 'Austin, TX',
            salary_min: 110000,
            salary_max: 130000,
            status: 'new_leads',
            starred: false,
            source: 'manual',
        },
        {
            id: '3',
            title: 'Data Pipeline Engineer',
            company: 'CloudBase',
            location: 'Remote',
            salary_min: 120000,
            salary_max: 145000,
            status: 'saved',
            starred: true,
            source: 'manual',
        },
        {
            id: '4',
            title: 'Senior Data Engineer',
            company: 'Fintech Co',
            location: 'New York, NY',
            salary_min: 140000,
            salary_max: 170000,
            status: 'applied',
            starred: true,
            source: 'manual',
        },
        {
            id: '5',
            title: 'Analytics Engineer',
            company: 'RetailCo',
            location: 'Chicago, IL',
            salary_min: 115000,
            salary_max: 135000,
            status: 'phone_screen',
            starred: false,
            source: 'manual',
        },
        {
            id: '6',
            title: 'Data Engineer II',
            company: 'HealthTech',
            location: 'Remote',
            salary_min: 125000,
            salary_max: 150000,
            status: 'interview',
            starred: true,
            source: 'manual',
        },
        {
            id: '7',
            title: 'Junior Data Engineer',
            company: 'StartupXYZ',
            location: 'Remote',
            salary_min: 90000,
            salary_max: 110000,
            status: 'rejected',
            starred: false,
            source: 'manual',
        },
    ])

    // Group jobs by status for the Kanban columns
    const jobsByStatus = computed(() => {
        return jobs.value.reduce((acc, job) => {
            if (!acc[job.status]) acc[job.status] = []
            acc[job.status].push(job)
            return acc
        }, {})
    })

    function toggleStar(id) {
        const job = jobs.value.find(j => j.id === id)
        if (job) job.starred = !job.starred
    }

    return { jobs, jobsByStatus, toggleStar }
})