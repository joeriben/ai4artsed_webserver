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
import { defineProps, defineEmits, ref, computed, watch, nextTick, onMounted } from 'vue'
import ImageUploadWidget from '@/components/ImageUploadWidget.vue'

// Template refs for parent access (like MediaOutputBox sectionRef)
const inputBoxRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

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
  'image-uploaded': [url: string, path: string, id: string]
  'image-removed': []
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

function handleImageUpload(url: string, path: string, id: string) {
  emit('image-uploaded', url, path, id)
  emit('update:value', url)  // Update v-model with image URL
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

// Lifecycle
onMounted(() => {
  if (props.inputType === 'text' && props.resizeType === 'auto') {
    autoResizeTextarea()
  }
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
