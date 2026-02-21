<template>
  <div class="latent-text-lab">
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">{{ t('latentLab.textLab.headerTitle') }}</h2>
      <p class="page-subtitle">{{ t('latentLab.textLab.headerSubtitle') }}</p>
      <details class="explanation-details">
        <summary>{{ t('latentLab.textLab.explanationToggle') }}</summary>
        <div class="explanation-body">
          <div class="explanation-section">
            <h4>{{ t('latentLab.textLab.explainWhatTitle') }}</h4>
            <p>{{ t('latentLab.textLab.explainWhatText') }}</p>
          </div>
          <div class="explanation-section">
            <h4>{{ t('latentLab.textLab.explainHowTitle') }}</h4>
            <p>{{ t('latentLab.textLab.explainHowText') }}</p>
          </div>
        </div>
      </details>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="error-banner" @click="errorMessage = ''">
      {{ errorMessage }}
    </div>

    <!-- Model Selector -->
    <div class="model-selector-row">
      <label class="control-label control-small">
        {{ t('latentLab.textLab.modelPanel.presetLabel') }}
        <select v-model="selectedPreset" class="control-select">
          <option v-for="(info, key) in presets" :key="key" :value="key">
            {{ key }} ({{ info.vram_gb }}GB)
          </option>
        </select>
      </label>
    </div>

    <!-- Tab navigation -->
    <div class="tab-nav">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ t(tab.labelKey) }}
      </button>
    </div>

    <!-- ================================================================ -->
    <!-- TAB 1: Representation Engineering -->
    <!-- ================================================================ -->
    <template v-if="activeTab === 'repeng'">
      <section class="tool-section">
        <h3 class="section-title">{{ t('latentLab.textLab.repeng.title') }}</h3>
        <p class="section-subtitle">{{ t('latentLab.textLab.repeng.subtitle') }}</p>

        <!-- Experiment Guide -->
        <div class="experiment-guide">
          <p class="guide-text">{{ t('latentLab.textLab.repeng.guide') }}</p>
          <p class="guide-hint">{{ t('latentLab.textLab.repeng.languageHint') }}</p>
        </div>

        <details class="science-details">
          <summary class="science-toggle">Zou et al. 2023 + Li et al. 2024</summary>
          <p class="science-text">{{ t('latentLab.textLab.repeng.science') }}</p>
        </details>

        <!-- Contrast Pair Editor -->
        <div class="subsection">
          <h4 class="subsection-title">{{ t('latentLab.textLab.repeng.pairsTitle') }}</h4>
          <p class="subsection-subtitle">{{ t('latentLab.textLab.repeng.pairsSubtitle') }}</p>
          <div class="contrast-pairs">
            <div v-for="(pair, idx) in contrastPairs" :key="idx" class="pair-row">
              <input
                v-model="pair.positive"
                type="text"
                class="control-input pair-input"
                :placeholder="t('latentLab.textLab.repeng.positivePlaceholder')"
              />
              <span class="pair-separator">vs.</span>
              <input
                v-model="pair.negative"
                type="text"
                class="control-input pair-input"
                :placeholder="t('latentLab.textLab.repeng.negativePlaceholder')"
              />
              <button
                v-if="contrastPairs.length > 1"
                class="remove-btn"
                @click="contrastPairs.splice(idx, 1)"
              >&#x2715;</button>
            </div>
            <button class="add-btn" @click="contrastPairs.push({ positive: '', negative: '' })">
              + {{ t('latentLab.textLab.repeng.addPair') }}
            </button>
          </div>
        </div>

        <!-- Direction Finder -->
        <div class="control-row">
          <label class="control-label control-small">
            {{ t('latentLab.textLab.repeng.targetLayerLabel') }}
            <select v-model.number="repTargetLayer" class="control-select">
              <option :value="-1">{{ t('latentLab.textLab.repeng.targetLayerAuto') }}</option>
              <option v-for="i in repLayerCount" :key="i" :value="i - 1">{{ i - 1 }}</option>
            </select>
            <div class="control-hint">{{ t('latentLab.textLab.repeng.targetLayerHint') }}</div>
          </label>
          <button
            class="action-btn"
            :disabled="!hasValidPairs || repLoading"
            @click="findDirection"
          >
            <span v-if="repLoading" class="spinner"></span>
            <span v-else>{{ t('latentLab.textLab.repeng.findDirection') }}</span>
          </button>
        </div>

        <!-- Direction Result -->
        <div v-if="repResult" class="direction-result">
          <div class="result-header">
            <span class="result-badge">{{ t('latentLab.textLab.repeng.directionFound') }}</span>
            <span class="result-stat">{{ t('latentLab.textLab.repeng.varianceLabel') }}: {{ (repResult.explained_variance * 100).toFixed(1) }}%</span>
            <span class="result-stat">{{ t('latentLab.textLab.repeng.dimLabel') }}: {{ repResult.embedding_dim }}</span>
          </div>

          <!-- Projections -->
          <div v-if="repResult.pair_projections" class="projections">
            <h4 class="subsection-title">{{ t('latentLab.textLab.repeng.projectionsTitle') }}</h4>
            <div v-for="(proj, idx) in repResult.pair_projections" :key="idx" class="projection-row">
              <div class="projection-bar-container">
                <div class="projection-bar" :style="projectionBarStyle(proj.projection)"></div>
              </div>
              <div class="projection-labels">
                <span class="proj-positive">{{ proj.positive }}</span>
                <span class="proj-value">{{ proj.projection.toFixed(3) }}</span>
                <span class="proj-negative">{{ proj.negative }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Expected Results Guide -->
        <div v-if="repResult" class="experiment-guide">
          <p class="guide-text">{{ t('latentLab.textLab.repeng.expectedResults') }}</p>
        </div>

        <!-- Test + Manipulation -->
        <div v-if="repResult" class="subsection">
          <h4 class="subsection-title">{{ t('latentLab.textLab.repeng.testTitle') }}</h4>
          <p class="subsection-subtitle">{{ t('latentLab.textLab.repeng.testSubtitle') }}</p>
          <div class="tool-inputs">
            <label class="control-label">
              {{ t('latentLab.textLab.repeng.testPromptLabel') }}
              <input
                v-model="repTestText"
                type="text"
                class="control-input"
                :placeholder="t('latentLab.textLab.repeng.testPromptPlaceholder')"
                :disabled="repGenerating"
              />
            </label>
            <div class="control-row">
              <label class="control-label control-small">
                {{ t('latentLab.textLab.repeng.alphaLabel') }}: {{ repAlpha.toFixed(1) }}
                <input v-model.number="repAlpha" type="range" min="-3" max="3" step="0.1" class="control-range" />
                <div class="control-hint">{{ t('latentLab.textLab.repeng.alphaHint') }}</div>
              </label>
              <label class="control-label control-small">
                {{ t('latentLab.textLab.repeng.temperatureLabel') }}: {{ repTemp.toFixed(1) }}
                <input v-model.number="repTemp" type="range" min="0.1" max="2.0" step="0.1" class="control-range" />
                <div class="control-hint">{{ t('latentLab.textLab.temperatureHint') }}</div>
              </label>
              <label class="control-label control-small">
                {{ t('latentLab.textLab.repeng.maxTokensLabel') }}: {{ repMaxTokens }}
                <input v-model.number="repMaxTokens" type="range" min="10" max="200" step="10" class="control-range" />
                <div class="control-hint">{{ t('latentLab.textLab.maxTokensHint') }}</div>
              </label>
              <label class="control-label control-small">
                {{ t('latentLab.textLab.repeng.seedLabel') }}
                <input v-model.number="repSeed" type="number" min="-1" class="control-input control-narrow" />
                <div class="control-hint">{{ t('latentLab.textLab.textSeedHint') }}</div>
              </label>
            </div>
            <button
              class="action-btn"
              :disabled="!repTestText.trim() || repGenerating"
              @click="runRepGeneration"
            >
              <span v-if="repGenerating" class="spinner"></span>
              <span v-else>{{ t('latentLab.textLab.repeng.generateBtn') }}</span>
            </button>
          </div>

          <!-- Generation Results -->
          <div v-if="repGenResult" class="generation-comparison">
            <div class="gen-column">
              <div class="gen-label">{{ t('latentLab.textLab.repeng.baselineLabel') }}</div>
              <div class="gen-text">{{ repGenResult.baseline_text }}</div>
            </div>
            <div class="gen-column manipulated">
              <div class="gen-label">{{ t('latentLab.textLab.repeng.manipulatedLabel', { alpha: repGenResult.alpha?.toFixed(1) }) }}</div>
              <div class="gen-text">{{ repGenResult.manipulated_text }}</div>
            </div>
          </div>

          <!-- LLM Interpretation -->
          <div v-if="repGenResult" class="bias-interpretation">
            <h4 class="subsection-title">{{ t('latentLab.textLab.repeng.interpretationTitle') }}</h4>
            <div v-if="repInterpreting" class="interpretation-loading">
              <span class="spinner"></span>
              <span class="interpretation-loading-text">{{ t('latentLab.textLab.repeng.interpreting') }}</span>
            </div>
            <div v-else-if="repInterpretation" class="interpretation-text">{{ repInterpretation }}</div>
            <div v-else-if="repInterpretationError" class="interpretation-error">{{ t('latentLab.textLab.repeng.interpretationError') }}</div>
          </div>
        </div>
      </section>
    </template>

    <!-- ================================================================ -->
    <!-- TAB 2: Model Comparison -->
    <!-- ================================================================ -->
    <template v-if="activeTab === 'compare'">
      <section class="tool-section">
        <h3 class="section-title">{{ t('latentLab.textLab.compare.title') }}</h3>
        <p class="section-subtitle">{{ t('latentLab.textLab.compare.subtitle') }}</p>
        <details class="science-details">
          <summary class="science-toggle">Belinkov 2022 + Olsson et al. 2022</summary>
          <p class="science-text">{{ t('latentLab.textLab.compare.science') }}</p>
        </details>

        <!-- Model A (from shared preset selector) -->
        <div class="subsection model-a-panel">
          <h4 class="subsection-title">{{ t('latentLab.textLab.compare.modelATitle') }}</h4>
          <div class="model-status">
            <span class="status-text">
              <strong>{{ selectedPreset }}</strong>
              <template v-if="presets[selectedPreset]">
                ({{ presets[selectedPreset]?.vram_gb }}GB) — {{ presets[selectedPreset]?.description }}
              </template>
            </span>
            <span class="model-a-hint">{{ t('latentLab.textLab.compare.modelAHint') }}</span>
          </div>
        </div>

        <!-- Model B Selector -->
        <div class="subsection model-b-panel">
          <h4 class="subsection-title">{{ t('latentLab.textLab.compare.modelBTitle') }}</h4>
          <div class="control-row">
            <label class="control-label">
              {{ t('latentLab.textLab.compare.modelBPresetLabel') }}
              <select v-model="cmpPresetB" class="control-select" :disabled="cmpLoadingB">
                <option value="">{{ t('latentLab.textLab.modelPanel.presetNone') }}</option>
                <option v-for="(info, key) in presets" :key="key" :value="key">
                  {{ key }} ({{ info.vram_gb }}GB) — {{ info.description }}
                </option>
              </select>
            </label>
            <label v-if="!cmpPresetB" class="control-label">
              {{ t('latentLab.textLab.compare.modelBCustomLabel') }}
              <input
                v-model="cmpCustomB"
                type="text"
                class="control-input"
                :placeholder="t('latentLab.textLab.compare.modelBCustomPlaceholder')"
                :disabled="cmpLoadingB"
              />
            </label>
            <button
              class="action-btn"
              :disabled="!cmpModelBId || cmpLoadingB"
              @click="loadModelB"
            >
              <span v-if="cmpLoadingB" class="spinner"></span>
              <span v-else>{{ t('latentLab.textLab.compare.modelBLoadBtn') }}</span>
            </button>
          </div>
          <div class="model-status">
            <template v-if="loadedModelB">
              <span class="status-dot loaded"></span>
              <span class="status-text">
                {{ t('latentLab.textLab.compare.modelBLoaded') }}:
                <strong>{{ loadedModelB.model_id }}</strong>
                ({{ loadedModelB.quantization }}) — {{ loadedModelB.vram_mb }}MB
              </span>
            </template>
            <template v-else>
              <span class="status-dot"></span>
              <span class="status-text muted">{{ t('latentLab.textLab.compare.modelBNone') }}</span>
            </template>
          </div>
        </div>

        <!-- Compare Controls -->
        <div class="tool-inputs">
          <label class="control-label">
            {{ t('latentLab.textLab.compare.promptLabel') }}
            <input
              v-model="cmpText"
              type="text"
              class="control-input"
              :placeholder="t('latentLab.textLab.compare.promptPlaceholder')"
              :disabled="cmpLoading"
            />
          </label>
          <div class="control-row">
            <label class="control-label control-small">
              {{ t('latentLab.textLab.compare.seedLabel') }}
              <input v-model.number="cmpSeed" type="number" min="0" class="control-input control-narrow" />
              <div class="control-hint">{{ t('latentLab.textLab.textSeedHint') }}</div>
            </label>
            <label class="control-label control-small">
              {{ t('latentLab.textLab.compare.temperatureLabel') }}: {{ cmpTemp.toFixed(1) }}
              <input v-model.number="cmpTemp" type="range" min="0.1" max="2.0" step="0.1" class="control-range" />
              <div class="control-hint">{{ t('latentLab.textLab.temperatureHint') }}</div>
            </label>
            <label class="control-label control-small">
              {{ t('latentLab.textLab.compare.maxTokensLabel') }}: {{ cmpMaxTokens }}
              <input v-model.number="cmpMaxTokens" type="range" min="10" max="200" step="10" class="control-range" />
              <div class="control-hint">{{ t('latentLab.textLab.maxTokensHint') }}</div>
            </label>
            <button
              class="action-btn"
              :disabled="!cmpText.trim() || !loadedModelB || cmpLoading"
              @click="runComparison"
            >
              <span v-if="cmpLoading" class="spinner"></span>
              <span v-else>{{ t('latentLab.textLab.compare.compareBtn') }}</span>
            </button>
          </div>
        </div>

        <!-- CKA Heatmap -->
        <div v-if="cmpResult" class="compare-results">
          <div class="subsection">
            <h4 class="subsection-title">{{ t('latentLab.textLab.compare.heatmapTitle') }}</h4>
            <div class="heatmap-container">
              <canvas ref="ckaCanvas" class="cka-canvas" @mousemove="onCkaHover" @mouseleave="ckaTooltip = ''"></canvas>
              <div v-if="ckaTooltip" class="canvas-tooltip" :style="ckaTooltipStyle">{{ ckaTooltip }}</div>
            </div>
            <p class="legend-text">{{ t('latentLab.textLab.compare.heatmapExplain') }}</p>
          </div>

          <!-- Generation Comparison -->
          <div class="subsection">
            <h4 class="subsection-title">{{ t('latentLab.textLab.compare.generationTitle') }}</h4>
            <div class="generation-comparison">
              <div class="gen-column">
                <div class="gen-label">{{ t('latentLab.textLab.compare.modelALabel') }}: {{ cmpResult.model_a.model_id }}</div>
                <div class="gen-text">{{ cmpResult.model_a.generated_text }}</div>
              </div>
              <div class="gen-column">
                <div class="gen-label">{{ t('latentLab.textLab.compare.modelBLabel') }}: {{ cmpResult.model_b.model_id }}</div>
                <div class="gen-text">{{ cmpResult.model_b.generated_text }}</div>
              </div>
            </div>
          </div>

          <!-- LLM Interpretation -->
          <div class="bias-interpretation">
            <h4 class="subsection-title">{{ t('latentLab.textLab.compare.interpretationTitle') }}</h4>
            <div v-if="cmpInterpreting" class="interpretation-loading">
              <span class="spinner"></span>
              <span class="interpretation-loading-text">{{ t('latentLab.textLab.compare.interpreting') }}</span>
            </div>
            <div v-else-if="cmpInterpretation" class="interpretation-text">{{ cmpInterpretation }}</div>
            <div v-else-if="cmpInterpretationError" class="interpretation-error">{{ t('latentLab.textLab.compare.interpretationError') }}</div>
          </div>
        </div>
      </section>
    </template>

    <!-- ================================================================ -->
    <!-- TAB 3: Bias Archaeology -->
    <!-- ================================================================ -->
    <template v-if="activeTab === 'bias'">
      <section class="tool-section">
        <h3 class="section-title">{{ t('latentLab.textLab.bias.title') }}</h3>
        <p class="section-subtitle">{{ t('latentLab.textLab.bias.subtitle') }}</p>
        <details class="science-details">
          <summary class="science-toggle">Zou et al. 2023 + Bricken et al. 2023</summary>
          <p class="science-text">{{ t('latentLab.textLab.bias.science') }}</p>
        </details>

        <div class="tool-inputs">
          <!-- Bias Type Selector -->
          <label class="control-label">
            {{ t('latentLab.textLab.bias.presetLabel') }}
            <select v-model="biasType" class="control-select" :disabled="biasLoading">
              <option value="gender">{{ t('latentLab.textLab.bias.presetGender') }}</option>
              <option value="sentiment">{{ t('latentLab.textLab.bias.presetSentiment') }}</option>
              <option value="domain">{{ t('latentLab.textLab.bias.presetDomain') }}</option>
              <option value="custom">{{ t('latentLab.textLab.bias.presetCustom') }}</option>
            </select>
          </label>

          <!-- Bias Description -->
          <p v-if="biasType === 'gender'" class="section-explain">{{ t('latentLab.textLab.bias.genderDesc') }}</p>
          <p v-if="biasType === 'sentiment'" class="section-explain">{{ t('latentLab.textLab.bias.sentimentDesc') }}</p>
          <p v-if="biasType === 'domain'" class="section-explain">{{ t('latentLab.textLab.bias.domainDesc') }}</p>

          <!-- Custom Tokens -->
          <template v-if="biasType === 'custom'">
            <div class="control-row">
              <label class="control-label">
                {{ t('latentLab.textLab.bias.customBoostLabel') }}
                <input
                  v-model="biasCustomBoost"
                  type="text"
                  class="control-input"
                  :placeholder="t('latentLab.textLab.bias.customBoostPlaceholder')"
                  :disabled="biasLoading"
                />
              </label>
              <label class="control-label">
                {{ t('latentLab.textLab.bias.customSuppressLabel') }}
                <input
                  v-model="biasCustomSuppress"
                  type="text"
                  class="control-input"
                  :placeholder="t('latentLab.textLab.bias.customSuppressPlaceholder')"
                  :disabled="biasLoading"
                />
              </label>
            </div>
          </template>

          <!-- Prompt + Controls -->
          <label class="control-label">
            {{ t('latentLab.textLab.bias.promptLabel') }}
            <input
              v-model="biasPrompt"
              type="text"
              class="control-input"
              :placeholder="t('latentLab.textLab.bias.promptPlaceholder')"
              :disabled="biasLoading"
            />
          </label>
          <div class="control-row">
            <label class="control-label control-small">
              {{ t('latentLab.textLab.bias.numSamplesLabel') }}: {{ biasSamples }}
              <input v-model.number="biasSamples" type="range" min="1" max="5" class="control-range" />
            </label>
            <label class="control-label control-small">
              {{ t('latentLab.textLab.bias.temperatureLabel') }}: {{ biasTemp.toFixed(1) }}
              <input v-model.number="biasTemp" type="range" min="0.1" max="2.0" step="0.1" class="control-range" />
              <div class="control-hint">{{ t('latentLab.textLab.temperatureHint') }}</div>
            </label>
            <label class="control-label control-small">
              {{ t('latentLab.textLab.bias.maxTokensLabel') }}: {{ biasMaxTokens }}
              <input v-model.number="biasMaxTokens" type="range" min="10" max="200" step="10" class="control-range" />
              <div class="control-hint">{{ t('latentLab.textLab.maxTokensHint') }}</div>
            </label>
            <label class="control-label control-small">
              {{ t('latentLab.textLab.bias.seedLabel') }}
              <input v-model.number="biasSeed" type="number" min="0" class="control-input control-narrow" />
              <div class="control-hint">{{ t('latentLab.textLab.textSeedHint') }}</div>
            </label>
          </div>
          <button
            class="action-btn"
            :disabled="!biasPrompt.trim() || biasLoading"
            @click="runBiasProbe"
          >
            <span v-if="biasLoading" class="spinner"></span>
            <span v-else>{{ t('latentLab.textLab.bias.runBtn') }}</span>
          </button>
        </div>

        <!-- Bias Results -->
        <div v-if="biasResult" class="bias-results">
          <!-- Baseline -->
          <div class="bias-group">
            <h4 class="bias-group-title">{{ t('latentLab.textLab.bias.baselineTitle') }}</h4>
            <div v-for="s in biasResult.baseline" :key="s.seed" class="bias-sample">
              <span class="sample-seed">{{ t('latentLab.textLab.bias.sampleSeedLabel') }}: {{ s.seed }}</span>
              <div class="sample-text">{{ s.text }}</div>
            </div>
          </div>

          <!-- Manipulation Groups -->
          <div v-for="group in biasResult.groups" :key="group.group_name" class="bias-group">
            <h4 class="bias-group-title">
              {{ t('latentLab.textLab.bias.groupTitle', { name: group.group_name }) }}
              <span class="group-mode">({{ group.mode === 'suppress' ? t('latentLab.textLab.bias.modeSuppress') : t('latentLab.textLab.bias.modeBoost') }})</span>
            </h4>
            <div class="group-tokens">
              {{ t('latentLab.textLab.bias.tokensLabel') }}: <code>{{ group.tokens.join(', ') }}</code>
            </div>
            <div v-for="s in group.samples" :key="s.seed" class="bias-sample">
              <span class="sample-seed">{{ t('latentLab.textLab.bias.sampleSeedLabel') }}: {{ s.seed }}</span>
              <div class="sample-text">{{ s.text }}</div>
            </div>
          </div>

          <!-- LLM Interpretation -->
          <div class="bias-interpretation">
            <h4 class="subsection-title">{{ t('latentLab.textLab.bias.interpretationTitle') }}</h4>
            <div v-if="biasInterpreting" class="interpretation-loading">
              <span class="spinner"></span>
              <span class="interpretation-loading-text">{{ t('latentLab.textLab.bias.interpreting') }}</span>
            </div>
            <div v-else-if="biasInterpretation" class="interpretation-text">{{ biasInterpretation }}</div>
            <div v-else-if="biasInterpretationError" class="interpretation-error">{{ t('latentLab.textLab.bias.interpretationError') }}</div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const apiBase = import.meta.env.DEV ? 'http://localhost:17802' : ''

// =========================================================================
// Error handling
// =========================================================================
const errorMessage = ref('')

function showError(msg: string) {
  errorMessage.value = msg
  setTimeout(() => { if (errorMessage.value === msg) errorMessage.value = '' }, 8000)
}

// =========================================================================
// Tabs
// =========================================================================
const tabs = [
  { id: 'repeng', labelKey: 'latentLab.textLab.tabs.repeng' },
  { id: 'compare', labelKey: 'latentLab.textLab.tabs.compare' },
  { id: 'bias', labelKey: 'latentLab.textLab.tabs.bias' },
] as const

type TabId = typeof tabs[number]['id']
const activeTab = ref<TabId>('repeng')

// =========================================================================
// A. Model Management (shared across tabs)
// =========================================================================
interface ModelInfo {
  model_id: string
  quantization: string
  vram_mb: number
  in_use?: boolean
}

interface PresetInfo {
  id: string
  vram_gb: number
  description: string
}

const presets = ref<Record<string, PresetInfo>>({})
const selectedPreset = ref('small')
const customModelId = ref('')
const quantization = ref('')

const activeModelId = computed(() => {
  const preset = selectedPreset.value ? presets.value[selectedPreset.value] : undefined
  if (preset) return preset.id
  return customModelId.value.trim()
})

async function fetchPresets() {
  try {
    const resp = await fetch(`${apiBase}/api/text/presets`)
    if (resp.ok) {
      const data = await resp.json()
      presets.value = data.presets || {}
    }
  } catch { /* GPU service may not be running */ }
}

// =========================================================================
// TAB 1: Representation Engineering
// =========================================================================
interface RepResult {
  explained_variance: number
  embedding_dim: number
  num_layers: number
  direction_norm: number
  pair_projections: Array<{ positive: string; negative: string; projection: number }>
  test_text?: string
  test_projection?: number
  baseline_text?: string
  manipulated_text?: string
  alpha?: number
  seed?: number
}

const contrastPairs = ref([
  { positive: 'The capital of France is Paris', negative: 'The capital of France is Berlin' },
  { positive: 'Water boils at 100 degrees Celsius', negative: 'Water boils at 50 degrees Celsius' },
  { positive: 'The earth orbits the sun', negative: 'The sun orbits the earth' },
])
const repTargetLayer = ref(-1)
const repLayerCount = ref(32)
const repLoading = ref(false)
const repResult = ref<RepResult | null>(null)

// Test generation state
const repTestText = ref('The capital of Germany is')
const repAlpha = ref(-1.0)
const repTemp = ref(0.7)
const repMaxTokens = ref(50)
const repSeed = ref(-1)
const repGenerating = ref(false)
const repGenResult = ref<RepResult | null>(null)
const repInterpretation = ref<string | null>(null)
const repInterpreting = ref(false)
const repInterpretationError = ref(false)

const hasValidPairs = computed(() =>
  contrastPairs.value.some(p => p.positive.trim() && p.negative.trim())
)

function projectionBarStyle(projection: number): Record<string, string> {
  // Map projection to a bar centered at 50%
  const maxProj = Math.max(
    ...((repResult.value?.pair_projections || []).map(p => Math.abs(p.projection))),
    0.01
  )
  const pct = (projection / maxProj) * 45
  if (pct >= 0) {
    return { left: '50%', width: pct + '%', background: 'rgba(74, 222, 128, 0.5)' }
  } else {
    return { left: (50 + pct) + '%', width: Math.abs(pct) + '%', background: 'rgba(248, 113, 113, 0.5)' }
  }
}

async function findDirection() {
  if (!hasValidPairs.value || !activeModelId.value || repLoading.value) return
  repLoading.value = true
  errorMessage.value = ''
  repGenResult.value = null

  const validPairs = contrastPairs.value.filter(p => p.positive.trim() && p.negative.trim())

  try {
    const resp = await fetch(`${apiBase}/api/text/rep-engineering`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contrast_pairs: validPairs,
        model_id: activeModelId.value,
        target_layer: repTargetLayer.value,
      }),
    })
    const data = await resp.json()
    if (data.error) {
      showError(data.error)
    } else {
      repResult.value = data
      if (data.num_layers) repLayerCount.value = data.num_layers
    }
  } catch {
    showError(t('latentLab.textLab.error.operationFailed'))
  } finally {
    repLoading.value = false
  }
}

