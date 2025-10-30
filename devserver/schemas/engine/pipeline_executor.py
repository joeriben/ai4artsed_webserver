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
# HYBRID STAGE 3: Fast String-Matching + LLM Context Verification
# ============================================================================

# Cache for filter terms (loaded once at module level)
_FILTER_TERMS_CACHE: Optional[Dict[str, List[str]]] = None

def load_filter_terms() -> Dict[str, List[str]]:
    """Load all filter terms from JSON files (cached)"""
    global _FILTER_TERMS_CACHE

    if _FILTER_TERMS_CACHE is None:
        try:
            # Load Stage 3 filters (Youth/Kids)
            stage3_path = Path(__file__).parent.parent / "youth_kids_safety_filters.json"
            with open(stage3_path, 'r', encoding='utf-8') as f:
                stage3_data = json.load(f)

            # Load Stage 1 filters (CSAM/Violence/Hate)
            stage1_path = Path(__file__).parent.parent / "stage1_safety_filters.json"
            with open(stage1_path, 'r', encoding='utf-8') as f:
                stage1_data = json.load(f)

            _FILTER_TERMS_CACHE = {
                'kids': stage3_data['filters']['kids']['terms'],
                'youth': stage3_data['filters']['youth']['terms'],
                'stage1': stage1_data['filters']['stage1']['terms']
            }
            logger.info(f"Loaded filter terms: stage1={len(_FILTER_TERMS_CACHE['stage1'])}, kids={len(_FILTER_TERMS_CACHE['kids'])}, youth={len(_FILTER_TERMS_CACHE['youth'])}")
        except Exception as e:
            logger.error(f"Failed to load filter terms: {e}")
            _FILTER_TERMS_CACHE = {'kids': [], 'youth': [], 'stage1': []}

    return _FILTER_TERMS_CACHE

