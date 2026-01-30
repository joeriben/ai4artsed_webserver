<template>
  <div class="forest-game" @click="handleClick">
    <!-- Sky -->
    <div class="sky" :style="skyStyle">
      <!-- Clouds - more factories = more dark clouds, more trees = fewer clouds -->
      <div
        v-for="(cloud, i) in clouds"
        :key="'cloud-' + i"
        class="cloud"
        :style="cloud.style"
      ></div>

      <!-- Flying bird (progress indicator: right to left) -->
      <!-- Sprite-based animation from CodePen (Open Source) -->
      <div class="bird-container" :style="birdStyle">
        <div class="bird"></div>
      </div>
    </div>

    <!-- Ground -->
    <div class="ground"></div>

    <!-- Trees -->
    <div
      v-for="tree in trees"
      :key="tree.id"
      class="tree"
      :class="[`tree-${tree.type}`, { growing: tree.growing }]"
      :style="getTreeStyle(tree)"
    >
      <div class="tree-top"></div>
      <div class="tree-trunk"></div>
    </div>

    <!-- Factories -->
    <div
      v-for="factory in factories"
      :key="factory.id"
      class="factory"
      :style="getFactoryStyle(factory)"
    >
      <div class="factory-body"></div>
      <div class="factory-chimney">
        <div class="smoke" v-for="n in 3" :key="n" :style="{ animationDelay: `${n * 0.3}s` }"></div>
      </div>
    </div>

    <!-- Stats bar -->
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

    <!-- Plant instruction (before first click) / Cooldown indicator (after) -->
    <div class="plant-instruction" :class="{ cooldown: plantCooldown > 0 }">
      <template v-if="treesPlanted === 0">
        {{ t('edutainment.forest.clickToPlant') }}
      </template>
      <template v-else-if="plantCooldown > 0">
        ⏳ {{ plantCooldown.toFixed(1) }}s
      </template>
    </div>

    <!-- Game over (all trees destroyed) -->
    <div v-if="gameOver" class="game-over">
      <div class="game-over-text">{{ t('edutainment.forest.gameOver') }}</div>
      <div class="game-over-co2">{{ totalCo2.toFixed(1) }}g CO₂</div>
      <div class="game-over-comparison">
        {{ t('edutainment.forest.comparison', { hours: treeHours }) }}
      </div>
      <div class="game-over-stats">
        {{ t('edutainment.forest.treesPlanted', { count: treesPlanted }) }}
      </div>
    </div>

    <!-- Summary overlay (progress >= 80% to account for fast generations) -->
    <div v-if="!gameOver && props.progress && props.progress >= 80" class="summary-overlay">
      <span class="summary-status">{{ t('edutainment.forest.complete') }}</span>
      <span class="summary-detail">{{ totalCo2.toFixed(2) }}g CO₂</span>
      <span class="summary-comparison">{{ t('edutainment.forest.comparison', { hours: treeHours }) }}</span>
      <span class="summary-trees">{{ t('edutainment.forest.treesPlanted', { count: treesPlanted }) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { GpuRealtimeStats } from '@/composables/useEdutainmentFacts'

const { t } = useI18n()

const props = defineProps<{
  progress?: number
  estimatedSeconds?: number
}>()

// Tree types for variety (conifers and broadleaf)
const TREE_TYPES = ['pine', 'spruce', 'fir', 'oak', 'birch', 'maple', 'willow'] as const
type TreeType = typeof TREE_TYPES[number]

interface Tree {
  id: number
  x: number // 0-100%
  type: TreeType
  scale: number // 0.5-1.5
  growing: boolean
  growthProgress: number // 0-1
}

interface Factory {
  id: number
  x: number
  y: number // vertical offset (0-8%)
  scale: number
}

// State
const trees = ref<Tree[]>([])
const factories = ref<Factory[]>([])
const plantCooldown = ref(0)
const treesPlanted = ref(0)
const gameOver = ref(false)
let nextId = 0

// Bird animation (progress indicator)
const birdProgress = ref(0)
let birdAnimationId: number | null = null

// GPU stats
const gpuStats = ref<GpuRealtimeStats>({ available: false })
const simulatedPower = ref(200)
const simulatedTemp = ref(55)
const totalCo2 = ref(0)
const totalEnergy = ref(0)
const elapsedSeconds = ref(0)

// Effective values
const effectivePower = computed(() => {
  const realPower = gpuStats.value.power_draw_watts || 0
  return realPower > 100 ? realPower : simulatedPower.value
})
const effectiveTemp = computed(() => {
  const realPower = gpuStats.value.power_draw_watts || 0
  const realTemp = gpuStats.value.temperature_celsius || 0
  return realPower > 100 ? realTemp : simulatedTemp.value
})

// Tree absorbs ~22kg CO2/year = ~2.51g/hour (mature tree average)
const treeHours = computed(() => {
  const hours = totalCo2.value / 2.51
  return hours.toFixed(1)
})

// Bird style (flies from left to right as progress increases - European reading direction)
const birdStyle = computed(() => {
  // left: 5% at 0% progress, left: 95% at 100% progress
  const leftPos = 5 + birdProgress.value * 0.9
  return {
    left: `${leftPos}%`,
    top: `${15 + Math.sin(birdProgress.value * 0.3) * 5}%` // Slight wave motion
  }
})

// Smooth bird animation
function animateBird() {
  const target = props.progress ?? 0
  const diff = target - birdProgress.value
  if (Math.abs(diff) > 0.01) {
    birdProgress.value += diff * 0.08 // lerp for smooth movement
  }
  birdAnimationId = requestAnimationFrame(animateBird)
}

// Sky darkens with CO2
const skyStyle = computed(() => {
  const pollution = Math.min(1, totalCo2.value / 20)
  const r = Math.round(135 - pollution * 80)
  const g = Math.round(206 - pollution * 120)
  const b = Math.round(250 - pollution * 100)
  return {
    background: `linear-gradient(180deg, rgb(${r}, ${g}, ${b}) 0%, rgb(${r + 40}, ${g + 30}, ${b - 20}) 100%)`
  }
})

// Clouds - more factories = more dark clouds, more trees = cleaner sky
const clouds = computed(() => {
  const treeCount = trees.value.length
  const factoryCount = factories.value.length

  // Calculate cloud amount: more factories = more clouds (0-12), fewer trees = more clouds
  const pollutionRatio = factoryCount / Math.max(1, treeCount)
  const cloudCount = Math.min(12, Math.floor(pollutionRatio * 8) + Math.floor(factoryCount * 0.8))

  if (cloudCount === 0) return []

  // Darkness based on factory/tree ratio
  const darkness = Math.min(0.9, pollutionRatio * 0.5)

  return Array.from({ length: cloudCount }, (_, i) => {
    const gray = Math.round(150 - darkness * 100)
    return {
      style: {
        left: `${5 + (i * 17 + i * i * 3) % 90}%`,
        top: `${8 + (i * 11) % 35}%`,
        opacity: 0.4 + darkness * 0.5,
        transform: `scale(${0.5 + (i % 4) * 0.25})`,
        backgroundColor: `rgba(${gray}, ${gray}, ${gray + 10}, ${0.6 + darkness * 0.3})`,
        animationDelay: `${i * 0.7}s`
      }
    }
  })
})

// Intervals
let gameLoopInterval: number | null = null
let gpuPollInterval: number | null = null
let energyInterval: number | null = null

// Initialize forest
function initForest() {
  trees.value = []
  factories.value = []

  // Create initial trees (15-25 trees spread across landscape)
  const treeCount = 18 + Math.floor(Math.random() * 8)
  for (let i = 0; i < treeCount; i++) {
    trees.value.push({
      id: nextId++,
      x: 5 + Math.random() * 90,
      type: TREE_TYPES[Math.floor(Math.random() * TREE_TYPES.length)]!,
      scale: 0.6 + Math.random() * 0.8,
      growing: false,
      growthProgress: 1
    })
  }
}

// Plant a tree
function plantTree(x: number) {
  if (plantCooldown.value > 0 || gameOver.value) return

  // Check if planting on/near a factory (within 8% distance)
  const nearbyFactory = factories.value.find(f => Math.abs(f.x - x) < 8)
  if (nearbyFactory) {
    // Remove the factory
    factories.value = factories.value.filter(f => f.id !== nearbyFactory.id)
  }

  trees.value.push({
    id: nextId++,
    x: x,
    type: TREE_TYPES[Math.floor(Math.random() * TREE_TYPES.length)]!,
    scale: 0.6 + Math.random() * 0.4,
    growing: true,
    growthProgress: 0.1
  })

  treesPlanted.value++
  plantCooldown.value = 1.0 // 1 second cooldown
}

// Handle click to plant
function handleClick(event: MouseEvent) {
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 100
  plantTree(x)
}

// Game loop
function gameLoop() {
  if (gameOver.value) return

  const dt = 0.1 // 100ms tick

  // Update cooldown
  if (plantCooldown.value > 0) {
    plantCooldown.value = Math.max(0, plantCooldown.value - dt)
  }

  // Grow trees
  for (const tree of trees.value) {
    if (tree.growing && tree.growthProgress < 1) {
      tree.growthProgress = Math.min(1, tree.growthProgress + dt * 0.15) // ~7 seconds to fully grow
      if (tree.growthProgress >= 1) {
        tree.growing = false
      }
    }
  }

  // Factory spawn rate: ~1.1 per second at 450W
  // 10 ticks/second, so need ~0.11 probability per tick at 450W
  // Formula: (watts / 450) * 0.11 per tick
  const factoryRate = (effectivePower.value / 450) * dt * 1.1

  if (Math.random() < factoryRate && factories.value.length < 30) {
    // Spawn factory with better distribution
    // Avoid clustering by checking existing factory positions
    let newX = 10 + Math.random() * 80
    const minDistance = 12
    for (let attempt = 0; attempt < 5; attempt++) {
      const tooClose = factories.value.some(f => Math.abs(f.x - newX) < minDistance)
      if (!tooClose) break
      newX = 10 + Math.random() * 80
    }

    factories.value.push({
      id: nextId++,
      x: newX,
      y: Math.random() * 6, // Slight vertical variation
      scale: 0.45 + Math.random() * 0.65
    })

    // Also remove a tree if available (factories replace trees)
    const matureTrees = trees.value.filter(t => !t.growing)
    if (matureTrees.length > 0 && Math.random() < 0.7) {
      const treeToRemove = matureTrees[Math.floor(Math.random() * matureTrees.length)]!
      trees.value = trees.value.filter(t => t.id !== treeToRemove.id)
    }
  }

  // Check game over
  if (trees.value.length === 0 && factories.value.length > 3) {
    gameOver.value = true
  }
}

// GPU fetching
async function fetchGpuStats() {
  try {
    const response = await fetch('/api/settings/gpu-realtime')
    if (response.ok) {
      gpuStats.value = await response.json()
    }
  } catch (error) {
    console.warn('[ForestGame] GPU fetch failed:', error)
  }
}

function updateEnergy() {
  elapsedSeconds.value++

  const realPower = gpuStats.value.power_draw_watts || 0
  const isGpuActive = realPower > 100

  simulatedPower.value = Math.min(450, 150 + elapsedSeconds.value * 10 + Math.random() * 50)
  simulatedTemp.value = Math.min(82, 45 + elapsedSeconds.value * 1.5 + Math.random() * 3)

  const watts = isGpuActive ? realPower : simulatedPower.value
  const co2PerKwh = gpuStats.value.co2_per_kwh_grams || 400

  const whThisSecond = watts / 3600
  totalEnergy.value += whThisSecond
  totalCo2.value += (whThisSecond / 1000) * co2PerKwh
}

// Tree styling
function getTreeStyle(tree: Tree) {
  const baseSize = 40 * tree.scale * tree.growthProgress
  return {
    left: `${tree.x}%`,
    bottom: '25%',
    width: `${baseSize}px`,
    height: `${baseSize * 1.5}px`,
    opacity: tree.growthProgress < 0.3 ? 0.5 : 1,
    zIndex: Math.floor(tree.x)
  }
}

// Factory styling
function getFactoryStyle(factory: Factory) {
  const baseSize = 30 * factory.scale
  const bottomPos = 18 + (factory.y || 0) // Lower base (18%) + variation
  return {
    left: `${factory.x}%`,
    bottom: `${bottomPos}%`,
    width: `${baseSize}px`,
    height: `${baseSize * 1.2}px`,
    zIndex: Math.floor(100 - factory.y * 10) // Closer to bottom = higher z-index
  }
}

// Lifecycle
onMounted(() => {
  initForest()
  fetchGpuStats()

  // Start game loop (100ms tick)
  gameLoopInterval = window.setInterval(gameLoop, 100)

  // GPU polling
  gpuPollInterval = window.setInterval(fetchGpuStats, 2000)

  // Energy calculation
  energyInterval = window.setInterval(updateEnergy, 1000)

  // Start bird animation
  animateBird()
})

onUnmounted(() => {
  if (gameLoopInterval) clearInterval(gameLoopInterval)
  if (gpuPollInterval) clearInterval(gpuPollInterval)
  if (energyInterval) clearInterval(energyInterval)
  if (birdAnimationId) cancelAnimationFrame(birdAnimationId)
})

// Watch progress for auto-start behavior
watch(() => props.progress, (newProgress) => {
  if (newProgress && newProgress > 0 && trees.value.length === 0) {
    initForest()
  }
})
</script>

<style scoped>
.forest-game {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
}

/* Sky */
.sky {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 75%;
  transition: background 1s ease;
}

/* Clouds */
.cloud {
  position: absolute;
  width: 50px;
  height: 20px;
  border-radius: 20px;
  transition: opacity 0.5s, background-color 0.5s;
  animation: float-cloud 10s ease-in-out infinite;
}

.cloud::before,
.cloud::after {
  content: '';
  position: absolute;
  background: inherit;
  border-radius: 50%;
}

.cloud::before {
  width: 20px;
  height: 20px;
  top: -10px;
  left: 8px;
}

.cloud::after {
  width: 28px;
  height: 28px;
  top: -14px;
  left: 20px;
}

@keyframes float-cloud {
  0%, 100% { transform: translateX(0) scale(var(--scale, 1)); }
  50% { transform: translateX(15px) scale(calc(var(--scale, 1) * 1.05)); }
}

/* Ground */
.ground {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30%;
  background: linear-gradient(180deg, #5a8f5a 0%, #3d6b3d 50%, #2d4a2d 100%);
}

/* Trees */
.tree {
  position: absolute;
  transform: translateX(-50%);
  transition: opacity 0.3s, width 0.3s, height 0.3s;
}

.tree-top {
  width: 100%;
  height: 70%;
  position: relative;
}

.tree-trunk {
  width: 20%;
  height: 35%;
  margin: 0 auto;
  background: linear-gradient(90deg, #5d4037 0%, #8b6914 50%, #5d4037 100%);
  border-radius: 2px;
}

/* Pine tree */
.tree-pine .tree-top {
  background: none;
}
.tree-pine .tree-top::before,
.tree-pine .tree-top::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-left: 50% solid transparent;
  border-right: 50% solid transparent;
}
.tree-pine .tree-top::before {
  bottom: 20%;
  border-bottom: 60% solid #2d5a2d;
  width: 80%;
}
.tree-pine .tree-top::after {
  bottom: 0;
  border-bottom: 70% solid #1e4a1e;
  width: 100%;
}

/* Oak tree */
.tree-oak .tree-top {
  background: radial-gradient(ellipse at center, #3d7a3d 0%, #2d5a2d 70%, #1e4a1e 100%);
  border-radius: 50% 50% 40% 40%;
}

/* Birch tree */
.tree-birch .tree-top {
  background: radial-gradient(ellipse at center, #7ab87a 0%, #5a9a5a 60%, #3d7a3d 100%);
  border-radius: 40% 40% 30% 30%;
}
.tree-birch .tree-trunk {
  background: linear-gradient(90deg, #f5f5f5 0%, #e0e0e0 30%, #bdbdbd 50%, #e0e0e0 70%, #f5f5f5 100%);
}

/* Spruce tree (tall conifer) */
.tree-spruce .tree-top {
  background: none;
  clip-path: polygon(50% 0%, 15% 100%, 85% 100%);
  background: linear-gradient(180deg, #1a4a1a 0%, #2d5a2d 50%, #1e3a1e 100%);
}

/* Fir tree (classic Christmas tree shape) */
.tree-fir .tree-top {
  background: none;
}
.tree-fir .tree-top::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 10%;
  width: 80%;
  height: 100%;
  background: #1e4a2e;
  clip-path: polygon(50% 0%, 5% 35%, 20% 35%, 0% 70%, 25% 70%, 10% 100%, 90% 100%, 75% 70%, 100% 70%, 80% 35%, 95% 35%);
}

/* Maple tree (rounded with reddish tint) */
.tree-maple .tree-top {
  background: radial-gradient(ellipse at center, #5a8a4a 0%, #4a7a3a 50%, #3a6a2a 100%);
  border-radius: 45% 45% 40% 40%;
}
.tree-maple .tree-trunk {
  background: linear-gradient(90deg, #6d4c41 0%, #8d6e63 50%, #6d4c41 100%);
}

/* Willow tree (drooping shape) */
.tree-willow .tree-top {
  background: radial-gradient(ellipse 60% 80% at center top, #6a9a5a 0%, #4a7a4a 60%, #3a6a3a 100%);
  border-radius: 50% 50% 60% 60%;
  height: 80%;
}
.tree-willow .tree-trunk {
  height: 40%;
  background: linear-gradient(90deg, #5d4037 0%, #795548 50%, #5d4037 100%);
}

/* Growing animation */
.tree.growing {
  animation: sway 2s ease-in-out infinite;
}

@keyframes sway {
  0%, 100% { transform: translateX(-50%) rotate(-1deg); }
  50% { transform: translateX(-50%) rotate(1deg); }
}

/* Factories */
.factory {
  position: absolute;
  transform: translateX(-50%);
}

.factory-body {
  width: 100%;
  height: 70%;
  background: linear-gradient(180deg, #616161 0%, #424242 50%, #212121 100%);
  border-radius: 2px 2px 0 0;
}

.factory-chimney {
  position: absolute;
  bottom: 60%;
  left: 30%;
  width: 25%;
  height: 60%;
  background: #757575;
}

.smoke {
  position: absolute;
  bottom: 100%;
  left: 50%;
  width: 15px;
  height: 15px;
  background: rgba(100, 100, 100, 0.6);
  border-radius: 50%;
  animation: rise-smoke 2s ease-out infinite;
}

@keyframes rise-smoke {
  0% {
    transform: translateX(-50%) translateY(0) scale(0.5);
    opacity: 0.7;
  }
  100% {
    transform: translateX(-50%) translateY(-50px) scale(1.5);
    opacity: 0;
  }
}

/* Stats bar */
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
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.stat-label {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
}

.stat-value {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #fff;
  font-weight: bold;
}

/* Plant instruction */
.plant-instruction {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(76, 175, 80, 0.8);
  color: white;
  padding: 6px 14px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  transition: background 0.3s;
  min-width: 60px;
  text-align: center;
}

.plant-instruction:empty {
  display: none;
}

.plant-instruction.cooldown {
  background: rgba(158, 158, 158, 0.8);
}

/* Game over */
.game-over {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
}

.game-over-text {
  color: #ff5722;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
}

.game-over-co2 {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 6px;
}

.game-over-comparison {
  color: #4CAF50;
  font-size: 13px;
  font-style: italic;
  margin-bottom: 10px;
  max-width: 280px;
}

.game-over-stats {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

/* Summary overlay (generation complete) */
.summary-overlay {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  z-index: 80;
}

.summary-status {
  display: block;
  color: #1e5631;
  font-size: 18px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-weight: bold;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.summary-detail {
  display: block;
  color: #2d5a2d;
  font-size: 15px;
  font-family: 'Georgia', 'Times New Roman', serif;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
}

.summary-comparison {
  display: block;
  color: #1e5631;
  font-size: 14px;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  margin-bottom: 10px;
  max-width: 280px;
}

.summary-trees {
  display: block;
  color: #3d7a3d;
  font-size: 12px;
  font-family: 'Georgia', 'Times New Roman', serif;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

/* Flying bird - Sprite-based animation (Open Source from CodePen) */
/* Source: https://codepen.io/hoangdacviet/pen/GRWvWmg */
.bird-container {
  position: absolute;
  z-index: 60;
}

.bird {
  background-image: url('https://s3-us-west-2.amazonaws.com/s.cdpn.io/174479/bird-cells.svg');
  background-size: auto 100%;
  width: 88px;
  height: 125px;
  will-change: background-position;
  animation: fly-cycle 1s steps(10) infinite;
  /* Make bird white with filter */
  filter: brightness(0) invert(1) drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
  transform: scale(0.4);
}

@keyframes fly-cycle {
  100% {
    background-position: -900px 0;
  }
}
</style>
