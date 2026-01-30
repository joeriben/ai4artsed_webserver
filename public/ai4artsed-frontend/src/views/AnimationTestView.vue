<template>
  <div class="animation-test-page">
    <h1>Animation Test - GPU Visualisierungen</h1>

    <!-- Controls -->
    <div class="controls">
      <div class="control-group">
        <label>Progress: {{ progress }}%</label>
        <input type="range" v-model.number="progress" min="0" max="100" />
      </div>

      <div class="control-group">
        <button @click="simulateGeneration" :disabled="isSimulating">
          {{ isSimulating ? 'Läuft...' : 'Generation simulieren' }}
        </button>
        <button @click="resetSimulation">Reset</button>
        <button @click="fetchRealGpuData">GPU-Daten abrufen</button>
      </div>

      <div class="gpu-status" v-if="gpuStats.available">
        <span class="status-ok">✓ GPU: {{ gpuStats.gpu_name }}</span>
      </div>
      <div class="gpu-status" v-else>
        <span class="status-warning">⚠ GPU nicht verfügbar (Simulation)</span>
      </div>
    </div>

    <!-- Animation selection -->
    <div class="animation-tabs">
      <button
        v-for="anim in animations"
        :key="anim.id"
        :class="['tab', { active: selectedAnimation === anim.id }]"
        @click="selectedAnimation = anim.id"
      >
        {{ anim.name }}
      </button>
    </div>

    <!-- Animation display -->
    <div class="animation-container">
      <!-- 1. Original Pixel Animation + Bubbles -->
      <div v-if="selectedAnimation === 'pixel'" class="animation-wrapper">
        <EdutainmentProgressAnimation
          :progress="progress"
          :show-summary="true"
        />
      </div>

      <!-- 2. Environment Animation -->
      <div v-if="selectedAnimation === 'environment'" class="animation-wrapper">
        <EnvironmentAnimation
          :progress="progress"
          :power-watts="gpuStats.power_draw_watts || simulatedPower"
          :temperature="gpuStats.temperature_celsius || simulatedTemp"
          :co2-grams="totalCo2"
          :power-limit="gpuStats.power_limit_watts || 600"
        />
      </div>

      <!-- 3. Retro Cockpit Animation -->
      <div v-if="selectedAnimation === 'cockpit'" class="animation-wrapper">
        <RetroCockpitAnimation
          :progress="progress"
          :power-watts="gpuStats.power_draw_watts || simulatedPower"
          :power-limit="gpuStats.power_limit_watts || 600"
          :temperature="gpuStats.temperature_celsius || simulatedTemp"
          :utilization="gpuStats.utilization_percent || simulatedUtil"
          :vram-used-mb="gpuStats.memory_used_mb || 24000"
          :vram-total-mb="gpuStats.memory_total_mb || 48000"
          :co2-grams="totalCo2"
          :energy-wh="totalEnergy"
          :elapsed-seconds="elapsedSeconds"
          :gpu-name="gpuStats.gpu_name || 'Simulated GPU'"
        />
      </div>

      <!-- 4. Klima-Eisberg Animation -->
      <div v-if="selectedAnimation === 'iceberg'" class="animation-wrapper">
        <IcebergAnimation
          :progress="progress"
        />
      </div>
    </div>

    <!-- Live stats (hidden for iceberg which has its own) -->
    <div v-if="selectedAnimation !== 'iceberg'" class="live-stats">
      <div class="stat-card">
        <div class="stat-label">Power</div>
        <div class="stat-value">{{ Math.round(gpuStats.power_draw_watts || simulatedPower) }}W</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Temp</div>
        <div class="stat-value">{{ gpuStats.temperature_celsius || simulatedTemp }}°C</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">VRAM</div>
        <div class="stat-value">{{ gpuStats.memory_used_percent || 50 }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">CO₂</div>
        <div class="stat-value">{{ totalCo2.toFixed(2) }}g</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Energy</div>
        <div class="stat-value">{{ (totalEnergy / 1000).toFixed(4) }}kWh</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Zeit</div>
        <div class="stat-value">{{ elapsedSeconds }}s</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import EdutainmentProgressAnimation from '@/components/edutainment/EdutainmentProgressAnimation.vue'
import EnvironmentAnimation from '@/components/edutainment/EnvironmentAnimation.vue'
import RetroCockpitAnimation from '@/components/edutainment/RetroCockpitAnimation.vue'
import IcebergAnimation from '@/components/edutainment/IcebergAnimation.vue'
import type { GpuRealtimeStats } from '@/composables/useEdutainmentFacts'

// Animation selection
const animations = [
  { id: 'pixel', name: '1. Pixel + Bubbles' },
  { id: 'environment', name: '2. Umwelt-Landschaft' },
  { id: 'cockpit', name: '3. Retro Cockpit' },
  { id: 'iceberg', name: '4. Klima-Eisberg' }
]
const selectedAnimation = ref('pixel')

// State
const progress = ref(0)
const gpuStats = ref<GpuRealtimeStats>({ available: false })
const isSimulating = ref(false)
const elapsedSeconds = ref(0)
const totalEnergy = ref(0) // Wh
const totalCo2 = ref(0) // grams

// Simulated values (when real GPU not available)
const simulatedPower = ref(250)
const simulatedTemp = ref(55)
const simulatedUtil = ref(80)

// Intervals
let simulationInterval: number | null = null
let gpuPollInterval: number | null = null
let energyInterval: number | null = null

// Fetch real GPU data
async function fetchRealGpuData() {
  try {
    const response = await fetch('/api/settings/gpu-realtime')
    if (response.ok) {
      gpuStats.value = await response.json()
      console.log('[AnimationTest] GPU Stats:', gpuStats.value)
    }
  } catch (error) {
    console.warn('[AnimationTest] GPU fetch failed:', error)
  }
}

// Simulate generation
function simulateGeneration() {
  if (isSimulating.value) return

  isSimulating.value = true
  progress.value = 0
  elapsedSeconds.value = 0
  totalEnergy.value = 0
  totalCo2.value = 0

  // Start GPU polling
  fetchRealGpuData()
  gpuPollInterval = window.setInterval(fetchRealGpuData, 2000)

  // Progress simulation (30 seconds total)
  simulationInterval = window.setInterval(() => {
    progress.value += 100 / 30 // 30 seconds
    elapsedSeconds.value++

    // Update simulated values with some variation
    simulatedPower.value = 200 + Math.random() * 150
    simulatedTemp.value = Math.min(85, simulatedTemp.value + Math.random() * 0.5)
    simulatedUtil.value = 70 + Math.random() * 25

    // Calculate energy and CO2
    const watts = gpuStats.value.power_draw_watts || simulatedPower.value
    const co2PerKwh = gpuStats.value.co2_per_kwh_grams || 400
    const whThisSecond = watts / 3600
    totalEnergy.value += whThisSecond
    totalCo2.value += (whThisSecond / 1000) * co2PerKwh

    if (progress.value >= 100) {
      stopSimulation()
    }
  }, 1000)
}

function stopSimulation() {
  isSimulating.value = false
  progress.value = 100

  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
  if (gpuPollInterval) {
    clearInterval(gpuPollInterval)
    gpuPollInterval = null
  }
}

function resetSimulation() {
  stopSimulation()
  progress.value = 0
  elapsedSeconds.value = 0
  totalEnergy.value = 0
  totalCo2.value = 0
  simulatedTemp.value = 55
}

onMounted(() => {
  fetchRealGpuData()
})

onUnmounted(() => {
  stopSimulation()
})
</script>

<style scoped>
.animation-test-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  padding: 20px;
  font-family: system-ui, sans-serif;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  color: #4facfe;
}

/* Controls */
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-group label {
  min-width: 120px;
}

.control-group input[type="range"] {
  width: 200px;
}

.control-group button {
  padding: 8px 16px;
  background: #4facfe;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}

.control-group button:hover:not(:disabled) {
  background: #3a8fd9;
}

.control-group button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.gpu-status {
  font-size: 14px;
}

.status-ok {
  color: #4CAF50;
}

.status-warning {
  color: #FFC107;
}

/* Tabs */
.animation-tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.tab {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tab.active {
  background: #4facfe;
  border-color: #4facfe;
}

/* Animation container */
.animation-container {
  max-width: 700px;
  margin: 0 auto 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.animation-wrapper {
  min-height: 320px;
}

/* Live stats */
.live-stats {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 15px;
  max-width: 700px;
  margin: 0 auto;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px 20px;
  text-align: center;
  min-width: 100px;
}

.stat-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #4facfe;
  font-family: 'Courier New', monospace;
}
</style>
