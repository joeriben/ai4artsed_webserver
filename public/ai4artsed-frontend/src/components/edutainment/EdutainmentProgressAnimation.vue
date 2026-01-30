<template>
  <div class="edutainment-animation-wrapper">
    <!-- Original Pixel Animation -->
    <SpriteProgressAnimation :progress="progress" />

    <!-- Rising GPU Stats Bubble -->
    <AIFactsBubble
      :gpu-stats="gpuStats"
      :total-energy="totalEnergyWh"
      :total-co2="totalCo2Grams"
      :visible="isGenerating"
    />

    <!-- Summary bar at bottom (optional) -->
    <div v-if="showSummary && gpuStats.available" class="gpu-summary-bar">
      <span class="summary-item">
        <span class="summary-emoji">⚡</span>
        <span class="summary-value">{{ Math.round(gpuStats.power_draw_watts || 0) }}W</span>
      </span>
      <span class="summary-item">
        <span class="summary-emoji">🌡️</span>
        <span class="summary-value">{{ gpuStats.temperature_celsius || 0 }}°C</span>
      </span>
      <span class="summary-item">
        <span class="summary-emoji">☁️</span>
        <span class="summary-value">{{ totalCo2Grams.toFixed(1) }}g CO₂</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import SpriteProgressAnimation from '@/components/SpriteProgressAnimation.vue'
import AIFactsBubble from './AIFactsBubble.vue'
import type { GpuRealtimeStats } from '@/composables/useEdutainmentFacts'

const props = defineProps<{
  progress: number
  showSummary?: boolean
}>()

// State
const gpuStats = ref<GpuRealtimeStats>({ available: false })
const totalEnergyWh = ref(0)
const totalCo2Grams = ref(0)
const elapsedSeconds = ref(0)

// Computed
const isGenerating = computed(() => props.progress > 0 && props.progress < 100)
const showSummary = computed(() => props.showSummary !== false)

// Polling intervals
let pollingInterval: number | null = null
let energyInterval: number | null = null

/**
 * Fetch GPU realtime stats
 */
async function fetchGpuStats(): Promise<void> {
  try {
    const response = await fetch('/api/settings/gpu-realtime')
    if (response.ok) {
      gpuStats.value = await response.json()
    }
  } catch (error) {
    console.warn('[Edutainment] GPU fetch failed:', error)
  }
}

/**
 * Update energy calculations
 */
function updateEnergy(): void {
  elapsedSeconds.value++
  const watts = gpuStats.value.power_draw_watts || 0
  const co2PerKwh = gpuStats.value.co2_per_kwh_grams || 400

  // Energy: Watts / 3600 = Wh per second
  const whThisSecond = watts / 3600
  totalEnergyWh.value += whThisSecond

  // CO2: Wh / 1000 * g/kWh
  const co2ThisSecond = (whThisSecond / 1000) * co2PerKwh
  totalCo2Grams.value += co2ThisSecond
}

/**
 * Start polling when generation begins
 */
function startPolling(): void {
  // Reset counters
  totalEnergyWh.value = 0
  totalCo2Grams.value = 0
  elapsedSeconds.value = 0

  // Initial fetch
  fetchGpuStats()

  // Poll GPU stats every 2 seconds
  pollingInterval = window.setInterval(fetchGpuStats, 2000)

  // Update energy every second
  energyInterval = window.setInterval(updateEnergy, 1000)
}

/**
 * Stop polling when generation ends
 */
function stopPolling(): void {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  if (energyInterval) {
    clearInterval(energyInterval)
    energyInterval = null
  }
}

// Watch progress to start/stop polling
watch(() => props.progress, (newProgress, oldProgress) => {
  // Start when generation begins
  if (newProgress > 0 && oldProgress === 0) {
    startPolling()
  }

  // Stop when generation ends
  if ((newProgress >= 100 || newProgress === 0) && pollingInterval !== null) {
    stopPolling()
  }
}, { immediate: true })

// Cleanup
onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.edutainment-animation-wrapper {
  position: relative;
  width: 100%;
}

.gpu-summary-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 8px 0;
  margin-top: -10px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0 0 8px 8px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.summary-emoji {
  font-size: 14px;
}

.summary-value {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #aaa;
}
</style>
