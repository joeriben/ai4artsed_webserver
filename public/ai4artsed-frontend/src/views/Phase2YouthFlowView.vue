<template>
  <div class="youth-flow-view">

    <!-- Single Continuous Flow (no phase transitions) -->
    <div class="phase-2a" ref="mainContainerRef">

        <!-- Section 1: Input + Context (Side by Side) -->
        <section class="input-context-section">
          <!-- Input Bubble -->
          <div class="input-bubble bubble-card" :class="{ filled: inputText }">
            <div class="bubble-header">
              <span class="bubble-icon">💡</span>
              <span class="bubble-label">Deine Idee: Worum soll es gehen?</span>
            </div>
            <textarea
              v-model="inputText"
              placeholder="Ein Fest in meiner Straße: ..."
              class="bubble-textarea"
              rows="3"
            ></textarea>
          </div>

          <!-- Context Bubble -->
          <div class="context-bubble bubble-card" :class="{ filled: contextPrompt, required: !contextPrompt }">
            <div class="bubble-header">
              <span class="bubble-icon">📋</span>
              <span class="bubble-label">Bestimme Regeln, Material, Besonderheiten</span>
            </div>
            <textarea
              v-model="contextPrompt"
              placeholder="Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen!"
              class="bubble-textarea"
              rows="3"
            ></textarea>
          </div>
        </section>

        <!-- Section 2: Category Selection (Horizontal Row) - Always visible -->
        <section class="category-section">
          <h2 class="section-title">Wähle ein KI-Modell aus</h2>
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

        <!-- Section 3: Config Selection (Appears Below Selected Category) -->
        <transition name="slide-down">
          <section v-if="selectedCategory" class="config-section">
            <h2 class="section-title">Wähle ein Modell</h2>
            <div class="config-bubbles-container">
              <div class="config-bubbles-row">
                <div
                  v-for="config in configsForCategory"
                  :key="config.id"
                  class="config-bubble"
                  :class="{ selected: selectedConfig === config.id, loading: config.id === selectedConfig && isInterceptionLoading, 'light-bg': config.lightBg }"
                  :style="{ '--bubble-color': config.color }"
                  @click="selectConfig(config.id)"
                  role="button"
                  :aria-pressed="selectedConfig === config.id"
                  tabindex="0"
                  @keydown.enter="selectConfig(config.id)"
                  @keydown.space.prevent="selectConfig(config.id)"
                >
                  <img v-if="config.logo" :src="config.logo" :alt="config.label" class="bubble-logo" />
                  <div v-else class="bubble-emoji-medium">{{ config.emoji }}</div>
                  <div class="bubble-label-medium">{{ config.label }}</div>
                  <div v-if="config.id === selectedConfig && isInterceptionLoading" class="loading-indicator">
                    <div class="spinner"></div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </transition>

        <!-- Section 4: Interception Preview (Always visible, shows placeholder when empty) -->
        <section class="interception-section">
          <div class="interception-preview bubble-card" :class="{ empty: !interceptionResult, loading: isInterceptionLoading }">
            <div class="bubble-header">
              <span class="bubble-icon">→</span>
              <span class="bubble-label">Idee + Regeln = Prompt</span>
            </div>
            <div v-if="isInterceptionLoading" class="preview-loading">
              <div class="spinner-large"></div>
              <p class="loading-text">Erstelle Prompt...</p>
            </div>
            <textarea
              v-else
              v-model="interceptionResult"
              :placeholder="interceptionResult ? '' : 'Du kannst den Prompt hinterher noch verändern.'"
              class="bubble-textarea"
              rows="5"
              :readonly="!interceptionResult"
            ></textarea>
          </div>
        </section>

        <!-- Start Button -->
        <transition name="fade">
          <button
            v-if="canStartPipeline"
            class="start-button"
            @click="startPipelineExecution"
            ref="startButtonRef"
          >
            🚀 Bild erstellen!
          </button>
        </transition>

        <!-- Section 5: Pipeline Path (always visible, inactive until generation starts) -->
        <section class="pipeline-section" ref="pipelineSectionRef">
          <transition name="fade" mode="out-in">
            <h2 v-if="outputImage" key="done" class="section-title">Fertig!</h2>
            <h2 v-else-if="isPipelineExecuting" key="executing" class="section-title">Dein Bild wird erstellt...</h2>
            <h2 v-else key="ready" class="section-title">Wenn du bereit bist:</h2>
          </transition>

          <div class="pipeline-stages">
            <div
              v-for="(stage, index) in displayPipelineStages"
              :key="stage.id"
              class="stage-container"
            >
              <!-- Stage Bubble -->
              <div
                class="stage-bubble"
                :class="stage.status"
                :style="{ '--stage-color': stage.color }"
              >
                <div class="stage-emoji">{{ stage.emoji }}</div>
                <div class="stage-label">{{ stage.label }}</div>

                <!-- Status Indicator -->
                <div class="status-indicator">
                  <span v-if="stage.status === 'waiting'" class="status-dot"></span>
                  <span v-if="stage.status === 'processing'" class="status-spinner"></span>
                  <span v-if="stage.status === 'completed'" class="status-check">✓</span>
                </div>
              </div>

              <!-- Arrow (except after last stage) -->
              <div v-if="index < displayPipelineStages.length - 1" class="stage-arrow">→</div>
            </div>
          </div>

          <!-- Final Output -->
          <transition name="slide-up">
            <div v-if="outputImage" class="final-output">
              <img
                :src="outputImage"
                alt="Generiertes Bild"
                class="output-image"
                @click="showImageFullscreen(outputImage)"
              />
            </div>
          </transition>
        </section>

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
import { ref, computed, nextTick } from 'vue'
import axios from 'axios'

