<template>
  <div class="direct-view">
    <!-- Main Content -->
    <div class="main-container">
      <!-- Input Section -->
      <section class="input-section">
        <div class="section-card">
          <div class="card-header">
            <span class="card-icon">💡</span>
            <span class="card-label">Dein Input</span>
            <div class="bubble-actions">
              <button @click="copyInputText" class="action-btn" title="Kopieren">📋</button>
              <button @click="pasteInputText" class="action-btn" title="Einfügen">📄</button>
              <button @click="clearInputText" class="action-btn" title="Löschen">🗑️</button>
            </div>
          </div>
          <textarea
            v-model="inputText"
            placeholder="Beschreibe deine Idee..."
            class="input-textarea"
            rows="6"
          ></textarea>
        </div>

        <!-- Surrealisierung Slider -->
        <div class="section-card">
          <div class="card-header">
            <span class="card-icon">🎚️</span>
            <span class="card-label">Surrealisierung</span>
          </div>
          <div class="slider-container">
            <div class="slider-labels">
              <span class="slider-label-left">very weird</span>
              <span class="slider-label-mid-left">weird</span>
              <span class="slider-label-center">normal</span>
              <span class="slider-label-mid-right">crazy</span>
              <span class="slider-label-right">really crazy</span>
            </div>
            <div class="slider-wrapper">
              <input
                type="range"
                min="-75"
                max="75"
                v-model.number="alphaFaktor"
                class="slider"
              />
            </div>
            <div class="slider-value">{{ alphaFaktor }}</div>
          </div>
        </div>

        <!-- Execute Button -->
        <button
          class="execute-button"
          :class="{ disabled: !canExecute }"
          :disabled="!canExecute"
          @click="executeWorkflow"
        >
          <span class="button-text">{{ isExecuting ? 'Surrealisiere...' : 'Surrealisieren' }}</span>
        </button>
      </section>

      <!-- Output Section -->
      <section class="output-section">
        <MediaOutputBox
          ref="pipelineSectionRef"
          :output-image="primaryOutput?.url || null"
          media-type="image"
          :is-executing="isExecuting"
          :progress="generationProgress"
          :is-analyzing="isAnalyzing"
          :show-analysis="showAnalysis"
          :analysis-data="imageAnalysis"
          forward-button-title="Weiterreichen zu Bild-Transformation"
          @save="saveMedia"
          @print="printImage"
          @forward="sendToI2I"
          @download="downloadMedia"
          @analyze="analyzeImage"
          @image-click="showImageFullscreen"
          @close-analysis="showAnalysis = false"
        />
      </section>
    </div>

    <!-- Fullscreen Image Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="fullscreenImage" class="fullscreen-modal" @click="fullscreenImage = null">
          <img :src="fullscreenImage" alt="Fullscreen" class="fullscreen-image" />
          <button class="close-fullscreen" @click="fullscreenImage = null">×</button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SpriteProgressAnimation from '@/components/SpriteProgressAnimation.vue'
import MediaOutputBox from '@/components/MediaOutputBox.vue'
import { useAppClipboard } from '@/composables/useAppClipboard'

// ============================================================================
// Types
// ============================================================================

interface OutputConfig {
  id: string
  label: string
}

interface WorkflowOutput {
  type: 'image' | 'text' | 'json' | 'unknown'
  filename: string
  url?: string
  content?: string
}

// ============================================================================
// STATE
// ============================================================================

// Global clipboard
const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()

// Router for navigation
const router = useRouter()

const inputText = ref('')
const alphaFaktor = ref<number>(0)  // Slider (-75 to +75), default 0 = normal/balanced
const isExecuting = ref(false)
const outputs = ref<WorkflowOutput[]>([])
const fullscreenImage = ref<string | null>(null)
const generationProgress = ref(0)
const primaryOutput = ref<WorkflowOutput | null>(null)

// Seed management for iterative experimentation
const previousPrompt = ref('')  // Track previous prompt
const previousAlpha = ref<number>(0)  // Track previous alpha value
const currentSeed = ref<number | null>(null)  // Current seed (null = first run)

// Image analysis state (for Stage 5)
const isAnalyzing = ref(false)
const imageAnalysis = ref<{
  analysis: string
  reflection_prompts: string[]
  insights: string[]
  success: boolean
} | null>(null)
const showAnalysis = ref(false)

// ============================================================================
// Computed
// ============================================================================

const canExecute = computed(() => {
  return inputText.value.trim().length > 0 && !isExecuting.value
})

const hasOutputs = computed(() => {
  return outputs.value.length > 0
})

// Slider percentage for CSS variable (0-100%)
// Map -75 to 0%, 0 to 50%, +75 to 100%
const alphaPercentage = computed(() => {
  return ((alphaFaktor.value + 75) / 150) * 100
})

