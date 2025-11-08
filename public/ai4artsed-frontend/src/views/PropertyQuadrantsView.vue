<template>
  <div class="property-quadrants-view">
    <!-- Loading state -->
    <div v-if="store.isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>{{ currentLanguage === 'en' ? 'Loading configs...' : 'Lade Konfigurationen...' }}</p>
    </div>

    <!-- Error state -->
    <div v-else-if="store.error" class="error-state">
      <div class="error-icon">❌</div>
      <h2>{{ currentLanguage === 'en' ? 'Error loading configs' : 'Fehler beim Laden' }}</h2>
      <p>{{ store.error }}</p>
      <button class="retry-button" @click="store.loadConfigs()">
        {{ currentLanguage === 'en' ? 'Retry' : 'Erneut versuchen' }}
      </button>
    </div>

    <!-- Main canvas (single canvas, no grid!) -->
    <div v-else class="main-canvas">
      <!-- Properties in upper-left area -->
      <PropertyCanvas
        :property-pairs="store.propertyPairs"
        :selected-properties="store.selectedProperties"
        :canvas-width="canvasWidth"
        :canvas-height="canvasHeight"
        :current-language="currentLanguage"
        @toggle-property="handlePropertyToggle"
      />

      <!-- Configs distributed across entire canvas (avoiding property area) -->
      <!-- Only show after user selects properties -->
      <ConfigCanvas
        v-if="store.selectedProperties.length > 0"
        :configs="store.filteredConfigs"
        :selected-properties="store.selectedProperties"
        :match-count="store.matchCount"
        :canvas-width="canvasWidth"
        :canvas-height="canvasHeight"
        :is-dimmed="store.hasNoMatch"
        :current-language="currentLanguage"
        @select-config="handleConfigSelect"
      />

      <!-- No-match overlay -->
      <NoMatchState
        v-if="store.hasNoMatch"
        :partial-matches="store.partialMatches"
        :selected-properties-count="store.selectedProperties.length"
        :current-language="currentLanguage"
        @clear-selection="store.clearAllProperties()"
        @select-config="handleConfigSelect"
      />

      <!-- Header controls -->
      <div class="header-controls">
        <h1 class="page-title">
          {{ currentLanguage === 'en' ? 'Select Configuration' : 'Konfiguration auswählen' }}
        </h1>
        <div class="controls">
          <button
            v-if="store.selectedProperties.length > 0"
            class="clear-button"
            @click="store.clearAllProperties()"
          >
            {{ currentLanguage === 'en' ? 'Clear selection' : 'Auswahl löschen' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigSelectionStore } from '@/stores/configSelection'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import PropertyCanvas from '@/components/PropertyCanvas.vue'
import ConfigCanvas from '@/components/ConfigCanvas.vue'
import NoMatchState from '@/components/NoMatchState.vue'

/**
 * PropertyQuadrantsView - Phase 1 Property-Based Selection Interface
 *
 * Main view component that implements the 4-quadrant layout:
 * - Quadrant II (upper-left): Property bubbles with rubber bands
 * - Quadrants I, III, IV (others): Config tiles with random distribution
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 * Updated Session 36 - Use global userPreferences store for language
 */

const store = useConfigSelectionStore()
const userPreferences = useUserPreferencesStore()
const router = useRouter()

// Language from global store (site-wide preference)
const currentLanguage = computed(() => userPreferences.language)

// Canvas dimensions (full viewport)
const canvasWidth = ref(0)
const canvasHeight = ref(0)

function updateCanvasDimensions() {
  canvasWidth.value = window.innerWidth
  canvasHeight.value = window.innerHeight
}

function handlePropertyToggle(property: string) {
  store.toggleProperty(property)
}

function handleConfigSelect(configId: string) {
  // Navigate to config execution view (TODO: implement execution view)
  console.log('[PropertyQuadrants] Config selected:', configId)
  // router.push({ name: 'execute', params: { configId } })
}

onMounted(() => {
  // Clear any previous selection (fresh start)
  store.clearAllProperties()

  // Load configs from API
  store.loadConfigs()

  // Set initial dimensions
  updateCanvasDimensions()

  // Update on window resize
  window.addEventListener('resize', updateCanvasDimensions)
})

// Cleanup on unmount
onUnmounted(() => {
  window.removeEventListener('resize', updateCanvasDimensions)
})
</script>

<style scoped>
.property-quadrants-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #0a0a0a;
  color: #ffffff;
}

/* Loading/Error states */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 20px;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  font-size: 48px;
}

.error-state h2 {
  margin: 0;
  font-size: 24px;
}

.error-state p {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
}

.retry-button {
  padding: 12px 24px;
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border: 2px solid #60a5fa;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: #60a5fa;
  color: #0a0a0a;
  transform: scale(1.05);
}

/* Main canvas layout */
.main-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #0a0a0a;
}

/* Header controls */
.header-controls {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to bottom, rgba(10, 10, 10, 0.95), transparent);
  pointer-events: none;
  z-index: 150;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
}

.controls {
  display: flex;
  gap: 12px;
}

.clear-button {
  padding: 10px 20px;
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border: 2px solid #f87171;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  pointer-events: all;
}

.clear-button:hover {
  background: #f87171;
  color: #0a0a0a;
  transform: scale(1.05);
}
</style>
