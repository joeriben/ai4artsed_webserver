<template>
  <div class="attention-cartography">
    <!-- Info Panel -->
    <div class="info-panel" v-if="showInfo">
      <div class="info-content">
        <h3>{{ t('latentLab.attention.infoTitle') }}</h3>
        <p>{{ t('latentLab.attention.infoDescription') }}</p>
        <div class="info-tech">
          <strong>{{ t('latentLab.attention.techTitle') }}</strong>
          <p>{{ t('latentLab.attention.techText') }}</p>
        </div>
        <button class="info-close" @click="showInfo = false">&times;</button>
      </div>
    </div>

    <!-- Input Section -->
    <div class="input-section">
      <div class="prompt-row">
        <textarea
          v-model="promptText"
          class="prompt-input"
          :placeholder="t('latentLab.attention.promptPlaceholder')"
          rows="2"
          :disabled="isGenerating"
          @keydown.enter.ctrl="generate"
        ></textarea>
        <button
          class="generate-btn"
          :disabled="isGenerating || !promptText.trim()"
          @click="generate"
        >
          <span v-if="isGenerating" class="spinner"></span>
          <span v-else>{{ t('latentLab.attention.generate') }}</span>
        </button>
        <button class="info-btn" @click="showInfo = !showInfo" :title="t('latentLab.attention.infoTitle')">?</button>
      </div>

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
    <div class="visualization-section" v-if="imageData">
      <!-- Image with heatmap overlay -->
      <div class="image-container" ref="imageContainerRef">
        <img
          :src="`data:image/png;base64,${imageData}`"
          class="generated-image"
          ref="imageRef"
          @load="onImageLoad"
        />
        <canvas
          ref="heatmapCanvas"
          class="heatmap-overlay"
          :style="{ opacity: heatmapOpacity }"
        ></canvas>
      </div>

      <!-- Token Chips -->
      <div class="token-section">
        <div class="token-label">{{ t('latentLab.attention.tokensLabel') }}</div>
        <div class="token-chips">
          <button
            v-for="(token, idx) in tokens"
            :key="idx"
            class="token-chip"
            :class="{
              selected: selectedTokens.includes(idx),
              [`color-${idx % 8}`]: selectedTokens.includes(idx)
            }"
            @click="toggleToken(idx)"
          >
            {{ token }}
          </button>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls-section">
        <!-- Timestep Slider -->
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

        <!-- Layer Toggle -->
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

        <!-- Opacity Slider -->
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
      </div>

      <!-- Seed display -->
      <div class="seed-display">
        Seed: {{ actualSeed }}
      </div>
    </div>

    <!-- Empty State -->
    <div class="empty-state" v-else-if="!isGenerating">
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
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()

// State
const promptText = ref('')
const negativePrompt = ref('')
const steps = ref(25)
const cfgScale = ref(4.5)
const seed = ref(-1)
const isGenerating = ref(false)
const showInfo = ref(false)
const errorMessage = ref('')

// Result data
const imageData = ref('')
const tokens = ref<string[]>([])
const attentionMaps = ref<Record<string, Record<string, number[][]>>>({})
const spatialResolution = ref<[number, number]>([64, 64])
const captureLayers = ref<number[]>([3, 9, 17])
const captureSteps = ref<number[]>([])
const totalSteps = ref(25)
const actualSeed = ref(0)

// Interaction state
const selectedTokens = ref<number[]>([])
const selectedStep = ref(0)
const selectedLayerIdx = ref(1) // Default: mid layer
const heatmapOpacity = ref(0.6)

// Refs
const imageRef = ref<HTMLImageElement | null>(null)
const heatmapCanvas = ref<HTMLCanvasElement | null>(null)
const imageContainerRef = ref<HTMLDivElement | null>(null)

const layerLabels = ['Early', 'Mid', 'Late']

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

function toggleToken(idx: number) {
  const pos = selectedTokens.value.indexOf(idx)
  if (pos >= 0) {
    selectedTokens.value.splice(pos, 1)
  } else {
    selectedTokens.value.push(idx)
  }
}