async function interpretRepEngResults(data: RepResult) {
  repInterpretation.value = null
  repInterpretationError.value = false
  repInterpreting.value = true
  try {
    const resp = await fetch(`${apiBase}/api/text/interpret`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ results: data, experiment_type: 'repeng' }),
    })
    const result = await resp.json()
    if (result.error) {
      repInterpretationError.value = true
    } else {
      repInterpretation.value = result.interpretation
    }
  } catch {
    repInterpretationError.value = true
  } finally {
    repInterpreting.value = false
  }
}

async function runRepGeneration() {
  if (!repTestText.value.trim() || !activeModelId.value || repGenerating.value) return
  repGenerating.value = true
  errorMessage.value = ''
  repInterpretation.value = null
  repInterpretationError.value = false

  const validPairs = contrastPairs.value.filter(p => p.positive.trim() && p.negative.trim())

  try {
    const resp = await fetch(`${apiBase}/api/text/rep-engineering`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contrast_pairs: validPairs,
        model_id: activeModelId.value,
        target_layer: repTargetLayer.value,
        test_text: repTestText.value,
        alpha: repAlpha.value,
        max_new_tokens: repMaxTokens.value,
        temperature: repTemp.value,
        seed: repSeed.value,
      }),
    })
    const data = await resp.json()
    if (data.error) {
      showError(data.error)
    } else {
      repGenResult.value = data
      interpretRepEngResults(data)
    }
  } catch {
    showError(t('latentLab.textLab.error.operationFailed'))
  } finally {
    repGenerating.value = false
  }
}

