<template>
  <div class="music-generation-view">

    <!-- Single Continuous Flow (t2x pattern) -->
    <div class="phase-2a" ref="mainContainerRef">

      <!-- Section 1: Dual Input (Lyrics + Tags) -->
      <section class="input-section" ref="inputSectionRef">
        <!-- Lyrics Input (TEXT_1) -->
        <MediaInputBox
          icon="💡"
          :label="$t('musicGen.lyricsLabel')"
          :placeholder="$t('musicGen.lyricsPlaceholder')"
          v-model:value="lyricsInput"
          input-type="text"
          :rows="8"
          :is-filled="!!lyricsInput"
          @copy="copyLyrics"
          @paste="pasteLyrics"
          @clear="clearLyrics"
          @focus="focusedField = 'lyrics'"
          @blur="(val: string) => logPromptChange('lyrics', val)"
        />

        <!-- Tags Input (TEXT_2) -->
        <MediaInputBox
          icon="📋"
          :label="$t('musicGen.tagsLabel')"
          :placeholder="$t('musicGen.tagsPlaceholder')"
          v-model:value="tagsInput"
          input-type="text"
          :rows="3"
          :is-filled="!!tagsInput"
          @copy="copyTags"
          @paste="pasteTags"
          @clear="clearTags"
          @focus="focusedField = 'tags'"
          @blur="(val: string) => logPromptChange('tags', val)"
        />
      </section>

      <!-- START BUTTON #1: Dual Interception (Lyrics + Tags) -->
      <div class="start-button-container">
        <button
          class="start-button"
          :class="{ disabled: !lyricsInput }"
          :disabled="!lyricsInput"
          @click="runDualInterception()"
        >
          <span class="button-arrows button-arrows-left">>>></span>
          <span class="button-text">{{ $t('musicGen.refineButton') }}</span>
          <span class="button-arrows button-arrows-right">>>></span>
        </button>
      </div>

      <!-- Section 2: Dual Interception Results (Side by Side) -->
      <section class="interception-section dual-outputs" ref="interceptionSectionRef">
        <!-- Refined Lyrics (TEXT_1) -->
        <MediaInputBox
          icon="→"
          :label="$t('musicGen.refinedLyricsLabel')"
          :placeholder="$t('musicGen.refinedLyricsPlaceholder')"
          v-model:value="refinedLyrics"
          input-type="text"
          :rows="8"
          resize-type="auto"
          :is-empty="!refinedLyrics"
          :is-loading="isLyricsInterceptionLoading"
          :loading-message="$t('musicGen.refiningLyricsMessage')"
          :enable-streaming="true"
          :stream-url="lyricsStreamingUrl"
          :stream-params="lyricsStreamingParams"
          @stream-started="handleLyricsStreamStarted"
          @stream-complete="handleLyricsStreamComplete"
          @stream-error="handleLyricsStreamError"
          @copy="copyRefinedLyrics"
          @paste="pasteRefinedLyrics"
          @clear="clearRefinedLyrics"
          @focus="focusedField = 'refinedLyrics'"
          @blur="(val: string) => logPromptChange('refined_lyrics', val)"
        />

        <!-- Refined Tags (TEXT_2) -->
        <MediaInputBox
          icon="✨"
          :label="$t('musicGen.refinedTagsLabel')"
          :placeholder="$t('musicGen.refinedTagsPlaceholder')"
          v-model:value="refinedTags"
          input-type="text"
          :rows="8"
          resize-type="auto"
          :is-empty="!refinedTags"
          :is-loading="isTagsInterceptionLoading"
          :loading-message="$t('musicGen.refiningTagsMessage')"
          :enable-streaming="true"
          :stream-url="tagsStreamingUrl"
          :stream-params="tagsStreamingParams"
          @stream-started="handleTagsStreamStarted"
          @stream-complete="handleTagsStreamComplete"
          @stream-error="handleTagsStreamError"
          @copy="copyRefinedTags"
          @paste="pasteRefinedTags"
          @clear="clearRefinedTags"
          @focus="focusedField = 'refinedTags'"
          @blur="(val: string) => logPromptChange('refined_tags', val)"
        />
      </section>

      <!-- Section 3: Model Selection -->
      <section class="config-section">
        <h2 v-if="executionPhase !== 'initial'" class="section-title">{{ $t('musicGen.selectModel') }}</h2>
        <div class="config-bubbles-container">
          <div class="config-bubbles-row">
            <div
              v-for="config in availableConfigs"
              :key="config.id"
              class="config-bubble"
              :class="{
                selected: selectedConfig === config.id,
                hovered: hoveredConfigId === config.id
              }"
              :style="{ '--bubble-color': config.color }"
              @click="selectConfig(config.id)"
              @mouseenter="hoveredConfigId = config.id"
              @mouseleave="hoveredConfigId = null"
              role="button"
              :aria-pressed="selectedConfig === config.id"
              tabindex="0"
              @keydown.enter="selectConfig(config.id)"
              @keydown.space.prevent="selectConfig(config.id)"
            >
              <div class="bubble-emoji-medium">{{ config.emoji }}</div>

              <!-- Hover info -->
              <div v-if="hoveredConfigId === config.id" class="bubble-hover-info">
                <div class="hover-info-name">{{ config.name }}</div>
                <div class="hover-info-meta">
                  <div class="meta-row">
                    <span class="meta-label">{{ $t('musicGen.quality') }}</span>
                    <span class="meta-value">
                      <span class="stars-filled">{{ '★'.repeat(config.quality) }}</span><span class="stars-unfilled">{{ '☆'.repeat(5 - config.quality) }}</span>
                    </span>
                  </div>
                  <div class="meta-row">
                    <span class="meta-label">Speed</span>
                    <span class="meta-value">
                      <span class="stars-filled">{{ '★'.repeat(config.speed) }}</span><span class="stars-unfilled">{{ '☆'.repeat(5 - config.speed) }}</span>
                    </span>
                  </div>
                  <div class="meta-row">
                    <span class="meta-value duration-only">⏱ {{ config.duration }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- START BUTTON #2: Generate Music -->
      <div class="start-button-container">
        <button
          class="start-button"
          :class="{ disabled: !canGenerate }"
          :disabled="!canGenerate"
          @click="startGeneration()"
          ref="startButtonRef"
        >
          <span class="button-arrows button-arrows-left">>>></span>
          <span class="button-text">{{ $t('musicGen.generateButton') }}</span>
          <span class="button-arrows button-arrows-right">>>></span>
        </button>

        <transition name="fade">
          <div v-if="showSafetyStamp" class="safety-stamp">
            <div class="stamp-inner">
              <div class="stamp-icon">✓</div>
              <div class="stamp-text">Safety<br/>Approved</div>
            </div>
          </div>
        </transition>
      </div>

      <!-- OUTPUT BOX -->
      <MediaOutputBox
        ref="outputSectionRef"
        :output-image="outputAudio"
        media-type="music"
        :is-executing="isGenerating"
        :progress="generationProgress"
        :estimated-seconds="estimatedGenerationSeconds"
        :run-id="currentRunId"
        :is-favorited="isFavorited"
        @save="saveMedia"
        @download="downloadMedia"
        @toggle-favorite="toggleFavorite"
      />

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppClipboard } from '@/composables/useAppClipboard'
import { usePageContextStore } from '@/stores/pageContext'
import { useFavoritesStore } from '@/stores/favorites'
import { usePipelineExecutionStore } from '@/stores/pipelineExecution'
import type { PageContext, FocusHint } from '@/composables/usePageContext'
import axios from 'axios'
import MediaOutputBox from '@/components/MediaOutputBox.vue'
import MediaInputBox from '@/components/MediaInputBox.vue'

