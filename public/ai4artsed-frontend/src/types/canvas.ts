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
 */
export type StageType = 'input' | 'interception' | 'translation' | 'generation' | 'collector'

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
    outputsTo: ['interception', 'translation'] // Direct to interception (safety is automatic)
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
    acceptsFrom: ['input', 'interception'],
    outputsTo: ['interception', 'translation', 'generation', 'collector']
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
    acceptsFrom: ['input', 'interception'],
    outputsTo: ['generation', 'collector']
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
    acceptsFrom: ['interception', 'translation'],
    outputsTo: ['collector']
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
    acceptsFrom: ['generation', 'interception', 'translation'],
    outputsTo: []
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
