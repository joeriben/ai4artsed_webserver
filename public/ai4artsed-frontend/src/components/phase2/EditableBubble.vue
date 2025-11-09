<template>
  <div class="editable-bubble" :class="{ 'is-modified': isModified, 'is-focused': isFocused }">
    <!-- Header -->
    <div class="bubble-header">
      <div class="header-left">
        <span class="bubble-icon">{{ icon }}</span>
        <h3 class="bubble-title">{{ title }}</h3>
      </div>
      <div class="header-right">
        <!-- Modified badge -->
        <span v-if="isModified" class="modified-badge">{{ $t('phase2.modified') }}</span>
        <!-- Character count -->
        <span v-if="maxChars" class="char-count" :class="{ 'is-near-limit': isNearLimit }">
          {{ currentLength }} / {{ maxChars }}
        </span>
        <!-- Reset button -->
        <button v-if="isModified" class="reset-button" @click="handleReset" :title="$t('phase2.reset')">
          ↺
        </button>
      </div>
    </div>

    <!-- Editable content -->
    <div
      v-if="!isMobile"
      ref="editableRef"
      class="bubble-content"
      contenteditable="true"
      :placeholder="placeholder"
      @input="handleInput"
      @focus="isFocused = true"
      @blur="handleBlur"
      @paste="handlePaste"
    ></div>

    <!-- Fallback textarea for mobile -->
    <textarea
      v-else
      v-model="currentValue"
      class="bubble-content-textarea"
      :placeholder="placeholder"
      :maxlength="maxChars"
      @input="handleTextareaInput"
      @focus="isFocused = true"
      @blur="handleBlur"
    ></textarea>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

/**
 * EditableBubble - Inline Editable Text Component for Phase 2
 *
 * Features:
 * - contenteditable with character limit
 * - Modified badge and reset button
 * - Responsive: textarea fallback on mobile
 * - Accessible: proper ARIA attributes
 *
 * Phase 2 - Multilingual Context Editing Implementation
 */

// ============================================================================
// PROPS & EMITS
// ============================================================================

interface Props {
  icon: string
  title: string
  modelValue: string
  defaultValue: string
  maxChars?: number
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  maxChars: 0,
  placeholder: ''
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// ============================================================================
// COMPOSABLES
// ============================================================================

const { t } = useI18n()

// ============================================================================
// STATE
// ============================================================================

const editableRef = ref<HTMLDivElement | null>(null)
const currentValue = ref(props.modelValue)
const isFocused = ref(false)
const isMobile = ref(false)

// ============================================================================
// COMPUTED
// ============================================================================

const currentLength = computed(() => currentValue.value.length)

const isModified = computed(() => currentValue.value !== props.defaultValue)

const isNearLimit = computed(() => {
  if (!props.maxChars) return false
  return currentLength.value > props.maxChars * 0.9
})

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  // Detect mobile
  isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )

  // Initialize contenteditable content
  if (!isMobile.value && editableRef.value) {
    editableRef.value.textContent = props.modelValue
  }
})

// ============================================================================
// WATCHERS
// ============================================================================

// Sync modelValue prop changes to internal state
watch(
  () => props.modelValue,
  (newValue) => {
    currentValue.value = newValue

    // Update contenteditable content
    if (!isMobile.value && editableRef.value) {
      nextTick(() => {
        if (editableRef.value && editableRef.value.textContent !== newValue) {
          editableRef.value.textContent = newValue
        }
      })
    }
  }
)

// ============================================================================
// METHODS
// ============================================================================

function handleInput(event: Event) {
  const target = event.target as HTMLDivElement
  let text = target.textContent || ''

  // Enforce character limit
  if (props.maxChars && text.length > props.maxChars) {
    text = text.substring(0, props.maxChars)
    target.textContent = text

    // Restore cursor position to end
    const selection = window.getSelection()
    const range = document.createRange()
    range.selectNodeContents(target)
    range.collapse(false)
    selection?.removeAllRanges()
    selection?.addRange(range)
  }

  currentValue.value = text
  emit('update:modelValue', text)
}

function handleTextareaInput() {
  emit('update:modelValue', currentValue.value)
}

function handleBlur() {
  isFocused.value = false
}

function handlePaste(event: ClipboardEvent) {
  // Prevent pasting rich text, only allow plain text
  event.preventDefault()
  const text = event.clipboardData?.getData('text/plain') || ''

  // Insert plain text
  const selection = window.getSelection()
  if (selection && selection.rangeCount > 0) {
    const range = selection.getRangeAt(0)
    range.deleteContents()
    range.insertNode(document.createTextNode(text))

    // Move cursor to end of inserted text
    range.collapse(false)
    selection.removeAllRanges()
    selection.addRange(range)
  }

  // Trigger input event
  if (editableRef.value) {
    handleInput({ target: editableRef.value } as any)
  }
}

function handleReset() {
  currentValue.value = props.defaultValue
  emit('update:modelValue', props.defaultValue)

  // Update contenteditable content
  if (!isMobile.value && editableRef.value) {
    nextTick(() => {
      if (editableRef.value) {
        editableRef.value.textContent = props.defaultValue
      }
    })
  }
}
</script>

<style scoped>
.editable-bubble {
  background: rgba(30, 30, 30, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.editable-bubble.is-focused {
  border-color: rgba(96, 165, 250, 0.5);
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.2);
}

.editable-bubble.is-modified {
  border-color: rgba(251, 191, 36, 0.5);
}

/* Header */
.bubble-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bubble-icon {
  font-size: 24px;
  line-height: 1;
}

.bubble-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modified-badge {
  padding: 4px 10px;
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border: 1px solid #fbbf24;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.char-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.char-count.is-near-limit {
  color: #f87171;
}

.reset-button {
  width: 32px;
  height: 32px;
  padding: 0;
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border: 2px solid #f87171;
  border-radius: 50%;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-button:hover {
  background: #f87171;
  color: #0a0a0a;
  transform: rotate(-180deg) scale(1.1);
}

/* Editable content */
.bubble-content,
.bubble-content-textarea {
  min-height: 120px;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ffffff;
  font-size: 15px;
  line-height: 1.6;
  font-family: inherit;
  transition: all 0.2s ease;
}

.bubble-content:focus,
.bubble-content-textarea:focus {
  outline: none;
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(0, 0, 0, 0.5);
}

.bubble-content:empty:before {
  content: attr(placeholder);
  color: rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

.bubble-content-textarea {
  width: 100%;
  resize: vertical;
  font-family: inherit;
}

/* Scrollbar styling */
.bubble-content::-webkit-scrollbar,
.bubble-content-textarea::-webkit-scrollbar {
  width: 8px;
}

.bubble-content::-webkit-scrollbar-track,
.bubble-content-textarea::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.bubble-content::-webkit-scrollbar-thumb,
.bubble-content-textarea::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.bubble-content::-webkit-scrollbar-thumb:hover,
.bubble-content-textarea::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .editable-bubble {
    padding: 16px;
  }

  .bubble-header {
    flex-wrap: wrap;
  }

  .bubble-title {
    font-size: 16px;
  }

  .bubble-icon {
    font-size: 20px;
  }

  .header-right {
    flex-wrap: wrap;
  }
}
</style>
