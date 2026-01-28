/**
 * Canvas Workflow Types for AI4ArtsEd DevServer
 *
 * Defines types for the visual canvas workflow builder.
 * Supports parallel fan-out workflows with feedback loops.
 *
 * Session 129: Phase 1 Implementation
 */

// ============================================================================
// NODE TYPES
// ============================================================================

/**
 * Available stage/node types in the canvas
 *
 * NOTE: Safety is NOT a user-visible node!
 * - Stage 1 Safety: Automatic in /pipeline/interception
 * - Stage 3 Safety: Automatic per output-config
 * DevServer handles all safety transparently.
 *
 * Session 134: Added evaluation/fork/display/loop nodes for decision logic
 */
export type StageType =
  | 'input'
  | 'random_prompt' // Session 140: LLM-based random prompt generator with presets
  | 'interception'
  | 'translation'
  | 'generation'
  | 'collector'
  // Session 134 Refactored: Unified evaluation node with optional branching
  | 'evaluation'
  // Display node (visualization)
  | 'display'

// ============================================================================
// RANDOM PROMPT TYPES
// ============================================================================

/** Random Prompt Preset Types */
export type RandomPromptPreset =
  | 'clean_image'  // Medienneutrale Bild-Prompts
  | 'photo'        // Fotografische Prompts mit Film-Typ
  | 'artform'      // Kunstform-Transformation
  | 'instruction'  // Kreative Transformation
  | 'language'     // Sprach-Vorschlag

/** Film types for photo preset */
export type PhotoFilmType =
  | 'random'
  | 'Kodachrome' | 'Ektachrome'
  | 'Portra 400' | 'Portra 800' | 'Ektar 100'
  | 'Fuji Pro 400H' | 'Fuji Superia' | 'CineStill 800T'
  | 'Ilford HP5' | 'Ilford Delta 400' | 'Ilford FP4' | 'Ilford Pan F' | 'Ilford XP2'
  | 'Tri-X 400'

/** Node type definition for the palette */
export interface NodeTypeDefinition {
  id: string
  type: StageType
  label: { en: string; de: string }
  description: { en: string; de: string }
  color: string
  icon: string
  /** Whether this node type allows multiple instances */
  allowMultiple: boolean
  /** Whether this node is mandatory in workflows */
  mandatory: boolean
  /** Allowed input connection types */
  acceptsFrom: StageType[]
  /** Allowed output connection types */
  outputsTo: StageType[]
}

/**
 * Predefined node types for the canvas
 *
 * Module Types:
 * - Input: Text input source
 * - Interception: LLM selection (primary!) + interception config (optional override)
 * - Translation: Translation prompt + LLM selection
 * - Generation: Output configs (sd35, qwen, flux2, etc.)
 * - Collector: Fan-in collector for parallel outputs (Media Collector)
 *
 * IMPORTANT: Safety is NOT a node!
 * DevServer handles Stage 1 + Stage 3 safety automatically.
 */
