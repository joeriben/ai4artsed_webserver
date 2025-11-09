<template>
  <div
    :class="['property-bubble', { selected: isSelected }]"
    :style="bubbleStyle"
    @click="handleClick"
    :data-property="property"
  >
    {{ $t('properties.' + property) }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * PropertyBubble - Individual property bubble component
 *
 * Displays a single property as an interactive bubble.
 * Clicking toggles selection (XOR logic handled by store).
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 */

interface Props {
  property: string
  color: string
  isSelected: boolean
  x: number // Position in Quadrant II
  y: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggle: [property: string]
}>()

const bubbleStyle = computed(() => ({
  left: `${props.x}px`,
  top: `${props.y}px`,
  '--bubble-color': props.color,
  '--bubble-shadow': props.isSelected ? `0 0 20px ${props.color}` : 'none'
}))

function handleClick() {
  emit('toggle', props.property)
}
</script>

<style scoped>
.property-bubble {
  position: absolute;
  padding: 12px 24px;
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  border-radius: 25px;
  color: var(--bubble-color);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  box-shadow: var(--bubble-shadow);
  transform: translate(-50%, -50%); /* Center on position */
}

.property-bubble:hover {
  background: rgba(30, 30, 30, 0.95);
  transform: translate(-50%, -50%) scale(1.05);
}

.property-bubble.selected {
  background: var(--bubble-color);
  color: #0a0a0a;
  font-weight: 600;
  box-shadow: 0 0 20px var(--bubble-color);
}
</style>
