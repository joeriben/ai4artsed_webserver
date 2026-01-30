<template>
  <div class="iceberg-animation">
    <!-- Climate background (sky, sun, clouds) -->
    <ClimateBackground
      :power-watts="gpuStats.power_draw_watts || simulatedPower"
      :power-limit="gpuStats.power_limit_watts || 600"
      :co2-grams="totalCo2"
      :temperature="gpuStats.temperature_celsius || simulatedTemp"
    />

    <!-- Water area -->
    <div class="water-area" :style="waterStyle"></div>

    <!-- Iceberg canvas (drawing or display) -->
    <div class="iceberg-container">
      <canvas
        ref="icebergCanvasRef"
        :width="canvasWidth"
        :height="canvasHeight"
        @pointerdown="handlePointerDown"
        @pointermove="handlePointerMove"
        @pointerup="handlePointerUp"
        @pointerleave="handlePointerUp"
        :class="{ drawing: state === 'drawing' && isPointerDown }"
      />

      <!-- Drawing instructions -->
      <div v-if="state === 'idle'" class="state-overlay">
        <span class="instruction">{{ t('edutainment.iceberg.drawPrompt') }}</span>
      </div>

      <!-- Melting indicator -->
      <div v-if="state === 'melting'" class="state-overlay melting">
        <span class="status">{{ t('edutainment.iceberg.melting') }}</span>
      </div>

      <!-- Melted message -->
      <div v-if="state === 'melted'" class="state-overlay melted">
        <span class="status">{{ t('edutainment.iceberg.melted') }}</span>
        <span class="detail">{{ t('edutainment.iceberg.meltedMessage', { co2: totalCo2.toFixed(2) }) }}</span>
        <button class="restart-btn" @click="resetAnimation">{{ t('edutainment.iceberg.redraw') }}</button>
      </div>
    </div>

    <!-- Stats overlay -->
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-icon">⚡</span>
        <span class="stat-value">{{ Math.round(gpuStats.power_draw_watts || simulatedPower) }}W</span>
      </div>
      <div class="stat">
        <span class="stat-icon">🌡️</span>
        <span class="stat-value">{{ gpuStats.temperature_celsius || simulatedTemp }}°C</span>
      </div>
      <div class="stat">
        <span class="stat-icon">☁️</span>
        <span class="stat-value">{{ totalCo2.toFixed(2) }}g CO₂</span>
      </div>
      <div class="stat">
        <span class="stat-icon">⏱️</span>
        <span class="stat-value">{{ elapsedSeconds }}s</span>
      </div>
    </div>

    <!-- Control buttons (when iceberg is drawn) -->
    <div v-if="state === 'drawn'" class="controls">
      <button class="start-btn" @click="startMelting">
        {{ t('edutainment.iceberg.startMelting') }}
      </button>
      <button class="clear-btn" @click="resetAnimation">
        {{ t('edutainment.iceberg.redraw') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ClimateBackground from './ClimateBackground.vue'
import {
  type Point,
  simplifyPolygon,
  meltIceberg,
  calculateArea,
  calculateCentroid,
  isMelted
} from '@/composables/useIcebergPhysics'
import type { GpuRealtimeStats } from '@/composables/useEdutainmentFacts'

const { t } = useI18n()

// Props
const props = defineProps<{
  autoStart?: boolean
  progress?: number
}>()

// State
type AnimationState = 'idle' | 'drawing' | 'drawn' | 'melting' | 'melted'
const state = ref<AnimationState>('idle')

// Canvas
const icebergCanvasRef = ref<HTMLCanvasElement | null>(null)
const canvasWidth = ref(500)
const canvasHeight = ref(320)
const waterLineY = computed(() => canvasHeight.value * 0.6)

// Drawing state
const isPointerDown = ref(false)
const currentPath = ref<Point[]>([])
const icebergPolygon = ref<Point[]>([])

// Physics state
const physicsState = ref({
  x: 0,           // Center position X
  y: 0,           // Center position Y
  angle: 0,       // Rotation angle in radians
  vx: 0,          // Velocity X
  vy: 0,          // Velocity Y
  vAngle: 0       // Angular velocity
})

// Physics constants
const GRAVITY = 0.15
const BUOYANCY_FACTOR = 0.18  // Upward force per submerged pixel
const WATER_DENSITY = 0.92    // Ice is less dense than water (floats ~10% above)
const DAMPING = 0.98          // Velocity damping
const ANGULAR_DAMPING = 0.95  // Angular velocity damping
const TORQUE_FACTOR = 0.00008 // How much offset creates rotation

// GPU stats
const gpuStats = ref<GpuRealtimeStats>({ available: false })
const simulatedPower = ref(200)
const simulatedTemp = ref(55)
const totalCo2 = ref(0)
const totalEnergy = ref(0)
const elapsedSeconds = ref(0)

// Animation
let animationFrameId: number | null = null
let gpuPollInterval: number | null = null
let energyInterval: number | null = null
let lastFrameTime = 0

// Original polygon (before transforms)
const originalPolygon = ref<Point[]>([])

// Water color based on temperature/energy
const waterStyle = computed(() => {
  const warmth = Math.min(1, totalEnergy.value / 10)
  const r = Math.round(0 + warmth * 50)
  const g = Math.round(100 - warmth * 30)
  const b = Math.round(200 - warmth * 50)
  return {
    background: `linear-gradient(180deg,
      rgba(${r}, ${g}, ${b}, 0.6) 0%,
      rgba(${r - 20}, ${g - 20}, ${b + 20}, 0.8) 100%)`
  }
})

// ==================== Physics Engine ====================

/**
 * Transform polygon by current physics state (position + rotation)
 */
function getTransformedPolygon(): Point[] {
  const { x, y, angle } = physicsState.value
  const cos = Math.cos(angle)
  const sin = Math.sin(angle)

  return originalPolygon.value.map(p => ({
    x: x + p.x * cos - p.y * sin,
    y: y + p.x * sin + p.y * cos
  }))
}

/**
 * Calculate submerged portion of polygon
 */
function getSubmergedPolygon(polygon: Point[]): Point[] {
  const submerged: Point[] = []
  const wl = waterLineY.value

  for (let i = 0; i < polygon.length; i++) {
    const curr = polygon[i]
    const next = polygon[(i + 1) % polygon.length]
    if (!curr || !next) continue

    // Current point is underwater
    if (curr.y >= wl) {
      submerged.push(curr)
    }

    // Edge crosses water line
    if ((curr.y < wl && next.y >= wl) || (curr.y >= wl && next.y < wl)) {
      // Interpolate crossing point
      const t = (wl - curr.y) / (next.y - curr.y)
      submerged.push({
        x: curr.x + t * (next.x - curr.x),
        y: wl
      })
    }
  }

  return submerged
}

/**
 * Apply physics forces and update state
 */
function updatePhysics(dt: number) {
  const dtSeconds = dt / 1000
  const state = physicsState.value

  // Get current transformed polygon
  const polygon = getTransformedPolygon()
  if (polygon.length < 3) return

  // Calculate centers
  const massCentroid = calculateCentroid(polygon)
  const submerged = getSubmergedPolygon(polygon)
  const submergedArea = calculateArea(submerged)
  const totalArea = calculateArea(polygon)

  // Apply gravity (downward force at center of mass)
  state.vy += GRAVITY * dtSeconds * 60

  // Apply buoyancy (upward force proportional to submerged volume)
  if (submergedArea > 0 && submerged.length >= 3) {
    const buoyancyCentroid = calculateCentroid(submerged)
    const buoyancyForce = submergedArea * BUOYANCY_FACTOR * dtSeconds * 60 / WATER_DENSITY

    state.vy -= buoyancyForce / Math.max(1, totalArea / 100)

    // Calculate torque from offset between mass center and buoyancy center
    const offsetX = buoyancyCentroid.x - massCentroid.x
    const torque = offsetX * buoyancyForce * TORQUE_FACTOR
    state.vAngle += torque
  }

  // Apply damping
  state.vx *= DAMPING
  state.vy *= DAMPING
  state.vAngle *= ANGULAR_DAMPING

  // Update position and angle
  state.x += state.vx * dtSeconds * 60
  state.y += state.vy * dtSeconds * 60
  state.angle += state.vAngle * dtSeconds * 60

  // Keep iceberg roughly centered horizontally
  if (state.x < -50) state.x = -50
  if (state.x > 50) state.x = 50

  // Prevent sinking too deep or flying away
  const minY = -100
  const maxY = canvasHeight.value * 0.3
  if (state.y < minY) {
    state.y = minY
    state.vy = 0
  }
  if (state.y > maxY) {
    state.y = maxY
    state.vy *= -0.3 // Bounce slightly
  }
}

/**
 * Initialize physics from drawn polygon
 */
function initializePhysics() {
  const polygon = icebergPolygon.value
  if (polygon.length < 3) return

  // Calculate initial centroid
  const centroid = calculateCentroid(polygon)

  // Center polygon around origin for rotation
  originalPolygon.value = polygon.map(p => ({
    x: p.x - centroid.x,
    y: p.y - centroid.y
  }))

  // Set initial position at centroid
  physicsState.value = {
    x: centroid.x,
    y: centroid.y,
    angle: 0,
    vx: 0,
    vy: 0,
    vAngle: 0
  }
}

// ==================== GPU Data ====================

async function fetchGpuStats() {
  try {
    const response = await fetch('/api/settings/gpu-realtime')
    if (response.ok) {
      gpuStats.value = await response.json()
    }
  } catch (error) {
    console.warn('[IcebergAnimation] GPU fetch failed:', error)
  }
}

function startGpuPolling() {
  fetchGpuStats()
  gpuPollInterval = window.setInterval(fetchGpuStats, 2000)

  energyInterval = window.setInterval(() => {
    elapsedSeconds.value++
    const watts = gpuStats.value.power_draw_watts || simulatedPower.value
    const co2PerKwh = gpuStats.value.co2_per_kwh_grams || 400

    const whThisSecond = watts / 3600
    totalEnergy.value += whThisSecond
    totalCo2.value += (whThisSecond / 1000) * co2PerKwh

    simulatedPower.value = 180 + Math.random() * 120
    simulatedTemp.value = Math.min(85, simulatedTemp.value + Math.random() * 0.3)
  }, 1000)
}

function stopGpuPolling() {
  if (gpuPollInterval) {
    clearInterval(gpuPollInterval)
    gpuPollInterval = null
  }
  if (energyInterval) {
    clearInterval(energyInterval)
    energyInterval = null
  }
}

// ==================== Drawing ====================

function handlePointerDown(event: PointerEvent) {
  if (state.value !== 'idle' && state.value !== 'drawing') return

  state.value = 'drawing'
  isPointerDown.value = true
  currentPath.value = []

  const point = getCanvasPoint(event)
  currentPath.value.push(point)

  ;(event.target as HTMLCanvasElement).setPointerCapture(event.pointerId)
}

function handlePointerMove(event: PointerEvent) {
  if (!isPointerDown.value) return

  const point = getCanvasPoint(event)
  const lastPoint = currentPath.value[currentPath.value.length - 1]

  if (lastPoint) {
    const dist = Math.sqrt((point.x - lastPoint.x) ** 2 + (point.y - lastPoint.y) ** 2)
    if (dist > 3) {
      currentPath.value.push(point)
      drawCurrentPath()
    }
  }
}

function handlePointerUp(event: PointerEvent) {
  if (!isPointerDown.value) return

  isPointerDown.value = false
  ;(event.target as HTMLCanvasElement).releasePointerCapture(event.pointerId)

  if (currentPath.value.length >= 5) {
    const simplified = simplifyPolygon(currentPath.value, 3)
    if (simplified.length >= 3) {
      icebergPolygon.value = simplified
      initializePhysics()
      state.value = 'drawn'
      // Start physics immediately for the "settling" effect
      lastFrameTime = performance.now()
      settleAnimation()
      return
    }
  }

  state.value = 'idle'
  clearCanvas()
}

function getCanvasPoint(event: PointerEvent): Point {
  const canvas = icebergCanvasRef.value
  if (!canvas) return { x: 0, y: 0 }

  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height

  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY
  }
}

// ==================== Rendering ====================

function clearCanvas() {
  const canvas = icebergCanvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!ctx || !canvas) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawWaterLine(ctx)
}

