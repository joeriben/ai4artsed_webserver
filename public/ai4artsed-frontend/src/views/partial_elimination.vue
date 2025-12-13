<template>
  <div class="partial-elimination-container">
    <!-- Left Column: Input -->
    <div class="input-section">
      <div class="header">
        <h2>🧬 Partial Elimination</h2>
        <p class="subtitle">Vektordimension-Manipulation</p>
      </div>

      <div class="prompt-input">
        <label>Prompt-Eingabe</label>
        <textarea
          v-model="userPrompt"
          placeholder="Beschreibe dein Bild..."
          rows="6"
        ></textarea>
      </div>

      <!-- Mode Selector -->
      <div class="mode-selector">
        <label>Eliminationsmodus</label>
        <select v-model="eliminationMode">
          <option value="average">Average (Durchschnitt)</option>
          <option value="random">Random (Zufall)</option>
          <option value="invert">Invert (Umkehrung)</option>
          <option value="zero_out">Zero Out (Nullsetzen)</option>
        </select>
        <small class="mode-description">{{ modeDescription }}</small>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="copyPrompt" class="icon-btn" title="Kopieren">
          📋
        </button>
        <button @click="pastePrompt" class="icon-btn" title="Einfügen">
          📄
        </button>
        <button @click="clearPrompt" class="icon-btn" title="Löschen">
          🗑️
        </button>
      </div>

      <button
        class="execute-btn"
        @click="executeWorkflow"
        :disabled="isGenerating || !userPrompt.trim()"
      >
        {{ isGenerating ? 'Generiere...' : 'Ausführen' }}
      </button>

      <!-- Info Box -->
      <div class="info-box">
        <h4>ℹ️ Wie funktioniert das?</h4>
        <p>Partial Elimination manipuliert Teile des Vektorraums, um zu zeigen, welche Dimensionen welche semantischen Informationen enthalten.</p>
        <ul>
          <li><strong>Referenzbild:</strong> Original ohne Manipulation</li>
          <li><strong>Erste Hälfte:</strong> Dimensionen 0-2047 manipuliert</li>
          <li><strong>Zweite Hälfte:</strong> Dimensionen 2048-4095 manipuliert</li>
        </ul>
      </div>
    </div>

    <!-- Right Column: Output (3-Image Grid) -->
    <div class="output-section">
      <!-- Empty State -->
      <div v-if="!hasResults && !isGenerating" class="empty-state">
        <div class="empty-icon">🎨</div>
        <h3>Deine 3 Bildvarianten erscheinen hier</h3>
        <p class="empty-subtitle">Referenzbild · Variante A · Variante B</p>
        <div class="preview-grid">
          <div class="preview-placeholder">
            <span>Referenz</span>
          </div>
          <div class="preview-placeholder">
            <span>Erste Hälfte</span>
          </div>
          <div class="preview-placeholder">
            <span>Zweite Hälfte</span>
          </div>
        </div>
      </div>

      <!-- Generating State -->
      <div v-if="isGenerating" class="generating-state">
        <SpriteProgressAnimation :progress="generationProgress" />
        <div class="progress-info">
          <p class="progress-text">{{ progressText }}</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: generationProgress + '%' }"></div>
          </div>
          <p class="progress-percent">{{ generationProgress }}%</p>
        </div>
      </div>

      <!-- Results: 3-Image Comparison Grid -->
      <div v-if="hasResults && !isGenerating" class="results-container">
        <div class="results-header">
          <h3>Ergebnisse: {{ eliminationMode }} Modus</h3>
          <button @click="clearResults" class="clear-btn">🗑️ Löschen</button>
        </div>

        <div class="image-grid">
          <div
            v-for="(image, idx) in images"
            :key="idx"
            class="image-card"
            @click="openFullscreen(idx)"
          >
            <div class="image-wrapper">
              <img :src="image.url" :alt="image.label" loading="lazy" />
            </div>
            <div class="image-label">
              <h4>{{ image.label }}</h4>
              <p>{{ image.description }}</p>
            </div>
            <div class="image-actions">
              <button @click.stop="downloadImage(idx)" class="action-btn" title="Download">
                💾
              </button>
              <button @click.stop="sendToI2I(idx)" class="action-btn" title="Send to Img2Img">
                🎨
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Fullscreen Modal -->
      <div v-if="fullscreenIndex !== null" class="fullscreen-modal" @click="closeFullscreen">
        <button class="close-btn" @click.stop="closeFullscreen">✕</button>
        <img :src="images[fullscreenIndex].url" @click.stop />
        <div class="fullscreen-info">
          <h3>{{ images[fullscreenIndex].label }}</h3>
          <p>{{ images[fullscreenIndex].description }}</p>
        </div>
        <div class="fullscreen-nav">
          <button @click.stop="prevImage" :disabled="fullscreenIndex === 0">◀</button>
          <span>{{ fullscreenIndex + 1 }} / {{ images.length }}</span>
          <button @click.stop="nextImage" :disabled="fullscreenIndex === images.length - 1">▶</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import SpriteProgressAnimation from '@/components/SpriteProgressAnimation.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const userPrompt = ref('')