// =========================================================================
// TAB 2: Model Comparison
// =========================================================================
interface CompareResult {
  text: string
  model_a: {
    model_id: string
    num_layers: number
    dim: number
    generated_text: string
    attention: { tokens: string[]; attention: number[][] }
    layer_stats: Array<{ layer: number; l2_norm: number; mean: number; std: number }>
  }
  model_b: {
    model_id: string
    num_layers: number
    dim: number
    generated_text: string
    attention: { tokens: string[]; attention: number[][] }
    layer_stats: Array<{ layer: number; l2_norm: number; mean: number; std: number }>
  }
  similarity_matrix: number[][]
  layer_indices_a: number[]
  layer_indices_b: number[]
  seed: number
}

const cmpPresetB = ref('')
const cmpCustomB = ref('')
const cmpLoadingB = ref(false)
const loadedModelB = ref<ModelInfo | null>(null)
const cmpText = ref('')
const cmpSeed = ref(42)
const cmpTemp = ref(0.7)
const cmpMaxTokens = ref(50)
const cmpLoading = ref(false)
const cmpResult = ref<CompareResult | null>(null)
const cmpInterpretation = ref<string | null>(null)
const cmpInterpreting = ref(false)
const cmpInterpretationError = ref(false)
const ckaCanvas = ref<HTMLCanvasElement | null>(null)
const ckaTooltip = ref('')
const ckaTooltipStyle = ref<Record<string, string>>({})

