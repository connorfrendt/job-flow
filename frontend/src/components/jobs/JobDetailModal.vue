<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useJobStore } from '../../stores/jobStore'
import { KANBAN_COLUMNS } from '../../utils/constants'

const props = defineProps({
    job: { type: Object, required: true },
})
const emit = defineEmits(['close'])

const store = useJobStore()
const saving = ref(false)
const deleting = ref(false)

// Local editable copy — never mutate the store directly from a form
const form = ref({})

watch(
    () => props.job,
    (job) => {
        form.value = {
            title:          job.title ?? '',
            company:        job.company ?? '',
            location:       job.location ?? '',
            salary_min:     job.salary_min ?? null,
            salary_max:     job.salary_max ?? null,
            url:            job.url ?? '',
            description:    job.description ?? '',
            status:         job.status ?? 'new_leads',
            notes:          job.notes ?? '',
            contact_name:   job.contact_name ?? '',
            contact_email:  job.contact_email ?? '',
            follow_up_date: job.follow_up_date ?? '',
            starred:        job.starred ?? false,
        }
    },
    { immediate: true }
)

// Convert empty strings to null so the backend receives proper nulls
function buildPayload() {
    return Object.fromEntries(
        Object.entries(form.value).map(([k, v]) => [k, v === '' ? null : v])
    )
}

async function save() {
    saving.value = true
    try {
        await store.updateJob(props.job.id, buildPayload())
        emit('close')
    } finally {
        saving.value = false
    }
}

async function confirmDelete() {
    if (!confirm('Delete this job? This cannot be undone.')) return
    deleting.value = true
    try {
        await store.deleteJob(props.job.id)
        emit('close')
    } finally {
        deleting.value = false
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
            <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl my-8 flex flex-col">

                <!-- Header -->
                <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                    <h2 class="text-base font-semibold text-gray-800">Job Details</h2>
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

                    <!-- Fit score panel -->
                    <div
                        v-if="job.fit_score !== null && job.fit_score !== undefined"
                        class="rounded-lg p-3 flex flex-col gap-2"
                        :class="{
                            'bg-green-50 border border-green-100': job.fit_score >= 70,
                            'bg-yellow-50 border border-yellow-100': job.fit_score >= 40 && job.fit_score < 70,
                            'bg-red-50 border border-red-100': job.fit_score < 40,
                        }"
                    >
                        <div class="flex items-center gap-2">
                            <span
                                class="text-sm font-bold"
                                :class="{
                                    'text-green-700': job.fit_score >= 70,
                                    'text-yellow-700': job.fit_score >= 40 && job.fit_score < 70,
                                    'text-red-700': job.fit_score < 40,
                                }"
                            >
                                {{ job.fit_score }}% fit
                            </span>
                            <span class="text-xs text-gray-400">vs. your profile</span>
                        </div>
                        <ul v-if="job.fit_reasons?.length" class="flex flex-col gap-1">
                            <li
                                v-for="(r, i) in job.fit_reasons"
                                :key="i"
                                class="text-xs flex items-start gap-1.5"
                                :class="r.type === 'pro' ? 'text-green-700' : 'text-red-600'"
                            >
                                <span class="mt-px font-bold">{{ r.type === 'pro' ? '✓' : '✗' }}</span>
                                <span>{{ r.text }}</span>
                            </li>
                        </ul>
                    </div>

                    <!-- Title -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Title *</label>
                        <input
                            v-model="form.title"
                            type="text"
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
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Location</label>
                            <input
                                v-model="form.location"
                                type="text"
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
                        <div class="flex items-center justify-between mb-1">
                            <label class="text-xs font-medium text-gray-500">Job URL</label>
                            <a
                                v-if="form.url"
                                :href="form.url"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="text-xs text-blue-500 hover:underline"
                            >
                                Open posting ↗
                            </a>
                        </div>
                        <input
                            v-model="form.url"
                            type="url"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                    </div>

                    <!-- Status -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Status</label>
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
                            rows="4"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y"
                        />
                    </div>

                    <!-- Notes -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Notes</label>
                        <textarea
                            v-model="form.notes"
                            rows="3"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y"
                        />
                    </div>

                    <!-- Contact -->
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Contact Name</label>
                            <input
                                v-model="form.contact_name"
                                type="text"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Contact Email</label>
                            <input
                                v-model="form.contact_email"
                                type="email"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                    </div>

                    <!-- Follow-up date + Starred -->
                    <div class="flex items-end gap-6">
                        <div class="flex-1">
                            <label class="block text-xs font-medium text-gray-500 mb-1">Follow-up Date</label>
                            <input
                                v-model="form.follow_up_date"
                                type="date"
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                        <label class="flex items-center gap-2 pb-2 cursor-pointer">
                            <input v-model="form.starred" type="checkbox" class="w-4 h-4 rounded accent-yellow-400" />
                            <span class="text-sm text-gray-600">Starred</span>
                        </label>
                    </div>

                    <!-- Read-only metadata -->
                    <div class="flex flex-wrap gap-4 pt-3 border-t border-gray-100 text-xs text-gray-400">
                        <span>Source: {{ job.source }}</span>
                        <span v-if="job.date_found">Found: {{ new Date(job.date_found).toLocaleDateString() }}</span>
                        <span v-if="job.date_applied">Applied: {{ new Date(job.date_applied).toLocaleDateString() }}</span>
                    </div>
                </div>

                <!-- Footer -->
                <div class="flex items-center justify-between px-6 py-4 border-t border-gray-100">
                    <button
                        class="text-sm text-red-500 hover:text-red-700 disabled:opacity-40"
                        :disabled="deleting"
                        @click="confirmDelete"
                    >
                        {{ deleting ? 'Deleting…' : 'Delete job' }}
                    </button>
                    <div class="flex gap-3">
                        <button
                            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                            @click="emit('close')"
                        >
                            Cancel
                        </button>
                        <button
                            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
                            :disabled="saving || !form.title"
                            @click="save"
                        >
                            {{ saving ? 'Saving…' : 'Save' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>