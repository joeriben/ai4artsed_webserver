<template>
  <div class="progress-animation-container">
    <div class="token-processing-scene">
      <!-- GPU Stats Bar -->
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
        <div class="stat">
          <span class="stat-label">Pixel</span>
          <span class="stat-value">{{ processedPixels.size }}/196</span>
        </div>
      </div>

      <!-- Instructions overlay (fades after 5s) -->
      <Transition name="fade">
        <div v-if="showInstructions && progress > 0" class="instructions-overlay">
          <span class="instruction-text">{{ t('edutainment.pixel.clickToProcess') }}</span>
        </div>
      </Transition>

      <!-- Summary overlay (bottom, appears after 5s) -->
      <Transition name="fade">
        <div v-if="isShowingSummary" class="summary-box">
          <div class="summary-comparison">
            {{ t('edutainment.pixel.smartphoneComparison', { minutes: smartphoneMinutes }) }}
          </div>
        </div>
      </Transition>

      <!-- Input Grid (Left) - Clickable -->
      <div class="input-grid-container">
        <div class="canvas-grid clickable" @click="handleGridClick" ref="inputGridRef">
          <div
            v-for="(pixel, index) in inputPixels"
            :key="'input-' + index"
            class="pixel-token"
            :class="{
              hidden: processedPixels.has(index) || flyingPixels.has(index),
              clickable: !processedPixels.has(index) && !flyingPixels.has(index) && !clickCooldown
            }"
            :style="getInputPixelStyle(pixel, index)"
            :data-index="index"
          ></div>
        </div>
      </div>

      <!-- Processor Box (Center) -->
      <div class="processor-box" :class="{ active: flyingPixels.size > 0 || isProcessing }">
        <div class="processor-glow"></div>
        <div class="processor-core">
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
              visible: processedPixels.has(index),
              flying: flyingPixels.has(index)
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  progress: number
  estimatedSeconds?: number
  gpuPower?: number
  gpuTemp?: number
  totalEnergy?: number
  totalCo2?: number
  isShowingSummary?: boolean
  smartphoneMinutes?: number
}>()

// Default values for GPU stats
const gpuPower = computed(() => props.gpuPower ?? 0)
const gpuTemp = computed(() => props.gpuTemp ?? 0)
const totalEnergy = computed(() => props.totalEnergy ?? 0)
const totalCo2 = computed(() => props.totalCo2 ?? 0)
const smartphoneMinutes = computed(() => {
  if (props.smartphoneMinutes !== undefined) return props.smartphoneMinutes
  return Math.round(totalCo2.value * 30)
})

const isProcessing = computed(() => props.progress > 0 && props.progress < 100)

// ==================== Interactive State ====================
const processedPixels = ref<Set<number>>(new Set())
const flyingPixels = ref<Set<number>>(new Set())
const clickCooldown = ref(false)
const autoCompleted = ref(false)
const showInstructions = ref(true)
const inputGridRef = ref<HTMLElement | null>(null)

// ==================== Image Templates ====================
const tokenColors = [
  '#3498db', '#9b59b6', '#e74c3c', '#2ecc71', '#f39c12', '#1abc9c', '#e91e63'
]

