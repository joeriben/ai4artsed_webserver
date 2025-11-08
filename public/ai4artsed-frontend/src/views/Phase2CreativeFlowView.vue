<template>
  <div class="app-container">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="handleBack">
          ← {{ $t('common.back') || 'Zurück' }}
        </button>
        <div class="config-info">
          <div class="config-name">
            {{ configName }}
          </div>
        </div>
      </div>
    </div>

    <!-- Canvas Container -->
    <div class="canvas-container">
      <!-- Particle Background -->
      <div class="particles" ref="particlesRef"></div>

      <!-- SVG Connections (Rubber Bands) -->
      <svg class="connections" ref="connectionsRef">
        <path
          class="connection-line connection-input-result"
          ref="line1Ref"
        />
        <path
          class="connection-line connection-meta-result"
          ref="line2Ref"
        />
      </svg>

      <!-- Card Container -->
      <div class="cards-wrapper">
        <div class="cards-container">
        <!-- Card 1: User Input (Idea) - WAS -->
        <div class="card card-input" ref="inputNodeRef">
          <div class="card-header">
            <div class="card-icon">💡</div>
            <div class="card-title">
              {{ $t('phase2.yourIdea') || 'Deine Idee: Um WAS soll es hier gehen?' }}
            </div>
          </div>
          <textarea
            class="card-input-area"
            v-model="userInput"
            @input="handleInputChange"
            :placeholder="$t('phase2.writeYourText') || 'Schreibe deinen Text...'"
            maxlength="500"
            ref="inputTextareaRef"
          ></textarea>
          <div class="card-footer">
            <span class="char-count">{{ userInput.length }} / 500</span>
          </div>
        </div>

        <!-- Card 2: Instructions/Rules (Clipboard) - WIE -->
        <div class="card card-rules" ref="metaNodeRef">
          <div class="card-header">
            <div class="card-icon">📋</div>
            <div class="card-title">
              {{ $t('phase2.rules') || 'Deine Regeln: WIE soll Deine Idee umgesetzt werden?' }}
            </div>
          </div>
          <div class="card-content scrollable">
            <div v-if="metaPromptPreview" class="rules-text">
              {{ metaPromptPreview }}
            </div>
            <div v-else class="loading-text">
              {{ $t('common.loading') || 'Lädt...' }}
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Central Stage 1+2 Processing Indicator -->
      <div class="llm-indicator" v-if="isTransforming">
        <div class="llm-icon rotating">⚙️</div>
        <div class="llm-text">
          <div v-if="transformationStage === 1">{{ $t('phase2.stage1') || 'Stage 1: Übersetzung + Sicherheit...' }}</div>
          <div v-else-if="transformationStage === 2">{{ $t('phase2.stage2') || 'Stage 2: Transformation...' }}</div>
          <div v-else>{{ $t('phase2.transforming') || 'Transformiere...' }}</div>
        </div>
      </div>

      <!-- Result Panel: Transformed Prompt (Full Width) -->
      <div
        class="result-panel"
        :class="{ 'is-empty': !transformedPrompt, 'is-filled': transformedPrompt }"
        ref="resultNodeRef"
      >
        <div class="result-header">
          <div class="result-icon">✨</div>
          <div class="result-title">
            {{ $t('phase2.transformedPrompt') || 'Transformierter Prompt' }}
          </div>
          <div v-if="transformedPrompt" class="char-count">{{ transformedPrompt.length }}</div>
        </div>
        <textarea
          v-if="transformedPrompt"
          class="result-textarea"
          :value="transformedPrompt"
          @input="handleTransformedPromptEdit"
          @blur="handleTransformedPromptBlur"
          ref="transformedTextareaRef"
        ></textarea>
        <div v-else class="result-empty">
          {{ $t('phase2.notYetTransformed') || 'Noch nicht transformiert...' }}
        </div>
      </div>

      <!-- Example Prompts Panel (Floating Left) - Optional Helper -->
      <div class="examples-panel" v-if="examplePrompts.length > 0">
        <div class="panel-title">{{ $t('phase2.examples') || 'Beispiele:' }}</div>
        <div
          v-for="(example, index) in examplePrompts"
          :key="index"
          class="example-item"
          @click="setExampleInput(example)"
        >
          {{ example }}
        </div>
      </div>

      <!-- Execute Panel (Floating Bottom Right) - Two Buttons -->
      <div class="execute-panel">
        <!-- Button 1: Transform (Stage 1+2) -->
        <button
          v-if="!transformedPrompt"
          class="execute-btn transform-btn"
          :disabled="!canTransform || isTransforming"
          @click="handleTransform"
        >
          <span v-if="!isTransforming">
            ✨ {{ $t('phase2.transform') || 'Transformieren' }}
          </span>
          <span v-else>
            ⚙️ {{ $t('phase2.transforming') || 'Transformiere...' }}
          </span>
        </button>

        <!-- Button 2: Continue to Phase 3 (Media Generation) -->
        <button
          v-if="transformedPrompt"
          class="execute-btn continue-btn"
          :disabled="isTransforming"
          @click="handleContinueToPhase3"
        >
          🎨 {{ $t('phase2.continueToMedia') || 'Weiter zum Bild generieren' }}
        </button>

        <!-- Re-transform Button (if already transformed) -->
        <button
          v-if="transformedPrompt"
          class="secondary-btn"
          :disabled="isTransforming"
          @click="handleReTransform"
        >
          🔄 {{ $t('phase2.reTransform') || 'Neu transformieren' }}
        </button>

        <div class="execute-info" v-if="!isTransforming">
          <span v-if="!transformedPrompt">{{ $t('phase2.stage12Time') || '~5-10 Sekunden' }}</span>
          <span v-else>{{ $t('phase2.readyForMedia') || 'Bereit für Bildgenerierung' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePipelineExecutionStore } from '@/stores/pipelineExecution'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { executePipeline, type PipelineExecuteRequest } from '@/services/api'

/**
 * Phase2CreativeFlowView - Organic Force-Based Creative Input Interface
 *
 * Implements the "3 Forces" pedagogical concept:
 * 1. User Input (blue) - Your creative idea
 * 2. Meta-Prompt (orange) - The transformation instruction
 * 3. Result (purple) - The synthesis of both forces
 *
 * Features:
 * - Canvas-based spatial layout with circular force nodes
 * - Animated SVG connections showing flow between forces
 * - Floating input panel with example prompts
 * - Floating execute button
 * - Particle background for ambient atmosphere
 * - Real-time preview sync
 *
 * Pedagogical Goal: Make AI transformation visible as interconnected forces,
 * not a black-box form submission.
 */

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

// Stores
const pipelineStore = usePipelineExecutionStore()
const userPreferences = useUserPreferencesStore()

// Refs
const particlesRef = ref<HTMLDivElement | null>(null)
const connectionsRef = ref<SVGElement | null>(null)
const line1Ref = ref<SVGPathElement | null>(null)
const line2Ref = ref<SVGPathElement | null>(null)
const inputNodeRef = ref<HTMLDivElement | null>(null)
const metaNodeRef = ref<HTMLDivElement | null>(null)
const resultNodeRef = ref<HTMLDivElement | null>(null)
const inputTextareaRef = ref<HTMLTextAreaElement | null>(null)
const transformedTextareaRef = ref<HTMLTextAreaElement | null>(null)

// State
const userInput = ref('')
const isTransforming = ref(false)
const transformationStage = ref<number>(0) // 0=idle, 1=stage1, 2=stage2
const error = ref<string | null>(null)

// Get transformed prompt from store
const transformedPrompt = computed(() => pipelineStore.transformedPrompt)

// Example prompts (could be loaded from config)
const examplePrompts = ref<string[]>([
  'Eine kleine Maus auf einem Fahrrad',
  'Der alte Mann und das Meer',
  'Elektrische Schafe',
])

// ============================================================================
// COMPUTED
// ============================================================================

const configName = computed(() => {
  if (!pipelineStore.selectedConfig) return ''
  const lang = userPreferences.language
  return pipelineStore.selectedConfig.name[lang] ||
         pipelineStore.selectedConfig.name.en ||
         pipelineStore.selectedConfig.id
})

const metaPromptPreview = computed(() => {
  if (!pipelineStore.metaPrompt) {
    console.log('[Phase2] No meta-prompt in store')
    return ''
  }
  // Show first 200 chars for preview
  const text = pipelineStore.metaPrompt
  const preview = text.length > 200 ? text.substring(0, 200) + '...' : text
  console.log('[Phase2] Meta-prompt preview:', preview.substring(0, 50) + '...')
  return preview
})

const canTransform = computed(() => {
  return userInput.value.trim().length > 0 && pipelineStore.selectedConfig
})

const canContinueToMedia = computed(() => {
  return transformedPrompt.value.trim().length > 0
})

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(async () => {
  const configId = route.params.configId as string

  console.log('[Phase2] Mounting with configId:', configId)

  if (!configId) {
    error.value = 'No config ID provided'
    return
  }

  // Load config and meta-prompt
  console.log('[Phase2] Loading config...')
  await pipelineStore.setConfig(configId)

  if (pipelineStore.error) {
    console.error('[Phase2] Config loading error:', pipelineStore.error)
    error.value = pipelineStore.error
    return
  }

  console.log('[Phase2] Config loaded:', pipelineStore.selectedConfig?.id)
  console.log('[Phase2] Loading meta-prompt for language:', userPreferences.language)

  await pipelineStore.loadMetaPromptForLanguage(userPreferences.language)

  if (pipelineStore.error) {
    console.error('[Phase2] Meta-prompt loading error:', pipelineStore.error)
  }

  console.log('[Phase2] Meta-prompt loaded:', pipelineStore.metaPrompt?.substring(0, 50))

  // Initialize user input from store if exists
  if (pipelineStore.userInput) {
    userInput.value = pipelineStore.userInput
  }

  // Initialize particles
  initParticles()

  // Update connections after DOM is ready
  await nextTick()
  updateConnections()

  // Update connections on window resize
  window.addEventListener('resize', updateConnections)
})

// ============================================================================
// METHODS
// ============================================================================

function initParticles() {
  if (!particlesRef.value) return

  // Generate 30 floating particles
  for (let i = 0; i < 30; i++) {
    const particle = document.createElement('div')
    particle.className = 'particle'
    particle.style.left = Math.random() * 100 + '%'
    particle.style.animationDelay = Math.random() * 20 + 's'
    particle.style.animationDuration = (15 + Math.random() * 10) + 's'
    particlesRef.value.appendChild(particle)
  }
}

function updateConnections() {
  if (!inputNodeRef.value || !metaNodeRef.value || !resultNodeRef.value) return
  if (!line1Ref.value || !line2Ref.value) return

  const inputRect = inputNodeRef.value.getBoundingClientRect()
  const metaRect = metaNodeRef.value.getBoundingClientRect()
  const resultRect = resultNodeRef.value.getBoundingClientRect()

  // Both lines converge to center top of result panel
  const xRCenter = resultRect.left + resultRect.width / 2
  const yRTop = resultRect.top

  // Connection 1: Input (bottom center) → Result panel (center top)
  const x1 = inputRect.left + inputRect.width / 2
  const y1 = inputRect.bottom
  const cx1 = (x1 + xRCenter) / 2
  const cy1 = (y1 + yRTop) / 2
  line1Ref.value.setAttribute('d', `M ${x1} ${y1} Q ${cx1} ${cy1} ${xRCenter} ${yRTop}`)

  // Connection 2: Meta (bottom center) → Result panel (center top)
  const x2 = metaRect.left + metaRect.width / 2
  const y2 = metaRect.bottom
  const cx2 = (x2 + xRCenter) / 2
  const cy2 = (y2 + yRTop) / 2
  line2Ref.value.setAttribute('d', `M ${x2} ${y2} Q ${cx2} ${cy2} ${xRCenter} ${yRTop}`)
}

/**
 * Stage 1+2: Transform user input via backend
 * - Stage 1: Translation + Safety check
 * - Stage 2: Prompt interception transformation
 */
async function handleTransform() {
  if (!canTransform.value || !pipelineStore.selectedConfig) return

  isTransforming.value = true
  transformationStage.value = 1
  error.value = null

  try {
    // Update store
    pipelineStore.updateUserInput(userInput.value)

    console.log('[Phase2] Starting transformation (Stage 1+2)...')

    // TODO: Call backend /api/schema/pipeline/transform endpoint
    // For now, simulate transformation
    transformationStage.value = 1
    await new Promise(resolve => setTimeout(resolve, 2000)) // Stage 1: Translation + Safety

    transformationStage.value = 2
    await new Promise(resolve => setTimeout(resolve, 3000)) // Stage 2: Interception

    // Mock transformed result
    const mockTransformed = `[TRANSFORMED via ${pipelineStore.selectedConfig.id}]\n\n${userInput.value}\n\n→ Petal-chaos contradicting meadow-umbrella existence with surrealist dreamscape qualities and absurdist spatial relationships.`

    // Store in Pinia for Phase 3 handoff
    pipelineStore.updateTransformedPrompt(mockTransformed)

    console.log('[Phase2] Transformation complete:', mockTransformed)

  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Transformation failed'
    console.error('[Phase2] Transformation error:', err)
  } finally {
    isTransforming.value = false
    transformationStage.value = 0
  }
}

/**
 * Re-transform: Clear transformed prompt and allow re-execution
 */
function handleReTransform() {
  pipelineStore.clearTransformedPrompt()
  console.log('[Phase2] Cleared transformed prompt for re-transformation')
}

/**
 * Continue to Phase 3: Media generation with transformed prompt
 */
function handleContinueToPhase3() {
  if (!canContinueToMedia.value) return

  console.log('[Phase2] Continuing to Phase 3 with transformed prompt:', transformedPrompt.value)

  // TODO: Store transformed prompt in Pinia
  // TODO: Navigate to Phase 3 with run context
  // router.push({ name: 'phase3-entity-flow', params: { ... } })

  alert(`Phase 3 not yet implemented.\n\nTransformed prompt:\n${transformedPrompt.value}`)
}

function handleInputChange() {
  // Update store
  pipelineStore.updateUserInput(userInput.value)

  // Clear transformed prompt when input changes
  if (transformedPrompt.value) {
    pipelineStore.clearTransformedPrompt()
  }
}

function handleTransformedPromptEdit(event: Event) {
  const target = event.target as HTMLTextAreaElement
  pipelineStore.updateTransformedPrompt(target.value)
}

function handleTransformedPromptBlur() {
  console.log('[Phase2] Transformed prompt editing complete')
}

function setExampleInput(example: string) {
  userInput.value = example
  pipelineStore.updateUserInput(example)

  // Clear transformed prompt when changing input
  pipelineStore.clearTransformedPrompt()
}

function handleBack() {
  router.push({ name: 'property-selection' })
}

// ============================================================================
// WATCHERS
// ============================================================================

// Watch language changes and reload meta-prompt
watch(
  () => userPreferences.language,
  async (newLang) => {
    await pipelineStore.loadMetaPromptForLanguage(newLang)
  }
)
</script>

<style scoped>
* {
  box-sizing: border-box;
}

/* App Container */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
  background: #0a0a0a;
  color: #e0e0e0;
  overflow: hidden;
}