// ============================================================================
// Types
// ============================================================================

type StageStatus = 'waiting' | 'processing' | 'completed'

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
  emoji: string
  color: string
  description: string
  logo?: string
  lightBg?: boolean
}

interface PipelineStage {
  id: string
  label: string
  emoji: string
  color: string
  status: StageStatus
}

// ============================================================================
// State
// ============================================================================

// Form state
const inputText = ref('')
const contextPrompt = ref('')
const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)
const interceptionResult = ref('')
const isInterceptionLoading = ref(false)

// Pipeline execution state
const isPipelineExecuting = ref(false)
const outputImage = ref<string | null>(null)
const fullscreenImage = ref<string | null>(null)

// Refs for DOM elements and scrolling
const mainContainerRef = ref<HTMLElement | null>(null)
const startButtonRef = ref<HTMLElement | null>(null)
const pipelineSectionRef = ref<HTMLElement | null>(null)

// ============================================================================
// Data
// ============================================================================

const availableCategories: Category[] = [
  { id: 'image', label: 'Bild', emoji: '🖼️', color: '#4CAF50' },
  { id: 'video', label: 'Video', emoji: '🎬', color: '#9C27B0', disabled: true },
  { id: 'sound', label: 'Sound', emoji: '🔊', color: '#FF9800', disabled: true },
  { id: '3d', label: '3D', emoji: '🧊', color: '#00BCD4', disabled: true }
]

const configsByCategory: Record<string, Config[]> = {
  image: [
    { id: 'sd35_large', label: 'Stable Diffusion', emoji: '🎨', color: '#2196F3', description: 'Klassische Bildgenerierung', logo: '/logos/logo_stable_diffusion.png', lightBg: false },
    { id: 'gpt_image_1', label: 'GPT Image', emoji: '🌟', color: '#FFC107', description: 'Moderne KI-Bilder', logo: '/logos/ChatGPT-Logo.png', lightBg: true },
    { id: 'qwen', label: 'Qwen', emoji: '🌸', color: '#9C27B0', description: 'Qwen Vision Model', logo: '/logos/Qwen_logo.png', lightBg: false }
  ],
  video: [],
  sound: [],
  '3d': []
}

const pipelineStages = ref<PipelineStage[]>([
  { id: 'safety', label: 'Sicherheit', emoji: '🛡️', color: '#4CAF50', status: 'waiting' },
  { id: 'generation', label: 'Bild', emoji: '🎨', color: '#2196F3', status: 'waiting' }
])

// Computed: Pipeline stages with dynamic medium label
const displayPipelineStages = computed(() => {
  const stages = [...pipelineStages.value]

  // Update generation stage label based on selected category
  if (selectedCategory.value && stages[1]) {
    const category = availableCategories.find(c => c.id === selectedCategory.value)
    if (category) {
      stages[1] = {
        ...stages[1],
        label: category.label,
        emoji: category.emoji
      }
    }
  }

  return stages
})

// ============================================================================
// Computed
// ============================================================================

const configsForCategory = computed(() => {
  if (!selectedCategory.value) return []
  return configsByCategory[selectedCategory.value] || []
})

const truncatedInput = computed(() => {
  if (!inputText.value) return ''
  const maxLength = 100
  return inputText.value.length > maxLength
    ? inputText.value.substring(0, maxLength) + '...'
    : inputText.value
})

