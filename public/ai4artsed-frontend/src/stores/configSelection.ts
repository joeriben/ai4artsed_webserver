import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// Type definitions
export interface ConfigMetadata {
  id: string
  name: { en: string; de: string }
  description: { en: string; de: string }
  short_description: { en: string; de: string }
  properties: string[]
  pipeline: string
  media_preferences?: {
    default_output?: string
  }
  // Backend sends icon/color as top-level fields
  icon?: string
  color?: string
  difficulty?: number
}

export type PropertyPair = [string, string]

// Session 40: Property symbols support
export interface PropertyPairV2 {
  id: number
  pair: [string, string]
  symbols: { [key: string]: string }
  labels: {
    de: { [key: string]: string }
    en: { [key: string]: string }
  }
  tooltips: {
    de: { [key: string]: string }
    en: { [key: string]: string }
  }
}

export interface SymbolData {
  symbol: string
  label: string
  tooltip: string
}

export interface ConfigsResponse {
  configs: ConfigMetadata[]
  property_pairs: PropertyPair[] | PropertyPairV2[]
  symbols_enabled?: boolean
}

/**
 * Pinia Store for Phase 1 Property-Based Config Selection
 *
 * Manages:
 * - Property selection with XOR logic (opposing properties within pairs)
 * - Config filtering based on selected properties (AND logic across pairs)
 * - API data fetching from /pipeline_configs_with_properties
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 */
export const useConfigSelectionStore = defineStore('configSelection', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  /** Selected properties (Set for O(1) lookup) */
  const selectedProperties = ref<Set<string>>(new Set())

  /** All available configs from API */
  const availableConfigs = ref<ConfigMetadata[]>([])

  /** Categories (extracted from config properties) */
  const categories = ref<string[]>([])

  /** Property pairs for XOR logic (DEPRECATED - keeping for compatibility) */
  const propertyPairs = ref<PropertyPair[]>([])

  /** Session 40: Symbols enabled flag */
  const symbolsEnabled = ref(false)

  /** Session 40: Symbol data map (property name -> SymbolData) */
  const symbolDataMap = ref<Map<string, SymbolData>>(new Map())

  /** Current language for labels/tooltips */
  const currentLanguage = ref<'de' | 'en'>('de')

  /** Loading state */
  const isLoading = ref(false)

  /** Error state */
  const error = ref<string | null>(null)

  // ============================================================================
  // COMPUTED
  // ============================================================================

  /**
   * Property pairs as a Map for O(1) opposite lookup
   * chill -> chaotic, chaotic -> chill, etc.
   */
  const propertyPairMap = computed(() => {
    const map = new Map<string, string>()
    propertyPairs.value.forEach(([a, b]) => {
      map.set(a, b)
      map.set(b, a)
    })
    return map
  })

  /**
   * Filtered configs based on selected properties
   * AND logic: Config must have ALL selected properties
   */
  const filteredConfigs = computed(() => {
    if (selectedProperties.value.size === 0) {
      return availableConfigs.value
    }

    return availableConfigs.value.filter(config => {
      // Check if config has ALL selected properties
      return Array.from(selectedProperties.value).every(prop =>
        config.properties.includes(prop)
      )
    })
  })

  /**
   * Number of configs matching current selection
   */
  const matchCount = computed(() => filteredConfigs.value.length)

  /**
   * Whether no configs match (no-match state)
   */
  const hasNoMatch = computed(() =>
    selectedProperties.value.size > 0 && matchCount.value === 0
  )

  /**
   * Partial matches for suggestions (configs matching at least 1 property)
   * Only relevant in no-match state
   */
  const partialMatches = computed(() => {
    if (!hasNoMatch.value) return []

    const matches = availableConfigs.value
      .map(config => {
        const matchingProps = Array.from(selectedProperties.value).filter(prop =>
          config.properties.includes(prop)
        )
        return {
          config,
          matchingProps,
          matchScore: matchingProps.length
        }
      })
      .filter(m => m.matchScore > 0)
      .sort((a, b) => b.matchScore - a.matchScore)

    return matches.slice(0, 5) // Top 5 suggestions
  })

  // ============================================================================
  // ACTIONS
  // ============================================================================

  /**
   * Load configs from API
   * Session 40: Now handles property_pairs_v2 with symbols
   */
  async function loadConfigs() {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/pipeline_configs_with_properties')

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data: ConfigsResponse = await response.json()

      availableConfigs.value = data.configs

      // NEW: Extract unique categories from config properties
      // Each config now has properties: ["semantics"] or ["arts"], etc.
      const uniqueCategories = [...new Set(
        data.configs.flatMap(c => c.properties)
      )]
      categories.value = uniqueCategories

      // Build symbol data map from config.icon (top-level field from backend)
      const newSymbolMap = new Map<string, SymbolData>()
      data.configs.forEach(config => {
        const category = config.properties[0] // Single category value

        if (category && config.icon && !newSymbolMap.has(category)) {
          newSymbolMap.set(category, {
            symbol: config.icon,
            label: '', // No labels - symbol only
            tooltip: ''
          })
        }
      })
      symbolDataMap.value = newSymbolMap

      console.log('[ConfigSelection] Symbol map:', Array.from(newSymbolMap.entries()))

      console.log(`[ConfigSelection] Loaded ${data.configs.length} configs, ${uniqueCategories.length} categories`)

      // Keep property_pairs for backward compatibility (but unused)
      propertyPairs.value = data.property_pairs as PropertyPair[]
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error loading configs'
      console.error('[ConfigSelection] Error loading configs:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle category selection
   * Implements XOR logic: Only ONE category active at a time
   *
   * @param category - Category to toggle
   */
  function toggleProperty(category: string) {
    if (selectedProperties.value.has(category)) {
      // Deselect category
      selectedProperties.value.delete(category)
    } else {
      // Select category and deselect ALL others (XOR across all categories)
      selectedProperties.value.clear()
      selectedProperties.value.add(category)
    }

    // Trigger reactivity
    selectedProperties.value = new Set(selectedProperties.value)
  }

  /**
   * Check if a property is selected
   */
  function isPropertySelected(property: string): boolean {
    return selectedProperties.value.has(property)
  }

  /**
   * Get opposite property from pair
   */
  function getOppositeProperty(property: string): string | undefined {
    return propertyPairMap.value.get(property)
  }

  /**
   * Clear all selected properties
   * @deprecated TODO: Prüfen, evtl. nicht mehr verwendet (UI-Button entfernt)
   */
  function clearAllProperties() {
    selectedProperties.value.clear()
    selectedProperties.value = new Set() // Trigger reactivity
  }

  /**
   * Select specific properties (for external control)
   */
  function setProperties(properties: string[]) {
    selectedProperties.value = new Set(properties)
  }

  /**
   * Get symbol data for a property (Session 40)
   */
  function getSymbolData(property: string): SymbolData | undefined {
    return symbolDataMap.value.get(property)
  }

  /**
   * Set current language for labels/tooltips (Session 40)
   */
  function setLanguage(lang: 'de' | 'en') {
    currentLanguage.value = lang
    // Reload configs to rebuild symbol data with new language
    if (symbolsEnabled.value) {
      loadConfigs()
    }
  }

  // ============================================================================
  // RETURN PUBLIC API
  // ============================================================================

  return {
    // State
    selectedProperties: computed(() => Array.from(selectedProperties.value)),
    availableConfigs: computed(() => availableConfigs.value),
    categories: computed(() => categories.value), // NEW: Categories list
    propertyPairs: computed(() => propertyPairs.value), // DEPRECATED
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    symbolsEnabled: computed(() => symbolsEnabled.value),
    currentLanguage: computed(() => currentLanguage.value),

    // Computed
    filteredConfigs,
    matchCount,
    hasNoMatch,
    partialMatches,

    // Actions
    loadConfigs,
    toggleProperty,
    isPropertySelected,
    getOppositeProperty,
    clearAllProperties,
    setProperties,
    getSymbolData,
    setLanguage
  }
})
