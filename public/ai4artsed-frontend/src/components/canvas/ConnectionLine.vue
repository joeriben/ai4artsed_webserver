<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  /** Start X position */
  x1: number
  /** Start Y position */
  y1: number
  /** End X position */
  x2: number
  /** End Y position */
  y2: number
  /** Whether this is a temporary connection being drawn */
  temporary?: boolean
  /** Whether this connection is selected/highlighted */
  selected?: boolean
}>()

const emit = defineEmits<{
  'click': []
}>()

/**
 * Generate a smooth Bezier curve path between two points
 */
const pathD = computed(() => {
  const { x1, y1, x2, y2 } = props

  // Calculate control points for a smooth curve
  // The curve bends horizontally based on the distance between points
  const dx = Math.abs(x2 - x1)
  const controlOffset = Math.min(dx * 0.5, 100) // Max control point offset of 100px

  // Control points create a horizontal S-curve
  const cx1 = x1 + controlOffset
  const cy1 = y1
  const cx2 = x2 - controlOffset
  const cy2 = y2

  return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`
})
</script>

<template>
  <g class="connection-line" :class="{ temporary, selected }">
    <!-- Invisible wider path for easier clicking -->
    <path
      v-if="!temporary"
      :d="pathD"
      class="connection-hitarea"
      @click.stop="emit('click')"
    />
    <!-- Visible connection path -->
    <path
      :d="pathD"
      class="connection-path"
      @click.stop="emit('click')"
    />
    <!-- Arrow indicator at the end -->
    <circle
      v-if="!temporary"
      :cx="x2 - 8"
      :cy="y2"
      r="3"
      class="connection-arrow"
    />
  </g>
</template>

<style scoped>
.connection-line {
  pointer-events: none;
}

.connection-hitarea {
  fill: none;
  stroke: transparent;
  stroke-width: 20;
  pointer-events: stroke;
  cursor: pointer;
}

.connection-path {
  fill: none;
  stroke: #3b82f6;
  stroke-width: 2;
  pointer-events: stroke;
  cursor: pointer;
  transition: stroke 0.15s, stroke-width 0.15s;
}

.connection-line:hover .connection-path,
.connection-line.selected .connection-path {
  stroke: #60a5fa;
  stroke-width: 3;
}

.connection-line.temporary .connection-path {
  stroke: #3b82f6;
  stroke-dasharray: 5 5;
  opacity: 0.6;
  pointer-events: none;
}

.connection-arrow {
  fill: #3b82f6;
  pointer-events: none;
  transition: fill 0.15s;
}

.connection-line:hover .connection-arrow,
.connection-line.selected .connection-arrow {
  fill: #60a5fa;
}

.connection-line.temporary .connection-arrow {
  display: none;
}
</style>