def fast_filter_check(prompt: str, safety_level: str) -> Tuple[bool, List[str]]:
    """
    Fast string-matching against filter lists (~0.001s)

    Returns:
        (has_terms, found_terms) - True if problematic terms found
    """
    filter_terms = load_filter_terms()
    terms_list = filter_terms.get(safety_level, [])

    if not terms_list:
        logger.warning(f"No filter terms for safety_level '{safety_level}'")
        return (False, [])

    prompt_lower = prompt.lower()
    found_terms = [term for term in terms_list if term.lower() in prompt_lower]

    return (len(found_terms) > 0, found_terms)

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
    Parse output from pre-output pipeline.
    Accepts two formats:
    1. Plain text: "safe" or "unsafe" (llama-guard format)
    2. JSON: {"safe": true/false, "positive_prompt": "...", ...}
    """
    output_cleaned = output.strip().lower()

    # CASE 1: Plain text "safe"/"unsafe" from llama-guard
    if output_cleaned == "safe":
        return {
            "safe": True,
            "positive_prompt": None,
            "negative_prompt": None,
            "abort_reason": None
        }
    elif output_cleaned.startswith("unsafe"):
        # llama-guard returns "unsafe\nS1\nS2" etc.
        return {
            "safe": False,
            "positive_prompt": None,
            "negative_prompt": None,
            "abort_reason": "Content flagged as unsafe by safety filter"
        }

    # CASE 2: Try JSON parsing
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
    
    async def execute_pipeline(self, config_name: str, input_text: str, user_input: Optional[str] = None, execution_mode: str = 'eco', safety_level: str = 'kids') -> PipelineResult:
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
                    execution_mode,
                    safety_level
                )
                if translation_result.success:
                    current_input = translation_result.final_output
                    logger.info(f"[4-STAGE] Translation complete: {current_input[:100]}...")
                else:
                    logger.warning(f"[4-STAGE] Translation failed: {translation_result.error}")
            except Exception as e:
                logger.error(f"[4-STAGE] Translation error: {e}")
                # Continue with original input if translation fails

            # Stage 1b: Hybrid Safety Check (Fast string-match + Llama-Guard)
            logger.info("[4-STAGE] Running hybrid safety check (Stage 1)")
            try:
                # HYBRID APPROACH: Fast string-match first
                start_time = time.time()
                has_terms, found_terms = fast_filter_check(current_input, 'stage1')
                fast_check_time = time.time() - start_time

                if not has_terms:
                    # FAST PATH: No problematic terms → instantly safe (95% of requests)
                    logger.info(f"[4-STAGE] Stage 1 PASSED (fast-path, {fast_check_time*1000:.1f}ms)")
                else:
                    # SLOW PATH: Terms found → Llama-Guard context verification
                    logger.info(f"[4-STAGE] Stage 1 found terms {found_terms[:3]}... → Llama-Guard check (fast: {fast_check_time*1000:.1f}ms)")

                    llm_start_time = time.time()
                    safety_result = await self.execute_pipeline(
                        'pre_interception/safety_llamaguard',
                        current_input,
                        user_input,
                        execution_mode,
                        safety_level
                    )
                    llm_check_time = time.time() - llm_start_time

                    if safety_result.success:
                        is_safe, codes = parse_llamaguard_output(safety_result.final_output)

                        if not is_safe:
                            # Build user-friendly error message
                            error_message = build_safety_message(codes, lang='de')
                            logger.warning(f"[4-STAGE] Stage 1 BLOCKED by Llama-Guard: {codes} (llm: {llm_check_time:.1f}s)")

                            # Return failed result with safety message
                            return PipelineResult(
                                config_name=config_name,
                                status=PipelineStatus.FAILED,
                                steps=[],
                                error=error_message,
                                metadata={"safety_codes": codes, "stage": "pre_interception", "found_terms": found_terms}
                            )
                        else:
                            # FALSE POSITIVE: Terms found but context is safe
                            logger.info(f"[4-STAGE] Stage 1 PASSED (Llama-Guard verified false positive, llm: {llm_check_time:.1f}s)")
                    else:
                        logger.warning(f"[4-STAGE] Stage 1 Llama-Guard failed: {safety_result.error}")
                        # Continue despite safety check failure (fail-open for now)
            except Exception as e:
                logger.error(f"[4-STAGE] Stage 1 safety check error: {e}")
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

        # ====================================================================
        # STAGE 3: PRE-OUTPUT (Hybrid Safety Check before Media Generation)
        # ====================================================================
        # Only run if:
        # 1. Pipeline succeeded
        # 2. Not a system pipeline
        # 3. Config requests media output (not text)
        # 4. Safety level is not 'off'
        if (result.success and
            not is_system_pipeline and
            resolved_config.media_preferences and
            resolved_config.media_preferences.get('default_output') not in [None, 'text'] and
            safety_level != 'off'):

            media_type = resolved_config.media_preferences.get('default_output')
            # safety_level comes from request parameter, NOT from config
            # (passed as function parameter from schema_pipeline_routes.py)

            logger.info(f"[4-STAGE] Stage 3: Pre-Output hybrid safety check for {media_type} (level: {safety_level})")

            try:
                # HYBRID APPROACH: Fast string-match first, then LLM context verification
                start_time = time.time()
                has_terms, found_terms = fast_filter_check(result.final_output, safety_level)
                fast_check_time = time.time() - start_time

                if not has_terms:
                    # FAST PATH: No problematic terms → instantly safe (95% of requests)
                    logger.info(f"[4-STAGE] Stage 3 PASSED (fast-path, {fast_check_time*1000:.1f}ms)")
                    result.metadata['stage_3_safe'] = True
                    result.metadata['stage_3_method'] = 'fast_filter'
                    result.metadata['safety_level'] = safety_level
                    # No negative_prompt modification needed for safe content
                else:
                    # SLOW PATH: Terms found → LLM context verification (prevents false positives)
                    logger.info(f"[4-STAGE] Stage 3 found terms {found_terms[:3]}... → LLM context check (fast: {fast_check_time*1000:.1f}ms)")

                    # Determine which pre-output config to use
                    # Note: Config loader uses string name field, not file path
                    pre_output_config = f'text_safety_check_{safety_level}'

                    llm_start_time = time.time()
                    safety_result = await self.execute_pipeline(
                        pre_output_config,
                        result.final_output,  # Check the transformed prompt
                        user_input,
                        execution_mode,
                        safety_level
                    )
                    llm_check_time = time.time() - llm_start_time

                    if safety_result.success:
                        # Parse JSON output
                        safety_data = parse_preoutput_json(safety_result.final_output)

                        if not safety_data.get('safe', True):
                            # UNSAFE: LLM confirmed it's problematic in context
                            abort_reason = safety_data.get('abort_reason', 'Content blocked by safety filter')
                            logger.warning(f"[4-STAGE] Stage 3 BLOCKED by LLM: {abort_reason} (llm: {llm_check_time:.1f}s)")

                            # Build user-friendly German message
                            error_message = f"🛡️ Sicherheitsfilter ({safety_level.upper()}):\n\n{abort_reason}\n\nℹ️ Dein Text wurde verarbeitet, aber die Bildgenerierung wurde aus Sicherheitsgründen blockiert."

                            # Return COMPLETED with text-only (no media generation)
                            result.metadata['stage_3_blocked'] = True
                            result.metadata['stage_3_method'] = 'llm_context_check'
                            result.metadata['safety_level'] = safety_level
                            result.metadata['abort_reason'] = abort_reason
                            result.metadata['found_terms'] = found_terms
                            result.final_output = f"{result.final_output}\n\n---\n\n{error_message}"

                            logger.info(f"[4-STAGE] Returning text-only result (media blocked)")
                        else:
                            # SAFE: False positive (e.g., "CD player", "dark chocolate")
                            logger.info(f"[4-STAGE] Stage 3 PASSED (LLM verified false positive, llm: {llm_check_time:.1f}s)")
                            result.metadata['stage_3_safe'] = True
                            result.metadata['stage_3_method'] = 'llm_context_check'
                            result.metadata['safety_level'] = safety_level
                            result.metadata['found_terms'] = found_terms
                            result.metadata['false_positive'] = True
                            result.metadata['positive_prompt'] = safety_data.get('positive_prompt', result.final_output)
                            result.metadata['negative_prompt'] = safety_data.get('negative_prompt', '')

                    else:
                        logger.warning(f"[4-STAGE] LLM check failed: {safety_result.error}")
                        # Continue with generation (fail-open)

            except Exception as e:
                logger.error(f"[4-STAGE] Stage 3 check error: {e}")
                import traceback
                traceback.print_exc()
                # Continue with generation (fail-open)

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
