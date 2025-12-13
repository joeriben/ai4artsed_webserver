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

        <!-- Elimination Mode Dropdown -->
        <div class="section-card">
          <div class="card-header">
            <span class="card-icon">🎛️</span>
            <span class="card-label">Eliminationsmodus</span>
          </div>
          <div class="dropdown-container">
            <select v-model="eliminationMode" class="mode-select">
              <option value="average">Average (Durchschnitt)</option>
              <option value="random">Random (Zufall)</option>
              <option value="invert">Invert (Umkehrung)</option>
              <option value="zero_out">Zero Out (Nullsetzen)</option>
            </select>
            <div class="mode-description">{{ modeDescription }}</div>
          </div>
        </div>

        <!-- Execute Button -->
        <button
          class="execute-button"
          :class="{ disabled: !canExecute }"
          :disabled="!canExecute"
          @click="executeWorkflow"
        >
          <span class="button-text">{{ isExecuting ? 'Generiere...' : 'Ausführen' }}</span>
        </button>
      </section>

      <!-- Output Frame (3 States: empty, generating, final) -->
      <section class="output-section">
        <div class="output-frame" :class="{
          empty: !isExecuting && outputs.length === 0,
          generating: isExecuting && outputs.length === 0
        }">
          <!-- State 1: Empty (before generation) -->
          <div v-if="!isExecuting && outputs.length === 0" class="empty-state">
            <div class="empty-icon">🖼️</div>
            <p>Deine 3 Bildvarianten erscheinen hier</p>
            <p class="empty-subtitle">Referenz · Erste Hälfte · Zweite Hälfte</p>
          </div>

          <!-- State 2: Generating (progress animation) -->
          <div v-if="isExecuting && outputs.length === 0" class="generation-animation-container">
            <SpriteProgressAnimation :progress="generationProgress" />
          </div>

          <!-- State 3: Final Output (3 Images Side by Side) -->
          <div v-else-if="outputs.length > 0" class="final-output">
            <div class="multi-image-grid">
              <div
                v-for="(output, idx) in outputs"
                :key="idx"
                class="image-box"
              >
                <!-- Image with Actions -->
                <div class="image-with-actions">
                  <img
                    :src="output.url"
                    :alt="output.label"
                    class="output-image"
                    @click="showFullscreen(output.url)"
                  />

                  <!-- Action Toolbar (vertical, right side) -->
                  <div class="action-toolbar">
                    <button class="action-btn" @click="saveMedia(idx)" disabled title="Merken (Coming Soon)">
                      <span class="action-icon">⭐</span>
                    </button>
                    <button class="action-btn" @click="printImage(idx)" title="Drucken">
                      <span class="action-icon">🖨️</span>
                    </button>
                    <button class="action-btn" @click="sendToI2I(idx)" title="Weiterreichen zu Bild-Transformation">
                      <span class="action-icon">➡️</span>
                    </button>
                    <button class="action-btn" @click="downloadMedia(idx)" title="Herunterladen">
                      <span class="action-icon">💾</span>
                    </button>
                  </div>
                </div>

                <!-- Image Label -->
                <div class="image-label">
                  <h4>{{ output.label }}</h4>
                  <p>{{ output.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
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
import { useAppClipboard } from '@/composables/useAppClipboard'

// ============================================================================
// Types
// ============================================================================

interface ImageOutput {
  url: string
  label: string
  description: string
  filename: string
}

// ============================================================================
// STATE
// ============================================================================

// Global clipboard
const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()

// Router for navigation
const router = useRouter()

const inputText = ref('')
const eliminationMode = ref('average')
const isExecuting = ref(false)
const outputs = ref<ImageOutput[]>([])
const fullscreenImage = ref<string | null>(null)
const generationProgress = ref(0)

// Seed management for iterative experimentation
const previousPrompt = ref('')
const previousMode = ref('average')
const currentSeed = ref<number | null>(null)

// ============================================================================
// Computed
// ============================================================================

const canExecute = computed(() => {
  return inputText.value.trim().length > 0 && !isExecuting.value
})

const modeDescription = computed(() => {
  const descriptions: Record<string, string> = {
    average: 'Ersetzt Dimensionen durch Durchschnittswert',
    random: 'Ersetzt Dimensionen durch Zufallswerte',
    invert: 'Kehrt Vorzeichen der Dimensionen um',
    zero_out: 'Setzt Dimensionen auf Null'
  }
  return descriptions[eliminationMode.value] || ''
})

// ============================================================================
// Methods
// ============================================================================

async function executeWorkflow() {
  if (!canExecute.value) return

  isExecuting.value = true
  outputs.value = []
  generationProgress.value = 0

  // Progress simulation (60 seconds for partial elimination)
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
    const modeChanged = eliminationMode.value !== previousMode.value

    if (promptChanged || modeChanged) {
      // Prompt OR mode changed → Keep same seed (user wants to see parameter variation)
      if (currentSeed.value === null) {
        // First run → Use default seed
        currentSeed.value = 123456789
        console.log('[Seed Logic] First run → Default seed:', currentSeed.value)
      } else {
        console.log('[Seed Logic] Prompt or mode changed → Keeping seed:', currentSeed.value)
      }
      // Update tracking variables
      previousPrompt.value = inputText.value
      previousMode.value = eliminationMode.value
    } else {
      // Prompt AND mode unchanged → New random seed (user wants different variation)
      currentSeed.value = Math.floor(Math.random() * 2147483647)
      console.log('[Seed Logic] No changes → New random seed:', currentSeed.value)
    }

    // Call 4-stage pipeline with partial_elimination workflow execution
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'partial_elimination',
      input_text: inputText.value,
      safety_level: 'open',
      output_config: 'partial_elimination_legacy',
      user_language: 'de',
      mode: eliminationMode.value,
      seed: currentSeed.value
    })

    if (response.data.status === 'success') {
      // Get run_id to fetch all entities
      const runId = response.data.run_id

      if (runId) {
        clearInterval(progressInterval)
        generationProgress.value = 100

        // Fetch all outputs from pipeline recorder
        await fetchAllOutputs(runId)
      } else {
        clearInterval(progressInterval)
        console.error('[Partial Elimination] No run_id in response')
        alert('Fehler: Keine run_id erhalten')
      }
    } else {
      clearInterval(progressInterval)
      alert(`Fehler: ${response.data.error}`)
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    console.error('[Partial Elimination] Execution error:', error)
    const errorMessage = error.response?.data?.error || error.message
    alert(`Fehler: ${errorMessage}`)
  } finally {
    isExecuting.value = false
  }
}

