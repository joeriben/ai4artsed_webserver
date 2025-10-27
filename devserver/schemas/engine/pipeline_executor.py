"""
Pipeline-Executor: Central orchestration for config-based pipelines
REFACTORED for new architecture (config_loader instead of schema_registry)
"""
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import time

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
    final_output: Optional[str] = None
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
    
    async def execute_pipeline(self, config_name: str, input_text: str, user_input: Optional[str] = None, execution_mode: str = 'eco') -> PipelineResult:
        """Execute complete pipeline"""
        # Auto-initialization if needed
        if not self._initialized:
            logger.info("Auto-initialization: Config-Loader and Backend-Router")
            self.config_loader.initialize(self.schemas_path)
            self.backend_router.initialize()
            self._initialized = True
        
        logger.info(f"[EXECUTION-MODE] Pipeline for config '{config_name}' with execution_mode='{execution_mode}'")
        
        # Get config
        resolved_config = self.config_loader.get_config(config_name)
        if not resolved_config:
            return PipelineResult(
                config_name=config_name,
                status=PipelineStatus.FAILED,
                steps=[],
                error=f"Config '{config_name}' not found"
            )
        
        logger.info(f"Config '{config_name}' loaded: Pipeline='{resolved_config.pipeline_name}', Chunks={resolved_config.chunks}")
        
        # Store config for step execution
        self._current_config = resolved_config
        
        # Create pipeline context
        context = PipelineContext(
            input_text=input_text,
            user_input=user_input or input_text
        )
        
        # Plan pipeline steps
        steps = self._plan_pipeline_steps(resolved_config)
        
        # Execute pipeline with execution_mode
        result = await self._execute_pipeline_steps(config_name, steps, context, execution_mode)
        
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
    
    async def _execute_pipeline_steps(self, config_name: str, steps: List[PipelineStep], context: PipelineContext, execution_mode: str = 'eco') -> PipelineResult:
        """Execute pipeline steps sequentially"""
        start_time = time.time()
        completed_steps = []
        
        for step in steps:
            try:
                step.status = PipelineStatus.RUNNING
                output = await self._execute_single_step(step, context, execution_mode)
                
                step.status = PipelineStatus.COMPLETED
                step.output_data = output
                context.add_output(output)
                
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
        
        return PipelineResult(
            config_name=config_name,
            status=PipelineStatus.COMPLETED,
            steps=completed_steps,
            final_output=final_output,
            execution_time=time.time() - start_time,
            metadata={
                "total_steps": len(steps),
                "input_length": len(context.input_text),
                "output_length": len(final_output),
                "pipeline_name": self._current_config.pipeline_name if self._current_config else None
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
            context=chunk_context,
            execution_mode=execution_mode
        )
        
        step.input_data = chunk_request['prompt']
        step.metadata.update(chunk_request['metadata'])
        
        backend_request = BackendRequest(
            backend_type=BackendType(chunk_request['backend_type']),
            model=chunk_request['model'],
            prompt=chunk_request['prompt'],
            parameters=chunk_request['parameters']
        )
        
        response = await self.backend_router.process_request(backend_request)
        
        if isinstance(response, BackendResponse):
            if response.success:
                step.metadata['model_used'] = chunk_request['model']
                step.metadata['backend_type'] = chunk_request['backend_type']
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
