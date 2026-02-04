<template>
  <div ref="containerRef" class="forest-game-canvas">
    <canvas
      ref="canvasRef"
      @click="handleClick"
    ></canvas>

    <!-- UI Overlays (same as original) -->
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-label">{{ t('edutainment.pixel.grafikkarte') }}</span>
        <span class="stat-value">{{ Math.round(effectivePower) }}W / {{ Math.round(effectiveTemp) }}°C</span>
      </div>
      <div class="stat">
        <span class="stat-label">{{ t('edutainment.forest.trees') }}</span>
        <span class="stat-value">{{ trees.length }} 🌳</span>
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

    <!-- Plant instruction / Cooldown -->
    <Transition name="fade">
      <div v-if="showInstructions" class="plant-instruction" :class="{ cooldown: plantCooldown > 0 }">
        <template v-if="treesPlanted === 0">
          {{ t('edutainment.forest.clickToPlant') }}
        </template>
        <template v-else-if="plantCooldown > 0">
          ⏳ {{ plantCooldown.toFixed(1) }}s
        </template>
      </div>
    </Transition>

    <!-- Game over -->
    <div v-if="gameOver" class="game-over">
      <div class="game-over-text">{{ t('edutainment.forest.gameOver') }}</div>
      <div class="game-over-co2">{{ totalCo2.toFixed(1) }}g CO₂</div>
      <div class="game-over-comparison">
        {{ t('edutainment.forest.comparison', { minutes: treeMinutes }) }}
      </div>
      <div class="game-over-stats">
        {{ t('edutainment.forest.treesPlanted', { count: treesPlanted }) }}
      </div>
    </div>

    <!-- Summary -->
    <Transition name="fade">
      <div v-if="!gameOver && isShowingSummary" class="summary-box">
        <span class="summary-detail">{{ totalCo2.toFixed(2) }}g CO₂</span>
        <span class="summary-comparison">{{ t('edutainment.forest.comparison', { minutes: treeMinutes }) }}</span>
        <span class="summary-trees">{{ t('edutainment.forest.treesPlanted', { count: treesPlanted }) }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAnimationProgress } from '@/composables/useAnimationProgress'
import { useCanvasRenderer } from '@/composables/useCanvasRenderer'
import { useGameLoop } from '@/composables/useGameLoop'
import { useCanvasDrawing } from '@/composables/useCanvasDrawing'
import { useCanvasObjects, type CanvasObject } from '@/composables/useCanvasObjects'

const { t } = useI18n()

const props = defineProps<{
  progress?: number
  estimatedSeconds?: number
}>()

// ==================== Animation Progress ====================
const {
  internalProgress,
  summaryShown,
  totalCo2,
  effectivePower,
  effectiveTemp,
  treeMinutes
} = useAnimationProgress({
  estimatedSeconds: computed(() => props.estimatedSeconds || 30),
  isActive: computed(() => (props.progress ?? 0) > 0)
})

const isShowingSummary = computed(() => summaryShown.value)
const showInstructions = ref(true)

// ==================== Tree Types ====================
const TREE_TYPES = ['pine', 'spruce', 'fir', 'oak', 'birch', 'maple', 'willow'] as const
type TreeType = typeof TREE_TYPES[number]

interface Tree extends CanvasObject {
  type: TreeType
  scale: number
  growing: boolean
  growthProgress: number
}

interface Factory extends CanvasObject {
  scale: number
  smoke: SmokeParticle[]
}

interface SmokeParticle {
  x: number
  y: number
  vy: number
  opacity: number
  life: number
}

interface Cloud {
  x: number
  y: number
  radius: number
  opacity: number
  color: string
}

// ==================== State ====================
const { objects: trees, addObject: addTree, clear: clearTrees } = useCanvasObjects<Tree>()
const { objects: factories, addObject: addFactory, clear: clearFactories } = useCanvasObjects<Factory>()

const plantCooldown = ref(0)
const treesPlanted = ref(0)
const gameOver = ref(false)
const birdProgress = ref(0)
const clouds = ref<Cloud[]>([])

let nextId = 0

// ==================== Canvas Setup ====================
const containerRef = ref<HTMLElement | null>(null)

