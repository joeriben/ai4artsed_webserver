<template>
  <div class="property-canvas">
    <!-- REMOVED: Rubber bands (no pairs anymore) -->

    <!-- Category bubbles (foreground) -->
    <PropertyBubble
      v-for="category in categories"
      :key="category"
      :property="category"
      :color="getCategoryColor(category)"
      :is-selected="isPropertySelected(category)"
      :x="categoryPositions[category]?.x || 0"
      :y="categoryPositions[category]?.y || 0"
      :symbol-data="getSymbolDataForProperty(category)"
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
  selectedProperties: string[]
  canvasWidth: number
  canvasHeight: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleProperty: [property: string]
}>()

// Access store for categories and symbol data
const store = useConfigSelectionStore()

// Get categories from store
const categories = computed(() => store.categories)

// Category bubble size (base unit - fixed for visual consistency)
const CATEGORY_BUBBLE_DIAMETER = 100

/**
 * Calculate responsive radius for category circle
 * Uses 25% of the smaller canvas dimension to ensure circles stay circular
 * and centered regardless of canvas size or aspect ratio
 */
function getResponsiveRadius(): number {
  const smallerDimension = Math.min(props.canvasWidth, props.canvasHeight)
  return smallerDimension * 0.25  // 25% of smaller dimension
}

// Category colors
const categoryColorMap: Record<string, string> = {
  'semantics': '#2196F3',    // blue 💬
  'aesthetics': '#9C27B0',   // purple 🪄
  'arts': '#E91E63',          // pink 🖌️
  'heritage': '#4CAF50',      // green 🌍
  'freestyle': '#FFC107'      // amber 🫵
}

// Category positions (calculated on mount)
const categoryPositions = ref<Record<string, { x: number; y: number }>>({})

/**
 * Calculate category positions
 * Freestyle in center, others in circle around it (X-formation)
 * Uses responsive radius based on canvas size
 */
function calculateCategoryPositions() {
  const positions: Record<string, { x: number; y: number }> = {}

  // Center of canvas (true geometric center)
  const centerX = props.canvasWidth / 2
  const centerY = props.canvasHeight / 2

  // Responsive circle radius: proportional to canvas size
  const radius = getResponsiveRadius()

  console.log('[PropertyCanvas] Calculating category positions:', {
    canvasWidth: props.canvasWidth,
    canvasHeight: props.canvasHeight,
    centerX,
    centerY,
    radius,
    smallerDimension: Math.min(props.canvasWidth, props.canvasHeight)
  })

  // Freestyle in center
  if (categories.value.includes('freestyle')) {
    positions['freestyle'] = { x: centerX, y: centerY }
  }

  // Other categories in circle around center (symmetrisch, X-Form statt Kreuz)
  const otherCategories = categories.value.filter(c => c !== 'freestyle')
  const angleStep = (2 * Math.PI) / otherCategories.length

  otherCategories.forEach((category, index) => {
    // Gleichmäßige Winkel, Start oben-rechts (45° / -45°)
    const angle = index * angleStep - Math.PI / 4  // -45° start (X-formation)

    const x = centerX + Math.cos(angle) * radius
    const y = centerY + Math.sin(angle) * radius

    positions[category] = { x, y }
  })

  categoryPositions.value = positions
}

function getCategoryColor(category: string): string {
  return categoryColorMap[category] || '#888'
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
 * Handle position update from draggable bubble
 * Constrains movement to circular boundary using responsive radius
 */
function handleUpdatePosition(category: string, x: number, y: number) {
  // Circular boundary constraint (same responsive radius as calculateCategoryPositions)
  const centerX = props.canvasWidth / 2
  const centerY = props.canvasHeight / 2
  const radius = getResponsiveRadius()  // Match radius from calculateCategoryPositions

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

  categoryPositions.value[category] = { x, y }
}

// Recalculate positions when canvas size changes or categories change
watch([() => props.canvasWidth, () => props.canvasHeight, categories], () => {
  calculateCategoryPositions()
})

onMounted(() => {
  calculateCategoryPositions()
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
