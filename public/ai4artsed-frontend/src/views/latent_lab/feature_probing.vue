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

    <!-- Side-by-Side Image Comparison (always visible) -->
    <div class="comparison-section" :class="{ disabled: !hasAnalysis && !isGenerating }">
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

        <!-- Modified (Transfer from Prompt B) -->
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

      <!-- Transfer Button -->
      <button
        class="generate-btn transfer-btn"
        :disabled="!hasAnalysis || isTransferring || selectedDimCount === 0"
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

    <!-- Dimension Analysis Section (always visible, disabled before analysis) -->
    <div class="analysis-section" :class="{ disabled: !hasAnalysis }">
      <!-- Prominent list header -->
      <div class="analysis-list-header">
        <h3 class="list-title">
          {{ t('latentLab.probing.listTitle', { count: nonzeroDimCount }) }}
        </h3>
        <p class="list-subtitle">
          {{ t('latentLab.probing.selectionDesc', { count: selectedDimCount, from: rankFrom, to: rankTo, total: nonzeroDimCount }) }}
        </p>
      </div>

      <!-- Slider label -->
      <div class="slider-label">{{ t('latentLab.probing.sliderLabel') }}</div>

      <!-- Visual Range Bar (shows both ranges) -->
      <div class="dimension-bar-visual">
        <div class="dimension-bar-track">
          <div class="dimension-bar-fill range-1"
            :style="{
              left: nonzeroDimCount > 0 ? ((rankFrom - 1) / nonzeroDimCount * 100) + '%' : '0%',
              width: nonzeroDimCount > 0 ? ((rankTo - rankFrom + 1) / nonzeroDimCount * 100) + '%' : '0%'
            }">
          </div>
          <div v-if="showRange2" class="dimension-bar-fill range-2"
            :style="{
              left: nonzeroDimCount > 0 ? ((rankFrom2 - 1) / nonzeroDimCount * 100) + '%' : '0%',
              width: nonzeroDimCount > 0 ? ((rankTo2 - rankFrom2 + 1) / nonzeroDimCount * 100) + '%' : '0%'
            }">
          </div>
        </div>
      </div>

      <!-- Range 1: Dual Handle Slider -->
      <div class="range-block">
        <div class="range-block-label">{{ t('latentLab.probing.range1Label') }}</div>
        <div class="dual-slider-container">
          <input type="range" min="1" :max="nonzeroDimCount || 1" step="1"
            v-model.number="rankFrom"
            class="slider-track slider-start"
            :disabled="!hasAnalysis"
            @input="clampStart" />
          <input type="range" min="1" :max="nonzeroDimCount || 1" step="1"
            v-model.number="rankTo"
            class="slider-track slider-end"
            :disabled="!hasAnalysis"
            @input="clampEnd" />
        </div>
        <div class="range-display">
          <div class="range-field">
            <label>{{ t('latentLab.probing.rankFromLabel') }}</label>
            <input type="number" v-model.number="rankFrom" :min="1" :max="rankTo || 1" class="range-input"
              :disabled="!hasAnalysis"
              @change="clampStart" @focus="($event.target as HTMLInputElement).select()" />
          </div>
          <span class="range-separator">–</span>
          <div class="range-field">
            <label>{{ t('latentLab.probing.rankToLabel') }}</label>
            <input type="number" v-model.number="rankTo" :min="rankFrom" :max="nonzeroDimCount || 0" class="range-input"
              :disabled="!hasAnalysis"
              @change="clampEnd" @focus="($event.target as HTMLInputElement).select()" />
          </div>
          <div class="selection-actions">
            <button class="mini-btn" @click="selectAll" :disabled="!hasAnalysis">{{ t('latentLab.probing.selectAll') }}</button>
            <button class="mini-btn" @click="selectNone" :disabled="!hasAnalysis">{{ t('latentLab.probing.selectNone') }}</button>
          </div>
        </div>
      </div>

      <!-- Add Range 2 Button -->
      <button v-if="!showRange2" class="mini-btn add-range-btn" :disabled="!hasAnalysis" @click="addRange2">
        + {{ t('latentLab.probing.addRange') }}
      </button>

      <!-- Range 2: Dual Handle Slider (optional) -->
      <div v-if="showRange2" class="range-block range-block-2">
        <div class="range-block-label">
          {{ t('latentLab.probing.range2Label') }}
          <button class="mini-btn remove-range-btn" @click="removeRange2">&times;</button>
        </div>
        <div class="dual-slider-container">
          <input type="range" min="1" :max="nonzeroDimCount || 1" step="1"
            v-model.number="rankFrom2"
            class="slider-track slider-start"
            :disabled="!hasAnalysis"
            @input="clampStart2" />
          <input type="range" min="1" :max="nonzeroDimCount || 1" step="1"
            v-model.number="rankTo2"
            class="slider-track slider-end"
            :disabled="!hasAnalysis"
            @input="clampEnd2" />
        </div>
        <div class="range-display">
          <div class="range-field">
            <label>{{ t('latentLab.probing.rankFromLabel') }}</label>
            <input type="number" v-model.number="rankFrom2" :min="1" :max="rankTo2 || 1" class="range-input"
              :disabled="!hasAnalysis"
              @change="clampStart2" @focus="($event.target as HTMLInputElement).select()" />
          </div>
          <span class="range-separator">–</span>
          <div class="range-field">
            <label>{{ t('latentLab.probing.rankToLabel') }}</label>
            <input type="number" v-model.number="rankTo2" :min="rankFrom2" :max="nonzeroDimCount || 0" class="range-input"
              :disabled="!hasAnalysis"
              @change="clampEnd2" @focus="($event.target as HTMLInputElement).select()" />
          </div>
        </div>
      </div>

      <!-- Sort toggle + column headers -->
      <div class="dim-list-controls" v-if="displayDims.length > 0">
        <button class="mini-btn sort-btn" @click="toggleSort">
          {{ sortAscending ? t('latentLab.probing.sortAsc') : t('latentLab.probing.sortDesc') }}
        </button>
      </div>

      <!-- Dimension Bars with checkboxes -->
      <div class="dimension-bars" v-if="displayDims.length > 0">
        <div
          v-for="(dim, idx) in sortedDisplayDims"
          :key="dim.index"
          class="dim-row"
          :class="{ 'in-range-1': inRange1(dim.rank), 'in-range-2': inRange2(dim.rank) }"
          @click="toggleDim(dim.rank)"
        >
          <label class="dim-checkbox" @click.stop>
            <input type="checkbox" :checked="isInRange(dim.rank)" @change="toggleDim(dim.rank)" />
          </label>
          <span class="dim-rank">{{ dim.rank + 1 }}</span>
          <span class="dim-index">d{{ dim.index }}</span>
          <div class="dim-bar-container">
            <div
              class="dim-bar"
              :style="{ width: `${(dim.value / maxDiffValue) * 100}%` }"
              :class="{ 'in-range-1': inRange1(dim.rank), 'in-range-2': inRange2(dim.rank) }"
            ></div>
          </div>
          <span class="dim-value">{{ dim.value.toFixed(3) }}</span>
        </div>
      </div>

      <!-- No difference message -->
      <div class="no-diff-message" v-if="analysisComplete && displayDims.length === 0">
        <p>{{ t('latentLab.probing.noDifference') }}</p>
      </div>
    </div>

    <!-- Error Display -->
    <div class="error-display" v-if="errorMessage">
      <p>{{ errorMessage }}</p>
      <button @click="errorMessage = ''" class="dismiss-btn">&times;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue'
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
const sortAscending = ref(false)

