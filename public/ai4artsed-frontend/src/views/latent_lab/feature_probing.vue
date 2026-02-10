<template>
  <div class="feature-probing">
    <!-- Header (always visible) -->
    <div class="page-header">
      <h2 class="page-title">{{ t('latentLab.probing.headerTitle') }}</h2>
      <p class="page-subtitle">{{ t('latentLab.probing.headerSubtitle') }}</p>
      <details class="explanation-details">
        <summary>{{ t('latentLab.probing.explanationToggle') }}</summary>
        <div class="explanation-body">
          <div class="explanation-section">
            <h4>{{ t('latentLab.probing.explainWhatTitle') }}</h4>
            <p>{{ t('latentLab.probing.explainWhatText') }}</p>
          </div>
          <div class="explanation-section">
            <h4>{{ t('latentLab.probing.explainHowTitle') }}</h4>
            <p>{{ t('latentLab.probing.explainHowText') }}</p>
          </div>
          <div class="explanation-section">
            <h4>{{ t('latentLab.probing.explainReadTitle') }}</h4>
            <p>{{ t('latentLab.probing.explainReadText') }}</p>
          </div>
          <div class="explanation-section explanation-tech">
            <h4>{{ t('latentLab.probing.techTitle') }}</h4>
            <p>{{ t('latentLab.probing.techText') }}</p>
          </div>
        </div>
      </details>
    </div>

    <!-- Input Section -->
    <div class="input-section">
      <!-- Prompt A -->
      <MediaInputBox
        icon="lightbulb"
        :label="t('latentLab.probing.promptALabel')"
        :placeholder="t('latentLab.probing.promptAPlaceholder')"
        v-model:value="promptA"
        input-type="text"
        :rows="2"
        resize-type="auto"
        :disabled="isGenerating"
        :show-actions="false"
      />

      <!-- Prompt B -->
      <MediaInputBox
        icon="clipboard"
        :label="t('latentLab.probing.promptBLabel')"
        :placeholder="t('latentLab.probing.promptBPlaceholder')"
        v-model:value="promptB"
        input-type="text"
        :rows="2"
        resize-type="auto"
        :disabled="isGenerating"
        :show-actions="false"
      />

      <!-- Encoder Toggle + Analyze Button -->
      <div class="action-row">
        <div class="control-group">
          <label class="control-label">{{ t('latentLab.probing.encoderLabel') }}</label>
          <div class="layer-toggles">
            <button
              v-for="enc in encoders"
              :key="enc.id"
              class="layer-btn"
              :class="{ active: selectedEncoder === enc.id }"
              @click="selectedEncoder = enc.id"
              :disabled="isGenerating"
            >
              {{ t(`latentLab.probing.${enc.labelKey}`) }}
            </button>
          </div>
        </div>
        <button
          class="generate-btn"
          :disabled="isGenerating || !promptA.trim() || !promptB.trim()"
          @click="analyze"
        >
          <span v-if="isAnalyzing" class="spinner"></span>
          <span v-else>{{ t('latentLab.probing.analyzeBtn') }}</span>
        </button>
      </div>

      <!-- Advanced Settings (collapsible) -->
      <details class="advanced-settings">
        <summary>{{ t('latentLab.probing.advancedLabel') }}</summary>
        <div class="settings-grid">
          <label>
            {{ t('latentLab.probing.negativeLabel') }}
            <input v-model="negativePrompt" type="text" class="setting-input" />
          </label>
          <label>
            {{ t('latentLab.probing.stepsLabel') }}
            <input v-model.number="steps" type="number" min="10" max="50" class="setting-input setting-small" />
          </label>
          <label>
            {{ t('latentLab.probing.cfgLabel') }}
            <input v-model.number="cfgScale" type="number" min="1" max="20" step="0.5" class="setting-input setting-small" />
          </label>
          <label>
            {{ t('latentLab.probing.seedLabel') }}
            <input v-model.number="seed" type="number" min="-1" class="setting-input setting-small" />
          </label>
        </div>
      </details>
    </div>

    <!-- Side-by-Side Image Comparison -->
    <div class="comparison-section" v-if="originalImage || isGenerating">
      <div class="image-pair">
        <!-- Original (Prompt A) -->
        <div class="image-panel">
          <div class="panel-label">{{ t('latentLab.probing.originalLabel') }}</div>
          <div class="image-frame" :class="{ empty: !originalImage }">
            <img
              v-if="originalImage"
              :src="`data:image/png;base64,${originalImage}`"
              class="result-image"
            />
            <div v-else-if="isAnalyzing" class="image-placeholder">
              <div class="progress-spinner"></div>
              <p>{{ t('latentLab.probing.analyzing') }}</p>
            </div>
          </div>
        </div>

        <!-- Modified (Transfer) -->
        <div class="image-panel">
          <div class="panel-label">{{ t('latentLab.probing.modifiedLabel') }}</div>
          <div class="image-frame" :class="{ empty: !modifiedImage }">
            <img
              v-if="modifiedImage"
              :src="`data:image/png;base64,${modifiedImage}`"
              class="result-image"
            />
            <div v-else-if="isTransferring" class="image-placeholder">
              <div class="progress-spinner"></div>
              <p>{{ t('latentLab.probing.transferring') }}</p>
            </div>
            <div v-else class="image-placeholder-hint">
              <p>{{ t('latentLab.probing.modifiedHint') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Transfer Button (directly under images) -->
      <button
        v-if="topDims.length > 0"
        class="generate-btn transfer-btn"
        :disabled="isTransferring || selectedDimCount === 0"
        @click="transfer"
      >
        <span v-if="isTransferring" class="spinner"></span>
        <span v-else>{{ t('latentLab.probing.transferBtn') }} ({{ selectedDimCount }})</span>
      </button>

      <!-- Seed display -->
      <div v-if="actualSeed !== null" class="seed-display">
        Seed: {{ actualSeed }}
      </div>
    </div>

    <!-- Dimension Analysis Section -->
    <div class="analysis-section" v-if="topDims.length > 0">
      <div class="analysis-header">
        <h3 class="analysis-title">{{ t('latentLab.probing.dimLabel') }} (Top {{ visibleDims.length }} / {{ topDims.length }})</h3>
        <div class="selection-info">
          {{ selectedDimCount }} {{ t('latentLab.probing.selectedDims') }}
          <button class="mini-btn" @click="selectAll">{{ t('latentLab.probing.selectAll') }}</button>
          <button class="mini-btn" @click="selectNone">{{ t('latentLab.probing.selectNone') }}</button>
        </div>
      </div>

      <!-- Threshold Slider -->
      <div class="threshold-group">
        <div class="control-row">
          <label class="control-label">{{ t('latentLab.probing.thresholdLabel') }}</label>
          <div class="slider-container">
            <input
              type="range"
              v-model.number="threshold"
              :min="0"
              :max="maxDiffValue"
              :step="maxDiffValue / 200"
              class="control-slider"
            />
            <span class="slider-value">{{ threshold.toFixed(3) }}</span>
          </div>
        </div>
        <div class="control-hint">{{ t('latentLab.probing.thresholdHint') }}</div>
      </div>

      <!-- Dimension Bars -->
      <div class="dimension-bars">
        <div
          v-for="(dim, idx) in visibleDims"
          :key="dim.index"
          class="dim-row"
          :class="{ selected: isDimSelected(dim.index) }"
          @click="toggleDim(dim.index)"
        >
          <label class="dim-checkbox">
            <input
              type="checkbox"
              :checked="isDimSelected(dim.index)"
              @click.stop="toggleDim(dim.index)"
            />
          </label>
          <span class="dim-index">{{ dim.index }}</span>
          <div class="dim-bar-container">
            <div
              class="dim-bar"
              :style="{ width: `${(dim.value / maxDiffValue) * 100}%` }"
              :class="{ 'above-threshold': dim.value >= threshold }"
            ></div>
          </div>
          <span class="dim-value">{{ dim.value.toFixed(3) }}</span>
        </div>
      </div>

      <div class="dim-hint">{{ t('latentLab.probing.dimHint') }}</div>
    </div>

    <!-- No difference message -->
    <div class="no-diff-message" v-else-if="analysisComplete && topDims.length === 0">
      <p>{{ t('latentLab.probing.noDifference') }}</p>
    </div>

    <!-- Empty State -->
    <div class="empty-state" v-else-if="!isGenerating && !originalImage">
      <p>{{ t('latentLab.probing.emptyHint') }}</p>
    </div>

    <!-- Error Display -->
    <div class="error-display" v-if="errorMessage">
      <p>{{ errorMessage }}</p>
      <button @click="errorMessage = ''" class="dismiss-btn">&times;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import MediaInputBox from '@/components/MediaInputBox.vue'
import { usePageContextStore } from '@/stores/pageContext'
import type { PageContext, FocusHint } from '@/composables/usePageContext'

const { t } = useI18n()
const pageContextStore = usePageContextStore()

// Encoder options
type EncoderId = 'all' | 'clip_l' | 'clip_g' | 't5'
const encoders: { id: EncoderId; labelKey: string }[] = [
  { id: 'all', labelKey: 'encoderAll' },
  { id: 'clip_l', labelKey: 'encoderClipL' },
  { id: 'clip_g', labelKey: 'encoderClipG' },
  { id: 't5', labelKey: 'encoderT5' },
]

// State
const promptA = ref('')
const promptB = ref('')
const selectedEncoder = ref<EncoderId>('all')
const negativePrompt = ref('')
const steps = ref(25)
const cfgScale = ref(4.5)
const seed = ref(-1)
const isAnalyzing = ref(false)
const isTransferring = ref(false)
const errorMessage = ref('')
const analysisComplete = ref(false)

// Result data
const originalImage = ref('')
const modifiedImage = ref('')
const actualSeed = ref<number | null>(null)
const topDims = ref<{ index: number; value: number }[]>([])
const allDiffPerDim = ref<number[]>([])
const selectedDims = ref<Set<number>>(new Set())
const threshold = ref(0)

// Computed
const isGenerating = computed(() => isAnalyzing.value || isTransferring.value)
const maxDiffValue = computed(() => {
  if (topDims.value.length === 0) return 1
  return topDims.value[0]?.value ?? 1
})
const selectedDimCount = computed(() => selectedDims.value.size)
// Show max 50 bars in UI, but all dims are selectable via threshold
const MAX_VISIBLE_BARS = 50
const visibleDims = computed(() => topDims.value.slice(0, MAX_VISIBLE_BARS))

function isDimSelected(dimIndex: number): boolean {
  return selectedDims.value.has(dimIndex)
}

function toggleDim(dimIndex: number) {
  const next = new Set(selectedDims.value)
  if (next.has(dimIndex)) {
    next.delete(dimIndex)
  } else {
    next.add(dimIndex)
  }
  selectedDims.value = next
}

function selectAll() {
  const next = new Set<number>()
  // Use allDiffPerDim to include ALL dimensions with nonzero difference,
  // not just the top-k visible in the bar chart
  allDiffPerDim.value.forEach((diffVal, dimIndex) => {
    if (diffVal > 1e-6) next.add(dimIndex)
  })
  selectedDims.value = next
}

function selectNone() {
  selectedDims.value = new Set()
}

// When threshold changes, auto-select ALL dimensions above threshold
// (using full diff array, not just top-k visible bars)
watch(threshold, (val) => {
  const next = new Set<number>()
  allDiffPerDim.value.forEach((diffVal, dimIndex) => {
    if (diffVal >= val && diffVal > 1e-6) {
      next.add(dimIndex)
    }
  })
  selectedDims.value = next
})

async function analyze() {
  if (!promptA.value.trim() || !promptB.value.trim() || isGenerating.value) return

  isAnalyzing.value = true
  errorMessage.value = ''
  originalImage.value = ''
  modifiedImage.value = ''
  topDims.value = []
  allDiffPerDim.value = []
  selectedDims.value = new Set()
  analysisComplete.value = false
  actualSeed.value = null

  try {
    const baseUrl = import.meta.env.DEV ? 'http://localhost:17802' : ''
    const response = await axios.post(`${baseUrl}/api/schema/pipeline/legacy`, {
      prompt: promptA.value,
      output_config: 'feature_probing_diffusers',
      seed: seed.value,
      negative_prompt: negativePrompt.value,
      steps: steps.value,
      cfg: cfgScale.value,
      prompt_b: promptB.value,
      probing_encoder: selectedEncoder.value,
    })

    if (response.data.status === 'success') {
      const probData = response.data.probing_data
      if (probData) {
        if (probData.image_base64) {
          originalImage.value = probData.image_base64
        }

        actualSeed.value = response.data.media_output?.seed ?? null

        // Build top dims list from probing data
        const dims = probData.top_dims || []
        const vals = probData.top_values || []
        topDims.value = dims.map((dimIdx: number, i: number) => ({
          index: dimIdx,
          value: vals[i] ?? 0,
        }))

        allDiffPerDim.value = probData.diff_per_dim || []

        // Set initial threshold to select ~half of returned dims
        // Semantic concepts are distributed across hundreds of dimensions,
        // so we need many dims selected by default to produce a visible change
        const halfIdx = Math.floor(topDims.value.length / 2)
        if (topDims.value.length > 0 && halfIdx > 0) {
          threshold.value = topDims.value[halfIdx]?.value ?? 0
        } else if (topDims.value.length > 0) {
          threshold.value = 0
        }

        analysisComplete.value = true
      } else {
        errorMessage.value = 'No probing data in response'
      }
    } else {
      errorMessage.value = response.data.error || response.data.message || 'Analysis failed'
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error || err.message || 'Network error'
  } finally {
    isAnalyzing.value = false
  }
}

async function transfer() {
  if (selectedDimCount.value === 0 || isGenerating.value) return

  isTransferring.value = true
  errorMessage.value = ''
  modifiedImage.value = ''

  try {
    const baseUrl = import.meta.env.DEV ? 'http://localhost:17802' : ''
    const response = await axios.post(`${baseUrl}/api/schema/pipeline/legacy`, {
      prompt: promptA.value,
      output_config: 'feature_probing_diffusers',
      seed: actualSeed.value ?? seed.value,
      negative_prompt: negativePrompt.value,
      steps: steps.value,
      cfg: cfgScale.value,
      prompt_b: promptB.value,
      probing_encoder: selectedEncoder.value,
      transfer_dims: Array.from(selectedDims.value),
    })

    if (response.data.status === 'success') {
      const probData = response.data.probing_data
      if (probData?.image_base64) {
        modifiedImage.value = probData.image_base64
      } else {
        errorMessage.value = 'No image in transfer response'
      }
    } else {
      errorMessage.value = response.data.error || response.data.message || 'Transfer failed'
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error || err.message || 'Network error'
  } finally {
    isTransferring.value = false
  }
}

// Trashy Page Context
const trashyFocusHint = computed<FocusHint>(() => {
  if (isGenerating.value || originalImage.value) {
    return { x: 95, y: 85, anchor: 'bottom-right' }
  }
  return { x: 8, y: 95, anchor: 'bottom-left' }
})

const pageContext = computed<PageContext>(() => ({
  activeViewType: 'feature_probing',
  pageContent: {
    inputText: `A: ${promptA.value}\nB: ${promptB.value}`,
  },
  focusHint: trashyFocusHint.value,
}))

watch(pageContext, (ctx) => {
  pageContextStore.setPageContext(ctx)
}, { immediate: true, deep: true })

onUnmounted(() => {
  pageContextStore.clearContext()
})
</script>

<style scoped>
.feature-probing {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
}

/* Page Header — same as Attention Cartography */
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  color: #00BCD4;
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
  background: rgba(0, 188, 212, 0.06);
  border: 1px solid rgba(0, 188, 212, 0.15);
  border-radius: 10px;
  overflow: hidden;
}

.explanation-details summary {
  padding: 0.65rem 1rem;
  color: rgba(0, 188, 212, 0.8);
  font-size: 0.85rem;
  cursor: pointer;
  user-select: none;
}

.explanation-details summary:hover {
  color: #00BCD4;
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
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

/* Action Row (Encoder + Analyze) */
.action-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.control-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  flex-shrink: 0;
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
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.layer-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.layer-btn.active {
  background: rgba(0, 188, 212, 0.2);
  border-color: rgba(0, 188, 212, 0.5);
  color: #00BCD4;
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
  min-height: 42px;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.transfer-btn {
  margin-top: 1rem;
  width: 100%;
  background: linear-gradient(135deg, #7C4DFF, #651FFF);
}

.transfer-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(124, 77, 255, 0.3);
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
  margin-top: 0.25rem;
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

/* Comparison Section (side-by-side images) */
.comparison-section {
  margin-bottom: 1.5rem;
}

.image-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.image-panel {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.panel-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.image-frame {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-frame.empty {
  border-style: dashed;
  border-color: rgba(255, 255, 255, 0.15);
}

.result-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-placeholder {
  text-align: center;
  color: rgba(0, 188, 212, 0.7);
  padding: 2rem;
}

.image-placeholder p {
  font-size: 0.85rem;
  margin-top: 0.75rem;
}

.image-placeholder-hint {
  text-align: center;
  padding: 2rem 1.5rem;
}

.image-placeholder-hint p {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.8rem;
  line-height: 1.5;
  margin: 0;
}

.progress-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 188, 212, 0.2);
  border-top-color: #00BCD4;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

.seed-display {
  margin-top: 0.5rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  font-family: 'Fira Code', 'Consolas', monospace;
}

/* Analysis Section (bars) */
.analysis-section {
  margin-top: 1rem;
}

.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.analysis-title {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
}

.selection-info {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mini-btn {
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mini-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Threshold Slider */
.threshold-group {
  margin-bottom: 1rem;
}

.control-row {
  display: flex;
  align-items: center;
  gap: 1rem;
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
  min-width: 55px;
  text-align: right;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.control-hint {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  line-height: 1.4;
  margin-top: 0.25rem;
  padding-left: calc(80px + 1rem);
}

/* Dimension Bars */
.dimension-bars {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.dim-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.1s ease;
}

.dim-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.dim-row.selected {
  background: rgba(124, 77, 255, 0.1);
}

.dim-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.dim-checkbox input {
  accent-color: #7C4DFF;
  cursor: pointer;
}

.dim-index {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.7rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  min-width: 45px;
  text-align: right;
}

.dim-bar-container {
  flex: 1;
  height: 14px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 3px;
  overflow: hidden;
}

.dim-bar {
  height: 100%;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
  transition: width 0.2s ease, background 0.2s ease;
}

.dim-bar.above-threshold {
  background: rgba(124, 77, 255, 0.5);
}

.dim-value {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.7rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  min-width: 50px;
  text-align: right;
}

.dim-hint {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  margin-top: 0.5rem;
  line-height: 1.4;
}

/* States */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.95rem;
}

.no-diff-message {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 193, 7, 0.7);
  font-size: 0.9rem;
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

/* Responsive */
@media (max-width: 640px) {
  .image-pair {
    grid-template-columns: 1fr;
  }

  .action-row {
    flex-direction: column;
    align-items: stretch;
  }

  .control-group {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
