/**
 * Web Audio API looper composable for Crossmodal Lab Synth tab.
 *
 * Double-buffered AudioBufferSourceNode with equal-power crossfade,
 * loop toggle, pitch transposition via playbackRate, adjustable
 * loop interval, and raw/loop WAV export.
 *
 * AudioContext is created lazily on first play() call to satisfy
 * browser autoplay policy (requires user gesture).
 *
 * Crossfade algorithm: Equal-power (constant energy) using sin/cos curves.
 * Based on Boris Smus, "Web Audio API" (O'Reilly, 2013), Chapter 3.
 * https://webaudioapi.com/book/Web_Audio_API_Boris_Smus_html/ch03.html
 * License: Creative Commons Attribution-NonCommercial-NoDerivs 3.0
 */
import { ref, readonly } from 'vue'

const CROSSFADE_MS = 150
const CURVE_RESOLUTION = 64

// Pre-compute equal-power crossfade curves (sin²+cos²=1 guarantees constant energy)
const fadeOutCurve = new Float32Array(CURVE_RESOLUTION)
const fadeInCurve = new Float32Array(CURVE_RESOLUTION)
for (let i = 0; i < CURVE_RESOLUTION; i++) {
  const t = i / (CURVE_RESOLUTION - 1)
  fadeOutCurve[i] = Math.cos(t * Math.PI * 0.5)
  fadeInCurve[i] = Math.sin(t * Math.PI * 0.5)
}

/**
 * Encode an AudioBuffer (or a slice of it) as a WAV Blob.
 */
function encodeWav(buffer: AudioBuffer, startSample: number, endSample: number): Blob {
  const numChannels = buffer.numberOfChannels
  const sampleRate = buffer.sampleRate
  const length = endSample - startSample
  const dataSize = length * numChannels * 2 // 16-bit PCM
  const headerSize = 44
  const arrayBuffer = new ArrayBuffer(headerSize + dataSize)
  const view = new DataView(arrayBuffer)

  function writeString(offset: number, str: string) {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i))
    }
  }

  writeString(0, 'RIFF')
  view.setUint32(4, 36 + dataSize, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * numChannels * 2, true)
  view.setUint16(32, numChannels * 2, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, dataSize, true)

  const channels: Float32Array[] = []
  for (let ch = 0; ch < numChannels; ch++) {
    channels.push(buffer.getChannelData(ch))
  }

  let offset = headerSize
  for (let i = startSample; i < endSample; i++) {
    for (let ch = 0; ch < numChannels; ch++) {
      const sample = Math.max(-1, Math.min(1, channels[ch]![i]!))
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
      offset += 2
    }
  }

  return new Blob([arrayBuffer], { type: 'audio/wav' })
}

export function useAudioLooper() {
  let ctx: AudioContext | null = null
  let activeSource: AudioBufferSourceNode | null = null
  let activeGain: GainNode | null = null
  let currentBuffer: AudioBuffer | null = null
  let rawBase64: string | null = null

  const isPlaying = ref(false)
  const isLooping = ref(true)
  const transposeSemitones = ref(0)
  const loopStartFrac = ref(0)
  const loopEndFrac = ref(1)
  const bufferDuration = ref(0)
  const hasAudio = ref(false)

  function ensureContext(): AudioContext {
    if (!ctx || ctx.state === 'closed') {
      ctx = new AudioContext()
    }
    if (ctx.state === 'suspended') {
      ctx.resume()
    }
    return ctx
  }

  function playbackRate(): number {
    return Math.pow(2, transposeSemitones.value / 12)
  }

  function applyLoopBounds(source: AudioBufferSourceNode) {
    if (!source.buffer) return
    const dur = source.buffer.duration
    source.loopStart = loopStartFrac.value * dur
    source.loopEnd = loopEndFrac.value * dur
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

  async function play(base64Wav: string) {
    const ac = ensureContext()
    const buffer = await decodeBase64Wav(base64Wav)
    currentBuffer = buffer
    rawBase64 = base64Wav
    bufferDuration.value = buffer.duration
    hasAudio.value = true

    const newGain = ac.createGain()
    newGain.connect(ac.destination)

    const newSource = ac.createBufferSource()
    newSource.buffer = buffer
    newSource.loop = isLooping.value
    newSource.playbackRate.value = playbackRate()
    applyLoopBounds(newSource)
    newSource.connect(newGain)

    const now = ac.currentTime
    const fadeSec = CROSSFADE_MS / 1000

    if (activeSource && activeGain) {
      // Equal-power crossfade: cos curve out, sin curve in
      activeGain.gain.setValueAtTime(activeGain.gain.value, now)
      activeGain.gain.setValueCurveAtTime(fadeOutCurve, now, fadeSec)

      newGain.gain.setValueAtTime(0, now)
      newGain.gain.setValueCurveAtTime(fadeInCurve, now, fadeSec)

      const oldSource = activeSource
      const oldGain = activeGain
      setTimeout(() => {
        try { oldSource.stop() } catch { /* already stopped */ }
        oldGain.disconnect()
      }, CROSSFADE_MS + 50)
    } else {
      newGain.gain.setValueAtTime(1, now)
    }

    const offset = loopStartFrac.value * buffer.duration
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
    if (activeSource) {
      activeSource.loop = on
    }
  }

  function setTranspose(semitones: number) {
    transposeSemitones.value = semitones
    if (activeSource) {
      activeSource.playbackRate.value = playbackRate()
    }
  }

  function setLoopStart(frac: number) {
    loopStartFrac.value = Math.max(0, Math.min(frac, loopEndFrac.value - 0.01))
    if (activeSource) applyLoopBounds(activeSource)
  }

  function setLoopEnd(frac: number) {
    loopEndFrac.value = Math.max(loopStartFrac.value + 0.01, Math.min(frac, 1))
    if (activeSource) applyLoopBounds(activeSource)
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
    if (!currentBuffer) return null
    const totalSamples = currentBuffer.length
    const startSample = Math.floor(loopStartFrac.value * totalSamples)
    const endSample = Math.ceil(loopEndFrac.value * totalSamples)
    if (endSample <= startSample) return null
    return encodeWav(currentBuffer, startSample, endSample)
  }

  function dispose() {
    stop()
    currentBuffer = null
    rawBase64 = null
    hasAudio.value = false
    if (ctx && ctx.state !== 'closed') {
      ctx.close()
    }
    ctx = null
  }

  return {
    play,
    stop,
    setLoop,
    setTranspose,
    setLoopStart,
    setLoopEnd,
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
  }
}
