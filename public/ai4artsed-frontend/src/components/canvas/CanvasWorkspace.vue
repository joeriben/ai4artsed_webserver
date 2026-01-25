<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import StageModule from './StageModule.vue'
import ConnectionLine from './ConnectionLine.vue'
import type { CanvasNode, CanvasConnection, StageType, LLMModelSummary } from '@/types/canvas'

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
}>()

const emit = defineEmits<{
  'select-node': [id: string | null]
  'update-node-position': [id: string, x: number, y: number]
  'delete-node': [id: string]
  'add-connection': [sourceId: string, targetId: string]
  'delete-connection': [sourceId: string, targetId: string]
  'start-connection': [nodeId: string]
  'cancel-connection': []
  'complete-connection': [targetId: string]
  'update-mouse-position': [x: number, y: number]
  'add-node-at': [type: StageType, x: number, y: number]
  'select-config': [nodeId: string]
  'update-node-llm': [nodeId: string, llmModel: string]
  'update-node-context-prompt': [nodeId: string, prompt: string]
  'update-node-translation-prompt': [nodeId: string, prompt: string]
  'update-node-prompt-text': [nodeId: string, text: string]
  'update-node-size': [nodeId: string, width: number, height: number]
}>()

const canvasRef = ref<HTMLElement | null>(null)
const draggingNodeId = ref<string | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

// Node dimensions (approximate for connection points)
const NODE_WIDTH = 180
const NODE_HEIGHT = 80

/**
 * Get center point of a node's output connector
 */
function getNodeOutputCenter(nodeId: string): { x: number; y: number } {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node) return { x: 0, y: 0 }
  return {
    x: node.x + NODE_WIDTH + 7, // Right edge + connector offset
    y: node.y + NODE_HEIGHT / 2
  }
}

/**
 * Get center point of a node's input connector
 */
function getNodeInputCenter(nodeId: string): { x: number; y: number } {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node) return { x: 0, y: 0 }
  return {
    x: node.x - 7, // Left edge - connector offset
    y: node.y + NODE_HEIGHT / 2
  }
}

/**
 * Connection paths for rendering
 */
const connectionPaths = computed(() => {
  return props.connections.map(conn => {
    const source = getNodeOutputCenter(conn.sourceId)
    const target = getNodeInputCenter(conn.targetId)
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
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    emit('add-node-at', nodeType, x, y)
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  e.dataTransfer!.dropEffect = 'copy'
}

function startNodeDrag(nodeId: string, e: MouseEvent) {
  const node = props.nodes.find(n => n.id === nodeId)
  if (!node) return

  draggingNodeId.value = nodeId
  dragOffset.value = {
    x: e.clientX - node.x,
    y: e.clientY - node.y
  }
  emit('select-node', nodeId)
}

function onMouseMove(e: MouseEvent) {
  if (!canvasRef.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  emit('update-mouse-position', x, y)

  if (draggingNodeId.value) {
    const newX = e.clientX - dragOffset.value.x
    const newY = e.clientY - dragOffset.value.y
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
      :execution-result="executionResults?.[node.id]"
      :collector-output="node.type === 'collector' ? collectorOutput : undefined"
      @mousedown="startNodeDrag(node.id, $event)"
      @start-connect="emit('start-connection', node.id)"
      @end-connect="emit('complete-connection', node.id)"
      @delete="emit('delete-node', node.id)"
      @select-config="emit('select-config', node.id)"
      @update-llm="emit('update-node-llm', node.id, $event)"
      @update-context-prompt="emit('update-node-context-prompt', node.id, $event)"
      @update-translation-prompt="emit('update-node-translation-prompt', node.id, $event)"
      @update-prompt-text="emit('update-node-prompt-text', node.id, $event)"
      @update-size="(width, height) => emit('update-node-size', node.id, width, height)"
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
  overflow: hidden;
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
