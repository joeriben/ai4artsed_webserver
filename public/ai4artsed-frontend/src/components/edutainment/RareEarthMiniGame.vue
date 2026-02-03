<template>
  <div class="rareearth-game" @click="handleClick">
    <!-- Sky (darkens with pollution) -->
    <div class="sky" :style="skyStyle"></div>

    <!-- Ground -->
    <div class="ground"></div>

    <!-- Mountain (left side) -->
    <div class="mountain"></div>

    <!-- Conveyor Belt (top-right, transports crystals) -->
    <div class="conveyor-belt">
      <div
        v-for="crystal in conveyorCrystals"
        :key="crystal.id"
        class="conveyor-crystal"
        :style="{
          left: `${crystal.x}%`,
          backgroundColor: crystal.color,
          animationDuration: `${2 / conveyorSpeed}s`
        }"
      ></div>

      <!-- Sludge drips from conveyor to lake -->
      <div
        v-for="drip in sludgeDrips"
        :key="drip.id"
        class="sludge-drip"
        :style="{
          left: `${drip.x}%`,
          animationDuration: `${1.5 / conveyorSpeed}s`
        }"
      ></div>
    </div>

    <!-- Lake (center-right, receives sludge) -->
    <div class="lake" :style="{ background: lakeColor }">
      <!-- Shovel animations (appear on click) -->
      <div
        v-for="shovel in shovels"
        :key="shovel.id"
        class="shovel"
        :style="{
          left: `${shovel.x}px`,
          top: `${shovel.y}px`
        }"
      ></div>
    </div>

    <!-- GPU Chip (bottom-right, shows 3 minerals) -->
    <div class="gpu-chip">
      <div class="chip-label">GPU</div>
      <div class="gem-container">
        <div
          v-for="(gem, i) in gpuGems"
          :key="i"
          class="gem"
          :style="{
            backgroundColor: gem.color,
            opacity: gem.opacity,
            boxShadow: gem.filled ? `0 0 10px ${gem.color}` : 'none'
          }"
        ></div>
      </div>
    </div>

    <!-- Container (bottom-left, collects sludge) -->
    <div class="container">
      <div class="container-fill" :style="{ height: `${containerFill}%` }"></div>
    </div>

    <!-- Truck animation (drives in when container full) -->
    <div v-if="showTruck" class="truck"></div>

    <!-- Vegetation (trees/bushes with health states) -->
    <div
      v-for="veg in vegetation"
      :key="veg.id"
      :class="['vegetation', `vegetation-${veg.type}`, veg.health]"
      :style="getVegetationStyle(veg)"
    >
      <div v-if="veg.type === 'tree'" class="veg-top"></div>
      <div v-if="veg.type === 'tree'" class="veg-trunk"></div>
    </div>

    <!-- Stats bar -->
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-label">{{ t('edutainment.rareearth.statsGpu') }}</span>
        <span class="stat-value">{{ Math.round(effectivePower) }}W / {{ Math.round(effectiveTemp) }}°C</span>
      </div>
      <div class="stat">
        <span class="stat-label">{{ t('edutainment.rareearth.statsSludge') }}</span>
        <span class="stat-value">{{ sludgeRemoved }} 🧪</span>
      </div>
      <div class="stat">
        <span class="stat-label">{{ t('edutainment.rareearth.statsHealth') }}</span>
        <span class="stat-value">{{ environmentHealth }}% 🌱</span>
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

    <!-- Instructions overlay (fades after 5s) -->
    <Transition name="fade">
      <div v-if="showInstructions" class="instruction-overlay" :class="{ cooldown: clickCooldown > 0 }">
        <template v-if="sludgeRemoved === 0">
          {{ t('edutainment.rareearth.clickToClean') }}
        </template>
        <template v-else-if="clickCooldown > 0">
          {{ t('edutainment.rareearth.instructionsCooldown', { seconds: clickCooldown.toFixed(1) }) }}
        </template>
      </div>
    </Transition>

    <!-- Game over (inactivity) -->
    <div v-if="gameOver" class="game-over">
      <div class="game-over-text">{{ t('edutainment.rareearth.gameOverInactive') }}</div>
      <div class="game-over-co2">{{ totalCo2.toFixed(1) }}g CO₂</div>
      <div class="game-over-stats">
        {{ t('edutainment.rareearth.statsSludge') }}: {{ sludgeRemoved }}
      </div>
    </div>

    <!-- Info banner (appears after 5s) -->
    <Transition name="fade">
      <div v-if="!gameOver && isShowingSummary" class="info-banner">
        <p>{{ t('edutainment.rareearth.infoBanner') }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAnimationProgress } from '@/composables/useAnimationProgress'

