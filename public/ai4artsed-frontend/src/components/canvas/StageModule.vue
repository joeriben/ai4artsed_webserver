<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CanvasNode, LLMModelSummary } from '@/types/canvas'
import { getNodeTypeDefinition } from '@/types/canvas'

const { locale } = useI18n()

// Icon URL helper
function getIconUrl(iconPath: string): string {
  return new URL(`../../assets/icons/${iconPath}`, import.meta.url).href
}

/** Collector output item from execution */
interface CollectorOutputItem {
  nodeId: string
  nodeType: string
  output: unknown
  error: string | null
}

const props = defineProps<{
  node: CanvasNode
  selected: boolean
  configName?: string
  llmModels?: LLMModelSummary[]
  /** Execution results for this node (from store) */
  executionResult?: {
    type: string
    output: unknown
    error: string | null
    model?: string
  }
  /** Collector output (only for collector nodes) */
  collectorOutput?: CollectorOutputItem[]
}>()

const emit = defineEmits<{
  'mousedown': [e: MouseEvent]
  'start-connect': []
  'end-connect': []
  'delete': []
  'select-config': []
  'update-llm': [llmModel: string]
  'update-context-prompt': [prompt: string]
  'update-translation-prompt': [prompt: string]
  'update-prompt-text': [text: string]
  'update-size': [width: number, height: number]
  'update-evaluation-prompt': [prompt: string]
  'update-output-type': [outputType: 'commentary' | 'score' | 'binary' | 'all']
  'update-display-title': [title: string]
  'update-display-mode': [mode: 'popup' | 'inline' | 'toast']
  'update-threshold-value': [threshold: number]
  'update-fork-labels': [trueLabel: string, falseLabel: string]
  'start-connect-labeled': [label: string]
}>()

const nodeTypeDef = computed(() => getNodeTypeDefinition(props.node.type))
const nodeColor = computed(() => nodeTypeDef.value?.color || '#666')
const nodeIcon = computed(() => nodeTypeDef.value?.icon || '📦')
const nodeIconUrl = computed(() => {
  const icon = nodeTypeDef.value?.icon
  if (icon && icon.endsWith('.svg')) {
    return getIconUrl(icon)
  }
  return null
})
const nodeLabel = computed(() => {
  const def = nodeTypeDef.value
  if (!def) return props.node.type
  return locale.value === 'de' ? def.label.de : def.label.en
})

const canDelete = computed(() => !props.node.locked)
const hasInputConnector = computed(() => {
  const def = nodeTypeDef.value
  return def && def.acceptsFrom.length > 0
})
const hasOutputConnector = computed(() => {
  const def = nodeTypeDef.value
  return def && def.outputsTo.length > 0
})

// Node type checks
const isInput = computed(() => props.node.type === 'input')
const isInterception = computed(() => props.node.type === 'interception')
const isTranslation = computed(() => props.node.type === 'translation')
const isGeneration = computed(() => props.node.type === 'generation')
const isCollector = computed(() => props.node.type === 'collector')
const isDisplay = computed(() => props.node.type === 'display')
const isBinaryFork = computed(() => props.node.type === 'binary_fork')
const isThresholdFork = computed(() => props.node.type === 'threshold_fork')
const isFork = computed(() => isBinaryFork.value || isThresholdFork.value)
// Session 134: Evaluation node types
const isEvaluation = computed(() => [
  'fairness_evaluation',
  'creativity_evaluation',
  'equity_evaluation',
  'quality_evaluation',
  'custom_evaluation'
].includes(props.node.type))
const needsLLM = computed(() => isInterception.value || isTranslation.value || isEvaluation.value)
const hasCollectorOutput = computed(() => isCollector.value && props.collectorOutput && props.collectorOutput.length > 0)

// Check if node is properly configured
const isConfigured = computed(() => {
  if (isGeneration.value) return !!props.node.configId
  if (needsLLM.value) return !!props.node.llmModel
  return true
})

const displayConfigName = computed(() => {
  if (props.configName) return props.configName
  if (props.node.configId) return props.node.configId
  return locale.value === 'de' ? 'Auswählen...' : 'Select...'
})

// Event handlers for inline editing
function onLLMChange(event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-llm', select.value)
}

function onContextPromptChange(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  emit('update-context-prompt', textarea.value)
}

function onTranslationPromptChange(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  emit('update-translation-prompt', textarea.value)
}

