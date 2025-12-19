<template>
  <div class="image-transformation-view">

    <div class="phase-2a" ref="mainContainerRef">

      <!-- Section 1: Image Upload + Context (Side by Side) -->
      <section class="input-context-section">
        <!-- Image Upload Bubble (LEFT) -->
        <MediaInputBox
          icon="💡"
          label="Dein Bild"
          v-model:value="uploadedImage"
          input-type="image"
          :initial-image="uploadedImage"
          :show-copy="false"
          :show-paste="false"
          @image-uploaded="handleImageUpload"
          @image-removed="handleImageRemove"
          @clear="clearImage"
        />

        <!-- Context Bubble (RIGHT) -->
        <MediaInputBox
          icon="📋"
          label="Sage was Du an dem Bild verändern möchtest"
          placeholder="Verwandle es in ein Ölgemälde... Mache es bunter... Füge einen Sonnenuntergang hinzu..."
          v-model:value="contextPrompt"
          input-type="text"
          :rows="6"
          :is-filled="!!contextPrompt"
          :is-required="!contextPrompt"
          @copy="copyContextPrompt"
          @paste="pasteContextPrompt"
          @clear="clearContextPrompt"
        />
      </section>

      <!-- Section 3: Category Selection (Horizontal Row) - Always visible after context -->
      <section v-if="canSelectMedia" class="category-section" ref="categorySectionRef">
        <div class="category-bubbles-row">
          <div
            v-for="category in availableCategories"
            :key="category.id"
            class="category-bubble"
            :class="{ selected: selectedCategory === category.id, disabled: category.disabled }"
            :style="{ '--bubble-color': category.color }"
            @click="!category.disabled && selectCategory(category.id)"
            role="button"
            :aria-pressed="selectedCategory === category.id"
            :aria-disabled="category.disabled"
            :tabindex="category.disabled ? -1 : 0"
            @keydown.enter="!category.disabled && selectCategory(category.id)"
            @keydown.space.prevent="!category.disabled && selectCategory(category.id)"
          >
            <div class="bubble-emoji-small">{{ category.emoji }}</div>
          </div>
        </div>
      </section>

      <!-- Section 3.5: Model Selection (appears BELOW category, filtered by selected category) -->
      <section v-if="selectedCategory" class="config-section">
        <h2 class="section-title">wähle ein Modell aus</h2>
        <div class="config-bubbles-container">
          <div class="config-bubbles-row">
            <div
              v-for="config in configsForCategory"
              :key="config.id"
              class="config-bubble"
              :class="{
                selected: selectedConfig === config.id,
                'light-bg': config.lightBg,
                disabled: false,
                hovered: hoveredConfigId === config.id
              }"
              :style="{ '--bubble-color': config.color }"
              @click="selectModel(config.id)"
              @mouseenter="hoveredConfigId = config.id"
              @mouseleave="hoveredConfigId = null"
              role="button"
              :aria-pressed="selectedConfig === config.id"
              tabindex="0"
            >
              <img v-if="config.logo" :src="config.logo" :alt="config.label" class="bubble-logo" />
              <div v-else class="bubble-emoji-medium">{{ config.emoji }}</div>

              <!-- Hover info overlay (shows INSIDE bubble when hovered) -->
              <div v-if="hoveredConfigId === config.id" class="bubble-hover-info">
                <div class="hover-info-name">{{ config.name }}</div>
                <div class="hover-info-meta">
                  <div class="meta-row">
                    <span class="meta-label">Qual.</span>
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
                    <span class="meta-value duration-only">⏱ {{ config.duration }} sec</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- START BUTTON (Always Visible) -->
      <div class="start-button-container">
        <button
          class="start-button"
          :class="{ disabled: !canStartGeneration || isPipelineExecuting }"
          :disabled="!canStartGeneration || isPipelineExecuting"
          @click="startGeneration"
        >
          <span class="button-arrows button-arrows-left">&gt;&gt;&gt;</span>
          <span class="button-text">Start</span>
          <span class="button-arrows button-arrows-right">&gt;&gt;&gt;</span>
        </button>

        <!-- Safety Stamp (next to button, not on image) -->
        <transition name="fade">
          <div v-if="showSafetyApprovedStamp" class="safety-stamp">
            <div class="stamp-inner">
              <div class="stamp-icon">✓</div>
              <div class="stamp-text">Safety<br/>Approved</div>
            </div>
          </div>
        </transition>
      </div>

      <!-- OUTPUT BOX (Template Component) -->
      <MediaOutputBox
        ref="pipelineSectionRef"
        :output-image="outputImage"
        :media-type="outputMediaType"
        :is-executing="isPipelineExecuting"
        :progress="generationProgress"
        :is-analyzing="isAnalyzing"
        :show-analysis="showAnalysis"
        :analysis-data="imageAnalysis"
        forward-button-title="Erneut Transformieren"
        @save="saveMedia"
        @print="printImage"
        @forward="sendToI2I"
        @download="downloadMedia"
        @analyze="analyzeImage"
        @image-click="showImageFullscreen"
        @close-analysis="showAnalysis = false"
      />

    </div>

    <!-- Fullscreen Image Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="fullscreenImage" class="fullscreen-modal" @click="fullscreenImage = null">
          <img :src="fullscreenImage" alt="Dein Bild" class="fullscreen-image" />
          <button class="close-fullscreen" @click="fullscreenImage = null">×</button>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import ImageUploadWidget from '@/components/ImageUploadWidget.vue'
