<template>
  <div class="matrix-container">
    <div class="matrix-header">
      <h2>Model Selection Matrix</h2>
      <p class="help">
        Click a column header to apply that preset. Your current configuration is highlighted.
      </p>
      <p v-if="props.detectedVramTier" class="hardware-info">
        Detected Hardware: <strong>{{ getVramLabel(props.detectedVramTier) }}</strong>
      </p>
    </div>

    <div class="matrix-scroll-container">
      <table class="model-matrix">
        <thead>
          <!-- Group headers -->
          <tr class="group-header-row">
            <th class="row-label-header"></th>
            <th :colspan="localColumns.length" class="group-header local-group">
              LOCAL (DSGVO compliant)
            </th>
            <th :colspan="cloudColumns.length" class="group-header cloud-group">
              CLOUD PROVIDERS
            </th>
          </tr>
          <!-- Column headers -->
          <tr class="column-header-row">
            <th class="row-label-header">Application Area</th>
            <th
              v-for="col in localColumns"
              :key="col.id"
              class="column-header local-column"
              :class="{
                'column-active': isColumnActive(col),
                'column-detected': isDetectedHardware(col)
              }"
              @click="applyPreset(col)"
              :title="'Click to apply ' + col.label + ' preset'"
            >
              <span class="col-label">{{ col.label }}</span>
              <span class="dsgvo-badge dsgvo-ok">DSGVO</span>
              <span v-if="isDetectedHardware(col)" class="hardware-badge">YOUR HW</span>
            </th>
            <th
              v-for="col in cloudColumns"
              :key="col.id"
              class="column-header cloud-column"
              :class="{
                'column-active': isColumnActive(col),
                'dsgvo-warning': !col.dsgvoCompliant
              }"
              @click="applyPreset(col)"
              :title="'Click to apply ' + col.label + ' preset'"
            >
              <span class="col-label">{{ col.label }}</span>
              <span v-if="col.dsgvoCompliant" class="dsgvo-badge dsgvo-ok">DSGVO</span>
              <span v-else class="dsgvo-badge dsgvo-no">US</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in matrixRows" :key="row.field" class="data-row">
            <td class="row-label">
              <span class="stage-badge">{{ row.stage }}</span>
              {{ row.label }}
            </td>
            <!-- Local columns -->
            <td
              v-for="col in localColumns"
              :key="col.id"
              class="matrix-cell"
              :class="{
                'cell-active': isCellActive(row.field, col),
                'cell-highlighted': isColumnActive(col)
              }"
              :title="getCellModel(col.id, 'none', row.field)"
            >
              <span class="model-name">{{ getShortModelName(col.id, 'none', row.field) }}</span>
              <span v-if="isCellActive(row.field, col)" class="active-indicator"></span>
            </td>
            <!-- Cloud columns -->
            <td
              v-for="col in cloudColumns"
              :key="col.id"
              class="matrix-cell"
              :class="{
                'cell-active': isCellActive(row.field, col),
                'cell-highlighted': isColumnActive(col),
                'dsgvo-warning-cell': !col.dsgvoCompliant
              }"
              :title="getCellModel('vram_24', col.id, row.field)"
            >
              <span class="model-name">{{ getShortModelName('vram_24', col.id, row.field) }}</span>
              <span v-if="isCellActive(row.field, col)" class="active-indicator"></span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="matrix-legend">
      <span class="legend-item">
        <span class="legend-color active-color"></span> Current selection
      </span>
      <span class="legend-item">
        <span class="legend-color dsgvo-color"></span> DSGVO compliant
      </span>
      <span class="legend-item">
        <span class="legend-color us-color"></span> NOT DSGVO
      </span>
    </div>

    <div class="matrix-notes">
      <p><strong>OpenRouter:</strong> EU server routing configurable, but NOT DSGVO compliant (US company).</p>
      <p><strong>Local models:</strong> Always DSGVO compliant - data stays on your hardware.</p>
    </div>

    <!-- Developer: Edit Matrix Button -->
    <div class="matrix-edit-section">
      <button @click="openJsonEditor" class="edit-matrix-btn">
        Edit Matrix (JSON)
      </button>
      <span v-if="saveMessage" :class="['save-message', { 'error': !saveSuccess }]">
        {{ saveMessage }}
      </span>
    </div>

    <!-- JSON Editor Modal -->
    <div v-if="showJsonEditor" class="json-editor-overlay" @click.self="closeJsonEditor">
      <div class="json-editor-modal">
        <div class="json-editor-header">
          <h3>Edit Hardware Matrix (JSON)</h3>
          <button @click="closeJsonEditor" class="close-btn">&times;</button>
        </div>
        <div class="json-editor-body">
          <textarea
            v-model="jsonContent"
            class="json-textarea"
            spellcheck="false"
          ></textarea>
          <p v-if="jsonError" class="json-error">{{ jsonError }}</p>
        </div>
        <div class="json-editor-footer">
          <button @click="validateJson" class="validate-btn">Validate</button>
          <button @click="saveMatrix" class="save-btn" :disabled="!!jsonError">Save</button>
          <button @click="closeJsonEditor" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ModelField, MatrixColumn, MatrixRow, HardwareMatrix, VramTier, CloudProvider } from '@/types/settings'

