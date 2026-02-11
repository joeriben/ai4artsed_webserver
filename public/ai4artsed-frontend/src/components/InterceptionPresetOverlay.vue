<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="preset-overlay" @click="$emit('close')">
        <div class="preset-container" @click.stop>
          <!-- Header -->
          <div class="preset-header">
            <h2>{{ $t('presetOverlay.title') }}</h2>
            <button class="preset-close" @click="$emit('close')" :title="$t('presetOverlay.close')">×</button>
          </div>

          <!-- Bubble Canvas Area -->
          <div class="preset-canvas">
            <div class="bubble-area">
              <!-- Category Bubbles (PropertyBubble reuse) -->
              <PropertyBubble
                v-for="category in categories"
                :key="category"
                :property="category"
                :color="getCategoryColor(category)"
                :is-selected="selectedCategory === category"
                :x="categoryPositions[category]?.x ?? 50"
                :y="categoryPositions[category]?.y ?? 50"
                :symbol-data="getSymbolData(category)"
                @toggle="handleCategoryToggle"
                @update-position="handleUpdatePosition"
              />

              <!-- Config Bubbles around selected category -->
              <transition-group name="config-fade" v-if="selectedCategory && visibleConfigs.length > 0">
                <div
                  v-for="(config, index) in visibleConfigs"
                  :key="config.id"
                  class="config-bubble"
                  :style="getConfigStyle(config, index)"
                  @click="selectPreset(config)"
                  @touchstart.prevent="selectPreset(config)"
                >
                  <div class="config-content">
                    <div class="preview-image" :style="{ backgroundImage: `url(/config-previews/${config.id}.png)` }"></div>
                    <div class="text-badge">{{ getConfigName(config) }}</div>
                  </div>
                </div>
              </transition-group>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import PropertyBubble from './PropertyBubble.vue'
import { useConfigSelectionStore, type SymbolData } from '@/stores/configSelection'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { usePipelineExecutionStore } from '@/stores/pipelineExecution'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  'preset-selected': [payload: { configId: string; context: string; configName: string }]
}>()

// Stores
const configStore = useConfigSelectionStore()
const userPreferences = useUserPreferencesStore()
const pipelineStore = usePipelineExecutionStore()

const currentLanguage = computed(() => userPreferences.language)

// State
const selectedCategory = ref<string | null>(null)
const isLoadingPreset = ref(false)

// Only show actual interception presets (not modes like HeartMuLa, Latent Lab, etc.)
const PRESET_PIPELINES = new Set(['text_transformation', 'text_transformation_recursive'])
const EXCLUDED_IDS = new Set(['tonejs_composer'])

// Data from store — filtered to interception presets only
const presetConfigs = computed(() =>
  configStore.availableConfigs.filter(config =>
    PRESET_PIPELINES.has(config.pipeline) && !EXCLUDED_IDS.has(config.id)
  )
)

// Categories that actually have presets after filtering
const categories = computed(() => {
  const cats = new Set<string>()
  presetConfigs.value.forEach(config => {
    config.properties?.forEach(p => cats.add(p))
  })
  return Array.from(cats)
})

// Filter configs for selected category
const visibleConfigs = computed(() => {
  if (!selectedCategory.value) return []
  return presetConfigs.value.filter(config =>
    config.properties?.includes(selectedCategory.value!)
  )
})

// Category color map (same as PropertyCanvas)
const categoryColorMap: Record<string, string> = {
  semantics: '#2196F3',
  aesthetics: '#9C27B0',
  arts: '#E91E63',
  critical_analysis: '#4CAF50',
  research: '#00BCD4',
  attitudes: '#FF6F00',
  freestyle: '#FFC107',
  technical_imaging: '#607D8B',
}

// Category positions (percentage-based circle layout)
type CategoryPosition = { x: number; y: number }
const categoryPositions = ref<Record<string, CategoryPosition>>({})