const truncatedContext = computed(() => {
  if (!contextPrompt.value) return ''
  const maxLength = 100
  return contextPrompt.value.length > maxLength
    ? contextPrompt.value.substring(0, maxLength) + '...'
    : contextPrompt.value
})

const truncatedInterception = computed(() => {
  if (!interceptionResult.value) return ''
  const maxLength = 150
  return interceptionResult.value.length > maxLength
    ? interceptionResult.value.substring(0, maxLength) + '...'
    : interceptionResult.value
})

const canStartPipeline = computed(() => {
  return inputText.value &&
         selectedConfig.value &&
         interceptionResult.value &&
         !isInterceptionLoading.value
})

// ============================================================================
// Methods
// ============================================================================

function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  selectedConfig.value = null
  interceptionResult.value = ''
}

async function selectConfig(configId: string) {
  if (isInterceptionLoading.value) return

  selectedConfig.value = configId
  await runInterception()
}

async function runInterception() {
  isInterceptionLoading.value = true

  try {
    const response = await axios.post('http://localhost:17802/api/schema/pipeline/transform', {
      schema: 'overdrive',
      input_text: inputText.value,
      context_prompt: contextPrompt.value || undefined,
      user_language: 'de',
      execution_mode: 'eco',
      safety_level: 'youth',
      output_config: selectedConfig.value
    })

    if (response.data.success) {
      interceptionResult.value = response.data.transformed_prompt || ''
    } else {
      alert(`Fehler: ${response.data.error}`)
    }
  } catch (error: any) {
    console.error('Interception error:', error)
    alert(`Fehler: ${error.message}`)
  } finally {
    isInterceptionLoading.value = false
  }
}

async function startPipelineExecution() {
  isPipelineExecuting.value = true

  // Wait for DOM update to render pipeline section
  await nextTick()

  // Auto-scroll to pipeline section
  if (pipelineSectionRef.value) {
    pipelineSectionRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  // Start pipeline execution
  await executePipeline()
}

async function executePipeline() {
  // Stage 1: Safety
  if (pipelineStages.value[0]) {
    pipelineStages.value[0].status = 'processing'
    await new Promise(resolve => setTimeout(resolve, 500))
    pipelineStages.value[0].status = 'completed'
  }

  // Stage 2: Generation
  if (pipelineStages.value[1]) {
    pipelineStages.value[1].status = 'processing'
  }

  try {
    const response = await axios.post('http://localhost:17802/api/schema/pipeline/execute', {
      schema: 'overdrive',
      input_text: inputText.value,
      interception_result: interceptionResult.value,
      context_prompt: contextPrompt.value || undefined,
      user_language: 'de',
      execution_mode: 'eco',
      safety_level: 'youth',
      output_config: selectedConfig.value
    })

    if (response.data.status === 'success') {
      if (pipelineStages.value[1]) {
        pipelineStages.value[1].status = 'completed'
      }

      // Get run_id from response to construct image URL
      const runId = response.data.media_output?.run_id || response.data.run_id
      if (runId) {
        // Use Vite proxy path: /api/media/image/{run_id}
        outputImage.value = `/api/media/image/${runId}`
      } else if (response.data.outputs && response.data.outputs.length > 0) {
        // Fallback: use outputs array
        outputImage.value = `http://localhost:17802${response.data.outputs[0]}`
      }
    } else {
      alert(`Generation fehlgeschlagen: ${response.data.error}`)
      if (pipelineStages.value[1]) {
        pipelineStages.value[1].status = 'waiting'
      }
    }
  } catch (error: any) {
    console.error('Pipeline error:', error)
    alert(`Fehler: ${error.message}`)
    if (pipelineStages.value[1]) {
      pipelineStages.value[1].status = 'waiting'
    }
  } finally {
    isPipelineExecuting.value = false
  }
}

function showImageFullscreen(imageUrl: string) {
  fullscreenImage.value = imageUrl
}
</script>

<style scoped>
/* ============================================================================
   Root Container
   ============================================================================ */

.youth-flow-view {
  position: fixed;
  inset: 0;
  background: #0a0a0a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* ============================================================================
   Phase 2a: Vertical Flow
   ============================================================================ */

.phase-2a {
  max-width: clamp(320px, 90vw, 1100px);
  max-height: 90vh;
  width: 100%;
  padding: clamp(1rem, 3vw, 2rem);

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(1rem, 3vh, 2rem);

  overflow-y: auto;
  overflow-x: hidden;
}

/* Section Titles */
.section-title {
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  margin: 0 0 1rem 0;
}

/* ============================================================================
   Section 1: Input + Context (Side by Side)
   ============================================================================ */

.input-context-section {
  display: flex;
  gap: clamp(1rem, 3vw, 2rem);
  width: 100%;
  justify-content: center;
  flex-wrap: wrap;
}

.bubble-card {
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: clamp(12px, 2vw, 20px);
  padding: clamp(1rem, 2.5vw, 1.5rem);
  transition: all 0.3s ease;
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

/* Expanded state for inline editing */
.bubble-card.expanded {
  min-height: clamp(200px, 30vh, 300px);
  z-index: 100;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-bubble,
.context-bubble {
  flex: 0 1 480px;
  width: 480px;
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
}

.bubble-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.bubble-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Expanded textarea (inline editing) - unused, kept for potential future use */
.expanded-textarea {
  width: 100%;
  min-height: clamp(120px, 20vh, 180px);
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(102, 126, 234, 0.6);
  border-radius: 8px;
  color: white;
  font-size: clamp(0.9rem, 2vw, 1rem);
  padding: clamp(0.75rem, 2vw, 1rem);
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
  transition: all 0.2s ease;
}

.expanded-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.9);
  background: rgba(0, 0, 0, 0.5);
}

.expanded-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Context Preview Area */
.preview-area {
  min-height: clamp(60px, 10vh, 80px);
  cursor: pointer;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  transition: background 0.2s ease;
  margin-bottom: 0.75rem;
}

.preview-area:hover {
  background: rgba(0, 0, 0, 0.3);
}

.preview-area.large {
  min-height: clamp(80px, 12vh, 100px);
}

.preview-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: clamp(0.85rem, 1.8vw, 0.95rem);
  line-height: 1.5;
  margin: 0;
}

.placeholder-text {
  color: rgba(255, 255, 255, 0.4);
  font-size: clamp(0.85rem, 1.8vw, 0.95rem);
  font-style: italic;
  margin: 0;
}

/* ============================================================================
   Section 2: Category Bubbles (Horizontal Row)
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
   Section 3: Config Bubbles (Horizontal Row Below Categories)
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
  /* Configs centered below selected category */
  max-width: fit-content;
}