function drawWaterLine(ctx: CanvasRenderingContext2D) {
  const canvas = icebergCanvasRef.value
  if (!canvas) return

  ctx.setLineDash([8, 4])
  ctx.beginPath()
  ctx.moveTo(0, waterLineY.value)
  ctx.lineTo(canvas.width, waterLineY.value)
  ctx.strokeStyle = 'rgba(100, 180, 255, 0.4)'
  ctx.lineWidth = 2
  ctx.stroke()
  ctx.setLineDash([])
}

function drawCurrentPath() {
  const canvas = icebergCanvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!ctx || !canvas) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawWaterLine(ctx)

  if (currentPath.value.length < 2) return

  const firstPoint = currentPath.value[0]
  if (!firstPoint) return

  ctx.beginPath()
  ctx.moveTo(firstPoint.x, firstPoint.y)
  for (let i = 1; i < currentPath.value.length; i++) {
    const point = currentPath.value[i]
    if (point) {
      ctx.lineTo(point.x, point.y)
    }
  }
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.stroke()

  ctx.beginPath()
  ctx.arc(firstPoint.x, firstPoint.y, 5, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
  ctx.fill()
}

function drawIceberg() {
  const canvas = icebergCanvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!ctx || !canvas) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawWaterLine(ctx)

  // Get transformed polygon with physics
  const polygon = getTransformedPolygon()
  if (polygon.length < 3) return

  const firstPoint = polygon[0]
  if (!firstPoint) return

  // Draw underwater portion with different color
  const submerged = getSubmergedPolygon(polygon)
  if (submerged.length >= 3) {
    const subFirst = submerged[0]
    if (subFirst) {
      ctx.beginPath()
      ctx.moveTo(subFirst.x, subFirst.y)
      for (let i = 1; i < submerged.length; i++) {
        const p = submerged[i]
        if (p) ctx.lineTo(p.x, p.y)
      }
      ctx.closePath()
      ctx.fillStyle = 'rgba(100, 180, 220, 0.4)'
      ctx.fill()
    }
  }

  // Draw full iceberg
  ctx.beginPath()
  ctx.moveTo(firstPoint.x, firstPoint.y)
  for (let i = 1; i < polygon.length; i++) {
    const point = polygon[i]
    if (point) {
      ctx.lineTo(point.x, point.y)
    }
  }
  ctx.closePath()

  // Gradient fill
  const centroid = calculateCentroid(polygon)
  const gradient = ctx.createRadialGradient(
    centroid.x, centroid.y, 0,
    centroid.x, centroid.y, 100
  )
  gradient.addColorStop(0, 'rgba(230, 245, 255, 0.95)')
  gradient.addColorStop(0.5, 'rgba(200, 230, 255, 0.9)')
  gradient.addColorStop(1, 'rgba(150, 200, 255, 0.85)')

  ctx.fillStyle = gradient
  ctx.fill()

  ctx.strokeStyle = 'rgba(100, 180, 220, 0.8)'
  ctx.lineWidth = 2
  ctx.stroke()
}

