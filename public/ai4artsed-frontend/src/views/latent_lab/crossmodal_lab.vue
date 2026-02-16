<template>
  <div class="crossmodal-lab">
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">{{ t('latentLab.crossmodal.headerTitle') }}</h2>
      <p class="page-subtitle">{{ t('latentLab.crossmodal.headerSubtitle') }}</p>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-nav">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <span class="tab-label">{{ t(`latentLab.crossmodal.tabs.${tab.id}.label`) }}</span>
        <span class="tab-short">{{ t(`latentLab.crossmodal.tabs.${tab.id}.short`) }}</span>
      </button>
    </div>

    <!-- ===== Tab 1: Latent Audio Synth ===== -->
    <div v-if="activeTab === 'synth'" class="tab-panel">
      <h3>{{ t('latentLab.crossmodal.tabs.synth.title') }}</h3>
      <p class="tab-description">{{ t('latentLab.crossmodal.tabs.synth.description') }}</p>

      <!-- Prompt A -->
      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.synth.promptA') }}</label>
        <textarea
          v-model="synth.promptA"
          rows="2"
          class="prompt-input"
          :placeholder="t('latentLab.crossmodal.synth.promptAPlaceholder')"
        />
      </div>

      <!-- Prompt B (optional) -->
      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.synth.promptB') }}</label>
        <textarea
          v-model="synth.promptB"
          rows="2"
          class="prompt-input"
          :placeholder="t('latentLab.crossmodal.synth.promptBPlaceholder')"
        />
      </div>

      <!-- Sliders -->
      <div class="slider-group">
        <div class="slider-item">
          <div class="slider-header">
            <label>{{ t('latentLab.crossmodal.synth.alpha') }}</label>
            <span class="slider-value">{{ synth.alpha.toFixed(2) }}</span>
          </div>
          <input type="range" v-model.number="synth.alpha" min="-2" max="3" step="0.05" />
          <span class="slider-hint">{{ t('latentLab.crossmodal.synth.alphaHint') }}</span>
        </div>

        <div class="slider-item">
          <div class="slider-header">
            <label>{{ t('latentLab.crossmodal.synth.magnitude') }}</label>
            <span class="slider-value">{{ synth.magnitude.toFixed(2) }}</span>
          </div>
          <input type="range" v-model.number="synth.magnitude" min="0.1" max="5" step="0.1" />
          <span class="slider-hint">{{ t('latentLab.crossmodal.synth.magnitudeHint') }}</span>
        </div>

        <div class="slider-item">
          <div class="slider-header">
            <label>{{ t('latentLab.crossmodal.synth.noise') }}</label>
            <span class="slider-value">{{ synth.noise.toFixed(2) }}</span>
          </div>
          <input type="range" v-model.number="synth.noise" min="0" max="1" step="0.05" />
          <span class="slider-hint">{{ t('latentLab.crossmodal.synth.noiseHint') }}</span>
        </div>
      </div>

      <!-- Params row -->
      <div class="params-row">
        <div class="param">
          <label>{{ t('latentLab.crossmodal.synth.duration') }}</label>
          <input v-model.number="synth.duration" type="number" min="0.5" max="5" step="0.5" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.synth.steps') }}</label>
          <input v-model.number="synth.steps" type="number" min="10" max="100" step="5" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.synth.cfg') }}</label>
          <input v-model.number="synth.cfg" type="number" min="1" max="15" step="0.5" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.seed') }}</label>
          <input v-model.number="synth.seed" type="number" />
        </div>
      </div>

      <div class="action-row">
        <button class="generate-btn" :disabled="!synth.promptA || generating" @click="runSynth">
          {{ generating ? t('latentLab.crossmodal.generating') : t('latentLab.crossmodal.generate') }}
        </button>
        <label class="loop-toggle">
          <input type="checkbox" v-model="synth.loop" />
          {{ synth.loop ? t('latentLab.crossmodal.synth.loopOn') : t('latentLab.crossmodal.synth.loopOff') }}
        </label>
      </div>
    </div>

    <!-- ===== Tab 2: MMAudio ===== -->
    <div v-if="activeTab === 'mmaudio'" class="tab-panel">
      <h3>{{ t('latentLab.crossmodal.tabs.mmaudio.title') }}</h3>
      <p class="tab-description">{{ t('latentLab.crossmodal.tabs.mmaudio.description') }}</p>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.mmaudio.imageUpload') }}</label>
        <input type="file" accept="image/*" @change="onImageUpload" class="file-input" />
        <img v-if="imagePreview" :src="imagePreview" class="image-preview" />
      </div>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.mmaudio.prompt') }}</label>
        <textarea
          v-model="mmaudio.prompt"
          rows="2"
          class="prompt-input"
          :placeholder="t('latentLab.crossmodal.mmaudio.promptPlaceholder')"
        />
      </div>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.mmaudio.negativePrompt') }}</label>
        <input v-model="mmaudio.negativePrompt" type="text" class="text-input" />
      </div>

      <div class="params-row">
        <div class="param">
          <label>{{ t('latentLab.crossmodal.mmaudio.duration') }}</label>
          <input v-model.number="mmaudio.duration" type="number" min="1" max="8" step="1" />
          <span class="param-hint">{{ t('latentLab.crossmodal.mmaudio.maxDuration') }}</span>
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.mmaudio.cfg') }}</label>
          <input v-model.number="mmaudio.cfg" type="number" min="1" max="15" step="0.5" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.mmaudio.steps') }}</label>
          <input v-model.number="mmaudio.steps" type="number" min="10" max="50" step="5" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.seed') }}</label>
          <input v-model.number="mmaudio.seed" type="number" />
        </div>
      </div>

      <button class="generate-btn" :disabled="(!mmaudio.prompt && !imageBase64) || generating" @click="runMMAudio">
        {{ generating ? t('latentLab.crossmodal.generating') : t('latentLab.crossmodal.generate') }}
      </button>
    </div>

    <!-- ===== Tab 3: ImageBind Guidance ===== -->
    <div v-if="activeTab === 'guidance'" class="tab-panel">
      <h3>{{ t('latentLab.crossmodal.tabs.guidance.title') }}</h3>
      <p class="tab-description">{{ t('latentLab.crossmodal.tabs.guidance.description') }}</p>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.guidance.imageUpload') }}</label>
        <input type="file" accept="image/*" @change="onImageUpload" class="file-input" />
        <img v-if="imagePreview" :src="imagePreview" class="image-preview" />
      </div>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.guidance.prompt') }}</label>
        <textarea
          v-model="guidance.prompt"
          rows="2"
          class="prompt-input"
          :placeholder="t('latentLab.crossmodal.guidance.promptPlaceholder')"
        />
      </div>

      <!-- Guidance sliders -->
      <div class="slider-group">
        <div class="slider-item">
          <div class="slider-header">
            <label>{{ t('latentLab.crossmodal.guidance.lambda') }}</label>
            <span class="slider-value">{{ guidance.lambda.toFixed(3) }}</span>
          </div>
          <input type="range" v-model.number="guidance.lambda" min="0.01" max="1" step="0.01" />
          <span class="slider-hint">{{ t('latentLab.crossmodal.guidance.lambdaHint') }}</span>
        </div>

        <div class="slider-item">
          <div class="slider-header">
            <label>{{ t('latentLab.crossmodal.guidance.warmupSteps') }}</label>
            <span class="slider-value">{{ guidance.warmupSteps }}</span>
          </div>
          <input type="range" v-model.number="guidance.warmupSteps" min="5" max="30" step="1" />
          <span class="slider-hint">{{ t('latentLab.crossmodal.guidance.warmupHint') }}</span>
        </div>
      </div>

      <div class="params-row">
        <div class="param">
          <label>{{ t('latentLab.crossmodal.guidance.totalSteps') }}</label>
          <input v-model.number="guidance.totalSteps" type="number" min="20" max="150" step="10" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.guidance.duration') }}</label>
          <input v-model.number="guidance.duration" type="number" min="1" max="30" step="1" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.guidance.cfg') }}</label>
          <input v-model.number="guidance.cfg" type="number" min="1" max="15" step="0.5" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.seed') }}</label>
          <input v-model.number="guidance.seed" type="number" />
        </div>
      </div>

      <button class="generate-btn" :disabled="!imageBase64 || generating" @click="runGuidance">
        {{ generating ? t('latentLab.crossmodal.generating') : t('latentLab.crossmodal.generate') }}
      </button>
    </div>

    <!-- ===== Output Area ===== -->
    <div v-if="resultAudio || error || embeddingStats" class="output-area">
      <h3>{{ t('latentLab.crossmodal.result') }}</h3>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div v-if="resultAudio" class="output-audio-container">
        <audio
          ref="audioEl"
          :src="resultAudio"
          controls
          :loop="synth.loop && activeTab === 'synth'"
          class="output-audio"
        />
      </div>

      <div class="result-meta">
        <span v-if="resultSeed !== null" class="meta-item">{{ t('latentLab.crossmodal.seed') }}: {{ resultSeed }}</span>
        <span v-if="generationTimeMs" class="meta-item">{{ t('latentLab.crossmodal.generationTime') }}: {{ generationTimeMs }}ms</span>
        <span v-if="cosineSimilarity !== null" class="meta-item">{{ t('latentLab.crossmodal.guidance.cosineSimilarity') }}: {{ cosineSimilarity.toFixed(4) }}</span>
      </div>

      <!-- Embedding stats (synth only) -->
      <div v-if="embeddingStats" class="embedding-stats">
        <h4>{{ t('latentLab.crossmodal.synth.embeddingStats') }}</h4>
        <div class="stats-grid">
          <span>Mean: {{ embeddingStats.mean }}</span>
          <span>Std: {{ embeddingStats.std }}</span>
        </div>
        <div v-if="embeddingStats.top_dimensions" class="top-dims">
          <div
            v-for="dim in embeddingStats.top_dimensions"
            :key="dim.dim"
            class="dim-bar"
          >
            <span class="dim-label">d{{ dim.dim }}</span>
            <div class="dim-fill" :style="{ width: dimBarWidth(dim.value) }" />
            <span class="dim-value">{{ dim.value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const API_BASE = import.meta.env.DEV ? 'http://localhost:17802' : ''

type TabId = 'synth' | 'mmaudio' | 'guidance'

const tabs: { id: TabId }[] = [
  { id: 'synth' },
  { id: 'mmaudio' },
  { id: 'guidance' },
]

const activeTab = ref<TabId>('synth')
const generating = ref(false)
const error = ref('')
const resultAudio = ref('')
const resultSeed = ref<number | null>(null)
const generationTimeMs = ref<number | null>(null)
const cosineSimilarity = ref<number | null>(null)
const audioEl = ref<HTMLAudioElement | null>(null)

interface EmbeddingStats {
  mean: number
  std: number
  top_dimensions: Array<{ dim: number; value: number }>
}
const embeddingStats = ref<EmbeddingStats | null>(null)

// Image upload (shared across MMAudio and Guidance)
const imagePreview = ref('')
const imageBase64 = ref('')

// Synth params
const synth = reactive({
  promptA: '',
  promptB: '',
  alpha: 0.5,
  magnitude: 1.0,
  noise: 0.0,
  duration: 1.0,
  steps: 20,
  cfg: 3.5,
  seed: 42,
  loop: true,
})

// MMAudio params
const mmaudio = reactive({
  prompt: '',
  negativePrompt: '',
  duration: 8,
  cfg: 4.5,
  steps: 25,
  seed: 42,
})

// ImageBind Guidance params
const guidance = reactive({
  prompt: '',
  lambda: 0.1,
  warmupSteps: 10,
  totalSteps: 50,
  duration: 10,
  cfg: 7.0,
  seed: 42,
})

function clearResults() {
  error.value = ''
  resultAudio.value = ''
  resultSeed.value = null
  generationTimeMs.value = null
  cosineSimilarity.value = null
  embeddingStats.value = null
}

function onImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target?.result as string
    imagePreview.value = dataUrl
    imageBase64.value = dataUrl.split(',')[1] ?? ''
  }
  reader.readAsDataURL(file)
}

