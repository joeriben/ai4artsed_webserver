<template>
  <div class="code-generation-view">

    <!-- Fixed Header -->
    <header class="page-header">
      <button class="return-button" @click="returnToSelection">
        ← Zurück zur Auswahl
      </button>
      <h1 class="page-title">p5.js Creative Coding</h1>
    </header>

    <!-- Main Container -->
    <div class="main-container" ref="mainContainerRef">

      <!-- SECTION 1: Input + Context -->
      <section class="input-section" ref="section1Ref">
        <h2 class="section-title">Phase 1: Beschreibe deine Szene</h2>

        <div class="bubble-grid">
          <div class="bubble-card input-bubble" :class="{ filled: inputText }">
            <label class="bubble-label">Deine Beschreibung</label>
            <textarea
              v-model="inputText"
              class="bubble-textarea auto-resize-textarea"
              placeholder="z.B. Eine Blumenwiese, Ein geheimnisvoller Wald, Eine Stadt bei Nacht..."
              rows="4"
              @input="autoResize"
            ></textarea>
          </div>

          <div class="bubble-card context-bubble">
            <label class="bubble-label">Layer-Analyse Context</label>
            <textarea
              v-model="contextPrompt"
              class="bubble-textarea auto-resize-textarea"
              placeholder="Standard: Szene wird in Schichten zerlegt (Hintergrund → Mittelgrund → Vordergrund)"
              rows="4"
              readonly
            ></textarea>
          </div>
        </div>

        <button
          class="start-button"
          @click="runSimplification"
          :disabled="!canSimplify || isSimplifying"
        >
          <span v-if="isSimplifying" class="spinner"></span>
          <span v-else>Analysieren >>>></span>
        </button>
      </section>

      <!-- SECTION 2: Layered Scene (editable) -->
      <section
        v-if="executionPhase !== 'initial'"
        class="simplification-section"
        ref="section2Ref"
      >
        <h2 class="section-title">Phase 2: Geschichtete Szene (editierbar)</h2>

        <div class="bubble-card simplification-bubble" :class="{ filled: simplifiedScene }">
          <label class="bubble-label">Schichten: Hintergrund | Mittelgrund | Vordergrund</label>
          <textarea
            v-model="simplifiedScene"
            class="bubble-textarea auto-resize-textarea"
            placeholder="Geschichtete Szenenbeschreibung erscheint hier..."
            rows="8"
            @input="autoResize"
          ></textarea>
        </div>

        <button
          class="start-button"
          @click="generateCode"
          :disabled="!canGenerate || isGenerating"
        >
          <span v-if="isGenerating" class="spinner"></span>
          <span v-else>Code generieren >>>></span>
        </button>
      </section>

      <!-- SECTION 3: Code + Preview -->
      <section
        v-if="executionPhase === 'code_generated'"
        class="code-section"
        ref="section3Ref"
      >
        <h2 class="section-title">Phase 3: Code + Live-Vorschau</h2>

        <div class="code-preview-grid">
          <!-- Code Editor -->
          <div class="code-editor-wrapper">
            <div class="editor-header">
              <span class="editor-title">💻 P5.js Code (editierbar)</span>
              <div class="editor-controls">
                <button class="icon-button" @click="copyCode" title="Copy">
                  📋
                </button>
                <button class="icon-button" @click="downloadCode" title="Download">
                  💾
                </button>
              </div>
            </div>
            <textarea
              v-model="generatedCode"
              class="code-textarea"
              spellcheck="false"
              @input="onCodeEdit"
            ></textarea>
          </div>

          <!-- Live Preview -->
          <div class="preview-wrapper">
            <div class="preview-header">
              <span class="preview-title">🎬 Live-Vorschau</span>
              <div class="preview-controls">
                <button class="icon-button run-button" @click="runCode" title="Run">
                  ▶️ Run
                </button>
                <button class="icon-button" @click="stopCode" title="Stop">
                  ⏹️
                </button>
              </div>
            </div>
            <div class="preview-container">
              <iframe
                ref="previewIframe"
                class="p5-canvas"
                sandbox="allow-scripts"
                title="P5.js Preview"
              ></iframe>
              <div v-if="codeError" class="error-overlay">
                <h3>⚠️ JavaScript Error</h3>
                <pre>{{ codeError }}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

// ============================================================================
// TYPES
// ============================================================================

type ExecutionPhase = 'initial' | 'simplified' | 'code_generated'

// ============================================================================
// ROUTER
// ============================================================================

const router = useRouter()

function returnToSelection() {
  router.push({ name: 'property-selection' })
}

// ============================================================================
// STATE
// ============================================================================

// Input
const inputText = ref('')
const contextPrompt = ref('Transform into ordered layers: BACKGROUND → MIDDLE GROUND → FOREGROUND')

