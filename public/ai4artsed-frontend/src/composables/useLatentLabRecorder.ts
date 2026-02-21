/**
 * Composable for recording Latent Lab experiment data.
 *
 * Always active (like Canvas recording) — every generation is persisted
 * to exports/json/ for research data export.
 *
 * Lifecycle:
 *   onMounted  → startRun()
 *   after each generation → record(...)
 *   onUnmounted → endRun()
 */
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useDeviceId } from './useDeviceId'

const BASE = import.meta.env.DEV ? 'http://localhost:17802' : ''

export interface RecordOutput {
  type: 'image' | 'audio' | 'text'
  format: string        // png, jpg, wav, json …
  dataBase64: string
}

export interface RecordStep {
  format: string        // jpg, png
  dataBase64: string
}

export interface RecordData {
  parameters: Record<string, unknown>
  results?: Record<string, unknown>
  outputs?: RecordOutput[]
  steps?: RecordStep[]
}

export function useLatentLabRecorder(toolType: string) {
  const runId = ref<string | null>(null)
  const isRecording = ref(false)
  const recordCount = ref(0)
  const deviceId = useDeviceId()

  async function startRun(): Promise<void> {
    try {
      const { data } = await axios.post(`${BASE}/api/latent-lab/record/start`, {
        latent_lab_tool: toolType,
        device_id: deviceId,
      })
      runId.value = data.run_id
      isRecording.value = true
      recordCount.value = 0
    } catch (err) {
      console.warn('[LatentLabRecorder] Failed to start run:', err)
    }
  }

  async function record(payload: RecordData): Promise<void> {
    if (!runId.value) return
    try {
      await axios.post(`${BASE}/api/latent-lab/record/save`, {
        run_id: runId.value,
        parameters: payload.parameters,
        results: payload.results,
        outputs: payload.outputs,
        steps: payload.steps,
      })
      recordCount.value++
    } catch (err) {
      console.warn('[LatentLabRecorder] Failed to save:', err)
    }
  }

  async function endRun(): Promise<void> {
    if (!runId.value) return
    try {
      await axios.post(`${BASE}/api/latent-lab/record/end`, {
        run_id: runId.value,
      })
    } catch (err) {
      console.warn('[LatentLabRecorder] Failed to end run:', err)
    } finally {
      isRecording.value = false
      runId.value = null
    }
  }

  onMounted(() => { startRun() })
  onUnmounted(() => { endRun() })

  return { isRecording, recordCount, record, startRun, endRun }
}
