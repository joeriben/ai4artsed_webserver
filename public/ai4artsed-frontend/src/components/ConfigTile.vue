<template>
  <div
    :class="['config-tile', { dimmed: isDimmed }]"
    :style="tileStyle"
    @click="handleClick"
    :data-config-id="config.id"
  >
    <div class="tile-header">
      <h3 class="tile-name">{{ config.name[currentLanguage] }}</h3>
    </div>
    <div class="tile-body">
      <p class="tile-description">
        {{ config.short_description[currentLanguage] }}
      </p>
    </div>
    <div class="tile-footer">
      <div class="tile-properties">
        <span
          v-for="prop in config.properties"
          :key="prop"
          :class="['property-tag', { selected: selectedProperties.includes(prop) }]"
          :style="{ '--tag-color': getPropertyColor(prop) }"
        >
          {{ prop }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ConfigMetadata } from '@/stores/configSelection'

/**
 * ConfigTile - Individual config tile component
 *
 * Displays a single config as a card with name, description, and properties.
 * Positioned dynamically to prevent overlaps.
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 */

interface Props {
  config: ConfigMetadata
  x: number // Position in Quadrants I/III/IV
  y: number
  isDimmed?: boolean // When no match
  selectedProperties: string[]
  currentLanguage: 'en' | 'de'
}

const props = withDefaults(defineProps<Props>(), {
  isDimmed: false
})

const emit = defineEmits<{
  select: [configId: string]
}>()

const tileStyle = computed(() => ({
  left: `${props.x}px`,
  top: `${props.y}px`
}))

// Property colors (should match PropertyCanvas)
const propertyColors: Record<string, string> = {
  calm: '#9b87f5',
  chaotic: '#9b87f5',
  narrative: '#60a5fa',
  algorithmic: '#60a5fa',
  facts: '#f87171',
  emotion: '#f87171',
  historical: '#fb923c',
  contemporary: '#fb923c',
  explore: '#4ade80',
  create: '#4ade80',
  playful: '#fbbf24',
  serious: '#fbbf24'
}

function getPropertyColor(property: string): string {
  return propertyColors[property] || '#888'
}

function handleClick() {
  emit('select', props.config.id)
}
</script>

<style scoped>
.config-tile {
  position: absolute;
  width: 280px;
  min-height: 160px;
  background: rgba(20, 20, 20, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transform: translate(-50%, -50%); /* Center on position */
}

.config-tile:hover {
  background: rgba(30, 30, 30, 0.98);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%) scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.config-tile.dimmed {
  opacity: 0.3;
  pointer-events: none;
}

.tile-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 8px;
}

.tile-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.tile-body {
  flex: 1;
}

.tile-description {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.7);
}

.tile-footer {
  margin-top: auto;
}

.tile-properties {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.property-tag {
  padding: 4px 10px;
  font-size: 11px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--tag-color);
  color: var(--tag-color);
  font-weight: 500;
  transition: all 0.2s ease;
}

.property-tag.selected {
  background: var(--tag-color);
  color: #0a0a0a;
  font-weight: 600;
}
</style>