// Let useCanvasRenderer auto-size to container (no hardcoded dimensions)
const { canvasRef, getRenderContext, width: canvasWidth, height: canvasHeight } = useCanvasRenderer(containerRef, {})

const { createCachedGradient, drawCircle, interpolateColor } = useCanvasDrawing()

// ==================== Colors & Constants ====================
const SKY_CLEAN = { r: 135, g: 206, b: 250 }
const SKY_POLLUTED = { r: 55, g: 86, b: 150 }
const GROUND_COLOR_TOP = '#8b7355'
const GROUND_COLOR_BOTTOM = '#6d5a44'
const GROUND_HEIGHT = 0.3  // 30% of canvas height

// Tree colors by type and health
const TREE_COLORS = {
  healthy: {
    foliage: '#2d5a2d',
    trunk: '#5d4037'
  },
  sick: {
    foliage: '#8b6914',
    trunk: '#4a3f2f'
  },
  dead: {
    foliage: '#4a4a4a',
    trunk: '#2a2a2a'
  }
}

// ==================== Init Forest ====================
function initForest() {
  clearTrees()
  clearFactories()
  nextId = 0
  treesPlanted.value = 0
  plantCooldown.value = 0
  gameOver.value = false
  birdProgress.value = 0

  // Initial trees
  const treeCount = 18 + Math.floor(Math.random() * 8)
  for (let i = 0; i < treeCount; i++) {
    const x = 5 + Math.random() * 90  // 5-95% of width
    const tree: Tree = {
      id: nextId++,
      x: x,
      y: 0,  // Will be calculated from height
      type: TREE_TYPES[Math.floor(Math.random() * TREE_TYPES.length)]!,
      scale: 0.6 + Math.random() * 0.8,
      growing: false,
      growthProgress: 1,
      render: (ctx) => renderTree(ctx, tree),
      update: (dt) => {
        if (tree.growing && tree.growthProgress < 1) {
          tree.growthProgress = Math.min(1, tree.growthProgress + dt * 2)
          if (tree.growthProgress >= 1) {
            tree.growing = false
          }
        }
      }
    }
    addTree(tree)
  }
}

// ==================== Rendering ====================
function renderSky(ctx: CanvasRenderingContext2D, width: number, height: number) {
  // Sky gradient based on pollution
  const pollution = Math.min(1, totalCo2.value / 20)
  const r = Math.round(SKY_CLEAN.r - pollution * (SKY_CLEAN.r - SKY_POLLUTED.r))
  const g = Math.round(SKY_CLEAN.g - pollution * (SKY_CLEAN.g - SKY_POLLUTED.g))
  const b = Math.round(SKY_CLEAN.b - pollution * (SKY_CLEAN.b - SKY_POLLUTED.b))

  const grad = createCachedGradient(ctx, 0, 0, 0, height * 0.7, [
    [0, `rgb(${r}, ${g}, ${b})`],
    [1, `rgb(${r + 40}, ${g + 30}, ${b - 20})`]
  ], `sky-${totalCo2.value.toFixed(1)}`)

  ctx.fillStyle = grad
  ctx.fillRect(0, 0, width, height * 0.7)
}

function renderGround(ctx: CanvasRenderingContext2D, width: number, height: number) {
  const groundY = height * 0.7
  const groundH = height * GROUND_HEIGHT

  const grad = createCachedGradient(ctx, 0, groundY, 0, groundY + groundH, [
    [0, GROUND_COLOR_TOP],
    [1, GROUND_COLOR_BOTTOM]
  ], 'ground')

  ctx.fillStyle = grad
  ctx.fillRect(0, groundY, width, groundH)
}

