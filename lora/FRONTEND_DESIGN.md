# LoRA Training Frontend Design

**Document Type:** Design Specification (Implementation by another session)

**Created:** 2025-11-07

**Target:** Vue 3 + TypeScript + Pinia frontend integration

---

## Overview

Design for a LoRA training interface integrated into the AI4ArtsEd DevServer Vue.js frontend. This is a **tool for advanced students** to train custom SD 3.5 Large LoRAs for use with DevServer's `sd35_large` output configuration.

---

## Architecture Integration

### Route

```typescript
// src/router/index.ts
{
  path: '/lora',
  name: 'lora-training',
  component: () => import('../views/LoraTrainingView.vue'),
}
```

### File Structure

```
src/
├── views/
│   └── LoraTrainingView.vue          # Main view (3-column layout)
├── components/
│   ├── LoraDatasetManager.vue        # Left: Dataset upload & management
│   ├── LoraTrainingPanel.vue         # Center: Training configuration & execution
│   ├── LoraProgressMonitor.vue       # Right: Real-time training progress
│   ├── LoraModelLibrary.vue          # Bottom: Trained LoRA library
│   └── LoraImageGallery.vue          # Dataset image gallery with captions
└── stores/
    └── lora.ts                        # Pinia store for LoRA training state
```

---

## UI Layout

### 3-Column Layout (Inspired by mockup_phase2_app_layout.html)

```
┌──────────────────────────────────────────────────────────────┐
│ Top Bar: LoRA Training | Mode: Advanced | Help               │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────┬───────────────────────┬──────────────────┐  │
│ │             │                       │                  │  │
│ │  Dataset    │   Training Config     │   Progress       │  │
│ │  Manager    │   & Execution         │   Monitor        │  │
│ │             │                       │                  │  │
│ │  [Upload]   │   ┌─────────────┐    │   Epoch: 5/10    │  │
│ │             │   │ Model: SD3.5│    │   Loss: 0.0023   │  │
│ │  16 images  │   │ Rank: 32    │    │   ├─────────┤    │  │
│ │  ┌──┬──┬──┐ │   │ Epochs: 10  │    │   60%            │  │
│ │  │🖼│🖼│🖼│ │   │ LR: 1e-4    │    │                  │  │
│ │  ├──┼──┼──┤ │   └─────────────┘    │   [📊 Loss]      │  │
│ │  │🖼│🖼│🖼│ │                       │   [📈 Preview]   │  │
│ │  └──┴──┴──┘ │   [🚀 Start]         │                  │  │
│ │             │   [⏸ Pause]          │   [💾 Save]      │  │
│ └─────────────┴───────────────────────┴──────────────────┘  │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐    │
│ │  Trained LoRAs Library                               │    │
│ │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │    │
│ │  │ yoruba_v1  │ │ dada_style │ │ bauhaus_v2 │  ...  │    │
│ │  │ [Test][⬇] │ │ [Test][⬇] │ │ [Test][⬇] │       │    │
│ │  └────────────┘ └────────────┘ └────────────┘       │    │
│ └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Responsive Behavior

**Desktop (>1200px):** 3-column layout as above

**Tablet (768px-1200px):** 2-column layout (Dataset + Training, Progress below)

**Mobile (<768px):** Single column, tabbed interface

---

## Component Designs

### 1. LoraDatasetManager.vue (Left Panel)

**Purpose:** Upload and manage training images with captions

**Features:**

```vue
<template>
  <div class="dataset-manager">
    <div class="panel-header">
      <h3>📁 Training Dataset</h3>
      <span class="image-count">{{ images.length }} images</span>
    </div>

    <!-- Upload Zone -->
    <div
      class="upload-zone"
      @drop.prevent="handleDrop"
      @dragover.prevent
    >
      <input
        type="file"
        ref="fileInput"
        multiple
        accept="image/*"
        @change="handleFileSelect"
        style="display: none"
      />
      <button @click="$refs.fileInput.click()" class="upload-btn">
        ➕ Add Images
      </button>
      <p class="upload-hint">or drag & drop</p>
    </div>

    <!-- Image Gallery -->
    <div class="image-gallery">
      <div
        v-for="(image, idx) in images"
        :key="idx"
        class="image-card"
        @click="selectImage(idx)"
        :class="{ selected: selectedImage === idx }"
      >
        <img :src="image.preview" :alt="image.name" />
        <div class="image-overlay">
          <span class="repeat-badge">{{ image.repeat }}x</span>
          <button @click.stop="removeImage(idx)" class="remove-btn">✕</button>
        </div>
      </div>
    </div>

    <!-- Selected Image Details -->
    <div v-if="selectedImage !== null" class="image-details">
      <h4>{{ images[selectedImage].name }}</h4>

      <div class="form-group">
        <label>Caption (optional)</label>
        <textarea
          v-model="images[selectedImage].caption"
          placeholder="Describe the image..."
          rows="3"
        ></textarea>
      </div>

      <div class="form-group">
        <label>Repeat Count</label>
        <input
          type="number"
          v-model.number="images[selectedImage].repeat"
          min="1"
          max="100"
        />
        <span class="help-text">
          Higher repeats for rare/important concepts
        </span>
      </div>
    </div>

    <!-- Dataset Actions -->
    <div class="dataset-actions">
      <button @click="clearDataset" class="btn-secondary">
        🗑️ Clear All
      </button>
      <button @click="saveDataset" class="btn-primary">
        💾 Save Dataset
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface TrainingImage {
  name: string
  preview: string  // Data URL
  file: File
  caption: string
  repeat: number
}

