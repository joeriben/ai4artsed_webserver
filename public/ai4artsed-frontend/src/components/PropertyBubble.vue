<template>
  <div
    ref="bubbleEl"
    :class="['property-bubble', { selected: isSelected, dragging: isDragging }]"
    :style="bubbleStyle"
    :title="tooltip"
    @click="handleClick"
    @mousedown="startDrag"
    @touchstart="startDragTouch"
    :data-property="property"
  >
    <!-- Icon based on property -->
    <span class="property-symbol">
      <!-- Technical Imaging -->
      <svg v-if="property === 'technical_imaging'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="M440-440ZM120-120q-33 0-56.5-23.5T40-200v-480q0-33 23.5-56.5T120-760h126l74-80h240l74 80h126q33 0 56.5 23.5T840-680v480q0 33-23.5 56.5T760-120H120Zm0-80h640v-480H638l-73-80H395l-73 80H120v480Zm320-60q75 0 127.5-52.5T620-440q0-75-52.5-127.5T440-620q-75 0-127.5 52.5T260-440q0 75 52.5 127.5T440-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29Z"/>
      </svg>
      <!-- Heritage/Arts -->
      <svg v-else-if="property === 'heritage' || property === 'arts'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="M160-80q-33 0-56.5-23.5T80-160v-360q-25-33-32.5-71T40-672v-48q0-33 23.5-56.5T120-800h80q33 0 56.5 23.5T280-720v48q0 43-7.5 81T240-520v120h480v-120q-25-33-32.5-71T680-672v-48q0-33 23.5-56.5T760-800h80q33 0 56.5 23.5T920-720v48q0 43-7.5 81T880-520v360q0 33-23.5 56.5T800-80H160Zm0-80h280v-80H160v80Zm360 0h280v-80H520v80ZM160-320h280v-80H160v80Zm360 0h280v-80H520v80ZM120-720h80v-40h-80v40Zm640 0h80v-40h-80v40ZM280-560q23-14 34.5-37.5T326-648v-72h-46v72q0 27 11.5 50.5T326-560Zm354 0q23-14 34.5-37.5T706-648v-72h-46v72q0 27 11.5 50.5T706-560ZM200-720h80-80Zm560 0h80-80ZM300-240Zm360 0ZM300-400Zm360 0Z"/>
      </svg>
      <!-- Attitudes (NEW) -->
      <svg v-else-if="property === 'attitudes'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="M620-520q25 0 42.5-17.5T680-580q0-25-17.5-42.5T620-640q-25 0-42.5 17.5T560-580q0 25 17.5 42.5T620-520Zm-280 0q25 0 42.5-17.5T400-580q0-25-17.5-42.5T340-640q-25 0-42.5 17.5T280-580q0 25 17.5 42.5T340-520Zm140 260q68 0 123.5-38.5T684-400h-66q-22 37-58.5 58.5T480-320q-43 0-79.5-21.5T342-400h-66q25 63 80.5 101.5T480-260Zm0 180q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/>
      </svg>
      <!-- Critical Thinking -->
      <svg v-else-if="property === 'critical_thinking'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="M0-240v-63q0-43 44-70t116-27q13 0 25 .5t23 2.5q-14 21-21 44t-7 48v65H0Zm240 0v-65q0-32 17.5-58.5T307-410q32-20 76.5-30t96.5-10q53 0 97.5 10t76.5 30q32 20 49 46.5t17 58.5v65H240Zm540 0v-65q0-26-6.5-49T754-397q11-2 22.5-2.5t23.5-.5q72 0 116 26.5t44 70.5v63H780Zm-455-80h311q-10-20-55.5-35T480-370q-55 0-100.5 15T325-320ZM160-440q-33 0-56.5-23.5T80-520q0-34 23.5-57t56.5-23q34 0 57 23t23 57q0 33-23 56.5T160-440Zm640 0q-33 0-56.5-23.5T720-520q0-34 23.5-57t56.5-23q34 0 57 23t23 57q0 33-23 56.5T800-440Zm-320-40q-50 0-85-35t-35-85q0-51 35-85.5t85-34.5q51 0 85.5 34.5T600-600q0 50-34.5 85T480-480Zm0-80q17 0 28.5-11.5T520-600q0-17-11.5-28.5T480-640q-17 0-28.5 11.5T440-600q0 17 11.5 28.5T480-560Zm1 240Zm-1-280Z"/>
      </svg>
      <!-- Semantics -->
      <svg v-else-if="property === 'semantics'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="m240-400 142-320h74l142 320h-72l-32-72H346l-32 72h-74Zm128-130h102l-48-112h-6l-48 112Zm318 330q-33 0-56.5-23.5T606-280v-150l-88 59-41-62 129-87-129-87 41-62 88 59v-150q0-33 23.5-56.5T686-840q33 0 56.5 23.5T766-760v150l88-59 41 62-129 87 129 87-41 62-88-59v150q0 33-23.5 56.5T686-200Z"/>
      </svg>
      <!-- Hacking/Analysis -->
      <svg v-else-if="property === 'hacking' || property === 'analysis'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="M180-120q-24 0-42-18t-18-42v-600q0-24 18-42t42-18h600q24 0 42 18t18 42v600q0 24-18 42t-42 18H180Zm0-660v600-600Zm180 200h240q8 0 14-6t6-14q0-8-6-14t-14-6H360q-8 0-14 6t-6 14q0 8 6 14t14 6Zm0 160h80q8 0 14-6t6-14q0-8-6-14t-14-6h-80q-8 0-14 6t-6 14q0 8 6 14t14 6Zm280-40q17 0 28.5-11.5T680-500q0-17-11.5-28.5T640-540q-17 0-28.5 11.5T600-500q0 17 11.5 28.5T640-460Zm-80 80q17 0 28.5-11.5T600-420q0-17-11.5-28.5T560-460q-17 0-28.5 11.5T520-420q0 17 11.5 28.5T560-380Zm80 80q17 0 28.5-11.5T680-340q0-17-11.5-28.5T640-380q-17 0-28.5 11.5T600-340q0 17 11.5 28.5T640-300ZM180-180h600v-600H180v600Z"/>
      </svg>
      <!-- Aesthetics/Magic Wand -->
      <svg v-else-if="property === 'aesthetics'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="m326-282-58-124-124-58 124-58 58-124 58 124 124 58-124 58-58 124ZM490-40l-42-90-90-42 90-42 42-90 42 90 90 42-90 42-42 90Zm256-502-42-90-90-42 90-42 42-90 42 90 90 42-90 42-42 90ZM196-618 80-734l116-116 60 60-56 56 56 56-60 60Zm568 0-60-60 56-56-56-56 60-60 116 116-116 116ZM480-40 360-400 40-520l320-120 120-320 120 320 320 120-320 120L480-40Zm0-159 70-189 189-70-189-70-70-189-70 189-189 70 189 70 70 189Zm0-259Z"/>
      </svg>
      <!-- Freestyle/YOU -->
      <svg v-else-if="property === 'freestyle'" xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="currentColor">
        <path d="M480-280q17 0 28.5-11.5T520-320v-40h40q17 0 28.5-11.5T600-400q0-17-11.5-28.5T560-440h-40v-40q0-17-11.5-28.5T480-520q-17 0-28.5 11.5T440-480v40h-40q-17 0-28.5 11.5T360-400q0 17 11.5 28.5T400-360h40v40q0 17 11.5 28.5T480-280ZM200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h168q13-36 43.5-58t68.5-22q38 0 68.5 22t43.5 58h168q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm280-590q13 0 21.5-8.5T510-820q0-13-8.5-21.5T480-850q-13 0-21.5 8.5T450-820q0 13 8.5 21.5T480-790ZM200-200v-560 560Z"/>
      </svg>
      <!-- Fallback to emoji if no match -->
      <span v-else>{{ symbol }}</span>
    </span>
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
  x: number  // Now percentage (0-100) instead of pixels
  y: number  // Now percentage (0-100) instead of pixels
  symbolData?: SymbolData  // NEW: Symbol, label, tooltip
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggle: [property: string]
  updatePosition: [property: string, x: number, y: number]
}>()

