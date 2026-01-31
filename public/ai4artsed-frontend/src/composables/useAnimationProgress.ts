import { ref, computed, watch, onUnmounted, type Ref, type ComputedRef } from 'vue'

/**
 * GPU Realtime Stats from /api/settings/gpu-realtime
 */
export interface GpuRealtimeStats {
  available: boolean
  gpu_name?: string
  power_draw_watts?: number
  power_limit_watts?: number
  temperature_celsius?: number
  utilization_percent?: number
  memory_used_mb?: number
  memory_total_mb?: number
  memory_used_percent?: number
  co2_per_kwh_grams?: number
  error?: string
}

export interface UseAnimationProgressOptions {
  /** Estimated generation time in seconds (from output config) */
  estimatedSeconds: Ref<number> | ComputedRef<number> | number
  /** Whether generation is active (controls start/stop) */
  isActive: Ref<boolean> | ComputedRef<boolean>
}

/**
 * Composable for unified animation progress across all edutainment animations
 *
 * Two INDEPENDENT concerns:
 * 1. Progress loop: 0→100→0→100 continuously (based on estimatedSeconds)
 * 2. Summary visibility: Shows when first loop completes OR 10s elapsed, stays visible
 *
 * These are completely decoupled - the loop doesn't care about summary, summary doesn't affect loop.
 */
