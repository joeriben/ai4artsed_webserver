<template>
  <div class="image-transformation-container">

    <!-- Section 1: Image Upload -->
    <section class="image-upload-section">
      <h2 class="section-title neon-glow">Lade dein Bild hoch</h2>
      <div class="image-bubble bubble-card" :class="{ filled: uploadedImage }">
        <ImageUploadWidget
          @image-uploaded="handleImageUpload"
          @image-removed="handleImageRemove"
        />
      </div>
    </section>

    <!-- Section 1.5: Context Prompt (Mandatory) -->
    <section v-if="uploadedImage" class="context-section">
      <h2 class="section-title neon-glow">Wie soll das Bild verändert werden?</h2>
      <div class="context-bubble bubble-card" :class="{ filled: contextPrompt, required: !contextPrompt }">
        <div class="bubble-header">
          <span class="bubble-icon">📋</span>
          <span class="bubble-label">Beschreibe die gewünschte Transformation</span>
        </div>
        <textarea
          v-model="contextPrompt"
          @input="handleContextPromptEdit"
          placeholder="Verwandle es in ein Ölgemälde... Mache es bunter... Füge einen Sonnenuntergang hinzu..."
          class="bubble-textarea"
          rows="4"
        ></textarea>
      </div>
    </section>

    <!-- Section 2: Category Selection (Media Type) -->
    <section v-if="canSelectMedia" class="category-section" ref="categorySectionRef">
      <h2 class="section-title neon-glow">Wähle ein Medium aus</h2>
      <div class="category-bubbles-row">
        <div
          v-for="category in availableCategories"
          :key="category.id"
          class="category-bubble"
          :class="{ selected: selectedCategory === category.id, disabled: category.disabled }"
          :style="{ '--bubble-color': category.color }"
          @click="!category.disabled && selectCategory(category.id)"
        >
          <div class="bubble-emoji-small">{{ category.emoji }}</div>
        </div>
      </div>
    </section>

    <!-- Section 2.5: Model Selection -->
    <section v-if="selectedCategory" class="config-section">
      <h2 class="section-title neon-glow">Wähle ein KI-Modell aus</h2>
      <div class="config-bubbles-container">
        <div class="config-bubbles-row">
          <div
            v-for="config in configsForCategory"
            :key="config.id"
            class="config-bubble"
            :class="{
              selected: selectedConfig === config.id,
              loading: config.id === selectedConfig && isOptimizationLoading,
              'light-bg': config.lightBg,
              disabled: config.disabled || !areModelBubblesEnabled
            }"
            @click="areModelBubblesEnabled && !config.disabled && selectConfig(config.id)"
          >
            <img v-if="config.logo" :src="config.logo" class="bubble-logo" />
            <div v-else class="bubble-emoji-medium">{{ config.emoji }}</div>
            <div class="bubble-label-medium">{{ config.label }}</div>
            <div v-if="config.disabled" class="coming-soon-badge">Bald</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: Optimization Preview (if optimization happened) -->
    <section v-if="hasOptimization" class="optimization-section">
      <h2 class="section-title neon-glow">Optimierter Prompt</h2>
      <div class="optimization-preview bubble-card" :class="{ empty: !optimizedPrompt, loading: isOptimizationLoading }">
        <div class="bubble-header">
          <span class="bubble-icon">✨</span>
          <span class="bubble-label">Modell-Optimierter Prompt</span>
        </div>
        <div v-if="isOptimizationLoading" class="preview-loading">
          <div class="spinner-large"></div>
          <p class="loading-text">Der Prompt wird jetzt für das gewählte KI-Modell angepasst...</p>
        </div>
        <textarea
          v-else
          ref="optimizationTextareaRef"
          v-model="optimizedPrompt"
          class="bubble-textarea auto-resize-textarea"
          rows="5"
          :readonly="!optimizedPrompt"
        ></textarea>
      </div>
    </section>

    <!-- Section 4: Start Generation Button -->
    <section v-if="canStartGeneration" class="start-section">
      <button
        class="start-button"
        :class="{ disabled: !canStartGeneration || isPipelineExecuting }"
        :disabled="!canStartGeneration || isPipelineExecuting"
        @click="startGeneration"
      >
        <span class="button-icon">🎨</span>
        <span class="button-text">{{ isPipelineExecuting ? 'Generierung läuft...' : 'Bild transformieren' }}</span>
        <span v-if="!isPipelineExecuting" class="button-arrow">→</span>
      </button>
    </section>

    <!-- Section 5: Pipeline Execution Progress -->
    <section v-if="isPipelineExecuting" class="progress-section">
      <SpriteProgressAnimation
        :progress="generationProgress"
        message="Die KI transformiert dein Bild..."
      />
    </section>

    <!-- Section 6: Output Display -->
    <section v-if="outputImage" class="output-section">
      <h2 class="section-title neon-glow">Dein transformiertes Bild</h2>
      <div class="output-frame" @click="openFullscreen">
        <img v-if="outputMediaType === 'image'" :src="outputImage" alt="Generated image" />
        <video v-else-if="outputMediaType === 'video'" :src="outputImage" controls />
        <audio v-else-if="outputMediaType === 'audio' || outputMediaType === 'music'" :src="outputImage" controls />

        <!-- Safety Approved Stamp -->
        <div v-if="showSafetyApprovedStamp" class="safety-stamp">
          <div class="stamp-inner">✓</div>
          <span class="stamp-text">FREIGEGEBEN</span>
        </div>
      </div>

      <!-- Retry Button -->
      <button class="retry-button" @click="retryGeneration">
        <span class="button-icon">🔄</span>
        <span class="button-text">Nochmal mit anderem Seed</span>
      </button>
    </section>

    <!-- Fullscreen Modal -->
    <div v-if="fullscreenImage" class="fullscreen-modal" @click="closeFullscreen">
      <img :src="fullscreenImage" alt="Fullscreen image" />
      <button class="close-fullscreen" @click="closeFullscreen">✕</button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import ImageUploadWidget from '@/components/ImageUploadWidget.vue'
