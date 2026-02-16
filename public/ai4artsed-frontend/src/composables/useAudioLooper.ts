/**
 * Web Audio API looper composable for Crossmodal Lab Synth tab.
 *
 * - Equal-power crossfade (piecewise linearRamp following sin/cos curve)
 * - Cross-correlation loop-point optimization for seamless oscillator-like loops
 * - OLA (Overlap-Add) pitch shifting: transpose without tempo change
 * - Adjustable crossfade duration, loop interval, pitch transposition
 * - Peak normalization (playback only), raw/loop WAV export
 *
 * AudioContext is created lazily on first play() call (browser autoplay policy).
 *
 * Equal-power crossfade: Boris Smus, "Web Audio API" (O'Reilly, 2013), Ch. 3
 * https://webaudioapi.com/book/Web_Audio_API_Boris_Smus_html/ch03.html
 * License: CC-BY-NC-ND 3.0
 *
 * OLA pitch shifting: Standard time-domain Overlap-Add technique.
 * Time stretch via analysis/synthesis hop ratio, then linear resample
 * to original length. Hann window for smooth grain overlap.
 * Reference: Zölzer, "DAFX: Digital Audio Effects" (Wiley, 2011), Ch. 7.
 */
import { ref, readonly } from 'vue'

// ═══════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════

const EP_STEPS = 16
const LOOP_FADE_MS = 5
// OLA pitch shift
const OLA_GRAIN_SIZE = 2048 // ~46ms at 44.1kHz
const OLA_OVERLAP = 4       // 75% overlap → hop = grain/4
// Loop optimization
const XCORR_WINDOW = 512    // comparison window (samples)
const XCORR_SEARCH = 2000   // search radius (samples)

// ═══════════════════════════════════════════════════════════════════
// DSP utilities (stateless, pure functions)
// ═══════════════════════════════════════════════════════════════════

// Pre-computed Hann window for OLA
const hannWindow = new Float32Array(OLA_GRAIN_SIZE)
for (let i = 0; i < OLA_GRAIN_SIZE; i++) {
  hannWindow[i] = 0.5 * (1 - Math.cos(2 * Math.PI * i / OLA_GRAIN_SIZE))
}

function scheduleEqualPowerFade(
  param: AudioParam, startVal: number, _endVal: number,
  startTime: number, duration: number, direction: 'in' | 'out',
) {
  param.cancelScheduledValues(startTime)
  param.setValueAtTime(startVal, startTime)
  for (let i = 1; i <= EP_STEPS; i++) {
    const t = i / EP_STEPS
    const curve = direction === 'out'
      ? Math.cos(t * Math.PI * 0.5)
      : Math.sin(t * Math.PI * 0.5)
    const val = direction === 'out' ? startVal * curve : 1 * curve
    param.linearRampToValueAtTime(val, startTime + t * duration)
  }
}

function encodeWav(buffer: AudioBuffer, startSample: number, endSample: number): Blob {
  const nc = buffer.numberOfChannels, sr = buffer.sampleRate
  const len = endSample - startSample, ds = len * nc * 2
  const ab = new ArrayBuffer(44 + ds), v = new DataView(ab)
  const ws = (o: number, s: string) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)) }
  ws(0, 'RIFF'); v.setUint32(4, 36 + ds, true); ws(8, 'WAVE'); ws(12, 'fmt ')
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, nc, true)
  v.setUint32(24, sr, true); v.setUint32(28, sr * nc * 2, true)
  v.setUint16(32, nc * 2, true); v.setUint16(34, 16, true); ws(36, 'data'); v.setUint32(40, ds, true)
  const chs: Float32Array[] = []
  for (let c = 0; c < nc; c++) chs.push(buffer.getChannelData(c))
  let off = 44
  for (let i = startSample; i < endSample; i++) {
    for (let c = 0; c < nc; c++) {
      const s = Math.max(-1, Math.min(1, chs[c]![i]!))
      v.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7fff, true); off += 2
    }
  }
  return new Blob([ab], { type: 'audio/wav' })
}

