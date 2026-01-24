import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { PageContext, PageContent, FocusHint } from '@/composables/usePageContext'
import { DEFAULT_FOCUS_HINT, formatPageContextForLLM } from '@/composables/usePageContext'

/**
 * Pinia Store for Page Context
 *
 * Session 133+: Provides current page state for Träshy chat assistant
 * Replaces provide/inject pattern to work across component tree siblings
 *
 * Views call setPageContext() to update their state
 * ChatOverlay reads the store to get positioning and context info
 */
export const usePageContextStore = defineStore('pageContext', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  /** Current view type (e.g., 'text_transformation', 'canvas_workflow') */
  const activeViewType = ref<string>('')

  /** Page-specific content */
  const pageContent = ref<PageContent>({})

  /** Position hint for Träshy floating assistant */
  const focusHint = ref<FocusHint>(DEFAULT_FOCUS_HINT)

  // ============================================================================
  // COMPUTED
  // ============================================================================

  /** Full page context object */
  const context = computed<PageContext | null>(() => {
    if (!activeViewType.value) return null
    return {
      activeViewType: activeViewType.value,
      pageContent: pageContent.value,
      focusHint: focusHint.value
    }
  })

  /** Current focus hint (with default fallback) */
  const currentFocusHint = computed(() => focusHint.value || DEFAULT_FOCUS_HINT)

  // ============================================================================
  // ACTIONS
  // ============================================================================

  /**
   * Set the complete page context (called by views)
   */
  function setPageContext(ctx: PageContext) {
    activeViewType.value = ctx.activeViewType
    pageContent.value = ctx.pageContent
    focusHint.value = ctx.focusHint || DEFAULT_FOCUS_HINT
  }

  /**
   * Update only the focus hint (for dynamic positioning)
   */
  function setFocusHint(hint: FocusHint) {
    focusHint.value = hint
  }

  /**
   * Clear context (when leaving a view)
   */
  function clearContext() {
    activeViewType.value = ''
    pageContent.value = {}
    focusHint.value = DEFAULT_FOCUS_HINT
  }

  /**
   * Format context for LLM consumption
   */
  function formatForLLM(routePath: string): string {
    return formatPageContextForLLM(context.value, routePath)
  }

  // ============================================================================
  // RETURN
  // ============================================================================

  return {
    // State
    activeViewType,
    pageContent,
    focusHint,

    // Computed
    context,
    currentFocusHint,

    // Actions
    setPageContext,
    setFocusHint,
    clearContext,
    formatForLLM
  }
})