const imageTemplates = {
  robot: { pattern: [[0,0,0,6,6,0,0,0,0,6,6,0,0,0],[0,0,0,6,6,0,0,0,0,6,6,0,0,0],[0,0,6,6,6,6,6,6,6,6,6,6,0,0],[0,0,6,0,0,6,6,6,6,0,0,6,0,0],[0,0,6,0,0,6,6,6,6,0,0,6,0,0],[0,0,6,6,6,7,6,6,7,6,6,6,0,0],[0,0,6,6,6,6,3,3,6,6,6,6,0,0],[0,0,0,6,6,6,6,6,6,6,6,0,0,0],[0,0,6,6,6,6,6,6,6,6,6,6,0,0],[0,6,6,6,1,1,6,6,1,1,6,6,6,0],[0,6,6,6,1,1,6,6,1,1,6,6,6,0],[0,0,6,6,6,6,6,6,6,6,6,6,0,0],[0,0,3,3,3,0,0,0,0,3,3,3,0,0],[0,0,3,3,3,0,0,0,0,3,3,3,0,0]] },
  flower: { pattern: [[0,0,0,7,7,0,0,0,0,7,7,0,0,0],[0,0,7,7,7,7,0,0,7,7,7,7,0,0],[0,7,7,7,7,7,7,7,7,7,7,7,7,0],[0,7,7,7,7,7,7,7,7,7,7,7,7,0],[0,0,7,7,7,5,5,5,5,7,7,7,0,0],[0,0,0,7,5,5,5,5,5,5,7,0,0,0],[0,0,0,7,5,5,0,0,5,5,7,0,0,0],[0,0,0,7,5,5,3,3,5,5,7,0,0,0],[0,0,0,7,5,5,5,5,5,5,7,0,0,0],[0,0,0,0,7,4,4,4,4,7,0,0,0,0],[0,0,0,0,4,4,4,4,4,4,0,0,0,0],[0,0,0,0,0,4,4,4,4,0,0,0,0,0],[0,0,0,0,0,0,4,4,0,0,0,0,0,0],[0,0,0,0,0,0,4,4,0,0,0,0,0,0]] },
  football: { pattern: [[0,0,0,0,1,1,1,1,1,1,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,0,0,1,1,0,0,1,1,0,0],[0,1,1,0,0,0,1,1,0,0,0,1,1,0],[0,1,1,0,0,1,1,1,1,0,0,1,1,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,0,0,1,1,1,1,1,1],[1,1,1,1,1,1,0,0,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[0,1,1,0,0,1,1,1,1,0,0,1,1,0],[0,1,1,0,0,0,1,1,0,0,0,1,1,0],[0,0,1,1,0,0,1,1,0,0,1,1,0,0],[0,0,0,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,1,1,1,1,1,1,0,0,0,0]] },
  heart: { pattern: [[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,3,3,3,0,0,0,3,3,3,0,0,0],[0,3,3,7,3,3,0,3,3,7,3,3,0,0],[0,3,7,7,7,3,3,3,7,7,7,3,0,0],[0,3,7,7,7,7,3,7,7,7,7,3,0,0],[0,3,7,7,7,7,7,7,7,7,7,3,0,0],[0,0,3,7,7,7,7,7,7,7,3,0,0,0],[0,0,0,3,7,7,7,7,7,3,0,0,0,0],[0,0,0,0,3,7,7,7,3,0,0,0,0,0],[0,0,0,0,0,3,7,3,0,0,0,0,0,0],[0,0,0,0,0,0,3,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  star: { pattern: [[0,0,0,0,0,0,5,5,0,0,0,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,5,5,5,5,5,5,0,0,0,0],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[0,5,5,5,5,5,5,5,5,5,5,5,5,0],[0,0,5,5,5,5,5,5,5,5,5,5,0,0],[0,0,5,5,5,5,0,0,5,5,5,5,0,0],[0,0,0,5,5,5,0,0,5,5,5,0,0,0],[0,0,5,5,5,0,0,0,0,5,5,5,0,0],[0,5,5,5,0,0,0,0,0,0,5,5,5,0],[5,5,5,0,0,0,0,0,0,0,0,5,5,5],[5,5,0,0,0,0,0,0,0,0,0,0,5,5]] },
  house: { pattern: [[0,0,0,0,0,0,3,3,0,0,0,0,0,0],[0,0,0,0,0,3,3,3,3,0,0,0,0,0],[0,0,0,0,3,3,3,3,3,3,0,0,0,0],[0,0,0,3,3,5,5,5,5,3,3,0,0,0],[0,0,3,3,5,5,5,5,5,5,3,3,0,0],[0,0,7,7,7,7,7,7,7,7,7,7,0,0],[0,0,7,7,1,1,7,7,1,1,7,7,0,0],[0,0,7,7,1,1,7,7,1,1,7,7,0,0],[0,0,7,7,7,7,7,7,7,7,7,7,0,0],[0,0,7,7,7,7,0,0,7,7,7,7,0,0],[0,0,7,7,7,7,0,0,7,7,7,7,0,0],[0,0,7,7,2,2,2,2,7,7,7,7,0,0],[0,0,7,7,2,2,2,2,7,7,7,7,0,0],[0,0,7,7,2,2,2,2,7,7,7,7,0,0]] },
  tree: { pattern: [[0,0,0,0,4,4,4,4,4,4,0,0,0,0],[0,0,0,4,4,4,4,4,4,4,4,0,0,0],[0,0,4,4,4,4,4,4,4,4,4,4,0,0],[0,4,4,4,4,4,4,4,4,4,4,4,4,0],[0,4,4,4,4,4,4,4,4,4,4,4,4,0],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[0,4,4,4,4,4,4,4,4,4,4,4,4,0],[0,4,4,4,4,4,4,4,4,4,4,4,4,0],[0,0,4,4,4,4,4,4,4,4,4,4,0,0],[0,0,0,4,4,4,4,4,4,4,4,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,0,0,5,5,0,0,0,0,0,0]] },
  moon: { pattern: [[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,6,6,6,6,6,1,1,1,1,1,1],[1,1,6,6,6,6,6,6,6,1,1,1,1,1],[1,6,6,6,6,6,6,6,6,6,1,1,1,1],[1,6,6,6,6,6,6,6,6,6,1,1,1,1],[1,6,6,6,6,6,6,6,6,1,1,1,1,1],[1,6,6,6,6,6,6,6,1,1,1,1,1,1],[1,1,6,6,6,6,6,1,1,1,1,1,1,1],[1,1,1,6,6,6,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1]] },
  cat: { pattern: [[0,0,5,5,0,0,0,0,0,0,5,5,0,0],[0,5,5,5,5,0,0,0,0,5,5,5,5,0],[0,5,5,5,5,0,0,0,0,5,5,5,5,0],[0,0,5,5,5,5,5,5,5,5,5,5,0,0],[0,0,5,5,5,5,5,5,5,5,5,5,0,0],[0,0,5,0,0,5,5,5,5,0,0,5,0,0],[0,0,5,0,0,5,5,5,5,0,0,5,0,0],[0,0,5,5,5,7,5,5,7,5,5,5,0,0],[0,0,5,5,5,5,5,5,5,5,5,5,0,0],[0,0,5,5,3,3,3,3,3,3,5,5,0,0],[0,0,5,5,5,3,3,3,3,5,5,5,0,0],[0,0,0,5,5,5,5,5,5,5,5,0,0,0],[0,0,0,0,5,5,5,5,5,5,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  music: { pattern: [[0,0,0,0,0,0,0,0,0,2,2,0,0,0],[0,0,0,0,0,0,0,0,0,2,2,0,0,0],[0,0,0,0,0,0,0,0,0,2,2,0,0,0],[0,0,0,0,0,0,0,0,0,2,2,0,0,0],[0,7,7,0,0,0,0,0,0,2,2,0,0,0],[7,7,7,7,0,0,0,0,0,2,2,0,0,0],[7,7,7,7,7,0,0,0,0,2,2,0,0,0],[7,7,7,7,7,7,0,0,7,2,2,7,0,0],[0,7,7,7,7,7,7,7,7,7,7,7,7,0],[0,0,7,7,7,7,7,7,7,7,7,7,7,0],[0,0,0,7,7,7,7,7,7,7,7,7,0,0],[0,0,0,0,7,7,7,7,0,7,7,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  computer: { pattern: [[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,2,6,6,6,6,6,6,6,6,2,0,0],[0,0,2,6,6,6,6,6,6,6,6,2,0,0],[0,0,2,6,6,3,6,6,3,6,6,2,0,0],[0,0,2,6,6,6,6,6,6,6,6,2,0,0],[0,0,2,6,6,6,3,3,6,6,6,2,0,0],[0,0,2,6,6,6,6,6,6,6,6,2,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,0,0,0,2,2,2,2,0,0,0,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,2,1,1,1,1,1,1,1,1,2,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  palette: { pattern: [[0,0,0,5,5,5,5,5,5,5,5,0,0,0],[0,0,5,5,3,5,5,5,5,1,5,5,0,0],[0,5,5,3,3,3,5,5,1,1,1,5,5,0],[0,5,5,3,3,3,5,5,1,1,1,5,5,0],[5,5,5,5,3,5,5,5,5,1,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,7,7,7,5,5,5,5,5,5,2,2,5,5],[5,7,7,7,5,5,5,5,5,2,2,2,2,5],[5,5,7,5,5,5,5,5,5,5,2,2,5,5],[0,5,5,4,4,4,5,5,6,6,5,5,0,0],[0,5,5,4,4,4,5,6,6,6,6,5,5,0],[0,0,5,5,4,5,5,5,6,6,5,5,0,0],[0,0,0,5,5,5,5,5,5,5,5,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  smiley: { pattern: [[0,0,0,5,5,5,5,5,5,5,5,0,0,0],[0,0,5,5,5,5,5,5,5,5,5,5,0,0],[0,5,5,5,5,5,5,5,5,5,5,5,5,0],[0,5,5,0,0,5,5,5,5,0,0,5,5,0],[5,5,5,0,0,5,5,5,5,0,0,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,0,5,5,5,5,5,5,5,5,0,5,5],[5,5,5,0,0,0,0,0,0,0,0,5,5,5],[0,5,5,5,0,0,0,0,0,0,5,5,5,0],[0,5,5,5,5,5,5,5,5,5,5,5,5,0],[0,0,5,5,5,5,5,5,5,5,5,5,0,0],[0,0,0,5,5,5,5,5,5,5,5,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  rainbow: { pattern: [[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,3,3,3,3,3,3,3,3,0,0,0],[0,0,3,3,5,5,5,5,5,5,3,3,0,0],[0,3,3,5,5,5,5,5,5,5,5,3,3,0],[0,3,5,5,5,4,4,4,4,5,5,5,3,0],[3,3,5,5,4,4,4,4,4,4,5,5,3,3],[3,5,5,4,4,4,1,1,4,4,4,5,5,3],[3,5,4,4,4,1,1,1,1,4,4,4,5,3],[3,5,4,4,1,1,1,1,1,1,4,4,5,3],[3,5,4,4,1,1,0,0,1,1,4,4,5,3],[0,3,4,4,1,1,0,0,1,1,4,4,3,0],[0,0,3,4,4,1,0,0,1,4,4,3,0,0],[0,0,0,3,4,4,0,0,4,4,3,0,0,0],[0,0,0,0,3,3,0,0,3,3,0,0,0,0]] },
  icecream: { pattern: [[0,0,0,0,7,7,7,7,7,7,0,0,0,0],[0,0,0,7,7,7,7,7,7,7,7,0,0,0],[0,0,7,7,7,7,7,7,7,7,7,7,0,0],[0,0,7,7,7,0,0,0,0,7,7,7,0,0],[0,0,7,7,7,7,7,7,7,7,7,7,0,0],[0,0,7,7,7,7,7,7,7,7,7,7,0,0],[0,0,0,7,7,7,7,7,7,7,7,0,0,0],[0,0,0,0,7,7,7,7,7,7,0,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,0,5,5,5,5,0,0,0,0,0],[0,0,0,0,0,0,5,5,0,0,0,0,0,0],[0,0,0,0,0,0,5,5,0,0,0,0,0,0],[0,0,0,0,0,0,5,5,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  camera: { pattern: [[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,3,3,3,3,3,3,0,0,0,0],[0,0,0,3,3,3,3,3,3,3,3,0,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,2,2,6,6,6,6,6,6,2,2,0,0],[0,0,2,2,6,1,1,1,1,6,2,2,0,0],[0,0,2,2,6,1,1,1,1,6,2,2,0,0],[0,0,2,2,6,6,6,6,6,6,2,2,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,0,0],[0,0,0,2,2,2,2,2,2,2,2,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]] },
  sun: { pattern: [[4,4,4,4,4,4,5,4,4,4,4,4,4,4],[4,4,4,4,4,4,5,4,4,4,4,4,4,4],[4,4,4,4,4,5,5,5,4,4,4,4,4,4],[4,5,4,4,5,5,5,5,5,4,4,5,4,4],[4,4,5,5,5,5,5,5,5,5,5,4,4,4],[4,4,4,5,5,5,5,5,5,5,4,4,4,4],[5,4,5,5,5,5,5,5,5,5,5,4,5,4],[4,4,5,5,5,5,5,5,5,5,5,4,4,4],[4,4,4,5,5,5,5,5,5,5,4,4,4,4],[4,4,5,5,5,5,5,5,5,5,5,4,4,4],[4,5,4,4,5,5,5,5,5,4,4,5,4,4],[4,4,4,4,4,5,5,5,4,4,4,4,4,4],[4,4,4,4,4,4,5,4,4,4,4,4,4,4],[4,4,4,4,4,4,5,4,4,4,4,4,4,4]] },
  earth: { pattern: [[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,4,4,4,1,1,1,1,1,1],[1,1,1,1,4,4,4,4,4,1,1,1,1,1],[1,1,1,4,4,1,1,4,4,4,1,1,1,1],[1,1,1,4,1,1,1,1,4,4,1,1,1,1],[1,1,1,4,1,1,1,1,4,4,4,1,1,1],[1,1,1,4,4,1,1,4,4,4,4,1,1,1],[1,1,1,1,4,4,4,4,4,4,1,1,1,1],[1,1,1,1,1,4,4,4,4,1,1,1,1,1],[1,1,1,1,1,1,4,4,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1]] },
  mountains: { pattern: [[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,3,3,2,2,2,2,2,2],[2,2,2,2,2,3,3,3,3,2,2,2,2,2],[2,2,3,3,3,3,3,3,3,3,2,2,2,2],[2,3,3,3,3,3,3,3,3,3,3,2,2,2],[3,3,3,3,3,3,6,3,3,3,3,3,2,2],[3,3,3,3,3,6,6,6,3,3,3,3,3,2],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  river: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,1,1,1,1,4,4,4,4,4,4,4],[4,4,4,4,1,1,1,1,4,4,4,4,4,4],[4,4,4,4,4,1,1,1,1,4,4,4,4,4],[4,4,4,4,4,4,1,1,1,1,4,4,4,4],[4,4,4,4,4,4,4,1,1,1,1,4,4,4],[4,4,4,4,4,4,1,1,1,1,4,4,4,4],[4,4,4,4,4,1,1,1,1,4,4,4,4,4],[4,4,4,4,1,1,1,1,4,4,4,4,4,4],[4,4,4,1,1,1,1,4,4,4,4,4,4,4],[4,4,1,1,1,1,4,4,4,4,4,4,4,4],[4,1,1,1,1,4,4,4,4,4,4,4,4,4],[1,1,1,1,4,4,4,4,4,4,4,4,4,4],[1,1,1,4,4,4,4,4,4,4,4,4,4,4]] },
  portal: { pattern: [[2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,7,7,7,7,7,7,2,2,2,2],[2,2,2,7,7,2,2,2,2,7,7,2,2,2],[2,2,7,7,2,6,6,6,6,2,7,7,2,2],[2,2,7,2,6,6,1,1,6,6,2,7,2,2],[2,2,7,2,6,1,1,1,1,6,2,7,2,2],[2,2,7,2,6,1,1,1,1,6,2,7,2,2],[2,2,7,2,6,6,1,1,6,6,2,7,2,2],[2,2,7,7,2,6,6,6,6,2,7,7,2,2],[2,2,2,7,7,2,2,2,2,7,7,2,2,2],[2,2,2,2,7,7,7,7,7,7,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2]] },
  rocket: { pattern: [[1,1,1,1,1,1,3,3,1,1,1,1,1,1],[1,1,1,1,1,3,3,3,3,1,1,1,1,1],[1,1,1,1,1,3,3,3,3,1,1,1,1,1],[1,1,1,1,1,2,2,2,2,1,1,1,1,1],[1,1,1,1,1,2,6,6,2,1,1,1,1,1],[1,1,1,1,1,2,6,6,2,1,1,1,1,1],[1,1,1,1,1,2,2,2,2,1,1,1,1,1],[1,1,1,1,1,2,2,2,2,1,1,1,1,1],[1,1,1,1,3,2,2,2,2,3,1,1,1,1],[1,1,1,3,3,2,2,2,2,3,3,1,1,1],[1,1,1,3,3,5,5,5,5,3,3,1,1,1],[1,1,1,1,5,5,5,5,5,5,1,1,1,1],[1,1,1,1,1,5,5,5,5,1,1,1,1,1],[1,1,1,1,1,1,5,5,1,1,1,1,1,1]] },
  sunset: { pattern: [[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,5,5,5,5,5,5,4,4,4,4,4],[4,4,5,5,5,5,5,5,5,5,4,4,4,4],[4,4,5,5,5,5,5,5,5,5,4,4,4,4],[4,4,4,5,5,5,5,5,5,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[6,6,6,6,6,6,6,6,6,6,6,6,6,6],[6,6,6,6,6,6,6,6,6,6,6,6,6,6],[6,6,6,6,6,6,6,6,6,6,6,6,6,6]] },
  alien: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,2,2,2,2,2,2,4,4,4,4],[4,4,4,2,2,2,2,2,2,2,2,4,4,4],[4,4,2,2,1,1,2,2,1,1,2,2,4,4],[4,4,2,2,1,1,2,2,1,1,2,2,4,4],[4,4,2,2,2,2,2,2,2,2,2,2,4,4],[4,4,4,2,2,1,1,1,1,2,2,4,4,4],[4,4,4,2,1,1,1,1,1,1,2,4,4,4],[4,4,4,4,2,2,2,2,2,2,4,4,4,4],[4,4,4,4,2,4,4,4,4,2,4,4,4,4],[4,4,4,2,2,4,4,4,4,2,2,4,4,4],[4,4,4,2,2,4,4,4,4,2,2,4,4,4]] },
  catNight: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,5,5,4,4,4,4,5,5,4,4,4],[4,4,4,5,5,4,4,4,4,5,5,4,4,4],[4,4,4,5,5,5,4,4,5,5,5,4,4,4],[4,4,4,5,5,5,5,5,5,5,5,4,4,4],[4,4,4,5,5,5,5,5,5,5,5,4,4,4],[4,4,4,5,1,5,5,5,5,1,5,4,4,4],[4,4,4,5,1,5,5,5,5,1,5,4,4,4],[4,4,4,5,5,5,7,7,5,5,5,4,4,4],[4,4,4,5,5,7,7,7,7,5,5,4,4,4],[4,4,4,5,5,5,7,7,5,5,5,4,4,4],[4,4,4,4,5,5,5,5,5,5,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  dog: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,5,5,4,4,4,4,4,4,5,5,4,4],[4,4,5,5,5,4,4,4,4,5,5,5,4,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,4,5,1,1,5,5,1,1,5,4,4,4],[4,4,4,5,1,1,5,5,1,1,5,4,4,4],[4,4,4,5,5,5,3,3,5,5,5,4,4,4],[4,4,4,5,5,3,3,3,3,5,5,4,4,4],[4,4,4,5,5,5,3,3,5,5,5,4,4,4],[4,4,4,4,5,5,5,5,5,5,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  bird: { pattern: [[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,5,5,1,1,1,1,1,1,1],[1,1,1,1,5,5,5,5,1,1,1,1,1,1],[1,1,1,5,5,5,5,5,5,1,1,1,1,1],[1,1,5,5,5,5,5,5,5,5,1,1,1,1],[1,5,5,5,5,5,5,5,5,5,5,1,1,1],[1,5,5,1,5,5,5,5,5,5,5,5,1,1],[5,5,5,1,5,5,5,5,5,5,5,5,5,1],[5,5,5,5,5,5,5,5,5,5,5,5,5,5],[1,5,5,5,5,5,5,5,5,5,5,5,5,1],[1,1,5,5,5,5,5,5,5,5,5,5,1,1],[1,1,1,5,5,5,5,5,5,5,5,1,1,1],[1,1,1,1,5,5,1,1,5,5,1,1,1,1],[1,1,1,1,5,5,1,1,5,5,1,1,1,1]] },
  pig: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,7,7,4,4,4,4,7,7,4,4,4],[4,4,4,7,7,7,4,4,7,7,7,4,4,4],[4,4,7,7,7,7,7,7,7,7,7,7,4,4],[4,4,7,7,7,7,7,7,7,7,7,7,4,4],[4,4,7,7,7,7,7,7,7,7,7,7,4,4],[4,4,7,1,1,7,7,7,7,1,1,7,4,4],[4,4,7,1,1,7,7,7,7,1,1,7,4,4],[4,4,7,7,7,7,3,3,7,7,7,7,4,4],[4,4,7,7,7,3,3,3,3,7,7,7,4,4],[4,4,7,7,7,3,3,3,3,7,7,7,4,4],[4,4,4,7,7,7,7,7,7,7,7,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  cow: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,3,3,4,4,4,4,4,4,3,3,4,4],[4,4,3,3,3,4,4,4,4,3,3,3,4,4],[4,4,6,6,6,6,6,6,6,6,6,6,4,4],[4,4,6,3,6,6,6,6,6,6,3,6,4,4],[4,4,6,6,6,6,6,6,6,6,6,6,4,4],[4,4,6,1,1,6,6,6,6,1,1,6,4,4],[4,4,6,1,1,6,6,6,6,1,1,6,4,4],[4,4,6,6,6,6,7,7,6,6,6,6,4,4],[4,4,6,6,6,7,7,7,7,6,6,6,4,4],[4,4,6,6,6,7,7,7,7,6,6,6,4,4],[4,4,4,6,6,6,6,6,6,6,6,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  horse: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,3,3,4,4,4,4,4],[4,4,4,4,4,4,3,3,3,3,4,4,4,4],[4,4,4,4,4,3,3,3,3,3,3,4,4,4],[4,4,4,4,3,3,3,3,3,3,3,3,4,4],[4,4,4,3,3,3,3,3,3,3,3,3,4,4],[4,4,4,3,3,3,3,3,3,3,3,3,4,4],[4,4,4,3,1,1,3,3,3,3,3,3,4,4],[4,4,4,3,1,1,3,3,3,3,3,3,4,4],[4,4,4,3,3,3,3,7,7,3,3,3,4,4],[4,4,4,3,3,3,7,7,7,7,3,3,4,4],[4,4,4,3,3,3,3,7,7,3,3,3,4,4],[4,4,4,4,3,3,3,3,3,3,3,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  camel: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,5,5,4,4,5,5,4,4,4,4],[4,4,4,5,5,5,5,5,5,5,5,4,4,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,5,1,1,5,5,5,5,5,5,5,4,4],[4,4,5,1,1,5,5,5,5,5,5,5,4,4],[4,4,5,5,5,5,3,3,5,5,5,5,4,4],[4,4,5,5,5,3,3,3,3,5,5,5,4,4],[4,4,5,5,5,5,3,3,5,5,5,5,4,4],[4,4,4,5,5,5,5,5,5,5,5,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  pizza: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,5,5,4,4,4,4,4,4],[4,4,4,4,4,5,5,5,5,4,4,4,4,4],[4,4,4,4,5,5,3,5,5,5,4,4,4,4],[4,4,4,5,5,5,5,5,3,5,5,4,4,4],[4,4,5,5,3,5,5,5,5,5,5,5,4,4],[4,4,5,5,5,5,5,3,5,5,3,5,4,4],[4,5,5,5,3,5,5,5,5,5,5,5,5,4],[4,5,5,5,5,5,5,3,5,5,5,5,5,4],[4,5,5,5,5,5,5,5,5,5,5,5,5,4],[4,4,5,5,5,5,5,5,5,5,5,5,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  cake: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,3,3,4,4,4,4,4,4],[4,4,4,4,4,4,5,5,4,4,4,4,4,4],[4,4,4,4,4,4,5,5,4,4,4,4,4,4],[4,4,4,4,4,3,7,7,3,4,4,4,4,4],[4,4,4,4,4,7,7,7,7,4,4,4,4,4],[4,4,4,4,4,7,7,7,7,4,4,4,4,4],[4,4,4,4,7,7,7,7,7,7,4,4,4,4],[4,4,4,7,7,7,7,7,7,7,7,4,4,4],[4,4,4,7,6,7,7,7,7,6,7,4,4,4],[4,4,7,7,7,7,6,6,7,7,7,7,4,4],[4,4,7,6,7,7,7,7,7,7,6,7,4,4],[4,4,7,7,7,7,7,7,7,7,7,7,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
  cupcake: { pattern: [[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,3,3,4,4,4,4,4,4],[4,4,4,4,4,4,5,5,4,4,4,4,4,4],[4,4,4,4,4,4,5,5,4,4,4,4,4,4],[4,4,4,4,4,7,7,7,7,4,4,4,4,4],[4,4,4,4,7,7,7,7,7,7,4,4,4,4],[4,4,4,7,7,7,7,7,7,7,7,4,4,4],[4,4,4,7,7,6,7,7,6,7,7,4,4,4],[4,4,4,4,7,7,7,7,7,7,4,4,4,4],[4,4,4,4,2,7,7,7,7,2,4,4,4,4],[4,4,4,4,2,2,7,7,2,2,4,4,4,4],[4,4,4,4,4,2,2,2,2,4,4,4,4,4],[4,4,4,4,4,4,4,4,4,4,4,4,4,4]] },
}

const imageKeys = Object.keys(imageTemplates) as Array<keyof typeof imageTemplates>
const currentImageKey = ref<keyof typeof imageTemplates>('robot')
const currentImage = computed(() => imageTemplates[currentImageKey.value])

// Input pixels (random colors)
const inputPixels = computed(() => {
  const pixels: Array<{ colorIndex: number; row: number; col: number }> = []
  for (let row = 0; row < 14; row++) {
    for (let col = 0; col < 14; col++) {
      const colorIndex = (row * 14 + col) % 7 + 1
      pixels.push({ colorIndex, row, col })
    }
  }
  return pixels
})

// Output pixels (target image)
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

// ==================== Click Handler ====================

function handleGridClick(event: MouseEvent) {
  if (clickCooldown.value || props.progress === 0) return

  const grid = inputGridRef.value
  if (!grid) return

  const rect = grid.getBoundingClientRect()
  const cellSize = rect.width / 14
  const col = Math.floor((event.clientX - rect.left) / cellSize)
  const row = Math.floor((event.clientY - rect.top) / cellSize)

  if (row < 0 || row >= 14 || col < 0 || col >= 14) return

  // Find 4-9 nearby unprocessed pixels
  const nearby = findNearbyUnprocessed(row, col, 4, 9)
  if (nearby.length === 0) return

  // Start flying animation
  nearby.forEach(idx => flyingPixels.value.add(idx))
  clickCooldown.value = true

  // After animation, mark as processed
  setTimeout(() => {
    nearby.forEach(idx => {
      flyingPixels.value.delete(idx)
      processedPixels.value.add(idx)
    })
    clickCooldown.value = false
  }, 600)
}

function findNearbyUnprocessed(row: number, col: number, min: number, max: number): number[] {
  const candidates: Array<{ idx: number; dist: number }> = []

  for (let r = 0; r < 14; r++) {
    for (let c = 0; c < 14; c++) {
      const idx = r * 14 + c
      if (processedPixels.value.has(idx) || flyingPixels.value.has(idx)) continue

      const dist = Math.abs(r - row) + Math.abs(c - col)
      candidates.push({ idx, dist })
    }
  }

  candidates.sort((a, b) => a.dist - b.dist)
  const count = Math.min(max, Math.max(min, candidates.length))
  return candidates.slice(0, count).map(c => c.idx)
}

// ==================== Auto-complete at 90% ====================

function autoCompleteRemaining() {
  const remaining: number[] = []
  for (let i = 0; i < 196; i++) {
    if (!processedPixels.value.has(i) && !flyingPixels.value.has(i)) {
      remaining.push(i)
    }
  }

  if (remaining.length === 0) return

  // Fly in batches of 8-12 with stagger
  let delay = 0
  for (let i = 0; i < remaining.length; i += 10) {
    const batch = remaining.slice(i, i + 10)
    setTimeout(() => {
      batch.forEach(idx => flyingPixels.value.add(idx))
      setTimeout(() => {
        batch.forEach(idx => {
          flyingPixels.value.delete(idx)
          processedPixels.value.add(idx)
        })
      }, 600)
    }, delay)
    delay += 150
  }
}

watch(() => props.progress, (newProgress) => {
  if (newProgress >= 90 && !autoCompleted.value) {
    autoCompleted.value = true
    autoCompleteRemaining()
  }
})

// ==================== Styles ====================

function getInputPixelStyle(pixel: { colorIndex: number }, index: number) {
  const color = tokenColors[pixel.colorIndex - 1] ?? '#888'
  const stagger = flyingPixels.value.has(index) ? (index % 5) * 0.03 : 0
  return {
    backgroundColor: color,
    boxShadow: `0 0 6px ${color}80, inset 0 0 3px rgba(255,255,255,0.2)`,
    '--fly-delay': `${stagger}s`
  }
}

function getOutputPixelStyle(pixel: { colorIndex: number }, index: number) {
  const inputPixel = inputPixels.value[index]
  const isFlying = flyingPixels.value.has(index)

  if (isFlying && inputPixel) {
    const fromColor = tokenColors[inputPixel.colorIndex - 1] ?? '#888'
    const toColor = pixel.colorIndex > 0 ? (tokenColors[pixel.colorIndex - 1] ?? '#888') : 'transparent'
    const stagger = (index % 5) * 0.03
    return {
      '--from-color': fromColor,
      '--to-color': toColor,
      '--fly-delay': `${stagger}s`,
      opacity: pixel.colorIndex === 0 ? 0 : 1
    }
  }

  const color = pixel.colorIndex > 0 ? (tokenColors[pixel.colorIndex - 1] ?? '#888') : 'transparent'
  return {
    backgroundColor: color,
    boxShadow: pixel.colorIndex > 0 ? `0 0 8px ${color}80` : 'none',
    opacity: pixel.colorIndex === 0 ? 0 : 1
  }
}

// ==================== Lifecycle ====================

onMounted(() => {
  const randomIndex = Math.floor(Math.random() * imageKeys.length)
  const selectedKey = imageKeys[randomIndex]
  if (selectedKey) currentImageKey.value = selectedKey

  // Hide instructions after 5s
  setTimeout(() => {
    showInstructions.value = false
  }, 5000)
})

// Reset when progress goes to 0
watch(() => props.progress, (newProgress, oldProgress) => {
  if (newProgress === 0 && oldProgress !== 0) {
    processedPixels.value.clear()
    flyingPixels.value.clear()
    autoCompleted.value = false
    showInstructions.value = true
    setTimeout(() => { showInstructions.value = false }, 5000)
  }
})
</script>

<style scoped>
.progress-animation-container {
  width: 100%;
  height: 320px;
  position: relative;
  overflow: hidden;
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

/* Stats bar */
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

/* Instructions */
.instructions-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 150;
  pointer-events: none;
}

.instruction-text {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #0f0;
  text-shadow: 0 0 10px #0f0;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid rgba(0, 255, 0, 0.3);
}

/* Summary box - positioned below the progress bar */
.summary-box {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  background: rgba(0, 0, 0, 0.85);
  padding: 4px 20px;
  border-radius: 6px;
  border: 1px solid rgba(0, 255, 0, 0.4);
  backdrop-filter: blur(8px);
}

.summary-comparison {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #0f0;
  text-shadow: 0 0 8px #0f0;
  white-space: nowrap;
}

/* Fade transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Input Grid */
.input-grid-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 160px;
}

.output-grid-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 160px;
}

/* Canvas Grid */
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

.canvas-grid.clickable {
  cursor: pointer;
}

/* Pixel Token */
.pixel-token {
  width: 10px;
  height: 10px;
  border-radius: 1px;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

/* Input pixels */
.input-grid-container .pixel-token.clickable:hover {
  transform: scale(1.3);
  z-index: 10;
}

.input-grid-container .pixel-token.hidden {
  transform: scale(0);
  opacity: 0;
}

/* Output pixels */
.output-grid-container .pixel-token {
  transform: scale(0);
  opacity: 0;
}

.output-grid-container .pixel-token.visible {
  transform: scale(1);
  opacity: 1;
}

.output-grid-container .pixel-token.flying {
  animation: pixel-fly-from-left 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  animation-delay: var(--fly-delay, 0s);
  animation-fill-mode: forwards;
  z-index: 100;
}

@keyframes pixel-fly-from-left {
  0% {
    transform: translate(-350px, 0) scale(0.7) rotate(0deg);
    background-color: var(--from-color);
    opacity: 1;
    box-shadow: 0 0 25px var(--from-color);
  }
  20% {
    transform: translate(-210px, 0) scale(1.2) rotate(90deg);
    background-color: var(--from-color);
  }
  50% {
    transform: translate(-150px, -8px) scale(1.8) rotate(380deg);
    background-color: color-mix(in srgb, var(--from-color) 50%, var(--to-color) 50%);
  }
  100% {
    transform: translate(0, 0) scale(1) rotate(720deg);
    background-color: var(--to-color);
    box-shadow: 0 0 8px var(--to-color);
  }
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
  box-shadow: 0 0 20px rgba(45, 74, 124, 0.3);
  transition: all 0.3s ease;
}

.processor-box.active {
  border-color: #4a90e2;
  box-shadow: 0 0 40px rgba(74, 144, 226, 0.6);
}

.processor-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  background: radial-gradient(circle, rgba(74, 144, 226, 0.3) 0%, transparent 70%);
  opacity: 0;
}

.processor-box.active .processor-glow {
  opacity: 1;
  animation: processor-flicker 0.8s ease-in-out infinite;
}

@keyframes processor-flicker {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 1; }
}

.processor-core {
  position: relative;
  width: 80%;
  height: 80%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.neural-network {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.network-node {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #4a90e2;
  border-radius: 50%;
  opacity: 0.3;
  box-shadow: 0 0 8px #4a90e2;
}

.node-1 { top: 15%; left: 20%; animation: node-pulse 1.5s ease-in-out infinite; }
.node-2 { top: 50%; left: 10%; animation: node-pulse 1.5s ease-in-out infinite 0.3s; }
.node-3 { top: 80%; left: 25%; animation: node-pulse 1.5s ease-in-out infinite 0.6s; }
.node-4 { top: 30%; right: 20%; animation: node-pulse 1.5s ease-in-out infinite 0.9s; }
.node-5 { top: 70%; right: 15%; animation: node-pulse 1.5s ease-in-out infinite 1.2s; }

.processor-box.active .network-node {
  opacity: 0.8;
  animation-duration: 0.8s;
}

@keyframes node-pulse {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.6); opacity: 1; box-shadow: 0 0 20px #4a90e2; }
}

.network-connection {
  position: absolute;
  background: linear-gradient(90deg, transparent 0%, #4a90e2 50%, transparent 100%);
  height: 1px;
  opacity: 0.2;
}

.conn-1 { top: 25%; left: 20%; width: 60%; transform: rotate(15deg); }
.conn-2 { top: 55%; left: 10%; width: 70%; transform: rotate(-10deg); }
.conn-3 { top: 40%; left: 15%; width: 50%; transform: rotate(45deg); }
.conn-4 { top: 70%; left: 25%; width: 55%; transform: rotate(-20deg); }

.processor-box.active .network-connection {
  opacity: 0.6;
  animation: connection-pulse 1s ease-in-out infinite;
}

@keyframes connection-pulse {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.8; }
}

.processor-icon {
  font-size: 44px;
  animation: processor-icon-pulse 1s ease-in-out infinite;
  filter: drop-shadow(0 0 10px #4a90e2);
  z-index: 10;
}

.processor-box.active .processor-icon {
  animation: processor-icon-active 0.5s ease-in-out infinite;
}

@keyframes processor-icon-pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 0.7; }
}

@keyframes processor-icon-active {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.25) rotate(-3deg); filter: brightness(1.7); }
}

/* Progress Bar */
.progress-bar-container {
  position: absolute;
  bottom: 38px;
  left: 50%;
  transform: translateX(-50%);
  width: 85%;
  max-width: 600px;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db 0%, #2ecc71 50%, #f39c12 100%);
  border-radius: 10px;
  transition: width 0.3s ease-out;
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


/* Responsive */
@media (max-width: 768px) {
  .token-processing-scene {
    gap: 15px;
    padding: 15px 8px;
  }

  .input-grid-container, .output-grid-container {
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
}
</style>
