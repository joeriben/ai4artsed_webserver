<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCanvasStore } from '@/stores/canvas'
import CanvasWorkspace from '@/components/canvas/CanvasWorkspace.vue'
import ModulePalette from '@/components/canvas/ModulePalette.vue'
import ConfigSelectorModal from '@/components/canvas/ConfigSelectorModal.vue'
import type { StageType } from '@/types/canvas'

const { t, locale } = useI18n()
const canvasStore = useCanvasStore()

// Config selector modal state
const showConfigSelector = ref(false)
const configSelectorType = ref<'interception' | 'generation'>('interception')
const configSelectorNodeId = ref<string | null>(null)

// Workflow name editing
const isEditingName = ref(false)
const editingNameValue = ref('')

// Panel visibility
const showPalette = ref(true)

onMounted(async () => {
  // Load available configs
  await canvasStore.loadAllConfigs()
})

// Event handlers
function handleAddNodeAt(type: StageType, x: number, y: number) {
  const node = canvasStore.addNode(type, x, y)

  // If it's an interception or generation node, open config selector
  if (type === 'interception' || type === 'generation') {
    openConfigSelector(node.id, type)
  }
}

function handleAddNodeFromPalette(type: StageType) {
  // Add node at a default position
  const x = 400 + Math.random() * 100
  const y = 200 + Math.random() * 100
  handleAddNodeAt(type, x, y)
}

function openConfigSelector(nodeId: string, type: 'interception' | 'generation') {
  configSelectorNodeId.value = nodeId
  configSelectorType.value = type
  showConfigSelector.value = true
}

function handleSelectConfig(nodeId: string) {
  const node = canvasStore.nodes.find(n => n.id === nodeId)
  if (!node) return

  if (node.type === 'interception' || node.type === 'generation') {
    openConfigSelector(nodeId, node.type)
  }
}

function handleConfigSelected(configId: string) {
  if (configSelectorNodeId.value) {
    canvasStore.updateNodeConfig(configSelectorNodeId.value, configId)
  }
}

function startEditingName() {
  editingNameValue.value = canvasStore.workflow.name
  isEditingName.value = true
}

function finishEditingName() {
  if (editingNameValue.value.trim()) {
    canvasStore.updateWorkflowMeta(editingNameValue.value.trim())
  }
  isEditingName.value = false
}

function handleNewWorkflow() {
  if (confirm(locale.value === 'de'
    ? 'Aktuellen Workflow verwerfen?'
    : 'Discard current workflow?'
  )) {
    canvasStore.newWorkflow()
  }
}

function handleExportWorkflow() {
  const workflow = canvasStore.exportWorkflow()
  const json = JSON.stringify(workflow, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${workflow.name.replace(/\s+/g, '_')}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function handleImportWorkflow() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const workflow = JSON.parse(text)
      canvasStore.loadWorkflow(workflow)
    } catch (err) {
      console.error('Failed to import workflow:', err)
      alert(locale.value === 'de'
        ? 'Fehler beim Importieren der Datei'
        : 'Failed to import file'
      )
    }
  }
  input.click()
}

// Computed helpers
const currentConfigId = computed(() => {
  if (!configSelectorNodeId.value) return undefined
  const node = canvasStore.nodes.find(n => n.id === configSelectorNodeId.value)
  return node?.configId
})
</script>