async function fetchAllOutputs(runId: string) {
  try {
    // Step 1: Fetch all entities metadata
    const entitiesResponse = await axios.get(`/api/pipeline/${runId}/entities`)
    const entities = entitiesResponse.data.entities || []

    console.log('[Partial Elimination] All entities:', entities)

    // Step 2: First, get the 3 individual images using /api/media/images
    try {
      const imagesResponse = await axios.get(`/api/media/images/${runId}`)

      if (imagesResponse.data.images && imagesResponse.data.images.length > 0) {
        const labels = [
          { label: 'Referenzbild', description: 'Unmanipulierte Ausgabe (Original)' },
          { label: 'Erste Hälfte eliminiert', description: `Dimensionen 0-2047 (${eliminationMode.value})` },
          { label: 'Zweite Hälfte eliminiert', description: `Dimensionen 2048-4095 (${eliminationMode.value})` }
        ]

        // Add the 3 individual images
        outputs.value = imagesResponse.data.images.map((img: any, idx: number) => ({
          url: img.url,
          label: labels[idx]?.label || `Bild ${idx + 1}`,
          description: labels[idx]?.description || '',
          filename: img.metadata?.original_filename || `image_${idx}.png`
        }))

        console.log('[Partial Elimination] Loaded 3 individual images')
      }
    } catch (error) {
      console.error('[Partial Elimination] Failed to load individual images:', error)
    }

    // Step 3: Then, try to fetch the composite image separately
    const compositeEntity = entities.find((e: any) => e.type === 'output_image_composite')

    if (compositeEntity) {
      try {
        console.log('[Partial Elimination] Found composite entity:', compositeEntity.filename)

        // Fetch composite using new filename-based endpoint
        const compositeResponse = await axios.get(`/api/pipeline/${runId}/file/${compositeEntity.filename}`, {
          responseType: 'blob'
        })

        const compositeUrl = URL.createObjectURL(compositeResponse.data)

        // Add composite as 4th image
        outputs.value.push({
          url: compositeUrl,
          label: 'Composite (alle 3)',
          description: 'Zusammengesetztes Bild mit allen Varianten',
          filename: compositeEntity.filename
        })

        console.log('[Partial Elimination] Loaded composite image:', compositeEntity.filename)
      } catch (error) {
        console.error('[Partial Elimination] Failed to load composite:', error)
      }
    } else {
      console.log('[Partial Elimination] No composite entity found')
    }
  } catch (error: any) {
    console.error('[Partial Elimination] Error fetching outputs:', error)
  }
}

function showFullscreen(url: string) {
  fullscreenImage.value = url
}