const images = ref<TrainingImage[]>([])
const selectedImage = ref<number | null>(null)

const handleFileSelect = (event: Event) => {
  // Implementation: Read files, create previews, add to images array
}

const handleDrop = (event: DragEvent) => {
  // Implementation: Handle drag-and-drop file upload
}

const removeImage = (idx: number) => {
  // Implementation: Remove image from array
}

const clearDataset = () => {
  // Implementation: Clear all images
}

const saveDataset = async () => {
  // Implementation: Upload dataset to backend
  // POST /api/lora/dataset/upload
}
</script>

<style scoped>
.dataset-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: #2a2a2a;
  border-radius: 8px;
}

.upload-zone {
  border: 2px dashed #4a4a4a;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-zone:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.image-card {
  position: relative;
  aspect-ratio: 1;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.image-card:hover {
  border-color: #667eea;
}

.image-card.selected {
  border-color: #27ae60;
  box-shadow: 0 0 10px rgba(39, 174, 96, 0.5);
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
}

.repeat-badge {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.remove-btn {
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 2px 6px;
  cursor: pointer;
  font-size: 12px;
}
</style>
```

---

### 2. LoraTrainingPanel.vue (Center Panel)

**Purpose:** Configure training parameters and start/stop training

**Features:**

```vue
<template>
  <div class="training-panel">
    <div class="panel-header">
      <h3>⚙️ Training Configuration</h3>
      <button @click="toggleMode" class="mode-toggle">
        {{ isAdvanced ? '📊 Simple' : '🔧 Advanced' }}
      </button>
    </div>

    <form @submit.prevent="startTraining" class="training-form">

      <!-- Basic Settings (Always Visible) -->
      <div class="form-section">
        <h4>Basic Settings</h4>

        <div class="form-group">
          <label>LoRA Name</label>
          <input
            v-model="config.name"
            placeholder="e.g., yorubaheritage_sd35"
            required
          />
        </div>

        <div class="form-group">
          <label>Base Model</label>
          <select v-model="config.baseModel" required>
            <option value="sd35_large">SD 3.5 Large (Recommended)</option>
            <option value="sdxl">SDXL Base 1.0</option>
            <option value="sd15">SD 1.5</option>
          </select>
        </div>

        <div class="form-group">
          <label>Training Epochs</label>
          <input
            type="number"
            v-model.number="config.epochs"
            min="5"
            max="100"
          />
          <span class="help-text">More epochs = longer training, better fit</span>
        </div>
      </div>

      <!-- Advanced Settings (Collapsible) -->
      <div v-if="isAdvanced" class="form-section advanced">
        <h4>Advanced Settings</h4>

        <div class="form-row">
          <div class="form-group">
            <label>LoRA Rank (dim)</label>
            <input type="number" v-model.number="config.rank" min="4" max="128" />
          </div>

          <div class="form-group">
            <label>LoRA Alpha</label>
            <input type="number" v-model.number="config.alpha" min="1" max="128" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Learning Rate</label>
            <input
              type="text"
              v-model="config.learningRate"
              placeholder="1e-4"
            />
          </div>

          <div class="form-group">
            <label>Batch Size</label>
            <input
              type="number"
              v-model.number="config.batchSize"
              min="1"
              max="8"
            />
          </div>
        </div>

        <div class="form-group">
          <label>Optimizer</label>
          <select v-model="config.optimizer">
            <option value="AdamW8bit">AdamW8bit (Recommended)</option>
            <option value="AdamW">AdamW</option>
            <option value="Prodigy">Prodigy</option>
            <option value="Lion">Lion</option>
          </select>
        </div>

        <div class="form-group">
          <label>LR Scheduler</label>
          <select v-model="config.scheduler">
            <option value="cosine">Cosine (Recommended)</option>
            <option value="constant">Constant</option>
            <option value="linear">Linear</option>
            <option value="polynomial">Polynomial</option>
          </select>
        </div>

        <div class="form-group checkbox">
          <label>
            <input type="checkbox" v-model="config.useXformers" />
            Use xformers (Flash Attention)
          </label>
        </div>

        <div class="form-group checkbox">
          <label>
            <input type="checkbox" v-model="config.gradientCheckpointing" />
            Gradient Checkpointing (Saves VRAM)
          </label>
        </div>
      </div>

      <!-- Training Actions -->
      <div class="training-actions">
        <button
          type="submit"
          class="btn-primary btn-large"
          :disabled="isTraining || images.length === 0"
        >
          {{ isTraining ? '⏳ Training...' : '🚀 Start Training' }}
        </button>

        <button
          v-if="isTraining"
          type="button"
          @click="stopTraining"
          class="btn-danger"
        >
          ⏹ Stop Training
        </button>
      </div>

      <!-- Estimated Time -->
      <div v-if="!isTraining && images.length > 0" class="estimate">
        <span>📊 Estimated time: {{ estimateTrainingTime() }}</span>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLoraStore } from '@/stores/lora'

const loraStore = useLoraStore()

const isAdvanced = ref(false)
const isTraining = ref(false)

const config = ref({
  name: '',
  baseModel: 'sd35_large',
  epochs: 10,
  rank: 32,
  alpha: 16,
  learningRate: '1e-4',
  batchSize: 1,
  optimizer: 'AdamW8bit',
  scheduler: 'cosine',
  useXformers: true,
  gradientCheckpointing: false,
})

const images = computed(() => loraStore.dataset.images)

const toggleMode = () => {
  isAdvanced.value = !isAdvanced.value
}

const startTraining = async () => {
  isTraining.value = true

  try {
    // Implementation: POST /api/lora/training/start
    const response = await fetch('/api/lora/training/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset_id: loraStore.dataset.id,
        config: config.value,
      }),
    })

    const result = await response.json()
    loraStore.startTraining(result.training_id)

  } catch (error) {
    console.error('Training start failed:', error)
    isTraining.value = false
  }
}