// Alpha value is used directly (no mapping needed)
// Slider range: -75 (weird/CLIP) to 0 (normal/balanced) to +75 (crazy/T5)
const mappedAlpha = computed(() => {
  return alphaFaktor.value
})

// ============================================================================
// Methods
// ============================================================================

async function executeWorkflow() {
  if (!canExecute.value) return

  isExecuting.value = true
  outputs.value = []
  primaryOutput.value = null
  generationProgress.value = 0

  // Progress simulation (60 seconds for surrealization)
  const durationSeconds = 60 * 0.9
  const targetProgress = 98
  const updateInterval = 100
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
    // Intelligent seed logic
    const promptChanged = inputText.value !== previousPrompt.value
    const alphaChanged = alphaFaktor.value !== previousAlpha.value

    if (promptChanged || alphaChanged) {
      // Prompt OR alpha changed → Keep same seed (user wants to see parameter variation)
      if (currentSeed.value === null) {
        // First run → Use default seed
        currentSeed.value = 123456789
        console.log('[Seed Logic] First run → Default seed:', currentSeed.value)
      } else {
        console.log('[Seed Logic] Prompt or alpha changed → Keeping seed:', currentSeed.value)
      }
      // Update tracking variables
      previousPrompt.value = inputText.value
      previousAlpha.value = alphaFaktor.value
    } else {
      // Prompt AND alpha unchanged → New random seed (user wants different variation)
      currentSeed.value = Math.floor(Math.random() * 2147483647)
      console.log('[Seed Logic] No changes → New random seed:', currentSeed.value)
    }

    // Call 4-stage pipeline with surrealizer workflow execution
    // Stage 1: Translation
    // Skip Stage 2 (no interception for surrealizer)
    // Stage 3: Safety check
    // Stage 4: Legacy workflow execution
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'surrealizer', // Surrealizer config for legacy surrealization workflow
      input_text: inputText.value,
      safety_level: 'open', // Surrealizer uses open safety level
      output_config: 'surrealization_legacy',  // Hardcoded for dedicated Surrealizer
      user_language: 'de',
      alpha_factor: mappedAlpha.value,  // Inject alpha factor
      seed: currentSeed.value  // Inject seed for reproducibility
    })

    if (response.data.status === 'success') {
      // Get run_id to fetch all entities
      const runId = response.data.run_id

      if (runId) {
        clearInterval(progressInterval)
        generationProgress.value = 100

        // Fetch all entities from pipeline recorder
        await fetchAllOutputs(runId)

        // Set primary output (first image)
        const imageOutput = outputs.value.find(o => o.type === 'image')
        if (imageOutput) {
          primaryOutput.value = imageOutput
        }
      } else {
        clearInterval(progressInterval)
        console.error('[Direct] No run_id in response')
        alert('Fehler: Keine run_id erhalten')
      }
    } else {
      clearInterval(progressInterval)
      alert(`Fehler: ${response.data.error}`)
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    console.error('[Direct] Execution error:', error)
    const errorMessage = error.response?.data?.error || error.message
    alert(`Fehler: ${errorMessage}`)
  } finally {
    isExecuting.value = false
  }
}

async function fetchAllOutputs(runId: string) {
  try {
    // Fetch entities metadata
    const entitiesResponse = await axios.get(`/api/pipeline/${runId}/entities`)
    const entities = entitiesResponse.data.entities || []

    console.log('[Direct] Entities:', entities)

    // Process each entity and add to outputs
    for (const entity of entities) {
      const output = await processEntity(runId, entity)
      if (output) {
        outputs.value.push(output)
      }
    }
  } catch (error: any) {
    console.error('[Direct] Error fetching outputs:', error)
  }
}

async function processEntity(runId: string, entity: any): Promise<WorkflowOutput | null> {
  try {
    const entityType = entity.type
    const filename = entity.filename

    // FAILSAFE: Only show final outputs (entities with prefix 'output_')
    // This filters out all intermediate results:
    // - config_used, input, stage1_output, interception, safety, safety_pre_output, etc.
    if (!entityType.startsWith('output_')) {
      return null
    }

    // Fetch entity content
    const response = await axios.get(`/api/pipeline/${runId}/entity/${entityType}`, {
      responseType: 'blob' // Get as blob to handle binary data
    })

    const contentType = response.headers['content-type']

    // Determine output type from content-type
    if (contentType.startsWith('image/')) {
      // Image output
      const url = URL.createObjectURL(response.data)
      return {
        type: 'image',
        filename,
        url
      }
    } else if (contentType.includes('application/json')) {
      // JSON output
      const text = await response.data.text()
      return {
        type: 'json',
        filename,
        content: text
      }
    } else if (contentType.includes('text/')) {
      // Text output
      const text = await response.data.text()
      return {
        type: 'text',
        filename,
        content: text
      }
    } else {
      // Unknown type
      return {
        type: 'unknown',
        filename
      }
    }
  } catch (error: any) {
    console.error(`[Direct] Error processing entity:`, error)
    return null
  }
}

