<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CanvasNode, LLMModelSummary } from '@/types/canvas'
import { getNodeTypeDefinition } from '@/types/canvas'

const { locale } = useI18n()

// Icon URL helper
function getIconUrl(iconPath: string): string {
  return new URL(`../../assets/icons/${iconPath}`, import.meta.url).href
}

const props = defineProps<{
  node: CanvasNode
  selected: boolean
  configName?: string
  llmModels?: LLMModelSummary[]
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
const isInterception = computed(() => props.node.type === 'interception')
const isTranslation = computed(() => props.node.type === 'translation')
const isGeneration = computed(() => props.node.type === 'generation')
const needsLLM = computed(() => isInterception.value || isTranslation.value)

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
</script>

<template>
  <div
    class="stage-module"
    :class="{
      selected,
      'needs-config': !isConfigured,
      'wide-module': needsLLM
    }"
    :style="{
      left: `${node.x}px`,
      top: `${node.y}px`,
      '--node-color': nodeColor
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

      <!-- INTERCEPTION NODE: LLM dropdown + Context prompt -->
      <template v-if="isInterception">
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

      <!-- Other node types (input, collector) -->
      <template v-else>
        <span class="module-type-info">{{ node.type }}</span>
      </template>
    </div>

    <!-- Output connector -->
    <div
      v-if="hasOutputConnector"
      class="connector output"
      @mousedown.stop="emit('start-connect')"
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
</style>
