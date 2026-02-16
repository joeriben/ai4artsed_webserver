/**
 * Web Audio API looper composable for Crossmodal Lab Synth tab.
 *
 * - Equal-power crossfade (piecewise linearRamp following sin/cos curve)
 *   for glitch-free buffer swaps
 * - Loop-point micro-fade baked into buffer to eliminate phase discontinuity
 * - Adjustable crossfade duration, loop interval, pitch transposition
 * - Raw and loop-region WAV export
 *
 * AudioContext is created lazily on first play() call (browser autoplay policy).
 *
 * Equal-power crossfade algorithm: sin²+cos²=1 constant-energy curve.
 * Reference: Boris Smus, "Web Audio API" (O'Reilly, 2013), Chapter 3.
 * https://webaudioapi.com/book/Web_Audio_API_Boris_Smus_html/ch03.html
 * License: CC-BY-NC-ND 3.0
 */
import { ref, readonly } from 'vue'

// Number of linearRamp segments approximating the equal-power curve
const EP_STEPS = 16
// Fixed micro-fade at loop boundaries (samples) to kill phase-discontinuity clicks
const LOOP_FADE_MS = 5

/**
 * Schedule an equal-power fade on a GainNode using piecewise linearRamp.
 * Each segment is natively per-sample smooth in the audio thread.
 */
function scheduleEqualPowerFade(
  param: AudioParam,
  startVal: number,
  endVal: number,
  startTime: number,
  duration: number,
  direction: 'in' | 'out',
) {
  param.cancelScheduledValues(startTime)
  param.setValueAtTime(startVal, startTime)
  for (let i = 1; i <= EP_STEPS; i++) {
    const t = i / EP_STEPS
    const curve = direction === 'out'
      ? Math.cos(t * Math.PI * 0.5)
      : Math.sin(t * Math.PI * 0.5)
    // Scale: startVal→endVal following the curve shape
    const val = direction === 'out'
      ? startVal * curve
      : endVal * curve
    param.linearRampToValueAtTime(val, startTime + t * duration)
  }
}

/**
 * Encode an AudioBuffer slice as 16-bit PCM WAV.
 */
function encodeWav(buffer: AudioBuffer, startSample: number, endSample: number): Blob {
  const numChannels = buffer.numberOfChannels
  const sampleRate = buffer.sampleRate
  const length = endSample - startSample
  const dataSize = length * numChannels * 2
  const buf = new ArrayBuffer(44 + dataSize)
  const v = new DataView(buf)

  function ws(o: number, s: string) { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)) }

  ws(0, 'RIFF'); v.setUint32(4, 36 + dataSize, true)
  ws(8, 'WAVE'); ws(12, 'fmt ')
  v.setUint32(16, 16, true); v.setUint16(20, 1, true)
  v.setUint16(22, numChannels, true); v.setUint32(24, sampleRate, true)
  v.setUint32(28, sampleRate * numChannels * 2, true)
  v.setUint16(32, numChannels * 2, true); v.setUint16(34, 16, true)
  ws(36, 'data'); v.setUint32(40, dataSize, true)

  const channels: Float32Array[] = []
  for (let ch = 0; ch < numChannels; ch++) channels.push(buffer.getChannelData(ch))

  let off = 44
  for (let i = startSample; i < endSample; i++) {
    for (let ch = 0; ch < numChannels; ch++) {
      const s = Math.max(-1, Math.min(1, channels[ch]![i]!))
      v.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7fff, true)
      off += 2
    }
  }
  return new Blob([buf], { type: 'audio/wav' })
}

/**
 * Create a buffer copy with micro-fade at loop boundaries to eliminate clicks.
 */
