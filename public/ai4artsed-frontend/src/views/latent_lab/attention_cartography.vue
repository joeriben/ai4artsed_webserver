<template>
  <div class="attention-cartography">
    <!-- Header (always visible) -->
    <div class="page-header">
      <h2 class="page-title">{{ t('latentLab.attention.headerTitle') }}</h2>
      <p class="page-subtitle">{{ t('latentLab.attention.headerSubtitle') }}</p>
      <details class="explanation-details">
        <summary>{{ t('latentLab.attention.explanationToggle') }}</summary>
        <div class="explanation-body">
          <div class="explanation-section">
            <h4>{{ t('latentLab.attention.explainWhatTitle') }}</h4>
            <p>{{ t('latentLab.attention.explainWhatText') }}</p>
          </div>
          <div class="explanation-section">
            <h4>{{ t('latentLab.attention.explainHowTitle') }}</h4>
            <p>{{ t('latentLab.attention.explainHowText') }}</p>
          </div>
          <div class="explanation-section">
            <h4>{{ t('latentLab.attention.explainReadTitle') }}</h4>
            <p>{{ t('latentLab.attention.explainReadText') }}</p>
          </div>
          <div class="explanation-section explanation-tech">
            <h4>{{ t('latentLab.attention.techTitle') }}</h4>
            <p>{{ t('latentLab.attention.techText') }}</p>
          </div>
        </div>
      </details>
    </div>

    <!-- Input Section -->
    <div class="input-section">
      <MediaInputBox
        icon="lightbulb"
        :label="t('latentLab.attention.promptLabel')"
        :placeholder="t('latentLab.attention.promptPlaceholder')"
        v-model:value="promptText"
        input-type="text"
        :rows="2"
        resize-type="auto"
        :disabled="isGenerating"
        @copy="copyInputText"
        @paste="pasteInputText"
        @clear="clearInputText"
      />
      <button
        class="generate-btn"
        :disabled="isGenerating || !promptText.trim()"
        @click="generate"
      >
        <span v-if="isGenerating" class="spinner"></span>
        <span v-else>{{ t('latentLab.attention.generate') }}</span>
      </button>

      <!-- Advanced Settings (collapsible) -->
      <details class="advanced-settings">
        <summary>{{ t('latentLab.attention.advancedLabel') }}</summary>
        <div class="settings-grid">
          <label>
            {{ t('latentLab.attention.negativeLabel') }}
            <input v-model="negativePrompt" type="text" class="setting-input" />
          </label>
          <label>
            {{ t('latentLab.attention.stepsLabel') }}
            <input v-model.number="steps" type="number" min="10" max="50" class="setting-input setting-small" />
          </label>
          <label>
            {{ t('latentLab.attention.cfgLabel') }}
            <input v-model.number="cfgScale" type="number" min="1" max="20" step="0.5" class="setting-input setting-small" />
          </label>
          <label>
            {{ t('latentLab.attention.seedLabel') }}
            <input v-model.number="seed" type="number" min="-1" class="setting-input setting-small" />
          </label>
        </div>
      </details>
    </div>

    <!-- Main Visualization -->
    <div class="visualization-section" :class="{ 'is-disabled': !imageData }">
      <!-- Image with heatmap overlay -->
      <div class="image-container" ref="imageContainerRef">
        <img
          v-if="imageData"
          :src="`data:image/png;base64,${imageData}`"
          class="generated-image"
          :class="{ grayscale: baseImageMode === 'bw', hidden: baseImageMode === 'off' }"
          ref="imageRef"
          @load="onImageLoad"
        />
        <div v-else class="placeholder-image"></div>
        <canvas
          ref="heatmapCanvas"
          class="heatmap-overlay"
          :style="{ opacity: heatmapOpacity }"
        ></canvas>
      </div>

      <!-- Token Chips (grouped by word) -->
      <div class="token-section">
        <div class="token-label">{{ t('latentLab.attention.tokensLabel') }}</div>
        <div class="token-hint">{{ t('latentLab.attention.tokensHint') }}</div>
        <div class="token-chips">
          <div
            v-for="(group, gIdx) in wordGroups"
            :key="gIdx"
            class="word-group"
            :class="{ selected: isWordSelected(group), [`color-${selectedWordColorIndex(group) % 8}`]: isWordSelected(group) }"
            @click="toggleWord(group)"
          >
            <span
              v-if="isWordSelected(group)"
              class="color-dot"
              :style="{ background: tokenColorCSS(selectedWordColorIndex(group)) }"
            ></span>
            <span class="word-text">{{ wordLabel(group) }}</span>
            <span v-if="group.length > 1" class="subtoken-hint">({{ group.length }})</span>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls-section">
        <!-- Timestep Slider -->
        <div class="control-group">
          <div class="control-row">
            <label class="control-label">{{ t('latentLab.attention.timestepLabel') }}</label>
            <div class="slider-container">
              <input
                type="range"
                v-model.number="selectedStep"
                :min="0"
                :max="captureSteps.length - 1"
                :step="1"
                class="control-slider"
              />
              <span class="slider-value">{{ t('latentLab.attention.step') }} {{ captureSteps[selectedStep] ?? 0 }} / {{ totalSteps }}</span>
            </div>
          </div>
          <div class="control-hint">{{ t('latentLab.attention.timestepHint') }}</div>
        </div>

        <!-- Layer Toggle -->
        <div class="control-group">
          <div class="control-row">
            <label class="control-label">{{ t('latentLab.attention.layerLabel') }}</label>
            <div class="layer-toggles">
              <button
                v-for="(layer, idx) in captureLayers"
                :key="layer"
                class="layer-btn"
                :class="{ active: selectedLayerIdx === idx }"
                @click="selectedLayerIdx = idx"
              >
                {{ layerLabels[idx] }}
              </button>
            </div>
          </div>
          <div class="control-hint">{{ t('latentLab.attention.layerHint') }}</div>
        </div>

        <!-- Opacity Slider -->
        <div class="control-group">
          <div class="control-row">
            <label class="control-label">{{ t('latentLab.attention.opacityLabel') }}</label>
            <div class="slider-container">
              <input
                type="range"
                v-model.number="heatmapOpacity"
                min="0"
                max="1"
                step="0.05"
                class="control-slider"
              />
              <span class="slider-value">{{ Math.round(heatmapOpacity * 100) }}%</span>
            </div>
          </div>
          <div class="control-hint">{{ t('latentLab.attention.opacityHint') }}</div>
        </div>

        <!-- Base Image Mode -->
        <div class="control-group">
          <div class="control-row">
            <label class="control-label">{{ t('latentLab.attention.baseImageLabel') }}</label>
            <div class="layer-toggles">
              <button
                v-for="(mode, idx) in baseImageModes"
                :key="mode"
                class="layer-btn"
                :class="{ active: baseImageMode === mode }"
                @click="baseImageMode = mode"
              >
                {{ baseImageModeLabels[idx] }}
              </button>
            </div>
          </div>
          <div class="control-hint">{{ t('latentLab.attention.baseImageHint') }}</div>
        </div>
      </div>

      <!-- Seed + Download -->
      <div class="seed-row">
        <div class="seed-display">Seed: {{ actualSeed }}</div>
        <button class="download-btn" @click="downloadImage">
          {{ t('latentLab.attention.download') }}
        </button>
      </div>
    </div>

    <!-- Empty State Hint (shown over disabled visualization) -->
    <div class="empty-state-overlay" v-if="!imageData && !isGenerating">
      <p>{{ t('latentLab.attention.emptyHint') }}</p>
    </div>

    <!-- Generation Progress -->
    <div class="progress-state" v-if="isGenerating">
      <div class="progress-spinner"></div>
      <p>{{ t('latentLab.attention.generating') }}</p>
    </div>

    <!-- Error Display -->
    <div class="error-display" v-if="errorMessage">
      <p>{{ errorMessage }}</p>
      <button @click="errorMessage = ''" class="dismiss-btn">&times;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import axios from 'axios'