// Phase tracking
const executionPhase = ref<ExecutionPhase>('initial')
const isSimplifying = ref(false)
const isGenerating = ref(false)

// Outputs
const simplifiedScene = ref('')
const generatedCode = ref('')
const codeError = ref('')

// Refs
const mainContainerRef = ref<HTMLElement | null>(null)
const section1Ref = ref<HTMLElement | null>(null)
const section2Ref = ref<HTMLElement | null>(null)
const section3Ref = ref<HTMLElement | null>(null)
const previewIframe = ref<HTMLIFrameElement | null>(null)

// ============================================================================
// COMPUTED
// ============================================================================

const canSimplify = computed(() => inputText.value.trim().length > 0 && !isSimplifying.value)
const canGenerate = computed(() => simplifiedScene.value.trim().length > 0 && !isGenerating.value)

// ============================================================================
// METHODS: API CALLS
// ============================================================================

async function runSimplification() {
  isSimplifying.value = true
  codeError.value = ''

  try {
    const response = await axios.post('/api/schema/pipeline/stage2', {
      schema: 'p5js_simplifier',  // Interception config
      input_text: inputText.value,
      context_prompt: contextPrompt.value || undefined,
      user_language: 'de',
      safety_level: 'youth'
    })

    if (response.data.success) {
      simplifiedScene.value = response.data.interception_result || response.data.stage2_result || ''
      executionPhase.value = 'simplified'

      await nextTick()
      scrollToSection(section2Ref.value)
    } else {
      alert(`Fehler bei Analyse: ${response.data.error}`)
    }
  } catch (error: any) {
    console.error('Simplification error:', error)
    alert(`Fehler: ${error.response?.data?.error || error.message}`)
  } finally {
    isSimplifying.value = false
  }
}

async function generateCode() {
  isGenerating.value = true
  codeError.value = ''

  try {
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'p5js_simplifier',  // Original schema (for tracking)
      input_text: simplifiedScene.value,  // Use simplified scene
      output_config: 'p5js_code',  // Output config for code generation
      user_language: 'de',
      safety_level: 'youth'
    })

    if (response.data.status === 'success') {
      // Extract code from response
      const code = response.data.code || response.data.final_output || ''

      if (code) {
        generatedCode.value = code
        executionPhase.value = 'code_generated'

        await nextTick()
        scrollToSection(section3Ref.value)

        // Auto-run first time
        setTimeout(() => runCode(), 300)
      } else {
        alert('Fehler: Kein Code generiert')
      }
    } else {
      alert(`Fehler bei Code-Generierung: ${response.data.error}`)
    }
  } catch (error: any) {
    console.error('Code generation error:', error)
    alert(`Fehler: ${error.response?.data?.error || error.message}`)
  } finally {
    isGenerating.value = false
  }
}

// ============================================================================
// METHODS: CODE EXECUTION
// ============================================================================

