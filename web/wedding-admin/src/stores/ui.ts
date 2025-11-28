import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({ isPresentationMode: false }),
  actions: {
    togglePresentation() { this.isPresentationMode = !this.isPresentationMode }
  }
})

