<template>
  <div class="medium-selection">
    <div class="selection-label">
      {{ $t('selectMedium', 'Wähle ein Medium') }}
    </div>

    <div class="bubbles-container">
      <div
        v-for="(config, index) in interceptionConfigs"
        :key="config.id"
        class="config-bubble"
        :class="{ 'is-selected': selectedConfigId === config.id }"
        :style="getConfigStyle(index)"
        @click="selectConfig(config)"
      >
        <div class="bubble-content">
          <!-- Preview image background -->
          <div
            class="preview-image"
            :style="{ backgroundImage: `url(${getConfigImageUrl(config)})` }"
          ></div>

          <!-- Text badge overlay -->
          <div class="text-badge">
            {{ getConfigName(config) }}
          </div>

          <!-- Selection indicator -->
          <div v-if="selectedConfigId === config.id" class="selected-indicator">
            ✓
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useConfigSelectionStore } from '@/stores/configSelection'
import { useUserPreferencesStore } from '@/stores/userPreferences'

interface Props {
  selectedConfigId?: string | null
  centerX?: number // percentage
  centerY?: number // percentage
  radius?: number  // percentage
}

const props = withDefaults(defineProps<Props>(), {
  selectedConfigId: null,
  centerX: 50,
  centerY: 50,
  radius: 20
})

const emit = defineEmits<{
  'select': [config: any]
}>()

const store = useConfigSelectionStore()
const userPreferences = useUserPreferencesStore()

const currentLanguage = computed(() => userPreferences.language)

// Get all interception configs (stage: "interception")
const interceptionConfigs = computed(() => {
  return store.availableConfigs.filter(config => {
    return config.meta?.stage === 'interception'
  })
})

// Get localized config name
function getConfigName(config: any): string {
  if (typeof config.name === 'string') {
    return config.name
  }
  return config.name[currentLanguage.value] || config.name.en || ''
}

// Get config image URL
function getConfigImageUrl(config: any): string {
  return `/config-previews/${config.id}.png`
}

// Calculate bubble position in circular arrangement
function getConfigStyle(index: number) {
  const numConfigs = interceptionConfigs.value.length
  const angleStep = (2 * Math.PI) / numConfigs
  const angle = index * angleStep - Math.PI / 2 // Start at top (-90°)

  const x = props.centerX + Math.cos(angle) * props.radius
  const y = props.centerY + Math.sin(angle) * props.radius

  return {
    left: `${x}%`,
    top: `${y}%`
  }
}

function selectConfig(config: any) {
  emit('select', config)
}
</script>

<style scoped>
.medium-selection {
  position: relative;
  width: 100%;
  height: 100%;
}

.selection-label {
  position: absolute;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  font-size: clamp(1rem, 2vw, 1.5rem);
  font-weight: 600;
  color: #333;
  text-align: center;
  z-index: 5;
}

.bubbles-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.config-bubble {
  position: absolute;
  width: 18%;
  aspect-ratio: 1 / 1;
  min-height: 0;
  border-radius: 50%;
  overflow: hidden;
  transform: translate(-50%, -50%);
  cursor: pointer;
  transition: all 0.3s ease;
  pointer-events: all;
  font-size: clamp(0.5rem, 1.2vw + 0.3vh, 1.2rem);
}

.config-bubble:hover {
  transform: translate(-50%, -50%) scale(1.1);
  z-index: 10;
}

.config-bubble.is-selected {
  transform: translate(-50%, -50%) scale(1.15);
  z-index: 15;
}

.bubble-content {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.config-bubble.is-selected .bubble-content {
  box-shadow: 0 6px 30px rgba(33, 150, 243, 0.5);
  border: 3px solid #2196F3;
}


/* Preview image background */
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
  padding: 0.3em 0.8em 0.5em;
  line-height: 1.3;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Selection indicator */
.selected-indicator {
  position: absolute;
  top: 10%;
  right: 10%;
  width: 2em;
  height: 2em;
  background: #2196F3;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2em;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  animation: pop-in 0.3s ease;
}

@keyframes pop-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style>