// ==================== Settling Animation (after drawing) ====================

let settleFrameId: number | null = null

function settleAnimation() {
  const now = performance.now()
  const dt = now - lastFrameTime
  lastFrameTime = now

  updatePhysics(dt)
  drawIceberg()

  // Continue settling until velocities are very small
  const { vx, vy, vAngle } = physicsState.value
  const isSettled = Math.abs(vx) < 0.01 && Math.abs(vy) < 0.01 && Math.abs(vAngle) < 0.001

  if (!isSettled && state.value === 'drawn') {
    settleFrameId = requestAnimationFrame(settleAnimation)
  }
}

function stopSettling() {
  if (settleFrameId) {
    cancelAnimationFrame(settleFrameId)
    settleFrameId = null
  }
}

// ==================== Melting Animation ====================

function startMelting() {
  if (state.value !== 'drawn') return

  stopSettling()
  state.value = 'melting'
  totalCo2.value = 0
  totalEnergy.value = 0
  elapsedSeconds.value = 0
  simulatedTemp.value = 55

  startGpuPolling()
  lastFrameTime = performance.now()
  animationLoop()
}

function animationLoop() {
  if (state.value !== 'melting') return

  const now = performance.now()
  const dt = now - lastFrameTime
  lastFrameTime = now

  const temp = gpuStats.value.temperature_celsius || simulatedTemp.value

  // Melt the original polygon (shrink towards center)
  originalPolygon.value = meltPolygonAtOrigin(originalPolygon.value, temp, dt)

  // Update physics
  updatePhysics(dt)

  // Redraw
  drawIceberg()

  // Check if melted
  if (calculateArea(originalPolygon.value) < 50) {
    state.value = 'melted'
    stopGpuPolling()
    stopAnimation()
    return
  }

  animationFrameId = requestAnimationFrame(animationLoop)
}

