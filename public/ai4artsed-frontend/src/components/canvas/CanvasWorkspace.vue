<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import StageModule from './StageModule.vue'
import ConnectionLine from './ConnectionLine.vue'
import type { CanvasNode, CanvasConnection, StageType, LLMModelSummary, OutputConfigSummary } from '@/types/canvas'

const { locale } = useI18n()

/** Collector output item from execution */
interface CollectorOutputItem {
  nodeId: string
  nodeType: string
  output: unknown
  error: string | null
}

const props = defineProps<{
  nodes: CanvasNode[]
  connections: CanvasConnection[]
  selectedNodeId: string | null
  connectingFromId: string | null
  mousePosition: { x: number; y: number }
  llmModels: LLMModelSummary[]
  /** Execution results per node (nodeId -> result) */
  executionResults?: Record<string, {
    type: string
    output: unknown
    error: string | null
    model?: string
  }>
  /** Collector output for collector nodes */
  collectorOutput?: CollectorOutputItem[]
  /** Available output configs for generation nodes */
  outputConfigs?: OutputConfigSummary[]
  /** Session 135: Active node for bubble animation */
  activeNodeId?: string | null
}>()

/**
 * Get config info for a node's configId
 */
function getConfigInfo(configId: string | undefined): { name: string; mediaType: string } | undefined {
  if (!configId || !props.outputConfigs) return undefined
  const config = props.outputConfigs.find(c => c.id === configId)
  if (!config) return undefined
  return {
    name: locale.value === 'de' ? config.name.de : config.name.en,
    mediaType: config.mediaType
  }
}

const emit = defineEmits<{
  'select-node': [id: string | null]
  'update-node-position': [id: string, x: number, y: number]
  'delete-node': [id: string]
  'add-connection': [sourceId: string, targetId: string]
  'delete-connection': [sourceId: string, targetId: string]
  'start-connection': [nodeId: string, label?: string]
  'cancel-connection': []
  'complete-connection': [targetId: string]
  'complete-connection-feedback': [targetId: string]
  'update-mouse-position': [x: number, y: number]
  'add-node-at': [type: StageType, x: number, y: number]
  'select-config': [nodeId: string]
  'update-node-llm': [nodeId: string, llmModel: string]
  'update-node-context-prompt': [nodeId: string, prompt: string]
  'update-node-translation-prompt': [nodeId: string, prompt: string]
  'update-node-prompt-text': [nodeId: string, text: string]
  'update-node-size': [nodeId: string, width: number, height: number]
  'update-node-display-title': [nodeId: string, title: string]
  'update-node-display-mode': [nodeId: string, mode: 'popup' | 'inline' | 'toast']
  // Session 134 Refactored: Unified evaluation events
  'update-node-evaluation-type': [nodeId: string, type: 'fairness' | 'creativity' | 'bias' | 'quality' | 'custom']
  'update-node-evaluation-prompt': [nodeId: string, prompt: string]
  'update-node-output-type': [nodeId: string, outputType: 'commentary' | 'score' | 'all']
  'update-node-enable-branching': [nodeId: string, enabled: boolean]
  'update-node-branch-condition': [nodeId: string, condition: 'binary' | 'threshold']
  'update-node-threshold-value': [nodeId: string, threshold: number]
  'update-node-branch-labels': [nodeId: string, trueLabel: string, falseLabel: string]
  // Session 140: Random Prompt events
  'update-node-random-prompt-preset': [nodeId: string, preset: string]
  'update-node-random-prompt-model': [nodeId: string, model: string]
  'update-node-random-prompt-film-type': [nodeId: string, filmType: string]
}>()

const canvasRef = ref<HTMLElement | null>(null)
const draggingNodeId = ref<string | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

/**
 * Node dimensions by type
 * Wide nodes: input, interception, translation, evaluation, display, collector
 * Narrow nodes: generation
 */
const NARROW_WIDTH = 180
const WIDE_WIDTH = 280
const DEFAULT_HEIGHT = 80

/**
 * Get node width based on type
 */
function getNodeWidth(node: CanvasNode): number {
  // Use custom width if set (resizable nodes)
  if (node.width) return node.width

  // Wide types: input, random_prompt, interception, translation, evaluation, display, collector
  const wideTypes: StageType[] = ['input', 'random_prompt', 'interception', 'translation', 'evaluation', 'display', 'collector']
  return wideTypes.includes(node.type) ? WIDE_WIDTH : NARROW_WIDTH
}

/**
 * Get node height
 */
function getNodeHeight(node: CanvasNode): number {
  return node.height || DEFAULT_HEIGHT
}

