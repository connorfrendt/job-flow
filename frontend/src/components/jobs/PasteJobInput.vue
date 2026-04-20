<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useJobStore } from '../../stores/jobStore'
import { KANBAN_COLUMNS } from '../../utils/constants'
import api from '../../services/api'

const emit = defineEmits(['close'])

const store = useJobStore()

// ── Phase: 'paste' → 'review' ─────────────────────────────────────────────────
const phase = ref('paste')

// ── Paste phase ───────────────────────────────────────────────────────────────
const rawText = ref('')
const parsing = ref(false)
const parseError = ref(null)

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
const skillsMentioned = ref([])

async function runParse() {
    parseError.value = null
    parsing.value = true
    try {
        const { data } = await api.post('/parse', { text: rawText.value })
        form.value = {
            title:       data.title       || '',
            company:     data.company     || '',
            location:    data.location    || '',
            salary_min:  data.salary_min  ?? null,
            salary_max:  data.salary_max  ?? null,
            url:         data.url         || '',
            status:      'new_leads',
            description: data.description || '',
            notes:       '',
        }
        skillsMentioned.value = data.skills_mentioned || []
        phase.value = 'review'
    } catch (e) {
        parseError.value = e.response?.data?.detail || 'Parse failed. Is ANTHROPIC_API_KEY set?'
    } finally {
        parsing.value = false
    }
}

// ── Review phase ──────────────────────────────────────────────────────────────
const saving = ref(false)
const saveError = ref(null)

function buildPayload() {
    return {
        ...Object.fromEntries(
            Object.entries(form.value).map(([k, v]) => [k, v === '' ? null : v])
        ),
        source: 'paste',
    }
}

async function submit() {
    saveError.value = null
    saving.value = true
    try {
        await store.createJob(buildPayload())
        emit('close')
    } catch {
        saveError.value = 'Failed to save job. Please try again.'
    } finally {
        saving.value = false
    }
}

// ── Modal UX ──────────────────────────────────────────────────────────────────
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
        <div
            class="fixed inset-0 bg-black/50 z-50 flex items-start justify-center p-4 overflow-y-auto"
            @click="onBackdropClick"
        >
            <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg my-8 flex flex-col">

                <!-- Header -->
                <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                    <div class="flex items-center gap-3">
                        <button
                            v-if="phase === 'review'"
                            class="text-gray-400 hover:text-gray-600 text-sm"
                            @click="phase = 'paste'"
                        >
                            ← Back
                        </button>
                        <h2 class="text-base font-semibold text-gray-800">
                            {{ phase === 'paste' ? 'Paste Job Description' : 'Review Parsed Job' }}
                        </h2>
                    </div>
                    <button
                        class="text-gray-400 hover:text-gray-600 text-xl leading-none"
                        aria-label="Close"
                        @click="emit('close')"
                    >
                        ✕
                    </button>
                </div>

                <!-- ── Paste phase ── -->
                <div v-if="phase === 'paste'" class="p-6 flex flex-col gap-4">
                    <p class="text-sm text-gray-500">
                        Paste a full job description below. Claude will extract the title, company, location, salary, and skills automatically.
                    </p>
                    <textarea
                        v-model="rawText"
                        rows="12"
                        placeholder="Paste the full job posting here…"
                        autofocus
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y"
                    />
                    <p v-if="parseError" class="text-sm text-red-500">{{ parseError }}</p>
                </div>

                <!-- ── Review phase ── -->
                <div v-else class="p-6 flex flex-col gap-4">

                    <!-- Skills chips (informational, read-only) -->
                    <div v-if="skillsMentioned.length" class="flex flex-wrap gap-1.5">
                        <span class="text-xs font-medium text-gray-500 self-center mr-1">Skills found:</span>
                        <span
                            v-for="skill in skillsMentioned"
                            :key="skill"
                            class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-100"
                        >
                            {{ skill }}
                        </span>
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
                                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                            />
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-500 mb-1">Salary Max</label>
                            <input
                                v-model.number="form.salary_max"
                                type="number"
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

                    <!-- Description (AI summary, editable) -->
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">
                            Description <span class="font-normal text-gray-400">(AI summary — editable)</span>
                        </label>
                        <textarea
                            v-model="form.description"
                            rows="3"
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

                    <p v-if="saveError" class="text-sm text-red-500">{{ saveError }}</p>
                </div>

                <!-- Footer -->
                <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100">
                    <button
                        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                        @click="emit('close')"
                    >
                        Cancel
                    </button>

                    <!-- Paste phase: Parse button -->
                    <button
                        v-if="phase === 'paste'"
                        class="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-40 flex items-center gap-2"
                        :disabled="parsing || !rawText.trim()"
                        @click="runParse"
                    >
                        <span
                            v-if="parsing"
                            class="inline-block w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin"
                        />
                        {{ parsing ? 'Analyzing…' : '✦ Parse with AI' }}
                    </button>

                    <!-- Review phase: Save button -->
                    <button
                        v-else
                        class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
                        :disabled="saving || !form.title"
                        @click="submit"
                    >
                        {{ saving ? 'Saving…' : 'Save Job' }}
                    </button>
                </div>

            </div>
        </div>
    </Teleport>
</template>