const cmpModelBId = computed(() => {
  const preset = cmpPresetB.value ? presets.value[cmpPresetB.value] : undefined
  if (preset) return preset.id
  return cmpCustomB.value.trim()
})

async function loadModelB() {
  if (!cmpModelBId.value || cmpLoadingB.value) return
  cmpLoadingB.value = true
  errorMessage.value = ''
  try {
    const resp = await fetch(`${apiBase}/api/text/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_id: cmpModelBId.value,
        quantization: quantization.value || undefined,
      }),
    })
    const data = await resp.json()
    if (data.error) {
      showError(data.error)
    } else {
      loadedModelB.value = {
        model_id: data.model_id,
        quantization: data.quantization,
        vram_mb: data.vram_mb,
      }
    }
  } catch {
    showError(t('latentLab.textLab.error.gpuUnreachable'))
  } finally {
    cmpLoadingB.value = false
  }
}

async function interpretCompareResults(data: CompareResult) {
  cmpInterpretation.value = null
  cmpInterpretationError.value = false
  cmpInterpreting.value = true
  try {
    const resp = await fetch(`${apiBase}/api/text/interpret`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ results: data, experiment_type: 'compare' }),
    })
    const result = await resp.json()
    if (result.error) {
      cmpInterpretationError.value = true
    } else {
      cmpInterpretation.value = result.interpretation
    }
  } catch {
    cmpInterpretationError.value = true
  } finally {
    cmpInterpreting.value = false
  }
}

async function runComparison() {
  if (!cmpText.value.trim() || !activeModelId.value || !loadedModelB.value || cmpLoading.value) return
  cmpLoading.value = true
  errorMessage.value = ''
  cmpInterpretation.value = null
  cmpInterpretationError.value = false
  try {
    const resp = await fetch(`${apiBase}/api/text/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: cmpText.value,
        model_id_a: activeModelId.value,
        model_id_b: loadedModelB.value.model_id,
        max_new_tokens: cmpMaxTokens.value,
        temperature: cmpTemp.value,
        seed: cmpSeed.value,
      }),
    })
    const data = await resp.json()
    if (data.error) {
      showError(data.error)
    } else {
      cmpResult.value = data
      await nextTick()
      drawCkaHeatmap()
      interpretCompareResults(data)
    }
  } catch {
    showError(t('latentLab.textLab.error.operationFailed'))
  } finally {
    cmpLoading.value = false
  }
}