/**
 * Melt polygon centered at origin
 */
function meltPolygonAtOrigin(polygon: Point[], temp: number, dt: number): Point[] {
  if (polygon.length < 3) return polygon

  const baseMeltRate = (temp / 1000) * (dt / 16.67) * 0.002

  return polygon.map(point => {
    // Points "above" water (negative Y in local coords relative to water line offset)
    const worldY = physicsState.value.y + point.y
    const isAboveWater = worldY < waterLineY.value
    const meltMultiplier = isAboveWater ? 1.5 : 1.0

    const factor = 1 - baseMeltRate * meltMultiplier

    return {
      x: point.x * factor,
      y: point.y * factor
    }
  })
}

function stopAnimation() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

function resetAnimation() {
  stopAnimation()
  stopSettling()
  stopGpuPolling()

  state.value = 'idle'
  icebergPolygon.value = []
  originalPolygon.value = []
  currentPath.value = []
  totalCo2.value = 0
  totalEnergy.value = 0
  elapsedSeconds.value = 0
  simulatedTemp.value = 55
  physicsState.value = { x: 0, y: 0, angle: 0, vx: 0, vy: 0, vAngle: 0 }

  clearCanvas()
}

// ==================== Lifecycle ====================

watch(() => props.progress, (newProgress) => {
  if (props.autoStart && newProgress && newProgress > 0 && state.value === 'idle') {
    // Auto-start with a default iceberg if progress starts
  }
})

