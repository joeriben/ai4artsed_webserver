<template>
  <div class="youth-flow-view">
    <!-- Centered Constellation Layout -->
    <div class="flow-constellation">

      <!-- Stage 1: Input (Top) -->
      <div class="stage-card input-stage" :class="{ filled: inputText }">
        <div class="stage-emoji">🎨</div>
        <div class="stage-label">Deine Idee</div>
        <textarea
          v-model="inputText"
          placeholder="Worüber soll dein Bild sein?"
          class="stage-textarea"
          rows="3"
        ></textarea>
      </div>

      <!-- Stage 2: Options Row (Context + Medium) -->
      <div class="options-row">
        <!-- Context (Optional) -->
        <div class="stage-card context-stage" :class="{ filled: contextPrompt }">
          <div class="stage-emoji">💭</div>
          <div class="stage-label">Details</div>
          <textarea
            v-model="contextPrompt"
            placeholder="Noch mehr dazu? (optional)"
            class="stage-textarea"
            rows="2"
          ></textarea>
        </div>

        <!-- Medium Selection -->
        <div class="medium-selection">
          <div class="medium-label">Welcher Stil?</div>
          <div class="medium-bubbles">
            <div
              v-for="medium in availableMedia"
              :key="medium.id"
              class="medium-bubble"
              :class="{ selected: selectedOutputMedium === medium.id }"
              :style="{ '--bubble-color': medium.color }"
              @click="selectedOutputMedium = medium.id"
            >
              {{ medium.emoji }}
            </div>
          </div>
        </div>
      </div>

      <!-- Stage 3: Transform (Largest - appears after click) -->
      <transition name="slide-down">
        <div
          v-if="interceptionResult"
          class="stage-card transform-stage"
          :class="{ processing: isInterceptionProcessing }"
        >
          <div class="stage-emoji-large">✨</div>
          <div class="stage-label">Verwandlung</div>
          <div class="transform-content">
            <div v-if="isInterceptionProcessing" class="processing-spinner"></div>
            <div v-else class="transform-text">
              {{ interceptionResult }}
            </div>
          </div>
          <button
            v-if="!isInterceptionProcessing"
            class="edit-button"
            @click="editingTransform = !editingTransform"
          >
            Bearbeiten
          </button>
        </div>
      </transition>

      <!-- Action Button -->
      <button
        v-if="!interceptionResult && inputText && selectedOutputMedium"
        class="action-button"
        @click="submitContextAndRunInterception"
        :disabled="isInterceptionProcessing"
      >
        ✨ Los geht's!
      </button>

      <!-- Start Generation Button -->
      <button
        v-if="interceptionResult && !isInterceptionProcessing && !pipelineStarted"
        class="action-button generate"
        @click="startPipeline"
      >
        🎬 Bild machen!
      </button>

      <!-- Stage 4: Generation Progress -->
      <transition name="slide-down">
        <div v-if="pipelineStarted" class="generation-stages">
          <div v-if="pipelineStages[0]" class="gen-stage" :class="pipelineStages[0].status">
            <span class="gen-emoji">🛡️</span>
            <span class="gen-label">Sicherheit</span>
            <span v-if="pipelineStages[0].status === 'processing'" class="gen-spinner">⏳</span>
            <span v-if="pipelineStages[0].status === 'completed'" class="gen-check">✓</span>
          </div>
          <div v-if="pipelineStages[1]" class="gen-stage" :class="pipelineStages[1].status">
            <span class="gen-emoji">🎬</span>
            <span class="gen-label">Generation</span>
            <span v-if="pipelineStages[1].status === 'processing'" class="gen-spinner">⏳</span>
            <span v-if="pipelineStages[1].status === 'completed'" class="gen-check">✓</span>
          </div>
        </div>
      </transition>

      <!-- Stage 5: Output (Bottom) -->
      <transition name="slide-down">
        <div v-if="outputImage" class="stage-card output-stage">
          <div class="stage-emoji">🖼️</div>
          <div class="stage-label">Fertig!</div>
          <img
            :src="outputImage"
            alt="Dein Bild"
            class="output-image"
            @click="showImageFullscreen(outputImage)"
          />
        </div>
      </transition>

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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()

// Available media with emojis
const availableMedia = ref([
  { id: 'sd35_large', label: 'Klassisch', emoji: '🎨', color: '#4CAF50' },
  { id: 'gpt_image_1', label: 'Modern', emoji: '🌟', color: '#2196F3' },
  { id: 'acestep_simple', label: 'Abstrakt', emoji: '🎭', color: '#E91E63' }
])

// State
const inputText = ref('')
const contextPrompt = ref('')
const selectedOutputMedium = ref<string>('sd35_large')
const interceptionResult = ref('')
const isInterceptionProcessing = ref(false)
const pipelineStarted = ref(false)
const outputImage = ref<string | null>(null)
const fullscreenImage = ref<string | null>(null)
const editingTransform = ref(false)

// Pipeline stage type
type PipelineStatus = 'waiting' | 'processing' | 'completed'
interface PipelineStage {
  name: string
  status: PipelineStatus
}

// Pipeline stages
const pipelineStages = ref<PipelineStage[]>([
  { name: 'safety', status: 'waiting' },
  { name: 'generation', status: 'waiting' }
])

