<template>
  <Teleport to="body">
    <div v-if="modelValue" class="compliance-backdrop" @click.self="cancel">
      <div class="compliance-dialog">
        <h2 class="compliance-title">{{ $t('research.complianceTitle') }}</h2>

        <p class="compliance-warning">{{ $t('research.complianceWarning') }}</p>
        <p class="compliance-age">{{ $t('research.complianceAge') }}</p>

        <label class="compliance-checkbox">
          <input type="checkbox" v-model="confirmed" />
          <span>{{ $t('research.complianceConfirm') }}</span>
        </label>

        <div class="compliance-actions">
          <button class="btn-cancel" @click="cancel">{{ $t('research.complianceCancel') }}</button>
          <button class="btn-proceed" :disabled="!confirmed" @click="proceed">{{ $t('research.complianceProceed') }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirmed: []
}>()

const confirmed = ref(false)

function cancel() {
  confirmed.value = false
  emit('update:modelValue', false)
}

function proceed() {
  if (!confirmed.value) return
  confirmed.value = false
  emit('update:modelValue', false)
  emit('confirmed')
}
</script>

<style scoped>
.compliance-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.compliance-dialog {
  background: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 2rem;
  max-width: 480px;
  width: 90%;
}

.compliance-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 1.25rem 0;
}

.compliance-warning {
  color: rgba(255, 200, 100, 0.9);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0 0 0.75rem 0;
}

.compliance-age {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0 0 1.5rem 0;
}

.compliance-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  margin-bottom: 1.5rem;
}

.compliance-checkbox input[type="checkbox"] {
  margin-top: 0.2rem;
  accent-color: #4CAF50;
}

.compliance-checkbox span {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.4;
}

.compliance-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-proceed {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.05);
}

.btn-proceed {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.btn-proceed:hover:not(:disabled) {
  background: #43a047;
}

.btn-proceed:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
