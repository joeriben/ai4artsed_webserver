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

  /** Property pairs for XOR logic */
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

      // Check if we have symbols enabled (property_pairs_v2)
      symbolsEnabled.value = data.symbols_enabled || false

      if (symbolsEnabled.value && data.property_pairs.length > 0) {
        // Process property_pairs_v2 with symbols
        const pairsV2 = data.property_pairs as PropertyPairV2[]

        // Extract simple pairs for XOR logic
        propertyPairs.value = pairsV2.map(p => p.pair)

        // Build symbol data map
        const newSymbolMap = new Map<string, SymbolData>()
        pairsV2.forEach(pairData => {
          const [prop1, prop2] = pairData.pair
          const lang = currentLanguage.value

          // Symbol data for first property
          newSymbolMap.set(prop1, {
            symbol: pairData.symbols[prop1] || '',
            label: pairData.labels[lang]?.[prop1] || prop1,
            tooltip: pairData.tooltips[lang]?.[prop1] || ''
          })

          // Symbol data for second property
          newSymbolMap.set(prop2, {
            symbol: pairData.symbols[prop2] || '',
            label: pairData.labels[lang]?.[prop2] || prop2,
            tooltip: pairData.tooltips[lang]?.[prop2] || ''
          })
        })
        symbolDataMap.value = newSymbolMap

        console.log(`[ConfigSelection] Loaded ${data.configs.length} configs, ${pairsV2.length} property pairs (with symbols)`)
      } else {
        // Legacy format: simple pairs
        propertyPairs.value = data.property_pairs as PropertyPair[]
        symbolDataMap.value.clear()

        console.log(`[ConfigSelection] Loaded ${data.configs.length} configs, ${data.property_pairs.length} property pairs`)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error loading configs'
      console.error('[ConfigSelection] Error loading configs:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle property selection
   * Implements XOR logic: selecting a property deselects its opposite
   *
   * @param property - Property to toggle
   */
  function toggleProperty(property: string) {
    const opposite = propertyPairMap.value.get(property)

    if (selectedProperties.value.has(property)) {
      // Deselect property
      selectedProperties.value.delete(property)
    } else {
      // Select property
      selectedProperties.value.add(property)

      // Deselect opposite if it exists and is selected (XOR within pair)
      if (opposite && selectedProperties.value.has(opposite)) {
        selectedProperties.value.delete(opposite)
      }
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
    propertyPairs: computed(() => propertyPairs.value),
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