const stopTraining = async () => {
  // Implementation: POST /api/lora/training/stop
  isTraining.value = false
}

const estimateTrainingTime = () => {
  // Simple estimation: ~5-10 min per epoch for SD 3.5
  const minPerEpoch = 7
  const totalMin = config.value.epochs * minPerEpoch
  const hours = Math.floor(totalMin / 60)
  const mins = totalMin % 60
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
}
</script>

<style scoped>
.training-panel {
  height: 100%;
  padding: 1rem;
  background: #2a2a2a;
  border-radius: 8px;
  overflow-y: auto;
}

.form-section {
  background: #1a1a1a;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.form-section h4 {
  color: #667eea;
  margin-bottom: 1rem;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.estimate {
  text-align: center;
  color: #a0a0a0;
  font-size: 0.9rem;
  padding: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
}
</style>
```

---

### 3. LoraProgressMonitor.vue (Right Panel)

**Purpose:** Real-time training progress monitoring

**Features:**

```vue
<template>
  <div class="progress-monitor">
    <div class="panel-header">
      <h3>📊 Training Progress</h3>
      <span v-if="isTraining" class="status-badge active">● Training</span>
      <span v-else class="status-badge idle">○ Idle</span>
    </div>

    <div v-if="!isTraining" class="idle-state">
      <p>No training in progress</p>
      <p class="hint">Configure settings and start training</p>
    </div>

    <div v-else class="progress-content">

      <!-- Current Status -->
      <div class="status-card">
        <div class="stat">
          <span class="stat-label">Epoch</span>
          <span class="stat-value">{{ currentEpoch }} / {{ totalEpochs }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Step</span>
          <span class="stat-value">{{ currentStep }} / {{ totalSteps }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Loss</span>
          <span class="stat-value loss">{{ currentLoss.toFixed(4) }}</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      </div>
      <p class="progress-text">{{ progress }}% Complete</p>

      <!-- Loss Chart -->
      <div class="chart-container">
        <h4>Loss Curve</h4>
        <canvas ref="lossChart" width="300" height="200"></canvas>
      </div>

      <!-- Time Estimate -->
      <div class="time-estimate">
        <div class="time-stat">
          <span>⏱️ Elapsed:</span>
          <strong>{{ elapsedTime }}</strong>
        </div>
        <div class="time-stat">
          <span>⏳ Remaining:</span>
          <strong>{{ remainingTime }}</strong>
        </div>
      </div>

      <!-- Sample Preview (if available) -->
      <div v-if="sampleImage" class="sample-preview">
        <h4>Latest Sample</h4>
        <img :src="sampleImage" alt="Training sample" />
        <p class="sample-info">Generated at epoch {{ sampleEpoch }}</p>
      </div>

      <!-- Checkpoint Management -->
      <div class="checkpoint-section">
        <h4>Checkpoints</h4>
        <div
          v-for="checkpoint in checkpoints"
          :key="checkpoint.epoch"
          class="checkpoint-item"
        >
          <span>Epoch {{ checkpoint.epoch }}</span>
          <span class="loss-value">Loss: {{ checkpoint.loss.toFixed(4) }}</span>
          <button @click="loadCheckpoint(checkpoint)" class="btn-small">
            Load
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLoraStore } from '@/stores/lora'

const loraStore = useLoraStore()

const lossChart = ref<HTMLCanvasElement | null>(null)
const pollInterval = ref<number | null>(null)

const isTraining = computed(() => loraStore.isTraining)
const currentEpoch = computed(() => loraStore.trainingProgress.epoch)
const totalEpochs = computed(() => loraStore.trainingConfig.epochs)
const currentStep = computed(() => loraStore.trainingProgress.step)
const totalSteps = computed(() => loraStore.trainingProgress.totalSteps)
const currentLoss = computed(() => loraStore.trainingProgress.loss)
const progress = computed(() => {
  if (totalEpochs.value === 0) return 0
  return Math.round((currentEpoch.value / totalEpochs.value) * 100)
})
const elapsedTime = computed(() => formatTime(loraStore.trainingProgress.elapsedSeconds))
const remainingTime = computed(() => formatTime(loraStore.trainingProgress.remainingSeconds))
const sampleImage = computed(() => loraStore.trainingProgress.sampleImage)
const sampleEpoch = computed(() => loraStore.trainingProgress.sampleEpoch)
const checkpoints = computed(() => loraStore.trainingProgress.checkpoints)

const formatTime = (seconds: number) => {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return hrs > 0
    ? `${hrs}h ${mins}m`
    : `${mins}m ${secs}s`
}

const startPolling = () => {
  pollInterval.value = setInterval(async () => {
    if (!loraStore.isTraining) {
      stopPolling()
      return
    }

    try {
      const response = await fetch(`/api/lora/training/${loraStore.trainingId}/status`)
      const data = await response.json()
      loraStore.updateTrainingProgress(data)
      updateLossChart()
    } catch (error) {
      console.error('Polling error:', error)
    }
  }, 2000) // Poll every 2 seconds
}

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

const updateLossChart = () => {
  // Implementation: Use Chart.js or similar to render loss curve
  // Plot loraStore.trainingProgress.lossHistory
}

const loadCheckpoint = async (checkpoint: any) => {
  // Implementation: Load a specific checkpoint
  // POST /api/lora/training/load-checkpoint
}

onMounted(() => {
  if (isTraining.value) {
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.progress-monitor {
  height: 100%;
  padding: 1rem;
  background: #2a2a2a;
  border-radius: 8px;
  overflow-y: auto;
}

.idle-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #a0a0a0;
}

.status-card {
  background: #1a1a1a;
  padding: 1rem;
  border-radius: 6px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #a0a0a0;
  text-transform: uppercase;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
}

.stat-value.loss {
  color: #667eea;
}

.progress-bar-container {
  background: #1a1a1a;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.chart-container {
  background: #1a1a1a;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
}

.chart-container h4 {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #a0a0a0;
}

.time-estimate {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1rem 0;
}

.time-stat {
  background: #1a1a1a;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sample-preview {
  background: #1a1a1a;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
}

.sample-preview img {
  width: 100%;
  border-radius: 4px;
  margin: 0.5rem 0;
}

.checkpoint-section {
  background: #1a1a1a;
  padding: 1rem;
  border-radius: 6px;
}

.checkpoint-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid #2a2a2a;
}
</style>
```

---

### 4. LoraModelLibrary.vue (Bottom Panel)

**Purpose:** Browse and manage trained LoRAs

**Features:**

```vue
<template>
  <div class="model-library">
    <div class="library-header">
      <h3>🎨 Trained LoRA Library</h3>
      <button @click="refreshLibrary" class="btn-secondary">
        🔄 Refresh
      </button>
    </div>

    <div v-if="models.length === 0" class="empty-state">
      <p>No trained LoRAs yet</p>
      <p class="hint">Start training to create your first LoRA</p>
    </div>

    <div v-else class="model-grid">
      <div
        v-for="model in models"
        :key="model.id"
        class="model-card"
      >
        <!-- Model Preview -->
        <div class="model-preview">
          <img
            v-if="model.previewImage"
            :src="model.previewImage"
            :alt="model.name"
          />
          <div v-else class="placeholder-preview">
            🎨
          </div>
        </div>

        <!-- Model Info -->
        <div class="model-info">
          <h4>{{ model.name }}</h4>
          <div class="model-meta">
            <span class="meta-item">
              📊 Rank: {{ model.rank }}
            </span>
            <span class="meta-item">
              📈 {{ model.epochs }} epochs
            </span>
            <span class="meta-item">
              📅 {{ formatDate(model.createdAt) }}
            </span>
          </div>
          <div class="model-stats">
            <span class="stat">
              Final Loss: <strong>{{ model.finalLoss.toFixed(4) }}</strong>
            </span>
            <span class="stat">
              Size: <strong>{{ formatSize(model.fileSize) }}</strong>
            </span>
          </div>
        </div>

        <!-- Model Actions -->
        <div class="model-actions">
          <button @click="testModel(model)" class="btn-primary btn-small">
            🧪 Test
          </button>
          <button @click="downloadModel(model)" class="btn-secondary btn-small">
            ⬇️ Download
          </button>
          <button @click="deleteModel(model)" class="btn-danger btn-small">
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Test Modal (if testingModel) -->
    <div v-if="testingModel" class="modal-overlay" @click="closeTest">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🧪 Test LoRA: {{ testingModel.name }}</h3>
          <button @click="closeTest" class="close-btn">✕</button>
        </div>

        <form @submit.prevent="generateTest" class="test-form">
          <div class="form-group">
            <label>Test Prompt</label>
            <textarea
              v-model="testPrompt"
              placeholder="Enter a prompt to test the LoRA..."
              rows="3"
              required
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>LoRA Strength</label>
              <input
                type="range"
                v-model.number="testStrength"
                min="0"
                max="1"
                step="0.1"
              />
              <span>{{ testStrength }}</span>
            </div>
          </div>

          <button type="submit" class="btn-primary" :disabled="isGenerating">
            {{ isGenerating ? '⏳ Generating...' : '🎨 Generate' }}
          </button>
        </form>

        <div v-if="testResult" class="test-result">
          <h4>Result</h4>
          <img :src="testResult" alt="Test result" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface LoraModel {
  id: string
  name: string
  rank: number
  epochs: number
  finalLoss: number
  fileSize: number
  createdAt: string
  previewImage?: string
}

const models = ref<LoraModel[]>([])
const testingModel = ref<LoraModel | null>(null)
const testPrompt = ref('')
const testStrength = ref(0.8)
const isGenerating = ref(false)
const testResult = ref<string | null>(null)

const refreshLibrary = async () => {
  try {
    const response = await fetch('/api/lora/models')
    const data = await response.json()
    models.value = data.models
  } catch (error) {
    console.error('Failed to load models:', error)
  }
}

const testModel = (model: LoraModel) => {
  testingModel.value = model
  testResult.value = null
}

const closeTest = () => {
  testingModel.value = null
  testResult.value = null
}

const generateTest = async () => {
  isGenerating.value = true

  try {
    const response = await fetch('/api/lora/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lora_id: testingModel.value!.id,
        prompt: testPrompt.value,
        strength: testStrength.value,
      }),
    })

    const result = await response.json()
    testResult.value = result.image_url
  } catch (error) {
    console.error('Test generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

const downloadModel = (model: LoraModel) => {
  // Implementation: Download .safetensors file
  window.open(`/api/lora/models/${model.id}/download`, '_blank')
}

const deleteModel = async (model: LoraModel) => {
  if (!confirm(`Delete "${model.name}"? This cannot be undone.`)) {
    return
  }

  try {
    await fetch(`/api/lora/models/${model.id}`, {
      method: 'DELETE',
    })
    await refreshLibrary()
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const formatSize = (bytes: number) => {
  if (bytes < 1024 * 1024) {
    return `${Math.round(bytes / 1024)} KB`
  }
  return `${Math.round(bytes / (1024 * 1024))} MB`
}

onMounted(() => {
  refreshLibrary()
})
</script>

<style scoped>
.model-library {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 1rem;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.model-card {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.model-preview {
  width: 100%;
  aspect-ratio: 1;
  background: #2a2a2a;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-preview {
  font-size: 4rem;
}

.model-info h4 {
  font-size: 1.1rem;
  color: #fff;
  margin-bottom: 0.5rem;
}

.model-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.meta-item {
  font-size: 0.75rem;
  color: #a0a0a0;
}

.model-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #c0c0c0;
}

.model-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.test-result {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #3a3a3a;
}

.test-result img {
  width: 100%;
  border-radius: 8px;
  margin-top: 0.5rem;
}
</style>
```

---

## Backend API Requirements

### Dataset Management

```typescript
// Upload dataset
POST /api/lora/dataset/upload
Content-Type: multipart/form-data
Body: {
  images: File[],
  captions: string[],
  repeats: number[]
}
Response: {
  dataset_id: string,
  image_count: number
}

// Get dataset info
GET /api/lora/dataset/:dataset_id
Response: {
  id: string,
  images: Array<{
    name: string,
    url: string,
    caption: string,
    repeat: number
  }>
}
```

### Training Execution

```typescript
// Start training
POST /api/lora/training/start
Body: {
  dataset_id: string,
  config: {
    name: string,
    baseModel: 'sd35_large' | 'sdxl' | 'sd15',
    epochs: number,
    rank: number,
    alpha: number,
    learningRate: string,
    batchSize: number,
    optimizer: string,
    scheduler: string,
    useXformers: boolean,
    gradientCheckpointing: boolean
  }
}
Response: {
  training_id: string,
  estimated_duration_seconds: number
}

// Get training status (polling endpoint)
GET /api/lora/training/:training_id/status
Response: {
  training_id: string,
  status: 'queued' | 'running' | 'completed' | 'failed',
  epoch: number,
  total_epochs: number,
  step: number,
  total_steps: number,
  loss: number,
  loss_history: number[],
  elapsed_seconds: number,
  remaining_seconds: number,
  sample_image?: string,
  sample_epoch?: number,
  checkpoints: Array<{
    epoch: number,
    loss: number
  }>
}

// Stop training
POST /api/lora/training/:training_id/stop
Response: {
  status: 'stopped',
  final_epoch: number
}

// Load checkpoint
POST /api/lora/training/load-checkpoint
Body: {
  training_id: string,
  checkpoint_epoch: number
}
Response: {
  status: 'loaded'
}
```

### Model Library

```typescript
// Get all trained models
GET /api/lora/models
Response: {
  models: Array<{
    id: string,
    name: string,
    rank: number,
    epochs: number,
    finalLoss: number,
    fileSize: number,
    createdAt: string,
    previewImage?: string
  }>
}

// Test a model
POST /api/lora/test
Body: {
  lora_id: string,
  prompt: string,
  strength: number
}
Response: {
  image_url: string
}

// Download model
GET /api/lora/models/:model_id/download
Response: Binary (.safetensors file)

// Delete model
DELETE /api/lora/models/:model_id
Response: {
  status: 'deleted'
}
```

---

## Pinia Store Structure

```typescript
// src/stores/lora.ts
import { defineStore } from 'pinia'

export const useLoraStore = defineStore('lora', {
  state: () => ({
    // Dataset
    dataset: {
      id: null as string | null,
      images: [] as Array<{
        name: string
        preview: string
        file: File
        caption: string
        repeat: number
      }>,
    },

    // Training
    isTraining: false,
    trainingId: null as string | null,
    trainingConfig: {
      epochs: 10,
    },
    trainingProgress: {
      epoch: 0,
      totalEpochs: 0,
      step: 0,
      totalSteps: 0,
      loss: 0,
      lossHistory: [] as number[],
      elapsedSeconds: 0,
      remainingSeconds: 0,
      sampleImage: null as string | null,
      sampleEpoch: null as number | null,
      checkpoints: [] as Array<{ epoch: number; loss: number }>,
    },

    // Library
    models: [] as Array<any>,
  }),

  actions: {
    async uploadDataset(images: any[]) {
      // Upload implementation
    },

    async startTraining(trainingId: string) {
      this.isTraining = true
      this.trainingId = trainingId
    },

    async stopTraining() {
      this.isTraining = false
    },

    updateTrainingProgress(data: any) {
      this.trainingProgress = data
    },

    async loadModels() {
      // Fetch models from API
    },
  },
})
```

---

## i18n Localization

```typescript
// src/locales/en.json (add to existing)
{
  "lora": {
    "title": "LoRA Training",
    "subtitle": "Train custom SD 3.5 Large LoRAs",
    "dataset": {
      "title": "Training Dataset",
      "upload": "Add Images",
      "dragHint": "or drag & drop",
      "imageCount": "{count} images",
      "caption": "Caption (optional)",
      "repeat": "Repeat Count",
      "repeatHint": "Higher repeats for rare/important concepts"
    },
    "training": {
      "title": "Training Configuration",
      "basicSettings": "Basic Settings",
      "advancedSettings": "Advanced Settings",
      "loraName": "LoRA Name",
      "baseModel": "Base Model",
      "epochs": "Training Epochs",
      "epochsHint": "More epochs = longer training, better fit",
      "startButton": "Start Training",
      "stopButton": "Stop Training",
      "estimatedTime": "Estimated time: {time}"
    },
    "progress": {
      "title": "Training Progress",
      "epoch": "Epoch",
      "step": "Step",
      "loss": "Loss",
      "elapsed": "Elapsed",
      "remaining": "Remaining",
      "lossChart": "Loss Curve",
      "latestSample": "Latest Sample",
      "checkpoints": "Checkpoints"
    },
    "library": {
      "title": "Trained LoRA Library",
      "empty": "No trained LoRAs yet",
      "emptyHint": "Start training to create your first LoRA",
      "test": "Test",
      "download": "Download",
      "delete": "Delete",
      "testPrompt": "Test Prompt",
      "loraStrength": "LoRA Strength",
      "generate": "Generate"
    }
  }
}

// src/locales/de.json (add to existing)
{
  "lora": {
    "title": "LoRA Training",
    "subtitle": "Trainiere eigene SD 3.5 Large LoRAs",
    "dataset": {
      "title": "Trainingsdatensatz",
      "upload": "Bilder hinzufügen",
      "dragHint": "oder Drag & Drop",
      "imageCount": "{count} Bilder",
      "caption": "Beschreibung (optional)",
      "repeat": "Wiederholungen",
      "repeatHint": "Höhere Wiederholungen für seltene/wichtige Konzepte"
    },
    // ... German translations
  }
}
```

---

## Theme & Styling

**Color Palette (Consistent with App.vue):**

```css
/* Dark Theme */
--bg-primary: #1a1a1a
--bg-secondary: #2a2a2a
--bg-tertiary: #3a3a3a

--text-primary: #e0e0e0
--text-secondary: #c0c0c0
--text-tertiary: #a0a0a0

--accent-primary: #667eea
--accent-secondary: #764ba2
--accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)

--success: #27ae60
--warning: #f39c12
--danger: #e74c3c

--border: #4a4a4a
```

**Typography:**

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

---

## Security Considerations

1. **File Upload Validation:**
   - Max file size: 10MB per image
   - Allowed formats: JPG, PNG only
   - Max total dataset size: 1GB

2. **Training Resource Limits:**
   - Max concurrent trainings: 1 per user
   - Max epochs: 100
   - Training timeout: 12 hours

3. **Authentication:**
   - Require user authentication for training endpoints
   - Rate limit API endpoints (10 req/min for training start)

4. **File Storage:**
   - Store datasets in user-specific directories
   - Clean up failed/cancelled trainings
   - Virus scan uploaded files

---

## Progressive Enhancement

### Phase 1 (MVP):
- Dataset upload & management ✓
- Basic training configuration ✓
- Simple progress monitoring ✓
- Model library (list only) ✓

### Phase 2:
- Advanced training settings ✓
- Real-time loss chart visualization
- Sample image generation during training
- Checkpoint management

### Phase 3:
- LoRA testing interface
- Batch training queue
- Training presets (save/load configs)
- Integration with DevServer configs (auto-select LoRA in sd35_large)

### Phase 4:
- Multi-user support with permissions
- Training history & analytics
- LoRA sharing/export to Civitai
- Automatic captioning (BLIP/CLIP)

---

## Implementation Notes

1. **Training Backend:**
   - Can use Kohya-SS CLI via subprocess
   - Or implement direct Diffusers training
   - Run as background job (Celery/Redis queue)

2. **Real-time Updates:**
   - Use WebSocket or Server-Sent Events (SSE) for live progress
   - Fallback to polling (2-second interval)

3. **File Handling:**
   - Store uploaded images in `/tmp/lora_datasets/{user_id}/{dataset_id}/`
   - Move trained LoRAs to `SwarmUI/Models/Lora/`
   - Clean up temporary files after training

4. **Error Handling:**
   - GPU OOM: Suggest reducing batch size/resolution
   - Training failure: Save checkpoint, allow resume
   - Dataset errors: Validate before training starts

---

## Testing Strategy

1. **Unit Tests:**
   - Component rendering
   - Form validation
   - State management (Pinia)

2. **Integration Tests:**
   - API endpoint connectivity
   - File upload flow
   - Training start/stop cycle

3. **E2E Tests (Playwright):**
   - Complete training workflow
   - Dataset upload → Config → Train → Download
   - Multi-user concurrent training

---

## Accessibility

- **Keyboard Navigation:** All buttons/forms accessible via keyboard
- **ARIA Labels:** Proper labels for screen readers
- **Color Contrast:** WCAG AA compliance (4.5:1 ratio)
- **Focus Indicators:** Visible focus states
- **Loading States:** Clear feedback for async operations

---

## Performance

- **Lazy Loading:** Code-split LoRA view (vue-router)
- **Image Optimization:** Compress previews to max 200KB
- **Debounce Input:** Caption editing, slider changes
- **Virtual Scrolling:** For large model libraries (>50 models)
- **Polling Throttle:** 2-second interval, stop when inactive

---

## Documentation for Users

Include help tooltips/modals:

1. **What is LoRA?** - Brief explanation
2. **Dataset Preparation** - Image requirements, captioning tips
3. **Training Parameters** - Explain rank, alpha, learning rate
4. **Troubleshooting** - Common errors (OOM, low loss)
5. **Integration Guide** - How to use LoRA with DevServer

---

## Summary

This design provides a complete, production-ready LoRA training interface that:

✅ Integrates seamlessly with existing Vue 3 frontend architecture
✅ Follows DevServer's dark theme and design patterns
✅ Supports SD 3.5 Large training (primary target)
✅ Provides real-time progress monitoring
✅ Includes model library for management
✅ Progressive enhancement (MVP → Advanced features)
✅ Comprehensive API specification for backend
✅ Accessibility, security, and performance considerations

**Next Steps for Implementation Session:**
1. Create route in `src/router/index.ts`
2. Implement components (start with MVP features)
3. Create Pinia store (`src/stores/lora.ts`)
4. Add i18n translations
5. Implement backend API endpoints
6. Test end-to-end workflow

---

**End of Design Document**