<template>
  <div class="canvas-workflow-view">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <!-- Toggle palette -->
        <button
          class="toolbar-btn"
          :class="{ active: showPalette }"
          @click="showPalette = !showPalette"
          :title="locale === 'de' ? 'Palette ein/aus' : 'Toggle palette'"
        >
          📦
        </button>

        <!-- Workflow name -->
        <div class="workflow-name" @dblclick="startEditingName">
          <template v-if="isEditingName">
            <input
              v-model="editingNameValue"
              type="text"
              class="name-input"
              @blur="finishEditingName"
              @keyup.enter="finishEditingName"
              @keyup.escape="isEditingName = false"
              autofocus
            />
          </template>
          <template v-else>
            <span class="name-text">{{ canvasStore.workflow.name }}</span>
            <span class="name-hint">{{ locale === 'de' ? '(doppelklicken zum Bearbeiten)' : '(double-click to edit)' }}</span>
          </template>
        </div>
      </div>

      <div class="toolbar-center">
        <!-- Validation status -->
        <div
          class="validation-status"
          :class="{ valid: canvasStore.isWorkflowValid, invalid: !canvasStore.isWorkflowValid }"
        >
          <span v-if="canvasStore.isWorkflowValid">✓ {{ locale === 'de' ? 'Bereit' : 'Ready' }}</span>
          <span v-else>{{ canvasStore.validationErrors.length }} {{ locale === 'de' ? 'Fehler' : 'errors' }}</span>
        </div>
      </div>

      <div class="toolbar-right">
        <!-- New workflow -->
        <button
          class="toolbar-btn"
          @click="handleNewWorkflow"
          :title="locale === 'de' ? 'Neuer Workflow' : 'New workflow'"
        >
          📄
        </button>

        <!-- Import -->
        <button
          class="toolbar-btn"
          @click="handleImportWorkflow"
          :title="locale === 'de' ? 'Importieren' : 'Import'"
        >
          📥
        </button>

        <!-- Export -->
        <button
          class="toolbar-btn"
          @click="handleExportWorkflow"
          :title="locale === 'de' ? 'Exportieren' : 'Export'"
        >
          📤
        </button>

        <!-- Execute (disabled for now) -->
        <button
          class="toolbar-btn primary"
          :disabled="!canvasStore.isWorkflowValid || canvasStore.isExecuting"
          @click="canvasStore.executeWorkflow()"
          :title="locale === 'de' ? 'Ausführen' : 'Execute'"
        >
          ▶️ {{ locale === 'de' ? 'Ausführen' : 'Execute' }}
        </button>
      </div>
    </div>

    <!-- Main content -->
    <div class="main-content">
      <!-- Palette panel -->
      <div v-if="showPalette" class="palette-panel">
        <ModulePalette @add-node="handleAddNodeFromPalette" />
      </div>

      <!-- Canvas -->
      <div class="canvas-container">
        <CanvasWorkspace
          :nodes="canvasStore.nodes"
          :connections="canvasStore.connections"
          :selected-node-id="canvasStore.selectedNodeId"
          :connecting-from-id="canvasStore.connectingFromId"
          :mouse-position="canvasStore.mousePosition"
          @select-node="canvasStore.selectNode"
          @update-node-position="canvasStore.updateNodePosition"
          @delete-node="canvasStore.deleteNode"
          @add-connection="canvasStore.completeConnection"
          @delete-connection="canvasStore.deleteConnection"
          @start-connection="canvasStore.startConnection"
          @cancel-connection="canvasStore.cancelConnection"
          @complete-connection="canvasStore.completeConnection"
          @update-mouse-position="canvasStore.updateMousePosition"
          @add-node-at="handleAddNodeAt"
          @select-config="handleSelectConfig"
        />
      </div>
    </div>

    <!-- Config selector modal -->
    <ConfigSelectorModal
      :visible="showConfigSelector"
      :type="configSelectorType"
      :interception-configs="canvasStore.interceptionConfigs"
      :output-configs="canvasStore.outputConfigs"
      :current-config-id="currentConfigId"
      @close="showConfigSelector = false"
      @select="handleConfigSelected"
    />

    <!-- Loading overlay -->
    <div v-if="canvasStore.isLoading" class="loading-overlay">
      <div class="loading-spinner">
        {{ locale === 'de' ? 'Laden...' : 'Loading...' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.canvas-workflow-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0f172a;
  color: #e2e8f0;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #1e293b;
  border-bottom: 1px solid #334155;
  gap: 1rem;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-left {
  flex: 1;
}

.toolbar-right {
  flex: 1;
  justify-content: flex-end;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background: #334155;
  border: none;
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s;
}

.toolbar-btn:hover:not(:disabled) {
  background: #475569;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn.active {
  background: #3b82f6;
}

.toolbar-btn.primary {
  background: #3b82f6;
}

.toolbar-btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.workflow-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.workflow-name:hover {
  background: rgba(255, 255, 255, 0.05);
}

.name-text {
  font-weight: 500;
}

.name-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.name-input {
  padding: 0.25rem 0.5rem;
  background: #0f172a;
  border: 1px solid #3b82f6;
  border-radius: 4px;
  color: #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
}

.name-input:focus {
  outline: none;
}

.validation-status {
  padding: 0.375rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.validation-status.valid {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.validation-status.invalid {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.palette-panel {
  width: 240px;
  background: #1e293b;
  border-right: 1px solid #334155;
  overflow-y: auto;
}

.canvas-container {
  flex: 1;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-spinner {
  padding: 1rem 2rem;
  background: #1e293b;
  border-radius: 8px;
  font-size: 1rem;
}
</style>