const eliminationMode = ref('average')
const isGenerating = ref(false)
const generationProgress = ref(0)
const runId = ref(null)
const images = ref([])
const fullscreenIndex = ref(null)

// Computed
const hasResults = computed(() => images.value.length > 0)

const progressText = computed(() => {
  if (generationProgress.value < 20) return 'Starte Workflow...'
  if (generationProgress.value < 40) return 'Lade Modell...'
  if (generationProgress.value < 60) return 'Generiere Referenzbild...'
  if (generationProgress.value < 80) return 'Manipuliere Vektordimensionen...'
  return 'Fast fertig...'
})

const modeDescription = computed(() => {
  const descriptions = {
    average: 'Ersetzt Dimensionen durch Durchschnittswert',
    random: 'Ersetzt Dimensionen durch Zufallswerte',
    invert: 'Kehrt Vorzeichen der Dimensionen um',
    zero_out: 'Setzt Dimensionen auf Null'
  }
  return descriptions[eliminationMode.value] || ''
})

// Methods
async function executeWorkflow() {
  if (!userPrompt.value.trim()) return

  isGenerating.value = true
  generationProgress.value = 0
  images.value = []

  try {
    // 1. POST to /api/schema/pipeline/execute
    const response = await fetch('/api/schema/pipeline/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        schema: 'partial_elimination',
        input_text: userPrompt.value,
        safety_level: 'open',
        output_config: 'partial_elimination_legacy',
        user_language: 'de',
        mode: eliminationMode.value,
        seed: Math.floor(Math.random() * 1000000)
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()

    if (!result.media_outputs || result.media_outputs.length === 0) {
      throw new Error('No media outputs in response')
    }

    runId.value = result.media_outputs[0].run_id

    // 2. Simulate progress (60-second workflow)
    const progressInterval = setInterval(() => {
      if (generationProgress.value < 98) {
        generationProgress.value = Math.min(98, generationProgress.value + 1.5)
      }
    }, 1000)

    // 3. Poll for completion
    let pollCount = 0
    const maxPolls = 90 // 3 minutes max
    const pollInterval = setInterval(async () => {
      pollCount++

      try {
        const metaResponse = await fetch(`/api/pipeline/${runId.value}/entities`)
        if (!metaResponse.ok) {
          console.warn('Metadata not yet available')
          return
        }

        const meta = await metaResponse.json()
        const outputEntities = meta.entities.filter(e => e.type.startsWith('output_'))

        if (outputEntities.length === 3) {
          clearInterval(pollInterval)
          clearInterval(progressInterval)
          await loadImages()
          isGenerating.value = false
          generationProgress.value = 100
        } else if (pollCount >= maxPolls) {
          clearInterval(pollInterval)
          clearInterval(progressInterval)
          throw new Error('Timeout waiting for images')
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }, 2000)

  } catch (error) {
    console.error('Execution failed:', error)
    alert(`Fehler bei der Generierung: ${error.message}`)
    isGenerating.value = false
  }
}

async function loadImages() {
  try {
    // Fetch all images via new endpoint
    const response = await fetch(`/api/media/images/${runId.value}`)

    if (!response.ok) {
      throw new Error('Failed to load images')
    }

    const data = await response.json()

    // Map to display structure with labels
    const labels = [
      {
        label: 'Referenzbild',
        description: 'Unmanipulierte Ausgabe (Original)'
      },
      {
        label: 'Erste Hälfte eliminiert',
        description: `Vektordimensionen 0-2047 (${eliminationMode.value})`
      },
      {
        label: 'Zweite Hälfte eliminiert',
        description: `Vektordimensionen 2048-4095 (${eliminationMode.value})`
      }
    ]

    images.value = data.images.map((img, idx) => ({
      url: img.url,
      label: labels[idx]?.label || `Bild ${idx + 1}`,
      description: labels[idx]?.description || '',
      index: idx,
      metadata: img.metadata
    }))

    console.log('Loaded images:', images.value)

  } catch (error) {
    console.error('Failed to load images:', error)
    alert('Fehler beim Laden der Bilder')
  }
}

function openFullscreen(idx) {
  fullscreenIndex.value = idx
}

function closeFullscreen() {
  fullscreenIndex.value = null
}

function prevImage() {
  if (fullscreenIndex.value > 0) {
    fullscreenIndex.value--
  }
}

function nextImage() {
  if (fullscreenIndex.value < images.value.length - 1) {
    fullscreenIndex.value++
  }
}

async function downloadImage(idx) {
  try {
    const response = await fetch(images.value[idx].url)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `partial_elimination_${eliminationMode.value}_${idx}.png`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
  }
}

function sendToI2I(idx) {
  const transferData = {
    sourceImage: images.value[idx].url,
    runId: runId.value,
    index: idx,
    workflow: 'partial_elimination'
  }
  localStorage.setItem('i2i_transfer_data', JSON.stringify(transferData))
  router.push('/img2img')
}

function copyPrompt() {
  navigator.clipboard.writeText(userPrompt.value)
}

async function pastePrompt() {
  try {
    const text = await navigator.clipboard.readText()
    userPrompt.value = text
  } catch (error) {
    console.error('Paste failed:', error)
  }
}

function clearPrompt() {
  userPrompt.value = ''
}

function clearResults() {
  images.value = []
  runId.value = null
}
</script>

<style scoped>
.partial-elimination-container {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 2rem;
  height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

/* Left Column: Input Section */
.input-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header h2 {
  margin: 0;
  color: #9C27B0;
  font-size: 1.8rem;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: #666;
  font-size: 0.9rem;
}

.prompt-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.prompt-input textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.2s;
}

.prompt-input textarea:focus {
  outline: none;
  border-color: #9C27B0;
}

.mode-selector {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mode-selector label {
  font-weight: 600;
  color: #333;
}

.mode-selector select {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  background: white;
  transition: border-color 0.2s;
}

.mode-selector select:focus {
  outline: none;
  border-color: #9C27B0;
}

.mode-description {
  color: #666;
  font-size: 0.85rem;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  flex: 1;
  padding: 0.75rem;
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}

.execute-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.execute-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.info-box {
  background: #f0f4ff;
  border-left: 4px solid #9C27B0;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.info-box h4 {
  margin: 0 0 0.5rem 0;
  color: #9C27B0;
}

.info-box p {
  margin: 0 0 0.5rem 0;
  color: #555;
}

.info-box ul {
  margin: 0;
  padding-left: 1.5rem;
  color: #555;
}

.info-box li {
  margin-bottom: 0.25rem;
}

/* Right Column: Output Section */
.output-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #666;
}

.empty-subtitle {
  margin: 0 0 2rem 0;
  color: #999;
  font-size: 0.9rem;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  width: 100%;
  max-width: 600px;
}

.preview-placeholder {
  aspect-ratio: 1;
  border: 2px dashed #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.85rem;
}

/* Generating State */
.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.progress-info {
  margin-top: 2rem;
  text-align: center;
  width: 100%;
  max-width: 400px;
}

.progress-text {
  margin: 0 0 1rem 0;
  color: #666;
  font-size: 1.1rem;
  font-weight: 500;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-percent {
  margin: 0;
  color: #999;
  font-size: 0.9rem;
}

/* Results */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.results-header h3 {
  margin: 0;
  color: #333;
}

.clear-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #ffebee;
  border-color: #ef5350;
  color: #ef5350;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  flex: 1;
}

.image-card {
  position: relative;
  border: 2px solid #9C27B0;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(156, 39, 176, 0.3);
}

.image-wrapper {
  aspect-ratio: 1;
  overflow: hidden;
  background: #f5f5f5;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-label {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.85);
  color: white;
}

.image-label h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.image-label p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.8;
}

.image-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-card:hover .image-actions {
  opacity: 1;
}

.action-btn {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.action-btn:hover {
  transform: scale(1.1);
}

/* Fullscreen Modal */
.fullscreen-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 2rem;
}

.fullscreen-modal img {
  max-width: 90%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
}

.close-btn {
  position: absolute;
  top: 2rem;
  right: 2rem;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid white;
  border-radius: 50%;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.fullscreen-info {
  margin-top: 2rem;
  text-align: center;
  color: white;
}

.fullscreen-info h3 {
  margin: 0 0 0.5rem 0;
}

.fullscreen-info p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.fullscreen-nav {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 1rem;
  align-items: center;
  color: white;
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem 1.5rem;
  border-radius: 24px;
}

.fullscreen-nav button {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid white;
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.fullscreen-nav button:not(:disabled):hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.fullscreen-nav button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.fullscreen-nav span {
  font-weight: 600;
  min-width: 60px;
  text-align: center;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #9C27B0;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #7B1FA2;
}
</style>
