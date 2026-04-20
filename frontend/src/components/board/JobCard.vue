<script setup>
import { computed } from 'vue'
import { useJobStore } from '../../stores/jobStore'

const props = defineProps({
    job: { type: Object, required: true },
})

// Wired to open the detail modal in Step 6
const emit = defineEmits(['select'])

const store = useJobStore()

const salaryDisplay = computed(() => {
    const { salary_min, salary_max } = props.job
    if (salary_min && salary_max) return `$${Math.round(salary_min / 1000)}k – $${Math.round(salary_max / 1000)}k`
    if (salary_min) return `From $${Math.round(salary_min / 1000)}k`
    if (salary_max) return `Up to $${Math.round(salary_max / 1000)}k`
    return null
})

function onDragStart(e) {
    e.dataTransfer.setData('text/plain', props.job.id)
    e.dataTransfer.effectAllowed = 'move'
}

function toggleStar(e) {
    e.stopPropagation()
    store.toggleStar(props.job.id)
}
</script>

<template>
    <div
        draggable="true"
        class="bg-white rounded-lg p-3 shadow-sm cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow select-none"
        @dragstart="onDragStart"
        @click="emit('select', job)"
    >
        <div class="flex items-start justify-between gap-2">
            <h3 class="text-sm font-medium text-gray-900 leading-tight">{{ job.title }}</h3>
            <button
                class="flex-shrink-0 text-lg leading-none transition-colors"
                :class="job.starred ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'"
                @click="toggleStar"
                aria-label="Toggle star"
            >
                ★
            </button>
        </div>

        <p v-if="job.company" class="text-xs text-gray-500 mt-1">{{ job.company }}</p>
        <p v-if="job.location" class="text-xs text-gray-400">{{ job.location }}</p>

        <p v-if="salaryDisplay" class="text-xs text-green-600 font-medium mt-2">
            {{ salaryDisplay }}
        </p>
    </div>
</template>