function drawCkaHeatmap() {
  const canvas = ckaCanvas.value
  const data = cmpResult.value
  if (!canvas || !data) return

  const matrix = data.similarity_matrix
  const nA = matrix.length
  const nB = matrix[0]?.length ?? 0
  if (nA === 0 || nB === 0) return

  const cellSize = Math.max(8, Math.min(24, Math.floor(500 / Math.max(nA, nB))))
  const labelMargin = 50
  const w = labelMargin + nB * cellSize
  const h = labelMargin + nA * cellSize

  canvas.width = w
  canvas.height = h
  canvas.style.width = w + 'px'
  canvas.style.height = h + 'px'

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.fillStyle = '#0a0a0a'
  ctx.fillRect(0, 0, w, h)

  // Draw cells
  for (let r = 0; r < nA; r++) {
    for (let c = 0; c < nB; c++) {
      const val = matrix[r]?.[c] ?? 0
      const intensity = Math.pow(Math.max(0, Math.min(1, val)), 0.7)
      const red = Math.round(102 * intensity)
      const green = Math.round(126 * intensity)
      const blue = Math.round(234 * intensity)
      ctx.fillStyle = `rgb(${red}, ${green}, ${blue})`
      ctx.fillRect(labelMargin + c * cellSize, labelMargin + r * cellSize, cellSize - 1, cellSize - 1)
    }
  }

  // Axis labels
  ctx.fillStyle = 'rgba(255,255,255,0.5)'
  ctx.font = `${Math.min(10, cellSize - 2)}px monospace`
  ctx.textAlign = 'right'
  ctx.textBaseline = 'middle'

  const stepLabelA = Math.max(1, Math.floor(nA / 8))
  for (let r = 0; r < nA; r += stepLabelA) {
    ctx.fillText(
      String(data.layer_indices_a[r] ?? r),
      labelMargin - 4,
      labelMargin + r * cellSize + cellSize / 2
    )
  }

  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  const stepLabelB = Math.max(1, Math.floor(nB / 8))
  for (let c = 0; c < nB; c += stepLabelB) {
    ctx.fillText(
      String(data.layer_indices_b[c] ?? c),
      labelMargin + c * cellSize + cellSize / 2,
      labelMargin + nA * cellSize + 4
    )
  }

  // Axis titles
  ctx.font = '10px sans-serif'
  ctx.fillStyle = 'rgba(255,255,255,0.4)'
  ctx.save()
  ctx.translate(12, labelMargin + (nA * cellSize) / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.fillText(t('latentLab.textLab.compare.heatmapAxisA'), 0, 0)
  ctx.restore()
  ctx.textAlign = 'center'
  ctx.fillText(t('latentLab.textLab.compare.heatmapAxisB'), labelMargin + (nB * cellSize) / 2, labelMargin + nA * cellSize + 18)
}

function onCkaHover(event: MouseEvent) {
  const canvas = ckaCanvas.value
  const data = cmpResult.value
  if (!canvas || !data) return

  const matrix = data.similarity_matrix
  const nA = matrix.length
  const nB = matrix[0]?.length ?? 0
  const cellSize = Math.max(8, Math.min(24, Math.floor(500 / Math.max(nA, nB))))
  const labelMargin = 50

  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const col = Math.floor((x - labelMargin) / cellSize)
  const row = Math.floor((y - labelMargin) / cellSize)

  if (row >= 0 && row < nA && col >= 0 && col < nB) {
    const val = matrix[row]?.[col] ?? 0
    const layerA = data.layer_indices_a[row] ?? row
    const layerB = data.layer_indices_b[col] ?? col
    ckaTooltip.value = `A:${layerA} / B:${layerB} = ${val.toFixed(3)}`
    ckaTooltipStyle.value = {
      left: (event.clientX - rect.left + 12) + 'px',
      top: (event.clientY - rect.top - 24) + 'px',
    }
  } else {
    ckaTooltip.value = ''
  }
}

// =========================================================================
// TAB 3: Bias Archaeology
// =========================================================================
interface BiasSample {
  seed: number
  text: string
}
interface BiasGroup {
  group_name: string
  tokens: string[]
  mode: string
  samples: BiasSample[]
}
interface BiasResult {
  model_id: string
  prompt: string
  bias_type: string
  baseline: BiasSample[]
  groups: BiasGroup[]
}

const biasType = ref('gender')
const biasPrompt = ref('')
const biasCustomBoost = ref('')
const biasCustomSuppress = ref('')
const biasSamples = ref(3)
const biasTemp = ref(0.7)
const biasMaxTokens = ref(50)
const biasSeed = ref(42)
const biasLoading = ref(false)
const biasResult = ref<BiasResult | null>(null)
const biasInterpretation = ref<string | null>(null)
const biasInterpreting = ref(false)
const biasInterpretationError = ref(false)

async function interpretBiasResults(data: BiasResult) {
  biasInterpretation.value = null
  biasInterpretationError.value = false
  biasInterpreting.value = true
  try {
    const resp = await fetch(`${apiBase}/api/text/interpret`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ results: data, experiment_type: 'bias' }),
    })
    const result = await resp.json()
    if (result.error) {
      biasInterpretationError.value = true
    } else {
      biasInterpretation.value = result.interpretation
    }
  } catch {
    biasInterpretationError.value = true
  } finally {
    biasInterpreting.value = false
  }
}