.config-bubble {
  position: relative;
  width: clamp(100px, 15vw, 130px);
  height: clamp(100px, 15vw, 130px);

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

.config-bubble:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--bubble-color);
}

.config-bubble.selected {
  transform: scale(1.1);
  background: var(--bubble-color);
  box-shadow: 0 0 30px var(--bubble-color);
  border-color: #ffffff;
}

.config-bubble.loading {
  pointer-events: none;
  opacity: 0.7;
}

.bubble-emoji-medium {
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  line-height: 1;
}

.bubble-logo {
  width: clamp(92px, 14.5vw, 122px);
  height: clamp(92px, 14.5vw, 122px);
  object-fit: contain;
}

.config-bubble.light-bg {
  background: rgba(255, 255, 255, 0.95);
}

.config-bubble.light-bg .bubble-label-medium {
  color: #0a0a0a;
}

.config-bubble.light-bg.selected {
  background: var(--bubble-color);
}

.config-bubble.light-bg.selected .bubble-label-medium {
  color: #0a0a0a;
}

.bubble-label-medium {
  position: absolute;
  bottom: clamp(8px, 1.5vw, 12px);
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  font-size: clamp(0.75rem, 1.8vw, 0.9rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.config-bubble.selected .bubble-label-medium {
  color: #0a0a0a;
}

.loading-indicator {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
}

.spinner {
  width: clamp(20px, 3vw, 28px);
  height: clamp(20px, 3vw, 28px);
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================================================
   Section 4: Interception Preview
   ============================================================================ */

.interception-section {
  width: 100%;
  display: flex;
  justify-content: center;
}

.interception-preview {
  width: 100%;
  max-width: 600px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
  box-shadow: 0 0 40px rgba(79, 172, 254, 0.6);
  transition: all 0.3s ease;
}

.interception-preview.empty {
  background: rgba(20, 20, 20, 0.5);
  border: 2px dashed rgba(255, 255, 255, 0.3);
  box-shadow: none;
}

.interception-preview.loading {
  background: rgba(20, 20, 20, 0.7);
  border: 2px solid rgba(79, 172, 254, 0.4);
  box-shadow: 0 0 20px rgba(79, 172, 254, 0.3);
}

.interception-preview .bubble-label {
  color: #0a0a0a;
}

.interception-preview.empty .bubble-label,
.interception-preview.loading .bubble-label {
  color: rgba(255, 255, 255, 0.7);
}

.interception-preview .bubble-textarea {
  background: rgba(0, 0, 0, 0.2);
}

.interception-preview.empty .bubble-textarea {
  background: rgba(0, 0, 0, 0.3);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  min-height: 120px;
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #4facfe;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: clamp(0.9rem, 2vw, 1rem);
  margin: 0;
}

/* ============================================================================
   Start Button
   ============================================================================ */

.start-button {
  padding: clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2.5rem);
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  font-weight: 700;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #ffffff;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(240, 147, 251, 0.4);
  transition: all 0.3s ease;
}

.start-button:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 6px 30px rgba(240, 147, 251, 0.6);
}

.start-button:active {
  transform: scale(0.98);
}

/* ============================================================================
   Phase 2b: Horizontal Pipeline
   ============================================================================ */

.phase-2b {
  width: 100%;
  max-width: clamp(800px, 90vw, 1200px);
  padding: clamp(2rem, 5vh, 3rem);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(2rem, 4vh, 3rem);
}

.pipeline-title {
  text-align: center;
  font-size: clamp(1.3rem, 3vw, 1.8rem);
  color: #ffffff;
  margin: 0;
}

.pipeline-stages {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1rem, 2vw, 2rem);
  flex-wrap: wrap;
}