import MediaInputBox from '@/components/MediaInputBox.vue'
import { useAppClipboard } from '@/composables/useAppClipboard'
import { usePageContextStore } from '@/stores/pageContext'
import type { PageContext, FocusHint } from '@/composables/usePageContext'

const { t } = useI18n()
const route = useRoute()
const pageContextStore = usePageContextStore()
const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()

// State
const promptText = ref('')
const negativePrompt = ref('')
const steps = ref(25)
const cfgScale = ref(4.5)
const seed = ref(-1)
const isGenerating = ref(false)
const errorMessage = ref('')

// Result data
const imageData = ref('')
const tokens = ref<string[]>([])
const wordGroups = ref<number[][]>([])  // [[0,1], [2], [3,4]] — subtoken indices per word
const attentionMaps = ref<Record<string, Record<string, number[][]>>>({})
const spatialResolution = ref<[number, number]>([64, 64])
const captureLayers = ref<number[]>([3, 9, 17])
const captureSteps = ref<number[]>([])
const totalSteps = ref(25)
const actualSeed = ref(0)

// Interaction state — selectedWords stores indices into wordGroups (not token indices)
const selectedWords = ref<number[]>([])
const selectedStep = ref(0)
const selectedLayerIdx = ref(1) // Default: mid layer
const heatmapOpacity = ref(0.6)
const baseImageModes = ['color', 'bw', 'off'] as const
type BaseImageMode = typeof baseImageModes[number]
const baseImageMode = ref<BaseImageMode>('color')
const baseImageModeLabels = computed(() => [
  t('latentLab.attention.baseColor'),
  t('latentLab.attention.baseBW'),
  t('latentLab.attention.baseOff'),
])

