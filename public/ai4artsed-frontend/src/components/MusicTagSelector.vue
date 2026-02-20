<template>
  <div class="music-tag-selector" :class="{ disabled }">
    <div
      v-for="dim in dimensions"
      :key="dim.name"
      class="dimension-row"
    >
      <div class="dimension-label" :style="{ color: dim.color }">
        <span class="dimension-name">{{ dimLabel(dim) }}</span>
        <span v-if="dim.importance === 'high'" class="dimension-badge">{{ t('musicGenV2.mostImportant') }}</span>
      </div>
      <div class="chip-row">
        <button
          v-for="chip in dim.chips"
          :key="chip"
          class="tag-chip"
          :class="{ selected: isSelected(dim.name, chip) }"
          :style="{
            '--chip-color': dim.color,
            '--chip-bg': dim.color + '22',
            '--chip-bg-selected': dim.color + '44'
          }"
          :disabled="disabled"
          @click="toggleChip(dim.name, chip)"
        >
          {{ chip.replace(/_/g, ' ') }}
        </button>
      </div>
    </div>

    <!-- Custom Tags Input -->
    <div class="custom-tags-row">
      <label class="custom-tags-label">{{ t('musicGenV2.customTags') }}</label>
      <input
        type="text"
        class="custom-tags-input"
        :placeholder="t('musicGenV2.customTagsPlaceholder')"
        :value="customTags"
        :disabled="disabled"
        @input="onCustomTagsInput"
      />
    </div>

    <!-- Live tag preview -->
    <div v-if="compiledTags" class="tag-preview">
      <span class="tag-preview-label">Tags:</span>
      <span class="tag-preview-value">{{ compiledTags }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { localized } from '@/i18n'

const { t, locale } = useI18n()

export interface DimensionConfig {
  name: string
  label_de: string
  label_en: string
  chips: string[]
  color: string
  importance?: 'high' | 'medium' | 'low'
}

const props = withDefaults(defineProps<{
  dimensions: DimensionConfig[]
  selected: Record<string, string[]>
  customTags?: string
  disabled?: boolean
}>(), {
  customTags: '',
  disabled: false
})

const emit = defineEmits<{
  'update:selected': [value: Record<string, string[]>]
  'update:customTags': [value: string]
}>()

function dimLabel(dim: DimensionConfig): string {
  return localized({ de: dim.label_de, en: dim.label_en }, locale.value)
}

function isSelected(dimName: string, chip: string): boolean {
  return props.selected[dimName]?.includes(chip) ?? false
}

function toggleChip(dimName: string, chip: string) {
  if (props.disabled) return

  const current = { ...props.selected }
  const dimSelection = [...(current[dimName] || [])]

  const idx = dimSelection.indexOf(chip)
  if (idx >= 0) {
    dimSelection.splice(idx, 1)
  } else {
    dimSelection.push(chip)
  }

  current[dimName] = dimSelection
  emit('update:selected', current)
}

function onCustomTagsInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  emit('update:customTags', value)
}

const compiledTags = computed(() => {
  const chipTags = Object.values(props.selected).flat()
  const custom = props.customTags
    ? props.customTags.split(',').map(t => t.trim()).filter(Boolean)
    : []
  return [...chipTags, ...custom].join(',')
})

defineExpose({ compiledTags })
</script>

<style scoped>
.music-tag-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.music-tag-selector.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.dimension-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.dimension-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.dimension-badge {
  font-size: 0.6rem;
  font-weight: 400;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: none;
  letter-spacing: 0;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.tag-chip {
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 12px;
  border: 1px solid var(--chip-color, rgba(255, 255, 255, 0.2));
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
  line-height: 1.3;
}

.tag-chip:hover:not(:disabled) {
  background: var(--chip-bg, rgba(255, 255, 255, 0.1));
  color: white;
}

.tag-chip.selected {
  background: var(--chip-bg-selected, rgba(156, 39, 176, 0.3));
  color: white;
  border-color: var(--chip-color, #9c27b0);
  font-weight: 600;
}

.tag-chip:disabled {
  cursor: not-allowed;
}

/* Custom Tags Input */
.custom-tags-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 0.5rem;
}

.custom-tags-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.6);
}

.custom-tags-input {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease;
}

.custom-tags-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.custom-tags-input:focus {
  border-color: rgba(156, 39, 176, 0.5);
}

.custom-tags-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tag-preview {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-family: monospace;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  word-break: break-all;
}

.tag-preview-label {
  color: rgba(255, 255, 255, 0.4);
  margin-right: 0.5rem;
}

.tag-preview-value {
  color: rgba(255, 255, 255, 0.8);
}
</style>