// ============================================================================
// i18n (temporary inline, move to i18n.ts later)
// ============================================================================

import { useI18n } from 'vue-i18n'
const { t } = useI18n()

// ============================================================================
// Types
// ============================================================================

interface MusicConfig {
  id: string
  name: string
  emoji: string
  color: string
  quality: number
  speed: number
  duration: string
}

type ExecutionPhase = 'initial' | 'interception_loading' | 'interception_done' | 'generating' | 'generation_done'

// ============================================================================
// STATE
// ============================================================================

const route = useRoute()
const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()
const pageContextStore = usePageContextStore()
const favoritesStore = useFavoritesStore()
const pipelineStore = usePipelineExecutionStore()

// Refs
const mainContainerRef = ref<HTMLElement | null>(null)
const inputSectionRef = ref<HTMLElement | null>(null)
const interceptionSectionRef = ref<HTMLElement | null>(null)
const startButtonRef = ref<HTMLButtonElement | null>(null)
const outputSectionRef = ref<InstanceType<typeof MediaOutputBox> | null>(null)

// Input state
const lyricsInput = ref('')
const tagsInput = ref('')
const focusedField = ref<'lyrics' | 'tags' | 'refinedLyrics' | 'refinedTags' | null>(null)

// Interception state - Dual (Lyrics + Tags)
const refinedLyrics = ref('')
const refinedTags = ref('')
const isLyricsInterceptionLoading = ref(false)
const isTagsInterceptionLoading = ref(false)
const lyricsStreamingUrl = ref('')
const lyricsStreamingParams = ref<Record<string, any>>({})
const tagsStreamingUrl = ref('')
const tagsStreamingParams = ref<Record<string, any>>({})

