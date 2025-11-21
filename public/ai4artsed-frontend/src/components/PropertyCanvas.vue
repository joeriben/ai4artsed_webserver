<template>
  <div class="property-canvas">
    <div class="cluster-wrapper">
      <PropertyBubble
        v-for="category in categories"
        :key="category"
        :property="category"
        :color="getCategoryColor(category)"
        :is-selected="isPropertySelected(category)"
        :x="categoryPositions[category]?.x ?? 50"
        :y="categoryPositions[category]?.y ?? 50"
        :symbol-data="getSymbolDataForProperty(category)"
        @toggle="handlePropertyToggle"
        @update-position="handleUpdatePosition"
      />

      <!-- Configuration Bubbles - Only visible when category selected -->
      <transition-group
        name="config-fade"
        v-if="selectedCategory && visibleConfigs.length > 0"
      >
        <div
          v-for="(config, index) in visibleConfigs"
          :key="config.id"
          class="config-bubble"
          :style="getConfigStyle(config, index)"
          @click="selectConfiguration(config)"
          @touchstart.prevent="selectConfiguration(config)"
        >
          <div class="config-content">
            <img
              v-if="config.imageUrl"
              :src="config.imageUrl"
              :alt="getConfigName(config)"
              loading="lazy"
            >
            <div v-else class="config-placeholder">
              {{ getConfigName(config).charAt(0) }}
            </div>
          </div>
          <span class="config-label">{{ getConfigName(config) }}</span>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PropertyBubble from './PropertyBubble.vue'
import type { SymbolData } from '@/stores/configSelection'
import { useConfigSelectionStore } from '@/stores/configSelection'
import { useUserPreferencesStore } from '@/stores/userPreferences'

interface Props {
  selectedProperties: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleProperty: [property: string]
  selectConfig: [configId: string]
}>()

// Stores
const store = useConfigSelectionStore()
const userPreferences = useUserPreferencesStore()
const router = useRouter()

// Selected category state
const selectedCategory = ref<string | null>(null)

// Kategorien aus dem Store
const categories = computed(() => store.categories)

// Current language for config names
const currentLanguage = computed(() => userPreferences.language)

// Get all available configs
const allConfigurations = computed(() => store.availableConfigs)

// Filter configs based on selected category
const visibleConfigs = computed(() => {
  if (!selectedCategory.value) return []

  return allConfigurations.value.filter(config => {
    return config.properties && config.properties.includes(selectedCategory.value)
  })
})

// Farben pro Kategorie
const categoryColorMap: Record<string, string> = {
  semantics: '#2196F3',   // 💬
  aesthetics: '#9C27B0',  // 🪄
  arts: '#E91E63',        // 🖌️
  heritage: '#4CAF50',    // 🌍
  freestyle: '#FFC107',   // 🫵
}

// Positionen in Prozent relativ zur cluster-wrapper
type CategoryPosition = { x: number; y: number }
const categoryPositions = ref<Record<string, CategoryPosition>>({})

/**
 * Zentrierte, geräteunabhängige Layout-Berechnung
 * - freestyle im Zentrum (50/50)
 * - übrige Kategorien gleichmäßig auf Kreis (Radius 35%)
 */
function calculateCategoryPositions() {
  const positions: Record<string, CategoryPosition> = {}

  const centerX = 50
  const centerY = 50
  const radiusPercent = 35

  const all = categories.value

  // freestyle in der Mitte, falls vorhanden
  if (all.includes('freestyle')) {
    positions.freestyle = { x: centerX, y: centerY }
  }

  const others = all.filter((c) => c !== 'freestyle')
  if (others.length === 0) {
    categoryPositions.value = positions
    return
  }

  const angleStep = (2 * Math.PI) / others.length

  others.forEach((category, index) => {
    // Start bei -45° für X-Formation
    const angle = index * angleStep - Math.PI / 4

    const x = centerX + Math.cos(angle) * radiusPercent
    const y = centerY + Math.sin(angle) * radiusPercent

    positions[category] = { x, y }
  })

  categoryPositions.value = positions
}

function getCategoryColor(category: string): string {
  return categoryColorMap[category] ?? '#888888'
}

function isPropertySelected(property: string): boolean {
  return props.selectedProperties.includes(property)
}

