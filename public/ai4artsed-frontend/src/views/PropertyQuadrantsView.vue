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

    <!-- Main layout -->
    <div v-else class="main-layout">
      <!-- Header -->
      <header class="header-controls">
        <h1 class="page-title">
          AI4ArtsEd - AI-Lab
        </h1>
      </header>

      <!-- Debug: Show selected properties -->
      <!-- PropertyCanvas now handles both categories and configs -->
      <PropertyCanvas
        :selected-properties="store.selectedProperties"
        @toggle-property="handlePropertyToggle"
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigSelectionStore } from '@/stores/configSelection'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { usePipelineExecutionStore } from '@/stores/pipelineExecution'
import PropertyCanvas from '@/components/PropertyCanvas.vue'
import NoMatchState from '@/components/NoMatchState.vue'

const store = useConfigSelectionStore()
const userPreferences = useUserPreferencesStore()
const pipelineStore = usePipelineExecutionStore()
const router = useRouter()

const currentLanguage = computed(() => userPreferences.language)

function handlePropertyToggle(property: string) {
  console.log('[PropertyQuadrantsView] Toggle:', property)
  store.toggleProperty(property)
}

function handleConfigSelect(configId: string) {
  console.log('[PropertyQuadrants] Config selected:', configId)

  // Clear pipeline store for fresh start
  pipelineStore.clearAll()

  // Navigate to Phase 2 execution view
  router.push({ name: 'pipeline-execution', params: { configId } })
}

onMounted(() => {
  store.clearAllProperties()
  store.loadConfigs()
})
</script>

<style scoped>
/* Root: Fullscreen container */
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
  to { transform: rotate(360deg); }
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

/* Main layout: Flexbox column */
.main-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

/* Header */
.header-controls {
  flex-shrink: 0;
  padding: 1.25rem 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(10, 10, 10, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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
}

.clear-button:hover {
  background: #f87171;
  color: #0a0a0a;
  transform: scale(1.05);
}

/* Canvas-area removed - PropertyCanvas handles its own centering */
</style>