const bubbleEl = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const hasDragged = ref(false)  // Track if actual dragging occurred
const touchStartPos = ref({ x: 0, y: 0 })  // Track initial touch position for tap detection

// Symbol and label from symbolData or fallback to i18n
const symbol = computed(() => props.symbolData?.symbol || '')
const label = computed(() => props.symbolData?.label || props.property)
const tooltip = computed(() => props.symbolData?.tooltip || '')

const bubbleStyle = computed(() => ({
  left: `${props.x}%`,  // Percentage positioning
  top: `${props.y}%`,   // Percentage positioning
  '--bubble-color': props.color,
  '--bubble-shadow': props.isSelected ? `0 0 20px ${props.color}` : 'none',
  cursor: isDragging.value ? 'grabbing' : 'grab'
}))

function handleClick(event: MouseEvent) {
  // Prevent toggle if currently dragging or just finished dragging
  if (!isDragging.value && !hasDragged.value) {
    console.log('[PropertyBubble] Click:', props.property)
    emit('toggle', props.property)
  }
}

// Draggable functionality (now with percentage calculations)
function startDrag(event: MouseEvent) {
  event.preventDefault()
  isDragging.value = true
  hasDragged.value = false  // Reset drag flag

  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event: MouseEvent) {
  if (!isDragging.value || !bubbleEl.value) return

  hasDragged.value = true  // Mark that dragging occurred

  // Get cluster-wrapper (parent container)
  const clusterWrapper = bubbleEl.value.parentElement
  if (!clusterWrapper) return

  const rect = clusterWrapper.getBoundingClientRect()

  // Calculate position relative to cluster-wrapper
  const relativeX = event.clientX - rect.left
  const relativeY = event.clientY - rect.top

  // Convert to percentage (0-100)
  const percentX = (relativeX / rect.width) * 100
  const percentY = (relativeY / rect.height) * 100

  emit('updatePosition', props.property, percentX, percentY)
}