// Device ID for folder structure (json/date/device_id/run_xxx/)
// Combines permanent browser ID + date = valid until end of day
function getDeviceId(): string {
  let browserId = localStorage.getItem('browser_id')
  if (!browserId) {
    browserId = crypto.randomUUID?.() || `${Math.random().toString(36).substring(2, 10)}${Date.now().toString(36)}`
    localStorage.setItem('browser_id', browserId)
  }
  const today = new Date().toISOString().split('T')[0]
  return `${browserId}_${today}`
}

// Config selection
const selectedConfig = ref<string>('heartmula_standard')
const hoveredConfigId = ref<string | null>(null)

// Available music generation configs
const availableConfigs = ref<MusicConfig[]>([
  {
    id: 'heartmula_standard',
    name: 'HeartMuLa',
    emoji: '🎵',
    color: '#9C27B0',
    quality: 4,
    speed: 2,
    duration: '30-240s'
  }
])

// Generation state
const isGenerating = ref(false)
const generationProgress = ref(0)
const estimatedGenerationSeconds = ref(180)
const outputAudio = ref<string | null>(null)
const currentRunId = ref<string | null>(null)
const executionPhase = ref<ExecutionPhase>('initial')
const showSafetyStamp = ref(false)

// Favorites
const isFavorited = ref(false)

// Page Context for Trashy
const trashyFocusHint = computed<FocusHint>(() => {
  if (isGenerating.value || outputAudio.value) {
    return { x: 95, y: 85, anchor: 'bottom-right' }
  }
  return { x: 2, y: 95, anchor: 'bottom-left' }
})

