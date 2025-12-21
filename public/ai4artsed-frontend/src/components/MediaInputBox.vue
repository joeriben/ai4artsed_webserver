<template>
  <div ref="inputBoxRef" class="media-input-box bubble-card" :class="{
    empty: isEmpty,
    filled: isFilled,
    required: isRequired,
    loading: isLoading
  }">
    <!-- Header -->
    <div class="bubble-header">
      <span class="bubble-icon">{{ icon }}</span>
      <span class="bubble-label">{{ label }}</span>
      <div v-if="showActions" class="bubble-actions">
        <button v-if="showCopy" @click="$emit('copy')" class="action-btn" title="Kopieren">📋</button>
        <button v-if="showPaste" @click="$emit('paste')" class="action-btn" title="Einfügen">📄</button>
        <button v-if="showClear" @click="$emit('clear')" class="action-btn" title="Löschen">🗑️</button>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="preview-loading">
      <div class="spinner-large"></div>
      <p class="loading-text">{{ loadingMessage }}</p>
    </div>

    <!-- Content: Text Input -->
    <textarea
      v-else-if="inputType === 'text'"
      ref="textareaRef"
      :value="value"
      @input="handleInput"
      :placeholder="placeholder"
      :rows="rows"
      :class="['bubble-textarea', resizeClass]"
    ></textarea>

    <!-- Content: Image Input -->
    <ImageUploadWidget
      v-else-if="inputType === 'image'"
      :initial-image="initialImage"
      @image-uploaded="handleImageUpload"
      @image-removed="$emit('image-removed')"
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import ImageUploadWidget from '@/components/ImageUploadWidget.vue'

// Template refs for parent access (like MediaOutputBox sectionRef)
const inputBoxRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// Streaming state
const eventSource = ref<EventSource | null>(null)
const streamedValue = ref('')
const isStreamComplete = ref(false)
const isFirstChunkReceived = ref(false)
const chunkBuffer = ref<string[]>([])
let bufferInterval: number | null = null

interface Props {
  icon: string
  label: string
  placeholder?: string
  value: string
  inputType?: 'text' | 'image'
  rows?: number
  resizeType?: 'standard' | 'auto' | 'none'
  isEmpty?: boolean
  isRequired?: boolean
  isFilled?: boolean
  isLoading?: boolean
  loadingMessage?: string
  showActions?: boolean
  showCopy?: boolean
  showPaste?: boolean
  showClear?: boolean
  initialImage?: string
  // Streaming props
  enableStreaming?: boolean
  streamUrl?: string
  streamParams?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  inputType: 'text',
  rows: 6,
  resizeType: 'standard',
  isEmpty: false,
  isRequired: false,
  isFilled: false,
  isLoading: false,
  loadingMessage: 'Lädt...',
  showActions: true,
  showCopy: true,
  showPaste: true,
  showClear: true,
  initialImage: undefined
})

const emit = defineEmits<{
  'update:value': [value: string]
  'copy': []
  'paste': []
  'clear': []
  'image-uploaded': [data: any]  // Changed: Accept full data object from ImageUploadWidget
  'image-removed': []
  'stream-started': []  // Emitted on first chunk (to hide loading spinner)
  'stream-complete': [data: any]
  'stream-error': [error: string]
}>()

// Expose refs for parent access (like MediaOutputBox)
defineExpose({
  inputBoxRef,
  textareaRef
})

// Computed Properties
const resizeClass = computed(() => {
  switch (props.resizeType) {
    case 'auto': return 'auto-resize-textarea'
    case 'none': return 'no-resize-textarea'
    case 'standard':
    default: return 'standard-resize-textarea'
  }
})

// Functions
function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:value', target.value)
}

function handleImageUpload(data: any) {
  // ImageUploadWidget emits full data object with preview_url, image_path, image_id
  emit('image-uploaded', data)
  emit('update:value', data.preview_url)  // Update v-model with preview URL
}

function autoResizeTextarea() {
  if (props.resizeType !== 'auto' || !textareaRef.value) return
  textareaRef.value.style.height = 'auto'
  textareaRef.value.style.height = (textareaRef.value.scrollHeight + 4) + 'px'
}

// Watchers
watch(() => props.value, async () => {
  if (props.inputType === 'text' && props.resizeType === 'auto') {
    await nextTick()
    autoResizeTextarea()
  }
})