// Refs
const imageRef = ref<HTMLImageElement | null>(null)
const heatmapCanvas = ref<HTMLCanvasElement | null>(null)
const imageContainerRef = ref<HTMLDivElement | null>(null)

const layerLabels = computed(() => [
  t('latentLab.attention.layerEarly'),
  t('latentLab.attention.layerMid'),
  t('latentLab.attention.layerLate'),
])

// Color palette for multi-token heatmaps (8 distinct colors)
const tokenColors = [
  [255, 0, 0],     // red
  [0, 150, 255],   // blue
  [0, 255, 100],   // green
  [255, 200, 0],   // yellow
  [255, 0, 255],   // magenta
  [255, 128, 0],   // orange
  [0, 255, 255],   // cyan
  [180, 0, 255],   // purple
]

// Word-level helpers
function wordLabel(group: number[]): string {
  return group.map(i => tokens.value[i] ?? '').join('')
}

function isWordSelected(group: number[]): boolean {
  const gIdx = wordGroups.value.indexOf(group)
  return selectedWords.value.includes(gIdx)
}

function selectedWordColorIndex(group: number[]): number {
  const gIdx = wordGroups.value.indexOf(group)
  return selectedWords.value.indexOf(gIdx)
}

function tokenColorCSS(selIdx: number): string {
  const c = tokenColors[selIdx % tokenColors.length]
  return c ? `rgb(${c[0]}, ${c[1]}, ${c[2]})` : 'white'
}

function toggleWord(group: number[]) {
  const gIdx = wordGroups.value.indexOf(group)
  const pos = selectedWords.value.indexOf(gIdx)
  if (pos >= 0) {
    selectedWords.value.splice(pos, 1)
  } else {
    selectedWords.value.push(gIdx)
  }
  nextTick(() => renderHeatmap())
}

function copyInputText() { copyToClipboard(promptText.value) }
function pasteInputText() { promptText.value = pasteFromClipboard() }
function clearInputText() { promptText.value = '' }

function downloadImage() {
  if (!imageData.value) return
  const link = document.createElement('a')
  link.href = `data:image/png;base64,${imageData.value}`
  link.download = `attention_cartography_${actualSeed.value}.png`
  link.click()
}