// ============================================================================
// Textbox Actions (Copy/Paste/Delete)
// ============================================================================

function copyInputText() {
  copyToClipboard(inputText.value)
  console.log('[Partial Elimination] Input copied to clipboard')
}

function pasteInputText() {
  inputText.value = pasteFromClipboard()
  console.log('[Partial Elimination] Text pasted from clipboard')
}

function clearInputText() {
  inputText.value = ''
  console.log('[Partial Elimination] Input cleared')
}

// ============================================================================
// Media Actions (For Each Image)
// ============================================================================

function saveMedia(idx: number) {
  // TODO: Implement save/bookmark feature
  console.log('[Media Actions] Save media (not yet implemented)', idx)
  alert('Merken-Funktion kommt bald!')
}

function printImage(idx: number) {
  if (!outputs.value[idx]?.url) return

  const printWindow = window.open(outputs.value[idx].url, '_blank')
  if (printWindow) {
    printWindow.onload = () => {
      printWindow.print()
    }
  }
}

function sendToI2I(idx: number) {
  if (!outputs.value[idx]?.url) return

  // Extract run_id from URL
  const runIdMatch = outputs.value[idx].url.match(/\/api\/.*\/(.+)$/)
  const runId = runIdMatch ? runIdMatch[1] : null

  // Store image data in localStorage for cross-component transfer
  const transferData = {
    imageUrl: outputs.value[idx].url,
    runId: runId,
    timestamp: Date.now()
  }

  localStorage.setItem('i2i_transfer_data', JSON.stringify(transferData))

  console.log('[Image Actions] Transferring to i2i:', transferData)

  // Navigate to image transformation
  router.push('/image-transformation')
}

async function downloadMedia(idx: number) {
  if (!outputs.value[idx]?.url) return

  try {
    // Extract run_id from URL
    const runIdMatch = outputs.value[idx].url.match(/\/api\/.*\/(.+)$/)
    const runId = runIdMatch ? runIdMatch[1] : 'media'

    const filename = `ai4artsed_partial_elimination_${outputs.value[idx].label.replace(/\s+/g, '_')}_${runId}.png`

    // Fetch and download
    const response = await fetch(outputs.value[idx].url)
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
  max-width: 1400px;
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

/* ============================================================================
   Dropdown
   ============================================================================ */

.dropdown-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mode-select {
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

.mode-select:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
}

.mode-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  padding-left: 0.5rem;
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
   Output Frame (3 States)
   ============================================================================ */

.output-frame {
  width: 100%;
  max-width: 1400px;
  margin: 2rem auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  transition: all 0.3s ease;
  min-height: 400px;
}

.output-frame.empty {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  background: rgba(20, 20, 20, 0.5);
}

.output-frame.generating {
  border: 2px solid rgba(76, 175, 80, 0.6);
  background: rgba(30, 30, 30, 0.9);
  box-shadow: 0 0 30px rgba(76, 175, 80, 0.3);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  opacity: 0.4;
}

.empty-icon {
  font-size: 5rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  margin: 0;
}

.empty-subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.4);
}

/* Generation Animation Container */
.generation-animation-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* Final Output - Multi-Image Grid */
.final-output {
  width: 100%;
}

.multi-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  width: 100%;
}

.image-box {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Image with Actions */
.image-with-actions {
  position: relative;
  display: inline-block;
}

.output-image {
  width: 100%;
  max-width: 100%;
  max-height: 400px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  cursor: pointer;
  transition: transform 0.3s ease;
  object-fit: contain;
}

.output-image:hover {
  transform: scale(1.02);
}

/* Action Toolbar */
.action-toolbar {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.action-toolbar .action-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  opacity: 1;
}

.action-toolbar .action-btn:hover:not(:disabled) {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.action-toolbar .action-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.action-toolbar .action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-icon {
  font-size: 1.5rem;
  line-height: 1;
}

/* Image Label */
.image-label {
  text-align: center;
  padding: 1rem;
  background: rgba(20, 20, 20, 0.8);
  border-radius: 8px;
}

.image-label h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
}

.image-label p {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

/* Responsive: Stack toolbar below media on mobile */
@media (max-width: 768px) {
  .multi-image-grid {
    grid-template-columns: 1fr;
  }

  .image-with-actions {
    flex-direction: column;
  }

  .action-toolbar {
    position: static;
    transform: none;
    flex-direction: row;
    gap: 0.5rem;
    margin-top: 1rem;
    justify-content: center;
  }

  .action-toolbar .action-btn {
    width: 40px;
    height: 40px;
  }

  .action-icon {
    font-size: 1.25rem;
  }
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
}
</style>