const { t } = useI18n()

const props = defineProps<{
  progress?: number
  estimatedSeconds?: number
}>()

// ==================== Use Animation Progress Composable ====================
const {
  internalProgress,
  summaryShown,
  totalCo2,
  effectivePower,
  effectiveTemp
} = useAnimationProgress({
  estimatedSeconds: computed(() => props.estimatedSeconds || 30),
  isActive: computed(() => (props.progress ?? 0) > 0)
})

const isShowingSummary = computed(() => summaryShown.value)
const showInstructions = ref(true)

// ==================== Interfaces ====================
interface VegetationItem {
  id: number
  x: number
  type: 'tree' | 'bush'
  health: 'healthy' | 'sick' | 'dead'
  scale: number
  transitionTimer: number
}

interface ConveyorCrystal {
  id: number
  x: number
  color: string
}

interface SludgeDrip {
  id: number
  x: number
}

interface Shovel {
  id: number
  x: number
  y: number
}

// ==================== State ====================
// Lake & Pollution
const lakePollution = ref(10)  // 0-100%

// Environment
const vegetation = ref<VegetationItem[]>([])
const environmentHealth = computed(() => {
  const healthy = vegetation.value.filter(v => v.health === 'healthy').length
  return Math.round((healthy / Math.max(1, vegetation.value.length)) * 100)
})

// Mining & Conveyor
const miningProgress = ref(0)  // 0-100% (GPU chip fill)
const conveyorSpeed = computed(() => {
  // Speed tied to GPU temp: 50°C = 1x, 100°C = 2x
  return Math.max(1, effectiveTemp.value / 50)
})
const conveyorCrystals = ref<ConveyorCrystal[]>([])
const sludgeDrips = ref<SludgeDrip[]>([])

// User actions
const sludgeRemoved = ref(0)
const clickCooldown = ref(0)
const containerFill = ref(0)
const showTruck = ref(false)
const shovels = ref<Shovel[]>([])

// Inactivity tracking
const lastClickTime = ref(Date.now())
const inactivityTimeout = 30000  // 30 seconds

// Game state
const gameOver = ref(false)

let nextId = 0

// ==================== Computed Styles ====================
const lakeColor = computed(() => {
  const pollution = lakePollution.value / 100
  const r = Math.round(30 + pollution * 60)
  const g = Math.round(144 - pollution * 90)
  const b = Math.round(255 - pollution * 180)
  return `radial-gradient(ellipse at center,
    rgb(${r}, ${g}, ${b}) 0%,
    rgb(${r-20}, ${g-30}, ${b-40}) 100%)`
})

const skyStyle = computed(() => {
  const darkness = lakePollution.value / 100
  const r = Math.round(135 - darkness * 80)
  const g = Math.round(206 - darkness * 120)
  const b = Math.round(250 - darkness * 100)
  return {
    background: `linear-gradient(180deg, rgb(${r}, ${g}, ${b}) 0%, rgb(${r + 40}, ${g + 30}, ${b - 20}) 100%)`
  }
})

const gpuGems = computed(() => {
  const progress = miningProgress.value
  return [
    {
      color: '#c0c0c0',  // Neodymium (silver)
      opacity: Math.min(1, progress / 33),
      filled: progress > 33
    },
    {
      color: '#9370db',  // Dysprosium (purple)
      opacity: Math.min(1, (progress - 33) / 33),
      filled: progress > 66
    },
    {
      color: '#98fb98',  // Terbium (pale green)
      opacity: Math.min(1, (progress - 66) / 34),
      filled: progress > 90
    }
  ]
})