import MediaOutputBox from '@/components/MediaOutputBox.vue'
import MediaInputBox from '@/components/MediaInputBox.vue'
import { usePipelineExecutionStore } from '@/stores/pipelineExecution'
import { useAppClipboard } from '@/composables/useAppClipboard'

// ============================================================================
// STATE
// ============================================================================

// Global clipboard (shared across all views)
const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()

// Image upload
const uploadedImage = ref<string | null>(null)  // Base64 preview URL
const uploadedImagePath = ref<string | null>(null)  // Server path
const uploadedImageId = ref<string | null>(null)

// Form inputs
const contextPrompt = ref('')
const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)  // User selects model from bubbles
const hoveredConfigId = ref<string | null>(null)  // For hover cards

// Phase 4: Seed management
const previousOptimizedPrompt = ref('')
const currentSeed = ref<number | null>(null)

// Execution
const executionPhase = ref<'initial' | 'image_uploaded' | 'ready_for_media' | 'generation_done'>('initial')
const isPipelineExecuting = ref(false)
const outputImage = ref<string | null>(null)
const outputMediaType = ref<string>('image')
const fullscreenImage = ref<string | null>(null)
const showSafetyApprovedStamp = ref(false)
const generationProgress = ref(0)
const estimatedDurationSeconds = ref<string>('30')  // Stores duration from backend (30s default if optimization skipped)

// Image Analysis
const isAnalyzing = ref(false)
const imageAnalysis = ref<{
  analysis: string
  reflection_prompts: string[]
  insights: string[]
  success: boolean
} | null>(null)
const showAnalysis = ref(false)

// Refs
const mainContainerRef = ref<HTMLElement | null>(null)
const categorySectionRef = ref<HTMLElement | null>(null)
const pipelineSectionRef = ref<any>(null) // MediaOutputBox component instance

// ============================================================================
// CONFIGURATION
// ============================================================================

interface Category {
  id: string
  label: string
  emoji: string
  color: string
  disabled?: boolean
}

const availableCategories: Category[] = [
  { id: 'image', label: 'Bild', emoji: '🖼️', color: '#4CAF50' },
  { id: 'video', label: 'Video', emoji: '🎬', color: '#9C27B0' },
  { id: 'sound', label: 'Sound', emoji: '🔊', color: '#FF9800', disabled: true }
]

// Available IMG2IMG Models (copied structure from text_transformation.vue)
interface ModelConfig {
  id: string
  label: string
  emoji: string
  name: string
  quality: number  // 1-5 stars
  speed: number    // 1-5 stars
  duration: string // e.g. "23" or "40-60"
  color: string    // Bubble color
  logo?: string    // Logo path
  lightBg?: boolean
}

