<template>
  <div
    ref="bubbleEl"
    :class="['property-bubble', { selected: isSelected, dragging: isDragging }]"
    :style="bubbleStyle"
    :title="tooltip"
    @click="handleClick"
    @mousedown="startDrag"
    :data-property="property"
  >
    <span v-if="symbol" class="property-symbol">{{ symbol }}</span>
    <span class="property-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

/**
 * PropertyBubble - Individual property bubble component
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 * Session 40 - Added symbols, larger icons, draggable
 */

interface SymbolData {
  symbol: string
  label: string
  tooltip: string
}

interface Props {
  property: string
  color: string
  isSelected: boolean
  x: number
  y: number
  symbolData?: SymbolData  // NEW: Symbol, label, tooltip
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggle: [property: string]
  updatePosition: [property: string, x: number, y: number]
}>()

const bubbleEl = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

// Symbol and label from symbolData or fallback to i18n
const symbol = computed(() => props.symbolData?.symbol || '')
const label = computed(() => props.symbolData?.label || props.property)
const tooltip = computed(() => props.symbolData?.tooltip || '')

const bubbleStyle = computed(() => ({
  left: `${props.x}px`,
  top: `${props.y}px`,
  '--bubble-color': props.color,
  '--bubble-shadow': props.isSelected ? `0 0 20px ${props.color}` : 'none',
  cursor: isDragging.value ? 'grabbing' : 'grab'
}))

function handleClick(event: MouseEvent) {
  if (!isDragging.value) {
    emit('toggle', props.property)
  }
}

// Draggable functionality
function startDrag(event: MouseEvent) {
  event.preventDefault()
  isDragging.value = true

  const rect = bubbleEl.value?.getBoundingClientRect()
  if (rect) {
    dragOffset.value = {
      x: event.clientX - rect.left - rect.width / 2,
      y: event.clientY - rect.top - rect.height / 2
    }
  }

  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event: MouseEvent) {
  if (!isDragging.value) return

  const newX = event.clientX - dragOffset.value.x
  const newY = event.clientY - dragOffset.value.y

  emit('updatePosition', props.property, newX, newY)
}

function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}
</script>

<style scoped>
.property-bubble {
  position: absolute;
  padding: 16px 28px;  /* Increased padding for larger bubbles */
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  border-radius: 30px;
  color: var(--bubble-color);
  font-size: 16px;
  font-weight: 500;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
  box-shadow: var(--bubble-shadow);
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 120px;
  justify-content: center;
}

.property-symbol {
  font-size: 32px;  /* MUCH larger icons */
  line-height: 1;
  flex-shrink: 0;
}

.property-label {
  font-size: 15px;
  white-space: nowrap;
}

.property-bubble:hover:not(.dragging) {
  background: rgba(30, 30, 30, 0.95);
  transform: translate(-50%, -50%) scale(1.08);
}

.property-bubble.dragging {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.property-bubble.selected {
  background: var(--bubble-color);
  color: #0a0a0a;
  font-weight: 600;
  box-shadow: 0 0 24px var(--bubble-color);
  border-width: 3px;
}

.property-bubble.selected .property-symbol {
  filter: brightness(0.3);
}

.property-bubble.selected .property-label {
  font-weight: 700;
}

/* Mobile: Hide label, only show larger symbol */
@media (max-width: 768px) {
  .property-label {
    display: none;
  }

  .property-bubble {
    padding: 20px;
    min-width: auto;
  }

  .property-symbol {
    font-size: 40px;  /* Even larger on mobile */
  }
}
</style>