.stage-container {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 1vw, 1rem);
}

.stage-bubble {
  position: relative;
  width: clamp(70px, 12vw, 90px);
  height: clamp(70px, 12vw, 90px);

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  background: rgba(30, 30, 30, 0.9);
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;

  transition: all 0.4s ease;
}

.stage-bubble.waiting {
  opacity: 0.5;
}

.stage-bubble.processing {
  border-color: var(--stage-color);
  box-shadow: 0 0 20px var(--stage-color);
  animation: pulse-glow 2s ease-in-out infinite;
}

.stage-bubble.completed {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
  box-shadow: 0 0 15px rgba(76, 175, 80, 0.4);
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px var(--stage-color);
  }
  50% {
    box-shadow: 0 0 40px var(--stage-color);
  }
}

.stage-emoji {
  font-size: clamp(1.5rem, 3.5vw, 2rem);
  line-height: 1;
}

.stage-label {
  font-size: clamp(0.65rem, 1.5vw, 0.75rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.status-indicator {
  position: absolute;
  bottom: clamp(8px, 1.5vw, 12px);
  right: clamp(8px, 1.5vw, 12px);
  width: clamp(20px, 3vw, 28px);
  height: clamp(20px, 3vw, 28px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
}

.status-spinner {
  width: clamp(16px, 2.5vw, 20px);
  height: clamp(16px, 2.5vw, 20px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: var(--stage-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.status-check {
  font-size: clamp(1.2rem, 2.5vw, 1.5rem);
  color: #4CAF50;
  font-weight: bold;
}

.stage-arrow {
  font-size: clamp(1.5rem, 3vw, 2rem);
  color: rgba(255, 255, 255, 0.4);
}

/* Final Output */
.final-output {
  text-align: center;
  padding: clamp(1.5rem, 3vh, 2rem);
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(76, 175, 80, 0.6);
  border-radius: clamp(12px, 2vw, 20px);
  width: 100%;
  margin-top: clamp(1rem, 3vh, 2rem);
}

.final-output h3 {
  margin: 0 0 1.5rem 0;
  font-size: clamp(1.1rem, 2.5vw, 1.4rem);
  color: #4CAF50;
}

.output-image {
  max-width: 100%;
  max-height: clamp(300px, 40vh, 500px);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.output-image:hover {
  transform: scale(1.02);
}

/* Fullscreen Modal */
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

/* Slide Down */
.slide-down-enter-active {
  animation: slideDown 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Slide Up */
.slide-up-enter-active {
  animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Phase Transition */
.phase-transition-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.phase-transition-enter-active {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.phase-transition-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-20px);
}

.phase-transition-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

/* Modal Fade */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* ============================================================================
   Scrollbar Styling
   ============================================================================ */

.phase-2a::-webkit-scrollbar {
  width: 8px;
}

.phase-2a::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.phase-2a::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.phase-2a::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* ============================================================================
   Responsive: Mobile Adjustments
   ============================================================================ */

@media (max-width: 768px) {
  .input-context-section {
    flex-direction: column;
  }

  .pipeline-stages {
    flex-direction: column;
  }

  .stage-arrow {
    transform: rotate(90deg);
  }
}

/* iPad 1024×768 Optimization */
@media (min-width: 1024px) and (max-height: 768px) {
  .phase-2a {
    padding: 1.5rem;
    gap: 1.25rem;
  }
}
</style>