/**
 * Get connector position from node data (no DOM queries)
 * All connectors positioned in HEADER area (fixed Y offset from top)
 * This ensures connectors don't move when nodes resize
 */
const HEADER_CONNECTOR_Y = 24  // Fixed offset from top (middle of header)

function getConnectorPosition(node: CanvasNode, connectorType: string): { x: number; y: number } {
  const width = getNodeWidth(node)

  if (connectorType === 'input') {
    // Left edge, header height
    return { x: node.x, y: node.y + HEADER_CONNECTOR_Y }
  } else if (connectorType === 'feedback-input') {
    // Right edge, slightly below header for feedback loops
    return { x: node.x + width, y: node.y + HEADER_CONNECTOR_Y + 20 }
  } else {
    // Output connectors: right edge, header height
    return { x: node.x + width, y: node.y + HEADER_CONNECTOR_Y }
  }
}

/**
 * Get center point of a node's output connector
 */
function getNodeOutputCenter(nodeId: string, label?: string): { x: number; y: number } {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node) return { x: 0, y: 0 }

  // For evaluation branching outputs, stack them in header area
  if (label && node.type === 'evaluation' && node.enableBranching) {
    const width = getNodeWidth(node)
    // Three outputs stacked starting from header: passthrough, commented, commentary
    const outputIndex = label === 'passthrough' ? 0 : label === 'commented' ? 1 : 2
    const yOffset = HEADER_CONNECTOR_Y + outputIndex * 20
    return { x: node.x + width, y: node.y + yOffset }
  }

  return getConnectorPosition(node, 'output')
}

/**
 * Get center point of a node's input connector
 */
function getNodeInputCenter(nodeId: string): { x: number; y: number } {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node) return { x: 0, y: 0 }
  return getConnectorPosition(node, 'input')
}

/**
 * Get center point of a node's feedback input connector
 */
function getNodeFeedbackInputCenter(nodeId: string): { x: number; y: number } {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node) return { x: 0, y: 0 }
  return getConnectorPosition(node, 'feedback-input')
}

/**
 * Connection paths for rendering
 * Pure data-based calculation - no DOM queries
 */
const connectionPaths = computed(() => {
  return props.connections.map(conn => {
    // For evaluation outputs with labels, use the specific labeled connector
    const outputLabel = ['passthrough', 'commented', 'commentary'].includes(conn.label || '')
      ? conn.label
      : undefined
    const source = getNodeOutputCenter(conn.sourceId, outputLabel)

    // Use feedback input position for connections with label 'feedback'
    const target = conn.label === 'feedback'
      ? getNodeFeedbackInputCenter(conn.targetId)
      : getNodeInputCenter(conn.targetId)

    return {
      ...conn,
      x1: source.x,
      y1: source.y,
      x2: target.x,
      y2: target.y
    }
  })
})

/**
 * Temporary connection path (when connecting)
 */
const tempConnection = computed(() => {
  if (!props.connectingFromId) return null
  const source = getNodeOutputCenter(props.connectingFromId)
  return {
    x1: source.x,
    y1: source.y,
    x2: props.mousePosition.x,
    y2: props.mousePosition.y
  }
})

