<template>
  <div
    :class="['config-bubble', { dimmed: isDimmed, dragging: isDragging, 'long-pressing': isLongPressing }]"
    :style="bubbleStyle"
    @mousedown="handleMouseDown"
    @touchstart="handleTouchStart"
    :data-config-id="config.id"
  >
    <!-- Preview image as background -->
    <div class="preview-image" :style="previewImageStyle"></div>

    <!-- Text badge overlay -->
    <div class="text-badge">
      {{ config.name[currentLanguage] }}
    </div>
  </div>

  <!-- Long-press modal -->
  <Teleport to="body">
    <div v-if="showModal" class="config-modal-overlay" @click="closeModal">
      <div class="config-modal" @click.stop>
        <img v-if="previewImageUrl" :src="previewImageUrl" class="modal-preview" />
        <h2>{{ config.name[currentLanguage] }}</h2>
        <p class="modal-description">{{ config.description[currentLanguage] }}</p>
        <button class="modal-close" @click="closeModal">{{ currentLanguage === 'de' ? 'Schließen' : 'Close' }}</button>
      </div>
    </div>
  </Teleport>
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

// Long-press state
const isLongPressing = ref(false)
const showModal = ref(false)
let longPressTimer: number | null = null
const LONG_PRESS_DURATION = 500 // ms

// Preview image URL
const previewImageUrl = computed(() => {
  // Map config.id to preview image
  // e.g., "dada" -> "/config-previews/dada.png"
  return `/config-previews/${props.config.id}.png`
})

const bubbleStyle = computed(() => ({
  left: `${currentX.value}px`,
  top: `${currentY.value}px`
}))

const previewImageStyle = computed(() => ({
  backgroundImage: `url(${previewImageUrl.value})`
}))

function startLongPressTimer() {
  longPressTimer = window.setTimeout(() => {
    isLongPressing.value = true
    showModal.value = true
    isDragging.value = false // Cancel drag if long-press triggered
  }, LONG_PRESS_DURATION)
}

function cancelLongPressTimer() {
  if (longPressTimer !== null) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
  isLongPressing.value = false
}

function closeModal() {
  showModal.value = false
}

function handleMouseDown(event: MouseEvent) {
  event.preventDefault()

  isDragging.value = true
  hasMoved.value = false
  dragStartX.value = event.clientX - currentX.value
  dragStartY.value = event.clientY - currentY.value

  // Start long-press timer
  startLongPressTimer()

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return

  hasMoved.value = true
  currentX.value = event.clientX - dragStartX.value
  currentY.value = event.clientY - dragStartY.value

  // Cancel long-press if moved
  if (hasMoved.value) {
    cancelLongPressTimer()
  }
}

function handleMouseUp(event: MouseEvent) {
  if (!isDragging.value && !isLongPressing.value) return

  isDragging.value = false
  cancelLongPressTimer()

  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)

  // Tap (no move, no long-press) = select
  if (!hasMoved.value && !isLongPressing.value) {
    emit('select', props.config.id)
  }
}

// Touch event handlers for iPad/mobile support
function handleTouchStart(event: TouchEvent) {
  event.preventDefault()

  const touch = event.touches[0]
  if (!touch) return

  isDragging.value = true
  hasMoved.value = false
  dragStartX.value = touch.clientX - currentX.value
  dragStartY.value = touch.clientY - currentY.value

  // Start long-press timer
  startLongPressTimer()

  document.addEventListener('touchmove', handleTouchMove, { passive: false })
  document.addEventListener('touchend', handleTouchEnd)
}

function handleTouchMove(event: TouchEvent) {
  if (!isDragging.value) return

  event.preventDefault()

  const touch = event.touches[0]
  if (!touch) return

  hasMoved.value = true
  currentX.value = touch.clientX - dragStartX.value
  currentY.value = touch.clientY - dragStartY.value

  // Cancel long-press if moved
  if (hasMoved.value) {
    cancelLongPressTimer()
  }
}

function handleTouchEnd(event: TouchEvent) {
  if (!isDragging.value && !isLongPressing.value) return

  isDragging.value = false
  cancelLongPressTimer()

  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)

  // Tap (no move, no long-press) = select
  if (!hasMoved.value && !isLongPressing.value) {
    emit('select', props.config.id)
  }
}

// Cleanup on unmount
onUnmounted(() => {
  cancelLongPressTimer()
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
/* Round config bubble with preview image */
.config-bubble {
  position: absolute;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  transform: translate(-50%, -50%);
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.config-bubble:hover {
  transform: translate(-50%, -50%) scale(1.08);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
}

.config-bubble.dimmed {
  opacity: 0.3;
  pointer-events: none;
}

.config-bubble.dragging {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
  z-index: 1000;
}

.config-bubble.long-pressing {
  transform: translate(-50%, -50%) scale(0.95);
}

/* Preview image background */
.preview-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Schwarze Bande: volle Breite, Kreis-overflow clippt die Ecken */
.text-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  padding: 4px 10px 8px;
  line-height: 1.3;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Long-press modal */
.config-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(8px);
}

.config-modal {
  background: rgba(20, 20, 20, 0.98);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 32px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.8);
}

.modal-preview {
  width: 100%;
  border-radius: 16px;
  margin-bottom: 20px;
}

.config-modal h2 {
  margin: 0 0 16px 0;
  color: white;
  font-size: 24px;
}

.modal-description {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 24px;
}

.modal-close {
  width: 100%;
  padding: 12px;
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border: 2px solid #60a5fa;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #60a5fa;
  color: black;
}
</style>