// Result data
const originalImage = ref('')
const modifiedImage = ref('')
const actualSeed = ref<number | null>(null)
const topDims = ref<{ index: number; value: number }[]>([])
// Range 1
const rankFrom = ref(1)
const rankTo = ref(0)
// Range 2 (optional, additive)
const showRange2 = ref(false)
const rankFrom2 = ref(1)
const rankTo2 = ref(0)

// Computed
const isGenerating = computed(() => isAnalyzing.value || isTransferring.value)
const hasAnalysis = computed(() => displayDims.value.length > 0)
const maxDiffValue = computed(() => {
  if (topDims.value.length === 0) return 1
  return topDims.value[0]?.value ?? 1
})
// Only show dimensions with nonzero difference
const displayDims = computed(() => topDims.value.filter(d => d.value > 1e-6))
const nonzeroDimCount = computed(() => displayDims.value.length)
// displayDims with original rank preserved, optionally reversed
const sortedDisplayDims = computed(() => {
  const withRank = displayDims.value.map((d, idx) => ({ ...d, rank: idx }))
  return sortAscending.value ? [...withRank].reverse() : withRank
})

// Derive selected dimensions from union of both rank ranges
const selectedDims = computed(() => {
  const dims = new Set<number>()
  const addRange = (from: number, to: number) => {
    const f = Math.max(0, from - 1)
    const t = Math.min(displayDims.value.length, to)
    for (let i = f; i < t; i++) {
      dims.add(displayDims.value[i]!.index)
    }
  }
  addRange(rankFrom.value, rankTo.value)
  if (showRange2.value) {
    addRange(rankFrom2.value, rankTo2.value)
  }
  return dims
})
const selectedDimCount = computed(() => selectedDims.value.size)