function formatJSON(jsonString: string): string {
  try {
    const obj = JSON.parse(jsonString)
    return JSON.stringify(obj, null, 2)
  } catch {
    return jsonString
  }
}

function showImageFullscreen(imageUrl: string) {
  fullscreenImage.value = imageUrl
}

// ============================================================================
// Textbox Actions (Copy/Paste/Delete)
// ============================================================================

function copyInputText() {
  copyToClipboard(inputText.value)
  console.log('[Direct] Input copied to clipboard')
}

function pasteInputText() {
  inputText.value = pasteFromClipboard()
  console.log('[Direct] Text pasted from clipboard')
}

function clearInputText() {
  inputText.value = ''
  console.log('[Direct] Input cleared')
}

// ============================================================================
// Media Actions (Universal for all media types)
// ============================================================================

function saveMedia() {
  // TODO: Implement save/bookmark feature for all media types
  console.log('[Media Actions] Save media (not yet implemented)')
  alert('Merken-Funktion kommt bald!')
}

function printImage() {
  if (!primaryOutput.value?.url) return

  // Open image in new window and print
  const printWindow = window.open(primaryOutput.value.url, '_blank')
  if (printWindow) {
    printWindow.onload = () => {
      printWindow.print()
    }
  }
}

function sendToI2I() {
  if (!primaryOutput.value?.url || primaryOutput.value.type !== 'image') return

  // Extract run_id from URL: /api/media/image/run_123 -> run_123
  const runIdMatch = primaryOutput.value.url.match(/\/api\/.*\/(.+)$/)
  const runId = runIdMatch ? runIdMatch[1] : null

  // Store image data in localStorage for cross-component transfer
  const transferData = {
    imageUrl: primaryOutput.value.url,  // For display
    runId: runId,  // For backend reference
    timestamp: Date.now()
  }

  localStorage.setItem('i2i_transfer_data', JSON.stringify(transferData))

  console.log('[Image Actions] Transferring to i2i:', transferData)

  // Navigate to image transformation
  router.push('/image-transformation')
}

async function downloadMedia() {
  if (!primaryOutput.value?.url || !primaryOutput.value.type) return

  try {
    // Extract run_id from URL: /api/media/{type}/{run_id}
    const runIdMatch = primaryOutput.value.url.match(/\/api\/.*\/(.+)$/)
    const runId = runIdMatch ? runIdMatch[1] : 'media'

    // Determine file extension based on media type
    const extensions: Record<string, string> = {
      'image': 'png',
      'audio': 'mp3',
      'video': 'mp4',
      'music': 'mp3',
      'code': 'js',
      '3d': 'glb'
    }
    const ext = extensions[primaryOutput.value.type] || 'bin'
    const filename = `ai4artsed_${runId}.${ext}`

    // Fetch and download
    const response = await fetch(primaryOutput.value.url)
    if (!response.ok) {
      throw new Error(`Download failed: ${response.status}`)
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)

    console.log('[Download] Media downloaded:', filename)

  } catch (error) {
    console.error('[Download] Error:', error)
    alert('Download fehlgeschlagen. Bitte versuche es erneut.')
  }
}

// ============================================================================
// Stage 5: Image Analysis (Pedagogical Reflection)
// ============================================================================

