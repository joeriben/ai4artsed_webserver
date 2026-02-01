/**
 * TypeScript interfaces for LLM Model Matrix settings
 */

/** Model field identifiers - the 9 application areas */
export type ModelField =
  | 'STAGE1_TEXT_MODEL'
  | 'STAGE1_VISION_MODEL'
  | 'STAGE2_INTERCEPTION_MODEL'
  | 'STAGE2_OPTIMIZATION_MODEL'
  | 'STAGE3_MODEL'
  | 'STAGE4_LEGACY_MODEL'
  | 'CHAT_HELPER_MODEL'
  | 'IMAGE_ANALYSIS_MODEL'
  | 'CODING_MODEL'

/** VRAM tier identifiers (local columns) */
export type VramTier = 'vram_8' | 'vram_16' | 'vram_24' | 'vram_32' | 'vram_48' | 'vram_96'

/** Cloud provider identifiers */
export type CloudProvider = 'none' | 'bedrock' | 'mistral' | 'anthropic' | 'openai' | 'openrouter'

/** Column definition for matrix display */
export interface MatrixColumn {
  id: string
  label: string
  type: 'local' | 'cloud'
  dsgvoCompliant: boolean
}

/** Row definition for matrix display */
export interface MatrixRow {
  field: ModelField
  label: string
  stage: string
}

/** Preset data from HARDWARE_MATRIX */
export interface PresetData {
  label: string
  models: Record<ModelField, string>
  EXTERNAL_LLM_PROVIDER: CloudProvider
  DSGVO_CONFORMITY: boolean
}

/** Matrix structure from backend */
export type HardwareMatrix = Record<VramTier, Record<CloudProvider, PresetData>>