// ==================== Initialization ====================
function initEnvironment() {
  vegetation.value = []
  let id = 0

  // Create 15-20 vegetation items
  const count = 15 + Math.floor(Math.random() * 6)
  for (let i = 0; i < count; i++) {
    const isTree = Math.random() < 0.6  // 60% trees, 40% bushes

    // Avoid lake area (center-right: 45-75%)
    let x = Math.random() * 100
    while (x > 45 && x < 75) {
      x = Math.random() * 100
    }

    vegetation.value.push({
      id: id++,
      x: x,
      type: isTree ? 'tree' : 'bush',
      health: 'healthy',
      scale: 0.6 + Math.random() * 0.6,
      transitionTimer: 0
    })
  }

  // Initialize conveyor crystals
  conveyorCrystals.value = [
    { id: nextId++, x: 0, color: '#c0c0c0' },    // Nd
    { id: nextId++, x: 33, color: '#9370db' },   // Dy
    { id: nextId++, x: 66, color: '#98fb98' }    // Tb
  ]

  // Initialize sludge drips
  sludgeDrips.value = Array.from({ length: 3 }, (_, i) => ({
    id: nextId++,
    x: 20 + i * 30
  }))

  // Reset state
  lakePollution.value = 10
  miningProgress.value = 0
  containerFill.value = 0
  sludgeRemoved.value = 0
  gameOver.value = false
  showInstructions.value = true
  lastClickTime.value = Date.now()
}

// ==================== Game Logic ====================
let gameLoopInterval: number | null = null

function gameLoop() {
  if (gameOver.value) return

  const dt = 0.1  // 100ms

  // Cooldown timer
  if (clickCooldown.value > 0) {
    clickCooldown.value = Math.max(0, clickCooldown.value - dt)
  }

  // Inactivity check
  if (Date.now() - lastClickTime.value > inactivityTimeout) {
    gameOver.value = true
    return
  }

  // Sludge influx from conveyor (speed tied to GPU temp)
  const influxRate = 0.067 * conveyorSpeed.value  // Base: 6.7% chance per tick = 1.5s
  if (Math.random() < influxRate) {
    lakePollution.value = Math.min(100, lakePollution.value + 8)
  }

  // Mining progress (fills GPU chip)
  if (Math.random() < 0.05) {  // Every ~2 seconds
    miningProgress.value = Math.min(100, miningProgress.value + 5)

    // Mining damages environment
    const healthyVeg = vegetation.value.filter(v => v.health === 'healthy')
    if (healthyVeg.length > 0 && Math.random() < 0.7) {
      const victim = healthyVeg[Math.floor(Math.random() * healthyVeg.length)]!
      victim.health = 'sick'
    }
  }

  // Environment degradation
  if (Math.random() < 0.04) {  // Every ~2.5s
    const healthyVeg = vegetation.value.filter(v => v.health === 'healthy')
    if (healthyVeg.length > 0) {
      healthyVeg[Math.floor(Math.random() * healthyVeg.length)]!.health = 'sick'
    }
  }

  if (Math.random() < 0.025) {  // Every ~4s
    const sickVeg = vegetation.value.filter(v => v.health === 'sick')
    if (sickVeg.length > 0) {
      sickVeg[Math.floor(Math.random() * sickVeg.length)]!.health = 'dead'
    }
  }

  // Re-degradation timers for healed vegetation
  for (const veg of vegetation.value) {
    if (veg.transitionTimer > 0) {
      veg.transitionTimer -= dt
      if (veg.transitionTimer <= 0 && veg.health === 'healthy') {
        veg.health = 'sick'  // Re-degrade after healing
      }
    }
  }
}

