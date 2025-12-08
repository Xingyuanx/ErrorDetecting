import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({ sidebarHidden: false }),
  actions: {
    toggleSidebar() { this.sidebarHidden = !this.sidebarHidden },
    hideSidebar() { this.sidebarHidden = true },
    showSidebar() { this.sidebarHidden = false }
  }
})