function applyLoopFade(
  ac: AudioContext,
  source: AudioBuffer,
  loopStartSample: number,
  loopEndSample: number,
): AudioBuffer {
  const copy = ac.createBuffer(source.numberOfChannels, source.length, source.sampleRate)
  for (let ch = 0; ch < source.numberOfChannels; ch++) {
    copy.getChannelData(ch).set(source.getChannelData(ch))
  }

  const loopLen = loopEndSample - loopStartSample
  const fadeSamples = Math.min(
    Math.floor(LOOP_FADE_MS / 1000 * source.sampleRate),
    Math.floor(loopLen / 4), // never more than 25% of loop
  )
  if (fadeSamples < 2) return copy

  for (let ch = 0; ch < copy.numberOfChannels; ch++) {
    const data = copy.getChannelData(ch)
    for (let i = 0; i < fadeSamples; i++) {
      const t = i / fadeSamples
      const gain = Math.sin(t * Math.PI * 0.5) // 0→1
      // Fade-in at loop start
      data[loopStartSample + i]! *= gain
      // Fade-out at loop end (mirror)
      data[loopEndSample - 1 - i]! *= gain
    }
  }
  return copy
}

export function useAudioLooper() {
  let ctx: AudioContext | null = null
  let activeSource: AudioBufferSourceNode | null = null
  let activeGain: GainNode | null = null
  let originalBuffer: AudioBuffer | null = null
  let rawBase64: string | null = null

  const isPlaying = ref(false)
  const isLooping = ref(true)
  const transposeSemitones = ref(0)
  const loopStartFrac = ref(0)
  const loopEndFrac = ref(1)
  const bufferDuration = ref(0)
  const hasAudio = ref(false)
  const crossfadeMs = ref(150)
  const normalize = ref(false)
  // Peak amplitude of the original (unmodified) buffer, for display
  const peakAmplitude = ref(0)

  function ensureContext(): AudioContext {
    if (!ctx || ctx.state === 'closed') {
      ctx = new AudioContext()
    }
    if (ctx.state === 'suspended') {
      ctx.resume()
    }
    return ctx
  }

  function currentPlaybackRate(): number {
    return Math.pow(2, transposeSemitones.value / 12)
  }

  function loopBoundsSamples(buf: AudioBuffer): [number, number] {
    return [
      Math.floor(loopStartFrac.value * buf.length),
      Math.min(buf.length, Math.ceil(loopEndFrac.value * buf.length)),
    ]
  }

  function measurePeak(buffer: AudioBuffer): number {
    let peak = 0
    for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
      const data = buffer.getChannelData(ch)
      for (let i = 0; i < data.length; i++) {
        const abs = Math.abs(data[i]!)
        if (abs > peak) peak = abs
      }
    }
    return peak
  }

  function normalizeBuffer(buffer: AudioBuffer): void {
    const peak = measurePeak(buffer)
    if (peak < 0.001) return
    const gain = 0.95 / peak
    for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
      const data = buffer.getChannelData(ch)
      for (let i = 0; i < data.length; i++) {
        data[i]! *= gain
      }
    }
  }

  async function decodeBase64Wav(base64: string): Promise<AudioBuffer> {
    const ac = ensureContext()
    const binaryStr = atob(base64)
    const bytes = new Uint8Array(binaryStr.length)
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i)
    }
    return ac.decodeAudioData(bytes.buffer)
  }

  function createSource(ac: AudioContext, buffer: AudioBuffer): AudioBufferSourceNode {
    const src = ac.createBufferSource()
    src.buffer = buffer
    src.loop = isLooping.value
    src.playbackRate.value = currentPlaybackRate()
    const dur = buffer.duration
    src.loopStart = loopStartFrac.value * dur
    src.loopEnd = loopEndFrac.value * dur
    return src
  }

  function prepareBuffer(ac: AudioContext, source: AudioBuffer): AudioBuffer {
    const [ls, le] = loopBoundsSamples(source)
    const processed = applyLoopFade(ac, source, ls, le)
    if (normalize.value) normalizeBuffer(processed)
    return processed
  }

  function startSource(ac: AudioContext, playBuffer: AudioBuffer) {
    const newGain = ac.createGain()
    newGain.connect(ac.destination)
    const newSource = createSource(ac, playBuffer)
    newSource.connect(newGain)

    const now = ac.currentTime
    const fadeSec = crossfadeMs.value / 1000

    if (activeSource && activeGain && isPlaying.value) {
      scheduleEqualPowerFade(activeGain.gain, activeGain.gain.value, 0, now, fadeSec, 'out')
      scheduleEqualPowerFade(newGain.gain, 0, 1, now, fadeSec, 'in')

      const oldSource = activeSource
      const oldGain = activeGain
      setTimeout(() => {
        try { oldSource.stop() } catch { /* already stopped */ }
        oldGain.disconnect()
      }, crossfadeMs.value + 50)
    } else {
      newGain.gain.setValueAtTime(1, now)
    }

    const offset = loopStartFrac.value * playBuffer.duration
    newSource.start(0, offset)
    newSource.onended = () => {
      if (newSource === activeSource) {
        isPlaying.value = false
        activeSource = null
        activeGain = null
      }
    }

    activeSource = newSource
    activeGain = newGain
    isPlaying.value = true
  }

  async function play(base64Wav: string) {
    const ac = ensureContext()
    const decoded = await decodeBase64Wav(base64Wav)
    originalBuffer = decoded
    rawBase64 = base64Wav
    bufferDuration.value = decoded.duration
    hasAudio.value = true
    peakAmplitude.value = measurePeak(decoded)

    const processed = prepareBuffer(ac, decoded)
    startSource(ac, processed)
  }

  /** Replay the last loaded buffer (after stop or loop-off playback ended). */
  function replay() {
    if (!originalBuffer) return
    const ac = ensureContext()
    const processed = prepareBuffer(ac, originalBuffer)
    startSource(ac, processed)
  }

  function stop() {
    if (activeSource) {
      try { activeSource.stop() } catch { /* already stopped */ }
      activeSource = null
    }
    if (activeGain) {
      activeGain.disconnect()
      activeGain = null
    }
    isPlaying.value = false
  }

  function setLoop(on: boolean) {
    isLooping.value = on
    if (activeSource) activeSource.loop = on
  }

  function setTranspose(semitones: number) {
    transposeSemitones.value = semitones
    if (activeSource) activeSource.playbackRate.value = currentPlaybackRate()
  }

  function setLoopStart(frac: number) {
    loopStartFrac.value = Math.max(0, Math.min(frac, loopEndFrac.value - 0.01))
    if (activeSource?.buffer) {
      activeSource.loopStart = loopStartFrac.value * activeSource.buffer.duration
    }
  }

  function setLoopEnd(frac: number) {
    loopEndFrac.value = Math.max(loopStartFrac.value + 0.01, Math.min(frac, 1))
    if (activeSource?.buffer) {
      activeSource.loopEnd = loopEndFrac.value * activeSource.buffer.duration
    }
  }

  function setCrossfade(ms: number) {
    crossfadeMs.value = Math.max(10, Math.min(ms, 500))
  }

  function setNormalize(on: boolean) {
    normalize.value = on
    // Re-start with normalized/unnormalized buffer if currently playing
    if (originalBuffer && isPlaying.value) {
      replay()
    }
  }

  function exportRaw(): Blob | null {
    if (!rawBase64) return null
    const binaryStr = atob(rawBase64)
    const bytes = new Uint8Array(binaryStr.length)
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i)
    }
    return new Blob([bytes], { type: 'audio/wav' })
  }

  function exportLoop(): Blob | null {
    if (!originalBuffer) return null
    const [startSample, endSample] = loopBoundsSamples(originalBuffer)
    if (endSample <= startSample) return null
    return encodeWav(originalBuffer, startSample, endSample)
  }

  function dispose() {
    stop()
    originalBuffer = null
    rawBase64 = null
    hasAudio.value = false
    if (ctx && ctx.state !== 'closed') {
      ctx.close()
    }
    ctx = null
  }

  return {
    play,
    replay,
    stop,
    setLoop,
    setTranspose,
    setLoopStart,
    setLoopEnd,
    setCrossfade,
    setNormalize,
    exportRaw,
    exportLoop,
    dispose,
    isPlaying: readonly(isPlaying),
    isLooping: readonly(isLooping),
    transposeSemitones: readonly(transposeSemitones),
    loopStartFrac: readonly(loopStartFrac),
    loopEndFrac: readonly(loopEndFrac),
    bufferDuration: readonly(bufferDuration),
    hasAudio: readonly(hasAudio),
    crossfadeMs: readonly(crossfadeMs),
    normalize: readonly(normalize),
    peakAmplitude: readonly(peakAmplitude),
  }
}
