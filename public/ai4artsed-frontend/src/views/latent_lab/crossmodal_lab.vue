<template>
  <div class="crossmodal-lab">
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">{{ t('latentLab.crossmodal.headerTitle') }}</h2>
      <p class="page-subtitle">{{ t('latentLab.crossmodal.headerSubtitle') }}</p>
    </div>

    <!-- Strategy Tabs -->
    <div class="strategy-tabs">
      <button
        v-for="s in strategies"
        :key="s.id"
        class="strategy-tab"
        :class="{ active: activeStrategy === s.id }"
        @click="activeStrategy = s.id"
      >
        <span class="strategy-label">{{ s.label }}</span>
        <span class="strategy-desc">{{ t(`latentLab.crossmodal.strategies.${s.id}.short`) }}</span>
      </button>
    </div>

    <!-- Strategy A: Image -> Audio -->
    <div v-if="activeStrategy === 'a'" class="strategy-panel">
      <h3>{{ t('latentLab.crossmodal.strategies.a.title') }}</h3>
      <p class="strategy-description">{{ t('latentLab.crossmodal.strategies.a.description') }}</p>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.imageUpload') }}</label>
        <input type="file" accept="image/*" @change="onImageUpload" class="file-input" />
        <img v-if="imagePreview" :src="imagePreview" class="image-preview" />
      </div>

      <div class="params-row">
        <div class="param">
          <label>{{ t('latentLab.crossmodal.duration') }}</label>
          <input v-model.number="params.duration" type="number" min="1" max="47" step="1" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.steps') }}</label>
          <input v-model.number="params.steps" type="number" min="10" max="200" step="10" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.cfg') }}</label>
          <input v-model.number="params.cfg" type="number" min="1" max="20" step="0.5" />
        </div>
        <div class="param">
          <label>Seed</label>
          <input v-model.number="params.seed" type="number" />
        </div>
      </div>

      <button class="generate-btn" :disabled="!imageBase64 || generating" @click="runStrategyA">
        {{ generating ? t('latentLab.crossmodal.generating') : t('latentLab.crossmodal.generate') }}
      </button>
    </div>

    <!-- Strategy B: Shared Seed -->
    <div v-if="activeStrategy === 'b'" class="strategy-panel">
      <h3>{{ t('latentLab.crossmodal.strategies.b.title') }}</h3>
      <p class="strategy-description">{{ t('latentLab.crossmodal.strategies.b.description') }}</p>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.prompt') }}</label>
        <textarea v-model="params.prompt" rows="3" class="prompt-input" />
      </div>

      <div class="params-row">
        <div class="param">
          <label>Seed</label>
          <input v-model.number="params.seed" type="number" />
        </div>
        <div class="param">
          <label>{{ t('latentLab.crossmodal.duration') }}</label>
          <input v-model.number="params.duration" type="number" min="1" max="47" step="1" />
        </div>
      </div>

      <button class="generate-btn" :disabled="!params.prompt || generating" @click="runStrategyB">
        {{ generating ? t('latentLab.crossmodal.generating') : t('latentLab.crossmodal.generate') }}
      </button>
    </div>

    <!-- Strategy C: Latent Cross-Decoding -->
    <div v-if="activeStrategy === 'c'" class="strategy-panel">
      <h3>{{ t('latentLab.crossmodal.strategies.c.title') }}</h3>
      <p class="strategy-description">{{ t('latentLab.crossmodal.strategies.c.description') }}</p>

      <div class="input-group">
        <label>{{ t('latentLab.crossmodal.prompt') }}</label>
        <textarea v-model="params.prompt" rows="3" class="prompt-input" />
      </div>

      <div class="params-row">
        <div class="param">
          <label>{{ t('latentLab.crossmodal.direction') }}</label>
          <select v-model="params.direction">
            <option value="image_to_audio">{{ t('latentLab.crossmodal.imageToAudio') }}</option>
            <option value="audio_to_image">{{ t('latentLab.crossmodal.audioToImage') }}</option>
          </select>
        </div>
        <div class="param">
          <label>Seed</label>
          <input v-model.number="params.seed" type="number" />
        </div>
      </div>

      <button class="generate-btn" :disabled="!params.prompt || generating" @click="runStrategyC">
        {{ generating ? t('latentLab.crossmodal.generating') : t('latentLab.crossmodal.generate') }}
      </button>
    </div>

    <!-- Output Area -->
    <div v-if="resultImage || resultAudio || error" class="output-area">
      <h3>{{ t('latentLab.crossmodal.result') }}</h3>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div v-if="resultImage" class="output-image-container">
        <img :src="resultImage" class="output-image" />
      </div>

      <div v-if="resultAudio" class="output-audio-container">
        <audio :src="resultAudio" controls class="output-audio" />
      </div>

      <div v-if="resultSeed !== null" class="seed-display">
        Seed: {{ resultSeed }}
      </div>

      <div v-if="strategyInfo" class="strategy-info">
        <pre>{{ JSON.stringify(strategyInfo, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const API_BASE = import.meta.env.DEV ? 'http://localhost:17802' : ''

type StrategyId = 'a' | 'b' | 'c'

const strategies = [
  { id: 'a' as StrategyId, label: 'A' },
  { id: 'b' as StrategyId, label: 'B' },
  { id: 'c' as StrategyId, label: 'C' },
]

const activeStrategy = ref<StrategyId>('a')
const generating = ref(false)
const error = ref('')
const resultImage = ref('')
const resultAudio = ref('')
const resultSeed = ref<number | null>(null)
const strategyInfo = ref<Record<string, unknown> | null>(null)

const imagePreview = ref('')
const imageBase64 = ref('')

const params = reactive({
  prompt: '',
  duration: 10,
  steps: 100,
  cfg: 7.0,
  seed: 42,
  direction: 'image_to_audio' as 'image_to_audio' | 'audio_to_image',
})

function clearResults() {
  error.value = ''
  resultImage.value = ''
  resultAudio.value = ''
  resultSeed.value = null
  strategyInfo.value = null
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

async function runStrategyA() {
  clearResults()
  generating.value = true
  try {
    const result = await apiPost('/api/cross_aesthetic/image_to_audio', {
      image_base64: imageBase64.value,
      duration_seconds: params.duration,
      steps: params.steps,
      cfg_scale: params.cfg,
      seed: params.seed,
    })
    if (result.success) {
      resultAudio.value = base64ToDataUrl(result.audio_base64, 'audio/wav')
      resultSeed.value = result.seed
      strategyInfo.value = result.strategy_info
    } else {
      error.value = result.error || 'Generation failed'
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    generating.value = false
  }
}

async function runStrategyB() {
  clearResults()
  generating.value = true
  try {
    const result = await apiPost('/api/cross_aesthetic/shared_seed', {
      prompt: params.prompt,
      seed: params.seed,
      audio_params: { duration_seconds: params.duration },
    })
    if (result.success) {
      if (result.image_base64) {
        resultImage.value = base64ToDataUrl(result.image_base64, 'image/png')
      }
      if (result.audio_base64) {
        resultAudio.value = base64ToDataUrl(result.audio_base64, 'audio/wav')
      }
      resultSeed.value = result.seed
      strategyInfo.value = result.strategy_info
    } else {
      error.value = result.error || 'Generation failed'
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    generating.value = false
  }
}

async function runStrategyC() {
  clearResults()
  generating.value = true
  try {
    const result = await apiPost('/api/cross_aesthetic/cross_decode', {
      prompt: params.prompt,
      direction: params.direction,
      seed: params.seed,
    })
    if (result.success) {
      if (result.output_type === 'image') {
        resultImage.value = base64ToDataUrl(result.output_base64, 'image/png')
      } else {
        resultAudio.value = base64ToDataUrl(result.output_base64, 'audio/wav')
      }
      resultSeed.value = result.seed
      strategyInfo.value = result.strategy_info
    } else {
      error.value = result.error || 'Cross-decoding failed'
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

.strategy-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.strategy-tab {
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

.strategy-tab:hover {
  background: rgba(255, 255, 255, 0.08);
}

.strategy-tab.active {
  background: rgba(76, 175, 80, 0.1);
  border-color: rgba(76, 175, 80, 0.4);
  color: #ffffff;
}

.strategy-label {
  font-size: 1.2rem;
  font-weight: 700;
  display: block;
  margin-bottom: 0.3rem;
}

.strategy-desc {
  font-size: 0.75rem;
  opacity: 0.7;
}

.strategy-panel {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  margin-bottom: 2rem;
}

.strategy-panel h3 {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.strategy-description {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

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

.prompt-input {
  width: 100%;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.9rem;
  resize: vertical;
}

.prompt-input:focus {
  outline: none;
  border-color: rgba(76, 175, 80, 0.5);
}

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
}

.param input:focus,
.param select:focus {
  outline: none;
  border-color: rgba(76, 175, 80, 0.5);
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

.output-image-container {
  margin-bottom: 1rem;
}

.output-image {
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.output-audio-container {
  margin-bottom: 1rem;
}

.output-audio {
  width: 100%;
}

.seed-display {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 0.5rem;
}

.strategy-info {
  margin-top: 1rem;
}

.strategy-info pre {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.3);
  padding: 0.8rem;
  border-radius: 6px;
  overflow-x: auto;
}
</style>
