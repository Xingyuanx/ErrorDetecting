import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useClusterStore = defineStore('cluster', () => {
  // 存储每个集群的采集开关状态，并从 localStorage 初始化
  const collectionStates = ref<Record<string, boolean>>(
    JSON.parse(localStorage.getItem('collection_states') || '{}')
  )

  const setCollectionState = (uuid: string, state: boolean) => {
    collectionStates.value[uuid] = state
    localStorage.setItem('collection_states', JSON.stringify(collectionStates.value))
  }

  const syncStates = (states: Record<string, boolean>) => {
    collectionStates.value = { ...collectionStates.value, ...states }
    localStorage.setItem('collection_states', JSON.stringify(collectionStates.value))
  }

  return {
    collectionStates,
    setCollectionState,
    syncStates
  }
})
