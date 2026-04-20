<script setup>
import { onMounted, ref, watch } from 'vue'
import { useProfileStore } from '../../stores/profileStore'

const store = useProfileStore()

// ── Form state ────────────────────────────────────────────────────────────────

const form = ref({
    skills:          [],
    target_titles:   [],
    location:        '',
    remote_pref:     'any',
    salary_floor:    null,
    exclusion_words: [],
})

const saved = ref(false)
const errorMsg = ref(null)

// Populate form once the profile loads
watch(
    () => store.profile,
    (p) => {
        if (!p) return
        form.value = {
            skills:          p.skills          ?? [],
            target_titles:   p.target_titles   ?? [],
            location:        p.location        ?? '',
            remote_pref:     p.remote_pref     ?? 'any',
            salary_floor:    p.salary_floor    ?? null,
            exclusion_words: p.exclusion_words ?? [],
        }
    },
    { immediate: true }
)

onMounted(() => store.fetchProfile())

// ── Tag input helpers ─────────────────────────────────────────────────────────

const newTitle = ref('')
const newExclusion = ref('')

function addTitle() {
    const val = newTitle.value.trim().replace(/,$/, '')
    if (val && !form.value.target_titles.includes(val)) form.value.target_titles.push(val)
    newTitle.value = ''
}

function addExclusion() {
    const val = newExclusion.value.trim().replace(/,$/, '')
    if (val && !form.value.exclusion_words.includes(val)) form.value.exclusion_words.push(val)
    newExclusion.value = ''
}

function removeTag(list, index) {
    list.splice(index, 1)
}

// ── Skill helpers ─────────────────────────────────────────────────────────────

const newSkill = ref({ name: '', level: 'intermediate' })

function addSkill() {
    const name = newSkill.value.name.trim()
    if (!name) return
    form.value.skills.push({ name, level: newSkill.value.level })
    newSkill.value = { name: '', level: 'intermediate' }
}

function removeSkill(index) {
    form.value.skills.splice(index, 1)
}

// ── Save ──────────────────────────────────────────────────────────────────────

async function save() {
    errorMsg.value = null
    saved.value = false
    try {
        await store.saveProfile({
            ...form.value,
            location:    form.value.location    || null,
            salary_floor: form.value.salary_floor || null,
            // Filter out any skills with an empty name
            skills: form.value.skills.filter(s => s.name.trim()),
        })
        saved.value = true
        setTimeout(() => { saved.value = false }, 3000)
    } catch {
        errorMsg.value = 'Failed to save. Please try again.'
    }
}

const REMOTE_OPTIONS = [
    { value: 'any',    label: 'Any' },
    { value: 'remote', label: 'Remote' },
    { value: 'hybrid', label: 'Hybrid' },
    { value: 'onsite', label: 'On-site' },
]

const LEVEL_OPTIONS = ['beginner', 'intermediate', 'advanced']
</script>