function renderClouds(ctx: CanvasRenderingContext2D) {
  // Each cloud = 3 overlapping circles (puffs) - pattern from ClimateBackground.vue
  clouds.value.forEach(cloud => {
    ctx.fillStyle = cloud.color
    ctx.globalAlpha = cloud.opacity

    const scale = cloud.radius / 25  // Scale factor based on radius

    // Puff 1: 40px circle at base position
    ctx.beginPath()
    ctx.arc(cloud.x, cloud.y, 20 * scale, 0, Math.PI * 2)
    ctx.fill()

    // Puff 2: 50px circle, offset right and slightly up (middle, largest)
    ctx.beginPath()
    ctx.arc(cloud.x + 25 * scale, cloud.y - 5 * scale, 25 * scale, 0, Math.PI * 2)
    ctx.fill()

    // Puff 3: 35px circle, offset further right
    ctx.beginPath()
    ctx.arc(cloud.x + 55 * scale, cloud.y, 17.5 * scale, 0, Math.PI * 2)
    ctx.fill()

    ctx.globalAlpha = 1
  })
}

function renderBird(ctx: CanvasRenderingContext2D, width: number, height: number) {
  const x = (5 + birdProgress.value * 90) / 100 * width
  const y = (15 + Math.sin(birdProgress.value * 0.3) * 5) / 100 * height

  // Simple bird shape (triangle)
  ctx.fillStyle = '#4a4a4a'
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x - 8, y + 4)
  ctx.lineTo(x - 8, y - 4)
  ctx.closePath()
  ctx.fill()
}

function renderTree(ctx: CanvasRenderingContext2D, tree: Tree) {
  const { width, height } = getRenderContext()
  const x = (tree.x / 100) * width
  const groundY = height * 0.7
  const treeSize = 35 * tree.scale * tree.growthProgress

  ctx.save()
  ctx.translate(x, groundY)
  ctx.scale(tree.scale * tree.growthProgress, tree.scale * tree.growthProgress)

  // Trunk
  ctx.fillStyle = TREE_COLORS.healthy.trunk
  ctx.fillRect(-3, -10, 6, 15)

  // Foliage (simplified - could be type-specific)
  ctx.fillStyle = TREE_COLORS.healthy.foliage
  ctx.beginPath()

  switch (tree.type) {
    case 'pine':
    case 'spruce':
    case 'fir':
      // Triangle
      ctx.moveTo(0, -30)
      ctx.lineTo(-15, 0)
      ctx.lineTo(15, 0)
      break

    case 'oak':
    case 'maple':
      // Round
      ctx.arc(0, -20, 18, 0, Math.PI * 2)
      break

    case 'birch':
    case 'willow':
      // Oval
      ctx.ellipse(0, -20, 12, 20, 0, 0, Math.PI * 2)
      break
  }

  ctx.closePath()
  ctx.fill()

  ctx.restore()
}

function renderFactory(ctx: CanvasRenderingContext2D, factory: Factory) {
  const { width, height } = getRenderContext()
  const x = (factory.x / 100) * width
  const groundY = height * 0.7
  // Bottom position: base 18% from bottom + Y offset (0-6%)
  const bottomOffset = (18 + factory.y) / 100 * height
  const y = height - bottomOffset - (30 * factory.scale)  // Subtract factory height

  const factoryWidth = 40 * factory.scale
  const factoryHeight = 30 * factory.scale
  const bodyHeight = factoryHeight * 0.7

  // Factory body with gradient (matches original CSS)
  const bodyGradient = ctx.createLinearGradient(0, y, 0, y + bodyHeight)
  bodyGradient.addColorStop(0, '#616161')
  bodyGradient.addColorStop(0.5, '#424242')
  bodyGradient.addColorStop(1, '#212121')

  ctx.fillStyle = bodyGradient
  ctx.beginPath()
  ctx.roundRect(x - factoryWidth / 2, y, factoryWidth, bodyHeight, [2, 2, 0, 0])
  ctx.fill()

  // Chimney (left side, 30% from left edge)
  const chimneyWidth = factoryWidth * 0.25
  const chimneyHeight = bodyHeight * 0.6
  const chimneyX = x - factoryWidth / 2 + factoryWidth * 0.3
  const chimneyY = y - chimneyHeight

  ctx.fillStyle = '#757575'
  ctx.fillRect(chimneyX, chimneyY, chimneyWidth, chimneyHeight)

  // Smoke particles
  factory.smoke.forEach(particle => {
    ctx.fillStyle = `rgba(100, 100, 100, ${particle.opacity})`
    drawCircle(ctx, particle.x, particle.y, 3, ctx.fillStyle)
  })
}