const pageContext = computed<PageContext>(() => ({
  activeViewType: 'music_generation',
  pageContent: {
    inputText: lyricsInput.value,
    contextPrompt: tagsInput.value,
    refinedText: refinedLyrics.value
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

const canGenerate = computed(() => {
  // Can generate if we have lyrics (either original or refined) and a selected config
  const hasLyrics = refinedLyrics.value || lyricsInput.value
  return hasLyrics && selectedConfig.value && executionPhase.value !== 'generating'
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

function copyRefinedLyrics() {
  copyToClipboard(refinedLyrics.value)
}

async function pasteRefinedLyrics() {
  const text = await pasteFromClipboard()
  if (text) refinedLyrics.value = text
}

function clearRefinedLyrics() {
  refinedLyrics.value = ''
}

function copyRefinedTags() {
  copyToClipboard(refinedTags.value)
}

async function pasteRefinedTags() {
  const text = await pasteFromClipboard()
  if (text) refinedTags.value = text
}

function clearRefinedTags() {
  refinedTags.value = ''
}

// ============================================================================
// Methods - Logging
// ============================================================================

function logPromptChange(field: string, value: string) {
  console.log(`[MusicGen] ${field} changed:`, value.substring(0, 50))
}

// ============================================================================
// Methods - Config Selection
// ============================================================================

function selectConfig(configId: string) {
  selectedConfig.value = configId
  console.log('[MusicGen] Selected config:', configId)
}

// ============================================================================
// Methods - Dual Interception (Lyrics + Tags separately)
// ============================================================================

async function runDualInterception() {
  if (!lyricsInput.value) return

  executionPhase.value = 'interception_loading'

  // Start Lyrics Interception
  isLyricsInterceptionLoading.value = true
  refinedLyrics.value = ''

  // Use correct endpoint (same as text_transformation.vue)
  const isDev = import.meta.env.DEV
  lyricsStreamingUrl.value = isDev
    ? 'http://localhost:17802/api/schema/pipeline/interception'
    : '/api/schema/pipeline/interception'

  lyricsStreamingParams.value = {
    schema: 'lyrics_refinement',
    input_text: lyricsInput.value,
    safety_level: pipelineStore.safetyLevel,
    device_id: getDeviceId(),  // FIX: Persistent device_id for consistent folders
    enable_streaming: true,  // KEY: Request SSE streaming
    skip_wikipedia: 'true'  // Music: No Wikipedia research needed for lyrics/tags
  }

  // Start Tags Interception (if tags exist)
  if (tagsInput.value) {
    isTagsInterceptionLoading.value = true
    refinedTags.value = ''

    tagsStreamingUrl.value = isDev
      ? 'http://localhost:17802/api/schema/pipeline/interception'
      : '/api/schema/pipeline/interception'

    tagsStreamingParams.value = {
      schema: 'tags_generation',
      input_text: tagsInput.value,
      safety_level: pipelineStore.safetyLevel,
      device_id: getDeviceId(),  // FIX: Persistent device_id for consistent folders
      enable_streaming: true
    }
  } else {
    // No tags input, just use empty
    refinedTags.value = ''
  }

  console.log('[MusicGen] Starting dual interception (lyrics + tags)')
}

// Lyrics Stream Handlers
function handleLyricsStreamStarted() {
  console.log('[MusicGen] Lyrics stream started')
}

function handleLyricsStreamComplete(data: any) {
  console.log('[MusicGen] Lyrics stream complete:', data)
  // v-model already updated by MediaInputBox, no need to set refinedLyrics
  isLyricsInterceptionLoading.value = false
  checkInterceptionComplete()
}

function handleLyricsStreamError(error: string) {
  console.error('[MusicGen] Lyrics stream error:', error)
  isLyricsInterceptionLoading.value = false
  refinedLyrics.value = lyricsInput.value // Fallback
  checkInterceptionComplete()
}

// Tags Stream Handlers
function handleTagsStreamStarted() {
  console.log('[MusicGen] Tags stream started')
}

function handleTagsStreamComplete(data: any) {
  console.log('[MusicGen] Tags stream complete:', data)
  // v-model already updated by MediaInputBox, no need to set refinedTags
  isTagsInterceptionLoading.value = false
  checkInterceptionComplete()
}

function handleTagsStreamError(error: string) {
  console.error('[MusicGen] Tags stream error:', error)
  isTagsInterceptionLoading.value = false
  refinedTags.value = tagsInput.value || '' // Fallback
  checkInterceptionComplete()
}

// Check if both interceptions are done
function checkInterceptionComplete() {
  if (!isLyricsInterceptionLoading.value && !isTagsInterceptionLoading.value) {
    executionPhase.value = 'interception_done'
    // Scroll to next section
    nextTick(() => {
      if (interceptionSectionRef.value) {
        interceptionSectionRef.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })
  }
}

// ============================================================================
// Methods - Generation
// ============================================================================

async function startGeneration() {
  if (!canGenerate.value) return

  isGenerating.value = true
  executionPhase.value = 'generating'
  outputAudio.value = null
  generationProgress.value = 0
  showSafetyStamp.value = true

  // Use refined lyrics if available, otherwise original
  const finalLyrics = refinedLyrics.value || lyricsInput.value

  // Progress simulation
  const progressInterval = setInterval(() => {
    if (generationProgress.value < 98) {
      generationProgress.value += 0.5
    }
  }, 1000)

  try {
    // Use refined lyrics + tags if available, otherwise original
    const finalTags = refinedTags.value || tagsInput.value || ''

    // Call pipeline execution endpoint with dual text inputs (TEXT_1 + TEXT_2 separately)
    const response = await axios.post('/api/schema/pipeline/interception', {
      schema: 'heartmula', // Use heartmula interception config
      input_text: finalLyrics,
      output_config: selectedConfig.value,
      safety_level: pipelineStore.safetyLevel,
      device_id: getDeviceId(), // FIX: Persistent device_id for consistent export folders
      custom_placeholders: {
        TEXT_1: finalLyrics,
        TEXT_2: finalTags
      }
    })

    if (response.data.status === 'success') {
      const runId = response.data.run_id
      currentRunId.value = runId

      if (runId) {
        // Fetch music output
        await fetchMusicOutput(runId)
      }

      executionPhase.value = 'generation_done'
    } else {
      console.error('[MusicGen] Generation failed:', response.data.error)
    }
  } catch (error) {
    console.error('[MusicGen] Error:', error)
  } finally {
    clearInterval(progressInterval)
    generationProgress.value = 100
    isGenerating.value = false
    showSafetyStamp.value = false

    // Scroll to output
    nextTick(() => {
      if (outputSectionRef.value) {
        (outputSectionRef.value.$el as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })
  }
}

async function fetchMusicOutput(runId: string) {
  try {
    // Poll for music output
    const maxAttempts = 60 // 5 minutes max
    let attempts = 0

    while (attempts < maxAttempts) {
      const response = await axios.get(`/api/media/music/${runId}`)

      if (response.data.files && response.data.files.length > 0) {
        // Found music file
        const musicFile = response.data.files[0]
        outputAudio.value = `/api/media/file/${runId}/${musicFile}`
        console.log('[MusicGen] Music output:', outputAudio.value)
        return
      }

      // Wait and retry
      await new Promise(resolve => setTimeout(resolve, 5000))
      attempts++
    }

    console.error('[MusicGen] Timeout waiting for music output')
  } catch (error) {
    console.error('[MusicGen] Error fetching output:', error)
  }
}

// ============================================================================
// Methods - Media Actions
// ============================================================================

async function saveMedia() {
  if (outputAudio.value && currentRunId.value) {
    console.log('[MusicGen] Save media:', currentRunId.value)
    // Add to favorites - deviceId will be extracted from runId or use 'local'
    const deviceId = 'local' // TODO: Extract from run directory structure
    const success = await favoritesStore.addFavorite(
      currentRunId.value,
      'music',
      deviceId
    )
    if (success) {
      isFavorited.value = true
    }
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

function toggleFavorite() {
  if (currentRunId.value) {
    if (isFavorited.value) {
      favoritesStore.removeFavorite(currentRunId.value)
      isFavorited.value = false
    } else {
      saveMedia()
    }
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
    console.log('[MusicGen] Config from route:', configId)
  }

  // Check if run is favorited
  if (currentRunId.value) {
    isFavorited.value = favoritesStore.isFavorited(currentRunId.value)
  }
})
</script>

<style scoped>
/* Import t2x-consistent styles */
.music-generation-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 2rem 1rem;
}

.phase-2a {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Input Section - Side by Side */
.input-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .input-section {
    grid-template-columns: 1fr;
  }
}

/* Sections */
.interception-section,
.config-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Dual Outputs - Side by Side */
.interception-section.dual-outputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .interception-section.dual-outputs {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

/* Start Button Container */
.start-button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  position: relative;
}

.start-button {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 3rem;
  font-size: 1.2rem;
  font-weight: 600;
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
}

.start-button:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(156, 39, 176, 0.5);
}

.start-button.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.button-arrows {
  font-size: 0.8em;
  opacity: 0.7;
}

/* Config Bubbles */
.config-bubbles-container {
  display: flex;
  justify-content: center;
}

.config-bubbles-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.config-bubble {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 3px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.config-bubble:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.config-bubble.selected {
  border-color: var(--bubble-color, #9c27b0);
  background: rgba(var(--bubble-color-rgb, 156, 39, 176), 0.2);
}

.bubble-emoji-medium {
  font-size: 3rem;
}

/* Bubble Hover Info */
.bubble-hover-info {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  gap: 0.5rem;
}

.hover-info-name {
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
}

.hover-info-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.meta-label {
  opacity: 0.7;
}

.stars-filled {
  color: #fbbf24;
}

.stars-unfilled {
  color: rgba(255, 255, 255, 0.2);
}

.duration-only {
  text-align: center;
  opacity: 0.8;
}

/* Safety Stamp */
.safety-stamp {
  position: absolute;
  right: 0;
  animation: stamp-appear 0.4s ease-out;
}

@keyframes stamp-appear {
  from {
    transform: scale(0) rotate(-20deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0);
    opacity: 1;
  }
}

.stamp-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(34, 197, 94, 0.2);
  border: 2px solid #22c55e;
  border-radius: 8px;
  transform: rotate(-5deg);
}

.stamp-icon {
  font-size: 1.5rem;
  color: #22c55e;
}

.stamp-text {
  font-size: 0.7rem;
  font-weight: 600;
  color: #22c55e;
  text-align: center;
  text-transform: uppercase;
  line-height: 1.2;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 600px) {
  .music-generation-view {
    padding: 1rem 0.5rem;
  }

  .phase-2a {
    gap: 1.5rem;
  }

  .start-button {
    padding: 0.75rem 2rem;
    font-size: 1rem;
  }

  .config-bubble {
    width: 100px;
    height: 100px;
  }

  .bubble-emoji-medium {
    font-size: 2.5rem;
  }
}
</style>
