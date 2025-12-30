import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({
    sidebarHidden: false,
    isLocked: localStorage.getItem('cm_locked') === 'true',
    lockPassword: localStorage.getItem('cm_lock_pwd') || ''
  }),
  actions: {
    toggleSidebar() { this.sidebarHidden = !this.sidebarHidden },
    hideSidebar() { this.sidebarHidden = true },
    showSidebar() { this.sidebarHidden = false },
    lock(password: string) {
      this.isLocked = true;
      this.lockPassword = password;
      localStorage.setItem('cm_locked', 'true');
      localStorage.setItem('cm_lock_pwd', password);
    },
    unlock() {
      this.isLocked = false;
      this.lockPassword = '';
      localStorage.removeItem('cm_locked');
      localStorage.removeItem('cm_lock_pwd');
    }
  }
})

