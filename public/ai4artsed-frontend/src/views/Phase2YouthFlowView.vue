<template>
  <div class="youth-flow-view">
    <!-- Horizontal Flow Layout -->
    <div class="horizontal-flow-container">
      <!-- Left Column: Input & Context Stack -->
      <div class="input-context-stack">
        <div class="bubble-wrapper">
          <div
            class="flow-bubble input-context-bubble"
            :class="[`status-${inputText ? 'filled' : 'empty'}`]"
            :style="{ '--bubble-color': '#2196F3' }"
            @click="editingBubble === 'input' ? null : (editingBubble = 'input')"
          >
            <div class="bubble-content">
              <div class="bubble-label">INPUT</div>
              <div
                v-if="editingBubble !== 'input'"
                class="bubble-preview"
              >
                {{ inputText || 'Click to enter prompt...' }}
              </div>
              <textarea
                v-else
                ref="inputTextarea"
                v-model="inputText"
                class="bubble-editor"
                placeholder="Enter your prompt here..."
                @blur="editingBubble = null"
                @keydown.esc="editingBubble = null"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="flow-arrow-down">↓</div>

        <div class="bubble-wrapper">
          <div
            class="flow-bubble input-context-bubble"
            :class="[`status-${contextPrompt ? 'filled' : 'empty'}`]"
            :style="{ '--bubble-color': '#9C27B0' }"
            @click="editingBubble === 'context' ? null : (editingBubble = 'context')"
          >
            <div class="bubble-content">
              <div class="bubble-label">CONTEXT</div>
              <div
                v-if="editingBubble !== 'context'"
                class="bubble-preview"
              >
                {{ contextPrompt || 'Optional context...' }}
              </div>
              <textarea
                v-else
                ref="contextTextarea"
                v-model="contextPrompt"
                class="bubble-editor"
                placeholder="Optional context for transformation..."
                @blur="editingBubble = null"
                @keydown.esc="editingBubble = null"
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <div class="flow-arrow-right">→</div>

      <!-- Medium Selection -->
      <div class="medium-selection-stack">
        <div class="flow-label-text">{{ $t('selectMedium', 'Wähle Output-Medium') }}</div>
        <div
          v-for="medium in availableMedia"
          :key="medium.id"
          class="bubble-wrapper"
        >
          <div
            class="flow-bubble medium-bubble"
            :class="[`status-${selectedOutputMedium === medium.id ? 'filled' : 'empty'}`]"
            :style="{ '--bubble-color': medium.color }"
            @click="handleMediumSelection(medium)"
          >
            <div class="bubble-content">
              <div class="bubble-label">{{ medium.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Weiter Button -->
      <button
        v-if="selectedOutputMedium && !interceptionResult && !isInterceptionProcessing"
        class="continue-button"
        @click="submitContextAndRunInterception"
      >
        WEITER
      </button>

      <!-- After medium selection: show INTERCEPTION bubble -->
      <template v-if="selectedOutputMedium">
        <div class="flow-arrow-right">→</div>

        <!-- Interception Bubble - editable -->
        <div class="bubble-wrapper">
          <div
            class="flow-bubble"
            :class="[`status-${interceptionResult ? (isInterceptionProcessing ? 'processing' : 'completed') : 'waiting'}`]"
            :style="{ '--bubble-color': '#9C27B0' }"
            @click="interceptionResult && !isInterceptionProcessing && editingBubble !== 'interception' ? (editingBubble = 'interception') : null"
          >
            <div class="bubble-content">
              <div class="bubble-label">INTERCEPTION</div>
              <div
                v-if="interceptionResult && editingBubble !== 'interception'"
                class="bubble-preview"
              >
                {{ interceptionResult }}
              </div>
              <textarea
                v-else-if="editingBubble === 'interception'"
                ref="interceptionTextarea"
                v-model="interceptionResult"
                class="bubble-editor"
                @blur="editingBubble = null"
                @keydown.esc="editingBubble = null"
              ></textarea>
              <div v-if="isInterceptionProcessing" class="processing-spinner"></div>
              <div v-if="interceptionResult && !isInterceptionProcessing" class="completed-check">✓</div>
            </div>
          </div>
        </div>

        <!-- START Button (only show after interception is done) -->
        <button
          v-if="interceptionResult && !isInterceptionProcessing && !pipelineStarted"
          class="start-button"
          @click="startPipeline"
        >
          START!
        </button>
      </template>

      <!-- Pipeline - only show AFTER start -->
      <template v-if="pipelineStarted">
        <div class="flow-arrow-right">→</div>

        <!-- Safety (small) -->
        <div class="bubble-wrapper">
          <div
            class="flow-bubble bubble-small"
            :class="[`status-${pipelineStages[0].status}`]"
            :style="{ '--bubble-color': pipelineStages[0].color }"
          >
            <div class="bubble-content">
              <div class="bubble-label">{{ pipelineStages[0].label }}</div>
              <div v-if="pipelineStages[0].status === 'processing'" class="processing-spinner"></div>
              <div v-if="pipelineStages[0].status === 'completed'" class="completed-check">✓</div>
            </div>
          </div>
        </div>

        <div class="flow-arrow-right">→</div>

        <!-- Generation -->
        <div class="bubble-wrapper">
          <div
            class="flow-bubble"
            :class="[`status-${pipelineStages[1].status}`]"
            :style="{ '--bubble-color': pipelineStages[1].color }"
          >
            <div class="bubble-content">
              <div class="bubble-label">{{ pipelineStages[1].label }}</div>
              <div v-if="pipelineStages[1].status === 'processing'" class="processing-spinner"></div>
              <div v-if="pipelineStages[1].status === 'completed'" class="completed-check">✓</div>
            </div>
          </div>
        </div>

        <div class="flow-arrow-right">→</div>

        <!-- Output Image -->
        <div class="bubble-wrapper">
          <div
            v-if="!outputImage"
            class="flow-bubble"
            :class="['status-waiting']"
            :style="{ '--bubble-color': '#4CAF50' }"
          >
            <div class="bubble-content">
              <div class="bubble-label">OUTPUT</div>
            </div>
          </div>
          <img
            v-else
            :src="outputImage"
            alt="Generated Output"
            class="output-image"
            @click="showImageFullscreen(outputImage)"
          />
        </div>
      </template>
    </div>

    <!-- Fullscreen Image Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="fullscreenImage" class="fullscreen-modal" @click="fullscreenImage = null">
          <img :src="fullscreenImage" alt="Generated Output" class="fullscreen-image" />
          <button class="close-fullscreen" @click="fullscreenImage = null">×</button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()

// Available OUTPUT media (not interception configs!)
// Using Phase 1 Material Design color palette
const availableMedia = ref([
  { id: 'sd35_large', label: 'SD 3.5 Large', color: '#4CAF50' },     // Green (heritage)
  { id: 'gpt_image_1', label: 'GPT Image', color: '#2196F3' },       // Blue (semantics)
  { id: 'acestep_simple', label: 'Acestep Simple', color: '#E91E63' } // Pink (arts)
])

// Selected output medium
const selectedOutputMedium = ref<string>('sd35_large')

// State
const inputText = ref('')
const contextPrompt = ref('')
const selectedMediumId = ref<string | null>(null)
const selectedMediumConfig = ref<any>(null)
const interceptionResult = ref('')
const isInterceptionProcessing = ref(false)
const pipelineStarted = ref(false)
const outputImage = ref<string | null>(null)
const fullscreenImage = ref<string | null>(null)

// Inline editing state
const editingBubble = ref<'input' | 'context' | 'interception' | null>(null)
const inputTextarea = ref<HTMLTextAreaElement | null>(null)
const contextTextarea = ref<HTMLTextAreaElement | null>(null)
const interceptionTextarea = ref<HTMLTextAreaElement | null>(null)

// Pipeline stages (simplified - using Phase 1 Material Design colors)
const pipelineStages = ref([
  {
    name: 'safety',
    label: 'SAFETY',
    status: 'waiting' as const,
    previewText: '',
    color: '#E91E63',  // Pink (arts)
    size: 'small'
  },
  {
    name: 'generation',
    label: 'GENERATION',
    status: 'waiting' as const,
    previewText: '',
    color: '#4CAF50',  // Green (heritage)
    size: 'normal'
  }
])

// Handle output medium selection (Phase 2: just select, don't run interception yet)
function handleMediumSelection(medium: any) {
  selectedOutputMedium.value = medium.id
}

// Handle context submission - trigger interception with fixed "overdrive" config
async function submitContextAndRunInterception() {
  if (!inputText.value) {
    alert('Bitte zuerst Input-Text eingeben!')
    return
  }

  // Trigger interception API with fixed "overdrive" config for Youth Mode
  isInterceptionProcessing.value = true
  interceptionResult.value = ''

  try {
    const response = await axios.post('http://localhost:17802/api/schema/pipeline/transform', {
      schema: 'overdrive',  // Fixed interception config for Youth Mode
      input_text: inputText.value,
      context_prompt: contextPrompt.value || undefined,
      user_language: 'de'
    })

    if (response.data.success) {
      interceptionResult.value = response.data.interception_result?.result || response.data.result || ''
    } else {
      alert(`Interception fehlgeschlagen: ${response.data.error}`)
    }
  } catch (error: any) {
    console.error('Interception error:', error)
    alert(`Fehler: ${error.message}`)
  } finally {
    isInterceptionProcessing.value = false
  }
}

// Start pipeline execution
async function startPipeline() {
  // Start pipeline visualization
  pipelineStarted.value = true

  // Execute pipeline stages sequentially
  await executePipelineStages()
}

async function executePipelineStages() {
  const API_BASE = 'http://localhost:17802'

  try {
    // Stage 3: Safety
    pipelineStages.value[2].status = 'processing'
    await new Promise(resolve => setTimeout(resolve, 500))

    // TODO: Call actual safety API
    pipelineStages.value[2].status = 'completed'
    pipelineStages.value[2].previewText = 'Safe ✓'

    // Stage 4: Pre-Output
    pipelineStages.value[3].status = 'processing'
    await new Promise(resolve => setTimeout(resolve, 500))

    // TODO: Call actual pre-output API
    pipelineStages.value[3].status = 'completed'
    pipelineStages.value[3].previewText = 'Enhanced prompt'

    // Stage 5: Generation
    pipelineStages.value[4].status = 'processing'

    const response = await axios.post(`${API_BASE}/api/schema/pipeline/execute`, {
      schema: 'overdrive',
      input_text: inputText.value,
      interception_config: selectedMediumId.value,
      interception_result: interceptionResult.value,
      context_prompt: contextPrompt.value || undefined,
      user_language: 'de',
      execution_mode: 'eco',
      safety_level: 'youth',
      output_config: 'sd35_large'
    })

    if (response.data.status === 'success') {
      pipelineStages.value[4].status = 'completed'
      pipelineStages.value[4].previewText = 'Image generated!'

      // Get output image
      if (response.data.outputs && response.data.outputs.length > 0) {
        outputImage.value = `${API_BASE}${response.data.outputs[0]}`
      }
    } else {
      alert(`Generation failed: ${response.data.error}`)
    }
  } catch (error: any) {
    console.error('Pipeline execution error:', error)
    alert(`Error: ${error.message}`)
  }
}

function showImageFullscreen(imageUrl: string) {
  fullscreenImage.value = imageUrl
}

// Auto-focus textarea when editing starts
watch(editingBubble, async (newValue) => {
  if (newValue) {
    await nextTick()
    if (newValue === 'input' && inputTextarea.value) {
      inputTextarea.value.focus()
    } else if (newValue === 'context' && contextTextarea.value) {
      contextTextarea.value.focus()
    } else if (newValue === 'interception' && interceptionTextarea.value) {
      interceptionTextarea.value.focus()
    }
  }
})

// Initialize from route params if available
onMounted(() => {
  const promptFromRoute = route.query.prompt as string
  if (promptFromRoute) {
    inputText.value = promptFromRoute
  }
})
</script>

<style scoped>
.youth-flow-view {
  position: fixed;
  inset: 0;
  background: #000000;
  overflow-x: auto;
  overflow-y: hidden;
}

/* Horizontal Flow Container */
.horizontal-flow-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 2rem;
  min-height: 100vh;
  padding: 2rem;
  width: max-content;
}

/* Input & Context Stack (Left Side) */
.input-context-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

/* Bubble Wrapper */
.bubble-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

/* Flow Bubble - iPad optimized sizes */
.flow-bubble {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;

  /* CSS variable for dynamic color */
  --bubble-color: #CCCCCC;

  /* Empty state: dark with border (Phase 1 style) */
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* INPUT/CONTEXT Bubbles - Rounded Rectangles (iPad size) */
.input-context-bubble {
  border-radius: 20px;
  width: 240px;
  height: 110px;
}

/* Small bubble for Safety */
.bubble-small {
  width: 80px;
  height: 80px;
}

.bubble-small .bubble-label {
  font-size: 0.65rem;
}

/* Waiting state: Gray placeholder */
.flow-bubble.status-waiting {
  background: rgba(80, 80, 80, 0.3);
  border: 2px solid rgba(120, 120, 120, 0.6);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.flow-bubble.status-waiting .bubble-content {
  color: rgba(150, 150, 150, 0.8);
}

/* Filled/Completed state: FILLED WITH COLOR */
.flow-bubble.status-filled,
.flow-bubble.status-completed {
  background: var(--bubble-color);
  border: none;
  box-shadow: 0 0 24px var(--bubble-color), 0 4px 20px rgba(0, 0, 0, 0.5);
}

.flow-bubble.status-filled .bubble-content,
.flow-bubble.status-completed .bubble-content {
  color: #0a0a0a;
}

.flow-bubble:hover {
  transform: scale(1.08);
}

.flow-bubble.status-filled:hover,
.flow-bubble.status-completed:hover {
  box-shadow: 0 0 30px var(--bubble-color), 0 6px 30px rgba(0, 0, 0, 0.6);
}

/* Processing state */
.flow-bubble.status-processing {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.bubble-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
  color: var(--bubble-color);
  overflow: hidden;
  position: relative;
}

.bubble-label {
  font-weight: 700;
  font-size: 0.75rem;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.bubble-preview {
  font-size: 0.6rem;
  line-height: 1.2;
  opacity: 0.9;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  max-height: 3rem;
}

/* Inline Editor */
.bubble-editor {
  width: 90%;
  height: 60%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: inherit;
  font-family: inherit;
  font-size: 0.7rem;
  padding: 0.5rem;
  resize: none;
  outline: none;
}

.bubble-editor:focus {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(0, 0, 0, 0.5);
}

.bubble-editor::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Processing Spinner */
.processing-spinner {
  position: absolute;
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--bubble-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Completed Check */
.completed-check {
  position: absolute;
  top: 8%;
  right: 8%;
  width: 2rem;
  height: 2rem;
  background: var(--bubble-color);
  color: rgba(20, 20, 20, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
  animation: check-pop 0.3s ease;
}

@keyframes check-pop {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

/* Flow Arrows - More visible */
.flow-arrow-down,
.flow-arrow-right {
  font-size: 2.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: bold;
  flex-shrink: 0;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
}

.flow-arrow-down {
  margin: 1rem 0;
}

.flow-arrow-right {
  margin: 0 1.5rem;
}

/* Flow Label Text - More visible */
.flow-label-text {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Medium Selection Stack */
.medium-selection-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.medium-bubble {
  width: 100px !important;
  height: 100px !important;
  cursor: pointer;
  transition: all 0.3s ease;
}

.medium-bubble:hover {
  transform: scale(1.1);
}

.medium-bubble .bubble-label {
  font-size: 0.65rem;
}

/* Continue Button & Start Button - Phase 1 style */
.continue-button,
.start-button {
  padding: 1.2rem 3rem;
  font-size: 1.1rem;
  font-weight: 700;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.4);
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  flex-shrink: 0;
}

.continue-button:hover,
.start-button:hover {
  transform: scale(1.05);
  background: #1976D2;
  box-shadow: 0 6px 30px rgba(33, 150, 243, 0.6);
}

/* Pipeline Stage Wrapper */
.pipeline-stage-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 2rem;
}

/* Output Image */
.output-image {
  width: 315px;
  height: 315px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 6px 30px rgba(76, 175, 80, 0.4);
  border: 3px solid #4CAF50;
  cursor: pointer;
  transition: all 0.3s ease;
}

.output-image:hover {
  transform: scale(1.05);
}

.output-label {
  font-weight: 700;
  font-size: 0.9rem;
  color: #4CAF50;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Fullscreen Image Modal */
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

/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