async function generate() {
  if (!promptText.value.trim() || isGenerating.value) return

  isGenerating.value = true
  errorMessage.value = ''
  imageData.value = ''
  tokens.value = []
  wordGroups.value = []
  attentionMaps.value = {}
  selectedWords.value = []

  try {
    const response = await axios.post('/api/schema/pipeline/legacy', {
      prompt: promptText.value,
      output_config: 'attention_cartography_diffusers',
      seed: seed.value,
      negative_prompt: negativePrompt.value,
      steps: steps.value,
      cfg: cfgScale.value,
    })

    if (response.data.status === 'success') {
      // Attention data (including image_base64) is included directly in the response
      const attData = response.data.attention_data
      if (attData) {
        // Use image_base64 directly — no separate media fetch needed
        if (attData.image_base64) {
          imageData.value = attData.image_base64
        }
        tokens.value = attData.tokens || []
        wordGroups.value = attData.word_groups || []
        attentionMaps.value = attData.attention_maps || {}
        spatialResolution.value = attData.spatial_resolution || [64, 64]
        captureLayers.value = attData.capture_layers || [3, 9, 17]
        captureSteps.value = attData.capture_steps || []
        totalSteps.value = steps.value
        actualSeed.value = attData.seed || response.data.media_output?.seed || 0

        // Diagnostic logging
        const mapKeys = Object.keys(attData.attention_maps || {})
        const firstStep = mapKeys[0]
        const firstLayerKeys = firstStep ? Object.keys(attData.attention_maps[firstStep]) : []
        const sampleMap = firstStep && firstLayerKeys[0] ? attData.attention_maps[firstStep][firstLayerKeys[0]] : null
        console.log('[AC] Attention data received:', {
          tokens: attData.tokens,
          captureSteps: attData.capture_steps,
          captureLayers: attData.capture_layers,
          mapStepKeys: mapKeys,
          mapLayerKeys: firstLayerKeys,
          sampleMapRows: sampleMap?.length,
          sampleMapCols: sampleMap?.[0]?.length,
          spatialRes: attData.spatial_resolution,
          imageBase64Length: attData.image_base64?.length,
        })

        // Auto-select first word
        if (wordGroups.value.length > 0) {
          selectedWords.value = [0]
        }
      } else {
        errorMessage.value = 'No attention data in response'
      }
    } else {
      errorMessage.value = response.data.error || response.data.message || 'Generation failed'
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error || err.message || 'Network error'
  } finally {
    isGenerating.value = false
  }
}

function onImageLoad() {
  renderHeatmap()
}

// Watch for changes that should trigger heatmap re-render
// deep: true needed because selectedWords is mutated in-place (splice/push)
watch([selectedWords, selectedStep, selectedLayerIdx, heatmapOpacity], () => {
  nextTick(() => renderHeatmap())
}, { deep: true })

function renderHeatmap() {
  const canvas = heatmapCanvas.value
  const img = imageRef.value
  if (!canvas || !img || !imageData.value) return
  if (selectedWords.value.length === 0) {
    const ctx = canvas.getContext('2d')
    if (ctx) {
      canvas.width = img.naturalWidth
      canvas.height = img.naturalHeight
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
    return
  }

  const [spatialH, spatialW] = spatialResolution.value
  const stepKey = `step_${captureSteps.value[selectedStep.value] ?? 0}`
  const layerKey = `layer_${captureLayers.value[selectedLayerIdx.value] ?? 9}`
  const stepData = attentionMaps.value[stepKey]
  if (!stepData) return
  const layerData = stepData[layerKey]
  if (!layerData) return

  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // For each selected word, sum attention across all its subtokens
  for (let wIdx = 0; wIdx < selectedWords.value.length; wIdx++) {
    const wordIdx = selectedWords.value[wIdx]
    if (wordIdx === undefined) continue
    const group = wordGroups.value[wordIdx]
    if (!group) continue
    const colorArr = tokenColors[wIdx % tokenColors.length]
    if (!colorArr) continue
    const color: [number, number, number] = [colorArr[0] ?? 0, colorArr[1] ?? 0, colorArr[2] ?? 0]

    // Sum attention across all subtokens of this word
    const numPixels = spatialH * spatialW
    const attnValues = new Float64Array(numPixels)
    for (const tokenIdx of group) {
      for (let i = 0; i < numPixels; i++) {
        const row = layerData[i]
        if (row && row[tokenIdx] !== undefined) {
          attnValues[i] = (attnValues[i] ?? 0) + row[tokenIdx]
        }
      }
    }

    // Normalize to [0, 1]
    let maxVal = 1e-8
    for (let i = 0; i < numPixels; i++) {
      const v = attnValues[i] ?? 0
      if (v > maxVal) maxVal = v
    }

    // Render to temporary canvas at patch resolution, then upscale
    const tmpCanvas = document.createElement('canvas')
    tmpCanvas.width = spatialW
    tmpCanvas.height = spatialH
    const tmpCtx = tmpCanvas.getContext('2d')
    if (!tmpCtx) continue

    const imgDataTmp = tmpCtx.createImageData(spatialW, spatialH)
    for (let i = 0; i < numPixels; i++) {
      const intensity = (attnValues[i] ?? 0) / maxVal
      const pixIdx = i * 4
      imgDataTmp.data[pixIdx] = color[0]
      imgDataTmp.data[pixIdx + 1] = color[1]
      imgDataTmp.data[pixIdx + 2] = color[2]
      imgDataTmp.data[pixIdx + 3] = Math.floor(intensity * 200)
    }
    tmpCtx.putImageData(imgDataTmp, 0, 0)

    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'
    ctx.globalCompositeOperation = wIdx === 0 ? 'source-over' : 'lighter'
    ctx.drawImage(tmpCanvas, 0, 0, canvas.width, canvas.height)
  }
}

// ============================================================================
// Träshy Page Context
// ============================================================================
const trashyFocusHint = computed<FocusHint>(() => {
  if (isGenerating.value || imageData.value) {
    return { x: 95, y: 85, anchor: 'bottom-right' }
  }
  return { x: 8, y: 95, anchor: 'bottom-left' }
})

const pageContext = computed<PageContext>(() => ({
  activeViewType: 'attention_cartography',
  pageContent: {
    inputText: promptText.value
  },
  focusHint: trashyFocusHint.value
}))

watch(pageContext, (ctx) => {
  pageContextStore.setPageContext(ctx)
}, { immediate: true, deep: true })

onUnmounted(() => {
  pageContextStore.clearContext()
})
</script>

<style scoped>
.attention-cartography {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
}

/* Page Header */
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  color: #667eea;
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 0.75rem;
}

.explanation-details {
  background: rgba(102, 126, 234, 0.06);
  border: 1px solid rgba(102, 126, 234, 0.15);
  border-radius: 10px;
  overflow: hidden;
}

.explanation-details summary {
  padding: 0.65rem 1rem;
  color: rgba(102, 126, 234, 0.8);
  font-size: 0.85rem;
  cursor: pointer;
  user-select: none;
}

.explanation-details summary:hover {
  color: #667eea;
}

.explanation-body {
  padding: 0 1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.explanation-section h4 {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.85rem;
  margin: 0 0 0.25rem;
}

.explanation-section p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.82rem;
  line-height: 1.6;
  margin: 0;
}

.explanation-tech {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
}

.explanation-tech p {
  font-size: 0.78rem;
}

/* Input Section */
.input-section {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.generate-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-height: 48px;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Advanced Settings */
.advanced-settings {
  margin-top: 0.75rem;
}

.advanced-settings summary {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.25rem 0;
}

.settings-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.settings-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
}

.setting-input {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
  color: white;
  font-size: 0.85rem;
}

.setting-small {
  width: 80px;
}

/* Visualization */
.visualization-section {
  margin-top: 1rem;
}

.image-container {
  position: relative;
  display: inline-block;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.generated-image {
  display: block;
  width: 100%;
  height: auto;
  transition: filter 0.3s ease;
}

.generated-image.grayscale {
  filter: grayscale(1);
}

.generated-image.hidden {
  opacity: 0;
}

.heatmap-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Token Chips */
.token-section {
  margin-top: 1rem;
}

.token-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.token-hint {
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.token-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.color-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
  flex-shrink: 0;
}

.word-group {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.word-group:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.word-group.selected {
  border-color: currentColor;
  font-weight: 600;
}

.word-text {
  white-space: nowrap;
}

.subtoken-hint {
  font-size: 0.6rem;
  opacity: 0.5;
  margin-left: 3px;
}

.word-group.color-0.selected { color: #ff4444; background: rgba(255, 68, 68, 0.15); }
.word-group.color-1.selected { color: #44aaff; background: rgba(68, 170, 255, 0.15); }
.word-group.color-2.selected { color: #44ff88; background: rgba(68, 255, 136, 0.15); }
.word-group.color-3.selected { color: #ffcc00; background: rgba(255, 204, 0, 0.15); }
.word-group.color-4.selected { color: #ff44ff; background: rgba(255, 68, 255, 0.15); }
.word-group.color-5.selected { color: #ff8800; background: rgba(255, 136, 0, 0.15); }
.word-group.color-6.selected { color: #00ffff; background: rgba(0, 255, 255, 0.15); }
.word-group.color-7.selected { color: #b844ff; background: rgba(184, 68, 255, 0.15); }

/* Controls */
.controls-section {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.control-hint {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  line-height: 1.4;
  padding-left: calc(80px + 1rem);
}

.control-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.control-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  min-width: 80px;
  flex-shrink: 0;
}

.slider-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.control-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #667eea;
  border-radius: 50%;
  cursor: pointer;
}

.slider-value {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.75rem;
  min-width: 70px;
  text-align: right;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.layer-toggles {
  display: flex;
  gap: 0.35rem;
}

.layer-btn {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.layer-btn.active {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: #667eea;
}

.seed-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
}

.seed-display {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.download-btn {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Empty / Progress / Error States */
.visualization-section.is-disabled {
  opacity: 0.35;
  pointer-events: none;
}

.placeholder-image {
  width: 100%;
  aspect-ratio: 1/1;
  max-width: 512px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.empty-state-overlay {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.95rem;
  margin-top: -2rem;
}

.progress-state {
  text-align: center;
  padding: 3rem 2rem;
  color: rgba(102, 126, 234, 0.7);
}

.progress-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

.error-display {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.3);
  border-radius: 8px;
  color: #ef5350;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dismiss-btn {
  background: none;
  border: none;
  color: rgba(244, 67, 54, 0.6);
  font-size: 1.2rem;
  cursor: pointer;
}
</style>