export const NODE_TYPE_DEFINITIONS: NodeTypeDefinition[] = [
  {
    id: 'input',
    type: 'input',
    label: { en: 'Input', de: 'Eingabe' },
    description: { en: 'Text input source', de: 'Text-Eingabequelle' },
    color: '#3b82f6', // blue
    icon: 'edit_square_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: false,
    mandatory: true,
    acceptsFrom: [],
    outputsTo: ['random_prompt', 'interception', 'translation', 'generation', 'evaluation', 'display'] // Can connect to processing, generation, evaluation, or display
  },
  // Session 140: Random Prompt Node with presets
  {
    id: 'random_prompt',
    type: 'random_prompt',
    label: { en: 'Random Prompt', de: 'Zufalls-Prompt' },
    description: {
      en: 'Generate creative content via LLM with presets',
      de: 'Generiert kreative Inhalte via LLM mit Presets'
    },
    color: '#ec4899', // pink
    icon: 'shuffle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false,
    acceptsFrom: ['input', 'interception', 'evaluation'], // Optional context
    outputsTo: ['interception', 'translation', 'generation', 'evaluation', 'display', 'collector']
  },
  {
    id: 'interception',
    type: 'interception',
    label: { en: 'Interception', de: 'Interception' },
    description: {
      en: 'Pedagogical transformation with LLM selection',
      de: 'Pädagogische Transformation mit LLM-Auswahl'
    },
    color: '#8b5cf6', // purple
    icon: 'cognition_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false,
    acceptsFrom: ['input', 'random_prompt', 'interception', 'evaluation'],
    outputsTo: ['interception', 'translation', 'generation', 'evaluation', 'display', 'collector']
  },
  {
    id: 'translation',
    type: 'translation',
    label: { en: 'Translation', de: 'Übersetzung' },
    description: {
      en: 'Language translation with custom prompt + LLM',
      de: 'Sprachübersetzung mit eigenem Prompt + LLM'
    },
    color: '#f59e0b', // amber
    icon: 'language_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false,
    acceptsFrom: ['input', 'random_prompt', 'interception', 'evaluation'],
    outputsTo: ['generation', 'evaluation', 'display', 'collector']
  },
  {
    id: 'generation',
    type: 'generation',
    label: { en: 'Generation', de: 'Generierung' },
    description: {
      en: 'Media generation (image, audio, video)',
      de: 'Mediengenerierung (Bild, Audio, Video)'
    },
    color: '#10b981', // emerald
    icon: 'brush_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: true,
    acceptsFrom: ['input', 'random_prompt', 'interception', 'translation', 'evaluation'],
    outputsTo: ['evaluation', 'display', 'collector']
  },
  {
    id: 'collector',
    type: 'collector',
    label: { en: 'Media Collector', de: 'Medien-Sammler' },
    description: {
      en: 'Collects outputs (media + text) from nodes',
      de: 'Sammelt Ausgaben (Medien + Text) von Knoten'
    },
    color: '#06b6d4', // cyan
    icon: 'gallery_thumbnail_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: false,
    mandatory: true,
    acceptsFrom: ['generation', 'random_prompt', 'interception', 'translation', 'display', 'evaluation'],
    outputsTo: []
  },
  // Session 134 Refactored: Unified Evaluation Node (replaces 5 eval nodes + 2 fork nodes)
  {
    id: 'evaluation',
    type: 'evaluation',
    label: { en: 'Evaluation', de: 'Bewertung' },
    description: {
      en: 'LLM-based evaluation with optional branching',
      de: 'LLM-basierte Bewertung mit optionaler Verzweigung'
    },
    color: '#f59e0b', // amber
    icon: 'checklist_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false,
    acceptsFrom: ['input', 'interception', 'translation', 'generation', 'display', 'evaluation'],
    outputsTo: ['interception', 'translation', 'generation', 'display', 'evaluation', 'collector']
  },
  // Session 135: Display Node (Terminal - no output)
  {
    id: 'display',
    type: 'display',
    label: { en: 'Preview', de: 'Vorschau' },
    description: {
      en: 'Preview text or media inline (tap/observer, no output)',
      de: 'Vorschau von Text oder Medien inline (Tap/Observer, kein Output)'
    },
    color: '#10b981', // green
    icon: 'info_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false,
    acceptsFrom: ['input', 'interception', 'translation', 'generation', 'evaluation', 'display'],
    outputsTo: []  // TERMINAL: No output connector (tap/observer pattern)
  }
]

// ============================================================================
// CANVAS NODE
// ============================================================================

/** A node instance on the canvas */
export interface CanvasNode {
  /** Unique node ID */
  id: string
  /** Node type (stage) */
  type: StageType
  /** X position on canvas */
  x: number
  /** Y position on canvas */
  y: number
  /** Node-specific configuration overrides */
  config: Record<string, unknown>
  /** Whether this node is locked (cannot be deleted) */
  locked?: boolean

  // === Generation node config ===
  /** Selected output config ID for generation nodes (e.g., 'sd35_large', 'flux2_schnell') */
  configId?: string

  // === Interception node config ===
  /** Selected LLM model ID (e.g., 'gpt-4o-mini', 'claude-3-haiku') */
  llmModel?: string
  /** Context/system prompt for the LLM (pedagogical transformation instructions) */
  contextPrompt?: string

  // === Translation node config ===
  /** Translation prompt/instructions */
  translationPrompt?: string