/**
 * Cross-correlation loop-point optimizer.
 * Finds the best loopEnd position (near the user's choice) where the waveform
 * at the end of the loop best matches the waveform at the start.
 * Uses normalized cross-correlation on channel 0.
 */
function optimizeLoopEndSample(
  data: Float32Array, loopStart: number, loopEnd: number,
): number {
  const win = Math.min(XCORR_WINDOW, Math.floor((loopEnd - loopStart) / 4))
  if (win < 16) return loopEnd

  // Reference: first `win` samples of the loop
  const searchLo = Math.max(loopStart + win * 2, loopEnd - XCORR_SEARCH)
  const searchHi = Math.min(data.length, loopEnd + XCORR_SEARCH)

  let bestCorr = -Infinity
  let bestEnd = loopEnd

  for (let cand = searchLo; cand < searchHi; cand++) {
    const eStart = cand - win
    if (eStart < loopStart) continue

    let sum = 0, normA = 0, normB = 0
    for (let i = 0; i < win; i++) {
      const a = data[loopStart + i]!
      const b = data[eStart + i]!
      sum += a * b
      normA += a * a
      normB += b * b
    }
    const denom = Math.sqrt(normA * normB)
    const corr = denom > 0 ? sum / denom : 0

    if (corr > bestCorr) {
      bestCorr = corr
      bestEnd = cand
    }
  }
  return bestEnd
}

/**
 * Apply micro-fade at loop boundaries + optional cross-correlation optimization.
 */
function applyLoopProcessing(
  ac: AudioContext, source: AudioBuffer,
  loopStart: number, loopEnd: number, optimize: boolean,
): { buffer: AudioBuffer; optimizedEnd: number } {
  const copy = ac.createBuffer(source.numberOfChannels, source.length, source.sampleRate)
  for (let ch = 0; ch < source.numberOfChannels; ch++) {
    copy.getChannelData(ch).set(source.getChannelData(ch))
  }

  let actualEnd = loopEnd
  if (optimize && source.numberOfChannels > 0) {
    actualEnd = optimizeLoopEndSample(source.getChannelData(0), loopStart, loopEnd)
  }

  const loopLen = actualEnd - loopStart
  const fadeSamples = Math.min(
    Math.floor(LOOP_FADE_MS / 1000 * source.sampleRate),
    Math.floor(loopLen / 4),
  )
  if (fadeSamples >= 2) {
    for (let ch = 0; ch < copy.numberOfChannels; ch++) {
      const d = copy.getChannelData(ch)
      for (let i = 0; i < fadeSamples; i++) {
        const g = Math.sin((i / fadeSamples) * Math.PI * 0.5)
        d[loopStart + i]! *= g
        d[actualEnd - 1 - i]! *= g
      }
    }
  }

  return { buffer: copy, optimizedEnd: actualEnd }
}

/**
 * OLA (Overlap-Add) pitch shift.
 * Time-stretches by 1/rate via different analysis/synthesis hops,
 * then resamples to original length → pitch shift without tempo change.
 */
function olaPitchShift(input: Float32Array, semitones: number): Float32Array {
  if (semitones === 0) return input
  const rate = Math.pow(2, semitones / 12)
  const alpha = 1 / rate // time stretch factor
  const analysisHop = Math.floor(OLA_GRAIN_SIZE / OLA_OVERLAP)
  const synthesisHop = Math.max(1, Math.round(analysisHop * alpha))
  const inputLen = input.length

  // Phase 1: OLA time stretch
  // Output length after stretch
  const numGrains = Math.floor((inputLen - OLA_GRAIN_SIZE) / analysisHop) + 1
  const stretchedLen = (numGrains - 1) * synthesisHop + OLA_GRAIN_SIZE
  const stretched = new Float32Array(stretchedLen)

  let inPos = 0
  let outPos = 0
  for (let g = 0; g < numGrains; g++) {
    for (let i = 0; i < OLA_GRAIN_SIZE; i++) {
      const idx = inPos + i
      if (idx < inputLen) {
        stretched[outPos + i]! += input[idx]! * hannWindow[i]!
      }
    }
    inPos += analysisHop
    outPos += synthesisHop
  }

  // Phase 2: Resample stretched → original length (linear interpolation)
  const output = new Float32Array(inputLen)
  const ratio = stretchedLen / inputLen
  for (let i = 0; i < inputLen; i++) {
    const readPos = i * ratio
    const idx0 = Math.floor(readPos)
    const frac = readPos - idx0
    const s0 = idx0 < stretchedLen ? stretched[idx0]! : 0
    const s1 = idx0 + 1 < stretchedLen ? stretched[idx0 + 1]! : 0
    output[i] = s0 + (s1 - s0) * frac
  }
  return output
}