function calculateCategoryPositions() {
  const positions: Record<string, CategoryPosition> = {}
  const centerX = 50
  const centerY = 50
  const radiusPercent = 35
  const all = categories.value

  if (all.includes('freestyle')) {
    positions.freestyle = { x: centerX, y: centerY }
  }

  const others = all.filter(c => c !== 'freestyle')
  if (others.length === 0) {
    categoryPositions.value = positions
    return
  }

  const angleStep = (2 * Math.PI) / others.length
  others.forEach((category, index) => {
    const angle = index * angleStep - Math.PI / 4
    positions[category] = {
      x: centerX + Math.cos(angle) * radiusPercent,
      y: centerY + Math.sin(angle) * radiusPercent,
    }
  })

  categoryPositions.value = positions
}

function getCategoryColor(category: string): string {
  return categoryColorMap[category] ?? '#888888'
}

function getSymbolData(property: string): SymbolData | undefined {
  return configStore.getSymbolData(property)
}

function getConfigName(config: any): string {
  if (typeof config.name === 'string') return config.name
  return config.name[currentLanguage.value] || config.name.en || ''
}

function getConfigStyle(config: any, index: number) {
  const categoryPos = categoryPositions.value[selectedCategory.value!]
  if (!categoryPos) return { left: '50%', top: '50%' }

  const numConfigs = visibleConfigs.value.length
  const angleStep = (2 * Math.PI) / numConfigs
  const angle = index * angleStep - Math.PI / 2
  const distance = 14

  return {
    left: `${categoryPos.x + Math.cos(angle) * distance}%`,
    top: `${categoryPos.y + Math.sin(angle) * distance}%`,
  }
}

function handleCategoryToggle(property: string) {
  selectedCategory.value = selectedCategory.value === property ? null : property
}

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

async function selectPreset(config: any) {
  if (isLoadingPreset.value) return
  isLoadingPreset.value = true

  try {
    // Load config and its context via the pipeline store
    await pipelineStore.setConfig(config.id)
    await pipelineStore.loadMetaPromptForLanguage(currentLanguage.value)

    const context = pipelineStore.metaPrompt || ''
    const configName = getConfigName(config)

    emit('preset-selected', { configId: config.id, context, configName })
    emit('close')
  } catch (error) {
    console.error('[PresetOverlay] Error loading preset:', error)
  } finally {
    isLoadingPreset.value = false
  }
}

// Load configs when overlay becomes visible
watch(() => props.visible, async (isVisible) => {
  if (isVisible && categories.value.length === 0) {
    await configStore.loadConfigs()
  }
  if (isVisible) {
    calculateCategoryPositions()
  }
  if (!isVisible) {
    selectedCategory.value = null
  }
})

// Recalculate when categories change
watch(categories, () => calculateCategoryPositions())
</script>

<style scoped>
.preset-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.preset-container {
  width: calc(100vw - 2rem);
  height: calc(100vh - 2rem);
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preset-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.preset-header h2 {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.preset-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  line-height: 1;
  transition: color 0.2s;
}

.preset-close:hover {
  color: white;
}

/* Canvas area for bubbles */
.preset-canvas {
  flex: 1;
  padding: 1rem;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bubble-area {
  position: relative;
  /* Explicit square: both dimensions set to the SAME value (smaller of w/h) */
  --square-size: min(calc(100vw - 4rem), calc(100vh - 8rem));
  width: var(--square-size);
  height: var(--square-size);
}

/* PropertyBubble needs pointer-events within overlay */
.bubble-area :deep(.property-bubble) {
  pointer-events: all;
}

/* Config bubbles: calc(--square-size * 0.145) für width UND height = Kreis */
.config-bubble {
  position: absolute;
  width: calc(var(--square-size) * 0.145);
  height: calc(var(--square-size) * 0.145);
  border-radius: 50%;
  overflow: hidden;
  transform: translate(-50%, -50%);
  cursor: pointer;
  pointer-events: all;
  transition: all 0.3s ease;
  font-size: calc(var(--square-size) * 0.02);
}

.config-bubble:hover {
  transform: translate(-50%, -50%) scale(1.1);
  z-index: 10;
}

.config-content {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}


.preview-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #f0f0f0;
}

/* Schwarze Bande: volle Breite, Kreis-overflow clippt die Ecken */
.text-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 0.9em;
  font-weight: 600;
  text-align: center;
  padding: 0.3em 15% 0.6em;
  line-height: 1.3;
  word-break: break-word;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Transitions */
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

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