async function generate() {
  if (!promptText.value.trim() || isGenerating.value) return

  isGenerating.value = true
  errorMessage.value = ''
  imageData.value = ''
  tokens.value = []
  attentionMaps.value = {}
  selectedTokens.value = []

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
      const runId = response.data.run_id
      const mediaOutput = response.data.media_output

      // Load the generated image from the media URL
      if (runId && mediaOutput?.url) {
        const imgResponse = await axios.get(mediaOutput.url, { responseType: 'blob' })
        const reader = new FileReader()
        const base64Promise = new Promise<string>((resolve) => {
          reader.onload = () => {
            const result = reader.result as string
            resolve(result.split(',')[1])
          }
          reader.readAsDataURL(imgResponse.data)
        })
        imageData.value = await base64Promise
        actualSeed.value = mediaOutput.seed || 0
      }

      // Attention data is included directly in the response
      const attData = response.data.attention_data
      if (attData) {
        tokens.value = attData.tokens || []
        attentionMaps.value = attData.attention_maps || {}
        spatialResolution.value = attData.spatial_resolution || [64, 64]
        captureLayers.value = attData.capture_layers || [3, 9, 17]
        captureSteps.value = attData.capture_steps || []
        totalSteps.value = steps.value

        // Auto-select first token
        if (tokens.value.length > 0) {
          selectedTokens.value = [0]
        }
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
watch([selectedTokens, selectedStep, selectedLayerIdx, heatmapOpacity], () => {
  renderHeatmap()
})

function renderHeatmap() {
  const canvas = heatmapCanvas.value
  const img = imageRef.value
  if (!canvas || !img || !imageData.value) return
  if (selectedTokens.value.length === 0) {
    // Clear canvas if no tokens selected
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

  // layerData shape: [image_tokens, text_tokens] = [spatialH*spatialW, num_tokens]
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // For each selected token, create a colored heatmap and composite
  for (let tIdx = 0; tIdx < selectedTokens.value.length; tIdx++) {
    const tokenIdx = selectedTokens.value[tIdx]
    const color = tokenColors[tIdx % tokenColors.length]

    // Extract attention values for this token: one value per spatial position
    const attnValues: number[] = []
    for (let i = 0; i < spatialH * spatialW; i++) {
      if (layerData[i] && layerData[i][tokenIdx] !== undefined) {
        attnValues.push(layerData[i][tokenIdx])
      } else {
        attnValues.push(0)
      }
    }

    // Normalize to [0, 1]
    const maxVal = Math.max(...attnValues, 1e-8)
    const normalized = attnValues.map(v => v / maxVal)

    // Create temporary canvas for bilinear upscaling
    const tmpCanvas = document.createElement('canvas')
    tmpCanvas.width = spatialW
    tmpCanvas.height = spatialH
    const tmpCtx = tmpCanvas.getContext('2d')
    if (!tmpCtx) continue

    const imgDataTmp = tmpCtx.createImageData(spatialW, spatialH)
    for (let y = 0; y < spatialH; y++) {
      for (let x = 0; x < spatialW; x++) {
        const idx = y * spatialW + x
        const intensity = normalized[idx]
        const pixIdx = idx * 4
        imgDataTmp.data[pixIdx] = color[0]
        imgDataTmp.data[pixIdx + 1] = color[1]
        imgDataTmp.data[pixIdx + 2] = color[2]
        imgDataTmp.data[pixIdx + 3] = Math.floor(intensity * 200)
      }
    }
    tmpCtx.putImageData(imgDataTmp, 0, 0)

    // Upscale with bilinear interpolation (canvas imageSmoothingEnabled)
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'
    ctx.globalCompositeOperation = tIdx === 0 ? 'source-over' : 'lighter'
    ctx.drawImage(tmpCanvas, 0, 0, canvas.width, canvas.height)
  }
}
</script>

<style scoped>
.attention-cartography {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
}

/* Info Panel */
.info-panel {
  margin-bottom: 1.5rem;
  background: rgba(0, 188, 212, 0.08);
  border: 1px solid rgba(0, 188, 212, 0.2);
  border-radius: 12px;
  padding: 1.25rem;
  position: relative;
}

.info-content h3 {
  color: #00BCD4;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.info-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.info-tech {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  margin-top: 0.5rem;
}

.info-tech strong {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
}

.info-tech p {
  font-size: 0.8rem;
  margin-top: 0.25rem;
  margin-bottom: 0;
}

.info-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.2rem;
  cursor: pointer;
}

/* Input Section */
.input-section {
  margin-bottom: 1.5rem;
}

.prompt-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.prompt-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  min-height: 48px;
}

.prompt-input:focus {
  outline: none;
  border-color: rgba(0, 188, 212, 0.5);
}

.prompt-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.generate-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #00BCD4, #0097A7);
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
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.info-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(0, 188, 212, 0.3);
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 6px;
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
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.token-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.token-chip {
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

.token-chip:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.token-chip.selected {
  border-color: currentColor;
  font-weight: 600;
}

.token-chip.color-0.selected { color: #ff4444; background: rgba(255, 68, 68, 0.15); }
.token-chip.color-1.selected { color: #44aaff; background: rgba(68, 170, 255, 0.15); }
.token-chip.color-2.selected { color: #44ff88; background: rgba(68, 255, 136, 0.15); }
.token-chip.color-3.selected { color: #ffcc00; background: rgba(255, 204, 0, 0.15); }
.token-chip.color-4.selected { color: #ff44ff; background: rgba(255, 68, 255, 0.15); }
.token-chip.color-5.selected { color: #ff8800; background: rgba(255, 136, 0, 0.15); }
.token-chip.color-6.selected { color: #00ffff; background: rgba(0, 255, 255, 0.15); }
.token-chip.color-7.selected { color: #b844ff; background: rgba(184, 68, 255, 0.15); }

/* Controls */
.controls-section {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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
  background: #00BCD4;
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
  background: rgba(0, 188, 212, 0.2);
  border-color: rgba(0, 188, 212, 0.5);
  color: #00BCD4;
}

.seed-display {
  margin-top: 0.75rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  font-family: 'Fira Code', 'Consolas', monospace;
}

/* Empty / Progress / Error States */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.95rem;
}

.progress-state {
  text-align: center;
  padding: 3rem 2rem;
  color: rgba(0, 188, 212, 0.7);
}

.progress-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 188, 212, 0.2);
  border-top-color: #00BCD4;
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
