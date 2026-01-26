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
  configMediaType?: string
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
  /** Session 135: Is this node currently active in bubble animation? */
  isActive?: boolean
}>()

const emit = defineEmits<{
  'mousedown': [e: MouseEvent]
  'start-connect': []
  'end-connect': []
  'end-connect-feedback': []
  'delete': []
  'select-config': []
  'update-llm': [llmModel: string]
  'update-context-prompt': [prompt: string]
  'update-translation-prompt': [prompt: string]
  'update-prompt-text': [text: string]
  'update-size': [width: number, height: number]
  'update-display-title': [title: string]
  'update-display-mode': [mode: 'popup' | 'inline' | 'toast']
  // Session 134 Refactored: Unified evaluation events
  'update-evaluation-type': [type: 'fairness' | 'creativity' | 'equity' | 'quality' | 'custom']
  'update-evaluation-prompt': [prompt: string]
  'update-output-type': [outputType: 'commentary' | 'score' | 'all']
  'update-enable-branching': [enabled: boolean]
  'update-branch-condition': [condition: 'binary' | 'threshold']
  'update-threshold-value': [threshold: number]
  'update-branch-labels': [trueLabel: string, falseLabel: string]
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
// Session 134 Refactored: Unified evaluation node
const isEvaluation = computed(() => props.node.type === 'evaluation')
const needsLLM = computed(() => isInterception.value || isTranslation.value || isEvaluation.value)
const hasCollectorOutput = computed(() => isCollector.value && props.collectorOutput && props.collectorOutput.length > 0)
// Evaluation branching
const hasBranching = computed(() => isEvaluation.value && props.node.enableBranching === true)
// Feedback input for Interception/Translation (enables feedback loops)
const hasFeedbackInput = computed(() => isInterception.value || isTranslation.value)

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

// Output bubble: shows truncated output when node has executed
const bubbleContent = computed(() => {
  if (!props.executionResult?.output) return null
  const output = props.executionResult.output

  // Handle different output types
  if (typeof output === 'string') {
    return output.length > 60 ? output.slice(0, 60) + '...' : output
  }
  if (typeof output === 'object' && output !== null) {
    // Image/media output
    if ((output as any).url) {
      return (output as any).media_type === 'image' ? '🖼️' : '📦'
    }
    // Evaluation with metadata
    if ((output as any).metadata?.score !== undefined) {
      const meta = (output as any).metadata
      return `Score: ${meta.score}/10 ${meta.binary ? '✓' : '✗'}`
    }
    // Other object
    return JSON.stringify(output).slice(0, 40) + '...'
  }
  return String(output).slice(0, 60)
})

const showBubble = computed(() => {
  // Show bubble only when:
  // 1. Node is active in animation (or animation not running = isActive undefined)
  // 2. Node has output content
  // 3. Node is not a terminal (collector/display)
  const isAnimationActive = props.isActive !== undefined
  const shouldShow = isAnimationActive ? props.isActive : bubbleContent.value !== null
  return shouldShow && bubbleContent.value && !isCollector.value && !isDisplay.value
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

// Session 134 Refactored: Unified evaluation node handlers
function onEvaluationTypeChange(event: Event) {
  const select = event.target as HTMLSelectElement
  const newType = select.value as 'fairness' | 'creativity' | 'equity' | 'quality' | 'custom'
  emit('update-evaluation-type', newType)

  // Auto-fill prompt based on type
  const prompt = getEvaluationPromptTemplate(newType)
  emit('update-evaluation-prompt', prompt)
}

function onEvaluationPromptChange(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  emit('update-evaluation-prompt', textarea.value)
}

function onOutputTypeChange(event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-output-type', select.value as 'commentary' | 'score' | 'all')
}

function onEnableBranchingChange(event: Event) {
  const checkbox = event.target as HTMLInputElement
  emit('update-enable-branching', checkbox.checked)
}

function onBranchConditionChange(event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-branch-condition', select.value as 'binary' | 'threshold')
}

function getEvaluationPromptTemplate(evalType: string): string {
  const templates: Record<string, { en: string; de: string }> = {
    fairness: {
      en: 'Check for stereotypes, bias, and fair representation. Evaluate whether this content reinforces harmful stereotypes or promotes diverse, equitable representation.',
      de: 'Prüfe auf Stereotype, Vorurteile und faire Repräsentation. Bewerte, ob dieser Inhalt schädliche Stereotype verstärkt oder vielfältige, gerechte Darstellung fördert.'
    },
    creativity: {
      en: 'Evaluate originality and creative quality. Check if the content shows genuine creativity or resembles generic stock imagery/text.',
      de: 'Bewerte Originalität und kreative Qualität. Prüfe, ob der Inhalt echte Kreativität zeigt oder generischen Stock-Bildern/-Texten ähnelt.'
    },
    equity: {
      en: 'Evaluate cultural sensitivity and representational equity. Check for respectful portrayal of diverse cultures and communities.',
      de: 'Bewerte kulturelle Sensibilität und Repräsentations-Equity. Prüfe auf respektvolle Darstellung verschiedener Kulturen und Gemeinschaften.'
    },
    quality: {
      en: 'Evaluate technical quality, composition, and clarity. Check for coherence, visual/textual quality, and overall execution.',
      de: 'Bewerte technische Qualität, Komposition und Klarheit. Prüfe auf Kohärenz, visuelle/textuelle Qualität und Gesamtumsetzung.'
    },
    custom: {
      en: 'Define your own evaluation criteria...',
      de: 'Definiere deine eigenen Bewertungskriterien...'
    }
  }

  const template = templates[evalType]
  if (!template) return locale.value === 'de' ? 'Bewertungskriterien...' : 'Evaluation criteria...'
  return locale.value === 'de' ? template.de : template.en
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

function onThresholdChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-threshold-value', parseFloat(input.value) || 0)
}

function onTrueLabelChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-branch-labels', input.value, props.node.falseLabel || (locale.value === 'de' ? 'Falsch' : 'False'))
}

function onFalseLabelChange(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update-branch-labels', props.node.trueLabel || (locale.value === 'de' ? 'Wahr' : 'True'), input.value)
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
      'wide-module': needsLLM || isInput || hasCollectorOutput || isEvaluation || isDisplay,
      'resizable': isCollector || isDisplay
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
    <!-- Input connector (normal) -->
    <div
      v-if="hasInputConnector"
      class="connector input"
      :data-node-id="node.id"
      data-connector="input"
      @mouseup.stop="emit('end-connect')"
    />

    <!-- Feedback input connector (for Interception/Translation nodes) -->
    <div
      v-if="hasFeedbackInput"
      class="connector feedback-input"
      :data-node-id="node.id"
      data-connector="feedback-input"
      @mouseup.stop="emit('end-connect-feedback')"
      :title="locale === 'de' ? 'Feedback-Eingang' : 'Feedback Input'"
    >
      <span class="feedback-label">FB</span>
    </div>

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

      <!-- GENERATION NODE: Config selector button with media type icon -->
      <template v-else-if="isGeneration">
        <button
          class="config-selector"
          :class="{ 'has-config': !!node.configId }"
          @click.stop="emit('select-config')"
        >
          <span class="config-media-icon">
            <!-- Image -->
            <svg v-if="configMediaType === 'image'" xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
              <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/>
            </svg>
            <!-- Video -->
            <svg v-else-if="configMediaType === 'video'" xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
              <path d="m380-300 280-180-280-180v360ZM160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm0-80h640v-480H160v480Zm0 0v-480 480Z"/>
            </svg>
            <!-- Audio / Music -->
            <svg v-else-if="configMediaType === 'audio' || configMediaType === 'music'" xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
              <path d="M400-120q-66 0-113-47t-47-113q0-66 47-113t113-47q23 0 42.5 5.5T480-418v-422h240v160H560v400q0 66-47 113t-113 47Z"/>
            </svg>
            <!-- Text -->
            <svg v-else-if="configMediaType === 'text'" xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
              <path d="M280-160v-520H80v-120h520v120H400v520H280Zm360 0v-320H520v-120h360v120H760v320H640Z"/>
            </svg>
            <!-- No config selected -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor" opacity="0.5">
              <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/>
            </svg>
          </span>
          <span class="config-name-text">{{ displayConfigName }}</span>
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
              <!-- Session 134 Refactored: Evaluation output display with metadata -->
              <template v-else-if="item.nodeType === 'evaluation' && typeof item.output === 'object' && item.output !== null && (item.output as any).metadata">
                <div class="evaluation-result">
                  <!-- Show metadata: binary result and score -->
                  <div class="eval-metadata">
                    <div v-if="(item.output as any).metadata.score !== null && (item.output as any).metadata.score !== undefined" class="eval-score">
                      <span class="eval-label">Score:</span>
                      <span class="eval-value">{{ (item.output as any).metadata.score }}/10</span>
                    </div>
                    <div v-if="(item.output as any).metadata.binary !== null && (item.output as any).metadata.binary !== undefined" class="eval-binary">
                      <span class="eval-value" :class="{ 'pass': (item.output as any).metadata.binary, 'fail': !(item.output as any).metadata.binary }">
                        {{ (item.output as any).metadata.binary ? '✓ Pass' : '✗ Fail' }}
                      </span>
                    </div>
                  </div>
                  <!-- Show the text that was passed through -->
                  <div v-if="(item.output as any).text" class="eval-text-output">
                    <p class="eval-text">{{ (item.output as any).text }}</p>
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
                {{ item.output }}
              </template>
              <template v-else-if="item.output != null">
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

      <!-- EVALUATION NODE: Unified evaluation with optional branching -->
      <template v-else-if="isEvaluation">
        <!-- Evaluation Type -->
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Bewertungstyp' : 'Evaluation Type' }}</label>
          <select
            class="llm-select"
            :value="node.evaluationType || 'custom'"
            @change="onEvaluationTypeChange"
            @mousedown.stop
          >
            <option value="fairness">{{ locale === 'de' ? 'Fairness' : 'Fairness' }}</option>
            <option value="creativity">{{ locale === 'de' ? 'Kreativität' : 'Creativity' }}</option>
            <option value="equity">{{ locale === 'de' ? 'Equity' : 'Equity' }}</option>
            <option value="quality">{{ locale === 'de' ? 'Qualität' : 'Quality' }}</option>
            <option value="custom">{{ locale === 'de' ? 'Eigene' : 'Custom' }}</option>
          </select>
        </div>

        <!-- LLM Selection -->
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

        <!-- Evaluation Criteria -->
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Bewertungskriterien' : 'Evaluation Criteria' }}</label>
          <textarea
            class="prompt-textarea"
            :value="node.evaluationPrompt || getEvaluationPromptTemplate(node.evaluationType || 'custom')"
            rows="3"
            @input="onEvaluationPromptChange"
            @mousedown.stop
          />
        </div>

        <!-- Output Type (score optional) -->
        <div class="field-group">
          <label class="field-label">{{ locale === 'de' ? 'Ausgabe-Typ' : 'Output Type' }}</label>
          <select
            class="llm-select"
            :value="node.outputType || 'commentary'"
            @change="onOutputTypeChange"
            @mousedown.stop
          >
            <option value="commentary">{{ locale === 'de' ? 'Kommentar + Binary' : 'Commentary + Binary' }}</option>
            <option value="score">{{ locale === 'de' ? 'Kommentar + Score + Binary' : 'Commentary + Score + Binary' }}</option>
            <option value="all">{{ locale === 'de' ? 'Alle' : 'All' }}</option>
          </select>
        </div>

        <!-- Enable Branching Checkbox -->
        <div class="field-group">
          <label class="field-checkbox">
            <input
              type="checkbox"
              :checked="node.enableBranching || false"
              @change="onEnableBranchingChange"
              @mousedown.stop
            />
            <span>{{ locale === 'de' ? 'Verzweigung aktivieren' : 'Enable Branching' }}</span>
          </label>
        </div>

        <!-- Conditional Branching UI -->
        <template v-if="node.enableBranching">
          <div class="branching-section">
            <div class="field-group">
              <label class="field-label">{{ locale === 'de' ? 'Verzweigungsbedingung' : 'Branch Condition' }}</label>
              <select
                class="llm-select"
                :value="node.branchCondition || 'binary'"
                @change="onBranchConditionChange"
                @mousedown.stop
              >
                <option value="binary">{{ locale === 'de' ? 'Binary (Pass/Fail)' : 'Binary (Pass/Fail)' }}</option>
                <option value="threshold">{{ locale === 'de' ? 'Schwellwert (Score)' : 'Threshold (Score)' }}</option>
              </select>
            </div>

            <div v-if="node.branchCondition === 'threshold'" class="field-group">
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
              <label class="field-label">{{ locale === 'de' ? 'Label "Pass/True"' : 'True Path Label' }}</label>
              <input
                type="text"
                class="llm-select"
                :value="node.trueLabel || (locale === 'de' ? 'Bestanden' : 'Approved')"
                :placeholder="locale === 'de' ? 'z.B. Bestanden' : 'e.g. Approved'"
                @input="onTrueLabelChange"
                @mousedown.stop
              />
            </div>

            <div class="field-group">
              <label class="field-label">{{ locale === 'de' ? 'Label "Fail/False"' : 'False Path Label' }}</label>
              <input
                type="text"
                class="llm-select"
                :value="node.falseLabel || (locale === 'de' ? 'Revision nötig' : 'Needs Revision')"
                :placeholder="locale === 'de' ? 'z.B. Revision nötig' : 'e.g. Needs Revision'"
                @input="onFalseLabelChange"
                @mousedown.stop
              />
            </div>
          </div>
        </template>
      </template>

      <!-- PREVIEW NODE: Shows content inline (pass-through) -->
      <template v-else-if="isDisplay">
        <div v-if="executionResult?.output" class="preview-content">
          <!-- Text preview (full text, scrollable) -->
          <template v-if="typeof executionResult.output === 'string'">
            <div class="preview-text">
              {{ executionResult.output }}
            </div>
          </template>
          <!-- Media preview (image/video) -->
          <template v-else-if="typeof executionResult.output === 'object' && (executionResult.output as any)?.url">
            <img
              v-if="(executionResult.output as any).media_type === 'image' || !(executionResult.output as any).media_type"
              :src="(executionResult.output as any).url"
              class="preview-image"
              :alt="locale === 'de' ? 'Vorschau' : 'Preview'"
            />
            <div v-else class="preview-media-info">
              {{ (executionResult.output as any).media_type }}: {{ (executionResult.output as any).url }}
            </div>
          </template>
          <template v-else-if="executionResult.output != null">
            <div class="preview-text">
              {{ JSON.stringify(executionResult.output).slice(0, 100) }}...
            </div>
          </template>
        </div>
        <div v-else-if="!executionResult" class="preview-empty">
          <span class="module-type-info">
            {{ locale === 'de' ? 'Vorschau (nach Ausführung)' : 'Preview (after execution)' }}
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
      v-if="hasOutputConnector && !hasBranching"
      class="connector output"
      :data-node-id="node.id"
      data-connector="output"
      @mousedown.stop="emit('start-connect')"
    />

    <!-- Output bubble: shows data flowing through -->
    <div v-if="showBubble" class="output-bubble">
      <span class="bubble-content">{{ bubbleContent }}</span>
    </div>

    <!-- Evaluation outputs: 3 separate text outputs (passthrough, commented, commentary) -->
    <div v-if="isEvaluation && node.enableBranching" class="eval-outputs">
      <div
        class="connector output output-passthrough"
        :data-node-id="node.id"
        data-connector="output-passthrough"
        @mousedown.stop="emit('start-connect-labeled', 'passthrough')"
        :title="locale === 'de' ? 'Passthrough (OK - unverändert)' : 'Passthrough (OK - unchanged)'"
      >
        <span class="connector-label">P</span>
      </div>
      <div
        class="connector output output-commented"
        :data-node-id="node.id"
        data-connector="output-commented"
        @mousedown.stop="emit('start-connect-labeled', 'commented')"
        :title="locale === 'de' ? 'Kommentiert (FAIL - mit Feedback)' : 'Commented (FAIL - with feedback)'"
      >
        <span class="connector-label">C</span>
      </div>
      <div
        class="connector output output-commentary"
        :data-node-id="node.id"
        data-connector="output-commentary"
        @mousedown.stop="emit('start-connect-labeled', 'commentary')"
        :title="locale === 'de' ? 'Nur Kommentar (für Anzeige)' : 'Commentary only (for display)'"
      >
        <span class="connector-label">→</span>
      </div>
    </div>

    <!-- Resize handle (only for collector nodes) -->
    <div
      v-if="isCollector || isDisplay"
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
  /* Note: overflow visible to allow bubbles, but module-body handles content overflow */
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
  overflow: auto;  /* Scroll when content exceeds container */
  flex: 1;  /* Fill available space in resizable nodes */
  min-height: 0;  /* Allow shrinking below content size */
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
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 4px;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.config-media-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.config-media-icon svg {
  display: block;
}

.config-name-text {
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  top: 24px;  /* Fixed position in header area */
  transform: translateY(-50%);
}

.connector.output {
  right: -7px;
  top: 24px;  /* Fixed position in header area */
  transform: translateY(-50%);
}

.connector:hover {
  background: var(--node-color);
}

/* Feedback input connector (for loops) */
.connector.feedback-input {
  right: -7px;
  top: 44px;  /* Below main connector in header area */
  transform: translateY(-50%);
  border-color: #f97316; /* Orange to distinguish from normal connectors */
  display: flex;
  align-items: center;
  justify-content: center;
}

.connector.feedback-input:hover {
  background: #f97316;
}

/* Output bubble: shows data flowing through the node */
.output-bubble {
  position: absolute;
  right: -12px;
  top: 40px;
  transform: translateX(100%);
  background: rgba(59, 130, 246, 0.95);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.6875rem;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  z-index: 20;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  animation: bubble-appear 0.3s ease-out;
  pointer-events: none;
}

.output-bubble::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
  border: 6px solid transparent;
  border-right-color: rgba(59, 130, 246, 0.95);
}

.bubble-content {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes bubble-appear {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateX(100%) scale(1);
  }
}

.feedback-label {
  font-size: 8px;
  font-weight: bold;
  color: #f97316;
  pointer-events: none;
}

.connector.feedback-input:hover .feedback-label {
  color: white;
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
  /* Allow custom dimensions but constrain max-width/height */
  width: auto;
  height: auto;
  max-width: 400px;   /* Prevent expanding beyond reasonable width */
  max-height: 600px;  /* Session 141: Prevent extremely tall nodes */
  display: flex;
  flex-direction: column;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Session 134 Refactored: Evaluation result display with 3 outputs */
.evaluation-result {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 4px;
  border-left: 3px solid #f59e0b;
}

.eval-metadata {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(245, 158, 11, 0.2);
}

.eval-score,
.eval-binary,
.eval-path {
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

.eval-commentary,
.eval-active-output {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.eval-active-output {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(245, 158, 11, 0.2);
}

.eval-text {
  font-size: 0.75rem;
  color: #cbd5e1;
  line-height: 1.4;
  margin: 0;
  white-space: pre-wrap;
  max-height: none;  /* Full text visible, container scrolls */
  overflow-y: visible;
}

/* Display node info */
/* Session 134 Refactored: Preview node inline display */
.preview-content {
  padding: 0.5rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 4px;
  border-left: 3px solid #10b981;
  max-height: none;  /* Node is resizable, no fixed limit */
  overflow-y: auto;
}

.preview-text {
  font-size: 0.75rem;
  color: #cbd5e1;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
}

.preview-image {
  max-width: 100%;
  max-height: 150px;
  border-radius: 4px;
  display: block;
}

.preview-media-info {
  font-size: 0.625rem;
  color: #94a3b8;
  font-style: italic;
}

.preview-empty {
  padding: 0.5rem;
  text-align: center;
}

.preview-empty .module-type-info {
  font-size: 0.625rem;
  color: #64748b;
  font-style: italic;
}

/* Session 134 Refactored: Unified evaluation node styles */
.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.75rem;
  color: #e2e8f0;
  user-select: none;
}

.field-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.branching-section {
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 4px;
  border-left: 3px solid #ef4444;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Evaluation outputs: 3 separate text outputs */
.eval-outputs {
  position: absolute;
  right: -16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 2;
}

.eval-outputs .connector {
  position: relative;
  width: 16px;
  height: 16px;
  background: var(--node-color);
  border: 2px solid #1e293b;
  border-radius: 50%;
  cursor: crosshair;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.eval-outputs .connector-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: white;
  user-select: none;
  pointer-events: none;
}

.eval-outputs .output-passthrough {
  background: #10b981; /* green - OK */
}

.eval-outputs .output-commented {
  background: #f59e0b; /* amber - needs revision */
}

.eval-outputs .output-commentary {
  background: #06b6d4; /* cyan - for display/control */
}

.eval-outputs .connector:hover {
  transform: scale(1.2);
  box-shadow: 0 0 10px currentColor;
}
</style>
