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
          <input type="range" v-model.number="synth.alpha" min="-2" max="3" step="0.01" />
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
          <input v-model.number="synth.duration" type="number" min="0.1" max="5" step="0.1" />
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
        <button class="loop-btn" :class="{ active: looper.isLooping.value }" @click="toggleLoop">
          {{ looper.isLooping.value ? t('latentLab.crossmodal.synth.loopOn') : t('latentLab.crossmodal.synth.loopOff') }}
        </button>
        <button v-if="looper.isPlaying.value" class="stop-btn" @click="looper.stop()">
          {{ t('latentLab.crossmodal.synth.stop') }}
        </button>
      </div>

      <!-- Looper Widget -->
      <div v-if="looper.isPlaying.value || lastSynthBase64" class="looper-widget">
        <div class="looper-status">
          <span class="looper-indicator" :class="{ pulsing: looper.isPlaying.value }" />
          <span class="looper-label">
            {{ looper.isPlaying.value
              ? (looper.isLooping.value ? t('latentLab.crossmodal.synth.looping') : t('latentLab.crossmodal.synth.playing'))
              : t('latentLab.crossmodal.synth.stopped') }}
          </span>
          <span v-if="looper.bufferDuration.value > 0" class="looper-duration">
            {{ looper.bufferDuration.value.toFixed(2) }}s
          </span>
        </div>
        <!-- Loop Interval -->
        <div class="loop-interval">
          <div class="slider-header">
            <label>{{ t('latentLab.crossmodal.synth.loopInterval') }}</label>
            <span class="slider-value">
              {{ (looper.loopStartFrac.value * looper.bufferDuration.value).toFixed(3) }}s
              – {{ (looper.loopEndFrac.value * looper.bufferDuration.value).toFixed(3) }}s
            </span>
          </div>
          <div class="dual-range">
            <input
              type="range"
              :value="looper.loopStartFrac.value"
              min="0"
              max="1"
              step="0.001"
              class="range-start"
              @input="onLoopStartInput"
            />
            <input
              type="range"
              :value="looper.loopEndFrac.value"
              min="0"
              max="1"
              step="0.001"
              class="range-end"
              @input="onLoopEndInput"
            />
          </div>
          <span class="slider-hint">{{ t('latentLab.crossmodal.synth.loopIntervalHint') }}</span>
        </div>
        <!-- Transpose -->
        <div class="transpose-row">
          <label>{{ t('latentLab.crossmodal.synth.transpose') }}</label>
          <input
            type="range"
            :value="looper.transposeSemitones.value"
            min="-24"
            max="24"
            step="1"
            @input="onTransposeInput"
          />
          <span class="transpose-value">{{ formatTranspose(looper.transposeSemitones.value) }}</span>
        </div>
        <!-- Crossfade duration -->
        <div class="transpose-row">
          <label>{{ t('latentLab.crossmodal.synth.crossfade') }}</label>
          <input
            type="range"
            :value="looper.crossfadeMs.value"
            min="10"
            max="500"
            step="10"
            @input="onCrossfadeInput"
          />
          <span class="transpose-value">{{ looper.crossfadeMs.value }}ms</span>
        </div>
        <!-- Save buttons -->
        <div v-if="looper.hasAudio.value" class="save-row">
          <button class="save-btn" @click="saveRaw">
            {{ t('latentLab.crossmodal.synth.saveRaw') }}
          </button>
          <button class="save-btn" @click="saveLoop">
            {{ t('latentLab.crossmodal.synth.saveLoop') }}
          </button>
        </div>
      </div>

      <!-- MIDI Section (collapsed by default) -->
      <details class="midi-section">
        <summary>{{ t('latentLab.crossmodal.synth.midiSection') }}</summary>
        <div class="midi-content">
          <div v-if="!midi.isSupported.value" class="midi-unsupported">
            {{ t('latentLab.crossmodal.synth.midiUnsupported') }}
          </div>
          <template v-else>
            <div class="midi-input-select">
              <label>{{ t('latentLab.crossmodal.synth.midiInput') }}</label>
              <select
                :value="midi.selectedInputId.value"
                @change="onMidiInputChange"
              >
                <option :value="null">{{ t('latentLab.crossmodal.synth.midiNone') }}</option>
                <option v-for="inp in midi.inputs.value" :key="inp.id" :value="inp.id">
                  {{ inp.name }}
                </option>
              </select>
            </div>
            <div class="midi-mapping-table">
              <h5>{{ t('latentLab.crossmodal.synth.midiMappings') }}</h5>
              <table>
                <tbody>
                  <tr><td>CC1</td><td>{{ t('latentLab.crossmodal.synth.alpha') }}</td></tr>
                  <tr><td>CC2</td><td>{{ t('latentLab.crossmodal.synth.magnitude') }}</td></tr>
                  <tr><td>CC3</td><td>{{ t('latentLab.crossmodal.synth.noise') }}</td></tr>
                  <tr><td>CC64</td><td>{{ t('latentLab.crossmodal.synth.loop') }}</td></tr>
                  <tr><td>{{ t('latentLab.crossmodal.synth.midiNoteC3') }}</td><td>{{ t('latentLab.crossmodal.synth.midiGenerate') }}</td></tr>
                  <tr><td>{{ t('latentLab.crossmodal.synth.midiPitch') }}</td><td>{{ t('latentLab.crossmodal.synth.transpose') }}</td></tr>
                </tbody>
              </table>
            </div>
          </template>
        </div>
      </details>
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

      <!-- Standard audio player for MMAudio / Guidance tabs -->
      <div v-if="resultAudio && activeTab !== 'synth'" class="output-audio-container">
        <audio :src="resultAudio" controls class="output-audio" />
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
import { ref, reactive, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAudioLooper } from '@/composables/useAudioLooper'
import { useWebMidi } from '@/composables/useWebMidi'

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