function handlePropertyToggle(property: string) {
  console.log('[PropertyCanvas] Toggle:', property)
  console.log('[PropertyCanvas] Before - Selected:', props.selectedProperties)

  // Update selected category for config display
  if (selectedCategory.value === property) {
    selectedCategory.value = null
  } else {
    selectedCategory.value = property
  }

  emit('toggleProperty', property)
  console.log('[PropertyCanvas] After - Selected:', props.selectedProperties)
}

function getSymbolDataForProperty(property: string): SymbolData | undefined {
  return store.getSymbolData(property)
}

// Get localized config name
function getConfigName(config: any): string {
  if (typeof config.name === 'string') {
    return config.name
  }
  return config.name[currentLanguage.value] || config.name.en || ''
}

// Calculate config bubble position around its parent category
function getConfigStyle(config: any, index: number) {
  const categoryPos = categoryPositions.value[selectedCategory.value!]
  if (!categoryPos) {
    return { left: '50%', top: '50%' }
  }

  const numConfigs = visibleConfigs.value.length
  // Calculate angle for this config (evenly distributed around circle)
  const angleStep = (2 * Math.PI) / numConfigs
  const angle = index * angleStep - Math.PI / 2 // Start at top (-90°)

  // Calculate distance from category center (20% of container)
  const distance = 20

  // Calculate position using trigonometry
  const x = categoryPos.x + Math.cos(angle) * distance
  const y = categoryPos.y + Math.sin(angle) * distance

  return {
    left: `${x}%`,
    top: `${y}%`
  }
}

// Handle config selection
function selectConfiguration(config: any) {
  emit('selectConfig', config.id)

  // Navigate to pipeline execution
  router.push({
    name: 'pipeline-execution',
    params: { configId: config.id }
  })
}

/**
 * Drag-Update: x,y sind Prozentkoordinaten (0–100)
 * Begrenzung auf Kreisradius (gleiche Logik wie in calculateCategoryPositions)
 */
function handleUpdatePosition(category: string, x: number, y: number) {
  const centerX = 50
  const centerY = 50
  const radiusPercent = 35

  const dx = x - centerX
  const dy = y - centerY
  const dist = Math.sqrt(dx * dx + dy * dy)

  if (dist > radiusPercent) {
    const angle = Math.atan2(dy, dx)
    x = centerX + Math.cos(angle) * radiusPercent
    y = centerY + Math.sin(angle) * radiusPercent
  }

  categoryPositions.value = {
    ...categoryPositions.value,
    [category]: { x, y },
  }
}

// Neu berechnen, wenn Kategorien sich ändern
watch(categories, () => {
  calculateCategoryPositions()
})

// Initial
onMounted(() => {
  calculateCategoryPositions()
})
</script>

<style scoped>
/**
 * Vollflächiges Overlay, das immer am Viewport hängt.
 * Flexbox zentriert die quadratische cluster-wrapper horizontal und vertikal.
 */

.property-canvas {
  position: fixed;
  inset: 0; /* top:0; right:0; bottom:0; left:0 */
  z-index: 10;
  pointer-events: none;

  display: flex;
  align-items: center;
  justify-content: center;

  /* falls nötig: etwas Abstand zu Header/Footern
     padding-top: 3.5rem;
     padding-bottom: 1.5rem;
  */
}

/* Quadrat, das mit min(70vw, 70vh) skaliert */
.cluster-wrapper {
  position: relative;
  width: min(70vw, 70vh);
  aspect-ratio: 1 / 1;

  /* Debug: Deaktiviert für Production */
  /* border: 2px dashed rgba(255, 0, 0, 0.4); */
  /* background: rgba(255, 0, 0, 0.03); */
}

/* Nur die Bubbles selbst sind klick-/draggable */
.property-canvas :deep(.property-bubble) {
  pointer-events: all;
}

/* Configuration Bubbles */
.config-bubble {
  position: absolute;
  width: 18%;
  aspect-ratio: 1 / 1;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  pointer-events: all;
  transition: all 0.3s ease;
}

.config-bubble:hover {
  transform: translate(-50%, -50%) scale(1.1);
  z-index: 10;
}

.config-content {
  width: 80%;
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  overflow: hidden;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  margin-bottom: 0.5rem;
}

.config-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.config-placeholder {
  font-size: 2rem;
  font-weight: bold;
  color: #666;
}

.config-label {
  font-size: 0.9rem;
  color: white;
  font-weight: 500;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  max-width: 90%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Transitions for config bubbles */
.config-fade-enter-active,
.config-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.config-fade-enter-from {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.8);
}

.config-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.8);
}
</style>