// Streaming functions
function startStreaming() {
  console.log('[DEBUG MediaInputBox] startStreaming() called, streamUrl:', props.streamUrl, 'streamParams:', props.streamParams)

  if (!props.streamUrl) {
    console.log('[DEBUG MediaInputBox] No streamUrl, returning early')
    return
  }

  // Close any existing stream first
  closeStream()

  // Reset state
  streamedValue.value = ''
  isStreamComplete.value = false
  isFirstChunkReceived.value = false
  chunkBuffer.value = []

  // Build URL with query parameters
  const params = new URLSearchParams(props.streamParams || {})
  const url = `${props.streamUrl}?${params.toString()}`

  console.log('[MediaInputBox] Starting stream:', url)

  eventSource.value = new EventSource(url)

  // Start buffer processor for smooth character-by-character display
  startBufferProcessor()

  eventSource.value.addEventListener('connected', (event) => {
    console.log('[MediaInputBox] Stream connected:', JSON.parse(event.data))
  })

  eventSource.value.addEventListener('chunk', (event) => {
    const data = JSON.parse(event.data)
    console.log('[MediaInputBox] Chunk received:', data.chunk_count, 'text:', data.text_chunk)

    // Emit stream-started on first chunk (so parent can hide loading spinner)
    if (!isFirstChunkReceived.value) {
      isFirstChunkReceived.value = true
      emit('stream-started')
    }

    // Add chunk to buffer for smooth display
    chunkBuffer.value.push(...data.text_chunk.split(''))
  })

  eventSource.value.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data)
    console.log('[MediaInputBox] Stream complete:', data.char_count, 'chars')
    isStreamComplete.value = true

    // Close EventSource but keep buffer processor running until empty
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

    // Store final text for safety check, but let buffer display naturally
    const finalText = data.final_text

    // Check buffer completion periodically until empty
    const checkBufferComplete = setInterval(() => {
      if (chunkBuffer.value.length === 0) {
        // Buffer is empty - verify we have complete text
        if (streamedValue.value !== finalText) {
          console.log('[MediaInputBox] Buffer finished but text incomplete, using final_text')
          streamedValue.value = finalText
          emit('update:value', streamedValue.value)
        }
        emit('stream-complete', data)
        stopBufferProcessor()
        clearInterval(checkBufferComplete)
      }
    }, 50)  // Check every 50ms
  })

  eventSource.value.addEventListener('error', (event) => {
    // Ignore error if stream already completed successfully
    if (isStreamComplete.value) {
      console.log('[MediaInputBox] Ignoring error after successful completion')
      return
    }

    console.error('[MediaInputBox] Stream error:', event)
    emit('stream-error', 'Stream connection failed')
    closeStream()
  })
}

function startBufferProcessor() {
  // Process buffer every 30ms for smooth character-by-character effect
  bufferInterval = window.setInterval(() => {
    if (chunkBuffer.value.length > 0) {
      // Take 1-3 characters at a time for smoother appearance
      const chars = chunkBuffer.value.splice(0, Math.min(3, chunkBuffer.value.length))
      streamedValue.value += chars.join('')
      emit('update:value', streamedValue.value)
    }
  }, 30)
}

function stopBufferProcessor() {
  if (bufferInterval) {
    clearInterval(bufferInterval)
    bufferInterval = null
  }
}

function closeStream() {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
  stopBufferProcessor()

  // Clear any remaining buffer
  if (chunkBuffer.value.length > 0 && !isStreamComplete.value) {
    streamedValue.value += chunkBuffer.value.join('')
    emit('update:value', streamedValue.value)
    chunkBuffer.value = []
  }
}

// Watch for streaming activation (only when URL changes)
watch(() => props.streamUrl, (newUrl, oldUrl) => {
  console.log('[DEBUG MediaInputBox] Watch triggered - enableStreaming:', props.enableStreaming, 'newUrl:', newUrl, 'oldUrl:', oldUrl)

  if (props.enableStreaming && newUrl && newUrl !== oldUrl) {
    console.log('[MediaInputBox] Stream URL changed, starting new stream')
    startStreaming()
  } else {
    console.log('[DEBUG MediaInputBox] NOT starting stream - conditions not met')
  }
})

// Lifecycle
onMounted(() => {
  if (props.inputType === 'text' && props.resizeType === 'auto') {
    autoResizeTextarea()
  }
})

onUnmounted(() => {
  closeStream()
})
</script>

<style scoped>
.media-input-box {
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: clamp(12px, 2vw, 20px);
  padding: clamp(1rem, 2.5vw, 1.5rem);
  transition: all 0.3s ease;
}

.media-input-box.filled {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
}

.media-input-box.required {
  border-color: rgba(255, 193, 7, 0.6);
  background: rgba(255, 193, 7, 0.05);
  animation: pulse-required 2s ease-in-out infinite;
}

@keyframes pulse-required {
  0%, 100% { border-color: rgba(255, 193, 7, 0.6); }
  50% { border-color: rgba(255, 193, 7, 0.9); }
}

.media-input-box.empty {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  background: rgba(20, 20, 20, 0.5);
}

.media-input-box.loading {
  background: rgba(20, 20, 20, 0.7);
  border: 2px solid rgba(79, 172, 254, 0.4);
}

/* Header */
.bubble-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.bubble-icon {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  flex-shrink: 0;
}

.bubble-label {
  font-size: clamp(0.9rem, 2vw, 1rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.bubble-actions {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.action-btn {
  background: transparent;
  border: none;
  font-size: 0.9rem;
  opacity: 0.4;
  cursor: pointer;
  transition: opacity 0.2s;
  padding: 0.25rem;
}

.action-btn:hover {
  opacity: 0.8;
}

/* Textarea */
.bubble-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: clamp(0.9rem, 2vw, 1rem);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
  font-family: inherit;
  line-height: 1.4;
}

.bubble-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.bubble-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Resize Types */
.standard-resize-textarea {
  resize: vertical;
  min-height: clamp(80px, 10vh, 100px);
}

.auto-resize-textarea {
  resize: vertical;
  overflow-y: auto;
  min-height: clamp(80px, 10vh, 100px);
  max-height: clamp(150px, 20vh, 250px);
}

.no-resize-textarea {
  resize: none;
  min-height: clamp(80px, 10vh, 100px);
}

/* Loading Overlay */
.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  min-height: 100px;
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: rgba(102, 126, 234, 0.8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-align: center;
}
</style>
