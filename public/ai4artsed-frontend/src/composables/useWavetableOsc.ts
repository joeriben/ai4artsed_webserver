/**
 * Composable for wavetable oscillator playback.
 *
 * Extracts single-cycle frames (2048 samples) from an AudioBuffer and
 * drives a phase-accumulator AudioWorklet for continuous oscillation.
 * Scan position morphs between frames for timbral control.
 */
import { ref, readonly } from 'vue'

const FRAME_SIZE = 2048
const MIN_FRAMES = 8

export function useWavetableOsc() {
  let ctx: AudioContext | null = null
  let workletNode: AudioWorkletNode | null = null
  let gainNode: GainNode | null = null
  let workletReady = false
  let frames: Float32Array[] = []

  const hasFrames = ref(false)
  const isPlaying = ref(false)
  const frameCount = ref(0)
  const currentFrequency = ref(440)

  function ensureContext(): AudioContext {
    if (!ctx || ctx.state === 'closed') {
      ctx = new AudioContext()
      workletReady = false
    }
    if (ctx.state === 'suspended') ctx.resume()
    return ctx
  }

  async function ensureWorklet(ac: AudioContext): Promise<void> {
    if (workletReady) return
    await ac.audioWorklet.addModule(
      new URL('../audio/wavetable-processor.ts', import.meta.url),
    )
    workletReady = true
  }

  function extractFrames(buffer: AudioBuffer): Float32Array[] {
    const nc = buffer.numberOfChannels
    const len = buffer.length
    // Sum to mono
    const mono = new Float32Array(len)
    for (let ch = 0; ch < nc; ch++) {
      const data = buffer.getChannelData(ch)
      for (let i = 0; i < len; i++) mono[i] = mono[i]! + data[i]!
    }
    if (nc > 1) {
      const scale = 1 / nc
      for (let i = 0; i < len; i++) mono[i] = mono[i]! * scale
    }

    // Chop into FRAME_SIZE frames
    const result: Float32Array[] = []
    let offset = 0
    while (offset + FRAME_SIZE <= len) {
      result.push(mono.slice(offset, offset + FRAME_SIZE))
      offset += FRAME_SIZE
    }

    // Need at least MIN_FRAMES for meaningful morphing
    if (result.length === 0) {
      // Buffer shorter than one frame — use what we have, zero-padded
      const padded = new Float32Array(FRAME_SIZE)
      padded.set(mono.subarray(0, Math.min(len, FRAME_SIZE)))
      result.push(padded)
    }
    while (result.length < MIN_FRAMES) {
      result.push(new Float32Array(result[result.length - 1]!))
    }

    return result
  }

  async function loadFrames(buffer: AudioBuffer): Promise<void> {
    frames = extractFrames(buffer)
    frameCount.value = frames.length
    hasFrames.value = true

    if (workletNode) {
      workletNode.port.postMessage({ frames })
    }
  }

  async function start(): Promise<void> {
    if (isPlaying.value) return
    const ac = ensureContext()
    await ensureWorklet(ac)

    // Create fresh node chain
    workletNode = new AudioWorkletNode(ac, 'wavetable-processor', {
      numberOfInputs: 0,
      numberOfOutputs: 1,
      outputChannelCount: [1],
    })
    gainNode = ac.createGain()
    gainNode.gain.value = 0.5
    workletNode.connect(gainNode)
    gainNode.connect(ac.destination)

    // Send frames if already loaded
    if (frames.length > 0) {
      workletNode.port.postMessage({ frames })
    }

    // Set initial frequency
    const freqParam = workletNode.parameters.get('frequency')
    if (freqParam) freqParam.value = currentFrequency.value

    isPlaying.value = true
  }

  function stop(): void {
    if (workletNode) {
      workletNode.disconnect()
      workletNode = null
    }
    if (gainNode) {
      gainNode.disconnect()
      gainNode = null
    }
    isPlaying.value = false
  }

  function setFrequency(hz: number): void {
    currentFrequency.value = Math.max(20, Math.min(20000, hz))
    if (workletNode) {
      const param = workletNode.parameters.get('frequency')
      if (param) param.value = currentFrequency.value
    }
  }

  function setFrequencyFromNote(midiNote: number): void {
    setFrequency(440 * Math.pow(2, (midiNote - 69) / 12))
  }

  function setScanPosition(pos: number): void {
    const clamped = Math.max(0, Math.min(1, pos))
    if (workletNode) {
      const param = workletNode.parameters.get('scanPosition')
      if (param) param.value = clamped
    }
  }

  function dispose(): void {
    stop()
    frames = []
    hasFrames.value = false
    frameCount.value = 0
    if (ctx && ctx.state !== 'closed') ctx.close()
    ctx = null
    workletReady = false
  }

  return {
    hasFrames: readonly(hasFrames),
    isPlaying: readonly(isPlaying),
    frameCount: readonly(frameCount),
    currentFrequency: readonly(currentFrequency),

    loadFrames,
    start,
    stop,
    setFrequency,
    setFrequencyFromNote,
    setScanPosition,
    dispose,
  }
}
