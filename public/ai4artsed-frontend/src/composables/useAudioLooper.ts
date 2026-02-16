/**
 * Web Audio API looper composable for Crossmodal Lab Synth tab.
 *
 * Double-buffered AudioBufferSourceNode with crossfade on new audio,
 * loop toggle, and pitch transposition via playbackRate.
 *
 * AudioContext is created lazily on first play() call to satisfy
 * browser autoplay policy (requires user gesture).
 */
import { ref, readonly } from 'vue'

const CROSSFADE_MS = 80

export function useAudioLooper() {
  let ctx: AudioContext | null = null
  let activeSource: AudioBufferSourceNode | null = null
  let activeGain: GainNode | null = null

  const isPlaying = ref(false)
  const isLooping = ref(true)
  const transposeSemitones = ref(0)

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

  /**
   * Decode base64 WAV to AudioBuffer.
   */
  async function decodeBase64Wav(base64: string): Promise<AudioBuffer> {
    const ac = ensureContext()
    const binaryStr = atob(base64)
    const bytes = new Uint8Array(binaryStr.length)
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i)
    }
    return ac.decodeAudioData(bytes.buffer)
  }

  /**
   * Start or crossfade to a new audio buffer.
   * If something is already playing, crossfade over CROSSFADE_MS.
   * If loop is on, the new buffer loops seamlessly.
   */
  async function play(base64Wav: string) {
    const ac = ensureContext()
    const buffer = await decodeBase64Wav(base64Wav)

    const newGain = ac.createGain()
    newGain.connect(ac.destination)

    const newSource = ac.createBufferSource()
    newSource.buffer = buffer
    newSource.loop = isLooping.value
    newSource.playbackRate.value = playbackRate()
    newSource.connect(newGain)

    const now = ac.currentTime
    const fadeSec = CROSSFADE_MS / 1000

    if (activeSource && activeGain) {
      // Crossfade: ramp old down, new up
      activeGain.gain.setValueAtTime(activeGain.gain.value, now)
      activeGain.gain.linearRampToValueAtTime(0, now + fadeSec)

      newGain.gain.setValueAtTime(0, now)
      newGain.gain.linearRampToValueAtTime(1, now + fadeSec)

      // Stop old source after crossfade completes
      const oldSource = activeSource
      const oldGain = activeGain
      setTimeout(() => {
        try { oldSource.stop() } catch { /* already stopped */ }
        oldGain.disconnect()
      }, CROSSFADE_MS + 20)
    } else {
      newGain.gain.setValueAtTime(1, now)
    }

    newSource.start(0)
    newSource.onended = () => {
      // Only update isPlaying if this is still the active source
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

  function dispose() {
    stop()
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
    dispose,
    isPlaying: readonly(isPlaying),
    isLooping: readonly(isLooping),
    transposeSemitones: readonly(transposeSemitones),
  }
}
