import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { getConfig, getConfigContext, type ConfigMetadata } from '@/services/api'

/**
 * Pinia Store for Phase 2 Pipeline Execution
 *
 * Manages:
 * - Selected config for execution
 * - User input text
 * - Meta-prompt (context) with edit tracking
 * - Execution settings (mode, safety level)
 * - Multilingual meta-prompt loading based on user language
 *
 * Phase 2 - Multilingual Context Editing Implementation
 */
export const usePipelineExecutionStore = defineStore('pipelineExecution', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  /** Selected config metadata */
  const selectedConfig = ref<ConfigMetadata | null>(null)

  /** User input text */
  const userInput = ref('')

  /** Meta-prompt (context) in current language */
  const metaPrompt = ref('')

  /** Original meta-prompt for comparison (detect modifications) */
  const originalMetaPrompt = ref('')

  /** Execution mode */
  const executionMode = ref<'eco' | 'fast' | 'best'>('eco')

  /** Safety level */
  const safetyLevel = ref<'kids' | 'youth' | 'adult'>('kids')

  /** Loading state */
  const isLoading = ref(false)

  /** Error state */
  const error = ref<string | null>(null)

  // ============================================================================
  // COMPUTED
  // ============================================================================

  /**
   * Whether meta-prompt has been modified from original
   */
  const metaPromptModified = computed(() => {
    return metaPrompt.value !== originalMetaPrompt.value && originalMetaPrompt.value !== ''
  })

  /**
   * Whether ready to execute (has config and user input)
   */
  const isReadyToExecute = computed(() => {
    return selectedConfig.value !== null && userInput.value.trim().length > 0
  })

  // ============================================================================
  // ACTIONS
  // ============================================================================

  /**
   * Set selected config and load its metadata
   *
   * @param configId - Config ID from Phase 1 selection
   */
  async function setConfig(configId: string) {
    isLoading.value = true
    error.value = null

    try {
      // Load config metadata
      const config = await getConfig(configId)
      selectedConfig.value = config

      console.log(`[PipelineExecution] Config set: ${configId}`)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load config'
      console.error('[PipelineExecution] Error loading config:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load meta-prompt (context) for selected language
   *
   * @param language - User's selected language
   */
  async function loadMetaPromptForLanguage(language: 'de' | 'en') {
    if (!selectedConfig.value) {
      console.warn('[PipelineExecution] No config selected')
      return
    }

    isLoading.value = true
    error.value = null

    try {
      // Fetch context from backend
      const contextData = await getConfigContext(selectedConfig.value.id)

      // Extract context in selected language
      let contextText: string

      if (typeof contextData.context === 'string') {
        // Old format (not yet translated)
        contextText = contextData.context
      } else {
        // New format {en: "...", de: "..."}
        contextText = contextData.context[language] || contextData.context.en || ''
      }

      // Set meta-prompt
      metaPrompt.value = contextText
      originalMetaPrompt.value = contextText

      console.log(
        `[PipelineExecution] Loaded meta-prompt for ${selectedConfig.value.id} (${language}): ${contextText.substring(0, 50)}...`
      )
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load meta-prompt'
      console.error('[PipelineExecution] Error loading meta-prompt:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update user input text
   *
   * @param text - New user input
   */
  function updateUserInput(text: string) {
    userInput.value = text
  }

  /**
   * Update meta-prompt (user editing)
   *
   * @param text - New meta-prompt text
   */
  function updateMetaPrompt(text: string) {
    metaPrompt.value = text
  }

  /**
   * Reset meta-prompt to original value
   */
  function resetMetaPrompt() {
    metaPrompt.value = originalMetaPrompt.value
    console.log('[PipelineExecution] Meta-prompt reset to original')
  }

  /**
   * Set execution mode
   */
  function setExecutionMode(mode: 'eco' | 'fast' | 'best') {
    executionMode.value = mode
  }

  /**
   * Set safety level
   */
  function setSafetyLevel(level: 'kids' | 'youth' | 'adult') {
    safetyLevel.value = level
  }

  /**
   * Clear all state (for new session)
   */
  function clearAll() {
    selectedConfig.value = null
    userInput.value = ''
    metaPrompt.value = ''
    originalMetaPrompt.value = ''
    executionMode.value = 'eco'
    safetyLevel.value = 'kids'
    error.value = null
    console.log('[PipelineExecution] State cleared')
  }

  // ============================================================================
  // RETURN PUBLIC API
  // ============================================================================

  return {
    // State
    selectedConfig: computed(() => selectedConfig.value),
    userInput: computed(() => userInput.value),
    metaPrompt: computed(() => metaPrompt.value),
    originalMetaPrompt: computed(() => originalMetaPrompt.value),
    executionMode: computed(() => executionMode.value),
    safetyLevel: computed(() => safetyLevel.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),

    // Computed
    metaPromptModified,
    isReadyToExecute,

    // Actions
    setConfig,
    loadMetaPromptForLanguage,
    updateUserInput,
    updateMetaPrompt,
    resetMetaPrompt,
    setExecutionMode,
    setSafetyLevel,
    clearAll
  }
})