const configsByCategory: Record<string, ModelConfig[]> = {
  image: [
    {
      id: 'qwen_img2img',
      label: 'Qwen',
      emoji: '🌸',
      name: 'QWEN Image Edit',
      quality: 3,
      speed: 5,
      duration: '23',
      color: '#9C27B0',
      logo: '/logos/Qwen_logo.png',
      lightBg: false
    },
    {
      id: 'flux2_img2img',
      label: 'Flux 2',
      emoji: '⚡',
      name: 'Flux2 Dev IMG2IMG',
      quality: 5,
      speed: 3,
      duration: '45',
      color: '#FF6B35',
      logo: '/logos/flux2_logo.png',
      lightBg: false
    }
  ],
  video: [
    {
      id: 'wan22_i2v_video',
      label: 'WAN 2.2',
      emoji: '🎬',
      name: 'WAN 2.2 Image-to-Video (14B)',
      quality: 4,
      speed: 3,
      duration: '35',
      color: '#9C27B0',
      logo: '/logos/wan_logo.png',
      lightBg: false
    }
  ],
  sound: []   // Future
}

// ============================================================================
// COMPUTED
// ============================================================================

const configsForCategory = computed(() => {
  if (!selectedCategory.value) return []
  return configsByCategory[selectedCategory.value] || []
})

const canSelectMedia = computed(() => {
  return uploadedImage.value && contextPrompt.value.trim().length > 0
})

const canStartGeneration = computed(() => {
  return (
    uploadedImage.value &&
    contextPrompt.value.trim().length > 0 &&
    selectedCategory.value &&
    selectedConfig.value &&
    !isPipelineExecuting.value
  )
})

// ============================================================================
// IMAGE UPLOAD HANDLERS
// ============================================================================

function handleImageUpload(data: any) {
  console.log('[Image Upload] Success:', data)
  uploadedImage.value = data.preview_url
  uploadedImagePath.value = data.image_path
  uploadedImageId.value = data.image_id
  executionPhase.value = 'image_uploaded'
}

function clearImage() {
  handleImageRemove()
  console.log('[I2I] Image cleared via action button')
}

function handleImageRemove() {
  console.log('[Image Upload] Removed')
  uploadedImage.value = null
  uploadedImagePath.value = null
  uploadedImageId.value = null
  contextPrompt.value = ''
  selectedCategory.value = null
  selectedConfig.value = null
  hoveredConfigId.value = null
  executionPhase.value = 'initial'
  outputImage.value = null
  isPipelineExecuting.value = false
}

// Watch contextPrompt changes and update phase
watch(contextPrompt, (newValue) => {
  console.log('[Context] Edited:', newValue.length, 'chars')

  // Update phase based on context prompt presence
  if (newValue.trim() && uploadedImage.value) {
    if (executionPhase.value === 'image_uploaded') {
      executionPhase.value = 'ready_for_media'
    }
  } else {
    if (executionPhase.value === 'ready_for_media') {
      executionPhase.value = 'image_uploaded'
    }
  }
})

// ============================================================================
// MODEL SELECTION (copied from text_transformation.vue)
// ============================================================================

function selectModel(modelId: string) {
  selectedConfig.value = modelId
  console.log('[Model] Selected:', modelId)
}

// ============================================================================
// CATEGORY SELECTION
// ============================================================================

async function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  console.log('[Category] Selected:', categoryId)

  await nextTick()
  scrollDownOnly(categorySectionRef.value, 'start')
}

// ============================================================================
// GENERATION (Stage 4)
// ============================================================================

