<script setup>
import { onMounted, ref } from 'vue'
import { useJobStore } from '../../stores/jobStore'
import { KANBAN_COLUMNS } from '../../utils/constants'
import KanbanColumn from './KanbanColumn.vue'
import JobDetailModal from '../jobs/JobDetailModal.vue'
import AddJobForm from '../jobs/AddJobForm.vue'
import PasteJobInput from '../jobs/PasteJobInput.vue'

const store = useJobStore()
const selectedJob  = ref(null)
const showAddForm  = ref(false)
const showPasteForm = ref(false)
const selectedIds  = ref(new Set())

function toggleSelect(id) {
    const next = new Set(selectedIds.value)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    selectedIds.value = next
}

async function bulkDelete() {
    const count = selectedIds.value.size
    if (!confirm(`Delete ${count} job${count === 1 ? '' : 's'}? This cannot be undone.`)) return
    await store.deleteJobs([...selectedIds.value])
    selectedIds.value = new Set()
}

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
            <button
                class="flex items-center gap-2 px-4 py-1.5 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
                @click="showPasteForm = true"
            >
                ✦ Paste &amp; Parse
            </button>
            <input
                v-model="store.searchQuery"
                type="search"
                placeholder="Search jobs..."
                class="w-64 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
                :class="store.remoteOnly
                    ? 'px-3 py-1.5 text-sm rounded-lg font-medium bg-teal-600 text-white hover:bg-teal-700'
                    : 'px-3 py-1.5 text-sm rounded-lg font-medium bg-white border border-gray-300 text-gray-600 hover:bg-gray-50'"
                @click="store.remoteOnly = !store.remoteOnly"
            >
                Remote only
            </button>
            <span v-if="store.loading" class="text-sm text-gray-400">Loading…</span>
            <span v-if="store.error" class="text-sm text-red-500">{{ store.error }}</span>

            <!-- Bulk delete -->
            <div v-if="selectedIds.size > 0" class="flex items-center gap-2 ml-auto">
                <span class="text-sm text-gray-500">{{ selectedIds.size }} selected</span>
                <button
                    class="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
                    @click="bulkDelete"
                >
                    🗑 Delete
                </button>
                <button
                    class="text-sm text-gray-400 hover:text-gray-600"
                    @click="selectedIds = new Set()"
                >
                    Cancel
                </button>
            </div>
        </div>

        <!-- Board -->
        <div class="overflow-x-auto pb-4">
            <div class="flex gap-4" style="min-width: max-content;">
                <KanbanColumn
                    v-for="col in KANBAN_COLUMNS"
                    :key="col.key"
                    :column="col"
                    :jobs="store.jobsByStatus[col.key] || []"
                    :selected-ids="selectedIds"
                    @drop-job="store.updateStatus($event, col.key)"
                    @select-job="selectedJob = $event"
                    @toggle-select="toggleSelect"
                />
            </div>
        </div>
    </main>

    <!-- Add job form -->
    <AddJobForm
        v-if="showAddForm"
        @close="showAddForm = false"
    />

    <!-- Paste & parse form -->
    <PasteJobInput
        v-if="showPasteForm"
        @close="showPasteForm = false"
    />

    <!-- Job detail modal -->
    <JobDetailModal
        v-if="selectedJob"
        :job="selectedJob"
        @close="selectedJob = null"
    />
</template>