async function analyzeImage() {
  if (!primaryOutput.value?.url || primaryOutput.value.type !== 'image') {
    console.warn('[Stage 5] Can only analyze images')
    return
  }

  // Extract run_id from URL: /api/media/image/run_abc123
  const runIdMatch = primaryOutput.value.url.match(/\/api\/.*\/(.+)$/)
  const runId = runIdMatch ? runIdMatch[1] : null

  if (!runId) {
    alert('Error: Cannot determine image ID')
    return
  }

  isAnalyzing.value = true
  imageAnalysis.value = null
  console.log('[Stage 5] Starting image analysis for run_id:', runId)

  try {
    // NEW: Call universal image analysis endpoint
    const response = await fetch('/api/image/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        run_id: runId,
        analysis_type: 'bildwissenschaftlich'  // Default: Panofsky framework
        // Can be changed to: bildungstheoretisch, ethisch, kritisch
        // No prompt parameter = uses default from config.py
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    const data = await response.json()

    if (data.success && data.analysis) {
      // Parse analysis text into structured format
      imageAnalysis.value = {
        analysis: data.analysis,
        reflection_prompts: extractReflectionPrompts(data.analysis),
        insights: extractInsights(data.analysis),
        success: true
      }
      showAnalysis.value = true
      console.log('[Stage 5] Analysis complete')
    } else {
      throw new Error(data.error || 'Unknown error')
    }

  } catch (error: any) {
    console.error('[Stage 5] Error:', error)
    alert(`Image analysis failed: ${error.message || error}`)
  } finally {
    isAnalyzing.value = false
  }
}

// Helper functions for parsing analysis text
function extractReflectionPrompts(analysisText: string): string[] {
  const match = analysisText.match(/REFLEXIONSFRAGEN:|REFLECTION QUESTIONS:([\s\S]*?)(?:\n\n|$)/i)
  if (match && match[1]) {
    return match[1]
      .split('\n')
      .filter(line => line.trim().startsWith('-'))
      .map(line => line.replace(/^-\s*/, '').trim())
      .filter(q => q.length > 0)
  }
  return []
}

function extractInsights(analysisText: string): string[] {
  const keywords = ['Komposition', 'Farbe', 'Licht', 'Perspektive', 'Stil',
                   'Composition', 'Color', 'Light', 'Perspective', 'Style']
  return keywords.filter(kw =>
    analysisText.toLowerCase().includes(kw.toLowerCase())
  )
}
</script>

<style scoped>
/* ============================================================================
   Root Container
   ============================================================================ */

.direct-view {
  min-height: 100vh;
  background: #0a0a0a;
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* ============================================================================
   Main Container
   ============================================================================ */

.main-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ============================================================================
   Sections
   ============================================================================ */

.input-section,
.output-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-card {
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card-icon {
  font-size: 1.5rem;
}

.card-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.bubble-actions {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.bubble-actions .action-btn {
  background: transparent;
  border: none;
  font-size: 0.9rem;
  opacity: 0.4;
  cursor: pointer;
  transition: opacity 0.2s;
  padding: 0.25rem;
}

.bubble-actions .action-btn:hover {
  opacity: 0.8;
}

/* ============================================================================
   Input Elements
   ============================================================================ */

.input-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  padding: 0.75rem;
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
  min-height: 150px;
}

.input-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.config-select {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  padding: 0.75rem;
  cursor: pointer;
  font-family: inherit;
}

.config-select:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
}

/* ============================================================================
   Slider
   ============================================================================ */

.slider-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.slider-label-left {
  color: rgba(147, 51, 234, 0.9); /* Purple for "very weird" */
}

.slider-label-mid-left {
  color: rgba(120, 80, 240, 0.8); /* Purple-Blue for "weird" */
  font-size: 0.9rem;
  font-weight: 500;
}

.slider-label-center {
  color: rgba(59, 130, 246, 0.9); /* Blue for "normal" */
  font-weight: 700;
}

.slider-label-mid-right {
  color: rgba(180, 100, 200, 0.8); /* Blue-Pink for "crazy" */
  font-size: 0.9rem;
  font-weight: 500;
}

.slider-label-right {
  color: rgba(236, 72, 153, 0.9); /* Pink for "really crazy" */
}

.slider-wrapper {
  width: 100%;
  padding: 0.5rem 0;
}

.slider {
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 16px; /* Double thickness */
  background: linear-gradient(
    to right,
    rgba(147, 51, 234, 0.6) 0%,    /* Purple (weird) */
    rgba(59, 130, 246, 0.6) 50%,   /* Blue (normal) */
    rgba(236, 72, 153, 0.6) 100%   /* Pink (crazy) */
  );
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.95), rgba(99, 102, 241, 0.95));
  cursor: grab;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
  cursor: grabbing;
}

.slider::-webkit-slider-thumb:active {
  cursor: grabbing;
  transform: scale(1.05);
}

.slider::-moz-range-thumb {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.95), rgba(99, 102, 241, 0.95));
  cursor: grab;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.slider::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
  cursor: grabbing;
}

.slider::-moz-range-thumb:active {
  cursor: grabbing;
  transform: scale(1.05);
}

/* Value display centered below slider */
.slider-value {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(59, 130, 246, 0.95); /* Blue color matching thumb */
  margin-top: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* ============================================================================
   Execute Button
   ============================================================================ */

.execute-button {
  width: 100%;
  padding: 1rem 2rem;
  font-size: 1.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.execute-button:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.execute-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

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

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* ============================================================================
   Responsive
   ============================================================================ */

@media (max-width: 768px) {
  .main-container {
    padding: 1rem;
  }

  .return-button {
    left: 1rem;
  }

  .page-title {
    font-size: 1.2rem;
  }
}
</style>
