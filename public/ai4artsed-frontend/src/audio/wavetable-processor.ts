/**
 * AudioWorklet processor for wavetable synthesis.
 *
 * Phase-accumulator reads single-cycle frames at a controlled frequency.
 * Bilinear interpolation between adjacent samples and adjacent frames
 * provides smooth timbral morphing via the scanPosition parameter.
 *
 * Frame size: 2048 samples (~21.5 Hz fundamental at 44.1 kHz).
 */

const FRAME_SIZE = 2048

class WavetableProcessor extends AudioWorkletProcessor {
  private frames: Float32Array[] = []
  private phase = 0

  static get parameterDescriptors(): AudioParamDescriptor[] {
    return [
      { name: 'frequency', defaultValue: 440, minValue: 20, maxValue: 20000, automationRate: 'a-rate' },
      { name: 'scanPosition', defaultValue: 0, minValue: 0, maxValue: 1, automationRate: 'a-rate' },
    ]
  }

  constructor() {
    super()
    this.port.onmessage = (e: MessageEvent) => {
      if (e.data?.frames) {
        this.frames = e.data.frames as Float32Array[]
      }
    }
  }

  process(
    _inputs: Float32Array[][],
    outputs: Float32Array[][],
    parameters: Record<string, Float32Array>,
  ): boolean {
    const output = outputs[0]?.[0]
    if (!output || this.frames.length === 0) return true

    const numFrames = this.frames.length
    const freqParam = parameters.frequency!
    const scanParam = parameters.scanPosition!
    const freqConstant = freqParam.length === 1
    const scanConstant = scanParam.length === 1

    for (let i = 0; i < output.length; i++) {
      const freq = freqConstant ? freqParam[0]! : freqParam[i]!
      const scan = scanConstant ? scanParam[0]! : scanParam[i]!

      // Frame selection via scan position
      const framePos = scan * (numFrames - 1)
      const frameA = Math.floor(framePos)
      const frameB = Math.min(frameA + 1, numFrames - 1)
      const frameMix = framePos - frameA

      // Sample position via phase accumulator
      const idx0 = Math.floor(this.phase) % FRAME_SIZE
      const idx1 = (idx0 + 1) % FRAME_SIZE
      const phaseFrac = this.phase - Math.floor(this.phase)

      // Bilinear interpolation: within frame, then between frames
      const a = this.frames[frameA]!
      const b = this.frames[frameB]!
      const sampleA = a[idx0]! + (a[idx1]! - a[idx0]!) * phaseFrac
      const sampleB = b[idx0]! + (b[idx1]! - b[idx0]!) * phaseFrac
      output[i] = sampleA + (sampleB - sampleA) * frameMix

      // Advance phase, wrap to prevent float precision loss
      this.phase += freq * FRAME_SIZE / sampleRate
      if (this.phase >= FRAME_SIZE) {
        this.phase -= FRAME_SIZE * Math.floor(this.phase / FRAME_SIZE)
      }
    }

    return true
  }
}

registerProcessor('wavetable-processor', WavetableProcessor)
