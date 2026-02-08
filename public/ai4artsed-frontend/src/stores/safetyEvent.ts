import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useSafetyEventStore = defineStore('safetyEvent', () => {
  const pendingBlock = ref<{ stage: number | string; reason: string; foundTerms: string[] } | null>(null)

  function reportBlock(stage: number | string, reason: string, foundTerms: string[] = []) {
    pendingBlock.value = { stage, reason, foundTerms }
  }

  function consume() {
    const event = pendingBlock.value
    pendingBlock.value = null
    return event
  }

  return { pendingBlock, reportBlock, consume }
})