// JSON Editor state
const showJsonEditor = ref(false)
const jsonContent = ref('')
const jsonError = ref('')
const saveMessage = ref('')
const saveSuccess = ref(true)

const props = defineProps<{
  matrix: HardwareMatrix
  currentSettings: Record<string, string>
  selectedVramTier: VramTier
  selectedProvider: CloudProvider
  detectedVramTier: VramTier | null
}>()

const emit = defineEmits<{
  (e: 'apply-preset', vramTier: VramTier, provider: CloudProvider): void
  (e: 'matrix-updated'): void
}>()

// Column definitions
const localColumns: MatrixColumn[] = [
  { id: 'vram_8', label: '8 GB', type: 'local', dsgvoCompliant: true },
  { id: 'vram_16', label: '16 GB', type: 'local', dsgvoCompliant: true },
  { id: 'vram_24', label: '24 GB', type: 'local', dsgvoCompliant: true },
  { id: 'vram_32', label: '32 GB', type: 'local', dsgvoCompliant: true },
  { id: 'vram_48', label: '48 GB', type: 'local', dsgvoCompliant: true },
  { id: 'vram_96', label: '96 GB', type: 'local', dsgvoCompliant: true },
]

const cloudColumns: MatrixColumn[] = [
  { id: 'mistral', label: 'Mistral EU', type: 'cloud', dsgvoCompliant: true },
  { id: 'anthropic', label: 'Anthropic', type: 'cloud', dsgvoCompliant: false },
  { id: 'openai', label: 'OpenAI', type: 'cloud', dsgvoCompliant: false },
  { id: 'openrouter', label: 'OpenRouter', type: 'cloud', dsgvoCompliant: false },
]

// Helper to get VRAM label
function getVramLabel(tier: VramTier): string {
  const labels: Record<VramTier, string> = {
    'vram_8': '8 GB VRAM',
    'vram_16': '16 GB VRAM',
    'vram_24': '24 GB VRAM',
    'vram_32': '32 GB VRAM',
    'vram_48': '48 GB VRAM',
    'vram_96': '96 GB VRAM',
  }
  return labels[tier] || tier
}

// Check if column matches detected hardware
function isDetectedHardware(col: MatrixColumn): boolean {
  return col.type === 'local' && col.id === props.detectedVramTier
}

// Row definitions
const matrixRows: MatrixRow[] = [
  { field: 'STAGE1_TEXT_MODEL', label: 'Text Model', stage: 'S1' },
  { field: 'STAGE1_VISION_MODEL', label: 'Vision Model', stage: 'S1' },
  { field: 'STAGE2_INTERCEPTION_MODEL', label: 'Interception', stage: 'S2' },
  { field: 'STAGE2_OPTIMIZATION_MODEL', label: 'Optimization', stage: 'S2' },
  { field: 'STAGE3_MODEL', label: 'Translation/Safety', stage: 'S3' },
  { field: 'STAGE4_LEGACY_MODEL', label: 'Legacy Model', stage: 'S4' },
  { field: 'CHAT_HELPER_MODEL', label: 'Chat Helper', stage: 'H' },
  { field: 'IMAGE_ANALYSIS_MODEL', label: 'Image Analysis', stage: 'H' },
  { field: 'CODING_MODEL', label: 'Coding', stage: 'H' },
]

// Get model from matrix
function getCellModel(vramTier: string, provider: string, field: ModelField): string {
  const preset = props.matrix?.[vramTier as VramTier]?.[provider as CloudProvider]
  if (!preset?.models) return '-'
  return preset.models[field] || '-'
}