import SpriteProgressAnimation from '@/components/SpriteProgressAnimation.vue'

// ============================================================================
// STATE
// ============================================================================

// Image upload
const uploadedImage = ref<string | null>(null)  // Base64 preview URL
const uploadedImagePath = ref<string | null>(null)  // Server path
const uploadedImageId = ref<string | null>(null)

// Form inputs
const contextPrompt = ref('')
const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)

// Optimization
const optimizedPrompt = ref('')
const isOptimizationLoading = ref(false)
const hasOptimization = ref(false)

// Phase 4: Seed management
const previousOptimizedPrompt = ref('')
const currentSeed = ref<number | null>(null)

// Execution
const executionPhase = ref<'initial' | 'image_uploaded' | 'ready_for_media' | 'optimization_done' | 'generation_done'>('initial')
const isPipelineExecuting = ref(false)
const outputImage = ref<string | null>(null)
const outputMediaType = ref<string>('image')
const fullscreenImage = ref<string | null>(null)
const showSafetyApprovedStamp = ref(false)
const generationProgress = ref(0)

// Refs
const categorySectionRef = ref<HTMLElement | null>(null)
const optimizationTextareaRef = ref<HTMLTextAreaElement | null>(null)

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

interface Config {
  id: string
  label: string
  emoji?: string
  logo?: string
  color: string
  lightBg?: boolean
  disabled?: boolean
}

const availableCategories: Category[] = [
  { id: 'image', label: 'Bild', emoji: '🖼️', color: '#4CAF50' },
  { id: 'video', label: 'Video', emoji: '🎬', color: '#9C27B0', disabled: true },
  { id: 'sound', label: 'Sound', emoji: '🔊', color: '#FF9800', disabled: true }
]

