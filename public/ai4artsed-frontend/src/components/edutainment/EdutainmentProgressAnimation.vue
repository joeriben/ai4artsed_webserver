<template>
  <div class="edutainment-animation-wrapper">
    <!-- Original Pixel Animation with GPU Stats -->
    <SpriteProgressAnimation
      :progress="progress"
      :gpu-power="gpuStats.power_draw_watts || simulatedPower"
      :gpu-temp="gpuStats.temperature_celsius || simulatedTemp"
      :total-energy="totalEnergyWh"
      :total-co2="totalCo2Grams"
    />

    <!-- Rising GPU Stats Bubble (optional visual effect) -->
    <AIFactsBubble
      :gpu-stats="gpuStats"
      :total-energy="totalEnergyWh"
      :total-co2="totalCo2Grams"
      :visible="isGenerating"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import SpriteProgressAnimation from '@/components/SpriteProgressAnimation.vue'
import AIFactsBubble from './AIFactsBubble.vue'
import type { GpuRealtimeStats } from '@/composables/useEdutainmentFacts'

const props = defineProps<{
  progress: number
}>()

// State
const gpuStats = ref<GpuRealtimeStats>({ available: false })
const totalEnergyWh = ref(0)
const totalCo2Grams = ref(0)
const elapsedSeconds = ref(0)
const simulatedPower = ref(200)
const simulatedTemp = ref(55)

// Computed
const isGenerating = computed(() => props.progress > 0 && props.progress < 100)

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

  // Use real GPU values if available and under load, otherwise simulate
  const realPower = gpuStats.value.power_draw_watts || 0
  const isGpuActive = realPower > 100

  // Simulation ramps up over time
  simulatedPower.value = Math.min(450, 150 + elapsedSeconds.value * 15 + Math.random() * 50)
  simulatedTemp.value = Math.min(82, 45 + elapsedSeconds.value * 2 + Math.random() * 3)

  const watts = isGpuActive ? realPower : simulatedPower.value
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
</style>