/* Top Bar */
.top-bar {
  background: rgba(42, 42, 42, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #3a3a3a;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  z-index: 100;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: transparent;
  border: 1px solid #4a90e2;
  color: #4a90e2;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(74, 144, 226, 0.1);
}

.config-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.config-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

/* Canvas Container */
.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* Particle Background */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 2px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 20s infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100vh) translateX(50px);
    opacity: 0;
  }
}

/* Cards Wrapper (contains cards) */
.cards-wrapper {
  position: relative;
  margin: 40px auto 0;
  max-width: 1200px;
  padding: 0 20px;
  z-index: 10;
}

/* SVG Connections - Fill viewport for coordinate alignment */
svg.connections {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 5;
}

.connection-line {
  stroke-width: 3;
  fill: none;
  stroke-dasharray: 10 5;
  animation: flow 3s linear infinite;
  filter: drop-shadow(0 0 8px currentColor);
}

.connection-input-result {
  stroke: rgba(74, 144, 226, 0.6);
}

.connection-meta-result {
  stroke: rgba(243, 156, 18, 0.6);
}

@keyframes flow {
  to {
    stroke-dashoffset: -15;
  }
}

/* Cards Container (Side by Side) */
.cards-container {
  display: flex;
  gap: 24px;
  justify-content: center;
  align-items: flex-start;
  position: relative;
  z-index: 12;
}