onMounted(() => {
  clearCanvas()
  fetchGpuStats()
})

onUnmounted(() => {
  stopAnimation()
  stopSettling()
  stopGpuPolling()
})
</script>

<style scoped>
.iceberg-animation {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
  background: #0a1628;
}

/* Water */
.water-area {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  transition: background 1s ease;
}

/* Iceberg canvas container */
.iceberg-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.iceberg-container canvas {
  cursor: crosshair;
  touch-action: none;
}

.iceberg-container canvas.drawing {
  cursor: none;
}

/* State overlays */
.state-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  z-index: 10;
}

.state-overlay.melted {
  pointer-events: auto;
}

.instruction {
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  font-family: system-ui, sans-serif;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  background: rgba(0, 0, 0, 0.4);
  padding: 12px 24px;
  border-radius: 8px;
}

.status {
  display: block;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  margin-bottom: 10px;
}

.detail {
  display: block;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin-bottom: 15px;
}

.restart-btn {
  padding: 10px 20px;
  background: rgba(100, 180, 255, 0.8);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.restart-btn:hover {
  background: rgba(100, 180, 255, 1);
}

/* Stats bar */
.stats-bar {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
  background: rgba(0, 0, 0, 0.5);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

.stat {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-icon {
  font-size: 14px;
}

.stat-value {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #fff;
}

/* Controls */
.controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
}

.start-btn {
  padding: 8px 16px;
  background: rgba(80, 200, 120, 0.9);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.start-btn:hover {
  background: rgba(80, 200, 120, 1);
}

.clear-btn {
  padding: 8px 16px;
  background: rgba(255, 100, 100, 0.8);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: rgba(255, 100, 100, 1);
}
</style>
