import axios, { type AxiosInstance } from 'axios'

/**
 * Centralized API Service for AI4ArtsEd DevServer
 *
 * Provides type-safe API methods for:
 * - Phase 1: Config fetching with properties
 * - Phase 2: Pipeline execution with multilingual context
 * - Phase 3: Entity retrieval and status polling
 *
 * Phase 2 - Multilingual Context Editing Implementation
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

/** Config metadata from /pipeline_configs_with_properties */
export interface ConfigMetadata {
  id: string
  name: { en: string; de: string }
  description: { en: string; de: string }
  short_description: { en: string; de: string }
  properties: string[]
  pipeline: string
  media_preferences?: {
    default_output?: string
  }
}

export type PropertyPair = [string, string]

export interface ConfigsWithPropertiesResponse {
  configs: ConfigMetadata[]
  property_pairs: PropertyPair[]
}

/** Pipeline execution request (Phase 2) */
export interface PipelineExecuteRequest {
  schema: string
  input_text: string
  user_language: 'de' | 'en'
  execution_mode?: 'eco' | 'fast' | 'best'
  safety_level?: 'kids' | 'youth' | 'adult'
  context_prompt?: string // Optional: user-edited meta-prompt
  context_language?: 'de' | 'en' // Language of context_prompt
}

/** Pipeline execution response */
export interface PipelineExecuteResponse {
  success: boolean
  final_output?: string
  media_output?: {
    output?: string // prompt_id for media polling
  }
  error?: string
  run_id?: string
}

/** Media info response (polling) */
export interface MediaInfoResponse {
  type: 'image' | 'audio' | 'video' | 'music'
  files: string[]
  prompt_id: string
}

/** Entity response (from exports) */
export interface EntityResponse {
  name: string
  content: string
  stage?: string
}

// ============================================================================
// AXIOS CLIENT
// ============================================================================

/** Base axios instance with default config */
const apiClient: AxiosInstance = axios.create({
  baseURL: '/', // DevServer serves on same origin
  timeout: 120000, // 2 minutes for long-running pipelines
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor (for logging)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor (for error handling)
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('[API] Response error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

// ============================================================================
// API METHODS
// ============================================================================

/**
 * Get all configs with properties (Phase 1)
 */
export async function getConfigsWithProperties(): Promise<ConfigsWithPropertiesResponse> {
  const response = await apiClient.get<ConfigsWithPropertiesResponse>(
    '/pipeline_configs_with_properties'
  )
  return response.data
}

/**
 * Get single config by ID
 */
export async function getConfig(configId: string): Promise<ConfigMetadata> {
  // This endpoint may not exist yet - fetch all and filter
  const data = await getConfigsWithProperties()
  const config = data.configs.find((c) => c.id === configId)
  if (!config) {
    throw new Error(`Config not found: ${configId}`)
  }
  return config
}

/**
 * Get config context (meta-prompt) for Phase 2
 *
 * Returns multilingual context: {en: "...", de: "..."} or string
 */
export interface ConfigContextResponse {
  config_id: string
  context: string | { en: string; de: string }
}

export async function getConfigContext(configId: string): Promise<ConfigContextResponse> {
  const response = await apiClient.get<ConfigContextResponse>(`/api/config/${configId}/context`)
  return response.data
}

/**
 * Execute pipeline (Phase 2)
 *
 * Supports multilingual context editing:
 * - If context_prompt provided, backend uses user-edited context
 * - If context_language != 'en', backend translates to English
 * - Both versions saved to exports/{run_id}/json/
 */
export async function executePipeline(
  request: PipelineExecuteRequest
): Promise<PipelineExecuteResponse> {
  const response = await apiClient.post<PipelineExecuteResponse>(
    '/api/schema/pipeline/execute',
    request
  )
  return response.data
}

/**
 * Get media info (Phase 3 polling)
 *
 * Returns 404 if not ready yet
 */
export async function getMediaInfo(promptId: string): Promise<MediaInfoResponse> {
  const response = await apiClient.get<MediaInfoResponse>(`/api/media/info/${promptId}`)
  return response.data
}

/**
 * Get media URL for display (Phase 3)
 */
export function getMediaUrl(promptId: string, type: 'image' | 'audio' | 'video' = 'image'): string {
  return `/api/media/${type}/${promptId}`
}

/**
 * Get entity from exports (Phase 3)
 *
 * Entities: input, translation, safety, interception, etc.
 */
export async function getEntity(runId: string, entityName: string): Promise<EntityResponse> {
  const response = await apiClient.get<EntityResponse>(`/api/entities/${runId}/${entityName}`)
  return response.data
}

/**
 * Get pipeline status (if implemented)
 */
export async function getPipelineStatus(runId: string): Promise<any> {
  const response = await apiClient.get(`/api/pipeline/status/${runId}`)
  return response.data
}

// ============================================================================
// EXPORT DEFAULT (for convenience imports)
// ============================================================================

export default {
  getConfigsWithProperties,
  getConfig,
  getConfigContext,
  executePipeline,
  getMediaInfo,
  getMediaUrl,
  getEntity,
  getPipelineStatus
}
