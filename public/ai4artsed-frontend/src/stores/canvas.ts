import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type {
  CanvasNode,
  CanvasConnection,
  CanvasWorkflow,
  StageType,
  NodeExecutionState,
  WorkflowExecutionState,
  InterceptionConfigSummary,
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

  /** Current mouse position (for connection preview) */
  const mousePosition = ref({ x: 0, y: 0 })

  /** Available interception configs */
  const interceptionConfigs = ref<InterceptionConfigSummary[]>([])

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
   * NOTE: Safety is NOT checked here - DevServer handles it automatically
   */
  const isWorkflowValid = computed(() => {
    const hasInput = workflow.value.nodes.some(n => n.type === 'input')
    const hasGeneration = workflow.value.nodes.some(n => n.type === 'generation')
    const hasCollector = workflow.value.nodes.some(n => n.type === 'collector')

    // Check all generation nodes have configs selected
    const generationNodes = workflow.value.nodes.filter(n => n.type === 'generation')
    const allGenerationConfigured = generationNodes.every(n => n.configId)

    // Check all interception nodes have either configId OR llmModel
    const interceptionNodes = workflow.value.nodes.filter(n => n.type === 'interception')
    const allInterceptionConfigured = interceptionNodes.every(n => n.configId || n.llmModel)

    return hasInput && hasGeneration && hasCollector && allGenerationConfigured && allInterceptionConfigured
  })

  /**
   * Get validation errors
   *
   * NOTE: Safety is NOT validated here - DevServer handles it automatically
   */
  const validationErrors = computed(() => {
    const errors: string[] = []

    if (!workflow.value.nodes.some(n => n.type === 'input')) {
      errors.push('Missing input node')
    }
    if (!workflow.value.nodes.some(n => n.type === 'generation')) {
      errors.push('Missing generation node')
    }
    if (!workflow.value.nodes.some(n => n.type === 'collector')) {
      errors.push('Missing media collector node')
    }

    const generationNodes = workflow.value.nodes.filter(n => n.type === 'generation')
    generationNodes.forEach(n => {
      if (!n.configId) {
        errors.push(`Generation node missing output config`)
      }
    })

    const interceptionNodes = workflow.value.nodes.filter(n => n.type === 'interception')
    interceptionNodes.forEach(n => {
      if (!n.configId && !n.llmModel) {
        errors.push(`Interception node needs LLM or config selection`)
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
   */
  function startConnection(nodeId: string) {
    connectingFromId.value = nodeId
  }

  /**
   * Cancel connection creation
   */
  function cancelConnection() {
    connectingFromId.value = null
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
    workflow.value.connections.push({
      sourceId: connectingFromId.value,
      targetId
    })

    console.log(`[Canvas] Added connection: ${connectingFromId.value} -> ${targetId}`)
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
   * Load available interception configs from backend
   */
  async function loadInterceptionConfigs() {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/canvas/interception-configs')
      if (!response.ok) {
        throw new Error(`Failed to load interception configs: ${response.statusText}`)
      }
      const data = await response.json()
      interceptionConfigs.value = data.configs || []
      console.log(`[Canvas] Loaded ${interceptionConfigs.value.length} interception configs`)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load configs'
      console.error('[Canvas] Error loading interception configs:', err)
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
      loadInterceptionConfigs(),
      loadOutputConfigs()
    ])
  }

  // ============================================================================
  // EXECUTION (placeholder for Phase 3)
  // ============================================================================

  /**
   * Start workflow execution
   */
  async function executeWorkflow() {
    if (!isWorkflowValid.value) {
      error.value = 'Workflow is not valid'
      console.error('[Canvas] Cannot execute invalid workflow:', validationErrors.value)
      return
    }

    isExecuting.value = true
    executionState.value = {
      workflowId: workflow.value.id,
      status: 'running',
      currentIteration: 1,
      totalIterations: workflow.value.loops?.maxIterations || 1,
      nodeStates: new Map(),
      startTime: Date.now()
    }

    console.log('[Canvas] Starting workflow execution...')
    // TODO: Implement actual execution in Phase 3
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
    interceptionConfigs: computed(() => interceptionConfigs.value),
    outputConfigs: computed(() => outputConfigs.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    executionState: computed(() => executionState.value),
    isExecuting: computed(() => isExecuting.value),

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
    loadInterceptionConfigs,
    loadOutputConfigs,
    loadAllConfigs,

    // Execution
    executeWorkflow,
    interruptExecution,
    resetExecution
  }
})