async function startGeneration() {
  if (!canStartGeneration.value) return

  isPipelineExecuting.value = true
  generationProgress.value = 0
  outputImage.value = null  // Clear previous output

  // Scroll to output frame
  await nextTick()
  setTimeout(() => scrollDownOnly(pipelineSectionRef.value?.sectionRef, 'start'), 150)

  // Start progress simulation based on estimated duration from stage4-chunk

  // Parse estimated_duration_seconds (handle ranges like "20-60" → use minimum 20)
  let durationSeconds = 30  // fallback if parsing fails
  const durationStr = estimatedDurationSeconds.value

  if (durationStr.includes('-')) {
    // Range value: "20-60" → use minimum
    durationSeconds = parseInt(durationStr.split('-')[0] || '30')
  } else {
    durationSeconds = parseInt(durationStr)
  }

  // Handle instant completion (duration=0 → show 5-second animation for UX)
  if (durationSeconds === 0 || isNaN(durationSeconds)) {
    durationSeconds = 5
  }

  // Finish 10% before estimated time (more buffer for backend completion)
  durationSeconds = durationSeconds * 0.9

  console.log(`[Progress] Using ${durationSeconds}s animation (10% faster than estimate: "${durationStr}")`)

  // Calculate progress to reach 98% at adjusted time (finishes ~10% early)
  const targetProgress = 98
  const updateInterval = 100  // Update every 100ms
  const totalUpdates = (durationSeconds * 1000) / updateInterval
  const progressPerUpdate = targetProgress / totalUpdates

  const progressInterval = setInterval(() => {
    if (generationProgress.value < targetProgress) {
      generationProgress.value += progressPerUpdate
      if (generationProgress.value > targetProgress) {
        generationProgress.value = targetProgress
      }
    }
    // Stop at 98%, backend completion will jump to 100%
  }, updateInterval)

  // Phase 4: Intelligent seed logic
  const promptChanged = contextPrompt.value !== previousOptimizedPrompt.value
  if (promptChanged || currentSeed.value === null) {
    currentSeed.value = Math.floor(Math.random() * 1000000000)
    console.log('[Seed] New prompt or first run → new seed:', currentSeed.value)
  } else {
    console.log('[Seed] Same prompt → reusing seed:', currentSeed.value)
  }
  previousOptimizedPrompt.value = contextPrompt.value

  try {
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'image_transformation',
      input_image: uploadedImagePath.value,
      input_text: contextPrompt.value,
      context_prompt: contextPrompt.value,
      output_config: selectedConfig.value,
      user_language: 'de',
      safety_level: 'youth',
      seed: currentSeed.value
    })

    if (response.data.status === 'success') {
      // Stop progress simulation and complete
      clearInterval(progressInterval)
      generationProgress.value = 100

      // Get run_id and media_type from response
      const runId = response.data.media_output?.run_id || response.data.run_id
      const mediaType = response.data.media_output?.media_type || 'image'

      console.log('[Generation] Success, run_id:', runId, 'media_type:', mediaType)

      if (runId) {
        // Dynamic URL based on media type: /api/media/{type}/{run_id}
        outputMediaType.value = mediaType
        outputImage.value = `/api/media/${mediaType}/${runId}`
        executionPhase.value = 'generation_done'
        showSafetyApprovedStamp.value = true

        // Hide stamp after 3 seconds
        setTimeout(() => {
          showSafetyApprovedStamp.value = false
        }, 3000)

        // Scroll to show complete output
        await nextTick()
        setTimeout(() => scrollDownOnly(pipelineSectionRef.value?.sectionRef, 'start'), 150)
      }
    } else {
      clearInterval(progressInterval)
      alert(`Generation fehlgeschlagen: ${response.data.error}`)
      generationProgress.value = 0
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    console.error('[Generation] Error:', error)
    alert('Fehler bei der Generierung: ' + (error.response?.data?.error || error.message))
    generationProgress.value = 0
  } finally {
    isPipelineExecuting.value = false
  }
}

// ============================================================================
// FULLSCREEN
// ============================================================================

function showImageFullscreen(imageUrl: string) {
  fullscreenImage.value = imageUrl
}

// ============================================================================
// SCROLL HELPERS
// ============================================================================

function scrollDownOnly(element: HTMLElement | null, block: ScrollLogicalPosition = 'start') {
  if (!element) return
  const rect = element.getBoundingClientRect()
  const targetTop = block === 'start' ? rect.top : rect.bottom - window.innerHeight
  // Only scroll if target is below current viewport
  if (targetTop > 0) {
    element.scrollIntoView({ behavior: 'smooth', block })
  }
}

// ============================================================================
// Route handling & Store
// ============================================================================

const route = useRoute()
const pipelineStore = usePipelineExecutionStore()

// ============================================================================
// Textbox Actions (Copy/Paste/Delete)
// ============================================================================

