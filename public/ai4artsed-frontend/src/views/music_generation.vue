<template>
  <div class="music-generation-view">
    <!-- Main Content -->
    <div class="main-container">
      <!-- Info Box -->
      <div class="info-box" :class="{ 'expanded': infoExpanded }">
        <div class="info-header" @click="infoExpanded = !infoExpanded">
          <span class="info-icon">🎵</span>
          <span class="info-title">{{ t('musicGeneration.infoTitle') }}</span>
          <span class="info-toggle">{{ infoExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-if="infoExpanded" class="info-content">
          <p>{{ t('musicGeneration.infoDescription') }}</p>
          <div class="info-purpose">
            <strong>{{ t('musicGeneration.purposeTitle') }}</strong>
            <p>{{ t('musicGeneration.purposeText') }}</p>
          </div>
        </div>
      </div>

      <!-- Input Section -->
      <section class="input-section">
        <!-- Lyrics Input (TEXT_1) -->
        <MediaInputBox
          icon="🎤"
          :label="t('musicGeneration.lyricsLabel')"
          :placeholder="t('musicGeneration.lyricsPlaceholder')"
          v-model:value="lyricsInput"
          input-type="text"
          :rows="8"
          @copy="copyLyrics"
          @paste="pasteLyrics"
          @clear="clearLyrics"
        />

        <!-- Tags Input (TEXT_2) -->
        <MediaInputBox
          icon="🏷️"
          :label="t('musicGeneration.tagsLabel')"
          :placeholder="t('musicGeneration.tagsPlaceholder')"
          v-model:value="tagsInput"
          input-type="text"
          :rows="3"
          @copy="copyTags"
          @paste="pasteTags"
          @clear="clearTags"
        />

        <!-- Execute Button -->
        <button
          class="execute-button"
          :class="{ disabled: !canExecute }"
          :disabled="!canExecute"
          @click="executeGeneration"
        >
          <span class="button-text">{{ isExecuting ? t('musicGeneration.generating') : t('musicGeneration.generate') }}</span>
        </button>
      </section>

      <!-- Model Selection Section -->
      <section class="model-section">
        <h3 class="section-title">{{ t('musicGeneration.selectModel') }}</h3>
        <div class="model-bubbles">
          <div
            v-for="config in availableConfigs"
            :key="config.id"
            class="model-bubble"
            :class="{ selected: selectedConfig === config.id }"
            @click="selectConfig(config.id)"
          >
            <span class="model-icon">{{ config.icon }}</span>
            <span class="model-name">{{ config.name }}</span>
          </div>
        </div>
      </section>

      <!-- Output Section -->
      <section class="output-section">
        <MediaOutputBox
          ref="outputSectionRef"
          :output-image="outputAudio"
          media-type="music"
          :is-executing="isExecuting"
          :progress="generationProgress"
          @save="saveMedia"
          @download="downloadMedia"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import MediaOutputBox from '@/components/MediaOutputBox.vue'
import MediaInputBox from '@/components/MediaInputBox.vue'
import { useAppClipboard } from '@/composables/useAppClipboard'
import { usePageContextStore } from '@/stores/pageContext'
import type { PageContext, FocusHint } from '@/composables/usePageContext'

// ============================================================================
// i18n
// ============================================================================

const { t } = useI18n()

// ============================================================================
// Types
// ============================================================================

interface MusicConfig {
  id: string
  name: string
  icon: string
}

// ============================================================================
// STATE
// ============================================================================

const route = useRoute()
const infoExpanded = ref(false)
const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()

// Input state
const lyricsInput = ref('')
const tagsInput = ref('')

// Execution state
const isExecuting = ref(false)
const generationProgress = ref(0)
const outputAudio = ref<string | null>(null)
const currentRunId = ref<string | null>(null)

// Config selection
const selectedConfig = ref<string>('heartmula_standard')

// Available music generation configs
const availableConfigs = ref<MusicConfig[]>([
  { id: 'heartmula_standard', name: 'HeartMuLa', icon: '🎵' },
  { id: 'acestep_instrumental', name: 'AceStep', icon: '🎸' },
  { id: 'stableaudio', name: 'Stable Audio', icon: '🎹' }
])

// Page Context for Trashy
const pageContextStore = usePageContextStore()

const trashyFocusHint = computed<FocusHint>(() => {
  if (isExecuting.value || outputAudio.value) {
    return { x: 95, y: 85, anchor: 'bottom-right' }
  }
  return { x: 2, y: 95, anchor: 'bottom-left' }
})

const pageContext = computed<PageContext>(() => ({
  activeViewType: 'music_generation',
  pageContent: {
    inputText: lyricsInput.value,
    contextPrompt: tagsInput.value
  },
  focusHint: trashyFocusHint.value
}))

watch(pageContext, (ctx) => {
  pageContextStore.setPageContext(ctx)
}, { immediate: true, deep: true })

onUnmounted(() => {
  pageContextStore.clearContext()
})

// ============================================================================
// Computed
// ============================================================================

const canExecute = computed(() => {
  return lyricsInput.value.trim().length > 0 && !isExecuting.value
})

// ============================================================================
// Methods - Clipboard
// ============================================================================

function copyLyrics() {
  copyToClipboard(lyricsInput.value)
}

async function pasteLyrics() {
  const text = await pasteFromClipboard()
  if (text) lyricsInput.value = text
}

function clearLyrics() {
  lyricsInput.value = ''
}

function copyTags() {
  copyToClipboard(tagsInput.value)
}

async function pasteTags() {
  const text = await pasteFromClipboard()
  if (text) tagsInput.value = text
}

function clearTags() {
  tagsInput.value = ''
}

// ============================================================================
// Methods - Config Selection
// ============================================================================

function selectConfig(configId: string) {
  selectedConfig.value = configId
  console.log('[MusicGeneration] Selected config:', configId)
}

// ============================================================================
// Methods - Execution
// ============================================================================

async function executeGeneration() {
  if (!canExecute.value) return

  isExecuting.value = true
  outputAudio.value = null
  generationProgress.value = 0

  // Progress simulation (music generation takes longer)
  const durationSeconds = 180 * 0.9  // ~3 minutes
  const targetProgress = 98
  const updateInterval = 500
  const totalUpdates = (durationSeconds * 1000) / updateInterval
  const progressPerUpdate = targetProgress / totalUpdates

  const progressInterval = setInterval(() => {
    if (generationProgress.value < targetProgress) {
      generationProgress.value += progressPerUpdate
      if (generationProgress.value > targetProgress) {
        generationProgress.value = targetProgress
      }
    }
  }, updateInterval)

  try {
    // Use interception endpoint with custom_placeholders for dual-text input
    const response = await axios.post('/api/schema/pipeline/interception', {
      schema: selectedConfig.value,
      input_text: lyricsInput.value,  // TEXT_1 as primary
      output_config: selectedConfig.value,
      safety_level: 'youth',
      custom_placeholders: {
        TEXT_1: lyricsInput.value,
        TEXT_2: tagsInput.value
      }
    })

    if (response.data.status === 'success') {
      const runId = response.data.run_id
      currentRunId.value = runId

      if (runId) {
        // Fetch media output
        await fetchMusicOutput(runId)
      }
    } else {
      console.error('[MusicGeneration] Generation failed:', response.data.error)
    }
  } catch (error) {
    console.error('[MusicGeneration] Error:', error)
  } finally {
    clearInterval(progressInterval)
    generationProgress.value = 100
    isExecuting.value = false
  }
}

async function fetchMusicOutput(runId: string) {
  try {
    // Poll for music output
    const maxAttempts = 60  // 5 minutes max (5s interval)
    let attempts = 0

    while (attempts < maxAttempts) {
      const response = await axios.get(`/api/media/music/${runId}`)

      if (response.data.files && response.data.files.length > 0) {
        // Found music file
        const musicFile = response.data.files[0]
        outputAudio.value = `/api/media/file/${runId}/${musicFile}`
        console.log('[MusicGeneration] Music output:', outputAudio.value)
        return
      }

      // Wait and retry
      await new Promise(resolve => setTimeout(resolve, 5000))
      attempts++
    }

    console.error('[MusicGeneration] Timeout waiting for music output')
  } catch (error) {
    console.error('[MusicGeneration] Error fetching output:', error)
  }
}

// ============================================================================
// Methods - Media Actions
// ============================================================================

function saveMedia() {
  if (outputAudio.value) {
    console.log('[MusicGeneration] Save media:', outputAudio.value)
    // TODO: Implement save to favorites
  }
}

function downloadMedia() {
  if (outputAudio.value) {
    const a = document.createElement('a')
    a.href = outputAudio.value
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-')
    a.download = `ai4artsed_music_${timestamp}.mp3`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  // Check if config was passed via route
  const configId = route.params.configId as string
  if (configId) {
    selectedConfig.value = configId
    console.log('[MusicGeneration] Config from route:', configId)
  }
})
</script>

<style scoped>
.music-generation-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
  color: white;
  padding: 1rem;
}

.main-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Info Box */
.info-box {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.info-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.info-icon {
  font-size: 1.5rem;
}

.info-title {
  flex: 1;
  font-weight: 600;
  font-size: 1.1rem;
}

.info-toggle {
  opacity: 0.6;
}

.info-content {
  padding: 0 1rem 1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.info-purpose {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(156, 39, 176, 0.1);
  border-radius: 8px;
}

/* Input Section */
.input-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Execute Button */
.execute-button {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
}

.execute-button:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(156, 39, 176, 0.4);
}

.execute-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Model Selection */
.model-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 1rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.model-bubbles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.model-bubble {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-bubble:hover {
  background: rgba(255, 255, 255, 0.1);
}

.model-bubble.selected {
  background: rgba(156, 39, 176, 0.2);
  border-color: #9c27b0;
}

.model-icon {
  font-size: 1.25rem;
}

.model-name {
  font-weight: 500;
}

/* Output Section */
.output-section {
  min-height: 200px;
}

/* Responsive */
@media (max-width: 600px) {
  .music-generation-view {
    padding: 0.5rem;
  }

  .model-bubbles {
    flex-direction: column;
  }

  .model-bubble {
    justify-content: center;
  }
}
</style>