// ==================== User Interaction ====================
function handleClick(event: MouseEvent) {
  if (clickCooldown.value > 0 || gameOver.value) return

  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  // Lake hitbox detection (approximate center-right area)
  const lakeX = rect.width * 0.6  // Center of lake
  const lakeY = rect.height * 0.7  // Vertical center
  const lakeRadiusX = rect.width * 0.15
  const lakeRadiusY = rect.height * 0.1

  const dx = (x - lakeX) / lakeRadiusX
  const dy = (y - lakeY) / lakeRadiusY
  const inLake = (dx * dx + dy * dy) < 1

  if (inLake) {
    removeSludge(x, y)
  }
}

function removeSludge(x: number, y: number) {
  if (lakePollution.value < 5) return  // Nothing to remove

  // Show shovel animation at click position
  const shovelId = Date.now()
  shovels.value.push({ id: shovelId, x, y })
  setTimeout(() => {
    shovels.value = shovels.value.filter(s => s.id !== shovelId)
  }, 500)  // Remove after animation

  // Remove 10% pollution
  lakePollution.value = Math.max(0, lakePollution.value - 10)

  // Add to container
  containerFill.value = Math.min(100, containerFill.value + 10)

  // Counter
  sludgeRemoved.value++

  // Reset inactivity timer
  lastClickTime.value = Date.now()

  // Heal 1-2 random sick vegetation (temporary)
  const sickVeg = vegetation.value.filter(v => v.health === 'sick')
  const toHeal = sickVeg.slice(0, Math.floor(Math.random() * 2) + 1)
  toHeal.forEach(v => {
    v.health = 'healthy'
    v.transitionTimer = 5.0  // Will degrade again in 5 seconds
  })

  // Check if container full → trigger truck
  if (containerFill.value >= 100) {
    showTruck.value = true
    setTimeout(() => {
      containerFill.value = 0
      showTruck.value = false
    }, 2000)  // 2-second truck animation
  }

  // Start cooldown
  clickCooldown.value = 1.0
}

// ==================== Styling Helpers ====================
function getVegetationStyle(veg: VegetationItem) {
  const baseSize = veg.type === 'tree' ? 35 : 25
  const size = baseSize * veg.scale

  return {
    left: `${veg.x}%`,
    bottom: '25%',
    width: `${size}px`,
    height: `${size * 1.4}px`,
    zIndex: Math.floor(veg.x)
  }
}

// ==================== Lifecycle ====================
onMounted(() => {
  initEnvironment()
  gameLoopInterval = window.setInterval(gameLoop, 100)

  // Hide instructions after 5 seconds
  setTimeout(() => {
    showInstructions.value = false
  }, 5000)
})

onUnmounted(() => {
  if (gameLoopInterval) clearInterval(gameLoopInterval)
})

watch(() => props.progress, (newProgress) => {
  if (newProgress && newProgress > 0 && vegetation.value.length === 0) {
    initEnvironment()
  }
})
</script>

<style scoped>
.rareearth-game {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
}

.sky {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 70%;
  transition: background 1s ease;
}

