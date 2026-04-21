import { createRouter, createWebHistory } from 'vue-router'
import KanbanBoard from '../components/board/KanbanBoard.vue'

const routes = [
    { path: '/', component: KanbanBoard },
    { path: '/profile', component: () => import('../components/profile/ProfileConfig.vue') },
    { path: '/ingest',  component: () => import('../components/ingest/IngestConfig.vue') },
]

export default createRouter({
    history: createWebHistory(),
    routes,
})