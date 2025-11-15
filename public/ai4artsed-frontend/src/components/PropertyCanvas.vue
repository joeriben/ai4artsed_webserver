<template>
  <div class="property-canvas">
    <!-- SVG layer for rubber bands (background) -->
    <svg class="rubber-bands-layer" :viewBox="`0 0 ${canvasWidth} ${canvasHeight}`">
      <defs>
        <!-- Animated gradient for flow effect -->
        <linearGradient id="flow-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" :stop-color="'transparent'" />
          <stop offset="50%" :stop-color="'currentColor'" stop-opacity="0.3" />
          <stop offset="100%" :stop-color="'transparent'" />
          <animate
            attributeName="x1"
            values="0%;100%;0%"
            dur="3s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="x2"
            values="100%;200%;100%"
            dur="3s"
            repeatCount="indefinite"
          />
        </linearGradient>
      </defs>

      <!-- Rubber bands connecting property pairs -->
      <g v-for="(pair, index) in propertyPairs" :key="`pair-${index}`">
        <line
          :x1="getPropertyPosition(pair[0]).x"
          :y1="getPropertyPosition(pair[0]).y"
          :x2="getPropertyPosition(pair[1]).x"
          :y2="getPropertyPosition(pair[1]).y"
          :stroke="propertyColors[index]"
          stroke-width="2"
          stroke-opacity="0.4"
          class="rubber-band"
        />
      </g>
    </svg>

    <!-- Property bubbles (foreground) -->
    <PropertyBubble
      v-for="(property, index) in allProperties"
      :key="property"
      :property="property"
      :color="getPropertyColorByName(property)"
      :is-selected="isPropertySelected(property)"
      :x="propertyPositions[property]?.x || 0"
      :y="propertyPositions[property]?.y || 0"
      :symbol-data="getSymbolDataForProperty(property)"
      @toggle="handlePropertyToggle"
      @update-position="handleUpdatePosition"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PropertyBubble from './PropertyBubble.vue'
import type { PropertyPair, SymbolData } from '@/stores/configSelection'
import { useConfigSelectionStore } from '@/stores/configSelection'

/**
 * PropertyCanvas - Quadrant II (upper-left)
 *
 * Displays property bubbles with rubber band connections between opposing pairs.
 * Handles property selection with XOR logic.
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 * Session 40 - Added symbols, draggable bubbles
 */

interface Props {
  propertyPairs: PropertyPair[]
  selectedProperties: string[]
  canvasWidth: number
  canvasHeight: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleProperty: [property: string]
}>()

// Access store for symbol data
const store = useConfigSelectionStore()

// Property colors (same order as mockup)
const propertyColors = [
  '#9b87f5', // purple - chill/chaotic
  '#60a5fa', // blue - narrative/algorithmic
  '#fb923c', // orange - historical/contemporary
  '#4ade80', // green - explore/create
  '#fbbf24'  // yellow - playful/serious
]

// Map property names to colors
const propertyColorMap = computed(() => {
  const map: Record<string, string> = {}
  props.propertyPairs.forEach((pair, index) => {
    const color = propertyColors[index] || '#888'
    map[pair[0]] = color
    map[pair[1]] = color
  })
  return map
})

// All properties flattened
const allProperties = computed(() => {
  return props.propertyPairs.flat()
})

// Property positions (calculated on mount)
const propertyPositions = ref<Record<string, { x: number; y: number }>>({})

/**
 * Calculate property positions
 * Properties are randomly spread in a CIRCLE at screen center
 * Ensures no overlap between bubbles
 */
function calculatePropertyPositions() {
  const positions: Record<string, { x: number; y: number }> = {}
  const placedPositions: Array<{ x: number; y: number }> = []

  // Center of canvas
  const centerX = props.canvasWidth / 2
  const centerY = props.canvasHeight / 2

  // Circle radius for property placement area (30% of smaller dimension)
  const radius = Math.min(props.canvasWidth, props.canvasHeight) * 0.3

  // Minimum distance between bubble centers (to prevent overlap)
  const minDistance = 120

  /**
   * Check if position is valid (within circle and no overlap)
   */
  function isValidPosition(x: number, y: number): boolean {
    // Check if within circle boundary
    const distFromCenter = Math.sqrt(
      Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2)
    )
    if (distFromCenter > radius) {
      return false
    }

    // Check distance from other bubbles
    for (const placed of placedPositions) {
      const distance = Math.sqrt(
        Math.pow(x - placed.x, 2) + Math.pow(y - placed.y, 2)
      )
      if (distance < minDistance) {
        return false
      }
    }
    return true
  }

  /**
   * Find a valid random position within circle
   */
  function findValidPosition(maxAttempts = 100): { x: number; y: number } {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      // Random angle and distance from center
      const angle = Math.random() * Math.PI * 2
      const dist = Math.random() * radius
      const x = centerX + Math.cos(angle) * dist
      const y = centerY + Math.sin(angle) * dist

      if (isValidPosition(x, y)) {
        return { x, y }
      }
    }
    // Fallback: return position within circle anyway
    const angle = Math.random() * Math.PI * 2
    const dist = Math.random() * radius
    return {
      x: centerX + Math.cos(angle) * dist,
      y: centerY + Math.sin(angle) * dist
    }
  }

  // Place each property with collision detection
  props.propertyPairs.forEach((pair) => {
    // First property in pair
    const pos1 = findValidPosition()
    positions[pair[0]] = pos1
    placedPositions.push(pos1)

    // Second property in pair
    const pos2 = findValidPosition()
    positions[pair[1]] = pos2
    placedPositions.push(pos2)
  })

  propertyPositions.value = positions
}

function getPropertyPosition(property: string) {
  return propertyPositions.value[property] || { x: 0, y: 0 }
}

function getPropertyColorByName(property: string): string {
  return propertyColorMap.value[property] || '#888'
}

function isPropertySelected(property: string): boolean {
  return props.selectedProperties.includes(property)
}

function handlePropertyToggle(property: string) {
  emit('toggleProperty', property)
}

/**
 * Get symbol data for a property (Session 40)
 */
function getSymbolDataForProperty(property: string): SymbolData | undefined {
  return store.getSymbolData(property)
}

/**
 * Handle position update from draggable bubble (Session 40)
 * Constrains movement to circular boundary
 */
function handleUpdatePosition(property: string, x: number, y: number) {
  // Circular boundary constraint
  const centerX = props.canvasWidth / 2
  const centerY = props.canvasHeight / 2
  const radius = Math.min(props.canvasWidth, props.canvasHeight) * 0.3

  // Check distance from center
  const distFromCenter = Math.sqrt(
    Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2)
  )

  // If outside circle, clamp to boundary
  if (distFromCenter > radius) {
    const angle = Math.atan2(y - centerY, x - centerX)
    x = centerX + Math.cos(angle) * radius
    y = centerY + Math.sin(angle) * radius
  }

  propertyPositions.value[property] = { x, y }
}

// Recalculate positions when canvas size changes (for responsive design)
watch([() => props.canvasWidth, () => props.canvasHeight], () => {
  calculatePropertyPositions()
})

onMounted(() => {
  calculatePropertyPositions()
})
</script>

<style scoped>
.property-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 2;
}

/* Re-enable pointer events on property bubbles */
.property-canvas :deep(.property-bubble) {
  pointer-events: all;
}

.rubber-bands-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.rubber-band {
  transition: all 0.3s ease;
}

.rubber-band:hover {
  stroke-opacity: 0.8;
  stroke-width: 3;
}

/* Property bubbles are z-index 2 (via PropertyBubble component) */
</style>