export function useAnimationProgress(options: UseAnimationProgressOptions) {
  const {
    estimatedSeconds: estimatedSecondsOption,
    isActive: isActiveOption
  } = options

  // Normalize refs
  const estimatedSeconds = typeof estimatedSecondsOption === 'number'
    ? ref(estimatedSecondsOption)
    : estimatedSecondsOption
  const isActive = isActiveOption

  // ==================== Progress State (Independent) ====================
  const internalProgress = ref(0)
  const cycleCount = ref(0)

  // ==================== Summary State (Independent) ====================
  // Once true, stays true until generation ends
  const summaryShown = ref(false)

  // ==================== GPU/Energy State ====================
  const gpuStats = ref<GpuRealtimeStats>({ available: false })
  const elapsedSeconds = ref(0)
  const totalEnergy = ref(0)  // Wh
  const totalCo2 = ref(0)     // grams

  // Simulated values for when GPU is idle
  const simulatedPower = ref(200)
  const simulatedTemp = ref(55)

  // ==================== Computed Values ====================

  /** Effective power: real GPU if active (>100W), otherwise simulated */
  const effectivePower = computed(() => {
    const realPower = gpuStats.value.power_draw_watts || 0
    return realPower > 100 ? realPower : simulatedPower.value
  })

  /** Effective temperature: real GPU if active, otherwise simulated */
  const effectiveTemp = computed(() => {
    const realPower = gpuStats.value.power_draw_watts || 0
    const realTemp = gpuStats.value.temperature_celsius || 0
    return realPower > 100 ? realTemp : simulatedTemp.value
  })

  /**
   * Smartphone comparison (for Pixel animation)
   */
  const smartphoneMinutes = computed(() => {
    return Math.round(totalCo2.value * 30)
  })

  /**
   * Tree absorption comparison (for Forest animation)
   * A tree absorbs ~2.51g CO2 per hour = ~0.042g per minute
   */
  const treeMinutes = computed(() => {
    return Math.round(totalCo2.value * 60 / 2.51)
  })

  /**
   * Arctic ice melt comparison (for Iceberg animation)
   */
  const iceMeltVolume = computed(() => {
    return Math.round(totalCo2.value * 6)
  })

  // ==================== Animation Loop State ====================
  let animationFrameId: number | null = null
  let animationStartTime: number = 0

  // ==================== Consolidated Timer ====================
  let consolidatedInterval: number | null = null
  let tickCount = 0

  // ==================== GPU Fetching ====================

  async function fetchGpuStats(): Promise<void> {
    try {
      const response = await fetch('/api/settings/gpu-realtime')
      if (response.ok) {
        gpuStats.value = await response.json()
      }
    } catch (error) {
      console.warn('[AnimationProgress] GPU fetch failed:', error)
    }
  }

  // ==================== Energy Tracking ====================

  function updateEnergy(): void {
    elapsedSeconds.value++

    // Simulation ramps up over time
    simulatedPower.value = Math.min(450, 150 + elapsedSeconds.value * 15 + Math.random() * 50)
    simulatedTemp.value = Math.min(82, 45 + elapsedSeconds.value * 2 + Math.random() * 3)

    const watts = effectivePower.value
    const co2PerKwh = gpuStats.value.co2_per_kwh_grams || 400

    // Energy: Watts / 3600 = Wh per second
    const whThisSecond = watts / 3600
    totalEnergy.value += whThisSecond

    // CO2: Wh / 1000 * g/kWh
    const co2ThisSecond = (whThisSecond / 1000) * co2PerKwh
    totalCo2.value += co2ThisSecond

    // Fallback: show summary after 10 seconds even if loop hasn't completed
    // (Primary trigger is in animationLoop when progress hits 100%)
    if (!summaryShown.value && elapsedSeconds.value >= 10) {
      summaryShown.value = true
    }
  }

  // ==================== Consolidated Timer Tick ====================

  function consolidatedTick(): void {
    tickCount++
    updateEnergy()
    if (tickCount % 2 === 0) {
      fetchGpuStats()
    }
  }

  // ==================== Progress Loop (completely independent) ====================

  function animationLoop(currentTime: number): void {
    if (!isActive.value) return

    const durationMs = (typeof estimatedSeconds.value === 'number'
      ? estimatedSeconds.value
      : 30) * 1000

    const elapsed = currentTime - animationStartTime
    const progress = (elapsed / durationMs) * 100

    if (progress >= 100) {
      // Loop: reset to 0 and continue
      internalProgress.value = 0
      cycleCount.value++
      animationStartTime = currentTime
      // Show summary after first complete cycle
      if (!summaryShown.value) {
        summaryShown.value = true
      }
    } else {
      internalProgress.value = progress
    }

    animationFrameId = requestAnimationFrame(animationLoop)
  }

  function startProgressLoop(): void {
    if (animationFrameId) return
    animationStartTime = performance.now()
    animationFrameId = requestAnimationFrame(animationLoop)
  }

  // ==================== Lifecycle ====================

  function start(): void {
    internalProgress.value = 0
    summaryShown.value = false

    if (cycleCount.value === 0) {
      elapsedSeconds.value = 0
      totalEnergy.value = 0
      totalCo2.value = 0
      simulatedPower.value = 200
      simulatedTemp.value = 55
      tickCount = 0
    }

    fetchGpuStats()
    if (!consolidatedInterval) {
      consolidatedInterval = window.setInterval(consolidatedTick, 1000)
    }

    startProgressLoop()
  }

  function stop(): void {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }
    if (consolidatedInterval) {
      clearInterval(consolidatedInterval)
      consolidatedInterval = null
    }
  }

  function reset(): void {
    stop()
    internalProgress.value = 0
    cycleCount.value = 0
    elapsedSeconds.value = 0
    totalEnergy.value = 0
    totalCo2.value = 0
    simulatedPower.value = 200
    simulatedTemp.value = 55
    tickCount = 0
    summaryShown.value = false
  }

  // ==================== Watch isActive ====================

  watch(isActive, (active, wasActive) => {
    if (active && !wasActive) {
      start()
    } else if (!active && wasActive) {
      stop()
    }
  }, { immediate: true })

  // ==================== Cleanup ====================

  onUnmounted(() => {
    stop()
  })

  return {
    // Progress (loops independently)
    internalProgress,
    cycleCount,

    // Summary visibility (independent, sticky once true)
    summaryShown,

    // GPU/Energy state
    gpuStats,
    elapsedSeconds,
    totalEnergy,
    totalCo2,
    effectivePower,
    effectiveTemp,
    simulatedPower,
    simulatedTemp,

    // Comparison values
    smartphoneMinutes,
    treeMinutes,
    iceMeltVolume,

    // Lifecycle
    start,
    stop,
    reset
  }
}