  // === Input node config ===
  /** User's prompt text (input node) */
  promptText?: string

  // === Display properties ===
  /** Custom width (optional, for resizable nodes like Collector) */
  width?: number
  /** Custom height (optional, for resizable nodes like Collector) */
  height?: number

  // === Session 134 Refactored: Unified Evaluation node config ===
  /** Evaluation type (pre-fills prompt template) */
  evaluationType?: 'fairness' | 'creativity' | 'bias' | 'quality' | 'custom'
  /** Evaluation prompt/criteria description */
  evaluationPrompt?: string
  /** Output type for evaluation results (controls if score is requested) */
  outputType?: 'commentary' | 'score' | 'all'
  /** Enable branching (fork) based on evaluation result */
  enableBranching?: boolean
  /** Branch condition type (only if enableBranching = true) */
  branchCondition?: 'binary' | 'threshold'
  /** Threshold value for threshold branching (0-10) */
  thresholdValue?: number
  /** Label for "true/pass" path */
  trueLabel?: string
  /** Label for "false/fail" path */
  falseLabel?: string

  // === Feedback config (for Interception/Translation nodes) ===
  /** Maximum feedback iterations (default: 3) */
  maxFeedbackIterations?: number

  // === Display node config ===
  /** Display mode for visualization */
  displayMode?: 'popup' | 'inline' | 'toast'
  /** Display title */
  title?: string

  // === Random Prompt node config (Session 140) ===
  /** Selected preset (determines system prompt) */
  randomPromptPreset?: RandomPromptPreset
  /** LLM model for generation */
  randomPromptModel?: string
  /** Film type (only for 'photo' preset) */
  randomPromptFilmType?: PhotoFilmType
  /** Custom system prompt override (collapsed by default) */
  randomPromptSystemPrompt?: string
  /** Show system prompt editor */
  randomPromptShowSystemPrompt?: boolean
  /** Cache-breaking seed */
  randomPromptSeed?: number
}

// ============================================================================
// CONNECTION
// ============================================================================

/** A connection between two nodes */
export interface CanvasConnection {
  /** Source node ID */
  sourceId: string
  /** Target node ID */
  targetId: string
  /** Session 134: Label for fork branches (e.g., 'true', 'false', 'approved', 'rejected') */
  label?: string
  /** Session 134: Active state for conditional execution (managed by execution engine) */
  active?: boolean
}

// ============================================================================
// WORKFLOW
// ============================================================================

/** Loop configuration for feedback workflows */
export interface LoopConfig {
  enabled: boolean
  maxIterations: number
  /** Node ID to collect feedback from */
  feedbackFrom?: string
  /** Node ID to feed back into */
  feedbackTo?: string
  /** Conditional termination expression (future) */
  condition?: string
}

/** Automation settings */
export interface AutomationConfig {
  /** Seed control: 'global' applies same seed to all generation nodes, 'per-node' allows individual seeds */
  seedControl: 'global' | 'per-node'
  /** Global seed value (when seedControl is 'global') */
  globalSeed?: number
  /** Whether to automatically apply LoRA automation */
  loraInjection: boolean
}

/** Complete canvas workflow definition */
export interface CanvasWorkflow {
  /** Workflow ID */
  id: string
  /** Workflow name */
  name: string
  /** Workflow description */
  description?: string
  /** Workflow type identifier */
  type: 'canvas_workflow'
  /** All nodes in the workflow */
  nodes: CanvasNode[]
  /** All connections between nodes */
  connections: CanvasConnection[]
  /** Loop/feedback configuration */
  loops?: LoopConfig
  /** Automation settings */
  automation?: AutomationConfig
  /** Creation timestamp */
  createdAt?: string
  /** Last modified timestamp */
  updatedAt?: string
}

// ============================================================================
// EXECUTION
// ============================================================================

/** Execution status for a node */
export type NodeExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

/** Execution state for a single node */
export interface NodeExecutionState {
  nodeId: string
  status: NodeExecutionStatus
  output?: unknown
  error?: string
  startTime?: number
  endTime?: number
  durationMs?: number
}

