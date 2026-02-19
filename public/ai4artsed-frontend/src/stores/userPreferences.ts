import { ref } from 'vue'
import { defineStore } from 'pinia'
import { SUPPORTED_LANGUAGES, type SupportedLanguage } from '../i18n'

const validCodes = SUPPORTED_LANGUAGES.map(l => l.code) as readonly string[]

/**
 * Pinia Store for Global User Preferences
 *
 * Manages:
 * - Global language selection for entire app
 * - Syncs with localStorage for persistence
 * - Syncs with vue-i18n locale for UI translations
 * - Used across all phases (Phase 1, 2, 3)
 *
 * Architecture Decision: Language selection is site-wide, not phase-specific
 */
export const useUserPreferencesStore = defineStore('userPreferences', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  /** Current language (default: German) */
  const language = ref<SupportedLanguage>('de')

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  /**
   * Load language from localStorage on store initialization
   */
  function initializeLanguage() {
    const savedLanguage = localStorage.getItem('ai4artsed_language')
    if (savedLanguage && validCodes.includes(savedLanguage)) {
      language.value = savedLanguage as SupportedLanguage
    }
  }

  // ============================================================================
  // ACTIONS
  // ============================================================================

  /**
   * Set language and sync with localStorage
   */
  function setLanguage(newLanguage: SupportedLanguage) {
    language.value = newLanguage
    localStorage.setItem('ai4artsed_language', newLanguage)
    console.log(`[UserPreferences] Language set to: ${newLanguage}`)
  }

  /**
   * Cycle to the next language in SUPPORTED_LANGUAGES
   */
  function toggleLanguage() {
    const currentIndex = SUPPORTED_LANGUAGES.findIndex(l => l.code === language.value)
    const nextIndex = (currentIndex + 1) % SUPPORTED_LANGUAGES.length
    setLanguage(SUPPORTED_LANGUAGES[nextIndex]!.code)
  }

  // Initialize from localStorage
  initializeLanguage()

  // ============================================================================
  // RETURN PUBLIC API
  // ============================================================================

  return {
    language,
    setLanguage,
    toggleLanguage
  }
})
