<script setup>
import { onMounted, ref } from 'vue'
import { useJobStore } from '../../stores/jobStore'
import api from '../../services/api'

const jobStore = useJobStore()

// ── Form state ────────────────────────────────────────────────────────────────
const form = ref({
    keywords:         '',
    location:         '',
    country:          'us',
    max_pages:        2,
    results_per_page: 50,
})

const saving   = ref(false)
const saveMsg  = ref(null)
const saveErr  = ref(null)

// ── Trigger state ─────────────────────────────────────────────────────────────
const running   = ref(false)
const runResult = ref(null)
const runErr    = ref(null)

onMounted(async () => {
    try {
        const { data } = await api.get('/ingest/config')
        if (data) {
            form.value = {
                keywords:         data.keywords         ?? '',
                location:         data.location         ?? '',
                country:          data.country          ?? 'us',
                max_pages:        data.max_pages        ?? 2,
                results_per_page: data.results_per_page ?? 50,
            }
        }
    } catch {
        // No config saved yet — form stays at defaults
    }
})

async function saveConfig() {
    saveMsg.value = null
    saveErr.value = null
    saving.value  = true
    try {
        await api.put('/ingest/config', {
            ...form.value,
            location: form.value.location || null,
        })
        saveMsg.value = 'Saved!'
        setTimeout(() => { saveMsg.value = null }, 3000)
    } catch (e) {
        saveErr.value = e.response?.data?.detail || 'Failed to save.'
    } finally {
        saving.value = false
    }
}

async function runIngest() {
    runResult.value = null
    runErr.value    = null
    running.value   = true
    try {
        const { data } = await api.post('/ingest/trigger')
        runResult.value = data
        await jobStore.fetchJobs()  // refresh board with newly ingested jobs
    } catch (e) {
        runErr.value = e.response?.data?.detail || 'Ingest failed. Check your Adzuna credentials and config.'
    } finally {
        running.value = false
    }
}

const COUNTRIES = [
    { code: 'us', label: 'United States' },
    { code: 'gb', label: 'United Kingdom' },
    { code: 'au', label: 'Australia' },
    { code: 'ca', label: 'Canada' },
    { code: 'de', label: 'Germany' },
    { code: 'fr', label: 'France' },
    { code: 'nl', label: 'Netherlands' },
    { code: 'sg', label: 'Singapore' },
    { code: 'nz', label: 'New Zealand' },
    { code: 'za', label: 'South Africa' },
]
</script>

<template>
    <main class="p-6 max-w-2xl mx-auto">
        <h1 class="text-xl font-bold text-gray-800 mb-6">Ingest</h1>

        <div class="flex flex-col gap-8">

            <!-- ── Search Criteria ── -->
            <section class="flex flex-col gap-4">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Search Criteria</h2>

                <!-- Keywords -->
                <div>
                    <label class="block text-xs font-medium text-gray-500 mb-1">Keywords *</label>
                    <input
                        v-model="form.keywords"
                        type="text"
                        placeholder="e.g. data engineer, python developer"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                    <p class="text-xs text-gray-400 mt-1">Sent directly to Adzuna as the job search query.</p>
                </div>

                <!-- Location + Country -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Location</label>
                        <input
                            v-model="form.location"
                            type="text"
                            placeholder="e.g. Austin, TX"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Country</label>
                        <select
                            v-model="form.country"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
                        >
                            <option v-for="c in COUNTRIES" :key="c.code" :value="c.code">
                                {{ c.label }}
                            </option>
                        </select>
                    </div>
                </div>

                <!-- Max Pages + Results per page -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Pages to fetch</label>
                        <input
                            v-model.number="form.max_pages"
                            type="number"
                            min="1"
                            max="10"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                        <p class="text-xs text-gray-400 mt-1">1–10 pages per run</p>
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Results per page</label>
                        <input
                            v-model.number="form.results_per_page"
                            type="number"
                            min="10"
                            max="50"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                        <p class="text-xs text-gray-400 mt-1">10–50 (Adzuna max is 50)</p>
                    </div>
                </div>

                <!-- Save -->
                <div class="flex items-center gap-4 pt-1">
                    <button
                        class="px-5 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 font-medium"
                        :disabled="saving || !form.keywords.trim()"
                        @click="saveConfig"
                    >
                        {{ saving ? 'Saving…' : 'Save Config' }}
                    </button>
                    <span v-if="saveMsg" class="text-sm text-green-600">{{ saveMsg }}</span>
                    <span v-if="saveErr" class="text-sm text-red-500">{{ saveErr }}</span>
                </div>
            </section>

            <!-- ── Run Ingest ── -->
            <section class="flex flex-col gap-4 pt-6 border-t border-gray-100">
                <div>
                    <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Run Ingest</h2>
                    <p class="text-xs text-gray-400 mt-1">
                        Pulls jobs from Adzuna using the config above, deduplicates, filters by your profile exclusions and salary floor, scores each job, and adds new matches to the board.
                    </p>
                </div>

                <div class="flex items-center gap-4">
                    <button
                        class="flex items-center gap-2 px-5 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-40 font-medium"
                        :disabled="running || !form.keywords.trim()"
                        @click="runIngest"
                    >
                        <span
                            v-if="running"
                            class="inline-block w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin"
                        />
                        {{ running ? 'Ingesting…' : '▶ Run Now' }}
                    </button>
                    <span v-if="running" class="text-sm text-gray-400">This may take 30–60 seconds…</span>
                </div>

                <!-- Result summary -->
                <div
                    v-if="runResult"
                    class="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm flex flex-col gap-1"
                >
                    <p class="font-semibold text-green-800">Ingest complete</p>
                    <ul class="text-green-700 flex flex-col gap-0.5">
                        <li>Fetched from Adzuna: <strong>{{ runResult.fetched }}</strong></li>
                        <li>Saved to board: <strong>{{ runResult.saved }}</strong></li>
                        <li>Skipped (already exists): <strong>{{ runResult.skipped_dedup }}</strong></li>
                        <li>Filtered out (exclusions / salary): <strong>{{ runResult.skipped_filter }}</strong></li>
                    </ul>
                </div>

                <p v-if="runErr" class="text-sm text-red-500">{{ runErr }}</p>
            </section>

        </div>
    </main>
</template>