/** Overall workflow execution state */
export interface WorkflowExecutionState {
  workflowId: string
  status: 'idle' | 'running' | 'completed' | 'failed' | 'interrupted'
  currentIteration: number
  totalIterations: number
  nodeStates: Map<string, NodeExecutionState>
  startTime?: number
  endTime?: number
}

// ============================================================================
// CONFIG SELECTION
// ============================================================================

/** Available LLM model for interception/translation nodes */
export interface LLMModelSummary {
  /** Model ID (e.g., 'gpt-4o-mini', 'claude-3-haiku') */
  id: string
  /** Display name */
  name: string
  /** Provider (openai, anthropic, google, local) */
  provider: string
  /** Model capabilities/description */
  description?: string
  /** Whether this is the default/recommended model */
  isDefault?: boolean
}

/** Output/generation config summary (for palette selection) */
export interface OutputConfigSummary {
  id: string
  name: { en: string; de: string }
  description: { en: string; de: string }
  icon: string
  color: string
  mediaType: 'image' | 'audio' | 'video' | 'music' | 'text'
  backend: string
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get node type definition by type
 */
export function getNodeTypeDefinition(type: StageType): NodeTypeDefinition | undefined {
  return NODE_TYPE_DEFINITIONS.find(n => n.type === type)
}

/**
 * Check if a connection is valid between two node types
 */
export function isValidConnection(sourceType: StageType, targetType: StageType): boolean {
  const sourceDef = getNodeTypeDefinition(sourceType)
  const targetDef = getNodeTypeDefinition(targetType)
  if (!sourceDef || !targetDef) return false
  return sourceDef.outputsTo.includes(targetType) && targetDef.acceptsFrom.includes(sourceType)
}

/**
 * Generate a unique node ID
 */
export function generateNodeId(type: StageType): string {
  return `${type}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Create a default canvas workflow
 *
 * Default structure: Input → (user adds interception/generation) → Collector
 * Safety is handled automatically by DevServer.
 */
export function createDefaultWorkflow(): CanvasWorkflow {
  const inputNode: CanvasNode = {
    id: generateNodeId('input'),
    type: 'input',
    x: 100,
    y: 200,
    config: { source: 'text' },
    locked: true
  }

  const collectorNode: CanvasNode = {
    id: generateNodeId('collector'),
    type: 'collector',
    x: 900,
    y: 200,
    config: {},
    locked: true
  }

  return {
    id: `workflow_${Date.now()}`,
    name: 'New Workflow',
    type: 'canvas_workflow',
    nodes: [inputNode, collectorNode],
    connections: [],
    automation: {
      seedControl: 'global',
      loraInjection: true
    }
  }
}

// ============================================================================
// RANDOM PROMPT PRESETS (Session 140)
// ============================================================================

/** Preset configuration for Random Prompt node */
export interface RandomPromptPresetConfig {
  label: { en: string; de: string }
  systemPrompt: string
  userPromptTemplate: string
}

/** Random Prompt Presets with system prompts */
export const RANDOM_PROMPT_PRESETS: Record<RandomPromptPreset, RandomPromptPresetConfig> = {
  clean_image: {
    label: { en: 'Clean Image Prompt', de: 'Sauberer Bild-Prompt' },
    systemPrompt: `You are an inventive creative. Your task is to invent a vivid, detailed image prompt.

IMPORTANT - Generate CLEAN, MEDIA-NEUTRAL images:
- NO camera or photographic references (no film, no camera, no lens)
- NO optical effects (no wide-angle, no telephoto, no macro)
- NO depth of field or bokeh
- NO motion blur or any blur effects
- NO "retro", "vintage", or nostalgic styling
- NO film grain, vignette, or post-processing artifacts

Think globally. Avoid cultural clichés.
Subject matter: scenes, objects, animals, nature, technology, culture, people, homes, family, work, holiday, urban, rural, trivia, intricate details.
Be verbose, provide rich visual details about colors, lighting, textures, composition, atmosphere.
Transform the prompt strictly following the context if provided.
NO META-COMMENTS, TITLES, Remarks, dialogue WHATSOEVER.`,
    userPromptTemplate: 'Generate a creative image prompt.'
  },
  photo: {
    label: { en: 'Photo Prompt', de: 'Foto-Prompt' },
    systemPrompt: `You are an inventive creative. Your task is to invent a REALISTIC photographic image prompt.

Think globally. Avoid cultural clichés. Avoid "retro" style descriptions.
Describe contemporary everyday motives: scenes, objects, animals, nature, tech, culture, people, homes, family, work, holiday, urban, rural, trivia, details.
Choose either unlikely, untypical or typical photographical sujets. Be verbose, provide intricate details.
Always begin your output with: "{film_description} of".
Transform the prompt strictly following the context if provided.
NO META-COMMENTS, TITLES, Remarks, dialogue WHATSOEVER.`,
    userPromptTemplate: 'Generate a creative photographic image prompt.'
  },
  artform: {
    label: { en: 'Artform Transformation', de: 'Kunstform-Transformation' },
    systemPrompt: `You generate artform transformation instructions from an artist practice perspective.

IMPORTANT: NEVER use "in the style of" - instead frame as artistic practice, technique, or creative process.

Good examples:
- "Render this as a Japanese Noh theatre performance"
- "Transform this into a Yoruba praise poem"
- "Compose this as a Maori chant"
- "Frame this message through Cubist fragmentation"
- "Present this as an Afro-futurist myth"
- "Choreograph this as a Bharatanatyam narrative"
- "Inscribe this as Egyptian hieroglyphics"
- "Express this through Aboriginal dot painting technique"

Think globally across all cultures and art practices.
Focus on the DOING - the artistic practice, not imitation.
Output ONLY the transformation instruction, nothing else.`,
    userPromptTemplate: 'Generate a creative artform transformation instruction.'
  },
  instruction: {
    label: { en: 'Creative Instruction', de: 'Kreative Anweisung' },
    systemPrompt: `You generate creative transformation instructions.
Your output is a single instruction that transforms content in an unusual, creative way.
Examples: nature language, theatrical play, nostalgic robot voice, rhythmic rap, animal fable, alien explanation, philosophical versions (Wittgenstein, Heidegger, Adorno), ancient manuscript, bedtime story for post-human child, internal monologue of a tree, forgotten folk song lyrics, spy messages, protest chant, underwater civilization dialect, extinct animal conversation, dream sequence, poetic weather forecast, love letter to future generation, etc.
Be wildly creative and unexpected.
Output ONLY the transformation instruction, nothing else.`,
    userPromptTemplate: 'Generate a creative transformation instruction.'
  },
  language: {
    label: { en: 'Language Suggestion', de: 'Sprach-Vorschlag' },
    systemPrompt: `You suggest a random language from around the world.
Choose from major world languages, regional languages, or less common languages.
Consider: European, Asian, African, Indigenous American, Pacific languages.
Output ONLY the language name in English, nothing else.
Example outputs: "Swahili", "Bengali", "Quechua", "Welsh", "Tagalog"`,
    userPromptTemplate: 'Suggest a random language.'
  }
}

/** Photo film type descriptions */
export const PHOTO_FILM_TYPES: Record<PhotoFilmType, string> = {
  random: '', // Will be selected at runtime
  'Kodachrome': 'a Kodachrome film slide',
  'Ektachrome': 'an Ektachrome film slide',
  'Portra 400': 'a Kodak Portra 400 color negative',
  'Portra 800': 'a Kodak Portra 800 color negative',
  'Ektar 100': 'a Kodak Ektar 100 color negative',
  'Fuji Pro 400H': 'a Fujifilm Pro 400H color negative',
  'Fuji Superia': 'a Fujifilm Superia color negative',
  'CineStill 800T': 'a CineStill 800T tungsten-balanced color negative',
  'Ilford HP5': 'an Ilford HP5 Plus black and white negative',
  'Ilford Delta 400': 'an Ilford Delta 400 black and white negative',
  'Ilford FP4': 'an Ilford FP4 Plus black and white negative',
  'Ilford Pan F': 'an Ilford Pan F Plus 50 black and white negative',
  'Ilford XP2': 'an Ilford XP2 Super chromogenic black and white negative',
  'Tri-X 400': 'a Kodak Tri-X 400 black and white negative'
}
