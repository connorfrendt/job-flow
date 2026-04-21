<template>
    <div class="min-h-screen bg-gray-100">
        <header class="bg-white shadow-sm sticky top-0 z-10">
            <div class="px-6 py-3 flex items-center gap-8">
                <span class="text-lg font-bold text-blue-600 tracking-tight">Job-Flow</span>
                <nav class="flex gap-6 text-sm font-medium">
                    <RouterLink
                        to="/"
                        class="text-gray-500 hover:text-blue-600 transition-colors"
                        active-class="text-blue-600"
                    >
                        Board
                    </RouterLink>
                    <RouterLink
                        to="/profile"
                        class="text-gray-500 hover:text-blue-600 transition-colors"
                        active-class="text-blue-600"
                    >
                        Profile
                    </RouterLink>
                    <RouterLink
                        to="/ingest"
                        class="text-gray-500 hover:text-blue-600 transition-colors"
                        active-class="text-blue-600"
                    >
                        Ingest
                    </RouterLink>
                </nav>
            </div>
        </header>
        <RouterView />
    </div>
</template>