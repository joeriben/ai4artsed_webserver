"""
Pipeline-Executor: Central orchestration for config-based pipelines
REFACTORED for new architecture (config_loader instead of schema_registry)
ENHANCED with 4-Stage Pre-Interception System
"""
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import time
import json
import re

from .config_loader import config_loader, ResolvedConfig
from .chunk_builder import ChunkBuilder
from .backend_router import BackendRouter, BackendRequest, BackendResponse, BackendType

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class PipelineStep:
    """Single pipeline step"""
    step_id: str
    chunk_name: str
    status: PipelineStatus = PipelineStatus.PENDING
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineContext:
    """Pipeline context for data exchange between steps"""
    input_text: str
    user_input: str
    previous_outputs: List[str] = field(default_factory=list)
    custom_placeholders: Dict[str, Any] = field(default_factory=dict)
    pipeline_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_previous_output(self) -> str:
        """Get last pipeline output"""
        return self.previous_outputs[-1] if self.previous_outputs else self.input_text
    
    def add_output(self, output: str) -> None:
        """Add pipeline output"""
        self.previous_outputs.append(output)

@dataclass
class PipelineResult:
    """Pipeline execution result"""
    config_name: str  # Changed from schema_name
    status: PipelineStatus
    steps: List[PipelineStep]
    final_output: str = ""  # Pipeline output as string (JSON parsing goes to context.custom_placeholders)
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Pipeline succeeded if status is COMPLETED"""
        return self.status == PipelineStatus.COMPLETED

class PipelineExecutor:
    """Central pipeline orchestration"""
    
    def __init__(self, schemas_path: Path):
        self.schemas_path = schemas_path
        self.config_loader = config_loader
        self.chunk_builder = ChunkBuilder(schemas_path)
        self.backend_router = BackendRouter()
        self._initialized = False
        self._current_config = None  # Store for _execute_single_step access
        
    def initialize(self, ollama_service=None, workflow_logic_service=None, comfyui_service=None):
        """Initialize pipeline executor with legacy services"""
        self.config_loader.initialize(self.schemas_path)
        self.backend_router.initialize(
            ollama_service=ollama_service,
            workflow_logic_service=workflow_logic_service,
            comfyui_service=comfyui_service
        )
        self._initialized = True
        logger.info("Pipeline-Executor initialized")
    
    async def execute_pipeline(
        self,
        config_name: str,
        input_text: str,
        user_input: Optional[str] = None,
        execution_mode: str = 'eco',  # DEPRECATED (Session 65): Ignored. Model selection via config.py. TODO: Remove parameter.
        safety_level: str = 'kids',
        tracker=None,
        config_override=None,  # Phase 2: Optional pre-modified config
        context_override: Optional[PipelineContext] = None,  # Multi-stage: Pre-populated context
        seed_override: Optional[int] = None,  # Phase 4: Intelligent seed for media generation
        input_image: Optional[str] = None,  # Session 80: IMG2IMG support - path to input image
        alpha_factor: Optional[float] = None  # Surrealizer: T5-CLIP fusion alpha factor
    ) -> PipelineResult:
        """Execute complete pipeline with 4-Stage Pre-Interception System

        DEPRECATED: execution_mode parameter is no longer used.
        Model selection now configured per-stage in config.py (STAGE1_MODEL, STAGE2_MODEL, etc.)
        Parameter kept for backward compatibility only.

        Args:
            config_override: Optional pre-modified Config object (Phase 2 user edits)
                           If provided, uses this instead of loading from config_name
        """
        # Auto-initialization if needed
        if not self._initialized:
            logger.info("Auto-initialization: Config-Loader and Backend-Router")
            self.config_loader.initialize(self.schemas_path)
            self.backend_router.initialize()
            self._initialized = True

        logger.info(f"[PIPELINE] Executing config '{config_name}' (execution_mode={execution_mode} - DEPRECATED)")

        # Get config (use override if provided, otherwise load)
        if config_override:
            logger.info(f"[PHASE2] Using user-modified config override")
            resolved_config = config_override
        else:
            resolved_config = self.config_loader.get_config(config_name)

        if not resolved_config:
            return PipelineResult(
                config_name=config_name,
                status=PipelineStatus.FAILED,
                steps=[],
                error=f"Config '{config_name}' not found"
            )

        logger.info(f"Config '{config_name}' loaded: Pipeline='{resolved_config.pipeline_name}', Chunks={resolved_config.chunks}")

        # ====================================================================
        # DUMB EXECUTOR: Just execute chunks (Stage 1-3 in DevServer now)
        # ====================================================================
        # Store config for step execution
        self._current_config = resolved_config

        # Create pipeline context (or use override for multi-stage workflows)
        if context_override:
            context = context_override
            logger.info(f"[CONTEXT-OVERRIDE] Using pre-populated context with {len(context.custom_placeholders)} custom placeholders")
        else:
            context = PipelineContext(
                input_text=input_text,
                user_input=user_input or input_text
            )

        # Phase 4: Add seed_override to context if provided
        if seed_override is not None:
            context.custom_placeholders['seed_override'] = seed_override
            logger.info(f"[PHASE4-SEED] Added seed_override to context: {seed_override}")

        # Session 80: Add input_image to context if provided (IMG2IMG support)
        if input_image is not None:
            context.custom_placeholders['input_image'] = input_image
            logger.info(f"[IMG2IMG] Added input_image to context: {input_image}")

        # Surrealizer: Add alpha_factor to context if provided (T5-CLIP fusion)
        if alpha_factor is not None:
            context.custom_placeholders['alpha_factor'] = alpha_factor
            logger.info(f"[SURREALIZER] Added alpha_factor to context: {alpha_factor}")

        # Plan pipeline steps
        steps = self._plan_pipeline_steps(resolved_config)

        # Execute pipeline with execution_mode and tracker
        result = await self._execute_pipeline_steps(config_name, steps, context, execution_mode, tracker)

        logger.info(f"Pipeline for config '{config_name}' completed: {result.status}")
        return result
    
    async def stream_pipeline(self, config_name: str, input_text: str, user_input: Optional[str] = None, execution_mode: str = 'eco') -> AsyncGenerator[Tuple[str, Any], None]:
        """Execute pipeline with streaming updates"""
        if not self._initialized:
            yield ("error", "Pipeline-Executor not initialized")
            return
        
        logger.info(f"[EXECUTION-MODE] Streaming pipeline for config '{config_name}' with execution_mode='{execution_mode}'")
        
        resolved_config = self.config_loader.get_config(config_name)
        if not resolved_config:
            yield ("error", f"Config '{config_name}' not found")
            return
        
        # Store config for step execution
        self._current_config = resolved_config
        
        context = PipelineContext(
            input_text=input_text,
            user_input=user_input or input_text
        )
        
        steps = self._plan_pipeline_steps(resolved_config)
        
        yield ("pipeline_started", {
            "config_name": config_name,
            "pipeline_name": resolved_config.pipeline_name,
            "total_steps": len(steps),
            "input_text": input_text,
            "execution_mode": execution_mode
        })
        
        # Execute pipeline steps with streaming
        async for event_type, event_data in self._stream_pipeline_steps(config_name, steps, context, execution_mode):
            yield (event_type, event_data)
    
    def _plan_pipeline_steps(self, resolved_config: ResolvedConfig) -> List[PipelineStep]:
        """Plan pipeline steps from resolved config"""
        steps = []

        for i, chunk_name in enumerate(resolved_config.chunks):
            step = PipelineStep(
                step_id=f"step_{i+1}_{chunk_name}",
                chunk_name=chunk_name
            )
            steps.append(step)

        logger.debug(f"Pipeline planned: {len(steps)} steps for config '{resolved_config.name}' (Pipeline: {resolved_config.pipeline_name})")
        return steps
    
    async def _execute_pipeline_steps(self, config_name: str, steps: List[PipelineStep], context: PipelineContext, execution_mode: str = 'eco', tracker=None) -> PipelineResult:
        """Execute pipeline steps sequentially (or recursively if pipeline supports it)"""

        # Check if this is a recursive pipeline
        if self._current_config and self._current_config.pipeline_name == 'text_transformation_recursive':
            return await self._execute_recursive_pipeline_steps(config_name, steps, context, execution_mode, tracker)

        # Normal sequential execution
        start_time = time.time()
        completed_steps = []

        for step in steps:
            try:
                step.status = PipelineStatus.RUNNING
                output = await self._execute_single_step(step, context, execution_mode)

                step.status = PipelineStatus.COMPLETED
                step.output_data = output
                context.add_output(output)

                # Log chunk output for debugging (especially useful for translate chunk)
                logger.info(f"[CHUNK-OUTPUT] {step.chunk_name}: {output[:200]}...")

                # AUTO-PARSE JSON: If output is valid JSON dict, add to custom_placeholders
                # This enables multi-stage workflows where Stage 2 outputs structured data
                try:
                    parsed_output = json.loads(output)
                    if isinstance(parsed_output, dict):
                        # Convert keys to uppercase for placeholder consistency
                        for key, value in parsed_output.items():
                            placeholder_key = key.upper()
                            context.custom_placeholders[placeholder_key] = value
                        logger.info(f"[JSON-AUTO-PARSE] Parsed output and added {len(parsed_output)} placeholders: {list(parsed_output.keys())}")
                except (json.JSONDecodeError, TypeError, ValueError):
                    # Not JSON or not a dict - treat as normal string output
                    pass

                completed_steps.append(step)
                logger.debug(f"Step {step.step_id} successful: {len(output)} chars output")

            except Exception as e:
                step.status = PipelineStatus.FAILED
                step.error = str(e)
                completed_steps.append(step)

                logger.error(f"Step {step.step_id} failed: {e}")

                return PipelineResult(
                    config_name=config_name,
                    status=PipelineStatus.FAILED,
                    steps=completed_steps,
                    error=f"Step {step.step_id} failed: {e}",
                    execution_time=time.time() - start_time
                )

        final_output = context.get_previous_output()

        # Merge backend metadata from last step (contains image_paths, seed, etc.)
        result_metadata = {
            "total_steps": len(steps),
            "input_length": len(context.input_text),
            "output_length": len(final_output),
            "pipeline_name": self._current_config.pipeline_name if self._current_config else None
        }

        # Add backend metadata from last completed step (e.g., image_paths from SwarmUI)
        if completed_steps:
            last_step_metadata = completed_steps[-1].metadata
            # Merge backend-specific keys into result metadata
            for key in ['image_paths', 'seed', 'model', 'media_type', 'swarmui_available', 'parameters', 'filesystem_path', 'prompt_id', 'workflow_completed', 'legacy_workflow', 'media_files', 'outputs_metadata', 'workflow_json', 'download_all', 'chunk_name']:
                if key in last_step_metadata:
                    result_metadata[key] = last_step_metadata[key]

        return PipelineResult(
            config_name=config_name,
            status=PipelineStatus.COMPLETED,
            steps=completed_steps,
            final_output=final_output,
            execution_time=time.time() - start_time,
            metadata=result_metadata
        )

    async def _execute_recursive_pipeline_steps(self, config_name: str, steps: List[PipelineStep], context: PipelineContext, execution_mode: str = 'eco', tracker=None) -> PipelineResult:
        """Execute recursive pipeline with internal loop (e.g., Stille Post)"""
        from .random_language_selector import get_random_language, get_language_name

        start_time = time.time()
        completed_steps = []

        # Read loop configuration from config parameters
        config_params = self._current_config.parameters or {}
        iterations = config_params.get('iterations', 8)
        use_random = config_params.get('use_random_languages', True)
        final_language = config_params.get('final_language', 'en')
        fixed_languages = config_params.get('languages', [])

        # Set stage 2 context for tracker
        if tracker:
            tracker.set_stage(2)

        # Generate language sequence
        if use_random:
            # Generate random language sequence
            languages = []
            for i in range(iterations - 1):
                lang = get_random_language(exclude=languages[-1:] if languages else [])
                languages.append(lang)
            languages.append(final_language)  # Always end with final_language
            logger.info(f"[RECURSIVE-PIPELINE] Random language sequence: {languages}")
        else:
            # Use fixed language list from config
            languages = fixed_languages
            if len(languages) < iterations:
                logger.warning(f"[RECURSIVE-PIPELINE] Fixed languages list too short ({len(languages)} < {iterations}), padding with final_language")
                languages = languages + [final_language] * (iterations - len(languages))
            languages = languages[:iterations]  # Trim to iterations
            logger.info(f"[RECURSIVE-PIPELINE] Fixed language sequence: {languages}")

        # Execute loop: one step per language
        for i, target_lang in enumerate(languages):
            step = PipelineStep(
                step_id=f"loop_{i+1}_{target_lang}",
                chunk_name=steps[0].chunk_name if steps else "manipulate"
            )

            try:
                step.status = PipelineStatus.RUNNING

                # Add target_language to custom placeholders
                context.custom_placeholders['TARGET_LANGUAGE'] = get_language_name(target_lang)
                context.custom_placeholders['TARGET_LANGUAGE_CODE'] = target_lang

                logger.info(f"[RECURSIVE-LOOP] Iteration {i+1}/{iterations}: Translating to {get_language_name(target_lang)} ({target_lang})")

                output = await self._execute_single_step(step, context, execution_mode)

                step.status = PipelineStatus.COMPLETED
                step.output_data = output
                context.add_output(output)

                completed_steps.append(step)
                logger.debug(f"[RECURSIVE-LOOP] Iteration {i+1} successful: {len(output)} chars")

                # Log iteration to tracker (if available)
                if tracker:
                    # Determine from_lang (previous language or 'en' for first iteration)
                    from_lang = languages[i-1] if i > 0 else 'en'
                    to_lang = target_lang

                    # Extract metadata from step
                    model_used = step.metadata.get('model_used') if step.metadata else None
                    backend_type = step.metadata.get('backend_type') if step.metadata else None

                    # Calculate iteration execution time (approximate from step timing)
                    iteration_time = time.time() - start_time - sum(
                        getattr(s, 'execution_time', 0) or 0 for s in completed_steps[:-1]
                    )

                    try:
                        tracker.log_interception_iteration(
                            iteration_num=i+1,
                            result_text=output,
                            from_lang=from_lang,
                            to_lang=to_lang,
                            model_used=model_used or 'unknown',
                            config_used=config_name
                        )
                    except Exception as log_error:
                        logger.warning(f"[TRACKER] Failed to log iteration {i+1}: {log_error}")

            except Exception as e:
                step.status = PipelineStatus.FAILED
                step.error = str(e)
                completed_steps.append(step)

                logger.error(f"[RECURSIVE-LOOP] Iteration {i+1} failed: {e}")

                return PipelineResult(
                    config_name=config_name,
                    status=PipelineStatus.FAILED,
                    steps=completed_steps,
                    error=f"Loop iteration {i+1} failed: {e}",
                    execution_time=time.time() - start_time
                )

        final_output = context.get_previous_output()

        return PipelineResult(
            config_name=config_name,
            status=PipelineStatus.COMPLETED,
            steps=completed_steps,
            final_output=final_output,
            execution_time=time.time() - start_time,
            metadata={
                "total_steps": len(completed_steps),
                "input_length": len(context.input_text),
                "output_length": len(final_output),
                "pipeline_name": self._current_config.pipeline_name,
                "iterations": iterations,
                "language_sequence": languages
            }
        )
    
    async def _stream_pipeline_steps(self, config_name: str, steps: List[PipelineStep], context: PipelineContext, execution_mode: str = 'eco') -> AsyncGenerator[Tuple[str, Any], None]:
        """Execute pipeline steps with streaming updates"""
        for i, step in enumerate(steps):
            yield ("step_started", {
                "step_id": step.step_id,
                "step_number": i + 1,
                "chunk_name": step.chunk_name
            })
            
            try:
                step.status = PipelineStatus.RUNNING
                output = await self._execute_single_step(step, context, execution_mode)
                
                step.status = PipelineStatus.COMPLETED
                step.output_data = output
                context.add_output(output)
                
                yield ("step_completed", {
                    "step_id": step.step_id,
                    "output": output,
                    "output_length": len(output)
                })
                
            except Exception as e:
                step.status = PipelineStatus.FAILED
                step.error = str(e)
                
                yield ("step_failed", {
                    "step_id": step.step_id,
                    "error": str(e)
                })
                
                yield ("pipeline_failed", {
                    "config_name": config_name,
                    "failed_step": step.step_id,
                    "error": str(e)
                })
                return
        
        final_output = context.get_previous_output()
        yield ("pipeline_completed", {
            "config_name": config_name,
            "final_output": final_output,
            "total_steps": len(steps)
        })
    
    async def _execute_single_step(self, step: PipelineStep, context: PipelineContext, execution_mode: str = 'eco') -> str:
        """Execute single pipeline step"""
        chunk_context = {
            "input_text": context.input_text,
            "user_input": context.user_input,
            "previous_output": context.get_previous_output(),
            "custom_placeholders": context.custom_placeholders
        }

        # Debug: Log chunk context
        logger.info(f"[CHUNK-CONTEXT] input_text: '{chunk_context['input_text'][:50]}...'")
        logger.info(f"[CHUNK-CONTEXT] previous_output: '{chunk_context['previous_output'][:50]}...'")
        
        chunk_request = self.chunk_builder.build_chunk(
            chunk_name=step.chunk_name,
            resolved_config=self._current_config,
            context=chunk_context
        )

        step.input_data = chunk_request['prompt']
        step.metadata.update(chunk_request['metadata'])

        # Phase 4: Add seed_override to parameters if present in context
        if 'seed_override' in context.custom_placeholders:
            seed_value = context.custom_placeholders['seed_override']
            chunk_request['parameters']['seed'] = seed_value  # lowercase!
            logger.info(f"[PHASE4-SEED] Injected seed into chunk parameters: {seed_value}")

        # Session 80: Add input_image to parameters if present in context (IMG2IMG support)
        if 'input_image' in context.custom_placeholders:
            image_path = context.custom_placeholders['input_image']
            chunk_request['parameters']['input_image'] = image_path
            logger.info(f"[IMG2IMG] Injected input_image into chunk parameters: {image_path}")

        # Surrealizer: Add alpha_factor to parameters if present in context (T5-CLIP fusion)
        if 'alpha_factor' in context.custom_placeholders:
            alpha_value = context.custom_placeholders['alpha_factor']
            chunk_request['parameters']['alpha_factor'] = alpha_value
            logger.info(f"[SURREALIZER] Injected alpha_factor into chunk parameters: {alpha_value}")

        # Add ALL custom placeholders to parameters (for legacy workflows with input_mappings)
        for key, value in context.custom_placeholders.items():
            if key not in chunk_request['parameters']:  # Don't overwrite existing
                chunk_request['parameters'][key] = value
                logger.info(f"[CUSTOM-PARAMS] Injected '{key}' = '{str(value)[:50]}' into chunk parameters")

        backend_request = BackendRequest(
            backend_type=BackendType(chunk_request['backend_type']),
            model=chunk_request['model'],
            prompt=chunk_request['prompt'],
            parameters=chunk_request['parameters']
        )
        
        response = await self.backend_router.process_request(backend_request)

        if isinstance(response, BackendResponse):
            if response.success:
                # Merge ALL backend metadata into step.metadata (preserves image_paths, seed, etc.)
                step.metadata.update(response.metadata)
                # Ensure fallbacks for critical fields
                step.metadata['model_used'] = response.metadata.get('model_used', chunk_request['model'])
                step.metadata['backend_type'] = response.metadata.get('backend_type', chunk_request['backend_type'])
                return response.content
            else:
                raise RuntimeError(f"Backend error: {response.error}")
        else:
            raise RuntimeError("Streaming not supported in single steps")
    
    def get_available_configs(self) -> List[str]:
        """List all available configs"""
        return self.config_loader.list_configs()
    
    def get_config_info(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get config information"""
        resolved_config = self.config_loader.get_config(config_name)
        if not resolved_config:
            return None

        return {
            "name": resolved_config.name,
            "display_name": resolved_config.display_name,
            "description": resolved_config.description,
            "pipeline_name": resolved_config.pipeline_name,
            "chunks": resolved_config.chunks,
            "parameters": resolved_config.parameters,
            "meta": resolved_config.meta
        }
    
    # Backward compatibility aliases
    def get_available_schemas(self) -> List[str]:
        """Backward compatibility: List all available configs"""
        return self.get_available_configs()
    
    def get_schema_info(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Backward compatibility: Get config information"""
        return self.get_config_info(schema_name)

# Singleton instance
executor = PipelineExecutor(Path(__file__).parent.parent)