function onPromptTextChange(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  emit('update-prompt-text', textarea.value)
}

// Session 134: Evaluation node handlers
function onEvaluationPromptChange(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  emit('update-evaluation-prompt', textarea.value)
}

function onOutputTypeChange(event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-output-type', select.value as 'commentary' | 'score' | 'binary' | 'all')
}

function getEvaluationPlaceholder(nodeType: string): string {
  const placeholders: Record<string, { en: string; de: string }> = {
    fairness_evaluation: {
      en: 'Check for stereotypes, bias, and fair representation...',
      de: 'Prüfung auf Stereotype, Vorurteile und faire Repräsentation...'
    },
    creativity_evaluation: {
      en: 'Evaluate originality. Avoid stock photo aesthetics...',
      de: 'Bewerte Originalität. Vermeide Stock-Foto-Ästhetik...'
    },
    equity_evaluation: {
      en: 'Evaluate cultural sensitivity and representational equity...',
      de: 'Bewerte kulturelle Sensibilität und Repräsentations-Equity...'
    },
    quality_evaluation: {
      en: 'Evaluate technical quality, composition, and clarity...',
      de: 'Bewerte technische Qualität, Komposition und Klarheit...'
    },
    custom_evaluation: {
      en: 'Define your own evaluation criteria...',
      de: 'Definiere deine eigenen Bewertungskriterien...'
    }
  }

  const placeholder = placeholders[nodeType]
  if (!placeholder) return locale.value === 'de' ? 'Bewertungskriterien...' : 'Evaluation criteria...'
  return locale.value === 'de' ? placeholder.de : placeholder.en
}

// Session 134: Display node handlers
function onDisplayTitleChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-display-title', input.value)
}

function onDisplayModeChange(event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-display-mode', select.value as 'popup' | 'inline' | 'toast')
}

// Session 134: Fork node handlers
function onThresholdChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-threshold-value', parseFloat(input.value) || 0)
}

function onTrueLabelChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-fork-labels', input.value, props.node.falseLabel || 'False')
}

function onFalseLabelChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-fork-labels', props.node.trueLabel || 'True', input.value)
}

// Resize handling (for Collector nodes)
const isResizing = ref(false)
const resizeStartSize = ref({ width: 0, height: 0 })
const resizeStartPos = ref({ x: 0, y: 0 })
const currentResizeSize = ref({ width: 0, height: 0 })