async function runBiasProbe() {
  if (!biasPrompt.value.trim() || !activeModelId.value || biasLoading.value) return
  biasLoading.value = true
  errorMessage.value = ''
  biasResult.value = null
  biasInterpretation.value = null
  biasInterpretationError.value = false

  const payload: Record<string, unknown> = {
    prompt: biasPrompt.value,
    model_id: activeModelId.value,
    bias_type: biasType.value,
    num_samples: biasSamples.value,
    temperature: biasTemp.value,
    max_new_tokens: biasMaxTokens.value,
    seed: biasSeed.value,
  }

  if (biasType.value === 'custom') {
    const boost = biasCustomBoost.value.split(',').map(s => s.trim()).filter(Boolean)
    const suppress = biasCustomSuppress.value.split(',').map(s => s.trim()).filter(Boolean)
    if (boost.length) payload.custom_boost = boost
    if (suppress.length) payload.custom_suppress = suppress
  }

  try {
    const resp = await fetch(`${apiBase}/api/text/bias-probe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await resp.json()
    if (data.error) {
      showError(data.error)
    } else {
      biasResult.value = data
      interpretBiasResults(data)
    }
  } catch {
    showError(t('latentLab.textLab.error.operationFailed'))
  } finally {
    biasLoading.value = false
  }
}

// =========================================================================
// Lifecycle
// =========================================================================
onMounted(() => {
  fetchPresets()
})
</script>

<style scoped>
.latent-text-lab {
  padding: 1rem 2rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header { text-align: center; margin-bottom: 2rem; }
.page-title { font-size: 1.4rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 0.5rem; }
.page-subtitle { font-size: 0.9rem; color: rgba(255, 255, 255, 0.5); max-width: 700px; margin: 0 auto 1rem; line-height: 1.5; }
.explanation-details { text-align: left; max-width: 700px; margin: 0 auto; }
.explanation-details summary { cursor: pointer; color: rgba(102, 126, 234, 0.7); font-size: 0.85rem; text-align: center; }
.explanation-body { margin-top: 0.75rem; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.06); }
.explanation-section { margin-bottom: 1rem; }
.explanation-section:last-child { margin-bottom: 0; }
.explanation-section h4 { color: rgba(255, 255, 255, 0.7); font-size: 0.85rem; margin-bottom: 0.3rem; }
.explanation-section p { color: rgba(255, 255, 255, 0.45); font-size: 0.8rem; line-height: 1.6; }

/* Error banner */
.error-banner { background: rgba(220, 38, 38, 0.15); border: 1px solid rgba(220, 38, 38, 0.3); color: #fca5a5; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1.5rem; cursor: pointer; font-size: 0.85rem; }

/* Model selector row */
.model-selector-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Tab navigation */
.tab-nav {
  display: flex;
  gap: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.tab-btn {
  padding: 0.75rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}
.tab-btn:hover { color: rgba(255, 255, 255, 0.7); }
.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

/* Tool sections */
.tool-section { margin-bottom: 2rem; padding: 1.25rem; background: rgba(255, 255, 255, 0.02); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.06); }
.section-title { font-size: 1.05rem; color: rgba(255, 255, 255, 0.85); margin-bottom: 0.25rem; }
.section-subtitle { font-size: 0.8rem; color: rgba(255, 255, 255, 0.4); margin-bottom: 0.5rem; }
.section-explain { font-size: 0.8rem; color: rgba(255, 255, 255, 0.35); line-height: 1.6; margin-bottom: 1rem; max-width: 700px; }

/* Science details */
.science-details { margin-bottom: 1rem; }
.science-toggle { cursor: pointer; color: rgba(102, 126, 234, 0.6); font-size: 0.8rem; font-style: italic; }
.science-text { margin-top: 0.5rem; font-size: 0.8rem; color: rgba(255, 255, 255, 0.4); line-height: 1.6; padding: 0.75rem; background: rgba(255, 255, 255, 0.02); border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.04); }

/* Subsections */
.subsection { margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.06); }
.subsection-title { font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem; }
.subsection-subtitle { font-size: 0.8rem; color: rgba(255, 255, 255, 0.35); margin-bottom: 0.75rem; }

/* Controls */
.tool-inputs { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1rem; }
.control-row { display: flex; gap: 0.75rem; align-items: flex-end; flex-wrap: wrap; }
.control-label { display: flex; flex-direction: column; gap: 0.3rem; color: rgba(255, 255, 255, 0.6); font-size: 0.8rem; flex: 1; min-width: 140px; }
.control-small { flex: 0 1 180px; }
.control-input { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: #fff; padding: 0.5rem 0.75rem; font-size: 0.85rem; font-family: inherit; }
.control-input:focus { outline: none; border-color: rgba(102, 126, 234, 0.5); }
.control-narrow { width: 80px; flex: none; }
.control-select { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: #fff; padding: 0.5rem 0.75rem; font-size: 0.85rem; font-family: inherit; }
.control-select option { background: #1a1a1a; color: #fff; }
.control-range { width: 100%; accent-color: #667eea; }

.model-status { display: flex; align-items: center; gap: 0.5rem; margin-left: auto; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255, 255, 255, 0.2); flex-shrink: 0; }
.status-dot.loaded { background: #4ade80; box-shadow: 0 0 6px rgba(74, 222, 128, 0.4); }
.status-text { font-size: 0.8rem; color: rgba(255, 255, 255, 0.7); }
.status-text.muted { color: rgba(255, 255, 255, 0.3); }

/* Buttons */
.action-btn { padding: 0.5rem 1.25rem; font-size: 0.85rem; font-weight: 600; border: none; border-radius: 8px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(102, 126, 234, 0.15)); color: #667eea; cursor: pointer; transition: all 0.2s ease; font-family: inherit; white-space: nowrap; flex-shrink: 0; }
.action-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
/* Spinner */
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(102, 126, 234, 0.3); border-top-color: #667eea; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Contrast Pairs */
.contrast-pairs { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }
.pair-row { display: flex; gap: 0.5rem; align-items: center; }
.pair-input { flex: 1; }
.pair-separator { color: rgba(255, 255, 255, 0.3); font-size: 0.85rem; flex-shrink: 0; }
.remove-btn { width: 28px; height: 28px; border: none; border-radius: 6px; background: rgba(220, 38, 38, 0.15); color: #f87171; cursor: pointer; font-size: 0.85rem; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.add-btn { align-self: flex-start; padding: 0.4rem 0.8rem; font-size: 0.8rem; border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 6px; background: none; color: rgba(255, 255, 255, 0.4); cursor: pointer; font-family: inherit; }
.add-btn:hover { border-color: rgba(102, 126, 234, 0.4); color: rgba(102, 126, 234, 0.7); }

/* Direction Result */
.direction-result { margin-top: 1rem; padding: 1rem; background: rgba(74, 222, 128, 0.05); border: 1px solid rgba(74, 222, 128, 0.15); border-radius: 8px; }
.result-header { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.75rem; }
.result-badge { background: rgba(74, 222, 128, 0.15); color: #4ade80; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
.result-stat { font-size: 0.8rem; color: rgba(255, 255, 255, 0.5); font-family: monospace; }

/* Projections */
.projections { margin-top: 0.75rem; }
.projection-row { margin-bottom: 0.5rem; }
.projection-bar-container { height: 16px; background: rgba(255, 255, 255, 0.04); border-radius: 3px; position: relative; overflow: hidden; }
.projection-bar { position: absolute; top: 0; height: 100%; border-radius: 3px; transition: all 0.3s ease; }
.projection-labels { display: flex; justify-content: space-between; align-items: center; margin-top: 0.2rem; font-size: 0.75rem; }
.proj-positive { color: rgba(74, 222, 128, 0.7); flex: 1; }
.proj-value { color: rgba(255, 255, 255, 0.5); font-family: monospace; text-align: center; flex: 0; padding: 0 0.5rem; }
.proj-negative { color: rgba(248, 113, 113, 0.7); flex: 1; text-align: right; }

/* Generation Comparison */
.generation-comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
.gen-column { padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.06); }
.gen-column.manipulated { border-color: rgba(102, 126, 234, 0.2); }
.gen-label { font-size: 0.75rem; color: rgba(255, 255, 255, 0.4); margin-bottom: 0.5rem; font-weight: 600; }
.gen-text { font-size: 0.85rem; color: rgba(255, 255, 255, 0.8); line-height: 1.6; white-space: pre-wrap; word-break: break-word; }

/* CKA Heatmap */
.heatmap-container { position: relative; overflow: auto; margin-bottom: 0.75rem; }
.cka-canvas { display: block; }
.canvas-tooltip { position: absolute; background: rgba(0, 0, 0, 0.85); color: #fff; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-family: monospace; pointer-events: none; white-space: nowrap; z-index: 10; }
.legend-text { font-size: 0.8rem; color: rgba(255, 255, 255, 0.4); line-height: 1.6; }

/* Model A/B Panels */
.model-a-panel { background: rgba(255, 255, 255, 0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(74, 222, 128, 0.15); }
.model-a-hint { font-size: 0.75rem; color: rgba(255, 255, 255, 0.3); margin-left: auto; font-style: italic; }
.model-b-panel { background: rgba(255, 255, 255, 0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.06); }

/* Bias Results */
.bias-results { margin-top: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.bias-group { padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.06); }
.bias-group-title { font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem; }
.group-mode { font-weight: 400; color: rgba(255, 255, 255, 0.4); font-size: 0.8rem; }
.group-tokens { font-size: 0.75rem; color: rgba(255, 255, 255, 0.35); margin-bottom: 0.75rem; }
.group-tokens code { color: rgba(102, 126, 234, 0.7); background: rgba(102, 126, 234, 0.1); padding: 0.1rem 0.3rem; border-radius: 3px; }
.bias-sample { margin-bottom: 0.5rem; padding: 0.5rem 0.75rem; background: rgba(255, 255, 255, 0.02); border-radius: 6px; }
.bias-sample:last-child { margin-bottom: 0; }
.sample-seed { font-family: monospace; font-size: 0.7rem; color: rgba(102, 126, 234, 0.6); }
.sample-text { font-size: 0.85rem; color: rgba(255, 255, 255, 0.8); line-height: 1.5; white-space: pre-wrap; word-break: break-word; margin-top: 0.25rem; }

/* Experiment Guide */
.experiment-guide { padding: 0.75rem 1rem; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; margin-bottom: 1rem; }
.guide-text { font-size: 0.8rem; color: rgba(255, 255, 255, 0.55); line-height: 1.7; }
.guide-hint { font-size: 0.75rem; color: rgba(102, 126, 234, 0.6); margin-top: 0.5rem; font-style: italic; }

/* Interpretation */
.bias-interpretation { padding: 1rem; background: rgba(102, 126, 234, 0.05); border: 1px solid rgba(102, 126, 234, 0.15); border-radius: 8px; }
.interpretation-loading { display: flex; align-items: center; gap: 0.75rem; }
.interpretation-loading-text { font-size: 0.85rem; color: rgba(255, 255, 255, 0.4); font-style: italic; }
.interpretation-text { font-size: 0.85rem; color: rgba(255, 255, 255, 0.75); line-height: 1.7; white-space: pre-wrap; }
.interpretation-error { font-size: 0.8rem; color: rgba(255, 255, 255, 0.3); font-style: italic; }

/* Responsive */
@media (max-width: 768px) {
  .latent-text-lab { padding: 1rem; }
  .control-row { flex-direction: column; }
  .control-small { flex: 1; }
  .generation-comparison { grid-template-columns: 1fr; }
  .model-status { margin-left: 0; margin-top: 0.5rem; }
  .pair-row { flex-direction: column; }
  .pair-separator { display: none; }
  .tab-nav { overflow-x: auto; }
}

.control-hint {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.7rem;
  line-height: 1.4;
}
</style>
