import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useSafetyLevelStore = defineStore('safetyLevel', () => {
  const level = ref<string>('kids') // safest default until fetch completes
  const loaded = ref(false)
  const researchConfirmed = ref(false) // per-session compliance (resets on page reload)

  async function fetchLevel() {
    try {
      const baseUrl = import.meta.env.DEV ? 'http://localhost:17802' : ''
      const { data } = await axios.get(`${baseUrl}/api/settings/safety-level`)
      level.value = data.safety_level
      loaded.value = true
    } catch (e) {
      console.error('[SafetyLevel] Failed to fetch safety level:', e)
      // Keep 'kids' as safe default
      loaded.value = true
    }
  }

  const isAdvancedMode = computed(() => ['adult', 'research'].includes(level.value))
  const isResearchMode = computed(() => level.value === 'research')

  function confirmResearch() {
    researchConfirmed.value = true
  }

  return { level, loaded, isAdvancedMode, isResearchMode, researchConfirmed, fetchLevel, confirmResearch }
})