function copyContextPrompt() {
  copyToClipboard(contextPrompt.value)
  console.log('[I2I] Context prompt copied to app clipboard')
}

function pasteContextPrompt() {
  contextPrompt.value = pasteFromClipboard()
  console.log('[I2I] Text pasted from app clipboard into context')
}

function clearContextPrompt() {
  contextPrompt.value = ''
  sessionStorage.removeItem('i2i_context_prompt')
  console.log('[I2I] Context prompt cleared')
}

// ============================================================================
// Output Actions (Print, Download, Re-transform, Analyze, Save)
// ============================================================================

function saveMedia() {
  alert('Speichern-Funktion kommt bald!')
}

function printImage() {
  if (!outputImage.value) return
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(`
      <html><head><title>Druck: Transformiertes Bild</title></head>
      <body style="margin:0;display:flex;justify-content:center;align-items:center;height:100vh;">
        <img src="${outputImage.value}" style="max-width:100%;max-height:100%;" onload="window.print();window.close()">
      </body></html>
    `)
    printWindow.document.close()
  }
  console.log('[I2I] Print initiated')
}

function sendToI2I() {
  if (!outputImage.value || outputMediaType.value !== 'image') return

  // Set current output as new input
  uploadedImage.value = outputImage.value
  uploadedImagePath.value = outputImage.value
  uploadedImageId.value = `retransform_${Date.now()}`

  // Keep context prompt for editing
  // Clear output to start fresh
  outputImage.value = null
  isPipelineExecuting.value = false
  executionPhase.value = 'image_uploaded'

  // Scroll to top to show input section
  window.scrollTo({ top: 0, behavior: 'smooth' })

  console.log('[I2I] Re-transform: Using output as new input')
}

async function downloadMedia() {
  if (!outputImage.value) return

  try {
    const response = await fetch(outputImage.value)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url

    // Generate filename with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-')
    const ext = outputMediaType.value === 'video' ? 'mp4' :
                outputMediaType.value === 'audio' || outputMediaType.value === 'music' ? 'mp3' :
                'png'
    a.download = `ai4artsed_i2i_${timestamp}.${ext}`

    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    console.log('[I2I Download] Media saved:', a.download)
  } catch (error) {
    console.error('[I2I Download] Error:', error)
    alert('Fehler beim Herunterladen')
  }
}

async function analyzeImage() {
  if (!outputImage.value || isAnalyzing.value) return

  isAnalyzing.value = true

  try {
    const response = await fetch('/api/image/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_url: outputImage.value,
        context: contextPrompt.value || ''
      })
    })

    const data = await response.json()

    if (data.success) {
      imageAnalysis.value = {
        analysis: data.analysis || '',
        reflection_prompts: data.reflection_prompts || [],
        insights: data.insights || [],
        success: true
      }
      showAnalysis.value = true
      console.log('[I2I Analysis] Success:', data)
    } else {
      console.error('[I2I Analysis] Failed:', data.error)
      alert('Bildanalyse fehlgeschlagen')
    }
  } catch (error) {
    console.error('[I2I Analysis] Error:', error)
    alert('Fehler bei der Bildanalyse')
  } finally {
    isAnalyzing.value = false
  }
}

// ============================================================================
// Lifecycle - sessionStorage persistence + Phase1 config loading
// ============================================================================

