<script setup>
import { ref } from 'vue'
import JobCard from './JobCard.vue'

defineProps({
    column: { type: Object, required: true },
    jobs:   { type: Array,  required: true },
})

const emit = defineEmits(['drop-job'])

const isDragOver = ref(false)

function onDragOver(e) {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    isDragOver.value = true
}

function onDragLeave(e) {
    // Only clear when leaving the column container itself, not a child card
    if (!e.currentTarget.contains(e.relatedTarget)) {
        isDragOver.value = false
    }
}

function onDrop(e) {
    isDragOver.value = false
    const id = e.dataTransfer.getData('text/plain')
    if (id) emit('drop-job', id)
}
</script>

<template>
    <div class="w-72 flex-shrink-0 flex flex-col">
        <!-- Column header -->
        <div class="flex items-center justify-between mb-2 px-1">
            <h2 class="text-sm font-semibold text-gray-600 uppercase tracking-wide">
                {{ column.label }}
            </h2>
            <span class="text-xs bg-gray-300 text-gray-600 font-medium px-2 py-0.5 rounded-full">
                {{ jobs.length }}
            </span>
        </div>

        <!-- Drop zone -->
        <div
            class="rounded-xl p-2 flex flex-col gap-2 min-h-24 transition-colors duration-150"
            :class="isDragOver ? 'bg-blue-100 ring-2 ring-blue-400' : 'bg-gray-200'"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
        >
            <JobCard
                v-for="job in jobs"
                :key="job.id"
                :job="job"
            />
            <p v-if="jobs.length === 0" class="text-xs text-gray-400 text-center py-4">
                No jobs here
            </p>
        </div>
    </div>
</template>