.ground {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30%;
  background: linear-gradient(180deg, #8b7355 0%, #6d5a44 50%, #4a3f2f 100%);
}

.mountain {
  position: absolute;
  left: 5%;
  bottom: 25%;
  width: 150px;
  height: 120px;
  background: linear-gradient(135deg, #696969 0%, #8b7355 50%, #4a4a4a 100%);
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
  z-index: 5;
}

.conveyor-belt {
  position: absolute;
  right: 15%;
  top: 25%;
  width: 120px;
  height: 20px;
  background: linear-gradient(90deg, #3a3a3a 0%, #2a2a2a 100%);
  border: 2px solid #555;
  z-index: 10;
}

.conveyor-crystal {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 4px;
  animation: conveyor-move 2s linear infinite;
}

@keyframes conveyor-move {
  0% { left: 0%; }
  100% { left: 100%; }
}

.sludge-drip {
  position: absolute;
  top: 100%;
  width: 4px;
  height: 15px;
  background: linear-gradient(180deg, #5a3e2b, transparent);
  animation: drip 1.5s ease-in infinite;
}

@keyframes drip {
  0% { transform: translateY(0); opacity: 1; }
  100% { transform: translateY(80px); opacity: 0; }
}

.lake {
  position: absolute;
  right: 20%;
  bottom: 28%;
  width: 180px;
  height: 80px;
  border-radius: 50%;
  transition: background 1s ease;
  z-index: 3;
}

.shovel {
  position: absolute;
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #8B4513 0%, #654321 50%, #8B4513 100%);
  clip-path: polygon(70% 0%, 100% 30%, 60% 70%, 30% 40%);
  animation: scoop 0.5s ease-out;
  transform-origin: bottom right;
  pointer-events: none;
}

@keyframes scoop {
  0% { transform: rotate(0deg) translateY(0); opacity: 1; }
  50% { transform: rotate(-15deg) translateY(-10px); opacity: 1; }
  100% { transform: rotate(0deg) translateY(0); opacity: 0; }
}

.gpu-chip {
  position: absolute;
  right: 8%;
  bottom: 12%;
  width: 60px;
  height: 40px;
  background: linear-gradient(135deg, #2c2c2c, #1a1a1a);
  border-radius: 4px;
  border: 2px solid #444;
  padding: 4px;
  z-index: 15;
}

.chip-label {
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 8px;
  color: #888;
  font-weight: bold;
}

.gem-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 100%;
  padding-top: 8px;
}

.gem {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: opacity 0.5s, box-shadow 0.3s;
}

.container {
  position: absolute;
  left: 8%;
  bottom: 12%;
  width: 40px;
  height: 50px;
  background: #424242;
  border: 2px solid #666;
  border-radius: 4px;
  overflow: hidden;
  z-index: 15;
}

.container-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: linear-gradient(180deg, #5a3e2b, #3d2817);
  transition: height 0.3s ease;
}

.truck {
  position: absolute;
  left: -60px;
  bottom: 12%;
  width: 50px;
  height: 30px;
  background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
  border-radius: 4px;
  animation: truck-drive-in 2s ease-in-out;
  z-index: 20;
}

@keyframes truck-drive-in {
  0% { left: -60px; }
  40% { left: 5%; }
  60% { left: 5%; }
  100% { left: -60px; }
}

.vegetation {
  position: absolute;
  transform: translateX(-50%);
  transition: opacity 0.5s, transform 0.5s;
  z-index: 4;
}

.vegetation-tree .veg-top {
  width: 100%;
  height: 70%;
  background: radial-gradient(ellipse at center, #3d7a3d 0%, #2d5a2d 70%, #1e4a1e 100%);
  border-radius: 50% 50% 40% 40%;
}

.vegetation-tree .veg-trunk {
  width: 20%;
  height: 35%;
  margin: 0 auto;
  background: linear-gradient(90deg, #5d4037 0%, #8b6914 50%, #5d4037 100%);
  border-radius: 2px;
}

.vegetation-bush {
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, #2d5a2d 0%, #1e4a1e 100%);
  border-radius: 50%;
}

/* Health states */
.vegetation.healthy .veg-top,
.vegetation.healthy.vegetation-bush {
  background: radial-gradient(ellipse at center, #3d7a3d 0%, #2d5a2d 70%, #1e4a1e 100%);
}

.vegetation.sick .veg-top,
.vegetation.sick.vegetation-bush {
  background: radial-gradient(ellipse at center, #8b6914 0%, #654321 70%, #4a3f2f 100%);
  transform: translateX(-50%) rotate(-5deg) scale(0.9);
}

.vegetation.dead .veg-top,
.vegetation.dead.vegetation-bush {
  background: radial-gradient(ellipse at center, #4a4a4a 0%, #2a2a2a 70%, #1a1a1a 100%);
  transform: translateX(-50%) rotate(-10deg) scale(0.7);
  opacity: 0.6;
}

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

.instruction-overlay {
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
  z-index: 90;
}

.instruction-overlay.cooldown {
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

.game-over-stats {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.info-banner {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30, 86, 49, 0.9);
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid rgba(76, 175, 80, 0.5);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  max-width: 90%;
  z-index: 80;
}

.info-banner p {
  color: #c8e6c9;
  font-size: 12px;
  font-family: 'Georgia', 'Times New Roman', serif;
  margin: 0;
  line-height: 1.4;
}

/* Fade transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
