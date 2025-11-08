<template>
  <div class="config-canvas">
    <!-- Config tiles -->
    <ConfigTile
      v-for="config in positionedConfigs"
      :key="config.id"
      :config="config"
      :x="config.position!.x"
      :y="config.position!.y"
      :is-dimmed="isDimmed"
      :selected-properties="selectedProperties"
      :current-language="currentLanguage"
      @select="handleConfigSelect"
    />

    <!-- Match counter -->
    <div v-if="!isDimmed" class="match-counter">
      {{ matchCount }} {{ matchCount === 1 ? 'config' : 'configs' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import ConfigTile from './ConfigTile.vue'
import type { ConfigMetadata } from '@/stores/configSelection'

/**
 * ConfigCanvas - Quadrants I, III, IV (upper-right, lower-left, lower-right)
 *
 * Displays config tiles with random distribution and overlap prevention.
 * Uses grid+jitter algorithm for positioning.
 *
 * Session 35 - Phase 1 Property Quadrants Implementation
 */

interface ConfigWithPosition extends ConfigMetadata {
  position?: { x: number; y: number }
}

interface Props {
  configs: ConfigMetadata[]
  selectedProperties: string[]
  matchCount: number
  canvasWidth: number
  canvasHeight: number
  isDimmed?: boolean
  currentLanguage: 'en' | 'de'
}

const props = withDefaults(defineProps<Props>(), {
  isDimmed: false
})

const emit = defineEmits<{
  selectConfig: [configId: string]
}>()

// Tile dimensions (must match ConfigTile.vue)
const TILE_WIDTH = 260
const TILE_HEIGHT = 120
const TILE_MARGIN = 50 // Minimum spacing between tiles (increased for better breathing room)

// Positioned configs
const positionedConfigs = ref<ConfigWithPosition[]>([])

/**
 * Calculate tile positions using grid+jitter algorithm
 * Prevents overlaps while maintaining random appearance
 * Avoids upper-left property area (40% width, 40% height)
 */
function calculatePositions() {
  const configs = [...props.configs]

  if (configs.length === 0) {
    positionedConfigs.value = []
    return
  }

  // Calculate grid dimensions
  const effectiveTileWidth = TILE_WIDTH + TILE_MARGIN
  const effectiveTileHeight = TILE_HEIGHT + TILE_MARGIN

  const cols = Math.floor(props.canvasWidth / effectiveTileWidth)
  const rows = Math.floor(props.canvasHeight / effectiveTileHeight)

  if (cols === 0 || rows === 0) {
    console.warn('[ConfigCanvas] Canvas too small for tiles')
    positionedConfigs.value = []
    return
  }

  // Property area bounds (upper-left 55% x 60% - must match PropertyCanvas!)
  const propertyAreaWidth = props.canvasWidth * 0.55
  const propertyAreaHeight = props.canvasHeight * 0.6

  /**
   * Check if a grid cell is in the property area (to avoid)
   */
  function isInPropertyArea(x: number, y: number): boolean {
    return x < propertyAreaWidth && y < propertyAreaHeight
  }

  // Create grid cells (excluding property area)
  const gridCells: Array<{ x: number; y: number }> = []
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const x = col * effectiveTileWidth + effectiveTileWidth / 2
      const y = row * effectiveTileHeight + effectiveTileHeight / 2

      // Skip cells in property area
      if (!isInPropertyArea(x, y)) {
        gridCells.push({ x, y })
      }
    }
  }

  // Shuffle grid cells for random distribution
  const shuffledCells = shuffleArray(gridCells)

  // Assign positions
  const positioned: ConfigWithPosition[] = []
  configs.forEach((config, index) => {
    if (index >= shuffledCells.length) {
      console.warn(`[ConfigCanvas] Not enough grid cells for ${configs.length} configs`)
      return
    }

    const cell = shuffledCells[index]
    if (!cell) return // Type guard

    // Add jitter (±15% of tile spacing for randomness, reduced to prevent overlaps)
    const jitterX = (Math.random() - 0.5) * effectiveTileWidth * 0.3
    const jitterY = (Math.random() - 0.5) * effectiveTileHeight * 0.3

    positioned.push({
      ...config,
      position: {
        x: Math.max(TILE_WIDTH / 2, Math.min(props.canvasWidth - TILE_WIDTH / 2, cell.x + jitterX)),
        y: Math.max(TILE_HEIGHT / 2, Math.min(props.canvasHeight - TILE_HEIGHT / 2, cell.y + jitterY))
      }
    })
  })

  positionedConfigs.value = positioned
}

/**
 * Fisher-Yates shuffle algorithm
 */
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    const temp = shuffled[i]
    shuffled[i] = shuffled[j]!
    shuffled[j] = temp!
  }
  return shuffled
}

function handleConfigSelect(configId: string) {
  emit('selectConfig', configId)
}

// Recalculate positions when configs OR canvas size changes
watch(() => props.configs, () => {
  calculatePositions()
}, { deep: true })

watch([() => props.canvasWidth, () => props.canvasHeight], () => {
  calculatePositions()
})

onMounted(() => {
  calculatePositions()
})
</script>

<style scoped>
.config-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

/* Re-enable pointer events on actual tiles */
.config-canvas :deep(.config-tile) {
  pointer-events: all;
}

.match-counter {
  position: absolute;
  bottom: 20px;
  right: 20px;
  padding: 8px 16px;
  background: rgba(20, 20, 20, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  font-weight: 500;
  pointer-events: all;
  z-index: 100;
}
</style>
