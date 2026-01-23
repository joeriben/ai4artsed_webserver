<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { InterceptionConfigSummary, OutputConfigSummary } from '@/types/canvas'

const { locale } = useI18n()

const props = defineProps<{
  visible: boolean
  type: 'interception' | 'generation' | 'translation'
  interceptionConfigs: InterceptionConfigSummary[]
  outputConfigs: OutputConfigSummary[]
  currentConfigId?: string
}>()

const emit = defineEmits<{
  'close': []
  'select': [configId: string]
}>()

const searchQuery = ref('')

const filteredConfigs = computed(() => {
  // For interception and translation, use interception configs (LLM models)
  // For generation, use output configs
  const configs = props.type === 'generation'
    ? props.outputConfigs
    : props.interceptionConfigs

  if (!searchQuery.value) return configs

  const query = searchQuery.value.toLowerCase()
  return configs.filter(c => {
    const name = locale.value === 'de' ? c.name.de : c.name.en
    const desc = locale.value === 'de' ? c.description.de : c.description.en
    return name.toLowerCase().includes(query) || desc.toLowerCase().includes(query)
  })
})

const title = computed(() => {
  if (props.type === 'interception') {
    return locale.value === 'de' ? 'LLM & Interception wählen' : 'Select LLM & Interception'
  }
  if (props.type === 'translation') {
    return locale.value === 'de' ? 'Übersetzungs-LLM wählen' : 'Select Translation LLM'
  }
  return locale.value === 'de' ? 'Ausgabe-Modell wählen' : 'Select Output Model'
})

function getName(config: InterceptionConfigSummary | OutputConfigSummary): string {
  return locale.value === 'de' ? config.name.de : config.name.en
}

function getDescription(config: InterceptionConfigSummary | OutputConfigSummary): string {
  return locale.value === 'de' ? config.description.de : config.description.en
}

function selectConfig(configId: string) {
  emit('select', configId)
  emit('close')
}

function onOverlayClick(e: MouseEvent) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}

// Reset search when modal opens
watch(() => props.visible, (visible) => {
  if (visible) {
    searchQuery.value = ''
  }
})
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click="onOverlayClick">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ title }}</h2>
          <button class="close-btn" @click="emit('close')">×</button>
        </div>

        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="locale === 'de' ? 'Suchen...' : 'Search...'"
            autofocus
          />
        </div>

        <div class="config-list">
          <button
            v-for="config in filteredConfigs"
            :key="config.id"
            class="config-item"
            :class="{ selected: config.id === currentConfigId }"
            @click="selectConfig(config.id)"
          >
            <span class="config-icon">{{ config.icon }}</span>
            <div class="config-info">
              <span class="config-name">{{ getName(config) }}</span>
              <span class="config-desc">{{ getDescription(config) }}</span>
            </div>
            <span v-if="config.id === currentConfigId" class="check-mark">✓</span>
          </button>

          <div v-if="filteredConfigs.length === 0" class="no-results">
            <p v-if="locale === 'de'">Keine Ergebnisse gefunden</p>
            <p v-else>No results found</p>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1e293b;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #334155;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #e2e8f0;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #e2e8f0;
}

.search-box {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #334155;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
}

.search-box input::placeholder {
  color: #64748b;
}

.config-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  color: #e2e8f0;
  transition: background 0.15s;
}

.config-item:hover {
  background: #334155;
}

.config-item.selected {
  background: rgba(59, 130, 246, 0.2);
}

.config-icon {
  font-size: 1.5rem;
  width: 2.5rem;
  text-align: center;
}

.config-info {
  flex: 1;
  min-width: 0;
}

.config-name {
  display: block;
  font-weight: 500;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.config-desc {
  display: block;
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.check-mark {
  color: #3b82f6;
  font-size: 1.25rem;
}

.no-results {
  padding: 2rem;
  text-align: center;
}

.no-results p {
  color: #64748b;
  margin: 0;
}
</style>
