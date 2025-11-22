<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="modal-overlay" @click.self="cancel">
        <div class="modal-container">
          <div class="modal-header">
            <h2>{{ title }}</h2>
            <button class="close-button" @click="cancel" aria-label="Close">
              ×
            </button>
          </div>

          <div class="modal-body">
            <textarea
              ref="textareaRef"
              v-model="localText"
              class="text-editor"
              :placeholder="placeholder"
              @keydown.esc="cancel"
            ></textarea>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="cancel">
              {{ cancelLabel }}
            </button>
            <button class="btn-confirm" @click="confirm">
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

interface Props {
  modelValue: boolean
  text: string
  title?: string
  placeholder?: string
  confirmLabel?: string
  cancelLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Edit Text',
  placeholder: 'Enter text here...',
  confirmLabel: 'Übernehmen',
  cancelLabel: 'Abbrechen'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'update:text': [text: string]
  'confirm': [text: string]
  'cancel': []
}>()

const localText = ref(props.text)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// Update local text when prop changes
watch(() => props.text, (newText) => {
  localText.value = newText
})

// Focus textarea when modal opens
watch(() => props.modelValue, async (isOpen) => {
  if (isOpen) {
    await nextTick()
    textareaRef.value?.focus()
  }
})

function confirm() {
  emit('update:text', localText.value)
  emit('confirm', localText.value)
  emit('update:modelValue', false)
}

function cancel() {
  // Reset to original text
  localText.value = props.text
  emit('cancel')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-container {
  background: rgba(20, 20, 20, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  padding: 2rem;
}

.text-editor {
  width: 100%;
  height: 100%;
  min-height: 300px;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.6;
  resize: none;
  transition: all 0.2s;

  /* Dark theme styling */
  background: rgba(0, 0, 0, 0.3);
  color: white;
}

.text-editor:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.4);
}

.text-editor::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-cancel,
.btn-confirm {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.btn-confirm {
  background: #2196F3;
  color: white;
}

.btn-confirm:hover {
  background: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