function render() {
  const { ctx, width, height, clear } = getRenderContext()
  clear()

  // Background
  renderSky(ctx, width, height)
  renderGround(ctx, width, height)
  renderClouds(ctx)
  renderBird(ctx, width, height)

  // Game objects
  trees.value.forEach(tree => tree.render(ctx))
  factories.value.forEach(factory => factory.render(ctx))
}

// ==================== Game Loop ====================
function updateClouds() {
  const treeCount = trees.value.length
  const factoryCount = factories.value.length
  const pollutionRatio = factoryCount / Math.max(1, treeCount)
  const cloudCount = Math.min(12, Math.floor(pollutionRatio * 8) + Math.floor(factoryCount * 0.8))

  // Only regenerate if count changed
  if (clouds.value.length !== cloudCount) {
    const darkness = Math.min(0.9, pollutionRatio * 0.5)
    clouds.value = Array.from({ length: cloudCount }, (_, i) => {
      const gray = Math.round(150 - darkness * 100)
      return {
        x: ((5 + (i * 17 + i * i * 3) % 90) / 100) * canvasWidth.value,
        y: ((8 + (i * 11) % 35) / 100) * canvasHeight.value,
        radius: 20 + (i % 4) * 10,
        opacity: 0.4 + darkness * 0.5,
        color: `rgba(${gray}, ${gray}, ${gray + 10}, ${0.6 + darkness * 0.3})`
      }
    })
  }
}

function gameTick(dt: number) {
  if (gameOver.value) return

  // Update cooldown
  if (plantCooldown.value > 0) {
    plantCooldown.value = Math.max(0, plantCooldown.value - dt)
  }

  // Update bird progress (smooth interpolation)
  const target = internalProgress.value * 100
  birdProgress.value += (target - birdProgress.value) * 0.08

  // Update trees
  trees.value.forEach(tree => tree.update?.(dt))

  // Update factories (smoke particles)
  factories.value.forEach(factory => {
    factory.smoke.forEach(particle => {
      particle.y -= particle.vy * dt * 60
      particle.opacity -= dt * 0.5
      particle.life -= dt
    })

    // Remove dead particles
    factory.smoke = factory.smoke.filter(p => p.life > 0)

    // Spawn new particles from chimney
    if (Math.random() < 0.3) {
      const { width, height } = getRenderContext()
      const factoryX = (factory.x / 100) * width
      const factoryWidth = 40 * factory.scale
      const factoryHeight = 30 * factory.scale
      const bodyHeight = factoryHeight * 0.7
      const chimneyHeight = bodyHeight * 0.6
      const bottomOffset = (18 + factory.y) / 100 * height
      const factoryY = height - bottomOffset - factoryHeight

      // Chimney center position
      const chimneyX = factoryX - factoryWidth / 2 + factoryWidth * 0.3 + (factoryWidth * 0.25) / 2
      const chimneyTop = factoryY - chimneyHeight

      factory.smoke.push({
        x: chimneyX,
        y: chimneyTop,
        vy: 0.5 + Math.random() * 0.5,
        opacity: 0.6,
        life: 2
      })
    }
  })

  // Factory spawn rate based on GPU power (matches original formula)
  const factoryRate = (effectivePower.value / 450) * dt * 1.1

  if (factories.value.length < 30 && Math.random() < factoryRate) {
    // Min distance check (5 attempts to find good position)
    let newX = 10 + Math.random() * 80
    const minDistance = 12
    for (let attempt = 0; attempt < 5; attempt++) {
      const tooClose = factories.value.some(f => Math.abs(f.x - newX) < minDistance)
      if (!tooClose) break
      newX = 10 + Math.random() * 80
    }

    const factory: Factory = {
      id: nextId++,
      x: newX,
      y: Math.random() * 6,  // Small offset 0-6
      scale: 0.45 + Math.random() * 0.65,  // Random scale 0.45-1.1
      smoke: [],
      render: (ctx) => renderFactory(ctx, factory)
    }
    addFactory(factory)

    // Tree destruction: Remove a random mature tree (70% chance)
    const matureTrees = trees.value.filter(t => !t.growing && t.growthProgress >= 1)
    if (matureTrees.length > 0 && Math.random() < 0.7) {
      const treeToRemove = matureTrees[Math.floor(Math.random() * matureTrees.length)]!
      const index = trees.value.findIndex(t => t.id === treeToRemove.id)
      if (index !== -1) {
        trees.value.splice(index, 1)
      }
    }
  }

  // Update clouds
  updateClouds()

  // Check game over
  if (trees.value.length === 0) {
    gameOver.value = true
  }

  // Render
  render()
}

