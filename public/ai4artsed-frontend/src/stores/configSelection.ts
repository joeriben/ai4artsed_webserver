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

export interface ConfigsResponse {
  configs: ConfigMetadata[]
  property_pairs: PropertyPair[]
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
      propertyPairs.value = data.property_pairs

      console.log(`[ConfigSelection] Loaded ${data.configs.length} configs, ${data.property_pairs.length} property pairs`)
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
    setProperties
  }
})