function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)

  // Reset drag flag after short delay to prevent click event
  setTimeout(() => {
    hasDragged.value = false
  }, 100)
}

// Touch event handlers for iPad/mobile support (now with percentage calculations)
function startDragTouch(event: TouchEvent) {
  event.preventDefault()
  isDragging.value = true
  hasDragged.value = false  // Reset drag flag

  const touch = event.touches[0]
  if (!touch) return

  // Store initial touch position for tap detection
  touchStartPos.value = {
    x: touch.clientX,
    y: touch.clientY
  }

  document.addEventListener('touchmove', onDragTouch, { passive: false })
  document.addEventListener('touchend', stopDragTouch)
}

function onDragTouch(event: TouchEvent) {
  if (!isDragging.value || !bubbleEl.value) return
  event.preventDefault() // Prevent scrolling while dragging

  hasDragged.value = true  // Mark that dragging occurred

  const touch = event.touches[0]
  if (!touch) return

  // Get cluster-wrapper (parent container)
  const clusterWrapper = bubbleEl.value.parentElement
  if (!clusterWrapper) return

  const rect = clusterWrapper.getBoundingClientRect()

  // Calculate position relative to cluster-wrapper
  const relativeX = touch.clientX - rect.left
  const relativeY = touch.clientY - rect.top

  // Convert to percentage (0-100)
  const percentX = (relativeX / rect.width) * 100
  const percentY = (relativeY / rect.height) * 100

  emit('updatePosition', props.property, percentX, percentY)
}

function stopDragTouch(event: TouchEvent) {
  isDragging.value = false
  document.removeEventListener('touchmove', onDragTouch)
  document.removeEventListener('touchend', stopDragTouch)

  // Tap detection: if minimal movement, treat as tap/click
  if (!hasDragged.value) {
    const touch = event.changedTouches[0]
    if (touch) {
      const dx = Math.abs(touch.clientX - touchStartPos.value.x)
      const dy = Math.abs(touch.clientY - touchStartPos.value.y)
      const tapThreshold = 10 // pixels

      // If movement is less than threshold, treat as tap
      if (dx < tapThreshold && dy < tapThreshold) {
        emit('toggle', props.property)
      }
    }
  }

  // Reset drag flag after short delay
  setTimeout(() => {
    hasDragged.value = false
  }, 100)
}
</script>

<style scoped>
.property-bubble {
  position: absolute;
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  border-radius: 50%;  /* Circular frames */
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
  justify-content: center;

  /* Responsive sizing: percentage of cluster-wrapper */
  width: 12%;   /* 12% of cluster-wrapper width */
  aspect-ratio: 1 / 1;  /* Keep circular */
}

.property-symbol {
  font-size: clamp(1.5rem, 3vw, 2.5rem);  /* Responsive symbol size */
  line-height: 1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.property-symbol svg {
  width: clamp(32px, 6vw, 48px);
  height: clamp(32px, 6vw, 48px);
}

.property-label {
  font-size: 15px;
  white-space: nowrap;
  display: none;  /* Hide labels - icon-only view */
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
</style>
