<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useJobStore } from '../../stores/jobStore'
import { KANBAN_COLUMNS } from '../../utils/constants'

const emit = defineEmits(['close'])

const store = useJobStore()
const saving = ref(false)
const errorMsg = ref(null)

const form = ref({
    title:       '',
    company:     '',
    location:    '',
    salary_min:  null,
    salary_max:  null,
    url:         '',
    status:      'new_leads',
    description: '',
    notes:       '',
})

function buildPayload() {
    return Object.fromEntries(
        Object.entries(form.value).map(([k, v]) => [k, v === '' ? null : v])
    )
}

async function submit() {
    errorMsg.value = null
    saving.value = true
    try {
        await store.createJob(buildPayload())
        emit('close')
    } catch {
        errorMsg.value = 'Failed to create job. Please try again.'
    } finally {
        saving.value = false
    }
}

function onBackdropClick(e) {
    if (e.target === e.currentTarget) emit('close')
}

function onKeydown(e) {
    if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
    <Teleport to="body">
        <!-- Backdrop -->
        <div
            class="fixed inset-0 bg-black/50 z-50 flex items-start justify-center p-4 overflow-y-auto"
            @click="onBackdropClick"
        >
            <!-- Modal panel -->
            <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg my-8 flex flex-col">

                <!-- Header -->
                <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                    <h2 class="text-base font-semibold text-gray-800">Add Job</h2>
                    <button
                        class="text-gray-400 hover:text-gray-600 text-xl leading-none"
                        aria-label="Close"
                        @click="emit('close')"
                    >
                        ✕
                    </button>
                </div>

                <!-- Form body -->
                <div class="p-6 flex flex-col gap-4">

                    <!-- Title -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Title *</label>
                        <input
                            v-model="form.title"
                            type="text"
                            placeholder="e.g. Data Engineer"
                            autofocus
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                    </div>

                    <!-- Company + Location -->
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Company</label>
                            <input
                                v-model="form.company"
                                type="text"
                                placeholder="e.g. Acme Corp"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Location</label>
                            <input
                                v-model="form.location"
                                type="text"
                                placeholder="e.g. Remote"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                    </div>

                    <!-- Salary -->
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Salary Min</label>
                            <input
                                v-model.number="form.salary_min"
                                type="number"
                                placeholder="e.g. 100000"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Salary Max</label>
                            <input
                                v-model.number="form.salary_max"
                                type="number"
                                placeholder="e.g. 130000"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                    </div>

                    <!-- URL -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Job URL</label>
                        <input
                            v-model="form.url"
                            type="url"
                            placeholder="https://..."
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                    </div>

                    <!-- Status -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Starting Column</label>
                        <select
                            v-model="form.status"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
                        >
                            <option v-for="col in KANBAN_COLUMNS" :key="col.key" :value="col.key">
                                {{ col.label }}
                            </option>
                        </select>
                    </div>

                    <!-- Description -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Description</label>
                        <textarea
                            v-model="form.description"
                            rows="3"
                            placeholder="Paste the job description here…"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y"
                        />
                    </div>

                    <!-- Notes -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Notes</label>
                        <textarea
                            v-model="form.notes"
                            rows="2"
                            placeholder="Any personal notes…"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y"
                        />
                    </div>

                    <!-- Error -->
                    <p v-if="errorMsg" class="text-sm text-red-500">{{ errorMsg }}</p>
                </div>

                <!-- Footer -->
                <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100">
                    <button
                        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                        @click="emit('close')"
                    >
                        Cancel
                    </button>
                    <button
                        class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
                        :disabled="saving || !form.title"
                        @click="submit"
                    >
                        {{ saving ? 'Adding…' : 'Add Job' }}
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
</template>