function inRange1(idx: number): boolean {
  return idx >= rankFrom.value - 1 && idx < rankTo.value
}

function inRange2(idx: number): boolean {
  return showRange2.value && idx >= rankFrom2.value - 1 && idx < rankTo2.value
}

function isInRange(idx: number): boolean {
  return inRange1(idx) || inRange2(idx)
}

function clampStart() {
  if (rankFrom.value < 1) rankFrom.value = 1
  if (rankFrom.value > rankTo.value) rankFrom.value = rankTo.value
}

function clampEnd() {
  if (rankTo.value < rankFrom.value) rankTo.value = rankFrom.value
  if (rankTo.value > nonzeroDimCount.value) rankTo.value = nonzeroDimCount.value
}

function clampStart2() {
  if (rankFrom2.value < 1) rankFrom2.value = 1
  if (rankFrom2.value > rankTo2.value) rankFrom2.value = rankTo2.value
}

function clampEnd2() {
  if (rankTo2.value < rankFrom2.value) rankTo2.value = rankFrom2.value
  if (rankTo2.value > nonzeroDimCount.value) rankTo2.value = nonzeroDimCount.value
}

function selectAll() {
  rankFrom.value = 1
  rankTo.value = nonzeroDimCount.value
  if (showRange2.value) {
    showRange2.value = false
    rankFrom2.value = 1
    rankTo2.value = 0
  }
}

function selectNone() {
  rankFrom.value = 1
  rankTo.value = 0
  rankFrom2.value = 1
  rankTo2.value = 0
}

function addRange2() {
  showRange2.value = true
  // Default: no selection, user positions it
  rankFrom2.value = 1
  rankTo2.value = 0
}

function removeRange2() {
  showRange2.value = false
  rankFrom2.value = 1
  rankTo2.value = 0
}

function toggleSort() {
  sortAscending.value = !sortAscending.value
}

function toggleDim(rankIdx: number) {
  // Expand or contract range 1 to include/exclude this rank
  const rank1based = rankIdx + 1
  if (inRange1(rankIdx)) {
    if (rank1based === rankFrom.value) rankFrom.value++
    else if (rank1based === rankTo.value) rankTo.value--
  } else if (inRange2(rankIdx)) {
    if (rank1based === rankFrom2.value) rankFrom2.value++
    else if (rank1based === rankTo2.value) rankTo2.value--
  } else {
    // Expand nearest range
    if (rank1based < rankFrom.value) rankFrom.value = rank1based
    else if (rank1based > rankTo.value) rankTo.value = rank1based
  }
}

