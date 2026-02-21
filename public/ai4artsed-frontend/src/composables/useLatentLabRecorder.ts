/**
 * Composable for recording Latent Lab experiment data.
 *
 * Always active (like Canvas recording) — every generation is persisted
 * to exports/json/ for research data export.
 *
 * Lazy start: the backend run folder is only created on the first record()
 * call, so navigating between tabs without generating creates no empty folders.
 *
 * Lifecycle:
 *   onMounted  → mark ready (no backend call)
 *   first record() → startRun() + save
 *   onUnmounted → endRun() (only if a run was started)
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
  let mounted = false

  async function startRun(): Promise<void> {
    if (runId.value) return // already started
    try {
      const { data } = await axios.post(`${BASE}/api/latent-lab/record/start`, {
        latent_lab_tool: toolType,
        device_id: deviceId,
      })
      runId.value = data.run_id
      isRecording.value = true
    } catch (err) {
      console.warn('[LatentLabRecorder] Failed to start run:', err)
    }
  }

  async function record(payload: RecordData): Promise<void> {
    // Lazy start: create run on first actual record
    if (!runId.value) await startRun()
    if (!runId.value) return // start failed
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
    if (!runId.value) return // nothing to end
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

  onMounted(() => {
    mounted = true
    isRecording.value = true
    recordCount.value = 0
  })

  onUnmounted(() => {
    mounted = false
    endRun()
  })

  return { isRecording, recordCount, record, startRun, endRun }
}
