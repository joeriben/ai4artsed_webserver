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

/** Available stage/node types in the canvas */
export type StageType = 'input' | 'safety' | 'interception' | 'translation' | 'generation' | 'output'

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

/** Predefined node types for the canvas */
export const NODE_TYPE_DEFINITIONS: NodeTypeDefinition[] = [
  {
    id: 'input',
    type: 'input',
    label: { en: 'Input', de: 'Eingabe' },
    description: { en: 'Text or image input source', de: 'Text- oder Bild-Eingabequelle' },
    color: '#3b82f6', // blue
    icon: '📝',
    allowMultiple: false,
    mandatory: true,
    acceptsFrom: [],
    outputsTo: ['safety']
  },
  {
    id: 'safety',
    type: 'safety',
    label: { en: 'Safety Check', de: 'Sicherheitsprüfung' },
    description: { en: 'Mandatory safety validation (Stage 1)', de: 'Verpflichtende Sicherheitsprüfung (Stufe 1)' },
    color: '#ef4444', // red
    icon: '🛡️',
    allowMultiple: false,
    mandatory: true,
    acceptsFrom: ['input'],
    outputsTo: ['interception', 'translation']
  },
  {
    id: 'interception',
    type: 'interception',
    label: { en: 'Interception', de: 'Transformation' },
    description: { en: 'Pedagogical prompt transformation (Stage 2)', de: 'Pädagogische Prompt-Transformation (Stufe 2)' },
    color: '#8b5cf6', // purple
    icon: '🎭',
    allowMultiple: true,
    mandatory: false,
    acceptsFrom: ['safety', 'interception'],
    outputsTo: ['interception', 'translation', 'generation']
  },
  {
    id: 'translation',
    type: 'translation',
    label: { en: 'Translation', de: 'Übersetzung' },
    description: { en: 'Optional language translation (Stage 3)', de: 'Optionale Sprachübersetzung (Stufe 3)' },
    color: '#f59e0b', // amber
    icon: '🌐',
    allowMultiple: false,
    mandatory: false,
    acceptsFrom: ['safety', 'interception'],
    outputsTo: ['generation']
  },
  {
    id: 'generation',
    type: 'generation',
    label: { en: 'Generation', de: 'Generierung' },
    description: { en: 'Media generation output (Stage 4)', de: 'Mediengenerierung (Stufe 4)' },
    color: '#10b981', // emerald
    icon: '🎨',
    allowMultiple: true,
    mandatory: true,
    acceptsFrom: ['interception', 'translation'],
    outputsTo: ['output']
  },
  {
    id: 'output',
    type: 'output',
    label: { en: 'Output', de: 'Ausgabe' },
    description: { en: 'Final output collection', de: 'Endausgabe-Sammlung' },
    color: '#06b6d4', // cyan
    icon: '📤',
    allowMultiple: false,
    mandatory: true,
    acceptsFrom: ['generation'],
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
  /** Selected config ID (e.g., 'bauhaus' for interception, 'sd35_large' for generation) */
  configId?: string
  /** Node-specific configuration overrides */
  config: Record<string, unknown>
  /** Whether this node is locked (cannot be deleted) */
  locked?: boolean
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

/** Interception config summary (for palette selection) */
export interface InterceptionConfigSummary {
  id: string
  name: { en: string; de: string }
  description: { en: string; de: string }
  icon: string
  color: string
  category: string
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

  const safetyNode: CanvasNode = {
    id: generateNodeId('safety'),
    type: 'safety',
    x: 300,
    y: 200,
    config: {},
    locked: true
  }

  const outputNode: CanvasNode = {
    id: generateNodeId('output'),
    type: 'output',
    x: 900,
    y: 200,
    config: {},
    locked: true
  }

  return {
    id: `workflow_${Date.now()}`,
    name: 'New Workflow',
    type: 'canvas_workflow',
    nodes: [inputNode, safetyNode, outputNode],
    connections: [
      { sourceId: inputNode.id, targetId: safetyNode.id }
    ],
    automation: {
      seedControl: 'global',
      loraInjection: true
    }
  }
}