async function analyze() {
  if (!promptA.value.trim() || !promptB.value.trim() || isGenerating.value) return

  isAnalyzing.value = true
  errorMessage.value = ''
  originalImage.value = ''
  modifiedImage.value = ''
  topDims.value = []
  analysisComplete.value = false
  actualSeed.value = null
  rankFrom.value = 1
  rankTo.value = 0
  showRange2.value = false
  rankFrom2.value = 1
  rankTo2.value = 0

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

        // Build top dims list from probing data (already sorted by magnitude)
        const dims = probData.top_dims || []
        const vals = probData.top_values || []
        topDims.value = dims.map((dimIdx: number, i: number) => ({
          index: dimIdx,
          value: vals[i] ?? 0,
        }))

        // Default: select all nonzero dimensions
        rankTo.value = topDims.value.filter((d: { value: number }) => d.value > 1e-6).length

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

/* Disabled state for sections before analysis */
.comparison-section.disabled,
.analysis-section.disabled {
  opacity: 0.35;
  pointer-events: none;
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

/* Analysis Section */
.analysis-section {
  margin-top: 1rem;
}

/* Prominent list header */
.analysis-list-header {
  background: rgba(124, 77, 255, 0.08);
  border: 1px solid rgba(124, 77, 255, 0.2);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.list-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
}

.list-subtitle {
  color: rgba(124, 77, 255, 0.85);
  font-size: 0.85rem;
  margin: 0;
}

.slider-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}

.selection-actions {
  display: flex;
  gap: 0.35rem;
  margin-left: auto;
}

/* Range blocks */
.range-block {
  margin-bottom: 0.5rem;
}

.range-block-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  margin-bottom: 0.15rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.range-block-2 .dimension-bar-fill,
.range-block-2 .dual-slider-container input[type="range"]::-webkit-slider-thumb {
  background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
}

.add-range-btn {
  margin-bottom: 0.75rem;
}

.remove-range-btn {
  padding: 0 0.35rem;
  font-size: 0.85rem;
  line-height: 1;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  cursor: pointer;
}

.remove-range-btn:hover {
  color: #ef5350;
  border-color: rgba(244, 67, 54, 0.3);
}

.dim-list-controls {
  display: flex;
  align-items: center;
  margin-bottom: 0.35rem;
}

.sort-btn {
  font-size: 0.7rem;
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

/* Visual Range Bar */
.dimension-bar-visual {
  margin-bottom: 0.25rem;
}

.dimension-bar-track {
  height: 20px;
  background: rgba(30, 30, 30, 0.8);
  border-radius: 10px;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.15);
  overflow: hidden;
}

.dimension-bar-fill {
  position: absolute;
  top: 2px;
  bottom: 2px;
  border-radius: 8px;
  transition: all 0.1s ease;
}

.dimension-bar-fill.range-1 {
  background: linear-gradient(135deg, #7C4DFF 0%, #651FFF 100%);
  box-shadow: 0 0 8px rgba(124, 77, 255, 0.4);
}

.dimension-bar-fill.range-2 {
  background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
  box-shadow: 0 0 8px rgba(0, 188, 212, 0.4);
}

/* Dual Handle Slider (pattern from partial_elimination) */
.dual-slider-container {
  position: relative;
  height: 32px;
  margin: 0.5rem 0;
}

.dual-slider-container input[type="range"] {
  position: absolute;
  width: 100%;
  height: 8px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
}

.dual-slider-container .slider-start {
  z-index: 1;
}

.dual-slider-container .slider-end {
  z-index: 2;
}

.dual-slider-container input[type="range"]::-webkit-slider-runnable-track {
  height: 8px;
  background: transparent;
  border-radius: 4px;
}

.dual-slider-container input[type="range"]::-moz-range-track {
  height: 8px;
  background: transparent;
  border-radius: 4px;
}

.dual-slider-container input[type="range"]::-webkit-slider-thumb {
  pointer-events: all;
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #7C4DFF 0%, #651FFF 100%);
  border: 2px solid white;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
  transition: transform 0.15s ease;
}

.dual-slider-container input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 10px rgba(124, 77, 255, 0.5);
}

.dual-slider-container input[type="range"]::-webkit-slider-thumb:active {
  cursor: grabbing;
}

.dual-slider-container input[type="range"]::-moz-range-thumb {
  pointer-events: all;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #7C4DFF 0%, #651FFF 100%);
  border: 2px solid white;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

/* Range Display (number fields) */
.range-display {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.range-field {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}

.range-field label {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.7rem;
}

.range-input {
  width: 75px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  padding: 0.35rem 0.5rem;
  color: white;
  font-size: 0.9rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  text-align: center;
}

.range-separator {
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.2rem;
  padding-bottom: 0.3rem;
}

/* Selection Description */
.selection-description {
  color: rgba(124, 77, 255, 0.85);
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0 0 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(124, 77, 255, 0.08);
  border-radius: 8px;
  border-left: 3px solid rgba(124, 77, 255, 0.4);
}

/* Dimension Bars */
.dimension-bars {
  display: flex;
  flex-direction: column;
  gap: 1px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.dim-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  transition: background 0.1s ease;
  opacity: 0.35;
}

.dim-row.in-range-1,
.dim-row.in-range-2 {
  opacity: 1;
}

.dim-row.in-range-1 {
  background: rgba(124, 77, 255, 0.06);
}

.dim-row.in-range-2 {
  background: rgba(0, 188, 212, 0.06);
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

.dim-rank {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.65rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  min-width: 35px;
  text-align: right;
}

.dim-row.in-range-1 .dim-rank {
  color: rgba(124, 77, 255, 0.6);
}

.dim-row.in-range-2 .dim-rank {
  color: rgba(0, 188, 212, 0.6);
}

.dim-index {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.65rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  min-width: 45px;
  text-align: right;
}

.dim-bar-container {
  flex: 1;
  height: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 2px;
  overflow: hidden;
}

.dim-bar {
  height: 100%;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 2px;
  transition: background 0.15s ease;
}

.dim-bar.in-range-1 {
  background: rgba(124, 77, 255, 0.5);
}

.dim-bar.in-range-2 {
  background: rgba(0, 188, 212, 0.5);
}

.dim-value {
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.65rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  min-width: 50px;
  text-align: right;
}

.dim-row.in-range-1 .dim-value,
.dim-row.in-range-2 .dim-value {
  color: rgba(255, 255, 255, 0.6);
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
