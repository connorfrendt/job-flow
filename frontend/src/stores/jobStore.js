import { defineStore } from 'pinia'

export const useJobStore = defineStore('jobs', {
  state: () => ({
    jobs: [],
  }),
})