// Event handlers
function onCanvasClick(e: MouseEvent) {
  if (e.target === canvasRef.value) {
    emit('select-node', null)
    if (props.connectingFromId) {
      emit('cancel-connection')
    }
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  const nodeType = e.dataTransfer?.getData('nodeType') as StageType | undefined
  if (nodeType && canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect()
    // Session 141: Account for scroll offset when dropping nodes
    const x = e.clientX - rect.left + canvasRef.value.scrollLeft
    const y = e.clientY - rect.top + canvasRef.value.scrollTop
    emit('add-node-at', nodeType, x, y)
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  e.dataTransfer!.dropEffect = 'copy'
}

function startNodeDrag(nodeId: string, e: MouseEvent) {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node || !canvasRef.value) return

  // Session 141: Calculate offset in canvas coordinates (with scroll)
  const rect = canvasRef.value.getBoundingClientRect()
  const canvasX = e.clientX - rect.left + canvasRef.value.scrollLeft
  const canvasY = e.clientY - rect.top + canvasRef.value.scrollTop

  draggingNodeId.value = nodeId
  dragOffset.value = {
    x: canvasX - node.x,
    y: canvasY - node.y
  }
  emit('select-node', nodeId)
}

function onMouseMove(e: MouseEvent) {
  if (!canvasRef.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  // Session 141: Account for scroll offset in canvas coordinates
  const x = e.clientX - rect.left + canvasRef.value.scrollLeft
  const y = e.clientY - rect.top + canvasRef.value.scrollTop

  emit('update-mouse-position', x, y)

  if (draggingNodeId.value) {
    const newX = x - dragOffset.value.x
    const newY = y - dragOffset.value.y
    emit('update-node-position', draggingNodeId.value, Math.max(0, newX), Math.max(0, newY))
  }
}

function onMouseUp() {
  draggingNodeId.value = null
}

function onKeyDown(e: KeyboardEvent) {
  // Delete selected node on Delete/Backspace
  if ((e.key === 'Delete' || e.key === 'Backspace') && props.selectedNodeId) {
    emit('delete-node', props.selectedNodeId)
  }
  // Cancel connection on Escape
  if (e.key === 'Escape' && props.connectingFromId) {
    emit('cancel-connection')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<template>
  <div
    ref="canvasRef"
    class="canvas-workspace"
    @click="onCanvasClick"
    @drop="onDrop"
    @dragover="onDragOver"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
  >
    <!-- Connections SVG layer -->
    <svg class="connections-layer">
      <!-- Existing connections -->
      <ConnectionLine
        v-for="conn in connectionPaths"
        :key="`${conn.sourceId}-${conn.targetId}`"
        :x1="conn.x1"
        :y1="conn.y1"
        :x2="conn.x2"
        :y2="conn.y2"
        @click="emit('delete-connection', conn.sourceId, conn.targetId)"
      />

      <!-- Temporary connection being drawn -->
      <ConnectionLine
        v-if="tempConnection"
        :x1="tempConnection.x1"
        :y1="tempConnection.y1"
        :x2="tempConnection.x2"
        :y2="tempConnection.y2"
        temporary
      />
    </svg>

    <!-- Nodes -->
    <StageModule
      v-for="node in nodes"
      :key="node.id"
      :node="node"
      :selected="node.id === selectedNodeId"
      :llm-models="llmModels"
      :config-name="getConfigInfo(node.configId)?.name"
      :config-media-type="getConfigInfo(node.configId)?.mediaType"
      :execution-result="executionResults?.[node.id]"
      :collector-output="node.type === 'collector' ? collectorOutput : undefined"
      :is-active="node.id === activeNodeId"
      @mousedown="startNodeDrag(node.id, $event)"
      @start-connect="emit('start-connection', node.id)"
      @start-connect-labeled="(label) => emit('start-connection', node.id, label)"
      @end-connect="emit('complete-connection', node.id)"
      @end-connect-feedback="emit('complete-connection-feedback', node.id)"
      @delete="emit('delete-node', node.id)"
      @select-config="emit('select-config', node.id)"
      @update-llm="emit('update-node-llm', node.id, $event)"
      @update-context-prompt="emit('update-node-context-prompt', node.id, $event)"
      @update-translation-prompt="emit('update-node-translation-prompt', node.id, $event)"
      @update-prompt-text="emit('update-node-prompt-text', node.id, $event)"
      @update-size="(width, height) => emit('update-node-size', node.id, width, height)"
      @update-display-title="emit('update-node-display-title', node.id, $event)"
      @update-display-mode="emit('update-node-display-mode', node.id, $event)"
      @update-evaluation-type="emit('update-node-evaluation-type', node.id, $event)"
      @update-evaluation-prompt="emit('update-node-evaluation-prompt', node.id, $event)"
      @update-output-type="emit('update-node-output-type', node.id, $event)"
      @update-enable-branching="emit('update-node-enable-branching', node.id, $event)"
      @update-branch-condition="emit('update-node-branch-condition', node.id, $event)"
      @update-threshold-value="emit('update-node-threshold-value', node.id, $event)"
      @update-branch-labels="(trueLabel, falseLabel) => emit('update-node-branch-labels', node.id, trueLabel, falseLabel)"
      @update-random-prompt-preset="emit('update-node-random-prompt-preset', node.id, $event)"
      @update-random-prompt-model="emit('update-node-random-prompt-model', node.id, $event)"
      @update-random-prompt-film-type="emit('update-node-random-prompt-film-type', node.id, $event)"
    />

    <!-- Empty state -->
    <div v-if="nodes.length === 0" class="empty-state">
      <p v-if="locale === 'de'">
        Ziehe Module aus der Palette hierher
      </p>
      <p v-else>
        Drag modules from the palette here
      </p>
    </div>
  </div>
</template>

<style scoped>
.canvas-workspace {
  width: 100%;
  height: 100%;
  position: relative;
  background:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  background-color: #0f172a;
  overflow: auto;  /* Session 141: Enable scrolling for tall nodes */
  cursor: default;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.connections-layer > :deep(*) {
  pointer-events: auto;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.empty-state p {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
}
</style>
