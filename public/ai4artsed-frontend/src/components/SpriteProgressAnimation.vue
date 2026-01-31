<template>
  <div class="progress-animation-container">
    <div class="token-processing-scene">
      <!-- GPU Stats Bar (like Iceberg, but terminal-styled) -->
      <div class="stats-bar">
        <div class="stat">
          <span class="stat-label">{{ t('edutainment.pixel.grafikkarte') }}</span>
          <span class="stat-value">{{ Math.round(gpuPower) }}W / {{ Math.round(gpuTemp) }}°C<span class="cursor">_</span></span>
        </div>
        <div class="stat">
          <span class="stat-label">{{ t('edutainment.pixel.energieverbrauch') }}</span>
          <span class="stat-value">{{ (totalEnergy / 1000).toFixed(4) }}kWh</span>
        </div>
        <div class="stat">
          <span class="stat-label">{{ t('edutainment.pixel.co2Menge') }}</span>
          <span class="stat-value">{{ totalCo2.toFixed(1) }}g</span>
        </div>
        <div v-if="estimatedSeconds" class="stat">
          <span class="stat-label">~</span>
          <span class="stat-value">{{ estimatedSeconds }}s</span>
        </div>
      </div>

      <!-- Summary overlay (bottom, styled box, appears after 5s) -->
      <Transition name="fade">
        <div v-if="isShowingSummary" class="summary-box">
          <div class="summary-comparison">
            {{ t('edutainment.pixel.smartphoneComparison', { minutes: smartphoneMinutes }) }}
          </div>
        </div>
      </Transition>

      <!-- Input Grid (Left) -->
      <div class="input-grid-container">
        <div class="canvas-grid">
          <div
            v-for="(pixel, index) in inputPixels"
            :key="'input-' + index"
            class="pixel-token"
            :class="{ hidden: index < processedCount }"
            :style="getInputPixelStyle(pixel, index)"
          ></div>
        </div>
      </div>

      <!-- Processor Box (Center) -->
      <div class="processor-box" :class="{ active: isProcessing }">
        <div class="processor-glow"></div>
        <div class="processor-core">
          <!-- Neural network nodes -->
          <div class="neural-network">
            <div class="network-node node-1"></div>
            <div class="network-node node-2"></div>
            <div class="network-node node-3"></div>
            <div class="network-node node-4"></div>
            <div class="network-node node-5"></div>
            <div class="network-connection conn-1"></div>
            <div class="network-connection conn-2"></div>
            <div class="network-connection conn-3"></div>
            <div class="network-connection conn-4"></div>
          </div>
          <div class="processor-icon">⚡</div>
        </div>
      </div>

      <!-- Output Grid (Right) -->
      <div class="output-grid-container">
        <div class="canvas-grid">
          <div
            v-for="(pixel, index) in outputPixels"
            :key="'output-' + index"
            class="pixel-token"
            :class="{
              visible: index < processedCount,
              flying: index === processedCount - 1 && isProcessing
            }"
            :style="getOutputPixelStyle(pixel, index)"
          ></div>
        </div>
      </div>

      <!-- Progress Bar at Bottom -->
      <div class="progress-bar-container">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" :style="{ width: progress + '%' }">
            <div class="progress-shine"></div>
          </div>
        </div>
        <div class="progress-text">{{ Math.round(progress) }}%</div>
      </div>

          </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  progress: number // 0-100 (internal progress from composable)
  estimatedSeconds?: number // From output config
  gpuPower?: number // Watts
  gpuTemp?: number // Celsius
  totalEnergy?: number // Wh
  totalCo2?: number // grams
  isShowingSummary?: boolean // True during 5s summary pause
  smartphoneMinutes?: number // Pre-computed from composable
}>()

// Default values for GPU stats
const gpuPower = computed(() => props.gpuPower ?? 0)
const gpuTemp = computed(() => props.gpuTemp ?? 0)
const totalEnergy = computed(() => props.totalEnergy ?? 0)
const totalCo2 = computed(() => props.totalCo2 ?? 0)

// Use prop if provided, otherwise compute locally (fallback for standalone use)
const smartphoneMinutes = computed(() => {
  if (props.smartphoneMinutes !== undefined) return props.smartphoneMinutes
  return Math.round(totalCo2.value * 30)
})

const totalTokens = 196 // 14x14 grid
// Animation completes at 90%, so scale progress accordingly
const processedCount = computed(() => {
  // At 90% progress, all tokens should be processed
  const scaledProgress = Math.min(props.progress / 90, 1)
  return Math.floor(scaledProgress * totalTokens)
})
const isProcessing = computed(() => props.progress > 0 && props.progress < 100)

// Runtime counter
const elapsedSeconds = ref(0)
let timerInterval: number | null = null

const tokenColors = [
  '#3498db', // blue
  '#9b59b6', // purple
  '#e74c3c', // red
  '#2ecc71', // green
  '#f39c12', // orange
  '#1abc9c', // turquoise
  '#e91e63', // pink
]

// Pre-computed pixel styles cache (avoids creating 196 objects per render)
const inputPixelStyleCache = new Map<string, Record<string, string>>()
const outputPixelStyleCache = new Map<string, Record<string, string | number>>()