<template>
    <main class="p-6 max-w-2xl mx-auto">
        <h1 class="text-xl font-bold text-gray-800 mb-6">Profile</h1>

        <div v-if="store.loading" class="text-sm text-gray-400">Loading…</div>

        <div v-else class="flex flex-col gap-8">

            <!-- ── Location & Remote Pref ── -->
            <section class="flex flex-col gap-3">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Location</h2>
                <div class="flex flex-col sm:flex-row gap-4">
                    <div class="flex-1">
                        <label class="block text-xs font-medium text-gray-500 mb-1">City / State</label>
                        <input
                            v-model="form.location"
                            type="text"
                            placeholder="e.g. Austin, TX"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-500 mb-1">Remote Preference</label>
                        <div class="flex rounded-lg border border-gray-300 overflow-hidden text-sm">
                            <button
                                v-for="opt in REMOTE_OPTIONS"
                                :key="opt.value"
                                class="px-3 py-2 transition-colors"
                                :class="form.remote_pref === opt.value
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-600 hover:bg-gray-50'"
                                @click="form.remote_pref = opt.value"
                            >
                                {{ opt.label }}
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ── Salary Floor ── -->
            <section class="flex flex-col gap-3">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Salary Floor</h2>
                <div class="flex items-center gap-3">
                    <input
                        v-model.number="form.salary_floor"
                        type="number"
                        placeholder="e.g. 100000"
                        class="w-48 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                    <span class="text-xs text-gray-400">Minimum acceptable annual salary</span>
                </div>
            </section>

            <!-- ── Target Titles ── -->
            <section class="flex flex-col gap-3">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Target Job Titles</h2>
                <div class="flex flex-wrap gap-2 p-3 border border-gray-300 rounded-lg min-h-12 focus-within:ring-2 focus-within:ring-blue-400">
                    <span
                        v-for="(title, i) in form.target_titles"
                        :key="i"
                        class="flex items-center gap-1 bg-blue-100 text-blue-700 text-sm px-2 py-0.5 rounded-full"
                    >
                        {{ title }}
                        <button class="text-blue-400 hover:text-blue-700 leading-none" @click="removeTag(form.target_titles, i)">×</button>
                    </span>
                    <input
                        v-model="newTitle"
                        type="text"
                        placeholder="Type a title and press Enter…"
                        class="flex-1 min-w-40 text-sm outline-none bg-transparent"
                        @keydown.enter.prevent="addTitle"
                        @keydown="e => { if (e.key === ',') { e.preventDefault(); addTitle() } }"
                    />
                </div>
                <p class="text-xs text-gray-400">Press Enter or comma to add each title.</p>
            </section>

            <!-- ── Skills ── -->
            <section class="flex flex-col gap-3">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Skills</h2>

                <!-- Existing skills -->
                <div v-if="form.skills.length" class="flex flex-col gap-2">
                    <div
                        v-for="(skill, i) in form.skills"
                        :key="i"
                        class="flex items-center gap-3"
                    >
                        <input
                            v-model="skill.name"
                            type="text"
                            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                        <select
                            v-model="skill.level"
                            class="w-36 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
                        >
                            <option v-for="lvl in LEVEL_OPTIONS" :key="lvl" :value="lvl">
                                {{ lvl.charAt(0).toUpperCase() + lvl.slice(1) }}
                            </option>
                        </select>
                        <button class="text-gray-400 hover:text-red-500 text-lg leading-none" @click="removeSkill(i)">×</button>
                    </div>
                </div>

                <!-- Add new skill row -->
                <div class="flex items-center gap-3">
                    <input
                        v-model="newSkill.name"
                        type="text"
                        placeholder="Skill name (e.g. Python)"
                        class="flex-1 border border-dashed border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                        @keydown.enter.prevent="addSkill"
                    />
                    <select
                        v-model="newSkill.level"
                        class="w-36 border border-dashed border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
                    >
                        <option v-for="lvl in LEVEL_OPTIONS" :key="lvl" :value="lvl">
                            {{ lvl.charAt(0).toUpperCase() + lvl.slice(1) }}
                        </option>
                    </select>
                    <button
                        class="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-600 whitespace-nowrap"
                        @click="addSkill"
                    >
                        + Add
                    </button>
                </div>
            </section>

            <!-- ── Exclusion Words ── -->
            <section class="flex flex-col gap-3">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Exclusion Keywords</h2>
                <div class="flex flex-wrap gap-2 p-3 border border-gray-300 rounded-lg min-h-12 focus-within:ring-2 focus-within:ring-blue-400">
                    <span
                        v-for="(word, i) in form.exclusion_words"
                        :key="i"
                        class="flex items-center gap-1 bg-red-100 text-red-700 text-sm px-2 py-0.5 rounded-full"
                    >
                        {{ word }}
                        <button class="text-red-400 hover:text-red-700 leading-none" @click="removeTag(form.exclusion_words, i)">×</button>
                    </span>
                    <input
                        v-model="newExclusion"
                        type="text"
                        placeholder="e.g. senior, clearance required…"
                        class="flex-1 min-w-40 text-sm outline-none bg-transparent"
                        @keydown.enter.prevent="addExclusion"
                        @keydown="e => { if (e.key === ',') { e.preventDefault(); addExclusion() } }"
                    />
                </div>
                <p class="text-xs text-gray-400">Jobs containing these words will be flagged. Press Enter or comma to add.</p>
            </section>

            <!-- ── Save ── -->
            <div class="flex items-center gap-4 pt-2 border-t border-gray-100">
                <button
                    class="px-5 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 font-medium"
                    :disabled="store.saving"
                    @click="save"
                >
                    {{ store.saving ? 'Saving…' : 'Save Profile' }}
                </button>
                <span v-if="saved" class="text-sm text-green-600">Saved!</span>
                <span v-if="errorMsg" class="text-sm text-red-500">{{ errorMsg }}</span>
            </div>

        </div>
    </main>
</template>