useGameLoop({
  mode: 'interval',
  fps: 10,
  onTick: gameTick,
  isActive: computed(() => !gameOver.value && (props.progress ?? 0) > 0)
})

// ==================== Click Handler ====================
function handleClick(e: MouseEvent) {
  if (gameOver.value || plantCooldown.value > 0) return

  const rect = canvasRef.value!.getBoundingClientRect()
  const clickX = ((e.clientX - rect.left) / rect.width) * 100  // Convert to percentage

  // Factory hit detection: Check if click is near a factory
  const nearbyFactory = factories.value.find(f => {
    const hitRadius = 5 * f.scale  // Factory width ~5% per scale unit
    return Math.abs(f.x - clickX) < hitRadius
  })

  if (nearbyFactory) {
    // Remove factory (but also plant tree - don't return!)
    const index = factories.value.findIndex(f => f.id === nearbyFactory.id)
    if (index !== -1) {
      factories.value.splice(index, 1)
    }
  }

  // Plant tree at click position
  const tree: Tree = {
    id: nextId++,
    x: clickX,
    y: 0,
    type: TREE_TYPES[Math.floor(Math.random() * TREE_TYPES.length)]!,
    scale: 0.6 + Math.random() * 0.8,
    growing: true,
    growthProgress: 0,  // Start at 0, grow to 1 over 1 second
    render: (ctx) => renderTree(ctx, tree),
    update: (dt) => {
      if (tree.growing && tree.growthProgress < 1) {
        tree.growthProgress = Math.min(1, tree.growthProgress + dt)  // dt * 1 = 1 second growth
        if (tree.growthProgress >= 1) {
          tree.growing = false
        }
      }
    }
  }

  addTree(tree)
  treesPlanted.value++
  plantCooldown.value = 1  // 1 second cooldown (same as growth time)
}

// ==================== Lifecycle ====================
onMounted(() => {
  initForest()

  setTimeout(() => {
    showInstructions.value = false
  }, 5000)
})
</script>

<style scoped>
.forest-game-canvas {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}

/* UI Overlays - same as original */
.stats-bar {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
  background: rgba(0, 0, 0, 0.6);
  padding: 6px 14px;
  border-radius: 15px;
  backdrop-filter: blur(4px);
  z-index: 100;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.stat-label {
  font-size: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
}

.stat-value {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  color: #fff;
  font-weight: bold;
}

.plant-instruction {
  position: absolute;
  bottom: 3%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(76, 175, 80, 0.8);
  color: white;
  padding: 2% 4%;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: bold;
  transition: background 0.3s;
  min-width: 20%;
  text-align: center;
  z-index: 90;
}

.plant-instruction.cooldown {
  background: rgba(158, 158, 158, 0.8);
}

.game-over {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
  z-index: 110;
}

.game-over-text {
  color: #ff5722;
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.game-over-co2 {
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.4rem;
}

.game-over-comparison,
.game-over-stats {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  margin-top: 0.3rem;
}

.summary-box {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  pointer-events: none;
  z-index: 80;
  background: rgba(30, 86, 49, 0.9);
  padding: 6px 20px;
  border-radius: 8px;
  border: 1px solid rgba(76, 175, 80, 0.5);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  max-width: 90%;
}

.summary-detail {
  color: #c8e6c9;
  font-size: 12px;
  font-family: 'Georgia', 'Times New Roman', serif;
  white-space: nowrap;
}

.summary-comparison {
  color: #a5d6a7;
  font-size: 12px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  white-space: nowrap;
}

.summary-trees {
  color: #81c784;
  font-size: 11px;
  font-family: 'Georgia', 'Times New Roman', serif;
  white-space: nowrap;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