interface EmbeddingStats {
  mean: number
  std: number
  top_dimensions: Array<{ dim: number; value: number }>
}
const embeddingStats = ref<EmbeddingStats | null>(null)

// Image upload (shared across MMAudio and Guidance)
const imagePreview = ref('')
const imageBase64 = ref('')

// Last synth base64 for replay
const lastSynthBase64 = ref('')

// ===== Audio Looper =====
const looper = useAudioLooper()

// ===== Web MIDI =====
const midi = useWebMidi()

// MIDI reference note for transpose (C3 = 60)
const MIDI_REF_NOTE = 60

// Initialize MIDI
midi.init()

// MIDI CC mappings
// CC1 → Alpha (-2 to 3)
midi.mapCC(1, (v) => { synth.alpha = -2 + v * 5 })
// CC2 → Magnitude (0.1 to 5)
midi.mapCC(2, (v) => { synth.magnitude = 0.1 + v * 4.9 })
// CC3 → Noise (0 to 1)
midi.mapCC(3, (v) => { synth.noise = v })
// CC64 → Loop toggle (sustain pedal: >0.5 = on)
midi.mapCC(64, (v) => { looper.setLoop(v > 0.5) })

// MIDI Note → Generate trigger + transpose
midi.onNote((note, _velocity, on) => {
  if (!on) return
  const semitones = note - MIDI_REF_NOTE
  looper.setTranspose(semitones)
  if (!generating.value && synth.promptA) {
    runSynth()
  }
})

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
  const maxVal = embeddingStats.value.top_dimensions[0]?.value ?? 0
  return maxVal > 0 ? `${(value / maxVal) * 100}%` : '0%'
}

function formatTranspose(semitones: number): string {
  if (semitones === 0) return '0'
  return semitones > 0 ? `+${semitones}` : `${semitones}`
}

function toggleLoop() {
  looper.setLoop(!looper.isLooping.value)
}

function onTransposeInput(event: Event) {
  const val = parseInt((event.target as HTMLInputElement).value)
  looper.setTranspose(val)
}

function onLoopStartInput(event: Event) {
  const val = parseFloat((event.target as HTMLInputElement).value)
  looper.setLoopStart(val)
}

function onLoopEndInput(event: Event) {
  const val = parseFloat((event.target as HTMLInputElement).value)
  looper.setLoopEnd(val)
}

function onCrossfadeInput(event: Event) {
  const val = parseInt((event.target as HTMLInputElement).value)
  looper.setCrossfade(val)
}