const configsByCategory: Record<string, Config[]> = {
  image: [
    // Local ComfyUI models only (DSGVO-compliant)
    { id: 'sd35_large_img2img', label: 'SD3.5\nIMG2IMG', emoji: '🎨', color: '#2196F3', lightBg: false, disabled: false },
    { id: 'qwen_img2img', label: 'Qwen\nIMG2IMG', emoji: '🌟', color: '#FFC107', lightBg: true, disabled: true }
  ],
  video: [
    // img2video via ComfyUI (local) - disabled for Phase 2
    { id: 'ltx_video_img2video', label: 'LTX\nIMG2Video', emoji: '🎬', color: '#9C27B0', lightBg: false, disabled: true }
  ],
  sound: [
    // img2sound via image analysis → text → sound (local pipeline) - disabled for Phase 2
    { id: 'acestep_img2sound', label: 'ACE\nIMG2Sound', emoji: '🔊', color: '#FF9800', lightBg: false, disabled: true }
  ]
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

const areModelBubblesEnabled = computed(() => {
  return canSelectMedia.value
})

const canStartGeneration = computed(() => {
  return (
    uploadedImage.value &&
    contextPrompt.value.trim().length > 0 &&
    selectedConfig.value &&
    executionPhase.value === 'optimization_done' &&
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

function handleImageRemove() {
  console.log('[Image Upload] Removed')
  uploadedImage.value = null
  uploadedImagePath.value = null
  uploadedImageId.value = null
  contextPrompt.value = ''
  selectedCategory.value = null
  selectedConfig.value = null
  optimizedPrompt.value = ''
  hasOptimization.value = false
  executionPhase.value = 'initial'
}

function handleContextPromptEdit() {
  console.log('[Context] Edited:', contextPrompt.value.length, 'chars')

  // Update phase based on context prompt presence
  if (contextPrompt.value.trim() && uploadedImage.value) {
    if (executionPhase.value === 'image_uploaded') {
      executionPhase.value = 'ready_for_media'
    }
  } else {
    if (executionPhase.value === 'ready_for_media') {
      executionPhase.value = 'image_uploaded'
    }
  }
}

// ============================================================================
// CATEGORY & CONFIG SELECTION
// ============================================================================

async function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  selectedConfig.value = null
  await nextTick()
  if (categorySectionRef.value) {
    categorySectionRef.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

async function selectConfig(configId: string) {
  if (!areModelBubblesEnabled.value || isOptimizationLoading.value) return

  selectedConfig.value = configId
  console.log('[SelectConfig] Selected:', configId)

  // Trigger optimization
  await runOptimization()
}

// ============================================================================
// OPTIMIZATION (Stage 3)
// ============================================================================

async function runOptimization() {
  isOptimizationLoading.value = true

  try {
    const response = await axios.post('/api/schema/pipeline/optimize', {
      input_text: contextPrompt.value,  // Context prompt goes directly to optimization
      output_config: selectedConfig.value
    })

    if (response.data.success) {
      optimizedPrompt.value = response.data.optimized_prompt || ''
      hasOptimization.value = response.data.optimization_applied || false
      executionPhase.value = 'optimization_done'
      console.log('[Optimize] Complete:', optimizedPrompt.value.substring(0, 60))
    }
  } catch (error) {
    console.error('[Optimize] Error:', error)
    // Fallback: use context prompt directly
    optimizedPrompt.value = contextPrompt.value
    hasOptimization.value = false
    executionPhase.value = 'optimization_done'
  } finally {
    isOptimizationLoading.value = false
  }
}

// ============================================================================
// GENERATION (Stage 4)
// ============================================================================

async function startGeneration() {
  if (!canStartGeneration.value) return

  isPipelineExecuting.value = true
  generationProgress.value = 0

  // Phase 4: Intelligent seed logic
  const promptChanged = optimizedPrompt.value !== previousOptimizedPrompt.value
  if (promptChanged || currentSeed.value === null) {
    currentSeed.value = Math.floor(Math.random() * 1000000000)
    console.log('[Seed] New prompt or first run → new seed:', currentSeed.value)
  } else {
    console.log('[Seed] Same prompt → reusing seed:', currentSeed.value)
  }
  previousOptimizedPrompt.value = optimizedPrompt.value

  try {
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'image_transformation',
      input_image: uploadedImagePath.value,
      input_text: optimizedPrompt.value || contextPrompt.value,
      context_prompt: contextPrompt.value,
      output_config: selectedConfig.value,
      user_language: 'de',
      safety_level: 'youth',
      seed: currentSeed.value
    })

    if (response.data.status === 'success') {
      // Complete progress
      generationProgress.value = 100

      // DEBUG: Log full response structure
      console.log('[DEBUG] Full response.data:', JSON.stringify(response.data, null, 2))
      console.log('[DEBUG] response.data.status:', response.data.status)
      console.log('[DEBUG] response.data.run_id:', response.data.run_id)
      console.log('[DEBUG] response.data.media_output:', response.data.media_output)

      // Get run_id and media_type from response
      const runId = response.data.media_output?.run_id || response.data.run_id
      const mediaType = response.data.media_output?.media_type || 'image'

      console.log('[Generation] Success, run_id:', runId, 'media_type:', mediaType)
      console.log('[DEBUG] Constructed URL:', `/api/media/${mediaType}/${runId}`)

      if (runId) {
        // Dynamic URL based on media type: /api/media/{type}/{run_id}
        outputMediaType.value = mediaType
        outputImage.value = `/api/media/${mediaType}/${runId}`
        executionPhase.value = 'generation_done'
        showSafetyApprovedStamp.value = true

        console.log('[DEBUG] outputImage.value set to:', outputImage.value)
        console.log('[DEBUG] outputMediaType.value set to:', outputMediaType.value)
        console.log('[DEBUG] executionPhase.value set to:', executionPhase.value)

        // Hide stamp after 3 seconds
        setTimeout(() => {
          showSafetyApprovedStamp.value = false
        }, 3000)
      } else if (response.data.outputs && response.data.outputs.length > 0) {
        // Fallback: use outputs array
        outputMediaType.value = 'image'
        outputImage.value = `http://localhost:17802${response.data.outputs[0]}`
        executionPhase.value = 'generation_done'
        showSafetyApprovedStamp.value = true
      }
    } else {
      alert(`Generation fehlgeschlagen: ${response.data.error}`)
      generationProgress.value = 0
    }
  } catch (error: any) {
    console.error('[Generation] Error:', error)
    alert('Fehler bei der Generierung: ' + (error.response?.data?.error || error.message))
  } finally {
    isPipelineExecuting.value = false
    generationProgress.value = 100
  }
}

function retryGeneration() {
  // Force new seed
  currentSeed.value = Math.floor(Math.random() * 1000000000)
  console.log('[Retry] New seed:', currentSeed.value)
  startGeneration()
}

// ============================================================================
// FULLSCREEN
// ============================================================================

function openFullscreen() {
  if (outputImage.value) {
    fullscreenImage.value = outputImage.value
  }
}

function closeFullscreen() {
  fullscreenImage.value = null
}

// ============================================================================
// WATCHERS
// ============================================================================

// Auto-resize optimization textarea when content changes
watch(optimizedPrompt, async () => {
  await nextTick()
  if (optimizationTextareaRef.value) {
    optimizationTextareaRef.value.style.height = 'auto'
    optimizationTextareaRef.value.style.height = optimizationTextareaRef.value.scrollHeight + 'px'
  }
})
</script>

<style scoped>
/* Container */
.image-transformation-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
  padding-bottom: 4rem;
}

/* Section Titles */
.section-title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 700;
  text-align: center;
  margin-bottom: 2rem;
  color: #ffffff;
}

.neon-glow {
  text-shadow:
    0 0 10px rgba(255, 179, 0, 0.5),
    0 0 20px rgba(255, 179, 0, 0.3),
    0 0 30px rgba(255, 179, 0, 0.2);
}

/* Sections */
section {
  margin-bottom: 3rem;
}

/* Bubble Cards */
.bubble-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.bubble-card.filled {
  border-color: rgba(76, 175, 80, 0.5);
  background: rgba(76, 175, 80, 0.05);
}

.bubble-card.required {
  border-color: rgba(255, 179, 0, 0.5);
  background: rgba(255, 179, 0, 0.05);
  animation: pulse-required 2s infinite;
}

@keyframes pulse-required {
  0%, 100% { border-color: rgba(255, 179, 0, 0.5); }
  50% { border-color: rgba(255, 179, 0, 0.8); }
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  color: #e0e0e0;
}

.bubble-icon {
  font-size: 1.5rem;
}

.bubble-label {
  font-size: 1rem;
  font-weight: 600;
}

.bubble-textarea {
  width: 100%;
  min-height: 80px;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.bubble-textarea:focus {
  outline: none;
  border-color: rgba(76, 175, 80, 0.6);
}

.bubble-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Category Bubbles */
.category-bubbles-row {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.category-bubble {
  width: clamp(70px, 12vw, 90px);
  height: clamp(70px, 12vw, 90px);
  border-radius: 50%;
  background: var(--bubble-color, #4CAF50);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent;
  position: relative;
}

.category-bubble:hover:not(.disabled) {
  transform: scale(1.1);
  box-shadow: 0 0 20px var(--bubble-color);
}

.category-bubble.selected {
  border-color: #FFB300;
  box-shadow: 0 0 30px var(--bubble-color);
}

.category-bubble.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.bubble-emoji-small {
  font-size: clamp(2rem, 5vw, 3rem);
}

/* Config Bubbles */
.config-bubbles-container {
  display: flex;
  justify-content: center;
}

.config-bubbles-row {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.config-bubble {
  width: clamp(100px, 15vw, 130px);
  height: clamp(100px, 15vw, 130px);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent;
  position: relative;
}

.config-bubble:hover:not(.disabled) {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.15);
}

.config-bubble.selected {
  border-color: #FFB300;
  box-shadow: 0 0 30px rgba(255, 179, 0, 0.5);
}

.config-bubble.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.bubble-emoji-medium {
  font-size: clamp(2rem, 4vw, 2.5rem);
  margin-bottom: 0.5rem;
}

.bubble-label-medium {
  font-size: clamp(0.7rem, 1.5vw, 0.85rem);
  text-align: center;
  line-height: 1.2;
  color: #e0e0e0;
  white-space: pre-line;
}

.coming-soon-badge {
  position: absolute;
  bottom: -10px;
  background: #FF9800;
  color: #000;
  font-size: 0.65rem;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-weight: 600;
}

/* Optimization Preview */
.optimization-preview {
  border-color: rgba(76, 175, 80, 0.5);
}

.preview-loading {
  text-align: center;
  padding: 2rem;
}

.spinner-large {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #b0e0b3;
  font-size: 0.95rem;
}

/* Start Button */
.start-button {
  width: 100%;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
}

.start-button:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6);
}

.start-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-icon {
  font-size: 1.5rem;
}

.button-arrow {
  font-size: 1.8rem;
  animation: arrow-pulse 1.5s infinite;
}

@keyframes arrow-pulse {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(5px); }
}

/* Output Frame */
.output-frame {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.5);
  cursor: pointer;
  max-width: 100%;
}

