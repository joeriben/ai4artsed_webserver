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

# ============================================================================
# 4-STAGE SYSTEM: EXCEPTIONS
# ============================================================================

class SafetyViolationError(Exception):
    """Raised when content fails safety check"""
    def __init__(self, message: str, codes: List[str]):
        super().__init__(message)
        self.codes = codes
        self.user_message = message

# ============================================================================
# 4-STAGE SYSTEM HELPER FUNCTIONS
# ============================================================================

def parse_llamaguard_output(output: str) -> Tuple[bool, List[str]]:
    """
    Parse Llama-Guard output format:
    "safe" → (True, [])
    "unsafe\nS1,S3" → (False, ['S1', 'S3'])
    "unsafe,S8, Violent Crimes" → (False, ['S8'])
    """
    lines = output.strip().split('\n')
    first_line = lines[0].strip().lower()

    if first_line == 'safe':
        return (True, [])
    elif first_line.startswith('unsafe'):
        # Handle two formats:
        # Format 1: "unsafe\nS1,S3" (two lines)
        # Format 2: "unsafe,S8, Violent Crimes" (one line with comma)

        if ',' in first_line:
            # Format 2: Extract codes from first line after "unsafe,"
            parts = first_line.split(',', 1)[1].strip()
            # Extract S-codes (S1, S2, etc.)
            import re
            codes = re.findall(r'S\d+', parts)
            return (False, codes)
        elif len(lines) > 1:
            # Format 1: Codes on second line
            codes = [code.strip() for code in lines[1].split(',')]
            return (False, codes)
        return (False, [])
    else:
        # Unexpected format
        logger.warning(f"Unexpected Llama-Guard output format: {output[:100]}")
        return (True, [])  # Default to safe if uncertain

def build_safety_message(codes: List[str], lang: str = 'de') -> str:
    """
    Build user-friendly safety message from Llama-Guard codes using llama_guard_explanations.json
    """
    explanations_path = Path(__file__).parent.parent / 'llama_guard_explanations.json'

    try:
        with open(explanations_path, 'r', encoding='utf-8') as f:
            explanations = json.load(f)

        base_msg = explanations['base_message'][lang]
        hint_msg = explanations['hint_message'][lang]

        # Build message from codes
        messages = []
        for code in codes:
            if code in explanations['codes']:
                messages.append(f"• {explanations['codes'][code][lang]}")
            else:
                messages.append(f"• Code: {code}")

        if not messages:
            return explanations['fallback'][lang]

        full_message = base_msg + "\n\n" + "\n".join(messages) + hint_msg
        return full_message

    except Exception as e:
        logger.error(f"Error building safety message: {e}")
        return "Dein Prompt wurde aus Sicherheitsgründen blockiert." if lang == 'de' else "Your prompt was blocked for safety reasons."

def parse_preoutput_json(output: str) -> Dict[str, Any]:
    """
    Parse JSON output from pre-output pipeline.
    Expected format:
    {
      "safe": true/false,
      "positive_prompt": "...",
      "negative_prompt": "...",
      "abort_reason": null/"reason"
    }
    """
    try:
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*|\s*```', '', output.strip())
        parsed = json.loads(cleaned)

        # Validate required fields
        if 'safe' not in parsed:
            raise ValueError("Missing 'safe' field in pre-output JSON")

        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse pre-output JSON: {e}\nOutput: {output[:200]}")
        # Return safe default to allow continuation
        return {
            "safe": True,
            "positive_prompt": output,
            "negative_prompt": "blurry, low quality, bad anatomy",
            "abort_reason": None
        }
    except Exception as e:
        logger.error(f"Error parsing pre-output JSON: {e}")
        return {
            "safe": True,
            "positive_prompt": output,
            "negative_prompt": "blurry, low quality, bad anatomy",
            "abort_reason": None
        }

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
        """Execute complete pipeline with 4-Stage Pre-Interception System"""
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

        # ====================================================================
        # STAGE 1: PRE-INTERCEPTION (Translation + Safety)
        # ====================================================================
        is_system_pipeline = resolved_config.meta.get('system_pipeline', False)
        current_input = input_text

        if not is_system_pipeline:
            logger.info("[4-STAGE] Stage 1: Pre-Interception")

            # Stage 1a: Correction + Translation (ALWAYS runs for ALL inputs)
            logger.info("[4-STAGE] Running correction + translation")
            try:
                translation_result = await self.execute_pipeline(
                    'pre_interception/correction_translation_de_en',
                    current_input,
                    user_input,
                    execution_mode
                )
                if translation_result.success:
                    current_input = translation_result.final_output
                    logger.info(f"[4-STAGE] Translation complete: {current_input[:100]}...")
                else:
                    logger.warning(f"[4-STAGE] Translation failed: {translation_result.error}")
            except Exception as e:
                logger.error(f"[4-STAGE] Translation error: {e}")
                # Continue with original input if translation fails

            # Stage 1b: Safety Check (Llama-Guard)
            logger.info("[4-STAGE] Running Llama-Guard safety check")
            try:
                safety_result = await self.execute_pipeline(
                    'pre_interception/safety_llamaguard',
                    current_input,
                    user_input,
                    execution_mode
                )

                if safety_result.success:
                    is_safe, codes = parse_llamaguard_output(safety_result.final_output)

                    if not is_safe:
                        # Build user-friendly error message
                        error_message = build_safety_message(codes, lang='de')
                        logger.warning(f"[4-STAGE] Safety check FAILED: {codes}")

                        # Return failed result with safety message
                        return PipelineResult(
                            config_name=config_name,
                            status=PipelineStatus.FAILED,
                            steps=[],
                            error=error_message,
                            metadata={"safety_codes": codes, "stage": "pre_interception"}
                        )
                    else:
                        logger.info("[4-STAGE] Safety check PASSED")
                else:
                    logger.warning(f"[4-STAGE] Safety check execution failed: {safety_result.error}")
                    # Continue despite safety check failure (fail-open for now)
            except Exception as e:
                logger.error(f"[4-STAGE] Safety check error: {e}")
                # Continue despite safety check error (fail-open for now)

        # Store config for step execution
        self._current_config = resolved_config

        # ====================================================================
        # STAGE 2: INTERCEPTION (Main Pipeline) or System Pipeline Execution
        # ====================================================================
        if is_system_pipeline:
            logger.info(f"[SYSTEM-PIPELINE] Executing system pipeline: {config_name}")
        else:
            logger.info("[4-STAGE] Stage 2: Interception (Main Pipeline)")

        # Create pipeline context with potentially translated input
        context = PipelineContext(
            input_text=current_input,  # Use translated input
            user_input=user_input or input_text  # Keep original for reference
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
