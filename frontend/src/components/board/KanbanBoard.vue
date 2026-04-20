<script setup>
import { onMounted, ref } from 'vue'
import { useJobStore } from '../../stores/jobStore'
import { KANBAN_COLUMNS } from '../../utils/constants'
import KanbanColumn from './KanbanColumn.vue'
import JobDetailModal from '../jobs/JobDetailModal.vue'
import AddJobForm from '../jobs/AddJobForm.vue'

const store = useJobStore()
const selectedJob = ref(null)
const showAddForm = ref(false)

onMounted(() => store.fetchJobs())
</script>

<template>
    <main class="p-6 flex flex-col gap-4">
        <!-- Toolbar -->
        <div class="flex items-center gap-4">
            <button
                class="flex items-center gap-2 px-4 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                @click="showAddForm = true"
            >
                <span class="text-base leading-none">+</span> Add Job
            </button>
            <input
                v-model="store.searchQuery"
                type="search"
                placeholder="Search jobs..."
                class="w-64 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <span v-if="store.loading" class="text-sm text-gray-400">Loading…</span>
            <span v-if="store.error" class="text-sm text-red-500">{{ store.error }}</span>
        </div>

        <!-- Board -->
        <div class="overflow-x-auto pb-4">
            <div class="flex gap-4" style="min-width: max-content;">
                <KanbanColumn
                    v-for="col in KANBAN_COLUMNS"
                    :key="col.key"
                    :column="col"
                    :jobs="store.jobsByStatus[col.key] || []"
                    @drop-job="store.updateStatus($event, col.key)"
                    @select-job="selectedJob = $event"
                />
            </div>
        </div>
    </main>

    <!-- Add job form -->
    <AddJobForm
        v-if="showAddForm"
        @close="showAddForm = false"
    />

    <!-- Job detail modal -->
    <JobDetailModal
        v-if="selectedJob"
        :job="selectedJob"
        @close="selectedJob = null"
    />
</template>