/* Card Base Style */
.card {
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
  flex: 1;
  max-width: 500px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.card-icon {
  font-size: 32px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.card-subtitle {
  font-size: 11px;
  font-weight: 500;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

/* Input Card (💡 Idea) - Blue */
.card-input {
  border-color: rgba(74, 144, 226, 0.5);
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.05) 0%, rgba(30, 30, 30, 0.95) 50%);
}

.card-input .card-title {
  color: #4a90e2;
}

.card-input .card-header {
  border-bottom-color: rgba(74, 144, 226, 0.3);
}

.card-input-area {
  flex: 1;
  width: 100%;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(74, 144, 226, 0.3);
  border-radius: 8px;
  padding: 12px;
  color: #e0e0e0;
  font-size: 14px;
  line-height: 1.6;
  font-family: inherit;
  resize: none;
  transition: all 0.2s ease;
}

.card-input-area:focus {
  outline: none;
  background: rgba(0, 0, 0, 0.6);
  border-color: rgba(74, 144, 226, 0.7);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.card-input-area::placeholder {
  color: rgba(255, 255, 255, 0.3);
  font-style: italic;
}

.card-footer {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.char-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* Rules Card (📋 Clipboard) - Orange */
.card-rules {
  border-color: rgba(243, 156, 18, 0.5);
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.05) 0%, rgba(30, 30, 30, 0.95) 50%);
}

.card-rules .card-title {
  color: #f39c12;
}

.card-rules .card-header {
  border-bottom-color: rgba(243, 156, 18, 0.3);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-content.scrollable {
  overflow-y: auto;
  max-height: 350px;
}

.rules-text {
  font-size: 13px;
  line-height: 1.7;
  color: #ccc;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(243, 156, 18, 0.2);
  border-radius: 8px;
  white-space: pre-wrap;
}

.loading-text {
  font-size: 13px;
  font-style: italic;
  color: #888;
  padding: 12px;
}

/* LLM Processing Indicator (Central) */
.llm-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  z-index: 20;
  animation: pulse 2s ease-in-out infinite;
}

.llm-icon {
  font-size: 64px;
  filter: drop-shadow(0 4px 12px rgba(255, 255, 255, 0.3));
}

.llm-icon.rotating {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.llm-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

/* Result Panel (Full Width, Below Cards) - Purple */
.result-panel {
  margin: 80px auto 100px;
  max-width: 1200px;
  padding: 0 20px;
  position: relative;
  z-index: 10;
  transition: all 0.5s ease;
}

.result-panel.is-empty {
  opacity: 0.5;
}

.result-panel.is-filled {
  opacity: 1;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 16px 20px;
  background: rgba(155, 89, 182, 0.1);
  border: 2px solid rgba(155, 89, 182, 0.3);
  border-radius: 12px 12px 0 0;
  backdrop-filter: blur(10px);
}

.result-panel.is-filled .result-header {
  border-color: rgba(155, 89, 182, 0.5);
  background: rgba(155, 89, 182, 0.15);
}

.result-panel.is-empty .result-header {
  border-style: dashed;
  border-radius: 12px;
  margin-bottom: 0;
}

.result-icon {
  font-size: 24px;
  filter: drop-shadow(0 2px 8px rgba(155, 89, 182, 0.4));
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: #9b59b6;
  flex: 1;
}

.result-textarea {
  width: 100%;
  min-height: 200px;
  max-height: 400px;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(155, 89, 182, 0.5);
  border-top: none;
  border-radius: 0 0 12px 12px;
  padding: 20px;
  color: #e0e0e0;
  font-size: 15px;
  line-height: 1.7;
  font-family: inherit;
  resize: vertical;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.result-textarea:focus {
  outline: none;
  background: rgba(30, 30, 30, 0.95);
  border-color: rgba(155, 89, 182, 0.7);
  box-shadow: 0 4px 16px rgba(155, 89, 182, 0.2);
}

.result-empty {
  padding: 40px;
  text-align: center;
  font-size: 14px;
  font-style: italic;
  color: #666;
}

/* Examples Panel (Floating Left) - Optional Helper */
.examples-panel {
  position: absolute;
  top: 50%;
  left: 3%;
  transform: translateY(-50%);
  width: 200px;
  background: rgba(42, 42, 42, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid #3a3a3a;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 50;
}

.panel-title {
  font-size: 12px;
  color: #888;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.example-item {
  background: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #aaa;
  cursor: pointer;
  transition: all 0.2s;
}

.example-item:hover {
  border-color: #4a90e2;
  background: #2a3a4a;
}

/* Execute Panel (Floating Bottom Right) */
.execute-panel {
  position: absolute;
  bottom: 5%;
  right: 5%;
  background: rgba(42, 42, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid #3a3a3a;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 50;
}

.execute-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 16px 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  white-space: nowrap;
}

.execute-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.transform-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.continue-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.secondary-btn {
  background: transparent;
  color: #888;
  border: 1px solid #555;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
}

.secondary-btn:hover:not(:disabled) {
  border-color: #888;
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.secondary-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.execute-info {
  text-align: center;
  font-size: 12px;
  color: #888;
  margin-top: 12px;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
  background: #3a3a3a;
  border-radius: 3px;
}

/* Responsive adjustments */
@media (max-width: 1400px) {
  .cards-wrapper {
    max-width: 1000px;
  }

  .cards-container {
    gap: 20px;
  }

  .card {
    max-width: 450px;
  }

  .result-panel {
    max-width: 1000px;
  }

  .examples-panel {
    width: 180px;
    left: 2%;
  }
}

@media (max-width: 1024px) {
  .cards-wrapper {
    max-width: 600px;
    padding: 0 16px;
  }

  .cards-container {
    flex-direction: column;
    align-items: stretch;
  }

  .card {
    max-width: 100%;
    min-height: 300px;
  }

  .result-panel {
    max-width: 600px;
    padding: 0 16px;
  }

  .canvas-container {
    overflow-y: auto;
    padding: 20px 0;
  }

  .examples-panel {
    position: relative;
    top: auto;
    left: auto;
    transform: none;
    width: 100%;
    max-width: 600px;
    margin: 20px auto;
  }

  .execute-panel {
    position: relative;
    bottom: auto;
    right: auto;
    width: 100%;
    max-width: 600px;
    margin: 20px auto;
  }

  svg.connections {
    display: none;
  }

  .particles {
    display: none;
  }
}
</style>