onMounted(async () => {
  // UNIFIED PATTERN: Always restore ALL boxes from storage first
  const savedContext = sessionStorage.getItem('i2i_context_prompt')
  if (savedContext) {
    contextPrompt.value = savedContext
    console.log('[I2I] Restored context from sessionStorage')
  }

  // Check if coming from Phase1 with configId
  const configId = route.params.configId as string

  if (configId) {
    console.log('[I2I] Received configId from Phase1:', configId)

    try {
      // Load config and meta-prompt from backend
      await pipelineStore.setConfig(configId)
      await pipelineStore.loadMetaPromptForLanguage('de')

      // Overwrite ONLY context (unified with t2i pattern)
      const freshContext = pipelineStore.metaPrompt || ''
      contextPrompt.value = freshContext

      // Overwrite context storage for both t2i and i2i
      sessionStorage.setItem('t2i_context_prompt', freshContext)
      sessionStorage.setItem('i2i_context_prompt', freshContext)

      console.log('[I2I] Context overwritten from Phase1 config')
    } catch (error) {
      console.error('[I2I] Failed to load config:', error)
    }
  }

  // LEGACY: Check if there's a transferred image from text_transformation (Weiterreichen)
  const transferDataStr = localStorage.getItem('i2i_transfer_data')

  if (transferDataStr) {
    try {
      const transferData = JSON.parse(transferDataStr)
      const now = Date.now()
      const fiveMinutes = 5 * 60 * 1000

      // Check if transfer is recent (within last 5 minutes)
      if (now - transferData.timestamp < fiveMinutes) {
        console.log('[i2i Transfer] Loading transferred image:', transferData)

        // Set the image as if it was uploaded
        uploadedImage.value = transferData.imageUrl
        // Use the URL for display, but store run_id for backend
        uploadedImagePath.value = transferData.imageUrl
        uploadedImageId.value = transferData.runId || `transferred_${transferData.timestamp}`
        executionPhase.value = 'image_uploaded'

        // Clear the transfer data
        localStorage.removeItem('i2i_transfer_data')

        console.log('[i2i Transfer] Image loaded successfully')
      } else {
        // Transfer expired, clean up
        localStorage.removeItem('i2i_transfer_data')
        console.log('[i2i Transfer] Transfer expired (>5 minutes old)')
      }
    } catch (error) {
      console.error('[i2i Transfer] Error parsing transfer data:', error)
      localStorage.removeItem('i2i_transfer_data')
    }
  }

  // Clean up old format (backward compatibility)
  localStorage.removeItem('i2i_transfer_image')
  localStorage.removeItem('i2i_transfer_timestamp')
})

// Watch for changes and persist to sessionStorage
watch(contextPrompt, (newVal) => {
  sessionStorage.setItem('i2i_context_prompt', newVal)
})
</script>

<style scoped>
/* ============================================================================
   Root Container
   ============================================================================ */

