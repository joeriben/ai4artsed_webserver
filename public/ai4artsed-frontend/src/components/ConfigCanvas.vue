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

// Bubble dimensions (must match ConfigTile.vue - round bubbles now!)
const BUBBLE_DIAMETER = 240
const BUBBLE_SPACING = 80 // Minimum spacing between bubbles

// Positioned configs
const positionedConfigs = ref<ConfigWithPosition[]>([])

// Category positions (must match PropertyCanvas.vue)
const CATEGORY_RADIUS = 125 // Distance from canvas center to category bubbles
const CATEGORY_BUBBLE_SIZE = 100 // Category bubble diameter

/**
 * Get category bubble position (matches PropertyCanvas.vue logic)
 */
function getCategoryPosition(category: string): { x: number; y: number } {
  const centerX = props.canvasWidth / 2
  const centerY = props.canvasHeight / 2

  console.log('[ConfigCanvas] Getting category position for', category, {
    canvasWidth: props.canvasWidth,
    canvasHeight: props.canvasHeight,
    centerX,
    centerY
  })

  // Freestyle in center
  if (category === 'freestyle') {
    return { x: centerX, y: centerY }
  }

  // Other categories in X-formation around center
  const otherCategories = ['semantics', 'aesthetics', 'arts', 'heritage'].filter(c => {
    // Only include categories that exist in configs
    return props.configs.some(cfg => cfg.properties.includes(c))
  })

  const index = otherCategories.indexOf(category)
  if (index === -1) {
    // Fallback for unknown category
    return { x: centerX, y: centerY }
  }

  const angleStep = (2 * Math.PI) / otherCategories.length
  const angle = index * angleStep - Math.PI / 4 // -45° start (X-formation)

  const x = centerX + Math.cos(angle) * CATEGORY_RADIUS
  const y = centerY + Math.sin(angle) * CATEGORY_RADIUS

  return { x, y }
}

/**
 * Calculate config bubble positions clustered around their category bubbles
 * Uses circular arrangement around each category
 */
function calculatePositions() {
  const configs = [...props.configs]

  if (configs.length === 0) {
    positionedConfigs.value = []
    return
  }

  // Group configs by category
  const configsByCategory = new Map<string, ConfigMetadata[]>()
  configs.forEach(config => {
    const category = config.properties[0] || 'freestyle' // First property is category
    if (!configsByCategory.has(category)) {
      configsByCategory.set(category, [])
    }
    configsByCategory.get(category)!.push(config)
  })

  // Position configs around their category bubbles
  const positioned: ConfigWithPosition[] = []

  configsByCategory.forEach((categoryConfigs, category) => {
    const categoryPos = getCategoryPosition(category)

    // Calculate radius for this cluster based on number of configs
    const numConfigs = categoryConfigs.length
    const clusterRadius = CATEGORY_BUBBLE_SIZE / 2 + BUBBLE_DIAMETER / 2 + BUBBLE_SPACING

    // Arrange configs in circle around category bubble
    const angleStep = (2 * Math.PI) / numConfigs

    categoryConfigs.forEach((config, index) => {
      const angle = index * angleStep
      const x = categoryPos.x + Math.cos(angle) * clusterRadius
      const y = categoryPos.y + Math.sin(angle) * clusterRadius

      // Clamp to canvas bounds
      const clampedX = Math.max(BUBBLE_DIAMETER / 2, Math.min(props.canvasWidth - BUBBLE_DIAMETER / 2, x))
      const clampedY = Math.max(BUBBLE_DIAMETER / 2, Math.min(props.canvasHeight - BUBBLE_DIAMETER / 2, y))

      positioned.push({
        ...config,
        position: { x: clampedX, y: clampedY }
      })
    })
  })

  positionedConfigs.value = positioned
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
