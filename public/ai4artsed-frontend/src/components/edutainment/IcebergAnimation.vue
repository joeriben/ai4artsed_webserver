<template>
  <div class="iceberg-animation">
    <!-- Climate background (sky, sun, clouds) -->
    <ClimateBackground
      :power-watts="effectivePower"
      :power-limit="gpuStats.power_limit_watts || 600"
      :co2-grams="totalCo2"
      :temperature="effectiveTemp"
    />

    <!-- Water area -->
    <div class="water-area" :style="waterStyle"></div>

    <!-- Iceberg canvas (drawing or display) -->
    <div class="iceberg-container" ref="containerRef">
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


      <!-- Melted/Summary message (shows when all icebergs melted OR progress >= 80%) -->
      <div v-if="state === 'melted' || (props.progress && props.progress >= 80)" class="state-overlay melted">
        <span class="status">{{ t('edutainment.iceberg.melted') }}</span>
        <span class="detail">{{ t('edutainment.iceberg.meltedMessage', { co2: totalCo2.toFixed(2) }) }}</span>
        <span class="comparison">{{ t('edutainment.iceberg.comparison', { volume: iceMeltVolume }) }}</span>
        <span class="comparison-info">{{ t('edutainment.iceberg.comparisonInfo') }}</span>
      </div>
    </div>

    <!-- Stats overlay with labels -->
    <div class="stats-bar">
      <div class="stat" :title="t('edutainment.iceberg.gpuPower')">
        <span class="stat-label">Grafikkarte</span>
        <span class="stat-value">{{ Math.round(effectivePower) }}W / {{ Math.round(effectiveTemp) }}°C</span>
      </div>
      <div class="stat">
        <span class="stat-label">Energie</span>
        <span class="stat-value">{{ (totalEnergy / 1000).toFixed(4) }}kWh</span>
      </div>
      <div class="stat" :title="t('edutainment.iceberg.co2Info')">
        <span class="stat-label">CO₂</span>
        <span class="stat-value">{{ totalCo2.toFixed(1) }}g</span>
      </div>
      <div v-if="estimatedSeconds" class="stat">
        <span class="stat-label">~</span>
        <span class="stat-value">{{ estimatedSeconds }}s</span>
      </div>
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
  estimatedSeconds?: number
}>()

// State
type AnimationState = 'idle' | 'drawing' | 'melting' | 'melted'
const state = ref<AnimationState>('idle')

// Canvas (responsive)
const icebergCanvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const canvasWidth = ref(600)
const canvasHeight = ref(320)
const waterLineY = computed(() => canvasHeight.value * 0.6)

// Smooth ship position (interpolates towards props.progress)
const shipProgress = ref(0)
let shipAnimationId: number | null = null

function animateShip() {
  const target = props.progress ?? 0
  const diff = target - shipProgress.value

  if (Math.abs(diff) > 0.01) {
    // Ease towards target (lerp factor 0.05 = smooth, 0.1 = faster)
    shipProgress.value += diff * 0.08

    // Redraw if not in melting animation (which redraws itself)
    if (state.value !== 'melting') {
      const canvas = icebergCanvasRef.value
      const ctx = canvas?.getContext('2d')
      if (ctx) {
        ctx.clearRect(0, 0, canvas!.width, canvas!.height)
        drawWaterLine(ctx)
        drawShip(ctx)
        for (const iceberg of icebergs.value) {
          drawSingleIceberg(ctx, iceberg)
        }
      }
    }
  }

  shipAnimationId = requestAnimationFrame(animateShip)
}

function resizeCanvas() {
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect()
    canvasWidth.value = Math.floor(rect.width)
  }
}

// Drawing state
const isPointerDown = ref(false)
const currentPath = ref<Point[]>([])

// Iceberg type with polygon and physics
interface Iceberg {
  polygon: Point[]      // Original polygon centered at origin
  x: number             // Position X
  y: number             // Position Y
  angle: number         // Rotation angle
  vx: number            // Velocity X
  vy: number            // Velocity Y
  vAngle: number        // Angular velocity
}

// Multiple icebergs
const icebergs = ref<Iceberg[]>([])

// Physics constants (from iceberger.html - physical formulas are not copyrightable)
const SPECIFIC_GRAVITY = 0.85   // Ice density relative to water (simplified 2D mode)
const TIME_SCALE = 0.5          // Simulation speed (slower for smooth animation)
const DAMPING_AIR = 0.98        // Velocity damping in air
const DAMPING_WATER = 0.94      // Velocity damping in water (more drag)

