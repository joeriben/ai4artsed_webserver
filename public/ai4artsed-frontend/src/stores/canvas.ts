import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type {
  CanvasNode,
  CanvasConnection,
  CanvasWorkflow,
  StageType,
  NodeExecutionState,
  WorkflowExecutionState,
  LLMModelSummary,
  OutputConfigSummary
} from '@/types/canvas'
import {
  generateNodeId,
  createDefaultWorkflow,
  getNodeTypeDefinition,
  isValidConnection
} from '@/types/canvas'

/**
 * Pinia Store for Canvas Workflow Builder
 *
 * Manages:
 * - Workflow state (nodes, connections)
 * - Node selection and editing
 * - Available configs (interception, output)
 * - Workflow execution state
 *
 * Session 129: Phase 1 Implementation
 */
export const useCanvasStore = defineStore('canvas', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  /** Current workflow being edited */
  const workflow = ref<CanvasWorkflow>(createDefaultWorkflow())

  /** Currently selected node ID */
  const selectedNodeId = ref<string | null>(null)

  /** Node being connected (source of new connection) */
  const connectingFromId = ref<string | null>(null)

  /** Session 134 Phase 3b: Label for the connection being created (passthrough/commented/commentary) */
  const connectingLabel = ref<string | null>(null)

  /** Current mouse position (for connection preview) */
  const mousePosition = ref({ x: 0, y: 0 })

  /** Available LLM models for interception/translation nodes */
  const llmModels = ref<LLMModelSummary[]>([])

  /** Available output/generation configs */
  const outputConfigs = ref<OutputConfigSummary[]>([])

  /** Loading state */
  const isLoading = ref(false)

  /** Error state */
  const error = ref<string | null>(null)

  /** Workflow execution state */
  const executionState = ref<WorkflowExecutionState | null>(null)

  /** Whether we're in execution mode (read-only canvas) */
  const isExecuting = ref(false)

  /** Execution results from backend (nodeId -> result) */
  const executionResults = ref<Record<string, {
    type: string
    output: unknown
    error: string | null
    model?: string
  }>>({})

  /** Collector output (aggregated from all connected nodes) */
  const collectorOutput = ref<Array<{
    nodeId: string
    nodeType: string
    output: unknown
    error: string | null
  }>>([])

  // ============================================================================
  // COMPUTED
  // ============================================================================

  /** All nodes in the workflow */
  const nodes = computed(() => workflow.value.nodes)

  /** All connections in the workflow */
  const connections = computed(() => workflow.value.connections)

  /** Currently selected node */
  const selectedNode = computed(() => {
    if (!selectedNodeId.value) return null
    return workflow.value.nodes.find(n => n.id === selectedNodeId.value) ?? null
  })

  /** Whether a connection is being created */
  const isConnecting = computed(() => connectingFromId.value !== null)

  /**
   * Check if workflow is valid (has required nodes and connections)
   *
   * Session 133: Generation is now optional for text-only workflows
   * Valid workflows:
   * - Input → Interception/Translation → Collector (text only)
   * - Input → Interception → Generation → Collector (with media)
   *
   * NOTE: Safety is NOT checked here - DevServer handles it automatically
   */
  const isWorkflowValid = computed(() => {
    const hasInput = workflow.value.nodes.some(n => n.type === 'input')
    const hasCollector = workflow.value.nodes.some(n => n.type === 'collector')

    // Check all generation nodes have configs selected (if any exist)
    const generationNodes = workflow.value.nodes.filter(n => n.type === 'generation')
    const allGenerationConfigured = generationNodes.every(n => n.configId)

    // Check all interception nodes have LLM selected
    const interceptionNodes = workflow.value.nodes.filter(n => n.type === 'interception')
    const allInterceptionConfigured = interceptionNodes.every(n => n.llmModel)

    // Check all translation nodes have LLM selected
    const translationNodes = workflow.value.nodes.filter(n => n.type === 'translation')
    const allTranslationConfigured = translationNodes.every(n => n.llmModel)

    // Need at least one processing node (interception, translation, or generation)
    const hasProcessingNode = interceptionNodes.length > 0 ||
                              translationNodes.length > 0 ||
                              generationNodes.length > 0

    return hasInput && hasCollector && hasProcessingNode &&
           allGenerationConfigured && allInterceptionConfigured && allTranslationConfigured
  })

  /**
   * Get validation errors
   *
   * Session 133: Generation is now optional for text-only workflows
   * NOTE: Safety is NOT validated here - DevServer handles it automatically
   */
  const validationErrors = computed(() => {
    const errors: string[] = []

    if (!workflow.value.nodes.some(n => n.type === 'input')) {
      errors.push('Missing input node')
    }
    if (!workflow.value.nodes.some(n => n.type === 'collector')) {
      errors.push('Missing collector node')
    }

    const interceptionNodes = workflow.value.nodes.filter(n => n.type === 'interception')
    const translationNodes = workflow.value.nodes.filter(n => n.type === 'translation')
    const generationNodes = workflow.value.nodes.filter(n => n.type === 'generation')

    // Need at least one processing node
    if (interceptionNodes.length === 0 && translationNodes.length === 0 && generationNodes.length === 0) {
      errors.push('Need at least one processing node (Interception, Translation, or Generation)')
    }

    generationNodes.forEach(n => {
      if (!n.configId) {
        errors.push(`Generation node missing output config`)
      }
    })

    interceptionNodes.forEach(n => {
      if (!n.llmModel) {
        errors.push(`Interception node needs LLM selection`)
      }
    })
    translationNodes.forEach(n => {
      if (!n.llmModel) {
        errors.push(`Translation node needs LLM selection`)
      }
    })

    return errors
  })

  // ============================================================================
  // NODE ACTIONS
  // ============================================================================

  /**
   * Add a new node to the canvas
   */
  function addNode(type: StageType, x: number, y: number, configId?: string): CanvasNode {
    const node: CanvasNode = {
      id: generateNodeId(type),
      type,
      x,
      y,
      configId,
      config: {}
    }

    workflow.value.nodes.push(node)
    console.log(`[Canvas] Added ${type} node at (${x}, ${y})`)
    return node
  }

  /**
   * Update a node's position
   */
  function updateNodePosition(nodeId: string, x: number, y: number) {
    const node = workflow.value.nodes.find(n => n.id === nodeId)
    if (node) {
      node.x = x
      node.y = y
    }
  }

  /**
   * Update a node's config
   */
  function updateNodeConfig(nodeId: string, configId: string) {
    const node = workflow.value.nodes.find(n => n.id === nodeId)
    if (node) {
      node.configId = configId
      console.log(`[Canvas] Updated node ${nodeId} config to ${configId}`)
    }
  }

  /**
   * Update node properties
   */
  function updateNode(nodeId: string, updates: Partial<CanvasNode>) {
    const node = workflow.value.nodes.find(n => n.id === nodeId)
    if (node) {
      Object.assign(node, updates)
    }
  }

  /**
   * Delete a node
   */
  function deleteNode(nodeId: string) {
    const node = workflow.value.nodes.find(n => n.id === nodeId)
    if (node?.locked) {
      console.warn(`[Canvas] Cannot delete locked node ${nodeId}`)
      return false
    }

    // Remove all connections to/from this node
    workflow.value.connections = workflow.value.connections.filter(
      c => c.sourceId !== nodeId && c.targetId !== nodeId
    )

    // Remove the node
    workflow.value.nodes = workflow.value.nodes.filter(n => n.id !== nodeId)

    // Deselect if it was selected
    if (selectedNodeId.value === nodeId) {
      selectedNodeId.value = null
    }

    console.log(`[Canvas] Deleted node ${nodeId}`)
    return true
  }

  /**
   * Select a node
   */
  function selectNode(nodeId: string | null) {
    selectedNodeId.value = nodeId
  }

  // ============================================================================
  // CONNECTION ACTIONS
  // ============================================================================

  /**
   * Start creating a connection from a node
   * Session 134 Phase 3b: Added label parameter for evaluation node outputs
   */
  function startConnection(nodeId: string, label?: string) {
    connectingFromId.value = nodeId
    connectingLabel.value = label || null
  }

  /**
   * Cancel connection creation
   */
  function cancelConnection() {
    connectingFromId.value = null
    connectingLabel.value = null
  }

  /**
   * Complete a connection to a target node
   */
  function completeConnection(targetId: string): boolean {
    if (!connectingFromId.value) return false
    if (connectingFromId.value === targetId) {
      cancelConnection()
      return false
    }

    const sourceNode = workflow.value.nodes.find(n => n.id === connectingFromId.value)
    const targetNode = workflow.value.nodes.find(n => n.id === targetId)

    if (!sourceNode || !targetNode) {
      cancelConnection()
      return false
    }

    // Validate connection types
    if (!isValidConnection(sourceNode.type, targetNode.type)) {
      console.warn(`[Canvas] Invalid connection: ${sourceNode.type} -> ${targetNode.type}`)
      cancelConnection()
      return false
    }

    // Check if connection already exists
    const exists = workflow.value.connections.some(
      c => c.sourceId === connectingFromId.value && c.targetId === targetId
    )

    if (exists) {
      console.warn(`[Canvas] Connection already exists`)
      cancelConnection()
      return false
    }

    // Add the connection
    // Session 134 Phase 3b: Include label if present (for evaluation nodes)
    const newConnection: CanvasConnection = {
      sourceId: connectingFromId.value,
      targetId
    }
    if (connectingLabel.value) {
      newConnection.label = connectingLabel.value
      console.log(`[Canvas] Added labeled connection: ${connectingFromId.value} -> ${targetId} (${connectingLabel.value})`)
    } else {
      console.log(`[Canvas] Added connection: ${connectingFromId.value} -> ${targetId}`)
    }
    workflow.value.connections.push(newConnection)

    cancelConnection()
    return true
  }

  /**
   * Delete a connection
   */
  function deleteConnection(sourceId: string, targetId: string) {
    workflow.value.connections = workflow.value.connections.filter(
      c => !(c.sourceId === sourceId && c.targetId === targetId)
    )
    console.log(`[Canvas] Deleted connection: ${sourceId} -> ${targetId}`)
  }

  /**
   * Update mouse position (for connection preview)
   */
  function updateMousePosition(x: number, y: number) {
    mousePosition.value = { x, y }
  }

  // ============================================================================
  // WORKFLOW ACTIONS
  // ============================================================================

  /**
   * Create a new workflow
   */
  function newWorkflow() {
    workflow.value = createDefaultWorkflow()
    selectedNodeId.value = null
    connectingFromId.value = null
    error.value = null
    console.log('[Canvas] Created new workflow')
  }

  /**
   * Load a workflow from JSON
   */
  function loadWorkflow(data: CanvasWorkflow) {
    workflow.value = data
    selectedNodeId.value = null
    connectingFromId.value = null
    error.value = null
    console.log(`[Canvas] Loaded workflow: ${data.name}`)
  }

  /**
   * Export workflow as JSON
   */
  function exportWorkflow(): CanvasWorkflow {
    return {
      ...workflow.value,
      updatedAt: new Date().toISOString()
    }
  }

  /**
   * Update workflow metadata
   */
  function updateWorkflowMeta(name?: string, description?: string) {
    if (name !== undefined) workflow.value.name = name
    if (description !== undefined) workflow.value.description = description
    workflow.value.updatedAt = new Date().toISOString()
  }

  // ============================================================================
  // CONFIG LOADING
  // ============================================================================

  /**
   * Load available LLM models from backend
   */
  async function loadLLMModels() {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/canvas/llm-models')
      if (!response.ok) {
        throw new Error(`Failed to load LLM models: ${response.statusText}`)
      }
      const data = await response.json()
      llmModels.value = data.models || []
      console.log(`[Canvas] Loaded ${llmModels.value.length} LLM models`)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load LLM models'
      console.error('[Canvas] Error loading LLM models:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load available output/generation configs from backend
   */
  async function loadOutputConfigs() {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/canvas/output-configs')
      if (!response.ok) {
        throw new Error(`Failed to load output configs: ${response.statusText}`)
      }
      const data = await response.json()
      outputConfigs.value = data.configs || []
      console.log(`[Canvas] Loaded ${outputConfigs.value.length} output configs`)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load configs'
      console.error('[Canvas] Error loading output configs:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load all configs
   */
  async function loadAllConfigs() {
    await Promise.all([
      loadLLMModels(),
      loadOutputConfigs()
    ])
  }

  // ============================================================================
  // EXECUTION (placeholder for Phase 3)
  // ============================================================================

  /**
   * Start workflow execution
   * Session 133: Calls /api/canvas/execute backend endpoint
   */
  async function executeWorkflow() {
    if (!isWorkflowValid.value) {
      error.value = 'Workflow is not valid'
      console.error('[Canvas] Cannot execute invalid workflow:', validationErrors.value)
      return
    }

    isExecuting.value = true
    error.value = null
    executionResults.value = {}
    collectorOutput.value = []

    executionState.value = {
      workflowId: workflow.value.id,
      status: 'running',
      currentIteration: 1,
      totalIterations: workflow.value.loops?.maxIterations || 1,
      nodeStates: new Map(),
      startTime: Date.now()
    }

    console.log('[Canvas] Starting workflow execution...')

    try {
      const response = await fetch('/api/canvas/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nodes: workflow.value.nodes,
          connections: workflow.value.connections,
          workflow: {
            id: workflow.value.id,
            name: workflow.value.name
          }
        })
      })

      const data = await response.json()

      if (data.status === 'success') {
        executionResults.value = data.results || {}
        collectorOutput.value = data.collectorOutput || []

        if (executionState.value) {
          executionState.value.status = 'completed'
          executionState.value.endTime = Date.now()
        }

        console.log('[Canvas] Execution completed:', data.executionOrder)
        console.log('[Canvas] Collector output:', collectorOutput.value)
      } else {
        error.value = data.error || 'Execution failed'
        if (executionState.value) {
          executionState.value.status = 'failed'
          executionState.value.endTime = Date.now()
        }
        console.error('[Canvas] Execution error:', data.error)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Network error'
      if (executionState.value) {
        executionState.value.status = 'failed'
        executionState.value.endTime = Date.now()
      }
      console.error('[Canvas] Execution fetch error:', err)
    } finally {
      isExecuting.value = false
    }
  }

  /**
   * Interrupt workflow execution
   */
  function interruptExecution() {
    if (executionState.value) {
      executionState.value.status = 'interrupted'
      executionState.value.endTime = Date.now()
    }
    isExecuting.value = false
    console.log('[Canvas] Execution interrupted')
  }

  /**
   * Reset execution state
   */
  function resetExecution() {
    executionState.value = null
    isExecuting.value = false
  }

  // ============================================================================
  // RETURN PUBLIC API
  // ============================================================================

  return {
    // State
    workflow: computed(() => workflow.value),
    nodes,
    connections,
    selectedNodeId: computed(() => selectedNodeId.value),
    selectedNode,
    connectingFromId: computed(() => connectingFromId.value),
    mousePosition: computed(() => mousePosition.value),
    llmModels: computed(() => llmModels.value),
    outputConfigs: computed(() => outputConfigs.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    executionState: computed(() => executionState.value),
    isExecuting: computed(() => isExecuting.value),
    executionResults: computed(() => executionResults.value),
    collectorOutput: computed(() => collectorOutput.value),

    // Computed
    isConnecting,
    isWorkflowValid,
    validationErrors,

    // Node actions
    addNode,
    updateNodePosition,
    updateNodeConfig,
    updateNode,
    deleteNode,
    selectNode,

    // Connection actions
    startConnection,
    cancelConnection,
    completeConnection,
    deleteConnection,
    updateMousePosition,

    // Workflow actions
    newWorkflow,
    loadWorkflow,
    exportWorkflow,
    updateWorkflowMeta,

    // Config loading
    loadLLMModels,
    loadOutputConfigs,
    loadAllConfigs,

    // Execution
    executeWorkflow,
    interruptExecution,
    resetExecution
  }
})