function startResize(event: MouseEvent) {
  event.stopPropagation()
  event.preventDefault()

  isResizing.value = true
  resizeStartPos.value = { x: event.clientX, y: event.clientY }
  resizeStartSize.value = {
    width: props.node.width || 280,
    height: props.node.height || 200
  }
  currentResizeSize.value = { ...resizeStartSize.value }

  // Add global mouse event listeners
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

function handleResize(event: MouseEvent) {
  if (!isResizing.value) return

  const deltaX = event.clientX - resizeStartPos.value.x
  const deltaY = event.clientY - resizeStartPos.value.y

  currentResizeSize.value.width = Math.max(180, resizeStartSize.value.width + deltaX)
  currentResizeSize.value.height = Math.max(100, resizeStartSize.value.height + deltaY)
}

function stopResize() {
  if (isResizing.value) {
    // Emit final size on mouseup
    emit('update-size', currentResizeSize.value.width, currentResizeSize.value.height)
  }

  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// Computed dimensions (use custom size if set, or live resize size, otherwise auto)
const nodeWidth = computed(() => {
  if (isResizing.value) return `${currentResizeSize.value.width}px`
  if (props.node.width) return `${props.node.width}px`
  return undefined
})
const nodeHeight = computed(() => {
  if (isResizing.value) return `${currentResizeSize.value.height}px`
  if (props.node.height) return `${props.node.height}px`
  return undefined
})
</script>

<template>
  <div
    class="stage-module"
    :class="{
      selected,
      'needs-config': !isConfigured,
      'wide-module': needsLLM || isInput || hasCollectorOutput || isEvaluation,
      'resizable': isCollector
    }"
    :style="{
      left: `${node.x}px`,
      top: `${node.y}px`,
      '--node-color': nodeColor,
      width: nodeWidth,
      height: nodeHeight
    }"
    @mousedown.stop="emit('mousedown', $event)"
  >
    <!-- Input connector -->
    <div
      v-if="hasInputConnector"
      class="connector input"
      @mouseup.stop="emit('end-connect')"
    />

    <!-- Node header -->
    <div class="module-header">
      <img
        v-if="nodeIconUrl"
        :src="nodeIconUrl"
        :alt="nodeLabel"
        class="module-icon-svg"
      />
      <span v-else class="module-icon">{{ nodeIcon }}</span>
      <span class="module-label">{{ nodeLabel }}</span>
      <button
        v-if="canDelete"
        class="delete-btn"
        @click.stop="emit('delete')"
        :title="locale === 'de' ? 'Löschen' : 'Delete'"
      >
        ×
      </button>
      <span v-else class="lock-icon" :title="locale === 'de' ? 'Gesperrt' : 'Locked'">🔒</span>
    </div>

    <!-- Node body -->
    <div class="module-body">

      <!-- INPUT NODE: Prompt text input (FIRST to ensure it matches) -->
      <template v-if="node.type === 'input'">
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Prompt' : 'Prompt' }}</label>
          <textarea
            class="prompt-textarea"
            :value="node.promptText || ''"
            :placeholder="locale === 'de' ? 'Dein Prompt...' : 'Your prompt...'"
            rows="4"
            @input="onPromptTextChange"
            @mousedown.stop
          />
        </div>
      </template>

      <!-- INTERCEPTION NODE: LLM dropdown + Context prompt -->
      <template v-else-if="isInterception">
        <div class="field-group">
          <label class="field-label">LLM</label>
          <select
            class="llm-select"
            :value="node.llmModel || ''"
            @change="onLLMChange"
            @mousedown.stop
          >
            <option value="" disabled>{{ locale === 'de' ? 'LLM wählen...' : 'Select LLM...' }}</option>
            <option
              v-for="model in llmModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Context-Prompt' : 'Context Prompt' }}</label>
          <textarea
            class="prompt-textarea"
            :value="node.contextPrompt || ''"
            :placeholder="locale === 'de' ? 'Transformations-Anweisungen...' : 'Transformation instructions...'"
            rows="3"
            @input="onContextPromptChange"
            @mousedown.stop
          />
        </div>
      </template>

      <!-- TRANSLATION NODE: LLM dropdown + Translation prompt -->
      <template v-else-if="isTranslation">
        <div class="field-group">
          <label class="field-label">LLM</label>
          <select
            class="llm-select"
            :value="node.llmModel || ''"
            @change="onLLMChange"
            @mousedown.stop
          >
            <option value="" disabled>{{ locale === 'de' ? 'LLM wählen...' : 'Select LLM...' }}</option>
            <option
              v-for="model in llmModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Übersetzungs-Prompt' : 'Translation Prompt' }}</label>
          <textarea
            class="prompt-textarea"
            :value="node.translationPrompt || ''"
            :placeholder="locale === 'de' ? 'Übersetzungsanweisungen...' : 'Translation instructions...'"
            rows="2"
            @input="onTranslationPromptChange"
            @mousedown.stop
          />
        </div>
      </template>

      <!-- GENERATION NODE: Config selector button -->
      <template v-else-if="isGeneration">
        <button
          class="config-selector"
          :class="{ 'has-config': !!node.configId }"
          @click.stop="emit('select-config')"
        >
          {{ displayConfigName }}
          <span class="config-arrow">▼</span>
        </button>
      </template>

      <!-- COLLECTOR NODE: Display collected outputs -->
      <template v-else-if="node.type === 'collector'">
        <div v-if="collectorOutput && collectorOutput.length > 0" class="collector-results">
          <div
            v-for="(item, idx) in collectorOutput"
            :key="idx"
            class="collector-item"
            :class="{ 'has-error': item.error }"
          >
            <div class="collector-item-header">
              <span class="item-type">{{ item.nodeType }}</span>
              <span v-if="item.error" class="item-error-badge">!</span>
            </div>
            <div class="collector-item-content">
              <template v-if="item.error">
                <span class="error-text">{{ item.error }}</span>
              </template>
              <!-- Session 134: Evaluation output display -->
              <template v-else-if="item.nodeType === 'evaluation' && typeof item.output === 'object' && item.output !== null">
                <div class="evaluation-result">
                  <div v-if="(item.output as any).score !== null && (item.output as any).score !== undefined" class="eval-score">
                    <span class="eval-label">{{ locale === 'de' ? 'Punktzahl' : 'Score' }}:</span>
                    <span class="eval-value">{{ (item.output as any).score }}/10</span>
                  </div>
                  <div v-if="(item.output as any).binary !== null && (item.output as any).binary !== undefined" class="eval-binary">
                    <span class="eval-label">{{ locale === 'de' ? 'Ergebnis' : 'Result' }}:</span>
                    <span class="eval-value" :class="{ 'pass': (item.output as any).binary, 'fail': !(item.output as any).binary }">
                      {{ (item.output as any).binary ? (locale === 'de' ? 'Bestanden' : 'Pass') : (locale === 'de' ? 'Nicht bestanden' : 'Fail') }}
                    </span>
                  </div>
                  <div v-if="(item.output as any).commentary" class="eval-commentary">
                    <span class="eval-label">{{ locale === 'de' ? 'Kommentar' : 'Commentary' }}:</span>
                    <p class="eval-text">{{ (item.output as any).commentary }}</p>
                  </div>
                </div>
              </template>
              <template v-else-if="typeof item.output === 'object' && item.output !== null && (item.output as any).url">
                <!-- Generation output: show image/media -->
                <img
                  v-if="(item.output as any).media_type === 'image' || !(item.output as any).media_type"
                  :src="(item.output as any).url"
                  class="collector-image"
                  :alt="`Generated by ${item.nodeType}`"
                />
                <div v-else class="collector-media-info">
                  {{ (item.output as any).media_type }}: {{ (item.output as any).url }}
                </div>
                <div class="collector-image-info">
                  seed: {{ (item.output as any).seed }}
                </div>
              </template>
              <template v-else-if="typeof item.output === 'string'">
                {{ item.output.slice(0, 200) }}{{ item.output.length > 200 ? '...' : '' }}
              </template>
              <template v-else>
                {{ JSON.stringify(item.output).slice(0, 100) }}...
              </template>
            </div>
          </div>
        </div>
        <div v-else class="collector-empty">
          <span class="module-type-info">
            {{ locale === 'de' ? 'Warte auf Ausführung...' : 'Waiting for execution...' }}
          </span>
        </div>
      </template>

      <!-- EVALUATION NODES: LLM dropdown + Evaluation prompt + Output type -->
      <template v-else-if="isEvaluation">
        <div class="field-group">
          <label class="field-label">LLM</label>
          <select
            class="llm-select"
            :value="node.llmModel || ''"
            @change="onLLMChange"
            @mousedown.stop
          >
            <option value="" disabled>{{ locale === 'de' ? 'LLM wählen...' : 'Select LLM...' }}</option>
            <option
              v-for="model in llmModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Bewertungs-Kriterien' : 'Evaluation Criteria' }}</label>
          <textarea
            class="prompt-textarea"
            :value="node.evaluationPrompt || ''"
            :placeholder="getEvaluationPlaceholder(node.type)"
            rows="3"
            @input="onEvaluationPromptChange"
            @mousedown.stop
          />
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Ausgabe-Typ' : 'Output Type' }}</label>
          <select
            class="llm-select"
            :value="node.outputType || 'all'"
            @change="onOutputTypeChange"
            @mousedown.stop
          >
            <option value="commentary">{{ locale === 'de' ? 'Kommentar' : 'Commentary' }}</option>
            <option value="score">{{ locale === 'de' ? 'Punktzahl' : 'Score' }}</option>
            <option value="binary">{{ locale === 'de' ? 'Pass/Fail' : 'Binary' }}</option>
            <option value="all">{{ locale === 'de' ? 'Alle' : 'All' }}</option>
          </select>
        </div>
      </template>

      <!-- DISPLAY NODE: Title + Display mode -->
      <template v-else-if="isDisplay">
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Titel' : 'Title' }}</label>
          <input
            type="text"
            class="llm-select"
            :value="node.title || ''"
            :placeholder="locale === 'de' ? 'Anzeige-Titel...' : 'Display title...'"
            @input="onDisplayTitleChange"
            @mousedown.stop
          />
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Anzeige-Modus' : 'Display Mode' }}</label>
          <select
            class="llm-select"
            :value="node.displayMode || 'inline'"
            @change="onDisplayModeChange"
            @mousedown.stop
          >
            <option value="inline">{{ locale === 'de' ? 'Inline' : 'Inline' }}</option>
            <option value="toast">{{ locale === 'de' ? 'Toast-Nachricht' : 'Toast' }}</option>
            <option value="popup">{{ locale === 'de' ? 'Popup' : 'Popup' }}</option>
          </select>
        </div>
        <div class="display-info">
          <span class="module-type-info">
            {{ locale === 'de' ? 'Zeigt Ergebnisse an (nicht-blockierend)' : 'Shows results (non-blocking)' }}
          </span>
        </div>
      </template>

      <!-- FORK NODES: Binary/Threshold branching -->
      <template v-else-if="isFork">
        <div v-if="isThresholdFork" class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Schwellwert (0-10)' : 'Threshold (0-10)' }}</label>
          <input
            type="number"
            min="0"
            max="10"
            step="0.1"
            class="llm-select"
            :value="node.thresholdValue || 5"
            @input="onThresholdChange"
            @mousedown.stop
          />
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? '"Wahr"-Pfad-Label' : 'True Path Label' }}</label>
          <input
            type="text"
            class="llm-select"
            :value="node.trueLabel || (locale === 'de' ? 'Wahr' : 'True')"
            :placeholder="locale === 'de' ? 'z.B. Bestanden' : 'e.g. Approved'"
            @input="onTrueLabelChange"
            @mousedown.stop
          />
        </div>
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? '"Falsch"-Pfad-Label' : 'False Path Label' }}</label>
          <input
            type="text"
            class="llm-select"
            :value="node.falseLabel || (locale === 'de' ? 'Falsch' : 'False')"
            :placeholder="locale === 'de' ? 'z.B. Revision nötig' : 'e.g. Needs Revision'"
            @input="onFalseLabelChange"
            @mousedown.stop
          />
        </div>
        <div class="fork-info">
          <span class="module-type-info">
            {{ isThresholdFork
              ? (locale === 'de' ? 'Verzweigt basierend auf Punktzahl' : 'Branches based on score')
              : (locale === 'de' ? 'Verzweigt basierend auf wahr/falsch' : 'Branches based on true/false') }}
          </span>
        </div>
      </template>

      <!-- Other node types -->
      <template v-else>
        <span class="module-type-info">{{ node.type }}</span>
      </template>
    </div>

    <!-- Output connector (standard single output) -->
    <div
      v-if="hasOutputConnector && !isFork"
      class="connector output"
      @mousedown.stop="emit('start-connect')"
    />

    <!-- Fork output connectors (multiple labeled outputs) -->
    <div v-if="isFork" class="fork-outputs">
      <div
        class="connector output output-true"
        @mousedown.stop="emit('start-connect-labeled', 'true')"
        :title="node.trueLabel || (locale === 'de' ? 'Wahr' : 'True')"
      >
        <span class="connector-label">{{ node.trueLabel || (locale === 'de' ? 'W' : 'T') }}</span>
      </div>
      <div
        class="connector output output-false"
        @mousedown.stop="emit('start-connect-labeled', 'false')"
        :title="node.falseLabel || (locale === 'de' ? 'Falsch' : 'False')"
      >
        <span class="connector-label">{{ node.falseLabel || (locale === 'de' ? 'F' : 'F') }}</span>
      </div>
    </div>

    <!-- Resize handle (only for collector nodes) -->
    <div
      v-if="isCollector"
      class="resize-handle"
      @mousedown.stop="startResize"
      :title="locale === 'de' ? 'Größe ändern' : 'Resize'"
    />
  </div>