// GPU stats
const gpuStats = ref<GpuRealtimeStats>({ available: false })
const simulatedPower = ref(200)
const simulatedTemp = ref(55)
const totalCo2 = ref(0)
const totalEnergy = ref(0)
const elapsedSeconds = ref(0)

// Effective values (use simulated when GPU not under load)
const effectivePower = computed(() => {
  const realPower = gpuStats.value.power_draw_watts || 0
  return realPower > 100 ? realPower : simulatedPower.value
})
const effectiveTemp = computed(() => {
  const realTemp = gpuStats.value.temperature_celsius || 0
  const realPower = gpuStats.value.power_draw_watts || 0
  return realPower > 100 ? realTemp : simulatedTemp.value
})

// Arctic ice melt: 1 ton CO2 = ~3m² sea ice loss × ~2m avg thickness = ~6m³
// 1g CO2 = 6 cm³ ice melt
const iceMeltVolume = computed(() => {
  const volumeCm3 = totalCo2.value * 6
  return Math.round(volumeCm3)
})

// Animation
let animationFrameId: number | null = null
let gpuPollInterval: number | null = null
let energyInterval: number | null = null
let lastFrameTime = 0

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
 * Transform polygon by iceberg's physics state (position + rotation)
 */
function getTransformedPolygon(iceberg: Iceberg): Point[] {
  const { x, y, angle, polygon } = iceberg
  const cos = Math.cos(angle)
  const sin = Math.sin(angle)

  return polygon.map(p => ({
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
 * Apply physics forces to a single iceberg
 * Physics from iceberger.html (formulas are not copyrightable)
 */
function updateIcebergPhysics(iceberg: Iceberg, dtScale: number) {
  const polygon = getTransformedPolygon(iceberg)
  if (polygon.length < 3) return

  const totalArea = calculateArea(polygon)
  if (totalArea < 10) return

  const pc = calculateCentroid(polygon)
  const submerged = getSubmergedPolygon(polygon)
  const submergedArea = calculateArea(submerged)
  const submergedRatio = submergedArea / totalArea

  // Forces (normalized to area)
  let forceY = 1  // Gravity: normalized downward force
  const fb = submergedRatio / SPECIFIC_GRAVITY  // Buoyancy factor
  forceY -= fb  // Net vertical force

  // Torque: fb * (submerged_centroid.x - full_centroid.x)
  // This creates rotation towards equilibrium
  let torque = 0
  if (submergedArea > 0 && submerged.length >= 3) {
    const pcSubmerged = calculateCentroid(submerged)
    torque = fb * (pcSubmerged.x - pc.x)  // No clamping - let physics work
  }

  // Rotational inertia proportional to area
  // Original formula sqrt(area)/1000000 is for different coordinate scale
  // Calibrated for our canvas size (~500x320)
  const rotationalInertia = Math.sqrt(totalArea) * 0.5

  // Apply forces to velocity
  iceberg.vy += forceY * TIME_SCALE * dtScale
  iceberg.vAngle += (torque / rotationalInertia) * TIME_SCALE * dtScale

  // Damping (interpolate air/water)
  const baseDamping = DAMPING_AIR * (1 - submergedRatio) + DAMPING_WATER * submergedRatio
  const damping = Math.pow(baseDamping, dtScale)
  const rotDamping = Math.pow(baseDamping - 0.1, dtScale)  // Stronger rotation damping

  iceberg.vx *= damping
  iceberg.vy *= damping
  iceberg.vAngle *= Math.max(0.5, rotDamping)

  // Update position
  iceberg.x += iceberg.vx * dtScale
  iceberg.y += iceberg.vy * dtScale
  iceberg.angle += iceberg.vAngle * dtScale

  // Soft bounds
  const minY = 30
  const maxY = canvasHeight.value - 30
  if (iceberg.y < minY) iceberg.vy += (minY - iceberg.y) * 0.02 * dtScale
  if (iceberg.y > maxY) iceberg.vy -= (iceberg.y - maxY) * 0.02 * dtScale
}

/**
 * Update physics for all icebergs
 */
function updateAllPhysics(dt: number) {
  const dtScale = Math.min(dt, 100) / 50
  for (const iceberg of icebergs.value) {
    updateIcebergPhysics(iceberg, dtScale)
  }
}

/**
 * Create new iceberg from drawn polygon
 */
function createIceberg(drawnPolygon: Point[]): Iceberg {
  const centroid = calculateCentroid(drawnPolygon)
  return {
    polygon: drawnPolygon.map(p => ({
      x: p.x - centroid.x,
      y: p.y - centroid.y
    })),
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

    // Use real GPU values if available and under load, otherwise simulate
    const realPower = gpuStats.value.power_draw_watts || 0
    const realTemp = gpuStats.value.temperature_celsius || 0
    const isGpuActive = realPower > 100  // GPU considered active above 100W

    // Simulation ramps up over time to demonstrate the effect
    simulatedPower.value = Math.min(450, 150 + elapsedSeconds.value * 15 + Math.random() * 50)
    simulatedTemp.value = Math.min(82, 45 + elapsedSeconds.value * 2 + Math.random() * 3)

    const watts = isGpuActive ? realPower : simulatedPower.value
    const temp = isGpuActive ? realTemp : simulatedTemp.value
    const co2PerKwh = gpuStats.value.co2_per_kwh_grams || 400

    const whThisSecond = watts / 3600
    totalEnergy.value += whThisSecond
    totalCo2.value += (whThisSecond / 1000) * co2PerKwh
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
  // Allow drawing anytime - keep existing icebergs

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
      // Add new iceberg to the array (keep existing ones)
      icebergs.value.push(createIceberg(simplified))
      // Start melting if not already
      if (state.value !== 'melting') {
        startMelting()
      }
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
  drawShip(ctx)
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

/**
 * Draw a small ship on the horizon based on progress (0-100%)
 */
function drawShip(ctx: CanvasRenderingContext2D) {
  const canvas = icebergCanvasRef.value
  if (!canvas) return

  // Use smoothed shipProgress for animation
  const progress = shipProgress.value
  if (progress <= 0.1) return

  const shipWidth = 24
  const shipHeight = 16
  const margin = 20

  // Ship position: left edge at 0%, right edge at 100%
  const x = margin + (progress / 100) * (canvas.width - 2 * margin - shipWidth)
  const y = waterLineY.value - shipHeight / 2

  ctx.save()

  // Hull (dark brown boat shape)
  ctx.beginPath()
  ctx.moveTo(x, y + shipHeight * 0.4)
  ctx.lineTo(x + shipWidth * 0.15, y + shipHeight)
  ctx.lineTo(x + shipWidth * 0.85, y + shipHeight)
  ctx.lineTo(x + shipWidth, y + shipHeight * 0.4)
  ctx.closePath()
  ctx.fillStyle = '#5D4037'
  ctx.fill()

  // Mast
  const mastX = x + shipWidth * 0.45
  ctx.beginPath()
  ctx.moveTo(mastX, y + shipHeight * 0.4)
  ctx.lineTo(mastX, y - shipHeight * 0.6)
  ctx.strokeStyle = '#4E342E'
  ctx.lineWidth = 2
  ctx.stroke()

  // Sail (white triangle)
  ctx.beginPath()
  ctx.moveTo(mastX + 1, y - shipHeight * 0.5)
  ctx.lineTo(mastX + shipWidth * 0.45, y + shipHeight * 0.2)
  ctx.lineTo(mastX + 1, y + shipHeight * 0.3)
  ctx.closePath()
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
  ctx.fill()

  ctx.restore()
}

function drawCurrentPath() {
  const canvas = icebergCanvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!ctx || !canvas) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawWaterLine(ctx)
  drawShip(ctx)

  // Draw existing icebergs first
  for (const iceberg of icebergs.value) {
    drawSingleIceberg(ctx, iceberg)
  }

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

function drawSingleIceberg(ctx: CanvasRenderingContext2D, iceberg: Iceberg) {
  const polygon = getTransformedPolygon(iceberg)
  if (polygon.length < 3) return

  const firstPoint = polygon[0]
  if (!firstPoint) return

  // Draw underwater portion
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
    if (point) ctx.lineTo(point.x, point.y)
  }
  ctx.closePath()

  const centroid = calculateCentroid(polygon)
  const gradient = ctx.createRadialGradient(centroid.x, centroid.y, 0, centroid.x, centroid.y, 100)
  gradient.addColorStop(0, 'rgba(230, 245, 255, 0.95)')
  gradient.addColorStop(0.5, 'rgba(200, 230, 255, 0.9)')
  gradient.addColorStop(1, 'rgba(150, 200, 255, 0.85)')

  ctx.fillStyle = gradient
  ctx.fill()
  ctx.strokeStyle = 'rgba(100, 180, 220, 0.8)'
  ctx.lineWidth = 2
  ctx.stroke()
}

function drawAllIcebergs() {
  const canvas = icebergCanvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!ctx || !canvas) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawWaterLine(ctx)
  drawShip(ctx)

  for (const iceberg of icebergs.value) {
    drawSingleIceberg(ctx, iceberg)
  }
}

// ==================== Continuous Physics Animation (after drawing) ====================

// ==================== Melting Animation ====================

function startMelting() {
  if (state.value === 'melting') return  // Already running, don't reset values

  state.value = 'melting'
  // Don't reset CO2/energy - they accumulate across the session
  // Only reset time and temp for new session
  if (elapsedSeconds.value === 0) {
    simulatedTemp.value = 55
  }

  startGpuPolling()
  lastFrameTime = performance.now()
  animationLoop()
}

function animationLoop() {
  if (state.value !== 'melting') return

  const now = performance.now()
  const dt = Math.min(now - lastFrameTime, 100)
  lastFrameTime = now

  // Use effective temperature (simulated when GPU idle)
  const temp = effectiveTemp.value

  // Melt and update physics for each iceberg
  for (const iceberg of icebergs.value) {
    meltIcebergPolygon(iceberg, temp, dt)
  }
  updateAllPhysics(dt)

  // Remove fully melted icebergs
  icebergs.value = icebergs.value.filter(iceberg =>
    calculateArea(iceberg.polygon) >= 50
  )

  // Redraw
  drawAllIcebergs()

  // Check if all melted
  if (icebergs.value.length === 0) {
    state.value = 'melted'
    stopGpuPolling()
    stopAnimation()
    return
  }

  animationFrameId = requestAnimationFrame(animationLoop)
}

/**
 * Melt a single iceberg's polygon
 */
function meltIcebergPolygon(iceberg: Iceberg, temp: number, dt: number) {
  if (iceberg.polygon.length < 3) return

  const MELT_THRESHOLD = 45
  if (temp < MELT_THRESHOLD) return

  const tempAboveThreshold = temp - MELT_THRESHOLD
  const meltRate = (tempAboveThreshold / 40) * (dt / 16.67) * 0.002  // 50% slower

  iceberg.polygon = iceberg.polygon.map(point => {
    const worldY = iceberg.y + point.y
    const isAboveWater = worldY < waterLineY.value
    const meltMultiplier = isAboveWater ? 2.0 : 1.0
    const factor = 1 - meltRate * meltMultiplier

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
  stopGpuPolling()

  state.value = 'idle'
  icebergs.value = []
  currentPath.value = []
  totalCo2.value = 0
  totalEnergy.value = 0
  elapsedSeconds.value = 0
  simulatedTemp.value = 55

  clearCanvas()
}

// ==================== Lifecycle ====================

watch(() => props.progress, (newProgress) => {
  if (newProgress && newProgress > 0) {
    // Auto-start energy tracking when progress begins (for use without drawing)
    if (!energyInterval) {
      startGpuPolling()
    }
  }
  // Ship position is now smoothly animated via animateShip()
})

onMounted(() => {
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  // Wait for next tick to ensure canvas is sized
  setTimeout(() => clearCanvas(), 10)
  fetchGpuStats()
  // Start smooth ship animation
  animateShip()
})

onUnmounted(() => {
  stopAnimation()
  stopGpuPolling()
  window.removeEventListener('resize', resizeCanvas)
  // Stop ship animation
  if (shipAnimationId) {
    cancelAnimationFrame(shipAnimationId)
    shipAnimationId = null
  }
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
  top: 40%;
  pointer-events: none;
}

.instruction {
  color: #1a5276;
  font-size: 16px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  font-weight: 400;
  letter-spacing: 0.5px;
  line-height: 1.6;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  max-width: 300px;
}

.status {
  display: block;
  color: #1a5276;
  font-size: 18px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  margin-bottom: 10px;
}

.detail {
  display: block;
  color: #1a5276;
  font-size: 15px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.comparison {
  display: block;
  color: #1a5276;
  font-size: 14px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  margin-bottom: 5px;
}

.comparison-info {
  display: block;
  color: #1a5276;
  font-size: 11px;
  font-family: 'Georgia', 'Times New Roman', serif;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  opacity: 0.7;
  margin-bottom: 15px;
}

.hint {
  display: block;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin-top: 10px;
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
  pointer-events: none; /* Don't interrupt drawing */
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #fff;
  font-weight: bold;
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
