<script setup>
import { useJobStore } from '../../stores/jobStore'
import { KANBAN_COLUMNS } from '../../utils/constants'
import KanbanColumn from './KanbanColumn.vue'

const store = useJobStore()
</script>

<template>
    <main class="p-6 overflow-x-auto">
        <div class="flex gap-4" style="min-width: max-content;">
            <KanbanColumn
                v-for="col in KANBAN_COLUMNS"
                :key="col.key"
                :column="col"
                :jobs="store.jobsByStatus[col.key] || []"
            />
        </div>
    </main>
</template>