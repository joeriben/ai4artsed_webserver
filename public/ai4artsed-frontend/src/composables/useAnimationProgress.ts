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
  /** Duration to show summary at 100% before looping (ms) */
  summaryPauseDuration?: number
}

/**
 * Composable for unified animation progress across all edutainment animations
 *
 * Features:
 * - Internal progress loops 0→100% over estimatedSeconds
 * - 5s pause at 100% to show summary, then restarts
 * - GPU polling with simulated fallback when GPU idle
 * - Energy/CO2 tracking across all cycles
 * - Computed comparison values for different animation themes
 */
export function useAnimationProgress(options: UseAnimationProgressOptions) {
  const {
    estimatedSeconds: estimatedSecondsOption,
    isActive: isActiveOption,
    summaryPauseDuration = 5000
  } = options

  // Normalize refs
  const estimatedSeconds = typeof estimatedSecondsOption === 'number'
    ? ref(estimatedSecondsOption)
    : estimatedSecondsOption
  const isActive = isActiveOption

  // ==================== Progress State ====================
  const internalProgress = ref(0)
  const isShowingSummary = ref(false)
  const cycleCount = ref(0)

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
   * Smartphone uses ~5W idle, German energy mix ~400g CO2/kWh
   * CO2 per hour of smartphone: 5W * 1h / 1000 * 400g = 2g/hour
   * Minutes to "save" X grams: X / 2 * 60 = X * 30 minutes
   */
  const smartphoneMinutes = computed(() => {
    return Math.round(totalCo2.value * 30)
  })

  /**
   * Tree absorption comparison (for Forest animation)
   * Average tree absorbs ~22kg CO2/year = 2.51g/hour
   * Hours for tree to absorb X grams: X / 2.51
   */
  const treeHours = computed(() => {
    return Math.round(totalCo2.value / 2.51)
  })

  /**
   * Arctic ice melt comparison (for Iceberg animation)
   * 1 ton CO2 = ~3m² sea ice loss × ~2m avg thickness = ~6m³
   * 1g CO2 = 6 cm³ ice melt
   */
  const iceMeltVolume = computed(() => {
    return Math.round(totalCo2.value * 6)
  })

  // ==================== Intervals ====================
  let progressInterval: number | null = null
  let gpuPollInterval: number | null = null
  let energyInterval: number | null = null
  let summaryTimeout: number | null = null

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
  }

  // ==================== Progress Animation ====================

  function startProgressLoop(): void {
    if (progressInterval) return

    const seconds = typeof estimatedSeconds.value === 'number'
      ? estimatedSeconds.value
      : 30

    // Calculate update rate: 100% over estimatedSeconds, update every 100ms
    const updateIntervalMs = 100
    const totalUpdates = (seconds * 1000) / updateIntervalMs
    const progressPerUpdate = 100 / totalUpdates

    progressInterval = window.setInterval(() => {
      if (isShowingSummary.value) return  // Paused during summary

      internalProgress.value += progressPerUpdate

      if (internalProgress.value >= 100) {
        internalProgress.value = 100
        showSummaryAndLoop()
      }
    }, updateIntervalMs)
  }

  function showSummaryAndLoop(): void {
    isShowingSummary.value = true

    // Clear any existing timeout
    if (summaryTimeout) {
      clearTimeout(summaryTimeout)
    }

    summaryTimeout = window.setTimeout(() => {
      // Only loop if still active
      if (isActive.value) {
        isShowingSummary.value = false
        internalProgress.value = 0
        cycleCount.value++
      }
    }, summaryPauseDuration)
  }

  // ==================== Lifecycle ====================

  function start(): void {
    // Reset progress state
    internalProgress.value = 0
    isShowingSummary.value = false

    // Don't reset energy totals - they accumulate across cycles
    // Only reset if this is the first start
    if (cycleCount.value === 0) {
      elapsedSeconds.value = 0
      totalEnergy.value = 0
      totalCo2.value = 0
      simulatedPower.value = 200
      simulatedTemp.value = 55
    }

    // Start GPU polling
    fetchGpuStats()
    if (!gpuPollInterval) {
      gpuPollInterval = window.setInterval(fetchGpuStats, 2000)
    }

    // Start energy tracking
    if (!energyInterval) {
      energyInterval = window.setInterval(updateEnergy, 1000)
    }

    // Start progress animation
    startProgressLoop()
  }

  function stop(): void {
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
    if (gpuPollInterval) {
      clearInterval(gpuPollInterval)
      gpuPollInterval = null
    }
    if (energyInterval) {
      clearInterval(energyInterval)
      energyInterval = null
    }
    if (summaryTimeout) {
      clearTimeout(summaryTimeout)
      summaryTimeout = null
    }
  }

  function reset(): void {
    stop()
    internalProgress.value = 0
    isShowingSummary.value = false
    cycleCount.value = 0
    elapsedSeconds.value = 0
    totalEnergy.value = 0
    totalCo2.value = 0
    simulatedPower.value = 200
    simulatedTemp.value = 55
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
    // Progress state
    internalProgress,
    isShowingSummary,
    cycleCount,

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
    treeHours,
    iceMeltVolume,

    // Lifecycle
    start,
    stop,
    reset
  }
}