// Submit and run interception
async function submitContextAndRunInterception() {
  if (!inputText.value) {
    alert('Bitte zuerst eine Idee eingeben!')
    return
  }

  isInterceptionProcessing.value = true
  interceptionResult.value = ''

  try {
    const response = await axios.post('http://localhost:17802/api/schema/pipeline/transform', {
      schema: 'overdrive',
      input_text: inputText.value,
      context_prompt: contextPrompt.value || undefined,
      user_language: 'de'
    })

    if (response.data.success) {
      interceptionResult.value = response.data.interception_result?.result || response.data.result || ''
    } else {
      alert(`Fehler: ${response.data.error}`)
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
  pipelineStarted.value = true

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
      output_config: selectedOutputMedium.value
    })

    if (response.data.status === 'success') {
      if (pipelineStages.value[1]) {
        pipelineStages.value[1].status = 'completed'
      }

      if (response.data.outputs && response.data.outputs.length > 0) {
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
  }
}

function showImageFullscreen(imageUrl: string) {
  fullscreenImage.value = imageUrl
}

// Initialize from route params
onMounted(() => {
  const promptFromRoute = route.query.prompt as string
  if (promptFromRoute) {
    inputText.value = promptFromRoute
  }
})
</script>

<style scoped>
/* Main Container */
.youth-flow-view {
  position: fixed;
  inset: 0;
  background: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* Centered Constellation - Fits on Screen */
.flow-constellation {
  max-width: 900px;
  max-height: 90vh;
  width: 100%;
  padding: 2rem;

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;

  /* Scrollbar only if absolutely necessary */
  overflow-y: auto;
  overflow-x: hidden;
}

/* Stage Card Base */
.stage-card {
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.stage-card.filled {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
}

/* Input Stage */
.input-stage {
  width: 100%;
  max-width: 500px;
}

/* Options Row (Context + Medium) */
.options-row {
  display: flex;
  gap: 2rem;
  width: 100%;
  max-width: 700px;
  justify-content: center;
  flex-wrap: wrap;
}

.context-stage {
  flex: 1;
  min-width: 250px;
}

/* Medium Selection */
.medium-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.medium-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  font-weight: 500;
}

.medium-bubbles {
  display: flex;
  gap: 1rem;
}

.medium-bubble {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.medium-bubble:hover {
  transform: scale(1.1);
  filter: brightness(1.2);
}

.medium-bubble.selected {
  background: var(--bubble-color);
  box-shadow: 0 0 20px var(--bubble-color);
  transform: scale(1.05);
}

/* Transform Stage (LARGEST!) */
.transform-stage {
  width: 100%;
  max-width: 600px;
  min-height: 200px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
  box-shadow: 0 0 40px rgba(79, 172, 254, 0.6);
}

.transform-stage.processing {
  animation: pulse 2s ease-in-out infinite;
}

.stage-emoji {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.stage-emoji-large {
  font-size: 3.5rem;
  margin-bottom: 0.75rem;
}

.stage-label {
  font-size: 1.1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 1rem;
}

.transform-stage .stage-label {
  color: #0a0a0a;
}

/* Textarea */
.stage-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  padding: 0.75rem;
  resize: none;
  font-family: inherit;
}

.stage-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.stage-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Transform Content */
.transform-content {
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.transform-text {
  color: #0a0a0a;
  font-size: 1.1rem;
  line-height: 1.5;
  padding: 1rem;
}

/* Processing Spinner */
.processing-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(10, 10, 10, 0.2);
  border-top-color: #0a0a0a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

/* Buttons */
.action-button,
.edit-button {
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #0a0a0a;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(67, 233, 123, 0.4);
  transition: all 0.3s ease;
}

.action-button.generate {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 4px 20px rgba(240, 147, 251, 0.4);
}

.action-button:hover:not(:disabled),
.edit-button:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 30px rgba(67, 233, 123, 0.6);
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.edit-button {
  padding: 0.5rem 1.5rem;
  font-size: 0.9rem;
  background: rgba(10, 10, 10, 0.3);
  margin-top: 1rem;
}

/* Generation Stages */
.generation-stages {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: rgba(20, 20, 20, 0.5);
  border-radius: 16px;
}

.gen-stage {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(40, 40, 40, 0.8);
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.gen-stage.processing {
  border-color: rgba(240, 147, 251, 0.6);
  animation: pulse 2s ease-in-out infinite;
}

.gen-stage.completed {
  border-color: rgba(76, 175, 80, 0.6);
  background: rgba(76, 175, 80, 0.1);
}

.gen-emoji {
  font-size: 1.5rem;
}

.gen-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  font-weight: 500;
}

.gen-spinner {
  font-size: 1.2rem;
  animation: spin 1s linear infinite;
}

.gen-check {
  color: #4CAF50;
  font-size: 1.2rem;
  font-weight: bold;
}

/* Output Stage */
.output-stage {
  width: 100%;
  max-width: 500px;
}

.output-image {
  width: 100%;
  max-width: 400px;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 8px 40px rgba(67, 233, 123, 0.4);
  transition: all 0.3s ease;
}

.output-image:hover {
  transform: scale(1.02);
}

/* Transitions */
.slide-down-enter-active {
  animation: slideDown 0.5s ease-out;
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

/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Scrollbar Styling */
.flow-constellation::-webkit-scrollbar {
  width: 8px;
}

.flow-constellation::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.flow-constellation::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.flow-constellation::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
