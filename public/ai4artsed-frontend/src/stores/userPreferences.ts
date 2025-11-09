import { ref } from 'vue'
import { defineStore } from 'pinia'

/**
 * Pinia Store for Global User Preferences
 *
 * Manages:
 * - Global language selection (de/en) for entire app
 * - Syncs with localStorage for persistence
 * - Syncs with vue-i18n locale for UI translations
 * - Used across all phases (Phase 1, 2, 3)
 *
 * Architecture Decision: Language selection is site-wide, not phase-specific
 *
 * Phase 2 - Multilingual Context Editing Implementation
 */
export const useUserPreferencesStore = defineStore('userPreferences', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  /** Current language (default: German) */
  const language = ref<'de' | 'en'>('de')

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  /**
   * Load language from localStorage on store initialization
   */
  function initializeLanguage() {
    const savedLanguage = localStorage.getItem('ai4artsed_language')
    if (savedLanguage === 'en' || savedLanguage === 'de') {
      language.value = savedLanguage
    }
  }

  // ============================================================================
  // ACTIONS
  // ============================================================================

  /**
   * Set language and sync with localStorage and vue-i18n
   *
   * @param newLanguage - Language code ('de' or 'en')
   */
  function setLanguage(newLanguage: 'de' | 'en') {
    language.value = newLanguage
    localStorage.setItem('ai4artsed_language', newLanguage)

    console.log(`[UserPreferences] Language set to: ${newLanguage}`)
  }

  /**
   * Toggle between German and English
   */
  function toggleLanguage() {
    const newLanguage = language.value === 'de' ? 'en' : 'de'
    setLanguage(newLanguage)
  }

  // Initialize from localStorage
  initializeLanguage()

  // ============================================================================
  // RETURN PUBLIC API
  // ============================================================================

  return {
    // State (as computed for reactivity)
    language,

    // Actions
    setLanguage,
    toggleLanguage
  }
})