.image-transformation-view {
  min-height: 100%;
  background: #0a0a0a;
  color: #ffffff;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ============================================================================
   Phase 2a: Vertical Flow
   ============================================================================ */

.phase-2a {
  max-width: clamp(320px, 90vw, 1100px);
  width: 100%;
  padding: clamp(1rem, 3vw, 2rem);
  padding-top: clamp(1rem, 3vw, 2rem); /* Reduced - App.vue header is smaller now */

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(1rem, 3vh, 2rem);
}

/* ============================================================================
   Input + Context Section (Side by Side)
   ============================================================================ */

.input-context-section {
  display: flex;
  gap: clamp(0.75rem, 2vw, 1.5rem);
  width: 100%;
  max-width: 1000px;
  align-items: stretch;
}

.input-bubble,
.context-bubble {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .input-context-section {
    flex-direction: column;
  }
}

/* ============================================================================
   Bubble Cards (Input/Context)
   ============================================================================ */

.bubble-card {
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: clamp(12px, 2vw, 20px);
  padding: clamp(1rem, 2.5vw, 1.5rem);
  transition: all 0.3s ease;
  width: 100%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
}

.bubble-card.filled {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
}

.bubble-card.required {
  border-color: rgba(255, 193, 7, 0.6);
  background: rgba(255, 193, 7, 0.05);
  animation: pulse-required 2s ease-in-out infinite;
}

@keyframes pulse-required {
  0%, 100% {
    border-color: rgba(255, 193, 7, 0.6);
  }
  50% {
    border-color: rgba(255, 193, 7, 0.9);
  }
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.bubble-icon {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  flex-shrink: 0;
}

.bubble-label {
  font-size: clamp(0.9rem, 2vw, 1rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.bubble-actions {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.action-btn {
  background: transparent;
  border: none;
  font-size: 0.9rem;
  opacity: 0.4;
  cursor: pointer;
  transition: opacity 0.2s;
  padding: 0.25rem;
}

.action-btn:hover {
  opacity: 0.8;
}

.bubble-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: clamp(0.9rem, 2vw, 1rem);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
  resize: vertical;
  font-family: inherit;
  line-height: 1.4;
  flex-grow: 1;
  min-height: 0;
}

.bubble-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.bubble-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* ============================================================================
   Section: Image Upload & Context
   ============================================================================ */

.image-upload-section,
.context-section {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* ============================================================================
   Section 3: Category Bubbles (Horizontal Row)
   ============================================================================ */

.category-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.category-bubbles-row {
  display: flex;
  flex-direction: row;
  gap: clamp(1rem, 2.5vw, 1.5rem);
  justify-content: center;
  flex-wrap: wrap;
}

.category-bubble {
  width: clamp(70px, 12vw, 90px);
  height: clamp(70px, 12vw, 90px);

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(30, 30, 30, 0.9);
  border: 3px solid var(--bubble-color, rgba(255, 255, 255, 0.3));
  border-radius: 50%;

  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.category-bubble:hover {
  transform: scale(1.08);
  box-shadow: 0 0 20px var(--bubble-color);
  border-width: 4px;
}

.category-bubble.selected {
  transform: scale(1.15);
  background: var(--bubble-color);
  box-shadow: 0 0 30px var(--bubble-color),
              0 0 60px var(--bubble-color);
  border-color: #ffffff;
}

.category-bubble:focus-visible {
  outline: 3px solid rgba(102, 126, 234, 0.8);
  outline-offset: 4px;
}

.category-bubble:active {
  transform: scale(0.95);
}

.category-bubble.disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(1);
}

.bubble-emoji-small {
  font-size: clamp(2rem, 4.5vw, 2.5rem);
  line-height: 1;
  transition: filter 0.3s ease;
}

.category-bubble.selected .bubble-emoji-small {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}

/* ============================================================================
   Start Button Container
   ============================================================================ */

.start-button-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1rem, 3vw, 2rem);
  flex-wrap: wrap;
}

/* ============================================================================
   Start Button
   ============================================================================ */

.start-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.5rem, 1.5vw, 0.75rem);
  padding: clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2.5rem);
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  font-weight: 700;
  background: #000000;
  color: #FFB300;
  border: 3px solid #FFB300;
  border-radius: 16px;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(255, 179, 0, 0.4),
              0 4px 15px rgba(0, 0, 0, 0.5);
  text-shadow: 0 0 10px rgba(255, 179, 0, 0.6);
  transition: all 0.3s ease;
}

.button-arrows {
  font-size: clamp(0.9rem, 2vw, 1.1rem);
}

.button-arrows-left {
  animation: arrow-pulse-left 1.5s ease-in-out infinite;
}

.button-arrows-right {
  animation: arrow-pulse-right 1.5s ease-in-out infinite;
}

.button-text {
  font-size: clamp(1rem, 2.5vw, 1.2rem);
}

@keyframes arrow-pulse-left {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes arrow-pulse-right {
  0%, 100% {
    opacity: 1;
    transform: scale(1.2);
  }
  50% {
    opacity: 0.4;
    transform: scale(1);
  }
}

.start-button:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 0 30px rgba(255, 179, 0, 0.6),
              0 6px 25px rgba(0, 0, 0, 0.6);
  border-color: #FF8F00;
}

.start-button:active {
  transform: scale(0.98);
}

.start-button.disabled,
.start-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(0.8);
  box-shadow: none;
  text-shadow: none;
}

.start-button.disabled .button-arrows,
.start-button:disabled .button-arrows {
  animation: none;
  opacity: 0.3;
}

/* Safety Approved Stamp */
.safety-stamp {
  display: flex;
  justify-content: center;
  align-items: center;
}