function runCode() {
  if (!previewIframe.value || !generatedCode.value) return

  codeError.value = ''

  try {
    const iframe = previewIframe.value
    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document
    if (!iframeDoc) {
      throw new Error('Cannot access iframe document')
    }

    // Create HTML with p5.js library + user code
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
  <style>
    body {
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #f0f0f0;
    }
    canvas {
      display: block;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <script>
    // Error handling
    window.addEventListener('error', function(e) {
      parent.postMessage({
        type: 'error',
        message: e.message,
        line: e.lineno,
        column: e.colno
      }, '*')
    })

    // User code
    try {
      ${generatedCode.value}
    } catch (err) {
      parent.postMessage({
        type: 'error',
        message: err.message,
        stack: err.stack
      }, '*')
    }
  </script>
</body>
</html>`

    iframeDoc.open()
    iframeDoc.write(html)
    iframeDoc.close()

  } catch (error: any) {
    codeError.value = error.message
    console.error('Code execution error:', error)
  }
}

function stopCode() {
  if (!previewIframe.value) return

  // Reload iframe to stop execution
  const iframe = previewIframe.value
  iframe.src = 'about:blank'

  // Clear after a moment to allow stop
  setTimeout(() => {
    codeError.value = ''
  }, 100)
}

function onCodeEdit() {
  // Code was manually edited - don't auto-run
  // User must click Run button
}

// ============================================================================
// METHODS: CODE ACTIONS
// ============================================================================

function copyCode() {
  if (!generatedCode.value) return

  navigator.clipboard.writeText(generatedCode.value)
    .then(() => {
      alert('Code in Zwischenablage kopiert!')
    })
    .catch(err => {
      console.error('Copy failed:', err)
      alert('Kopieren fehlgeschlagen')
    })
}

function downloadCode() {
  if (!generatedCode.value) return

  const element = document.createElement('a')
  const file = new Blob([generatedCode.value], { type: 'text/javascript' })
  element.href = URL.createObjectURL(file)
  element.download = 'sketch.js'
  element.style.display = 'none'
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
  URL.revokeObjectURL(element.href)
}

// ============================================================================
// METHODS: UI HELPERS
// ============================================================================

function autoResize(event: Event) {
  const target = event.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = target.scrollHeight + 'px'
}

function scrollToSection(element: HTMLElement | null) {
  if (!element) return

  setTimeout(() => {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  // Listen for iframe errors
  window.addEventListener('message', (event) => {
    if (event.data.type === 'error') {
      codeError.value = `Line ${event.data.line || '?'}: ${event.data.message}`
    }
  })

  // Auto-resize existing textareas
  const textareas = document.querySelectorAll('.auto-resize-textarea')
  textareas.forEach(ta => {
    const textarea = ta as HTMLTextAreaElement
    textarea.style.height = 'auto'
    textarea.style.height = textarea.scrollHeight + 'px'
  })
})

// ============================================================================
// WATCHES
// ============================================================================

watch([inputText, simplifiedScene], () => {
  nextTick(() => {
    const textareas = document.querySelectorAll('.auto-resize-textarea')
    textareas.forEach(ta => {
      const textarea = ta as HTMLTextAreaElement
      textarea.style.height = 'auto'
      textarea.style.height = textarea.scrollHeight + 'px'
    })
  })
})
</script>

<style scoped>
/* ============================================================================
   ROOT CONTAINER
   ============================================================================ */

.code-generation-view {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  color: #ffffff;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ============================================================================
   HEADER
   ============================================================================ */

.page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 2rem;
  background: rgba(10, 10, 10, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.return-button {
  position: absolute;
  left: 2rem;
  padding: 0.6rem 1.2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.return-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-2px);
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ============================================================================
   MAIN CONTAINER
   ============================================================================ */

.main-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 6rem 2rem 4rem;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #a0aec0;
}

/* ============================================================================
   BUBBLE CARDS
   ============================================================================ */

.bubble-card {
  background: rgba(30, 30, 40, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1rem 0;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.bubble-card.filled {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.bubble-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #a0aec0;
  margin-bottom: 0.5rem;
}

.bubble-textarea {
  width: 100%;
  min-height: 80px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  color: #ffffff;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
}

.bubble-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.bubble-textarea::placeholder {
  color: #4a5568;
}

/* ============================================================================
   SECTIONS
   ============================================================================ */

.input-section,
.simplification-section {
  margin-bottom: 3rem;
}

.bubble-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.start-button {
  display: block;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.start-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.start-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================================================
   CODE SECTION
   ============================================================================ */

.code-section {
  margin-bottom: 3rem;
}

.code-preview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1.5rem;
}

.code-editor-wrapper,
.preview-wrapper {
  display: flex;
  flex-direction: column;
  height: 700px;
}

.editor-header,
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: rgba(30, 30, 40, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: none;
  border-radius: 12px 12px 0 0;
}

.editor-title,
.preview-title {
  font-weight: 600;
  font-size: 1rem;
}

.editor-controls,
.preview-controls {
  display: flex;
  gap: 0.5rem;
}

.icon-button {
  padding: 0.5rem 0.8rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.icon-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.run-button {
  background: rgba(76, 175, 80, 0.3);
  border-color: rgba(76, 175, 80, 0.5);
}

.run-button:hover {
  background: rgba(76, 175, 80, 0.5);
}

.code-textarea {
  flex: 1;
  width: 100%;
  background: #1a1a1a;
  color: #00ff00;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top: none;
  border-radius: 0 0 12px 12px;
  padding: 1.5rem;
  resize: none;
  overflow-y: auto;
}

.code-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.5);
}

.preview-container {
  position: relative;
  flex: 1;
  background: #f0f0f0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top: none;
  border-radius: 0 0 12px 12px;
  overflow: hidden;
}

.p5-canvas {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(220, 38, 38, 0.9);
  color: #ffffff;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.error-overlay h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
}

.error-overlay pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  max-width: 100%;
  overflow-x: auto;
}

/* ============================================================================
   SPINNER
   ============================================================================ */

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================================================
   RESPONSIVE
   ============================================================================ */

@media (max-width: 1024px) {
  .bubble-grid,
  .code-preview-grid {
    grid-template-columns: 1fr;
  }

  .code-editor-wrapper,
  .preview-wrapper {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 1rem;
  }

  .return-button {
    left: 1rem;
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
  }

  .page-title {
    font-size: 1.4rem;
  }

  .main-container {
    padding: 5rem 1rem 2rem;
  }
}
</style>