/**
 * Apply OLA pitch shift to an AudioBuffer (all channels).
 */
function pitchShiftBuffer(ac: AudioContext, source: AudioBuffer, semitones: number): AudioBuffer {
  if (semitones === 0) return source
  const result = ac.createBuffer(source.numberOfChannels, source.length, source.sampleRate)
  for (let ch = 0; ch < source.numberOfChannels; ch++) {
    const shifted = olaPitchShift(source.getChannelData(ch), semitones)
    result.getChannelData(ch).set(shifted)
  }
  return result
}

// ═══════════════════════════════════════════════════════════════════
// Composable
// ═══════════════════════════════════════════════════════════════════

export type TransposeMode = 'rate' | 'pitch'

export function useAudioLooper() {
  let ctx: AudioContext | null = null
  let activeSource: AudioBufferSourceNode | null = null
  let activeGain: GainNode | null = null
  let originalBuffer: AudioBuffer | null = null
  let rawBase64: string | null = null

  const isPlaying = ref(false)
  const isLooping = ref(true)
  const transposeSemitones = ref(0)
  const transposeMode = ref<TransposeMode>('rate')
  const loopStartFrac = ref(0)
  const loopEndFrac = ref(1)
  const bufferDuration = ref(0)
  const hasAudio = ref(false)
  const crossfadeMs = ref(150)
  const normalizeOn = ref(false)
  const peakAmplitude = ref(0)
  const loopOptimize = ref(false)
  // Optimized loop end as fraction (for display, may differ from user's loopEndFrac)
  const optimizedEndFrac = ref(1)

  function ensureContext(): AudioContext {
    if (!ctx || ctx.state === 'closed') ctx = new AudioContext()
    if (ctx.state === 'suspended') ctx.resume()
    return ctx
  }

  function rateForPlayback(): number {
    return transposeMode.value === 'rate'
      ? Math.pow(2, transposeSemitones.value / 12)
      : 1 // OLA mode: pitch baked into buffer, play at normal rate
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
      const d = buffer.getChannelData(ch)
      for (let i = 0; i < d.length; i++) {
        const a = Math.abs(d[i]!)
        if (a > peak) peak = a
      }
    }
    return peak
  }

  function normalizeBuffer(buffer: AudioBuffer): void {
    const peak = measurePeak(buffer)
    if (peak < 0.001) return
    const g = 0.95 / peak
    for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
      const d = buffer.getChannelData(ch)
      for (let i = 0; i < d.length; i++) d[i]! *= g
    }
  }

  async function decodeBase64Wav(base64: string): Promise<AudioBuffer> {
    const ac = ensureContext()
    const bin = atob(base64)
    const bytes = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
    return ac.decodeAudioData(bytes.buffer)
  }

  function createSource(ac: AudioContext, buffer: AudioBuffer): AudioBufferSourceNode {
    const src = ac.createBufferSource()
    src.buffer = buffer
    src.loop = isLooping.value
    src.playbackRate.value = rateForPlayback()
    const dur = buffer.duration
    // Use optimized end for loop bounds
    src.loopStart = loopStartFrac.value * dur
    src.loopEnd = optimizedEndFrac.value * dur
    return src
  }

  function prepareBuffer(ac: AudioContext, source: AudioBuffer): AudioBuffer {
    const [ls, le] = loopBoundsSamples(source)

    // 1. Loop processing (micro-fade + optional optimization)
    const { buffer: loopProcessed, optimizedEnd } =
      applyLoopProcessing(ac, source, ls, le, loopOptimize.value)
    optimizedEndFrac.value = optimizedEnd / source.length

    // 2. OLA pitch shift (if in pitch mode and transposed)
    let processed = loopProcessed
    if (transposeMode.value === 'pitch' && transposeSemitones.value !== 0) {
      processed = pitchShiftBuffer(ac, loopProcessed, transposeSemitones.value)
    }

    // 3. Normalize (if enabled)
    if (normalizeOn.value) normalizeBuffer(processed)

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
        try { oldSource.stop() } catch { /* */ }
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
    startSource(ac, prepareBuffer(ac, decoded))
  }

  function replay() {
    if (!originalBuffer) return
    const ac = ensureContext()
    startSource(ac, prepareBuffer(ac, originalBuffer))
  }

  function stop() {
    if (activeSource) { try { activeSource.stop() } catch { /* */ } activeSource = null }
    if (activeGain) { activeGain.disconnect(); activeGain = null }
    isPlaying.value = false
  }

  function setLoop(on: boolean) {
    isLooping.value = on
    if (activeSource) activeSource.loop = on
  }

  function setTranspose(semitones: number) {
    transposeSemitones.value = semitones
    if (transposeMode.value === 'rate') {
      // Instant: just change playback rate
      if (activeSource) activeSource.playbackRate.value = rateForPlayback()
    } else {
      // OLA: re-process buffer and crossfade
      if (originalBuffer && isPlaying.value) replay()
    }
  }

  function setTransposeMode(mode: TransposeMode) {
    transposeMode.value = mode
    if (originalBuffer && isPlaying.value) replay()
  }

  function setLoopStart(frac: number) {
    loopStartFrac.value = Math.max(0, Math.min(frac, loopEndFrac.value - 0.01))
    if (activeSource?.buffer) {
      activeSource.loopStart = loopStartFrac.value * activeSource.buffer.duration
    }
  }

  function setLoopEnd(frac: number) {
    loopEndFrac.value = Math.max(loopStartFrac.value + 0.01, Math.min(frac, 1))
    // Also update optimized end (without optimization, they're the same)
    optimizedEndFrac.value = loopEndFrac.value
    if (activeSource?.buffer) {
      activeSource.loopEnd = loopEndFrac.value * activeSource.buffer.duration
    }
  }

  function setCrossfade(ms: number) {
    crossfadeMs.value = Math.max(10, Math.min(ms, 500))
  }

  function setNormalize(on: boolean) {
    normalizeOn.value = on
    if (originalBuffer && isPlaying.value) replay()
  }

  function setLoopOptimize(on: boolean) {
    loopOptimize.value = on
    if (originalBuffer && isPlaying.value) replay()
  }

  function exportRaw(): Blob | null {
    if (!rawBase64) return null
    const bin = atob(rawBase64)
    const bytes = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
    return new Blob([bytes], { type: 'audio/wav' })
  }

  function exportLoop(): Blob | null {
    if (!originalBuffer) return null
    const [s, e] = loopBoundsSamples(originalBuffer)
    if (e <= s) return null
    return encodeWav(originalBuffer, s, e)
  }

  function dispose() {
    stop()
    originalBuffer = null; rawBase64 = null; hasAudio.value = false
    if (ctx && ctx.state !== 'closed') ctx.close()
    ctx = null
  }

  return {
    play, replay, stop,
    setLoop, setTranspose, setTransposeMode,
    setLoopStart, setLoopEnd, setLoopOptimize,
    setCrossfade, setNormalize,
    exportRaw, exportLoop, dispose,
    isPlaying: readonly(isPlaying),
    isLooping: readonly(isLooping),
    transposeSemitones: readonly(transposeSemitones),
    transposeMode: readonly(transposeMode),
    loopStartFrac: readonly(loopStartFrac),
    loopEndFrac: readonly(loopEndFrac),
    optimizedEndFrac: readonly(optimizedEndFrac),
    bufferDuration: readonly(bufferDuration),
    hasAudio: readonly(hasAudio),
    crossfadeMs: readonly(crossfadeMs),
    normalizeOn: readonly(normalizeOn),
    peakAmplitude: readonly(peakAmplitude),
    loopOptimize: readonly(loopOptimize),
  }
}