// Image templates - 14x14 grid
// 0 = empty, 1-7 = color index
const imageTemplates = {
  robot: {
    pattern: [
      [0,0,0,6,6,0,0,0,0,6,6,0,0,0],
      [0,0,0,6,6,0,0,0,0,6,6,0,0,0],
      [0,0,6,6,6,6,6,6,6,6,6,6,0,0],
      [0,0,6,0,0,6,6,6,6,0,0,6,0,0],
      [0,0,6,0,0,6,6,6,6,0,0,6,0,0],
      [0,0,6,6,6,7,6,6,7,6,6,6,0,0],
      [0,0,6,6,6,6,3,3,6,6,6,6,0,0],
      [0,0,0,6,6,6,6,6,6,6,6,0,0,0],
      [0,0,6,6,6,6,6,6,6,6,6,6,0,0],
      [0,6,6,6,1,1,6,6,1,1,6,6,6,0],
      [0,6,6,6,1,1,6,6,1,1,6,6,6,0],
      [0,0,6,6,6,6,6,6,6,6,6,6,0,0],
      [0,0,3,3,3,0,0,0,0,3,3,3,0,0],
      [0,0,3,3,3,0,0,0,0,3,3,3,0,0],
    ]
  },
  flower: {
    pattern: [
      [0,0,0,7,7,0,0,0,0,7,7,0,0,0],
      [0,0,7,7,7,7,0,0,7,7,7,7,0,0],
      [0,7,7,7,7,7,7,7,7,7,7,7,7,0],
      [0,7,7,7,7,7,7,7,7,7,7,7,7,0],
      [0,0,7,7,7,5,5,5,5,7,7,7,0,0],
      [0,0,0,7,5,5,5,5,5,5,7,0,0,0],
      [0,0,0,7,5,5,0,0,5,5,7,0,0,0],
      [0,0,0,7,5,5,3,3,5,5,7,0,0,0],
      [0,0,0,7,5,5,5,5,5,5,7,0,0,0],
      [0,0,0,0,7,4,4,4,4,7,0,0,0,0],
      [0,0,0,0,4,4,4,4,4,4,0,0,0,0],
      [0,0,0,0,0,4,4,4,4,0,0,0,0,0],
      [0,0,0,0,0,0,4,4,0,0,0,0,0,0],
      [0,0,0,0,0,0,4,4,0,0,0,0,0,0],
    ]
  },
  football: {
    pattern: [
      [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,1,1,0,0,1,1,0,0,1,1,0,0],
      [0,1,1,0,0,0,1,1,0,0,0,1,1,0],
      [0,1,1,0,0,1,1,1,1,0,0,1,1,0],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,0,0,1,1,1,1,1,1],
      [1,1,1,1,1,1,0,0,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [0,1,1,0,0,1,1,1,1,0,0,1,1,0],
      [0,1,1,0,0,0,1,1,0,0,0,1,1,0],
      [0,0,1,1,0,0,1,1,0,0,1,1,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
    ]
  },
  heart: {
    pattern: [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,3,3,3,0,0,0,3,3,3,0,0,0],
      [0,3,3,7,3,3,0,3,3,7,3,3,0,0],
      [0,3,7,7,7,3,3,3,7,7,7,3,0,0],
      [0,3,7,7,7,7,3,7,7,7,7,3,0,0],
      [0,3,7,7,7,7,7,7,7,7,7,3,0,0],
      [0,0,3,7,7,7,7,7,7,7,3,0,0,0],
      [0,0,0,3,7,7,7,7,7,3,0,0,0,0],
      [0,0,0,0,3,7,7,7,3,0,0,0,0,0],
      [0,0,0,0,0,3,7,3,0,0,0,0,0,0],
      [0,0,0,0,0,0,3,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  star: {
    pattern: [
      [0,0,0,0,0,0,5,5,0,0,0,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,5,5,5,5,5,5,0,0,0,0],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [0,5,5,5,5,5,5,5,5,5,5,5,5,0],
      [0,0,5,5,5,5,5,5,5,5,5,5,0,0],
      [0,0,5,5,5,5,0,0,5,5,5,5,0,0],
      [0,0,0,5,5,5,0,0,5,5,5,0,0,0],
      [0,0,5,5,5,0,0,0,0,5,5,5,0,0],
      [0,5,5,5,0,0,0,0,0,0,5,5,5,0],
      [5,5,5,0,0,0,0,0,0,0,0,5,5,5],
      [5,5,0,0,0,0,0,0,0,0,0,0,5,5],
    ]
  },
  house: {
    pattern: [
      [0,0,0,0,0,0,3,3,0,0,0,0,0,0],
      [0,0,0,0,0,3,3,3,3,0,0,0,0,0],
      [0,0,0,0,3,3,3,3,3,3,0,0,0,0],
      [0,0,0,3,3,5,5,5,5,3,3,0,0,0],
      [0,0,3,3,5,5,5,5,5,5,3,3,0,0],
      [0,0,7,7,7,7,7,7,7,7,7,7,0,0],
      [0,0,7,7,1,1,7,7,1,1,7,7,0,0],
      [0,0,7,7,1,1,7,7,1,1,7,7,0,0],
      [0,0,7,7,7,7,7,7,7,7,7,7,0,0],
      [0,0,7,7,7,7,0,0,7,7,7,7,0,0],
      [0,0,7,7,7,7,0,0,7,7,7,7,0,0],
      [0,0,7,7,2,2,2,2,7,7,7,7,0,0],
      [0,0,7,7,2,2,2,2,7,7,7,7,0,0],
      [0,0,7,7,2,2,2,2,7,7,7,7,0,0],
    ]
  },
  tree: {
    pattern: [
      [0,0,0,0,4,4,4,4,4,4,0,0,0,0],
      [0,0,0,4,4,4,4,4,4,4,4,0,0,0],
      [0,0,4,4,4,4,4,4,4,4,4,4,0,0],
      [0,4,4,4,4,4,4,4,4,4,4,4,4,0],
      [0,4,4,4,4,4,4,4,4,4,4,4,4,0],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [0,4,4,4,4,4,4,4,4,4,4,4,4,0],
      [0,4,4,4,4,4,4,4,4,4,4,4,4,0],
      [0,0,4,4,4,4,4,4,4,4,4,4,0,0],
      [0,0,0,4,4,4,4,4,4,4,4,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,0,0,5,5,0,0,0,0,0,0],
    ]
  },
  moon: {
    pattern: [
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,6,6,6,6,6,1,1,1,1,1,1],
      [1,1,6,6,6,6,6,6,6,1,1,1,1,1],
      [1,6,6,6,6,6,6,6,6,6,1,1,1,1],
      [1,6,6,6,6,6,6,6,6,6,1,1,1,1],
      [1,6,6,6,6,6,6,6,6,1,1,1,1,1],
      [1,6,6,6,6,6,6,6,1,1,1,1,1,1],
      [1,1,6,6,6,6,6,1,1,1,1,1,1,1],
      [1,1,1,6,6,6,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
  },
  cat: {
    pattern: [
      [0,0,5,5,0,0,0,0,0,0,5,5,0,0],
      [0,5,5,5,5,0,0,0,0,5,5,5,5,0],
      [0,5,5,5,5,0,0,0,0,5,5,5,5,0],
      [0,0,5,5,5,5,5,5,5,5,5,5,0,0],
      [0,0,5,5,5,5,5,5,5,5,5,5,0,0],
      [0,0,5,0,0,5,5,5,5,0,0,5,0,0],
      [0,0,5,0,0,5,5,5,5,0,0,5,0,0],
      [0,0,5,5,5,7,5,5,7,5,5,5,0,0],
      [0,0,5,5,5,5,5,5,5,5,5,5,0,0],
      [0,0,5,5,3,3,3,3,3,3,5,5,0,0],
      [0,0,5,5,5,3,3,3,3,5,5,5,0,0],
      [0,0,0,5,5,5,5,5,5,5,5,0,0,0],
      [0,0,0,0,5,5,5,5,5,5,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  music: {
    pattern: [
      [0,0,0,0,0,0,0,0,0,2,2,0,0,0],
      [0,0,0,0,0,0,0,0,0,2,2,0,0,0],
      [0,0,0,0,0,0,0,0,0,2,2,0,0,0],
      [0,0,0,0,0,0,0,0,0,2,2,0,0,0],
      [0,7,7,0,0,0,0,0,0,2,2,0,0,0],
      [7,7,7,7,0,0,0,0,0,2,2,0,0,0],
      [7,7,7,7,7,0,0,0,0,2,2,0,0,0],
      [7,7,7,7,7,7,0,0,7,2,2,7,0,0],
      [0,7,7,7,7,7,7,7,7,7,7,7,7,0],
      [0,0,7,7,7,7,7,7,7,7,7,7,7,0],
      [0,0,0,7,7,7,7,7,7,7,7,7,0,0],
      [0,0,0,0,7,7,7,7,0,7,7,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  computer: {
    pattern: [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,2,6,6,6,6,6,6,6,6,2,0,0],
      [0,0,2,6,6,6,6,6,6,6,6,2,0,0],
      [0,0,2,6,6,3,6,6,3,6,6,2,0,0],
      [0,0,2,6,6,6,6,6,6,6,6,2,0,0],
      [0,0,2,6,6,6,3,3,6,6,6,2,0,0],
      [0,0,2,6,6,6,6,6,6,6,6,2,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,0,0,0,2,2,2,2,0,0,0,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,2,1,1,1,1,1,1,1,1,2,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  palette: {
    pattern: [
      [0,0,0,5,5,5,5,5,5,5,5,0,0,0],
      [0,0,5,5,3,5,5,5,5,1,5,5,0,0],
      [0,5,5,3,3,3,5,5,1,1,1,5,5,0],
      [0,5,5,3,3,3,5,5,1,1,1,5,5,0],
      [5,5,5,5,3,5,5,5,5,1,5,5,5,5],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [5,7,7,7,5,5,5,5,5,5,2,2,5,5],
      [5,7,7,7,5,5,5,5,5,2,2,2,2,5],
      [5,5,7,5,5,5,5,5,5,5,2,2,5,5],
      [0,5,5,4,4,4,5,5,6,6,5,5,0,0],
      [0,5,5,4,4,4,5,6,6,6,6,5,5,0],
      [0,0,5,5,4,5,5,5,6,6,5,5,0,0],
      [0,0,0,5,5,5,5,5,5,5,5,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  smiley: {
    pattern: [
      [0,0,0,5,5,5,5,5,5,5,5,0,0,0],
      [0,0,5,5,5,5,5,5,5,5,5,5,0,0],
      [0,5,5,5,5,5,5,5,5,5,5,5,5,0],
      [0,5,5,0,0,5,5,5,5,0,0,5,5,0],
      [5,5,5,0,0,5,5,5,5,0,0,5,5,5],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [5,5,0,5,5,5,5,5,5,5,5,0,5,5],
      [5,5,5,0,0,0,0,0,0,0,0,5,5,5],
      [0,5,5,5,0,0,0,0,0,0,5,5,5,0],
      [0,5,5,5,5,5,5,5,5,5,5,5,5,0],
      [0,0,5,5,5,5,5,5,5,5,5,5,0,0],
      [0,0,0,5,5,5,5,5,5,5,5,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  rainbow: {
    pattern: [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,3,3,3,3,3,3,3,3,0,0,0],
      [0,0,3,3,5,5,5,5,5,5,3,3,0,0],
      [0,3,3,5,5,5,5,5,5,5,5,3,3,0],
      [0,3,5,5,5,4,4,4,4,5,5,5,3,0],
      [3,3,5,5,4,4,4,4,4,4,5,5,3,3],
      [3,5,5,4,4,4,1,1,4,4,4,5,5,3],
      [3,5,4,4,4,1,1,1,1,4,4,4,5,3],
      [3,5,4,4,1,1,1,1,1,1,4,4,5,3],
      [3,5,4,4,1,1,0,0,1,1,4,4,5,3],
      [0,3,4,4,1,1,0,0,1,1,4,4,3,0],
      [0,0,3,4,4,1,0,0,1,4,4,3,0,0],
      [0,0,0,3,4,4,0,0,4,4,3,0,0,0],
      [0,0,0,0,3,3,0,0,3,3,0,0,0,0],
    ]
  },
  icecream: {
    pattern: [
      [0,0,0,0,7,7,7,7,7,7,0,0,0,0],
      [0,0,0,7,7,7,7,7,7,7,7,0,0,0],
      [0,0,7,7,7,7,7,7,7,7,7,7,0,0],
      [0,0,7,7,7,0,0,0,0,7,7,7,0,0],
      [0,0,7,7,7,7,7,7,7,7,7,7,0,0],
      [0,0,7,7,7,7,7,7,7,7,7,7,0,0],
      [0,0,0,7,7,7,7,7,7,7,7,0,0,0],
      [0,0,0,0,7,7,7,7,7,7,0,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,0,5,5,5,5,0,0,0,0,0],
      [0,0,0,0,0,0,5,5,0,0,0,0,0,0],
      [0,0,0,0,0,0,5,5,0,0,0,0,0,0],
      [0,0,0,0,0,0,5,5,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  camera: {
    pattern: [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,3,3,3,3,3,3,0,0,0,0],
      [0,0,0,3,3,3,3,3,3,3,3,0,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,2,2,6,6,6,6,6,6,2,2,0,0],
      [0,0,2,2,6,1,1,1,1,6,2,2,0,0],
      [0,0,2,2,6,1,1,1,1,6,2,2,0,0],
      [0,0,2,2,6,6,6,6,6,6,2,2,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,2,2,2,2,2,2,2,2,2,2,0,0],
      [0,0,0,2,2,2,2,2,2,2,2,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
  },
  sun: {
    pattern: [
      [4,4,4,4,4,4,5,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,4,4,4,4,4,4,4],
      [4,4,4,4,4,5,5,5,4,4,4,4,4,4],
      [4,5,4,4,5,5,5,5,5,4,4,5,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,4,4,4],
      [4,4,4,5,5,5,5,5,5,5,4,4,4,4],
      [5,4,5,5,5,5,5,5,5,5,5,4,5,4],
      [4,4,5,5,5,5,5,5,5,5,5,4,4,4],
      [4,4,4,5,5,5,5,5,5,5,4,4,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,4,4,4],
      [4,5,4,4,5,5,5,5,5,4,4,5,4,4],
      [4,4,4,4,4,5,5,5,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,4,4,4,4,4,4,4],
    ]
  },
  earth: {
    pattern: [
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,4,4,4,1,1,1,1,1,1],
      [1,1,1,1,4,4,4,4,4,1,1,1,1,1],
      [1,1,1,4,4,1,1,4,4,4,1,1,1,1],
      [1,1,1,4,1,1,1,1,4,4,1,1,1,1],
      [1,1,1,4,1,1,1,1,4,4,4,1,1,1],
      [1,1,1,4,4,1,1,4,4,4,4,1,1,1],
      [1,1,1,1,4,4,4,4,4,4,1,1,1,1],
      [1,1,1,1,1,4,4,4,4,1,1,1,1,1],
      [1,1,1,1,1,1,4,4,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
  },
  mountains: {
    pattern: [
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [2,2,2,2,2,2,2,2,2,2,2,2,2,2],
      [2,2,2,2,2,2,3,3,2,2,2,2,2,2],
      [2,2,2,2,2,3,3,3,3,2,2,2,2,2],
      [2,2,3,3,3,3,3,3,3,3,2,2,2,2],
      [2,3,3,3,3,3,3,3,3,3,3,2,2,2],
      [3,3,3,3,3,3,6,3,3,3,3,3,2,2],
      [3,3,3,3,3,6,6,6,3,3,3,3,3,2],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  river: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,1,1,1,1,4,4,4,4,4,4,4],
      [4,4,4,4,1,1,1,1,4,4,4,4,4,4],
      [4,4,4,4,4,1,1,1,1,4,4,4,4,4],
      [4,4,4,4,4,4,1,1,1,1,4,4,4,4],
      [4,4,4,4,4,4,4,1,1,1,1,4,4,4],
      [4,4,4,4,4,4,1,1,1,1,4,4,4,4],
      [4,4,4,4,4,1,1,1,1,4,4,4,4,4],
      [4,4,4,4,1,1,1,1,4,4,4,4,4,4],
      [4,4,4,1,1,1,1,4,4,4,4,4,4,4],
      [4,4,1,1,1,1,4,4,4,4,4,4,4,4],
      [4,1,1,1,1,4,4,4,4,4,4,4,4,4],
      [1,1,1,1,4,4,4,4,4,4,4,4,4,4],
      [1,1,1,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  portal: {
    pattern: [
      [2,2,2,2,2,2,2,2,2,2,2,2,2,2],
      [2,2,2,2,2,2,2,2,2,2,2,2,2,2],
      [2,2,2,2,7,7,7,7,7,7,2,2,2,2],
      [2,2,2,7,7,2,2,2,2,7,7,2,2,2],
      [2,2,7,7,2,6,6,6,6,2,7,7,2,2],
      [2,2,7,2,6,6,1,1,6,6,2,7,2,2],
      [2,2,7,2,6,1,1,1,1,6,2,7,2,2],
      [2,2,7,2,6,1,1,1,1,6,2,7,2,2],
      [2,2,7,2,6,6,1,1,6,6,2,7,2,2],
      [2,2,7,7,2,6,6,6,6,2,7,7,2,2],
      [2,2,2,7,7,2,2,2,2,7,7,2,2,2],
      [2,2,2,2,7,7,7,7,7,7,2,2,2,2],
      [2,2,2,2,2,2,2,2,2,2,2,2,2,2],
      [2,2,2,2,2,2,2,2,2,2,2,2,2,2],
    ]
  },
  rocket: {
    pattern: [
      [1,1,1,1,1,1,3,3,1,1,1,1,1,1],
      [1,1,1,1,1,3,3,3,3,1,1,1,1,1],
      [1,1,1,1,1,3,3,3,3,1,1,1,1,1],
      [1,1,1,1,1,2,2,2,2,1,1,1,1,1],
      [1,1,1,1,1,2,6,6,2,1,1,1,1,1],
      [1,1,1,1,1,2,6,6,2,1,1,1,1,1],
      [1,1,1,1,1,2,2,2,2,1,1,1,1,1],
      [1,1,1,1,1,2,2,2,2,1,1,1,1,1],
      [1,1,1,1,3,2,2,2,2,3,1,1,1,1],
      [1,1,1,3,3,2,2,2,2,3,3,1,1,1],
      [1,1,1,3,3,5,5,5,5,3,3,1,1,1],
      [1,1,1,1,5,5,5,5,5,5,1,1,1,1],
      [1,1,1,1,1,5,5,5,5,1,1,1,1,1],
      [1,1,1,1,1,1,5,5,1,1,1,1,1,1],
    ]
  },
  sunset: {
    pattern: [
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,5,5,5,5,5,5,4,4,4,4,4],
      [4,4,5,5,5,5,5,5,5,5,4,4,4,4],
      [4,4,5,5,5,5,5,5,5,5,4,4,4,4],
      [4,4,4,5,5,5,5,5,5,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [6,6,6,6,6,6,6,6,6,6,6,6,6,6],
      [6,6,6,6,6,6,6,6,6,6,6,6,6,6],
      [6,6,6,6,6,6,6,6,6,6,6,6,6,6],
    ]
  },
  alien: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,2,2,2,2,2,2,4,4,4,4],
      [4,4,4,2,2,2,2,2,2,2,2,4,4,4],
      [4,4,2,2,1,1,2,2,1,1,2,2,4,4],
      [4,4,2,2,1,1,2,2,1,1,2,2,4,4],
      [4,4,2,2,2,2,2,2,2,2,2,2,4,4],
      [4,4,4,2,2,1,1,1,1,2,2,4,4,4],
      [4,4,4,2,1,1,1,1,1,1,2,4,4,4],
      [4,4,4,4,2,2,2,2,2,2,4,4,4,4],
      [4,4,4,4,2,4,4,4,4,2,4,4,4,4],
      [4,4,4,2,2,4,4,4,4,2,2,4,4,4],
      [4,4,4,2,2,4,4,4,4,2,2,4,4,4],
    ]
  },
  catNight: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,5,5,4,4,4,4,5,5,4,4,4],
      [4,4,4,5,5,4,4,4,4,5,5,4,4,4],
      [4,4,4,5,5,5,4,4,5,5,5,4,4,4],
      [4,4,4,5,5,5,5,5,5,5,5,4,4,4],
      [4,4,4,5,5,5,5,5,5,5,5,4,4,4],
      [4,4,4,5,1,5,5,5,5,1,5,4,4,4],
      [4,4,4,5,1,5,5,5,5,1,5,4,4,4],
      [4,4,4,5,5,5,7,7,5,5,5,4,4,4],
      [4,4,4,5,5,7,7,7,7,5,5,4,4,4],
      [4,4,4,5,5,5,7,7,5,5,5,4,4,4],
      [4,4,4,4,5,5,5,5,5,5,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  dog: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,5,5,4,4,4,4,4,4,5,5,4,4],
      [4,4,5,5,5,4,4,4,4,5,5,5,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,4,5,1,1,5,5,1,1,5,4,4,4],
      [4,4,4,5,1,1,5,5,1,1,5,4,4,4],
      [4,4,4,5,5,5,3,3,5,5,5,4,4,4],
      [4,4,4,5,5,3,3,3,3,5,5,4,4,4],
      [4,4,4,5,5,5,3,3,5,5,5,4,4,4],
      [4,4,4,4,5,5,5,5,5,5,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  bird: {
    pattern: [
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,5,5,1,1,1,1,1,1,1],
      [1,1,1,1,5,5,5,5,1,1,1,1,1,1],
      [1,1,1,5,5,5,5,5,5,1,1,1,1,1],
      [1,1,5,5,5,5,5,5,5,5,1,1,1,1],
      [1,5,5,5,5,5,5,5,5,5,5,1,1,1],
      [1,5,5,1,5,5,5,5,5,5,5,5,1,1],
      [5,5,5,1,5,5,5,5,5,5,5,5,5,1],
      [5,5,5,5,5,5,5,5,5,5,5,5,5,5],
      [1,5,5,5,5,5,5,5,5,5,5,5,5,1],
      [1,1,5,5,5,5,5,5,5,5,5,5,1,1],
      [1,1,1,5,5,5,5,5,5,5,5,1,1,1],
      [1,1,1,1,5,5,1,1,5,5,1,1,1,1],
      [1,1,1,1,5,5,1,1,5,5,1,1,1,1],
    ]
  },
  pig: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,7,7,4,4,4,4,7,7,4,4,4],
      [4,4,4,7,7,7,4,4,7,7,7,4,4,4],
      [4,4,7,7,7,7,7,7,7,7,7,7,4,4],
      [4,4,7,7,7,7,7,7,7,7,7,7,4,4],
      [4,4,7,7,7,7,7,7,7,7,7,7,4,4],
      [4,4,7,1,1,7,7,7,7,1,1,7,4,4],
      [4,4,7,1,1,7,7,7,7,1,1,7,4,4],
      [4,4,7,7,7,7,3,3,7,7,7,7,4,4],
      [4,4,7,7,7,3,3,3,3,7,7,7,4,4],
      [4,4,7,7,7,3,3,3,3,7,7,7,4,4],
      [4,4,4,7,7,7,7,7,7,7,7,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  cow: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,3,3,4,4,4,4,4,4,3,3,4,4],
      [4,4,3,3,3,4,4,4,4,3,3,3,4,4],
      [4,4,6,6,6,6,6,6,6,6,6,6,4,4],
      [4,4,6,3,6,6,6,6,6,6,3,6,4,4],
      [4,4,6,6,6,6,6,6,6,6,6,6,4,4],
      [4,4,6,1,1,6,6,6,6,1,1,6,4,4],
      [4,4,6,1,1,6,6,6,6,1,1,6,4,4],
      [4,4,6,6,6,6,7,7,6,6,6,6,4,4],
      [4,4,6,6,6,7,7,7,7,6,6,6,4,4],
      [4,4,6,6,6,7,7,7,7,6,6,6,4,4],
      [4,4,4,6,6,6,6,6,6,6,6,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  horse: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,3,3,4,4,4,4,4],
      [4,4,4,4,4,4,3,3,3,3,4,4,4,4],
      [4,4,4,4,4,3,3,3,3,3,3,4,4,4],
      [4,4,4,4,3,3,3,3,3,3,3,3,4,4],
      [4,4,4,3,3,3,3,3,3,3,3,3,4,4],
      [4,4,4,3,3,3,3,3,3,3,3,3,4,4],
      [4,4,4,3,1,1,3,3,3,3,3,3,4,4],
      [4,4,4,3,1,1,3,3,3,3,3,3,4,4],
      [4,4,4,3,3,3,3,7,7,3,3,3,4,4],
      [4,4,4,3,3,3,7,7,7,7,3,3,4,4],
      [4,4,4,3,3,3,3,7,7,3,3,3,4,4],
      [4,4,4,4,3,3,3,3,3,3,3,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  camel: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,5,5,4,4,5,5,4,4,4,4],
      [4,4,4,5,5,5,5,5,5,5,5,4,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,5,1,1,5,5,5,5,5,5,5,4,4],
      [4,4,5,1,1,5,5,5,5,5,5,5,4,4],
      [4,4,5,5,5,5,3,3,5,5,5,5,4,4],
      [4,4,5,5,5,3,3,3,3,5,5,5,4,4],
      [4,4,5,5,5,5,3,3,5,5,5,5,4,4],
      [4,4,4,5,5,5,5,5,5,5,5,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  pizza: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,5,4,4,4,4,4,4],
      [4,4,4,4,4,5,5,5,5,4,4,4,4,4],
      [4,4,4,4,5,5,3,5,5,5,4,4,4,4],
      [4,4,4,5,5,5,5,5,3,5,5,4,4,4],
      [4,4,5,5,3,5,5,5,5,5,5,5,4,4],
      [4,4,5,5,5,5,5,3,5,5,3,5,4,4],
      [4,5,5,5,3,5,5,5,5,5,5,5,5,4],
      [4,5,5,5,5,5,5,3,5,5,5,5,5,4],
      [4,5,5,5,5,5,5,5,5,5,5,5,5,4],
      [4,4,5,5,5,5,5,5,5,5,5,5,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  cake: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,3,3,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,5,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,5,4,4,4,4,4,4],
      [4,4,4,4,4,3,7,7,3,4,4,4,4,4],
      [4,4,4,4,4,7,7,7,7,4,4,4,4,4],
      [4,4,4,4,4,7,7,7,7,4,4,4,4,4],
      [4,4,4,4,7,7,7,7,7,7,4,4,4,4],
      [4,4,4,7,7,7,7,7,7,7,7,4,4,4],
      [4,4,4,7,6,7,7,7,7,6,7,4,4,4],
      [4,4,7,7,7,7,6,6,7,7,7,7,4,4],
      [4,4,7,6,7,7,7,7,7,7,6,7,4,4],
      [4,4,7,7,7,7,7,7,7,7,7,7,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
  cupcake: {
    pattern: [
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
      [4,4,4,4,4,4,3,3,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,5,4,4,4,4,4,4],
      [4,4,4,4,4,4,5,5,4,4,4,4,4,4],
      [4,4,4,4,4,7,7,7,7,4,4,4,4,4],
      [4,4,4,4,7,7,7,7,7,7,4,4,4,4],
      [4,4,4,7,7,7,7,7,7,7,7,4,4,4],
      [4,4,4,7,7,6,7,7,6,7,7,4,4,4],
      [4,4,4,4,7,7,7,7,7,7,4,4,4,4],
      [4,4,4,4,2,7,7,7,7,2,4,4,4,4],
      [4,4,4,4,2,2,7,7,2,2,4,4,4,4],
      [4,4,4,4,4,2,2,2,2,4,4,4,4,4],
      [4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    ]
  },
}

// Select random image on mount
const imageKeys = Object.keys(imageTemplates) as Array<keyof typeof imageTemplates>
const currentImageKey = ref<keyof typeof imageTemplates>('robot')
const currentImage = computed(() => imageTemplates[currentImageKey.value])

// Create input pixels (random colors at start)
const inputPixels = computed(() => {
  const pixels: Array<{ colorIndex: number; row: number; col: number }> = []

  for (let row = 0; row < 14; row++) {
    for (let col = 0; col < 14; col++) {
      // Random color index 1-7 for each input pixel
      const colorIndex = (row * 14 + col) % 7 + 1
      pixels.push({ colorIndex, row, col })
    }
  }

  return pixels
})

// Output pixels are the target image pattern
const outputPixels = computed(() => {
  const pattern = currentImage.value.pattern
  const pixels: Array<{ colorIndex: number; row: number; col: number }> = []

  for (let row = 0; row < 14; row++) {
    for (let col = 0; col < 14; col++) {
      const colorIndex = pattern[row]?.[col] ?? 0
      pixels.push({ colorIndex, row, col })
    }
  }

  return pixels
})

onMounted(() => {
  // Select random image
  const randomIndex = Math.floor(Math.random() * imageKeys.length)
  const selectedKey = imageKeys[randomIndex]
  if (selectedKey) {
    currentImageKey.value = selectedKey
  }
})

onUnmounted(() => {
  // Clean up timer
  if (timerInterval !== null) {
    clearInterval(timerInterval)
  }
})

// Watch progress to start/stop timer
watch(() => props.progress, (newProgress, oldProgress) => {
  // Start timer when progress becomes > 0
  if (newProgress > 0 && oldProgress === 0) {
    elapsedSeconds.value = 0
    if (timerInterval !== null) {
      clearInterval(timerInterval)
    }
    timerInterval = setInterval(() => {
      elapsedSeconds.value++
    }, 1000) as unknown as number
  }

  // Stop timer when progress reaches 100 or resets to 0
  if ((newProgress >= 100 || newProgress === 0) && timerInterval !== null) {
    clearInterval(timerInterval)
    timerInterval = null
  }
})

function getInputPixelStyle(pixel: { colorIndex: number; row: number; col: number }, index: number) {
  const cacheKey = `${pixel.colorIndex}-${index}`
  if (inputPixelStyleCache.has(cacheKey)) {
    return inputPixelStyleCache.get(cacheKey)!
  }

  const color = tokenColors[pixel.colorIndex - 1] ?? '#888'
  const style = {
    backgroundColor: color,
    boxShadow: `0 0 6px ${color}80, inset 0 0 3px rgba(255,255,255,0.2)`,
    animationDelay: (index * 0.005) + 's'
  }
  inputPixelStyleCache.set(cacheKey, style)
  return style
}

function getOutputPixelStyle(pixel: { colorIndex: number; row: number; col: number }, index: number) {
  const outputPixel = outputPixels.value[index]
  const inputPixel = inputPixels.value[index]

  // If this is the flying pixel, use CSS variables for color transition (not cached - dynamic state)
  if (index === processedCount.value - 1 && isProcessing.value && inputPixel && outputPixel) {
    const fromColor = tokenColors[inputPixel.colorIndex - 1]
    const toColor = outputPixel.colorIndex > 0 ? tokenColors[outputPixel.colorIndex - 1] : 'transparent'
    return {
      '--from-color': fromColor,
      '--to-color': toColor,
      animationDelay: (index * 0.005) + 's',
      opacity: outputPixel.colorIndex === 0 ? 0 : 1
    }
  }

  // Non-flying pixels: cache the style
  const cacheKey = `${pixel.colorIndex}-${index}`
  if (outputPixelStyleCache.has(cacheKey)) {
    return outputPixelStyleCache.get(cacheKey)!
  }

  const color = pixel.colorIndex > 0 ? (tokenColors[pixel.colorIndex - 1] ?? '#888') : 'transparent'
  const style = {
    backgroundColor: color,
    boxShadow: pixel.colorIndex > 0 ? `0 0 8px ${color}80, inset 0 0 4px rgba(255,255,255,0.3)` : 'none',
    animationDelay: (index * 0.005) + 's',
    opacity: pixel.colorIndex === 0 ? 0 : 1
  }
  outputPixelStyleCache.set(cacheKey, style)
  return style
}
</script>

<style scoped>
.progress-animation-container {
  width: 100%;
  height: 320px;
  position: relative;
  overflow: hidden;
  background: transparent;
}

.token-processing-scene {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 20px;
  background: radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a1a 100%);
  border-radius: 12px;
}

/* Stats bar (terminal-styled like Iceberg) */
.stats-bar {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 20px;
  z-index: 100;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-label {
  font-family: 'Courier New', monospace;
  font-size: 9px;
  color: rgba(0, 255, 0, 0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #0f0;
  font-weight: bold;
  text-shadow: 0 0 8px #0f0;
}

.cursor {
  animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  50.1%, 100% { opacity: 0; }
}

/* Summary box at bottom - wide and compact */
.summary-box {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  background: rgba(0, 0, 0, 0.85);
  padding: 6px 24px;
  border-radius: 8px;
  border: 1px solid rgba(0, 255, 0, 0.4);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
  max-width: 90%;
}

.summary-comparison {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #0f0;
  text-shadow: 0 0 8px #0f0;
  white-space: nowrap;
}

/* Fade transition for summary */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Input Grid (Left) */
.input-grid-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 160px;
}

/* Output Grid (Right) */
.output-grid-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 160px;
}

/* Processor Box */
.processor-box {
  position: relative;
  width: 140px;
  height: 160px;
  background: linear-gradient(135deg, #1a1a3e 0%, #0f0f2a 100%);
  border: 3px solid #2d4a7c;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 0 20px rgba(45, 74, 124, 0.3),
    inset 0 0 30px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.processor-box.active {
  border-color: #4a90e2;
  box-shadow:
    0 0 40px rgba(74, 144, 226, 0.6),
    inset 0 0 30px rgba(0, 0, 0, 0.5);
}

.processor-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  background: radial-gradient(circle, rgba(74, 144, 226, 0.3) 0%, rgba(147, 51, 234, 0.2) 50%, transparent 70%);
  opacity: 0;
  animation: processor-flicker 1.2s ease-in-out infinite;
}

.processor-box.active .processor-glow {
  opacity: 1;
  animation: processor-flicker-active 0.8s ease-in-out infinite;
}

@keyframes processor-flicker {
  0%, 100% {
    transform: scale(1);
    opacity: 0.2;
  }
  25% {
    transform: scale(1.05);
    opacity: 0.4;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.6;
  }
  75% {
    transform: scale(1.08);
    opacity: 0.5;
  }
}

@keyframes processor-flicker-active {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
    filter: brightness(1);
  }
  20% {
    transform: scale(1.12);
    opacity: 0.9;
    filter: brightness(1.3);
  }
  40% {
    transform: scale(1.08);
    opacity: 0.7;
    filter: brightness(1.1);
  }
  60% {
    transform: scale(1.15);
    opacity: 1;
    filter: brightness(1.5);
  }
  80% {
    transform: scale(1.05);
    opacity: 0.8;
    filter: brightness(1.2);
  }
}

.processor-core {
  position: relative;
  width: 80%;
  height: 80%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Neural Network */
.neural-network {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Network Nodes */
.network-node {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #4a90e2;
  border-radius: 50%;
  opacity: 0.3;
  box-shadow: 0 0 8px #4a90e2;
}

.node-1 {
  top: 15%;
  left: 20%;
  animation: node-pulse 1.5s ease-in-out infinite;
}

.node-2 {
  top: 50%;
  left: 10%;
  animation: node-pulse 1.5s ease-in-out infinite 0.3s;
}

.node-3 {
  top: 80%;
  left: 25%;
  animation: node-pulse 1.5s ease-in-out infinite 0.6s;
}

.node-4 {
  top: 30%;
  right: 20%;
  animation: node-pulse 1.5s ease-in-out infinite 0.9s;
}

.node-5 {
  top: 70%;
  right: 15%;
  animation: node-pulse 1.5s ease-in-out infinite 1.2s;
}

.processor-box.active .network-node {
  opacity: 0.8;
  animation-duration: 0.8s;
}

@keyframes node-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
    box-shadow: 0 0 8px #4a90e2;
  }
  50% {
    transform: scale(1.6);
    opacity: 1;
    box-shadow: 0 0 20px #4a90e2, 0 0 40px #4a90e2;
  }
}

/* Network Connections */
.network-connection {
  position: absolute;
  background: linear-gradient(90deg, transparent 0%, #4a90e2 50%, transparent 100%);
  height: 1px;
  opacity: 0.2;
}

.conn-1 {
  top: 25%;
  left: 20%;
  width: 60%;
  transform: rotate(15deg);
  animation: connection-pulse 2s ease-in-out infinite;
}

.conn-2 {
  top: 55%;
  left: 10%;
  width: 70%;
  transform: rotate(-10deg);
  animation: connection-pulse 2s ease-in-out infinite 0.4s;
}

.conn-3 {
  top: 40%;
  left: 15%;
  width: 50%;
  transform: rotate(45deg);
  animation: connection-pulse 2s ease-in-out infinite 0.8s;
}

.conn-4 {
  top: 70%;
  left: 25%;
  width: 55%;
  transform: rotate(-20deg);
  animation: connection-pulse 2s ease-in-out infinite 1.2s;
}

.processor-box.active .network-connection {
  opacity: 0.6;
  animation-duration: 1s;
}

@keyframes connection-pulse {
  0%, 100% {
    opacity: 0.1;
    filter: brightness(0.8);
  }
  50% {
    opacity: 0.8;
    filter: brightness(1.5);
  }
}

.processor-icon {
  font-size: 44px;
  animation: processor-icon-pulse 1s ease-in-out infinite;
  filter: drop-shadow(0 0 10px #4a90e2);
  z-index: 10;
}

.processor-box.active .processor-icon {
  animation: processor-icon-active 0.5s ease-in-out infinite;
  filter: drop-shadow(0 0 20px #4a90e2) drop-shadow(0 0 40px #9333ea);
}

@keyframes processor-icon-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.7;
  }
}

@keyframes processor-icon-active {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
    filter: brightness(1);
  }
  15% {
    transform: scale(1.2) rotate(-8deg);
    opacity: 1;
    filter: brightness(1.5);
  }
  30% {
    transform: scale(0.95) rotate(5deg);
    opacity: 0.9;
    filter: brightness(1.2);
  }
  50% {
    transform: scale(1.25) rotate(-3deg);
    opacity: 1;
    filter: brightness(1.7);
  }
  75% {
    transform: scale(1.05) rotate(8deg);
    opacity: 0.95;
    filter: brightness(1.3);
  }
}

/* Canvas Grid (used by both input and output) */
.canvas-grid {
  display: grid;
  grid-template-columns: repeat(14, 10px);
  grid-template-rows: repeat(14, 10px);
  gap: 1px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

/* Pixel Token */
.pixel-token {
  width: 10px;
  height: 10px;
  border-radius: 1px;
  transition: all 0.3s ease;
  position: relative;
}

/* Input grid pixels */
.input-grid-container .pixel-token {
  transform: scale(1);
  opacity: 1;
}

.input-grid-container .pixel-token.hidden {
  transform: scale(0);
  opacity: 0;
}

/* Output grid pixels */
.output-grid-container .pixel-token {
  transform: scale(0);
  opacity: 0;
}

.output-grid-container .pixel-token.visible {
  transform: scale(1);
  opacity: 1;
  transition: transform 0.3s ease-out, opacity 0.3s ease-out;
}

.output-grid-container .pixel-token.flying {
  animation: pixel-fly-from-left 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  animation-fill-mode: forwards;
  z-index: 100;
}

@keyframes pixel-fly-from-left {
  /* Fly from left grid to left edge of processor box */
  0% {
    transform: translate(-350px, 0) scale(0.7) rotate(0deg);
    background-color: var(--from-color);
    opacity: 1;
    box-shadow: 0 0 25px var(--from-color), 0 0 50px var(--from-color);
  }

  /* Arrive at left edge of processor box */
  20% {
    transform: translate(-210px, 0) scale(1.2) rotate(90deg);
    background-color: var(--from-color);
    opacity: 1;
    box-shadow: 0 0 40px var(--from-color), 0 0 70px var(--from-color);
  }

  /* Enter processor box - swirl inside layer 1 */
  30% {
    transform: translate(-180px, -15px) scale(1.6) rotate(180deg);
    background-color: var(--from-color);
    opacity: 1;
    box-shadow: 0 0 50px var(--from-color), 0 0 90px var(--from-color);
  }

  /* Swirl deeper - layer 2, color starts changing */
  42% {
    transform: translate(-165px, 12px) scale(1.7) rotate(290deg);
    background-color: color-mix(in srgb, var(--from-color) 70%, var(--to-color) 30%);
    opacity: 1;
    box-shadow: 0 0 55px color-mix(in srgb, var(--from-color) 70%, var(--to-color) 30%),
                0 0 95px color-mix(in srgb, var(--from-color) 70%, var(--to-color) 30%);
  }

  /* Center of processor - mid transformation */
  50% {
    transform: translate(-150px, -8px) scale(1.8) rotate(380deg);
    background-color: color-mix(in srgb, var(--from-color) 50%, var(--to-color) 50%);
    opacity: 1;
    box-shadow: 0 0 60px color-mix(in srgb, var(--from-color) 50%, var(--to-color) 50%),
                0 0 100px color-mix(in srgb, var(--from-color) 50%, var(--to-color) 50%);
  }

  /* Move toward exit - layer 3 */
  58% {
    transform: translate(-135px, 10px) scale(1.7) rotate(470deg);
    background-color: color-mix(in srgb, var(--from-color) 30%, var(--to-color) 70%);
    opacity: 1;
    box-shadow: 0 0 55px color-mix(in srgb, var(--from-color) 30%, var(--to-color) 70%),
                0 0 95px color-mix(in srgb, var(--from-color) 30%, var(--to-color) 70%);
  }

  /* Final swirl - transformation complete */
  68% {
    transform: translate(-120px, -12px) scale(1.6) rotate(560deg);
    background-color: var(--to-color);
    opacity: 1;
    box-shadow: 0 0 50px var(--to-color), 0 0 90px var(--to-color);
  }

  /* Exit at right edge of processor box */
  78% {
    transform: translate(-100px, 0) scale(1.3) rotate(630deg);
    background-color: var(--to-color);
    opacity: 1;
    box-shadow: 0 0 40px var(--to-color), 0 0 70px var(--to-color);
  }

  /* Fly from processor to output grid */
  90% {
    transform: translate(-30px, 0) scale(1.15) rotate(680deg);
    background-color: var(--to-color);
    opacity: 1;
    box-shadow: 0 0 30px var(--to-color), 0 0 55px var(--to-color);
  }

  /* Land in final position */
  100% {
    transform: translate(0, 0) scale(1) rotate(720deg);
    background-color: var(--to-color);
    opacity: 1;
    box-shadow: 0 0 8px var(--to-color), 0 0 15px var(--to-color);
  }
}

/* Progress Bar at Bottom */
.progress-bar-container {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 85%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5);
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db 0%, #2ecc71 50%, #f39c12 100%);
  border-radius: 10px;
  position: relative;
  transition: width 0.3s ease-out;
  box-shadow: 0 0 10px rgba(52, 152, 219, 0.5);
}

.progress-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
  animation: shine-move 2s ease-in-out infinite;
}

@keyframes shine-move {
  0% { left: -100%; }
  100% { left: 200%; }
}

.progress-text {
  font-family: 'Courier New', monospace;
  font-size: 16px;
  font-weight: bold;
  color: #0f0;
  text-shadow: 0 0 8px #0f0;
}

/* Responsive */
@media (max-width: 768px) {
  .token-processing-scene {
    gap: 15px;
    padding: 15px 8px;
  }

  .generating-text {
    font-size: 13px;
    letter-spacing: 1px;
  }

  .input-grid-container,
  .output-grid-container {
    width: 130px;
  }

  .processor-box {
    width: 100px;
    height: 120px;
  }

  .processor-icon {
    font-size: 32px;
  }

  .canvas-grid {
    grid-template-columns: repeat(14, 8px);
    grid-template-rows: repeat(14, 8px);
    padding: 8px;
  }

  .pixel-token {
    width: 8px;
    height: 8px;
  }

  .progress-text {
    font-size: 14px;
  }
}
</style>