async function apiPost(path: string, body: Record<string, unknown>) {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(`Error ${resp.status}: ${text}`)
  }
  return resp.json()
}

function base64ToDataUrl(b64: string, mime: string): string {
  return `data:${mime};base64,${b64}`
}

function dimBarWidth(value: number): string {
  if (!embeddingStats.value?.top_dimensions?.length) return '0%'
  const maxVal = embeddingStats.value.top_dimensions[0].value
  return maxVal > 0 ? `${(value / maxVal) * 100}%` : '0%'
}

// ===== Synth =====
async function runSynth() {
  clearResults()
  generating.value = true
  try {
    const body: Record<string, unknown> = {
      prompt_a: synth.promptA,
      alpha: synth.alpha,
      magnitude: synth.magnitude,
      noise_sigma: synth.noise,
      duration_seconds: synth.duration,
      steps: synth.steps,
      cfg_scale: synth.cfg,
      seed: synth.seed,
    }
    if (synth.promptB.trim()) {
      body.prompt_b = synth.promptB
    }

    const result = await apiPost('/api/cross_aesthetic/synth', body)
    if (result.success) {
      resultAudio.value = base64ToDataUrl(result.audio_base64, 'audio/wav')
      resultSeed.value = result.seed
      generationTimeMs.value = result.generation_time_ms
      embeddingStats.value = result.embedding_stats
    } else {
      error.value = result.error || 'Synth generation failed'
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    generating.value = false
  }
}

// ===== MMAudio =====
async function runMMAudio() {
  clearResults()
  generating.value = true
  try {
    const body: Record<string, unknown> = {
      prompt: mmaudio.prompt,
      negative_prompt: mmaudio.negativePrompt,
      duration_seconds: mmaudio.duration,
      cfg_strength: mmaudio.cfg,
      num_steps: mmaudio.steps,
      seed: mmaudio.seed,
    }
    if (imageBase64.value) {
      body.image_base64 = imageBase64.value
    }

    const result = await apiPost('/api/cross_aesthetic/mmaudio', body)
    if (result.success) {
      resultAudio.value = base64ToDataUrl(result.audio_base64, 'audio/wav')
      resultSeed.value = result.seed
      generationTimeMs.value = result.generation_time_ms
    } else {
      error.value = result.error || 'MMAudio generation failed'
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    generating.value = false
  }
}

// ===== ImageBind Guidance =====
async function runGuidance() {
  clearResults()
  generating.value = true
  try {
    const result = await apiPost('/api/cross_aesthetic/image_guided_audio', {
      image_base64: imageBase64.value,
      prompt: guidance.prompt,
      lambda_guidance: guidance.lambda,
      warmup_steps: guidance.warmupSteps,
      total_steps: guidance.totalSteps,
      duration_seconds: guidance.duration,
      cfg_scale: guidance.cfg,
      seed: guidance.seed,
    })
    if (result.success) {
      resultAudio.value = base64ToDataUrl(result.audio_base64, 'audio/wav')
      resultSeed.value = result.seed
      generationTimeMs.value = result.generation_time_ms
      cosineSimilarity.value = result.cosine_similarity ?? null
    } else {
      error.value = result.error || 'Guided generation failed'
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.crossmodal-lab {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  color: #ffffff;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 300;
  letter-spacing: 0.05em;
  margin-bottom: 0.3rem;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.tab-btn.active {
  background: rgba(76, 175, 80, 0.1);
  border-color: rgba(76, 175, 80, 0.4);
  color: #ffffff;
}

.tab-label {
  font-size: 1rem;
  font-weight: 700;
  display: block;
  margin-bottom: 0.3rem;
}

.tab-short {
  font-size: 0.72rem;
  opacity: 0.7;
}

/* Tab Panels */
.tab-panel {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  margin-bottom: 2rem;
}

.tab-panel h3 {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.tab-description {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* Input groups */
.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.4rem;
}

.file-input {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
}

.image-preview {
  margin-top: 0.5rem;
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.prompt-input,
.text-input {
  width: 100%;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.9rem;
  resize: vertical;
  box-sizing: border-box;
}

.text-input {
  resize: none;
}

.prompt-input:focus,
.text-input:focus {
  outline: none;
  border-color: rgba(76, 175, 80, 0.5);
}

/* Slider groups */
.slider-group {
  margin-bottom: 1.5rem;
}

.slider-item {
  margin-bottom: 1rem;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}

.slider-header label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.slider-value {
  font-size: 0.8rem;
  color: #4CAF50;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.slider-item input[type="range"] {
  width: 100%;
  accent-color: #4CAF50;
}

.slider-hint {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.35);
  display: block;
  margin-top: 0.2rem;
}

/* Params row */
.params-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.param {
  flex: 1;
  min-width: 100px;
}

.param label {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.3rem;
}

.param input,
.param select {
  width: 100%;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #ffffff;
  font-size: 0.85rem;
  box-sizing: border-box;
}

.param input:focus,
.param select:focus {
  outline: none;
  border-color: rgba(76, 175, 80, 0.5);
}

.param-hint {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.3);
  display: block;
  margin-top: 0.2rem;
}

/* Action row */
.action-row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.generate-btn {
  padding: 0.8rem 2rem;
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid rgba(76, 175, 80, 0.4);
  border-radius: 8px;
  color: #4CAF50;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: rgba(76, 175, 80, 0.3);
}

.generate-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.loop-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
}

.loop-toggle input[type="checkbox"] {
  accent-color: #4CAF50;
}

/* Output area */
.output-area {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.output-area h3 {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.error-message {
  color: #ff5252;
  font-size: 0.85rem;
  padding: 0.8rem;
  background: rgba(255, 82, 82, 0.1);
  border-radius: 6px;
  margin-bottom: 1rem;
}

.output-audio-container {
  margin-bottom: 1rem;
}

.output-audio {
  width: 100%;
}

.result-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.meta-item {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
}

/* Embedding stats */
.embedding-stats {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.embedding-stats h4 {
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
}

.stats-grid {
  display: flex;
  gap: 1.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 0.8rem;
}

.top-dims {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.dim-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 1.2rem;
}

.dim-label {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.4);
  width: 2.5rem;
  text-align: right;
  flex-shrink: 0;
}

.dim-fill {
  height: 0.5rem;
  background: rgba(76, 175, 80, 0.4);
  border-radius: 2px;
  min-width: 2px;
  transition: width 0.3s;
}

.dim-value {
  font-size: 0.6rem;
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}
</style>
