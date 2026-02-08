import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useSafetyEventStore = defineStore('safetyEvent', () => {
  const pendingBlock = ref<{ stage: number | string; reason: string; foundTerms: string[]; vlmDescription?: string } | null>(null)
  const pendingAnalysis = ref<{ description: string; safe: boolean } | null>(null)

  function reportBlock(stage: number | string, reason: string, foundTerms: string[] = [], vlmDescription?: string) {
    pendingBlock.value = { stage, reason, foundTerms, vlmDescription }
  }

  function reportAnalysis(description: string, safe: boolean) {
    pendingAnalysis.value = { description, safe }
  }

  function consume() {
    const event = pendingBlock.value
    pendingBlock.value = null
    return event
  }

  function consumeAnalysis() {
    const event = pendingAnalysis.value
    pendingAnalysis.value = null
    return event
  }

  return { pendingBlock, pendingAnalysis, reportBlock, reportAnalysis, consume, consumeAnalysis }
})
