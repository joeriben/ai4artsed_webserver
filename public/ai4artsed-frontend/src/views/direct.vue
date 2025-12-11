<template>
  <div class="direct-view">
    <!-- Header -->
    <header class="page-header">
      <button class="return-button" @click="$router.push('/')" title="Zurück zur Startseite">
        ← Zurück
      </button>
      <h1 class="page-title">Surrealisierer</h1>
    </header>

    <!-- Main Content -->
    <div class="main-container">
      <!-- Input Section -->
      <section class="input-section">
        <div class="section-card">
          <div class="card-header">
            <span class="card-icon">💡</span>
            <span class="card-label">Dein Input</span>
          </div>
          <textarea
            v-model="inputText"
            placeholder="Beschreibe deine Idee..."
            class="input-textarea"
            rows="6"
          ></textarea>
        </div>

        <!-- Output Config Selection -->
        <div class="section-card">
          <div class="card-header">
            <span class="card-icon">⚙️</span>
            <span class="card-label">Surrealisierungs-Stil auswählen</span>
          </div>
          <select v-model="selectedOutputConfig" class="config-select">
            <option value="" disabled>Stil auswählen...</option>
            <option
              v-for="config in availableConfigs"
              :key="config.id"
              :value="config.id"
            >
              {{ config.label }}
            </option>
          </select>
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
      <section class="output-section" v-if="hasOutputs || isExecuting">
        <div class="section-card">
          <div class="card-header">
            <span class="card-icon">🎨</span>
            <span class="card-label">Surrealisierte Ausgabe</span>
          </div>

          <!-- Loading State -->
          <div v-if="isExecuting && !hasOutputs" class="loading-container">
            <div class="spinner"></div>
            <p class="loading-text">Surrealisierung läuft...</p>
          </div>

          <!-- Outputs Display (naiv, alle Outputs in Reihenfolge) -->
          <div v-else class="outputs-container">
            <div
              v-for="(output, index) in outputs"
              :key="index"
              class="output-item"
            >
              <!-- Image Output -->
              <div v-if="output.type === 'image'" class="output-image-wrapper">
                <img
                  :src="output.url"
                  :alt="`Output ${index + 1}`"
                  class="output-image"
                  @click="showFullscreen(output.url)"
                />
                <p class="output-caption">{{ output.filename }}</p>
              </div>

              <!-- Text Output -->
              <div v-else-if="output.type === 'text'" class="output-text-wrapper">
                <div class="text-header">
                  <span class="text-icon">📄</span>
                  <span class="text-filename">{{ output.filename }}</span>
                </div>
                <pre class="output-text">{{ output.content }}</pre>
              </div>

              <!-- JSON Output -->
              <div v-else-if="output.type === 'json'" class="output-json-wrapper">
                <div class="json-header">
                  <span class="json-icon">📋</span>
                  <span class="json-filename">{{ output.filename }}</span>
                </div>
                <pre class="output-json">{{ formatJSON(output.content) }}</pre>
              </div>

              <!-- Unknown Output Type -->
              <div v-else class="output-unknown-wrapper">
                <p class="unknown-type">Unbekannter Output-Typ: {{ output.type }}</p>
                <p class="unknown-filename">{{ output.filename }}</p>
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
import axios from 'axios'

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
// State
// ============================================================================

const inputText = ref('')
const selectedOutputConfig = ref('')
const isExecuting = ref(false)
const outputs = ref<WorkflowOutput[]>([])
const fullscreenImage = ref<string | null>(null)

// Available output configs (legacy workflows)
const availableConfigs: OutputConfig[] = [
  { id: 'surrealization_legacy', label: 'Surrealization (Legacy)' },
  // Add more legacy workflows here as needed
]

// ============================================================================
// Computed
// ============================================================================

const canExecute = computed(() => {
  return inputText.value.trim().length > 0 && selectedOutputConfig.value && !isExecuting.value
})

const hasOutputs = computed(() => {
  return outputs.value.length > 0
})

// ============================================================================
// Methods
// ============================================================================

async function executeWorkflow() {
  if (!canExecute.value) return

  isExecuting.value = true
  outputs.value = [] // Clear previous outputs

  try {
    // Call 4-stage pipeline with surrealizer workflow execution
    // Stage 1: Translation
    // Skip Stage 2 (no interception for surrealizer)
    // Stage 3: Safety check
    // Stage 4: Legacy workflow execution
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'surrealizer', // Surrealizer config for legacy surrealization workflow
      input_text: inputText.value,
      safety_level: 'open', // Surrealizer uses open safety level
      output_config: selectedOutputConfig.value,
      user_language: 'de'
    })

    if (response.data.status === 'success') {
      // Get run_id to fetch all entities
      const runId = response.data.run_id

      if (runId) {
        // Fetch all entities from pipeline recorder
        await fetchAllOutputs(runId)
      } else {
        console.error('[Direct] No run_id in response')
        alert('Fehler: Keine run_id erhalten')
      }
    } else {
      alert(`Fehler: ${response.data.error}`)
    }
  } catch (error: any) {
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

function showFullscreen(url: string) {
  fullscreenImage.value = url
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
   Header
   ============================================================================ */

.page-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  padding: 1.5rem 2rem;
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
}

.return-button {
  position: absolute;
  left: 2rem;
  padding: 0.6rem 1.2rem;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.return-button:hover {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.2);
  transform: translateX(-4px);
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
   Loading State
   ============================================================================ */

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  margin: 0;
}

/* ============================================================================
   Outputs Container
   ============================================================================ */

.outputs-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.output-item {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
}

/* Image Output */
.output-image-wrapper {
  text-align: center;
}

.output-image {
  max-width: 100%;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.output-image:hover {
  transform: scale(1.02);
}

.output-caption {
  margin-top: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* Text Output */
.output-text-wrapper,
.output-json-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.text-header,
.json-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
}

.text-icon,
.json-icon {
  font-size: 1.2rem;
}

.text-filename,
.json-filename {
  font-weight: 600;
}

.output-text,
.output-json {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Unknown Output */
.output-unknown-wrapper {
  text-align: center;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.unknown-type {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.unknown-filename {
  font-size: 0.9rem;
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
