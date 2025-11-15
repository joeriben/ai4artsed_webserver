<template>
  <div
    :class="['config-tile', { dimmed: isDimmed, dragging: isDragging }]"
    :style="tileStyle"
    @mousedown="handleMouseDown"
    @touchstart="handleTouchStart"
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import type { ConfigMetadata } from '@/stores/configSelection'

/**
 * ConfigTile - Individual config tile component
 *
 * Displays a single config as a card with name and description.
 * User can drag tiles to reposition them for better overview.
 * Click (without drag) selects the config.
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 */

interface Props {
  config: ConfigMetadata
  x: number // Initial position
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

// Dragging state
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const currentX = ref(props.x)
const currentY = ref(props.y)
const hasMoved = ref(false)

const tileStyle = computed(() => ({
  left: `${currentX.value}px`,
  top: `${currentY.value}px`
}))

function handleMouseDown(event: MouseEvent) {
  // Prevent default to avoid text selection
  event.preventDefault()

  isDragging.value = true
  hasMoved.value = false
  dragStartX.value = event.clientX - currentX.value
  dragStartY.value = event.clientY - currentY.value

  // Add global listeners
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return

  hasMoved.value = true
  currentX.value = event.clientX - dragStartX.value
  currentY.value = event.clientY - dragStartY.value
}

function handleMouseUp(event: MouseEvent) {
  if (!isDragging.value) return

  isDragging.value = false

  // Remove global listeners
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)

  // If tile wasn't moved, treat it as a click
  if (!hasMoved.value) {
    emit('select', props.config.id)
  }
}

// Touch event handlers for iPad/mobile support
function handleTouchStart(event: TouchEvent) {
  // Prevent default to avoid text selection and scrolling
  event.preventDefault()

  const touch = event.touches[0]
  if (!touch) return

  isDragging.value = true
  hasMoved.value = false
  dragStartX.value = touch.clientX - currentX.value
  dragStartY.value = touch.clientY - currentY.value

  // Add global listeners
  document.addEventListener('touchmove', handleTouchMove, { passive: false })
  document.addEventListener('touchend', handleTouchEnd)
}

function handleTouchMove(event: TouchEvent) {
  if (!isDragging.value) return

  event.preventDefault() // Prevent scrolling while dragging

  const touch = event.touches[0]
  if (!touch) return

  hasMoved.value = true
  currentX.value = touch.clientX - dragStartX.value
  currentY.value = touch.clientY - dragStartY.value
}

function handleTouchEnd(event: TouchEvent) {
  if (!isDragging.value) return

  isDragging.value = false

  // Remove global listeners
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)

  // If tile wasn't moved, treat it as a tap
  if (!hasMoved.value) {
    emit('select', props.config.id)
  }
}

// Cleanup on unmount
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)
})

// Reset position when props change
onMounted(() => {
  currentX.value = props.x
  currentY.value = props.y
})
</script>

<style scoped>
.config-tile {
  position: absolute;
  width: 260px;
  min-height: 120px;
  background: rgba(20, 20, 20, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px; /* More playful, rounder */
  padding: 18px;
  cursor: grab;
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
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

/* Dragging state */
.config-tile.dragging {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.05);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
  z-index: 1000;
  user-select: none;
}
</style>