// Get shortened model name for display
function getShortModelName(vramTier: string, provider: string, field: ModelField): string {
  const fullModel = getCellModel(vramTier, provider, field)
  if (fullModel === '-') return '-'

  // Remove provider prefix (local/, bedrock/, etc.)
  const withoutPrefix = fullModel.replace(/^[a-z]+\//, '')

  // Shorten long model names
  if (withoutPrefix.length > 20) {
    // Extract key part of model name
    const parts = withoutPrefix.split(/[:\-.]/)
    if (parts.length > 1 && parts[0]) {
      return parts[0].substring(0, 12) + '...'
    }
    return withoutPrefix.substring(0, 15) + '...'
  }
  return withoutPrefix
}

// Check if a column is the currently active selection
function isColumnActive(col: MatrixColumn): boolean {
  if (col.type === 'local') {
    return props.selectedVramTier === col.id && props.selectedProvider === 'none'
  } else {
    return props.selectedProvider === col.id
  }
}

// Check if a specific cell matches current settings
function isCellActive(field: ModelField, col: MatrixColumn): boolean {
  const currentModel = props.currentSettings?.[field]
  if (!currentModel) return false

  let presetModel: string
  if (col.type === 'local') {
    presetModel = getCellModel(col.id, 'none', field)
  } else {
    // For cloud columns, use vram_24 as reference
    presetModel = getCellModel('vram_24', col.id, field)
  }

  return currentModel === presetModel
}

// Apply preset when column header is clicked
function applyPreset(col: MatrixColumn) {
  if (col.type === 'local') {
    emit('apply-preset', col.id as VramTier, 'none')
  } else {
    // For cloud providers, use the current VRAM tier
    emit('apply-preset', props.selectedVramTier, col.id as CloudProvider)
  }
}

// JSON Editor functions
function openJsonEditor() {
  jsonContent.value = JSON.stringify(props.matrix, null, 2)
  jsonError.value = ''
  showJsonEditor.value = true
}

function closeJsonEditor() {
  showJsonEditor.value = false
  jsonError.value = ''
}

function validateJson() {
  try {
    JSON.parse(jsonContent.value)
    jsonError.value = ''
    saveMessage.value = 'JSON is valid'
    saveSuccess.value = true
    setTimeout(() => { saveMessage.value = '' }, 2000)
  } catch (e) {
    jsonError.value = `Invalid JSON: ${(e as Error).message}`
  }
}

async function saveMatrix() {
  try {
    const matrixData = JSON.parse(jsonContent.value)
    jsonError.value = ''

    const response = await fetch('/api/settings/hardware-matrix', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(matrixData)
    })

    const result = await response.json()

    if (result.success) {
      saveMessage.value = 'Matrix saved successfully'
      saveSuccess.value = true
      showJsonEditor.value = false
      emit('matrix-updated')
    } else {
      saveMessage.value = result.error || 'Save failed'
      saveSuccess.value = false
    }
  } catch (e) {
    jsonError.value = `Error: ${(e as Error).message}`
    saveMessage.value = 'Save failed'
    saveSuccess.value = false
  }

  setTimeout(() => { saveMessage.value = '' }, 3000)
}
</script>

<style scoped>
.matrix-container {
  background: #fff;
  border: 1px solid #ccc;
  padding: 15px;
}

.matrix-header {
  margin-bottom: 15px;
}

.matrix-header h2 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.matrix-header .help {
  margin: 0;
  font-size: 13px;
  color: #666;
}

.matrix-header .hardware-info {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #1565c0;
  background: #e3f2fd;
  padding: 6px 10px;
  border-radius: 4px;
  display: inline-block;
}

.matrix-scroll-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.model-matrix {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
  font-size: 12px;
}

/* Group headers (LOCAL / CLOUD) */
.group-header-row th {
  background: #333;
  color: #fff;
  padding: 8px 4px;
  font-weight: 600;
  text-align: center;
  border: 1px solid #222;
}

.row-label-header {
  background: #f0f0f0 !important;
  color: #333 !important;
  font-weight: 500;
  text-align: left;
  padding: 8px 10px !important;
  width: 140px;
  min-width: 140px;
  position: sticky;
  left: 0;
  z-index: 2;
  border: 1px solid #999 !important;
}

.local-group {
  background: #2e7d32 !important;
}

.cloud-group {
  background: #1565c0 !important;
}

/* Column headers */
.column-header-row th {
  padding: 6px 4px;
  text-align: center;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid #999;
  vertical-align: middle;
}

.column-header:hover {
  filter: brightness(0.9);
}

.local-column {
  background: #e8f5e9;
  color: #1b5e20;
}

.cloud-column {
  background: #e3f2fd;
  color: #0d47a1;
}