.output-frame img,
.output-frame video {
  width: 100%;
  height: auto;
  display: block;
}

.safety-stamp {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(76, 175, 80, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: stamp-appear 0.5s ease;
}

@keyframes stamp-appear {
  from {
    transform: scale(0) rotate(-45deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

.stamp-inner {
  font-size: 2rem;
  color: white;
  font-weight: 700;
}

.stamp-text {
  font-size: 0.6rem;
  color: white;
  font-weight: 700;
  text-transform: uppercase;
}

/* Retry Button */
.retry-button {
  margin-top: 1rem;
  width: 100%;
  padding: 1rem;
  background: rgba(255, 152, 0, 0.2);
  border: 2px solid rgba(255, 152, 0, 0.5);
  border-radius: 8px;
  color: #FFB300;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.retry-button:hover {
  background: rgba(255, 152, 0, 0.3);
  border-color: rgba(255, 152, 0, 0.7);
}

/* Fullscreen Modal */
.fullscreen-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.fullscreen-modal img {
  max-width: 95vw;
  max-height: 95vh;
  object-fit: contain;
}

.close-fullscreen {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-fullscreen:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* Responsive */
@media (max-width: 768px) {
  .category-bubbles-row {
    gap: 1rem;
  }

  .config-bubbles-row {
    gap: 1rem;
  }
}
</style>
