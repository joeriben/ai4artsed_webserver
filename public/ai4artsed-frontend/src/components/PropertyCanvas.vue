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
      @toggle="handlePropertyToggle"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PropertyBubble from './PropertyBubble.vue'
import type { PropertyPair } from '@/stores/configSelection'

/**
 * PropertyCanvas - Quadrant II (upper-left)
 *
 * Displays property bubbles with rubber band connections between opposing pairs.
 * Handles property selection with XOR logic.
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
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

// Property colors (same order as mockup)
const propertyColors = [
  '#9b87f5', // purple - calm/chaotic
  '#60a5fa', // blue - narrative/algorithmic
  '#f87171', // red - facts/emotion
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
 * Properties are randomly spread in UPPER-LEFT area only (not whole canvas)
 * Ensures no overlap between bubbles
 */
function calculatePropertyPositions() {
  const positions: Record<string, { x: number; y: number }> = {}
  const placedPositions: Array<{ x: number; y: number }> = []

  // Properties only in upper-left area (40% width, 40% height)
  const propertyAreaWidth = props.canvasWidth * 0.4
  const propertyAreaHeight = props.canvasHeight * 0.4

  // Margins to keep bubbles away from edges
  const marginX = 80
  const marginY = 60
  const effectiveWidth = propertyAreaWidth - marginX * 2
  const effectiveHeight = propertyAreaHeight - marginY * 2

  // Minimum distance between bubble centers (to prevent overlap)
  const minDistance = 120

  /**
   * Check if position is valid (no overlap with existing bubbles)
   */
  function isValidPosition(x: number, y: number): boolean {
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
   * Find a valid random position (with max attempts to avoid infinite loop)
   */
  function findValidPosition(maxAttempts = 100): { x: number; y: number } {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const x = marginX + Math.random() * effectiveWidth
      const y = marginY + Math.random() * effectiveHeight

      if (isValidPosition(x, y)) {
        return { x, y }
      }
    }
    // Fallback: return position anyway (rare case when canvas is too small)
    return {
      x: marginX + Math.random() * effectiveWidth,
      y: marginY + Math.random() * effectiveHeight
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
.property-canvas >>> .property-bubble {
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
