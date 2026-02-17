/**
 * TypeScript declarations for AudioWorklet global scope.
 *
 * AudioWorklet processors run in a separate thread with their own global scope
 * that includes these special types and variables not present in the standard DOM.
 */

// Global sample rate variable (provided by the audio rendering context)
declare const sampleRate: number

// Global registration function for AudioWorklet processors
declare function registerProcessor(
  name: string,
  processorCtor: new () => AudioWorkletProcessor,
): void

// Base class for AudioWorklet processors
declare class AudioWorkletProcessor {
  readonly port: MessagePort
  process(
    inputs: Float32Array[][],
    outputs: Float32Array[][],
    parameters: Record<string, Float32Array>,
  ): boolean
}

// Descriptor for audio parameters (used by parameterDescriptors static getter)
interface AudioParamDescriptor {
  name: string
  defaultValue?: number
  minValue?: number
  maxValue?: number
  automationRate?: 'a-rate' | 'k-rate'
}