.stamp-inner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: clamp(0.4rem, 1.5vw, 0.6rem) clamp(0.8rem, 2.5vw, 1.2rem);
  background: rgba(76, 175, 80, 0.15);
  border: 2px solid #4CAF50;
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
  animation: stamp-appear 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes stamp-appear {
  0% {
    opacity: 0;
    transform: scale(0.5) rotate(-10deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

.stamp-icon {
  font-size: clamp(1.2rem, 3vw, 1.5rem);
  color: #4CAF50;
  font-weight: bold;
  line-height: 1;
}

.stamp-text {
  font-size: clamp(0.65rem, 1.5vw, 0.75rem);
  font-weight: 700;
  color: #4CAF50;
  text-align: center;
  line-height: 1.2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Output box styles moved to MediaOutputBox.vue component */

/* ============================================================================
   Fullscreen Modal
   ============================================================================ */

.fullscreen-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.fullscreen-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.close-fullscreen {
  position: absolute;
  top: 2rem;
  right: 2rem;
  width: 4rem;
  height: 4rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid white;
  color: white;
  font-size: 2.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-fullscreen:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

/* ============================================================================
   Transitions
   ============================================================================ */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* ============================================================================
   Responsive: Mobile Adjustments
   ============================================================================ */

@media (max-width: 768px) {
  .category-bubbles-row {
    gap: 1rem;
  }
}

/* iPad 1024×768 Optimization */
@media (min-width: 1024px) and (max-height: 768px) {
  .phase-2a {
    padding: 1.5rem;
    gap: 1.25rem;
  }
}

/* ============================================================================
   Model Selection Bubbles (copied from text_transformation.vue)
   ============================================================================ */

.config-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.config-bubbles-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.config-bubbles-row {
  display: inline-flex;
  flex-direction: row;
  gap: clamp(0.75rem, 2vw, 1rem);
  justify-content: center;
  flex-wrap: wrap;
  max-width: fit-content;
}

.config-bubble {
  position: relative;
  z-index: 1;
  width: clamp(80px, 12vw, 100px);
  height: clamp(80px, 12vw, 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 30, 30, 0.9);
  border: 3px solid var(--bubble-color, rgba(255, 255, 255, 0.3));
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.config-bubble:hover:not(.disabled),
.config-bubble.hovered {
  transform: scale(2.0);
  background: rgba(20, 20, 20, 0.9);
  box-shadow: 0 0 30px var(--bubble-color);
  z-index: 100;
}

.config-bubble.selected {
  transform: scale(1.1);
  background: var(--bubble-color);
  box-shadow: 0 0 30px var(--bubble-color);
  border-color: #ffffff;
}

.config-bubble.disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(0.8);
}

.bubble-emoji-medium {
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  line-height: 1;
}

.bubble-logo {
  width: clamp(72px, 11vw, 92px);
  height: clamp(72px, 11vw, 92px);
  object-fit: contain;
}

.config-bubble.light-bg {
  background: rgba(255, 255, 255, 0.95);
}

.config-bubble.light-bg.selected {
  background: var(--bubble-color);
}

/* Hover info overlay */
.bubble-hover-info {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18%;
  color: white;
  z-index: 10;
  pointer-events: none;
  gap: 0.3rem;
}

.hover-info-name {
  font-size: 0.5rem;
  font-weight: 600;
  text-align: center;
  line-height: 1.25;
  margin-bottom: 0;
  letter-spacing: -0.01em;
  color: rgba(255, 255, 255, 0.95);
  max-width: 100%;
  word-wrap: break-word;
}

.hover-info-meta {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.18rem;
  width: 100%;
  line-height: 1;
  margin: 0;
  padding: 0;
}

.meta-label {
  font-size: 0.45rem;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 400;
  text-align: left;
  flex-shrink: 0;
  flex-basis: 35%;
  letter-spacing: -0.01em;
}

.meta-value {
  font-size: 0.65rem;
  font-weight: 500;
  text-align: right;
  white-space: nowrap;
  flex-shrink: 0;
  flex-basis: 60%;
  letter-spacing: 0.02em;
}

.stars-filled {
  color: #FFD700;
}

.stars-unfilled {
  color: rgba(150, 150, 150, 0.5);
}

.meta-value.duration-only {
  width: 100%;
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.45rem;
  flex-basis: auto;
  margin-top: 0.25rem;
  line-height: 1;
}

/* Hide logo/emoji when hovering */
.config-bubble.hovered .bubble-logo,
.config-bubble.hovered .bubble-emoji-medium {
  opacity: 0;
  display: none;
}

/* Action toolbar and analysis styles moved to MediaOutputBox.vue component */
</style>
