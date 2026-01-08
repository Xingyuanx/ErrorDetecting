import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useDark, useToggle } from '@vueuse/core'

export const useUIStore = defineStore('ui', () => {
  const sidebarHidden = ref(false)
  const isLocked = ref(localStorage.getItem('cm_locked') === 'true')
  const lockPassword = ref(localStorage.getItem('cm_lock_pwd') || '')
  
  const isDark = useDark()
  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  const toggleSidebar = () => { sidebarHidden.value = !sidebarHidden.value }
  const hideSidebar = () => { sidebarHidden.value = true }
  const showSidebar = () => { sidebarHidden.value = false }

  const lock = (password: string) => {
    isLocked.value = true
    lockPassword.value = password
    localStorage.setItem('cm_locked', 'true')
    localStorage.setItem('cm_lock_pwd', password)
  }

  const unlock = () => {
    isLocked.value = false
    lockPassword.value = ''
    localStorage.removeItem('cm_locked')
    localStorage.removeItem('cm_lock_pwd')
  }

  return {
    sidebarHidden,
    isLocked,
    lockPassword,
    isDark,
    toggleTheme,
    toggleSidebar,
    hideSidebar,
    showSidebar,
    lock,
    unlock
  }
})