.cloud-column.dsgvo-warning {
  background: #fff3e0;
  color: #e65100;
}

.column-active {
  box-shadow: inset 0 0 0 3px #2196f3;
  font-weight: 700;
}

.column-detected {
  background: #c8e6c9 !important;
  border: 2px solid #2e7d32 !important;
}

.hardware-badge {
  display: inline-block;
  font-size: 8px;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 700;
  background: #1565c0;
  color: #fff;
}

.col-label {
  display: block;
  font-size: 11px;
  margin-bottom: 2px;
}

.dsgvo-badge {
  display: inline-block;
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 600;
}

.dsgvo-ok {
  background: #4caf50;
  color: #fff;
}

.dsgvo-no {
  background: #ff9800;
  color: #fff;
}

/* Data rows */
.data-row {
  border-bottom: 1px solid #ddd;
}

.data-row:hover {
  background: #fafafa;
}

.row-label {
  background: #f5f5f5;
  padding: 6px 10px;
  font-weight: 500;
  color: #333;
  text-align: left;
  white-space: nowrap;
  position: sticky;
  left: 0;
  z-index: 1;
  border-right: 1px solid #999;
}

.stage-badge {
  display: inline-block;
  width: 22px;
  text-align: center;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  background: #666;
  border-radius: 3px;
  margin-right: 6px;
  padding: 1px 0;
}

/* Matrix cells */
.matrix-cell {
  padding: 5px 4px;
  text-align: center;
  border: 1px solid #e0e0e0;
  position: relative;
  transition: all 0.15s ease;
}

.matrix-cell:hover {
  background: #f0f0f0;
}

.cell-highlighted {
  background: #e3f2fd !important;
}

.cell-active {
  background: #bbdefb !important;
  font-weight: 600;
}

.dsgvo-warning-cell {
  background: #fff8e1;
}

.model-name {
  font-family: 'Courier New', monospace;
  font-size: 10px;
  color: #333;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 80px;
}

.active-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  background: #2196f3;
  border-radius: 50%;
}

/* Legend */
.matrix-legend {
  display: flex;
  gap: 20px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ddd;
  font-size: 12px;
  color: #666;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid #ccc;
}

.active-color {
  background: #bbdefb;
}

.dsgvo-color {
  background: #4caf50;
}

.us-color {
  background: #ff9800;
}

/* Notes section */
.matrix-notes {
  margin-top: 12px;
  padding: 10px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  color: #555;
}

.matrix-notes p {
  margin: 4px 0;
}

.matrix-notes p:first-child {
  margin-top: 0;
}

.matrix-notes p:last-child {
  margin-bottom: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .matrix-header .help {
    font-size: 11px;
  }

  .model-matrix {
    font-size: 10px;
  }

  .model-name {
    font-size: 9px;
    max-width: 60px;
  }

  .row-label {
    font-size: 11px;
    padding: 4px 6px;
  }

  .col-label {
    font-size: 10px;
  }
}

/* JSON Editor */
.matrix-edit-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
  display: flex;
  align-items: center;
  gap: 15px;
}

.edit-matrix-btn {
  background: #555;
  color: #fff;
  border: 1px solid #333;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
}

.edit-matrix-btn:hover {
  background: #666;
}

.save-message {
  font-size: 13px;
  color: #2e7d32;
}

.save-message.error {
  color: #c62828;
}

.json-editor-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.json-editor-modal {
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.json-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  background: #f5f5f5;
  border-radius: 8px 8px 0 0;
}

.json-editor-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.json-editor-body {
  flex: 1;
  padding: 15px 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.json-textarea {
  width: 100%;
  flex: 1;
  min-height: 400px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
  line-height: 1.4;
}

.json-error {
  margin-top: 10px;
  padding: 8px 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 4px;
  font-size: 12px;
}

.json-editor-footer {
  padding: 15px 20px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  background: #f5f5f5;
  border-radius: 0 0 8px 8px;
}

.validate-btn,
.save-btn,
.cancel-btn {
  padding: 8px 16px;
  font-size: 13px;
  border-radius: 4px;
  cursor: pointer;
}

.validate-btn {
  background: #fff;
  border: 1px solid #999;
  color: #333;
}

.save-btn {
  background: #2e7d32;
  border: 1px solid #1b5e20;
  color: #fff;
}

.save-btn:disabled {
  background: #ccc;
  border-color: #999;
  cursor: not-allowed;
}

.cancel-btn {
  background: #fff;
  border: 1px solid #999;
  color: #333;
}
</style>
