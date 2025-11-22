<template>
  <div
    class="editable-bubble"
    :class="[`status-${status}`, { 'is-editable': editable }]"
    :style="bubbleStyle"
    @click="handleClick"
  >
    <div class="bubble-content">
      <!-- Label/Title -->
      <div class="bubble-label">{{ label }}</div>

      <!-- Preview Text -->
      <div v-if="previewText" class="bubble-preview">
        {{ previewText }}
      </div>

      <!-- Status Indicator -->
      <div v-if="status === 'processing'" class="processing-spinner"></div>
      <div v-if="status === 'completed'" class="completed-check">✓</div>

      <!-- Edit Icon -->
      <div v-if="editable && status !== 'processing'" class="edit-icon">
        ✎
      </div>
    </div>

    <!-- Edit Modal -->
    <TextEditModal
      v-model="showModal"
      :text="fullText"
      :title="modalTitle"
      :placeholder="placeholder"
      @update:text="handleTextUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TextEditModal from './TextEditModal.vue'

type BubbleStatus = 'empty' | 'filled' | 'processing' | 'completed'

interface Props {
  label: string
  fullText: string
  x: number // percentage
  y: number // percentage
  size?: number // percentage (default 15%)
  status?: BubbleStatus
  editable?: boolean
  color?: string
  modalTitle?: string
  placeholder?: string
  maxPreviewLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 15,
  status: 'empty',
  editable: false,
  color: '#CCCCCC',
  modalTitle: 'Edit Text',
  placeholder: 'Enter text here...',
  maxPreviewLength: 80
})

const emit = defineEmits<{
  'update:text': [text: string]
  click: []
}>()

const showModal = ref(false)

const bubbleStyle = computed(() => ({
  left: `${props.x}%`,
  top: `${props.y}%`,
  width: `${props.size}%`,
  paddingBottom: `${props.size}%`,
  '--bubble-color': props.color
}))

const previewText = computed(() => {
  if (!props.fullText) return ''
  if (props.fullText.length <= props.maxPreviewLength) {
    return props.fullText
  }
  return props.fullText.substring(0, props.maxPreviewLength) + '...'
})

function handleClick() {
  emit('click')
  if (props.editable && props.status !== 'processing') {
    showModal.value = true
  }
}

function handleTextUpdate(newText: string) {
  emit('update:text', newText)
}
</script>

<style scoped>
.editable-bubble {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 50%;

  /* Create aspect ratio square */
  height: 0;
  padding-bottom: 18%;

  /* CSS variable for dynamic color */
  --bubble-color: #CCCCCC;

  /* Empty state: dark with border */
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Filled/Completed state: FILLED WITH COLOR like Phase 1 selected */
.status-filled,
.status-completed {
  background: var(--bubble-color);
  border: none;
  box-shadow: 0 0 24px var(--bubble-color), 0 4px 20px rgba(0, 0, 0, 0.5);
}

.status-filled .bubble-content,
.status-completed .bubble-content {
  color: #0a0a0a;
}

.editable-bubble:hover {
  transform: translate(-50%, -50%) scale(1.08);
}

.status-filled:hover,
.status-completed:hover {
  box-shadow: 0 0 30px var(--bubble-color), 0 6px 30px rgba(0, 0, 0, 0.6);
}

.editable-bubble.is-editable:hover {
  cursor: pointer;
}

.bubble-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
  color: var(--bubble-color);
  overflow: hidden;
}

.bubble-label {
  font-weight: 700;
  font-size: clamp(0.8rem, 1.5vw, 1rem);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.bubble-preview {
  font-size: clamp(0.65rem, 1.2vw, 0.8rem);
  line-height: 1.3;
  opacity: 0.9;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  max-height: 4.5rem;
}

/* Status: processing */
.status-processing {
  animation: pulse 2s ease-in-out infinite;
}

.status-processing .bubble-content {
  color: white;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.05);
  }
}

.processing-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--bubble-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

/* Status: completed */
.status-completed .bubble-content {
  color: white;
}

.completed-check {
  position: absolute;
  top: 8%;
  right: 8%;
  width: 2rem;
  height: 2rem;
  background: var(--bubble-color);
  color: rgba(20, 20, 20, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
  animation: check-pop 0.3s ease;
}

@keyframes check-pop {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

/* Edit icon */
.edit-icon {
  position: absolute;
  bottom: 8%;
  right: 8%;
  width: 2rem;
  height: 2rem;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  opacity: 0;
  transition: opacity 0.2s;
  backdrop-filter: blur(4px);
}

.editable-bubble.is-editable:hover .edit-icon {
  opacity: 1;
}

/* Status: empty */
.status-empty .bubble-content {
  color: #888;
}

.status-empty .bubble-label {
  opacity: 0.7;
}
</style>