</template>

<style scoped>
.stage-module {
  position: absolute;
  min-width: 180px;
  background: #1e293b;
  border: 2px solid var(--node-color);
  border-radius: 8px;
  cursor: move;
  user-select: none;
  z-index: 1;
}

.stage-module.wide-module {
  min-width: 280px;
}

.stage-module.selected {
  box-shadow: 0 0 0 2px var(--node-color), 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.stage-module.needs-config {
  border-style: dashed;
}

.module-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--node-color);
  border-radius: 5px 5px 0 0;
}

.module-icon {
  font-size: 1rem;
}

.module-icon-svg {
  width: 18px;
  height: 18px;
  filter: brightness(0) invert(1); /* Make SVG white */
}

.module-label {
  flex: 1;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.delete-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.delete-btn:hover {
  color: white;
}

.lock-icon {
  font-size: 0.75rem;
  opacity: 0.7;
}

.module-body {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.625rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.llm-select {
  width: 100%;
  padding: 0.375rem 0.5rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 4px;
  color: #e2e8f0;
  font-size: 0.75rem;
  cursor: pointer;
}

.llm-select:hover {
  border-color: var(--node-color);
}

.llm-select:focus {
  outline: none;
  border-color: var(--node-color);
}

.prompt-textarea {
  width: 100%;
  padding: 0.375rem 0.5rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 4px;
  color: #e2e8f0;
  font-size: 0.6875rem;
  font-family: inherit;
  resize: vertical;
  min-height: 40px;
}

.prompt-textarea:hover {
  border-color: var(--node-color);
}

.prompt-textarea:focus {
  outline: none;
  border-color: var(--node-color);
}

.prompt-textarea::placeholder {
  color: #475569;
}

.config-selector {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 4px;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.config-selector:hover {
  border-color: var(--node-color);
  color: #e2e8f0;
}

.config-selector.has-config {
  color: #e2e8f0;
  border-color: var(--node-color);
}

.config-arrow {
  font-size: 0.6rem;
  opacity: 0.7;
}

.module-type-info {
  font-size: 0.6875rem;
  color: #64748b;
}

.connector {
  position: absolute;
  width: 14px;
  height: 14px;
  background: #1e293b;
  border: 2px solid var(--node-color);
  border-radius: 50%;
  cursor: crosshair;
  z-index: 2;
}

.connector.input {
  left: -7px;
  top: 50%;
  transform: translateY(-50%);
}

.connector.output {
  right: -7px;
  top: 50%;
  transform: translateY(-50%);
}

.connector:hover {
  background: var(--node-color);
}

/* Collector node styles */
.collector-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  /* Auto-resize: no max-height constraint */
  overflow-y: auto;
}

.collector-item {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 4px;
  padding: 0.5rem;
}

.collector-item.has-error {
  border-color: #ef4444;
}

.collector-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.item-type {
  font-size: 0.625rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
}

.item-error-badge {
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  font-weight: bold;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collector-item-content {
  font-size: 0.6875rem;
  color: #e2e8f0;
  word-break: break-word;
  white-space: pre-wrap;
}

.error-text {
  color: #ef4444;
}

.collector-empty {
  text-align: center;
  padding: 0.5rem;
}

.collector-image {
  max-width: 100%;
  border-radius: 4px;
  margin-top: 0.25rem;
  display: block;
}

.collector-media-info {
  font-size: 0.625rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.collector-image-info {
  font-size: 0.625rem;
  color: #64748b;
  margin-top: 0.25rem;
}

/* Resize handle */
.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 50%, var(--node-color) 50%);
  opacity: 0.5;
  transition: opacity 0.15s;
  z-index: 3;
}

.resize-handle:hover {
  opacity: 1;
}

.stage-module.resizable {
  /* Allow custom dimensions */
  width: auto;
  height: auto;
}

/* Session 134: Evaluation result display */
.evaluation-result {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 4px;
  border-left: 3px solid #f59e0b;
}

.eval-score,
.eval-binary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.eval-label {
  font-weight: 600;
  color: #f59e0b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.625rem;
}

.eval-value {
  color: #e2e8f0;
  font-weight: 500;
}

.eval-value.pass {
  color: #10b981;
}

.eval-value.fail {
  color: #ef4444;
}

.eval-commentary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.eval-text {
  font-size: 0.75rem;
  color: #cbd5e1;
  line-height: 1.4;
  margin: 0;
  white-space: pre-wrap;
}

/* Display node info */
.display-info {
  padding: 0.5rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 4px;
  margin-top: 0.5rem;
}

.display-info .module-type-info {
  font-size: 0.625rem;
  color: #10b981;
  font-style: italic;
}

/* Fork node styles */
.fork-info {
  padding: 0.5rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 4px;
  margin-top: 0.5rem;
}

.fork-info .module-type-info {
  font-size: 0.625rem;
  color: #ef4444;
  font-style: italic;
}

.fork-outputs {
  position: absolute;
  right: -14px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 2;
}

.fork-outputs .connector {
  position: relative;
  width: 14px;
  height: 14px;
  background: var(--node-color);
  border: 2px solid #1e293b;
  border-radius: 50%;
  cursor: crosshair;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fork-outputs .connector-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: white;
  user-select: none;
  pointer-events: none;
}

.fork-outputs .output-true {
  background: #10b981;
}

.fork-outputs .output-false {
  background: #ef4444;
}

.fork-outputs .connector:hover {
  transform: scale(1.15);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
}
</style>
