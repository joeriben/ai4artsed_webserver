<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { NODE_TYPE_DEFINITIONS, type StageType, type NodeTypeDefinition } from '@/types/canvas'
import { localized } from '@/i18n'

const { locale } = useI18n()

// Icon URL helper
function getIconUrl(iconPath: string): string {
  return new URL(`../../assets/icons/${iconPath}`, import.meta.url).href
}

const emit = defineEmits<{
  'add-node': [type: StageType]
}>()

/**
 * Group node types by category
 *
 * NOTE: Safety is NOT shown here - DevServer handles it automatically
 * Session 134 Refactored: Unified evaluation node (replaces 5 eval + 2 fork nodes)
 */
const categories = computed(() => [
  {
    id: 'input',
    label: locale.value === 'de' ? '1 · Eingabe' : '1 · Input',
    // Session 152: Added image_input
    types: ['input', 'image_input', 'random_prompt'] as StageType[]
  },
  {
    id: 'interception',
    label: locale.value === 'de' ? '2 · Interception' : '2 · Interception',
    // Session 152: Added image_evaluation
    types: ['interception', 'evaluation', 'image_evaluation', 'comparison_evaluator'] as StageType[]
  },
  {
    id: 'adaption',
    label: locale.value === 'de' ? '3 · Adaption' : '3 · Adaption',
    types: ['translation', 'model_adaption'] as StageType[]
  },
  {
    id: 'generate',
    label: locale.value === 'de' ? '4 · Generierung' : '4 · Generation',
    types: ['generation'] as StageType[]
  },
  {
    id: 'tools',
    label: 'Tools',
    // Session 151: Parameter nodes (seed, resolution, quality) + display under Tools
    types: ['seed', 'resolution', 'quality', 'display'] as StageType[]
  }
])

function getNodeDef(type: StageType): NodeTypeDefinition | undefined {
  return NODE_TYPE_DEFINITIONS.find(n => n.type === type)
}

function getLabel(def: NodeTypeDefinition): string {
  return localized(def.label, locale.value)
}

function getDescription(def: NodeTypeDefinition): string {
  return localized(def.description, locale.value)
}

function onDragStart(e: DragEvent, type: StageType) {
  e.dataTransfer?.setData('nodeType', type)
  e.dataTransfer!.effectAllowed = 'copy'
}
</script>

<template>
  <div class="module-palette">
    <h3>{{ $t('canvas.modules') }}</h3>

    <div v-for="cat in categories" :key="cat.id" class="category">
      <h4>{{ cat.label }}</h4>
      <div class="module-list">
        <button
          v-for="type in cat.types"
          :key="type"
          class="module-btn"
          :style="{ '--node-color': getNodeDef(type)?.color }"
          :title="getNodeDef(type) ? getDescription(getNodeDef(type)!) : ''"
          draggable="true"
          @dragstart="onDragStart($event, type)"
          @click="emit('add-node', type)"
        >
          <img
            v-if="getNodeDef(type)?.icon?.endsWith('.svg')"
            :src="getIconUrl(getNodeDef(type)!.icon)"
            :alt="type"
            class="module-icon-svg"
          />
          <span v-else class="module-icon">{{ getNodeDef(type)?.icon }}</span>
          <span class="module-label">{{ getNodeDef(type) ? getLabel(getNodeDef(type)!) : type }}</span>
        </button>
      </div>
    </div>

    <div class="palette-help">
      <p v-if="locale === 'de'">
        Klicke oder ziehe Module auf die Arbeitsfläche
      </p>
      <p v-else>
        Click or drag modules onto the canvas
      </p>
    </div>
  </div>
</template>

<style scoped>
.module-palette {
  color: #e2e8f0;
  padding: 1rem;
}

h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.category {
  margin-bottom: 1.25rem;
}

h4 {
  font-size: 0.6875rem;
  font-weight: 500;
  margin: 0 0 0.5rem;
  color: #64748b;
  text-transform: uppercase;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.module-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--node-color);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.8125rem;
  font-weight: 500;
  text-align: left;
  cursor: grab;
  transition: all 0.15s;
}

.module-btn:hover {
  filter: brightness(1.1);
  transform: translateX(2px);
}

.module-btn:active {
  cursor: grabbing;
}

.module-icon {
  font-size: 1rem;
}

.module-icon-svg {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1); /* Make SVG white */
}

.module-label {
  flex: 1;
}

.palette-help {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #334155;
}

.palette-help p {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}
</style>