function onMidiInputChange(event: Event) {
  const val = (event.target as HTMLSelectElement).value
  midi.selectInput(val || null)
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function saveRaw() {
  const blob = looper.exportRaw()
  if (blob) downloadBlob(blob, `synth_raw_${resultSeed.value ?? 0}.wav`)
}

function saveLoop() {
  const blob = looper.exportLoop()
  if (blob) downloadBlob(blob, `synth_loop_${resultSeed.value ?? 0}.wav`)
}

// ===== Synth =====
async function runSynth() {
  // Don't clear looper state — keep playing during generation
  error.value = ''
  resultSeed.value = null
  generationTimeMs.value = null
  embeddingStats.value = null
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
      lastSynthBase64.value = result.audio_base64
      resultAudio.value = base64ToDataUrl(result.audio_base64, 'audio/wav')
      resultSeed.value = result.seed
      generationTimeMs.value = result.generation_time_ms
      embeddingStats.value = result.embedding_stats

      // Feed into looper (crossfades if already playing)
      await looper.play(result.audio_base64)
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

onUnmounted(() => {
  looper.dispose()
})
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
  gap: 1rem;
  margin-bottom: 1rem;
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

.loop-btn,
.stop-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.loop-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.5);
}

.loop-btn.active {
  background: rgba(76, 175, 80, 0.15);
  border-color: rgba(76, 175, 80, 0.4);
  color: #4CAF50;
}

.stop-btn {
  background: rgba(255, 82, 82, 0.15);
  border: 1px solid rgba(255, 82, 82, 0.3);
  color: #ff5252;
}

.stop-btn:hover {
  background: rgba(255, 82, 82, 0.25);
}

/* Looper widget */
.looper-widget {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.looper-status {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}

.looper-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.looper-indicator.pulsing {
  background: #4CAF50;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 4px rgba(76, 175, 80, 0.4); }
  50% { opacity: 0.5; box-shadow: 0 0 8px rgba(76, 175, 80, 0.8); }
}

.looper-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.looper-duration {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.3);
  margin-left: auto;
  font-variant-numeric: tabular-nums;
}

/* Loop interval dual-range */
.loop-interval {
  margin-bottom: 0.8rem;
}

.dual-range {
  position: relative;
  height: 1.5rem;
}

.dual-range input[type="range"] {
  position: absolute;
  width: 100%;
  top: 0;
  pointer-events: none;
  appearance: none;
  -webkit-appearance: none;
  background: transparent;
  accent-color: #4CAF50;
}

.dual-range input[type="range"]::-webkit-slider-thumb {
  pointer-events: auto;
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: none;
}

.dual-range input[type="range"]::-moz-range-thumb {
  pointer-events: auto;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: none;
}

.dual-range input[type="range"]::-webkit-slider-runnable-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.dual-range input[type="range"]::-moz-range-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.transpose-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.transpose-row label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

.transpose-row input[type="range"] {
  flex: 1;
  accent-color: #4CAF50;
}

.transpose-value {
  font-size: 0.8rem;
  color: #4CAF50;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  min-width: 2.5rem;
  text-align: right;
}

/* Save buttons */
.save-row {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.8rem;
}

.save-btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.75rem;
  border-radius: 5px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.2s;
}

.save-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

/* MIDI section */
.midi-section {
  margin-top: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  overflow: hidden;
}

.midi-section summary {
  padding: 0.7rem 1rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  background: rgba(255, 255, 255, 0.03);
}

.midi-section summary:hover {
  color: rgba(255, 255, 255, 0.7);
}

.midi-content {
  padding: 1rem;
}

.midi-unsupported {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.35);
  font-style: italic;
}

.midi-input-select {
  margin-bottom: 1rem;
}

.midi-input-select label {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.3rem;
}

.midi-input-select select {
  width: 100%;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #ffffff;
  font-size: 0.85rem;
}

.midi-mapping-table h5 {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.5rem;
}

.midi-mapping-table table {
  width: 100%;
  font-size: 0.75rem;
  border-collapse: collapse;
}

.midi-mapping-table td {
  padding: 0.3rem 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.5);
}

.midi-mapping-table td:first-child {
  color: #4CAF50;
  font-weight: 600;
  width: 5rem;
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
