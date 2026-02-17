/**
 * ADSR envelope composable for Crossmodal Lab monophonic synth.
 *
 * Wraps a single GainNode driven by Web Audio AudioParam scheduling.
 * Provides triggerAttack / triggerRelease for MIDI note-on/off and
 * bypass() for non-MIDI playback (sets gain=1, no envelope).
 */
import { ref } from 'vue'

export function useEnvelope() {
  const attackMs = ref(50)
  const decayMs = ref(200)
  const sustain = ref(0.7)
  const releaseMs = ref(300)

  let gainNode: GainNode | null = null
  let releaseTimer: ReturnType<typeof setTimeout> | null = null

  /** Create the envelope GainNode. Call once after AudioContext exists. */
  function createNode(ac: AudioContext): GainNode {
    gainNode = ac.createGain()
    gainNode.gain.value = 0
    return gainNode
  }

  /** Note-on: ramp 0 -> peak (velocity) -> sustain level. */
  function triggerAttack(velocity = 1): void {
    if (!gainNode) return
    const now = gainNode.context.currentTime
    const atk = attackMs.value / 1000
    const dec = decayMs.value / 1000
    const sus = sustain.value * velocity

    if (releaseTimer) { clearTimeout(releaseTimer); releaseTimer = null }

    gainNode.gain.cancelScheduledValues(now)
    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(velocity, now + atk)
    gainNode.gain.linearRampToValueAtTime(sus, now + atk + dec)
  }

  /** Note-off: ramp current level -> 0. Optional callback when release completes. */
  function triggerRelease(onComplete?: () => void): void {
    if (!gainNode) return
    const now = gainNode.context.currentTime
    const rel = releaseMs.value / 1000

    gainNode.gain.cancelScheduledValues(now)
    gainNode.gain.setValueAtTime(gainNode.gain.value, now)
    gainNode.gain.linearRampToValueAtTime(0, now + rel)

    if (onComplete) {
      if (releaseTimer) clearTimeout(releaseTimer)
      releaseTimer = setTimeout(onComplete, releaseMs.value + 50)
    }
  }

  /** Bypass envelope: cancel scheduling, set gain=1 immediately (for non-MIDI playback). */
  function bypass(): void {
    if (!gainNode) return
    const now = gainNode.context.currentTime
    if (releaseTimer) { clearTimeout(releaseTimer); releaseTimer = null }
    gainNode.gain.cancelScheduledValues(now)
    gainNode.gain.setValueAtTime(1, now)
  }

  function dispose(): void {
    if (releaseTimer) { clearTimeout(releaseTimer); releaseTimer = null }
    if (gainNode) { gainNode.disconnect(); gainNode = null }
  }

  return {
    attackMs,
    decayMs,
    sustain,
    releaseMs,
    createNode,
    triggerAttack,
    triggerRelease,
    bypass,
    dispose,
  }
}
