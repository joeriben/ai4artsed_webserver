"""
Schema Pipeline Routes - API für Schema-basierte Pipeline-Execution
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import logging
import asyncio
import json
import uuid

# Schema-Engine importieren
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.prompt_interception_engine import PromptInterceptionEngine
from schemas.engine.config_loader import config_loader
from schemas.engine.stage_orchestrator import (
    execute_stage1_translation,
    execute_stage1_safety,
    execute_stage1_gpt_oss_unified,
    execute_stage3_safety,
    build_safety_message
)

# Execution History Tracking (OLD - DEPRECATED in Session 29)
# from execution_history import ExecutionTracker

# No-op tracker to gracefully deprecate OLD ExecutionTracker
class NoOpTracker:
    """
    Session 29: No-op tracker that does nothing.
    Replaces OLD ExecutionTracker during migration to LivePipelineRecorder.
    """
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        # Return a no-op function for any method call
        def noop(*args, **kwargs):
            pass
        return noop

# Live Pipeline Recorder - Single source of truth (Session 37 Migration Complete)
from my_app.services.pipeline_recorder import get_recorder

logger = logging.getLogger(__name__)

# Blueprint erstellen
schema_bp = Blueprint('schema', __name__, url_prefix='/api/schema')

# Backward compatibility blueprint (no prefix) for legacy frontend endpoints
# TODO: Remove after frontend migration complete
schema_compat_bp = Blueprint('schema_compat', __name__)

# Global Pipeline-Executor (wird bei App-Start initialisiert)
pipeline_executor = None

# Cache for output_config_defaults.json
_output_config_defaults = None

def init_schema_engine():
    """Schema-Engine initialisieren"""
    global pipeline_executor
    if pipeline_executor is None:
        schemas_path = Path(__file__).parent.parent.parent / "schemas"
        pipeline_executor = PipelineExecutor(schemas_path)

        # Config Loader initialisieren (ohne Legacy-Services vorerst)
        pipeline_executor.config_loader.initialize(schemas_path)

        logger.info("Schema engine initialized")

def load_output_config_defaults():
    """Load output_config_defaults.json"""
    global _output_config_defaults

    if _output_config_defaults is None:
        try:
            defaults_path = Path(__file__).parent.parent.parent / "schemas" / "output_config_defaults.json"
            with open(defaults_path, 'r', encoding='utf-8') as f:
                _output_config_defaults = json.load(f)
            logger.info("output_config_defaults.json loaded")
        except Exception as e:
            logger.error(f"Failed to load output_config_defaults.json: {e}")
            _output_config_defaults = {}

    return _output_config_defaults

def lookup_output_config(media_type: str, execution_mode: str = 'eco') -> str:
    """
    Lookup Output-Config name from output_config_defaults.json

    Args:
        media_type: image, audio, video, music, text
        execution_mode: eco (local) or fast (cloud)

    Returns:
        Config name (e.g., "sd35_large") or None if not found
    """
    defaults = load_output_config_defaults()

    if media_type not in defaults:
        logger.warning(f"Unknown media type: {media_type}")
        return None

    config_name = defaults[media_type].get(execution_mode)

    # Filter out metadata keys that start with underscore
    if config_name and not config_name.startswith('_'):
        logger.info(f"Output-Config lookup: {media_type}/{execution_mode} → {config_name}")
        return config_name
    else:
        logger.info(f"No Output-Config for {media_type}/{execution_mode} (config_name={config_name})")
        return None


# ============================================================================
# SHARED STAGE 2 EXECUTION FUNCTION
# ============================================================================

async def execute_stage2_with_optimization_SINGLE_RUN_VERSION(
    schema_name: str,
    input_text: str,
    config,
    execution_mode: str,
    safety_level: str,
    output_config: str = None,
    media_preferences = None,
    tracker = None,
    user_input: str = None
):
    """
    BACKUP VERSION: Execute Stage 2 with SINGLE LLM call (interception + optimization combined)

    This is the OLD implementation that combines pedagogical interception and model-specific
    optimization in ONE LLM call. Kept as backup for potential future use.

    REPLACED BY: execute_stage2_with_optimization() which does 2 separate LLM calls.

    Args:
        schema_name: Name of the interception config (e.g., "dada", "bauhaus")
        input_text: User input text (already safety-checked in Stage 1)
        config: Loaded interception config object
        execution_mode: "eco" or "fast"
        safety_level: "kids", "youth", or "off"
        output_config: Optional output config name for optimization (e.g., "sd35_large")
        media_preferences: Optional media preferences from config
        tracker: Optional execution tracker
        user_input: Optional original user input text (before safety check)

    Returns:
        PipelineResult object with Stage 2 output
    """
    from dataclasses import replace

    logger.info(f"[STAGE2] Starting interception for '{schema_name}'")

    # ====================================================================
    # STAGE 2 OPTIMIZATION: Fetch media-specific optimization instruction
    # ====================================================================
    optimization_instruction = None

    # Determine which output config will be used
    if output_config:
        # User-selected or explicitly provided
        target_output_config = output_config
    elif media_preferences and media_preferences.get('output_configs'):
        # Use first output config from array
        target_output_config = media_preferences['output_configs'][0]
    elif media_preferences and media_preferences.get('default_output') and media_preferences.get('default_output') != 'text':
        # Lookup output config from default_output
        target_output_config = lookup_output_config(media_preferences['default_output'], execution_mode)
    else:
        target_output_config = None

    if target_output_config:
        logger.info(f"[STAGE2-OPT] Target output config: {target_output_config}")
        try:
            # Load output config to get OUTPUT_CHUNK name
            output_config_obj = pipeline_executor.config_loader.get_config(target_output_config)
            if output_config_obj and hasattr(output_config_obj, 'parameters'):
                output_chunk_name = output_config_obj.parameters.get('OUTPUT_CHUNK')
                if output_chunk_name:
                    logger.info(f"[STAGE2-OPT] Output chunk: {output_chunk_name}")
                    # Load output chunk JSON directly to get optimization_instruction
                    import json
                    from pathlib import Path
                    chunk_file = Path(__file__).parent.parent.parent / "schemas" / "chunks" / f"{output_chunk_name}.json"
                    if chunk_file.exists():
                        with open(chunk_file, 'r', encoding='utf-8') as f:
                            output_chunk = json.load(f)
                        if output_chunk and 'meta' in output_chunk:
                            optimization_instruction = output_chunk['meta'].get('optimization_instruction')
                            if optimization_instruction:
                                logger.info(f"[STAGE2-OPT] Found optimization instruction (length: {len(optimization_instruction)})")
                            else:
                                logger.info(f"[STAGE2-OPT] No optimization instruction in chunk {output_chunk_name}")
                    else:
                        logger.warning(f"[STAGE2-OPT] Chunk file not found: {chunk_file}")
        except Exception as e:
            logger.warning(f"[STAGE2-OPT] Failed to load optimization instruction: {e}")

    # ====================================================================
    # Append optimization instruction to context if found
    # ====================================================================
    stage2_config = config
    if optimization_instruction:
        logger.info(f"[STAGE2-OPT] Appending optimization instruction to pipeline context")

        # Get original context
        original_context = config.context if hasattr(config, 'context') and config.context else ""
        new_context = original_context + "\n\n" + optimization_instruction

        # Create modified config using dataclasses.replace()
        stage2_config = replace(
            config,
            context=new_context,
            meta={**config.meta, 'optimization_added': True}
        )
        logger.info(f"[STAGE2-OPT] Context extended with optimization instruction")

    # ====================================================================
    # Execute Stage 2 Pipeline
    # ====================================================================
    if tracker is None:
        # Use locally-defined NoOpTracker class (defined at top of file)
        tracker = NoOpTracker()

    result = await pipeline_executor.execute_pipeline(
        config_name=schema_name,
        input_text=input_text,
        user_input=user_input if user_input is not None else input_text,
        execution_mode=execution_mode,
        safety_level=safety_level,
        tracker=tracker,
        config_override=stage2_config
    )

    logger.info(f"[STAGE2] Interception completed: {result.success}")
    return result


async def execute_stage2_with_optimization(
    schema_name: str,
    input_text: str,
    config,
    execution_mode: str,
    safety_level: str,
    output_config: str = None,
    media_preferences = None,
    tracker = None,
    user_input: str = None
):
    """
    Execute Stage 2: Interception + Media-Specific Optimization (2 LLM Calls)

    NEW IMPLEMENTATION: Splits Stage 2 into TWO sequential LLM calls:
    1. INTERCEPTION: Pedagogical transformation (using config.context only)
    2. OPTIMIZATION: Model-specific optimization (using optimization_instruction only)

    This separation improves quality by giving each task focused attention.

    Args:
        schema_name: Name of the interception config (e.g., "dada", "bauhaus")
        input_text: User input text (already safety-checked in Stage 1)
        config: Loaded interception config object
        execution_mode: "eco" or "fast"
        safety_level: "kids", "youth", or "off"
        output_config: Optional output config name for optimization (e.g., "sd35_large")
        media_preferences: Optional media preferences from config
        tracker: Optional execution tracker
        user_input: Optional original user input text (before safety check)

    Returns:
        Dict with both interception_result and optimized_prompt (if optimization was run)
    """
    from dataclasses import replace

    logger.info(f"[STAGE2] Starting 2-phase interception for '{schema_name}'")

    # ====================================================================
    # LLM CALL 1: PEDAGOGICAL INTERCEPTION
    # ====================================================================
    logger.info(f"[STAGE2-CALL1] Executing pedagogical interception")

    if tracker is None:
        tracker = NoOpTracker()

    # Execute pipeline with ONLY pedagogical context (NO optimization instruction)
    result1 = await pipeline_executor.execute_pipeline(
        config_name=schema_name,
        input_text=input_text,
        user_input=user_input if user_input is not None else input_text,
        execution_mode=execution_mode,
        safety_level=safety_level,
        tracker=tracker,
        config_override=config  # Use original config (no modification)
    )

    if not result1.success:
        logger.error(f"[STAGE2-CALL1] Interception failed: {result1.error}")
        return result1  # Return error from Call 1

    interception_result = result1.final_output
    logger.info(f"[STAGE2-CALL1] Interception completed: '{interception_result[:100]}...'")

    # ====================================================================
    # LLM CALL 2: MODEL-SPECIFIC OPTIMIZATION (optional)
    # ====================================================================
    optimization_instruction = None
    optimized_prompt = None

    # Determine which output config will be used
    if output_config:
        target_output_config = output_config
    elif media_preferences and media_preferences.get('output_configs'):
        target_output_config = media_preferences['output_configs'][0]
    elif media_preferences and media_preferences.get('default_output') and media_preferences.get('default_output') != 'text':
        target_output_config = lookup_output_config(media_preferences['default_output'], execution_mode)
    else:
        target_output_config = None

    if target_output_config:
        logger.info(f"[STAGE2-CALL2] Target output config: {target_output_config}")
        try:
            # Load output config to get OUTPUT_CHUNK name
            output_config_obj = pipeline_executor.config_loader.get_config(target_output_config)
            if output_config_obj and hasattr(output_config_obj, 'parameters'):
                output_chunk_name = output_config_obj.parameters.get('OUTPUT_CHUNK')
                if output_chunk_name:
                    logger.info(f"[STAGE2-CALL2] Output chunk: {output_chunk_name}")
                    # Load output chunk JSON to get optimization_instruction
                    import json
                    from pathlib import Path
                    chunk_file = Path(__file__).parent.parent.parent / "schemas" / "chunks" / f"{output_chunk_name}.json"
                    if chunk_file.exists():
                        with open(chunk_file, 'r', encoding='utf-8') as f:
                            output_chunk = json.load(f)
                        if output_chunk and 'meta' in output_chunk:
                            optimization_instruction = output_chunk['meta'].get('optimization_instruction')
                            if optimization_instruction:
                                logger.info(f"[STAGE2-CALL2] Found optimization instruction (length: {len(optimization_instruction)})")
                            else:
                                logger.info(f"[STAGE2-CALL2] No optimization instruction in chunk {output_chunk_name}")
                    else:
                        logger.warning(f"[STAGE2-CALL2] Chunk file not found: {chunk_file}")
        except Exception as e:
            logger.warning(f"[STAGE2-CALL2] Failed to load optimization instruction: {e}")

    # Execute optimization call if we found an optimization_instruction
    result2 = None  # Initialize result2 to avoid NameError
    if optimization_instruction:
        logger.info(f"[STAGE2-CALL2] Executing model-specific optimization")

        # Create modified config with ONLY optimization_instruction as context
        optimization_config = replace(
            config,
            context=optimization_instruction,
            meta={**config.meta, 'optimization_only': True}
        )

        # Execute pipeline with interception_result as INPUT and optimization_instruction as CONTEXT
        result2 = await pipeline_executor.execute_pipeline(
            config_name=schema_name,
            input_text=interception_result,  # Use Call 1 output as input
            user_input=interception_result,
            execution_mode=execution_mode,
            safety_level=safety_level,
            tracker=tracker,
            config_override=optimization_config
        )

        if result2.success:
            optimized_prompt = result2.final_output
            logger.info(f"[STAGE2-CALL2] Optimization completed: '{optimized_prompt[:100]}...'")
        else:
            logger.warning(f"[STAGE2-CALL2] Optimization failed: {result2.error}, using interception result")
            optimized_prompt = interception_result  # Fallback to Call 1 output
    else:
        logger.info(f"[STAGE2-CALL2] SKIPPED (no optimization instruction found)")
        optimized_prompt = interception_result  # Use Call 1 output directly

    # ====================================================================
    # Return combined result
    # ====================================================================
    # Create a combined result object with both outputs
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class Stage2Result:
        success: bool
        interception_result: str
        optimized_prompt: str
        final_output: str  # For backward compatibility, use optimized_prompt
        error: Optional[str] = None
        steps: list = None
        metadata: dict = None
        execution_time: float = 0.0

        def __post_init__(self):
            if self.steps is None:
                self.steps = []
            if self.metadata is None:
                self.metadata = {}

    combined_result = Stage2Result(
        success=True,
        interception_result=interception_result,
        optimized_prompt=optimized_prompt,
        final_output=optimized_prompt,  # Use optimized_prompt for backward compatibility
        steps=result1.steps + (result2.steps if result2 and result2.success else []),
        metadata={
            'interception_model': result1.metadata.get('model_used') if result1.metadata else None,
            'optimization_model': result2.metadata.get('model_used') if result2 and result2.success and result2.metadata else None,
            'two_phase_execution': True,
            'optimization_applied': optimization_instruction is not None
        },
        execution_time=result1.execution_time + (result2.execution_time if result2 and result2.success else 0)
    )

    logger.info(f"[STAGE2] 2-phase execution completed successfully")
    return combined_result


@schema_bp.route('/info', methods=['GET'])
def get_schema_info():
    """Schema-System Informationen"""
    try:
        init_schema_engine()

        available_schemas = pipeline_executor.get_available_schemas()

        return jsonify({
            'status': 'success',
            'schemas_available': len(available_schemas),
            'schemas': available_schemas,
            'engine_status': 'initialized'
        })

    except Exception as e:
        logger.error(f"Schema-Info Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# ============================================================================
# NEW REFACTORED ENDPOINTS - CLEAN STAGE SEPARATION
# ============================================================================

@schema_bp.route('/pipeline/stage2', methods=['POST'])
def execute_stage2():
    """
    Execute ONLY Stage 2: Interception + Optimization

    This endpoint executes Stage 2 (prompt interception with media-specific optimization)
    and returns the result for frontend preview/editing.

    Frontend can then call /pipeline/stage3-4 with the (possibly edited) Stage 2 result.

    Request Body:
    {
        "schema": "dada",                      # Interception config
        "input_text": "Ein roter Apfel",       # User input
        "output_config": "sd35_large",         # Output config for optimization
        "execution_mode": "eco",               # eco or fast
        "safety_level": "kids",                # kids, youth, or off
        "user_language": "de"                  # User's interface language
    }

    Response:
    {
        "success": true,
        "stage2_result": "Ein roter Apfel in fragmentierter dadaistischer Form...",
        "run_id": "uuid",                      # Session ID for Stage 3-4
        "model_used": "llama3:8b",
        "backend_used": "ollama",
        "execution_time_ms": 1234
    }
    """
    import time
    import uuid

    start_time = time.time()

    try:
        # Request validation
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON-Request erwartet'
            }), 400

        schema_name = data.get('schema')
        input_text = data.get('input_text')
        execution_mode = data.get('execution_mode', 'eco')
        safety_level = data.get('safety_level', 'kids')
        output_config = data.get('output_config')  # Optional
        user_language = data.get('user_language', 'en')

        # Context editing support (same as /execute)
        context_prompt = data.get('context_prompt')  # Optional: user-edited meta-prompt
        context_language = data.get('context_language', 'en')  # Language of context_prompt

        if not schema_name or not input_text:
            return jsonify({
                'success': False,
                'error': 'schema und input_text sind erforderlich'
            }), 400

        # Initialize engine
        init_schema_engine()

        # Load config
        config = pipeline_executor.config_loader.get_config(schema_name)
        if not config:
            return jsonify({
                'success': False,
                'error': f'Config "{schema_name}" nicht gefunden'
            }), 404

        logger.info(f"[STAGE2-ENDPOINT] Starting Stage 2 for schema '{schema_name}'")

        # ====================================================================
        # CONTEXT EDITING SUPPORT (same pattern as /execute)
        # ====================================================================
        execution_config = config
        if context_prompt:
            logger.info(f"[STAGE2-ENDPOINT] User edited context in language: {context_language}")

            # Translate to English if needed
            context_prompt_en = context_prompt
            if context_language != 'en':
                logger.info(f"[STAGE2-ENDPOINT] Translating context from {context_language} to English")

                from my_app.services.ollama_service import ollama_service
                translation_prompt = f"Translate this educational text from {context_language} to English. Preserve pedagogical intent and technical terminology:\n\n{context_prompt}"

                try:
                    context_prompt_en = ollama_service.translate_text(translation_prompt)
                    if not context_prompt_en:
                        logger.error("[STAGE2-ENDPOINT] Context translation failed, using original")
                        context_prompt_en = context_prompt
                    else:
                        logger.info(f"[STAGE2-ENDPOINT] Context translated successfully")
                except Exception as e:
                    logger.error(f"[STAGE2-ENDPOINT] Context translation error: {e}")
                    context_prompt_en = context_prompt

            # Create modified config with user-edited context
            logger.info(f"[STAGE2-ENDPOINT] Creating modified config with user-edited context")

            from dataclasses import replace
            execution_config = replace(
                config,
                context=context_prompt_en,  # Use English version for pipeline
                meta={
                    **config.meta,
                    'user_edited': True,
                    'original_config': schema_name,
                    'user_language': user_language
                }
            )

        # ====================================================================
        # STAGE 1: PRE-INTERCEPTION (Safety Check)
        # ====================================================================
        logger.info(f"[STAGE2-ENDPOINT] Stage 1: Safety Check")

        stage1_start = time.time()
        is_safe, checked_text, error_message = asyncio.run(execute_stage1_gpt_oss_unified(
            input_text,
            safety_level,
            execution_mode,
            pipeline_executor
        ))
        stage1_time = (time.time() - stage1_start) * 1000  # ms

        if not is_safe:
            logger.warning(f"[STAGE2-ENDPOINT] Stage 1 BLOCKED by safety check")
            return jsonify({
                'success': False,
                'error': error_message,
                'blocked_at_stage': 1,
                'safety_level': safety_level
            }), 403

        logger.info(f"[STAGE2-ENDPOINT] Stage 1 completed: Safety passed")

        # ====================================================================
        # STAGE 2: INTERCEPTION + OPTIMIZATION (Shared Function)
        # ====================================================================
        stage2_start = time.time()

        media_preferences = execution_config.media_preferences if hasattr(execution_config, 'media_preferences') else None

        result = asyncio.run(execute_stage2_with_optimization(
            schema_name=schema_name,
            input_text=checked_text,
            config=execution_config,  # Use execution_config (may be modified with user context)
            execution_mode=execution_mode,
            safety_level=safety_level,
            output_config=output_config,
            media_preferences=media_preferences,
            tracker=None
        ))

        stage2_time = (time.time() - stage2_start) * 1000  # ms

        if not result.success:
            logger.error(f"[STAGE2-ENDPOINT] Stage 2 failed: {result.error}")
            return jsonify({
                'success': False,
                'error': result.error,
                'execution_time_ms': stage2_time
            }), 500

        # Extract metadata
        model_used = None
        backend_used = None
        if result.steps and len(result.steps) > 0:
            for step in reversed(result.steps):
                if step.metadata:
                    model_used = step.metadata.get('model_used', model_used)
                    backend_used = step.metadata.get('backend_type', backend_used)
                    if model_used and backend_used:
                        break

        # Generate session ID for Stage 3-4 continuation
        run_id = str(uuid.uuid4())

        total_time = (time.time() - start_time) * 1000

        logger.info(f"[STAGE2-ENDPOINT] ✅ Success! Stage 2 result: '{result.final_output[:100]}...'")

        # Build response - include both prompts if 2-phase execution
        response_data = {
            'success': True,
            'stage2_result': result.final_output,
            'run_id': run_id,
            'model_used': model_used,
            'backend_used': backend_used,
            'execution_time_ms': total_time,
            'stage1_time_ms': stage1_time,
            'stage2_time_ms': stage2_time
        }

        # Add both prompts if using new 2-phase implementation
        if hasattr(result, 'interception_result') and hasattr(result, 'optimized_prompt'):
            response_data['interception_result'] = result.interception_result
            response_data['optimized_prompt'] = result.optimized_prompt
            response_data['two_phase_execution'] = True
            response_data['optimization_applied'] = result.metadata.get('optimization_applied', False) if result.metadata else False
            logger.info(f"[STAGE2-ENDPOINT] 2-phase execution: interception + optimization")

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"[STAGE2-ENDPOINT] Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@schema_bp.route('/pipeline/stage3-4', methods=['POST'])
def execute_stage3_4():
    """
    Execute Stage 3-4: Translation + Safety + Media Generation

    Takes the Stage 2 result (possibly edited by user) and continues with
    translation, safety check, and media generation.

    Request Body:
    {
        "stage2_result": "Ein roter Apfel in dadaistischer...",  # From /stage2 (can be edited)
        "output_config": "sd35_large",                           # Output config for media generation
        "execution_mode": "eco",                                 # eco or fast
        "safety_level": "kids",                                  # kids, youth, or off
        "run_id": "uuid",                                        # Optional: Session ID from /stage2
        "seed": 123456                                           # Optional: Seed for reproducible generation
    }

    Response:
    {
        "success": true,
        "media_output": {
            "url": "/media/run_xyz/image.png",
            "media_type": "image",
            "seed": 123456,
            ...
        },
        "stage3_result": "A red apple in fragmented dadaist form...",  # Translated text
        "execution_time_ms": 5678
    }
    """
    import time
    import uuid

    start_time = time.time()

    try:
        # Request validation
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON-Request erwartet'
            }), 400

        stage2_result = data.get('stage2_result')
        output_config = data.get('output_config')
        execution_mode = data.get('execution_mode', 'eco')
        safety_level = data.get('safety_level', 'kids')
        run_id = data.get('run_id', str(uuid.uuid4()))
        seed_override = data.get('seed')

        if not stage2_result or not output_config:
            return jsonify({
                'success': False,
                'error': 'stage2_result und output_config sind erforderlich'
            }), 400

        # Initialize engine
        init_schema_engine()

        logger.info(f"[STAGE3-4-ENDPOINT] Starting Stage 3-4 for output config '{output_config}'")
        logger.info(f"[STAGE3-4-ENDPOINT] Stage 2 result (first 100 chars): {stage2_result[:100]}...")

        # ====================================================================
        # STAGE 3: TRANSLATION + PRE-OUTPUT SAFETY
        # ====================================================================
        logger.info(f"[STAGE3-4-ENDPOINT] Stage 3: Translation + Pre-Output Safety")

        stage3_start = time.time()

        # Determine media type from output config
        if 'image' in output_config.lower() or 'sd' in output_config.lower() or 'flux' in output_config.lower() or 'gpt' in output_config.lower():
            media_type = 'image'
        elif 'audio' in output_config.lower():
            media_type = 'audio'
        elif 'music' in output_config.lower() or 'ace' in output_config.lower():
            media_type = 'music'
        elif 'video' in output_config.lower():
            media_type = 'video'
        else:
            media_type = 'image'  # Default fallback

        # Execute Stage 3 safety check
        safety_result = asyncio.run(execute_stage3_safety(
            stage2_result,
            safety_level,
            execution_mode,
            pipeline_executor,
            media_type=media_type
        ))

        stage3_time = (time.time() - stage3_start) * 1000  # ms

        if not safety_result['safe']:
            logger.warning(f"[STAGE3-4-ENDPOINT] Stage 3 BLOCKED by safety check")
            return jsonify({
                'success': False,
                'error': safety_result.get('reason', 'Content blocked by safety check'),
                'blocked_at_stage': 3,
                'safety_level': safety_level,
                'stage3_time_ms': stage3_time
            }), 403

        translated_prompt = safety_result.get('positive_prompt', stage2_result)
        logger.info(f"[STAGE3-4-ENDPOINT] Stage 3 completed: Translated to '{translated_prompt[:100]}...'")

        # ====================================================================
        # STAGE 4: MEDIA GENERATION
        # ====================================================================
        logger.info(f"[STAGE3-4-ENDPOINT] Stage 4: Executing output config '{output_config}'")

        stage4_start = time.time()

        try:
            # Execute Output Pipeline with translated text
            # Use locally-defined NoOpTracker class (defined at top of file)
            tracker = NoOpTracker()

            output_result = asyncio.run(pipeline_executor.execute_pipeline(
                config_name=output_config,
                input_text=translated_prompt,
                user_input=translated_prompt,
                execution_mode=execution_mode,
                tracker=tracker
            ))

            stage4_time = (time.time() - stage4_start) * 1000  # ms

            if not output_result.success:
                logger.error(f"[STAGE3-4-ENDPOINT] Stage 4 failed: {output_result.error}")
                return jsonify({
                    'success': False,
                    'error': output_result.error,
                    'stage': 'stage4',
                    'stage3_time_ms': stage3_time,
                    'stage4_time_ms': stage4_time
                }), 500

            # ====================================================================
            # MEDIA STORAGE - Download and store media locally
            # ====================================================================
            media_stored = False
            media_output_data = None

            try:
                output_value = output_result.final_output
                saved_filename = None

                # Extract seed from output_result metadata (if available)
                seed = output_result.metadata.get('seed') if output_result.metadata else None
                if seed_override:
                    seed = seed_override

                # Import media manager
                from my_app.services.media_manager import media_manager

                # Detect generation backend and download appropriately
                if output_value == 'swarmui_generated':
                    # SwarmUI generation - image paths returned directly
                    image_paths = output_result.metadata.get('image_paths', [])
                    logger.info(f"[STAGE3-4-ENDPOINT] Downloading from SwarmUI: {len(image_paths)} image(s)")

                    if image_paths:
                        saved_filename = media_manager.save_swarmui_media(
                            image_paths=image_paths,
                            run_id=run_id,
                            media_type=media_type
                        )
                        media_stored = True

                elif output_value and output_value.startswith('http'):
                    # URL-based media (ComfyUI, OpenRouter, etc.)
                    logger.info(f"[STAGE3-4-ENDPOINT] Downloading from URL: {output_value[:100]}...")

                    saved_filename = media_manager.save_media_from_url(
                        url=output_value,
                        run_id=run_id,
                        media_type=media_type
                    )
                    media_stored = True

                if media_stored and saved_filename:
                    media_output_data = {
                        'url': f'/api/media/{run_id}/{saved_filename}',
                        'filename': saved_filename,
                        'run_id': run_id,
                        'media_type': media_type,
                        'config': output_config,
                        'seed': seed,
                        'media_stored': True
                    }
                    logger.info(f"[STAGE3-4-ENDPOINT] ✅ Media stored: {saved_filename}")

            except Exception as e:
                logger.error(f"[STAGE3-4-ENDPOINT] Media storage failed: {e}")
                import traceback
                traceback.print_exc()

            total_time = (time.time() - start_time) * 1000

            logger.info(f"[STAGE3-4-ENDPOINT] ✅ Success! Total time: {total_time:.0f}ms")

            return jsonify({
                'success': True,
                'media_output': media_output_data,
                'stage3_result': translated_prompt,
                'run_id': run_id,
                'execution_time_ms': total_time,
                'stage3_time_ms': stage3_time,
                'stage4_time_ms': stage4_time
            })

        except Exception as e:
            logger.error(f"[STAGE3-4-ENDPOINT] Stage 4 error: {e}")
            import traceback
            traceback.print_exc()

            return jsonify({
                'success': False,
                'error': str(e),
                'stage': 'stage4'
            }), 500

    except Exception as e:
        logger.error(f"[STAGE3-4-ENDPOINT] Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@schema_bp.route('/pipeline/execute', methods=['POST'])
def execute_pipeline():
    """Schema-Pipeline ausführen mit 4-Stage Orchestration"""
    try:
        # Request-Validation
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'JSON-Request erwartet'
            }), 400

        schema_name = data.get('schema')
        input_text = data.get('input_text')
        execution_mode = data.get('execution_mode', 'eco')  # eco (local) or fast (cloud)
        safety_level = data.get('safety_level', 'kids')  # kids (default), youth, or off

        # Phase 2: Multilingual context editing support
        context_prompt = data.get('context_prompt')  # Optional: user-edited meta-prompt
        context_language = data.get('context_language', 'en')  # Language of context_prompt
        user_language = data.get('user_language', 'en')  # User's interface language

        # Media generation support
        output_config = data.get('output_config')  # Optional: specific output config for Stage 4 (e.g., 'sd35_large')

        # Stage 2 result support: use frontend-provided interception result
        interception_result = data.get('interception_result')  # Optional: frontend-provided Stage 2 output (if already executed)

        # Fast regeneration support: skip Stage 1-3 with stage4_only flag
        stage4_only = data.get('stage4_only', False)  # Boolean: skip to Stage 4 (media generation) only
        seed_override = data.get('seed')  # Optional: specific seed for exact regeneration

        if not schema_name or not input_text:
            return jsonify({
                'status': 'error',
                'error': 'Parameter "schema" and "input_text" erforderlich'
            }), 400

        # Schema-Engine initialisieren
        init_schema_engine()

        # Get config
        config = pipeline_executor.config_loader.get_config(schema_name)
        if not config:
            return jsonify({
                'status': 'error',
                'error': f'Config "{schema_name}" nicht gefunden'
            }), 404

        # Check if this is an output config (skip Stage 1-3 for output configs)
        is_output_config = config.meta.get('stage') == 'output'
        is_system_pipeline = config.meta.get('system_pipeline', False)

        # ====================================================================
        # SESSION 29: GENERATE UNIFIED RUN ID
        # ====================================================================
        # FIX: Generate ONE run_id used by ALL systems (not separate IDs)
        run_id = str(uuid.uuid4())
        logger.info(f"[RUN_ID] Generated unified run_id: {run_id} for {schema_name}")

        # ====================================================================
        # EXECUTION HISTORY TRACKER - DEPRECATED (Session 29)
        # ====================================================================
        # Session 29: Replaced ExecutionTracker with NoOpTracker
        # LivePipelineRecorder now handles all tracking responsibilities
        # Use locally-defined NoOpTracker class (defined at top of file)
        tracker = NoOpTracker()

        # Log pipeline start
        tracker.log_pipeline_start(
            input_text=input_text,
            metadata={'request_timestamp': data.get('timestamp')}
        )

        # ====================================================================
        # LIVE PIPELINE RECORDER - Single source of truth (Session 37 Migration)
        # ====================================================================
        from config import JSON_STORAGE_DIR
        recorder = get_recorder(
            run_id=run_id,
            config_name=schema_name,
            execution_mode=execution_mode,
            safety_level=safety_level,
            user_id='anonymous',
            base_path=JSON_STORAGE_DIR
        )
        recorder.set_state(0, "pipeline_starting")
        logger.info(f"[RECORDER] Initialized LivePipelineRecorder for run {run_id}")

        # ====================================================================
        # PHASE 2: USER-EDITED CONTEXT HANDLING
        # ====================================================================
        # If user edited the meta-prompt (context) in Phase 2, handle translation
        # and save both language versions to exports
        modified_config = None

        if context_prompt:
            logger.info(f"[PHASE2] User edited context in language: {context_language}")

            # Save original language version
            recorder.save_entity(f'context_prompt_{context_language}', context_prompt)

            # Translate to English if needed
            context_prompt_en = context_prompt
            if context_language != 'en':
                logger.info(f"[PHASE2] Translating context from {context_language} to English...")

                # Use Ollama service for translation
                from my_app.services.ollama_service import ollama_service

                translation_prompt = f"Translate this educational text from {context_language} to English. Preserve pedagogical intent and technical terminology:\n\n{context_prompt}"

                try:
                    context_prompt_en = ollama_service.translate_text(translation_prompt)
                    if not context_prompt_en:
                        logger.error("[PHASE2] Context translation failed, using original")
                        context_prompt_en = context_prompt
                    else:
                        logger.info(f"[PHASE2] Context translated successfully")
                        # Save English version
                        recorder.save_entity('context_prompt_en', context_prompt_en)
                except Exception as e:
                    logger.error(f"[PHASE2] Context translation error: {e}")
                    context_prompt_en = context_prompt

            # Create modified config with user-edited context
            logger.info(f"[PHASE2] Creating modified config with user-edited context")

            from dataclasses import replace
            modified_config = replace(
                config,
                context=context_prompt_en,  # Use English version for pipeline
                meta={
                    **config.meta,
                    'user_edited': True,
                    'original_config': schema_name,
                    'user_language': user_language
                }
            )

            # Save modified config as first entity
            recorder.save_entity('config_used', modified_config.to_dict())
            logger.info(f"[RECORDER] Saved user-modified config")
        else:
            # Save original config (unmodified)
            recorder.save_entity('config_used', config.to_dict())
            logger.info(f"[RECORDER] Saved original config")

        # Use modified config for execution if available
        execution_config = modified_config if modified_config else config

        # ====================================================================
        # FAST REGENERATION: Skip Stage 1-3 if stage4_only=True
        # ====================================================================
        if stage4_only:
            logger.info(f"[FAST-REGEN] stage4_only=True: Skipping Stage 1-3, direct to Stage 4")
            # Create a mock result object for Stage 2 output
            class MockResult:
                def __init__(self, output):
                    self.success = True
                    self.final_output = output
                    self.error = None
                    self.steps = []
                    self.metadata = {}
                    self.execution_time = 0
            result = MockResult(input_text)  # input_text is already transformed text
            current_input = input_text
        else:
            # ====================================================================
            # STAGE 1: PRE-INTERCEPTION (Translation + Safety)
            # ====================================================================
            current_input = input_text

            if not is_system_pipeline and not is_output_config:
                logger.info(f"[4-STAGE] Stage 1: Pre-Interception for '{schema_name}'")
                tracker.set_stage(1)
                recorder.set_state(1, "translation_and_safety")

                # Log user input
                tracker.log_user_input_text(input_text)

                # SESSION 29: Save input entity
                recorder.save_entity('input', input_text)
                logger.info(f"[RECORDER] Saved input entity")

                # Stage 1: GPT-OSS Safety Check (No Translation)
                is_safe, checked_text, error_message = asyncio.run(execute_stage1_gpt_oss_unified(
                    input_text,
                    safety_level,
                    execution_mode,
                    pipeline_executor
                ))
                current_input = checked_text

                if not is_safe:
                    logger.warning(f"[4-STAGE] Stage 1 BLOCKED by GPT-OSS §86a")

                    # SESSION 29: Save checked text (even if blocked)
                    recorder.save_entity('stage1_output', checked_text)

                    # SESSION 29: Save safety error
                    recorder.save_error(
                        stage=1,
                        error_type='safety_blocked',
                        message=error_message,
                        details={'codes': ['§86a']}
                    )
                    logger.info(f"[RECORDER] Saved stage 1 blocked error")

                    # Log blocked event
                    tracker.log_stage1_blocked(
                        blocked_reason='§86a_violation',
                        blocked_codes=['§86a'],
                        error_message=error_message
                    )
                    tracker.finalize()  # Persist even though blocked

                    return jsonify({
                        'status': 'error',
                        'schema': schema_name,
                        'error': error_message,
                        'metadata': {
                            'stage': 'pre_interception',
                            'safety_codes': ['§86a']  # Blocked by GPT-OSS §86a StGB check
                        }
                    }), 403

                # SESSION 29: Save stage1 output and safety results
                recorder.save_entity('stage1_output', checked_text)
                recorder.save_entity('safety', {
                    'safe': True,
                    'method': 'gpt_oss_safety',
                    'codes_checked': ['§86a'],
                    'safety_level': safety_level
                })
                logger.info(f"[RECORDER] Saved stage1 output and safety entities")

                # Note: Stage 1 now only does safety check, no translation
                # Translation will be moved to Stage 3 (before media generation)

            # ====================================================================
            # STAGE 2: INTERCEPTION (Main Pipeline + Optimization)
            # ====================================================================
            tracker.set_stage(2)
            recorder.set_state(2, "interception")

            # Check if frontend already executed Stage 2 and provides result
            if interception_result:
                logger.info(f"[4-STAGE] Stage 2: Using frontend-provided interception_result (already executed)")

                # Create mock result object to maintain interface compatibility
                class MockResult:
                    def __init__(self, output):
                        self.success = True
                        self.final_output = output
                        self.error = None
                        self.steps = []
                        self.metadata = {'frontend_provided': True}
                        self.execution_time = 0

                result = MockResult(interception_result)
            else:
                logger.info(f"[4-STAGE] Stage 2: Executing interception pipeline for '{schema_name}'")

                # Use shared Stage 2 function (eliminates code duplication)
                media_preferences = config.media_preferences if hasattr(config, 'media_preferences') else None
                result = asyncio.run(execute_stage2_with_optimization(
                    schema_name=schema_name,
                    input_text=current_input,
                    config=execution_config,
                    execution_mode=execution_mode,
                    safety_level=safety_level,
                    output_config=output_config,
                    media_preferences=media_preferences,
                    tracker=tracker,
                    user_input=data.get('user_input', input_text)
                ))

            # Check if pipeline succeeded
            if not result.success:
                tracker.log_pipeline_error(
                    error_type='PipelineExecutionError',
                    error_message=result.error,
                    stage=2
                )
                tracker.finalize()

                return jsonify({
                    'status': 'error',
                    'schema': schema_name,
                    'error': result.error,
                    'steps_completed': len([s for s in result.steps if s.status.value == 'completed']),
                    'total_steps': len(result.steps)
                }), 500

            # Extract metadata from pipeline result
            model_used = None
            backend_used = None
            if result.steps and len(result.steps) > 0:
                # Get metadata from last successful step
                for step in reversed(result.steps):
                    if step.metadata:
                        model_used = step.metadata.get('model_used', model_used)
                        backend_used = step.metadata.get('backend_type', backend_used)
                        if model_used and backend_used:
                            break

            # Get actual total_iterations from result metadata (for recursive pipelines like Stille Post)
            total_iterations = result.metadata.get('iterations', 1) if result.metadata else 1

            # Log interception final result
            tracker.log_interception_final(
                final_text=result.final_output,
                total_iterations=total_iterations,
                config_used=schema_name,
                model_used=model_used,
                backend_used=backend_used,
                execution_time=result.execution_time
            )

            # SESSION 29: Save interception output
            recorder.save_entity('interception', result.final_output, metadata={
                'config': schema_name,
                'iterations': total_iterations,
                'model_used': model_used,
                'backend_used': backend_used
            })
            logger.info(f"[RECORDER] Saved interception entity")

        # ====================================================================
        # CONDITIONAL STAGE 3: Post-Interception Safety Check
        # ====================================================================
        # Only run Stage 3 if Stage 2 pipeline requires it (prompt_interception type)
        # Non-transformation pipelines (text_semantic_split, etc.) skip this

        pipeline_def = pipeline_executor.config_loader.get_pipeline(config.pipeline_name)
        requires_stage3 = pipeline_def.requires_interception_prompt if pipeline_def else True  # Default True for safety

        if requires_stage3 and safety_level != 'off' and isinstance(result.final_output, str):
            logger.info(f"[4-STAGE] Stage 3: Post-Interception Safety Check (pipeline requires it)")
            # TODO: Implement Stage 3 safety check on result.final_output here
            # For now, this is a placeholder - actual implementation in future session
        else:
            if not requires_stage3:
                pipeline_type = pipeline_def.pipeline_type if pipeline_def else 'unknown'
                logger.info(f"[4-STAGE] Stage 3: SKIPPED (pipeline_type={pipeline_type}, no transformation)")
            elif not isinstance(result.final_output, str):
                logger.info(f"[4-STAGE] Stage 3: SKIPPED (structured output, not text string)")

        # Response für erfolgreiche Pipeline
        response_data = {
            'status': 'success',
            'run_id': run_id,  # SESSION 30: Frontend needs run_id for status polling
            'schema': schema_name,
            'config_name': schema_name,  # Config name (same as schema for simple workflows)
            'input_text': input_text,
            'final_output': result.final_output,
            'steps_completed': len(result.steps),
            'execution_time': result.execution_time,
            'metadata': result.metadata
        }

        # ====================================================================
        # STAGE 3-4 LOOP: Multi-Output Support
        # ====================================================================
        media_preferences = config.media_preferences or {}
        default_output = media_preferences.get('default_output') if media_preferences else None
        output_configs = media_preferences.get('output_configs', [])

        # DEBUG: Log what we found
        logger.info(f"[DEBUG] media_preferences type: {type(media_preferences)}, value: {media_preferences}")
        logger.info(f"[DEBUG] default_output: {default_output}")
        logger.info(f"[DEBUG] output_configs: {output_configs}")
        logger.info(f"[DEBUG] output_config (from request): {output_config}")
        logger.info(f"[DEBUG] execution_mode: {execution_mode}")

        # Determine which output configs to use
        # Priority: 1) Request parameter, 2) Config output_configs array, 3) Config default_output
        if output_config:
            # HIGHEST PRIORITY: User directly selected output config from frontend
            logger.info(f"[USER-SELECTED] Using output_config from request: {output_config}")
            configs_to_execute = [output_config]
        elif output_configs:
            # Multi-Output: Use explicit output_configs array from config
            logger.info(f"[MULTI-OUTPUT] Config requests {len(output_configs)} outputs: {output_configs}")
            configs_to_execute = output_configs
        elif default_output and default_output != 'text':
            # Single-Output: Use lookup from default_output
            logger.info(f"[DEBUG] Calling lookup_output_config({default_output}, {execution_mode})")
            output_config_name = lookup_output_config(default_output, execution_mode)
            logger.info(f"[DEBUG] lookup returned: {output_config_name}")
            if output_config_name:
                configs_to_execute = [output_config_name]
            else:
                configs_to_execute = []
        else:
            # Text-only output
            logger.info(f"[DEBUG] No media output (default_output={default_output})")
            configs_to_execute = []

        logger.info(f"[DEBUG] configs_to_execute: {configs_to_execute}")

        # Execute Stage 3-4 for each output config
        media_outputs = []

        if configs_to_execute and not is_system_pipeline and not is_output_config:
            logger.info(f"[4-STAGE] Stage 3-4 Loop: Processing {len(configs_to_execute)} output configs")

            for i, output_config_name in enumerate(configs_to_execute):
                logger.info(f"[4-STAGE] Stage 3-4 Loop iteration {i+1}/{len(configs_to_execute)}: {output_config_name}")
                tracker.set_loop_iteration(i + 1)

                # ====================================================================
                # DETERMINE MEDIA TYPE (needed for both Stage 3 and Stage 4)
                # ====================================================================
                # Extract media type from output config name BEFORE Stage 3
                # This ensures media_type is ALWAYS defined, even when stage4_only=True
                if 'image' in output_config_name.lower() or 'sd' in output_config_name.lower() or 'flux' in output_config_name.lower() or 'gpt' in output_config_name.lower():
                    media_type = 'image'
                elif 'audio' in output_config_name.lower():
                    media_type = 'audio'
                elif 'music' in output_config_name.lower() or 'ace' in output_config_name.lower():
                    media_type = 'music'
                elif 'video' in output_config_name.lower():
                    media_type = 'video'
                else:
                    media_type = 'image'  # Default fallback

                # ====================================================================
                # STAGE 3: PRE-OUTPUT SAFETY (per output config)
                # ====================================================================
                stage_3_blocked = False

                # Skip Stage 3 ONLY if stage4_only=True (fast regeneration)
                # Note: Stage 3 now includes translation, so it runs even if safety_level='off'
                if not stage4_only:
                    tracker.set_stage(3)
                    recorder.set_state(3, "pre_output_safety")

                    logger.info(f"[4-STAGE] Stage 3: Pre-Output Safety for {output_config_name} (type: {media_type}, level: {safety_level})")

                    safety_result = asyncio.run(execute_stage3_safety(
                        result.final_output,
                        safety_level,
                        media_type,
                        execution_mode,
                        pipeline_executor
                    ))

                    # Log Stage 3 safety check
                    tracker.log_stage3_safety_check(
                        loop_iteration=i + 1,
                        safe=safety_result['safe'],
                        method=safety_result.get('method', 'hybrid'),
                        config_used=output_config_name,
                        model_used=safety_result.get('model_used'),
                        backend_used=safety_result.get('backend_used'),
                        execution_time=safety_result.get('execution_time')
                    )

                    if not safety_result['safe']:
                        # Stage 3 blocked for this output
                        abort_reason = safety_result.get('abort_reason', 'Content blocked by safety filter')
                        logger.warning(f"[4-STAGE] Stage 3 BLOCKED for {output_config_name}: {abort_reason}")

                        # SESSION 29: Save safety_pre_output result (blocked)
                        recorder.save_entity('safety_pre_output', {
                            'safe': False,
                            'method': safety_result.get('method', 'hybrid'),
                            'media_type': media_type,
                            'safety_level': safety_level,
                            'blocked': True,
                            'abort_reason': abort_reason
                        })

                        # SESSION 29: Save stage 3 blocked error
                        recorder.save_error(
                            stage=3,
                            error_type='safety_blocked',
                            message=abort_reason,
                            details={'media_type': media_type, 'config': output_config_name}
                        )
                        logger.info(f"[RECORDER] Saved stage 3 blocked error")

                        # Log Stage 3 blocked
                        tracker.log_stage3_blocked(
                            loop_iteration=i + 1,
                            config_used=output_config_name,
                            abort_reason=abort_reason
                        )

                        media_outputs.append({
                            'config': output_config_name,
                            'status': 'blocked',
                            'reason': abort_reason,
                            'media_type': media_type,  # Add media_type for frontend
                            'safety_level': safety_level
                        })
                        stage_3_blocked = True
                        continue  # Skip Stage 4 for this output
                    else:
                        # SESSION 29: Save safety_pre_output result (passed)
                        recorder.save_entity('safety_pre_output', {
                            'safe': True,
                            'method': safety_result.get('method', 'hybrid'),
                            'media_type': media_type,
                            'safety_level': safety_level
                        })
                        logger.info(f"[RECORDER] Saved safety_pre_output entity")

        # End of skip_preprocessing else block - Stage 1-3 complete

        # ====================================================================
        # Determine prompt for Stage 4 (use translated text if Stage 3 ran)
        # ====================================================================
                # If Stage 3 ran and translated the text, use the English positive_prompt
                # Otherwise, fallback to Stage 2 output (only if stage4_only=True)
                if not stage_3_blocked and not stage4_only:
                    # Stage 3 ran - use translated English text from positive_prompt
                    prompt_for_media = safety_result.get('positive_prompt', result.final_output)
                    logger.info(f"[4-STAGE] Using translated prompt from Stage 3 for media generation")
                    logger.info(f"[STAGE3-TRANSLATED] Prompt (first 200 chars): {prompt_for_media[:200]}...")
                else:
                    # Stage 3 skipped - use Stage 2 output directly
                    prompt_for_media = result.final_output
                    logger.info(f"[4-STAGE] Using Stage 2 output directly (Stage 3 skipped)")

        # ====================================================================
        # STAGE 4: OUTPUT (Media Generation)
        # ====================================================================
                if not stage_3_blocked:
                    logger.info(f"[4-STAGE] Stage 4: Executing output config '{output_config_name}'")
                    tracker.set_stage(4)
                    recorder.set_state(4, "media_generation")

                    try:
                        # Execute Output-Pipeline with translated/transformed text
                        output_result = asyncio.run(pipeline_executor.execute_pipeline(
                            config_name=output_config_name,
                            input_text=prompt_for_media,  # Use translated English text from Stage 3!
                            user_input=prompt_for_media,
                            execution_mode=execution_mode
                        ))

                        # Add media output to results
                        if output_result.success:
                            # ====================================================================
                            # MEDIA STORAGE - Download and store media locally
                            # ====================================================================
                            logger.info(f"[MEDIA-STORAGE-DEBUG] Starting media storage for config: {output_config_name}")
                            logger.info(f"[MEDIA-STORAGE-DEBUG] output_result.success: {output_result.success}")
                            logger.info(f"[MEDIA-STORAGE-DEBUG] output_result.final_output length: {len(output_result.final_output) if output_result.final_output else 0}")
                            logger.info(f"[MEDIA-STORAGE-DEBUG] output_result.final_output starts with: {output_result.final_output[:100] if output_result.final_output else 'EMPTY'}")
                            logger.info(f"[MEDIA-STORAGE-DEBUG] output_result.metadata keys: {list(output_result.metadata.keys())}")

                            media_stored = False
                            media_output_data = None

                            try:
                                output_value = output_result.final_output
                                saved_filename = None

                                # Extract seed from output_result metadata (if available)
                                seed = output_result.metadata.get('seed')

                                logger.info(f"[MEDIA-STORAGE-DEBUG] output_value type: {type(output_value)}, length: {len(output_value) if output_value else 0}")
                                logger.info(f"[MEDIA-STORAGE-DEBUG] Checking routing conditions...")

                                # Detect generation backend and download appropriately
                                logger.info(f"[MEDIA-STORAGE-DEBUG] Checking if output_value == 'swarmui_generated': {output_value == 'swarmui_generated'}")
                                if output_value == 'swarmui_generated':
                                    logger.info(f"[MEDIA-STORAGE-DEBUG] ✓ Matched: swarmui_generated")
                                    # SwarmUI generation - image paths returned directly
                                    logger.info(f"[RECORDER-DEBUG] output_result.metadata keys: {list(output_result.metadata.keys())}")
                                    logger.info(f"[RECORDER-DEBUG] full metadata: {output_result.metadata}")
                                    image_paths = output_result.metadata.get('image_paths', [])
                                    logger.info(f"[RECORDER] Downloading from SwarmUI: {len(image_paths)} image(s)")
                                    saved_filename = asyncio.run(recorder.download_and_save_from_swarmui(
                                        image_paths=image_paths,
                                        media_type=media_type,
                                        config=output_config_name,
                                        seed=seed
                                    ))
                                elif output_value == 'workflow_generated':
                                    logger.info(f"[MEDIA-STORAGE-DEBUG] ✓ Matched: workflow_generated")
                                    # Use recorder.save_entity for consistency
                                    filesystem_path = output_result.metadata.get('filesystem_path')
                                    if filesystem_path:
                                        try:
                                            with open(filesystem_path, 'rb') as f:
                                                file_data = f.read()

                                            saved_filename = recorder.save_entity(
                                                entity_type=f'output_{media_type}',
                                                content=file_data,
                                                metadata={
                                                    'config': output_config_name,
                                                    'backend': 'comfyui',
                                                    'seed': seed,
                                                    'filesystem_path': filesystem_path
                                                }
                                            )
                                            logger.info(f"[RECORDER] Saved {media_type} from filesystem: {saved_filename}")
                                        except Exception as e:
                                            logger.error(f"[RECORDER] Failed to save {media_type} from filesystem: {e}")
                                            saved_filename = None
                                    else:
                                        logger.warning(f"[RECORDER] No filesystem_path in metadata for workflow_generated")
                                        saved_filename = None
                                elif output_value.startswith('http://') or output_value.startswith('https://'):
                                    logger.info(f"[MEDIA-STORAGE-DEBUG] ✓ Matched: http/https URL")
                                    # API-based generation (GPT-5, Replicate, etc.) - URL
                                    logger.info(f"[RECORDER] Downloading from URL: {output_value}")
                                    saved_filename = asyncio.run(recorder.download_and_save_from_url(
                                        url=output_value,
                                        media_type=media_type,
                                        config=output_config_name,
                                        seed=seed
                                    ))
                                elif not output_value.startswith(('http://', 'https://', 'data:')) and len(output_value) > 1000 and output_value[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/':
                                    # Pure base64 string (OpenAI Images API format)
                                    logger.info(f"[MEDIA-STORAGE-DEBUG] ✓ Matched: Pure base64 (OpenAI Images API)")
                                    logger.info(f"[RECORDER] Decoding pure base64 string ({len(output_value)} chars)")
                                    try:
                                        import base64

                                        # Decode base64 directly (no data URI parsing needed)
                                        image_bytes = base64.b64decode(output_value)

                                        # Default to PNG format for Images API
                                        image_format = 'png'

                                        # Save using recorder.save_entity
                                        saved_filename = recorder.save_entity(
                                            entity_type=f'output_{media_type}',
                                            content=image_bytes,
                                            metadata={
                                                'config': output_config_name,
                                                'backend': 'api',
                                                'provider': 'openai',
                                                'seed': seed,
                                                'format': image_format,
                                                'source': 'images_api_base64'
                                            }
                                        )
                                        logger.info(f"[RECORDER] Saved {media_type} from pure base64: {saved_filename}")
                                    except Exception as e:
                                        logger.error(f"[RECORDER] Failed to decode pure base64: {e}")
                                        import traceback
                                        traceback.print_exc()
                                        saved_filename = None
                                elif output_value.startswith('data:'):
                                    logger.info(f"[MEDIA-STORAGE-DEBUG] ✓ Matched: data: URI (base64 with mime type)")
                                    # API-based generation with base64 data URI (e.g., some API providers)
                                    logger.info(f"[RECORDER] Decoding base64 data URI ({len(output_value)} chars)")
                                    try:
                                        import base64
                                        import re

                                        # Extract mime type and base64 data from data URI
                                        # Format: data:image/png;base64,iVBORw0KGgo...
                                        match = re.match(r'data:([^;]+);base64,(.+)', output_value)
                                        if match:
                                            mime_type = match.group(1)
                                            base64_data = match.group(2)

                                            # Decode base64
                                            image_bytes = base64.b64decode(base64_data)

                                            # Detect format from mime type
                                            format_map = {
                                                'image/png': 'png',
                                                'image/jpeg': 'jpg',
                                                'image/webp': 'webp',
                                                'image/gif': 'gif'
                                            }
                                            image_format = format_map.get(mime_type, 'png')

                                            # Save using recorder.save_entity
                                            saved_filename = recorder.save_entity(
                                                entity_type=f'output_{media_type}',
                                                content=image_bytes,
                                                metadata={
                                                    'config': output_config_name,
                                                    'backend': 'api',
                                                    'provider': 'openrouter',
                                                    'seed': seed,
                                                    'format': image_format,
                                                    'source': 'data_uri'
                                                }
                                            )
                                            logger.info(f"[RECORDER] Saved {media_type} from data URI: {saved_filename}")
                                        else:
                                            logger.error(f"[RECORDER] Invalid data URI format")
                                            saved_filename = None
                                    except Exception as e:
                                        logger.error(f"[RECORDER] Failed to decode data URI: {e}")
                                        import traceback
                                        traceback.print_exc()
                                        saved_filename = None
                                else:
                                    logger.info(f"[MEDIA-STORAGE-DEBUG] ✓ Matched: ComfyUI prompt_id (fallback)")
                                    # ComfyUI generation - prompt_id
                                    logger.info(f"[RECORDER] Downloading from ComfyUI: {output_value}")

                                    # Save prompt_id for potential SSE streaming
                                    recorder.save_prompt_id(output_value, media_type)

                                    # Download and save media immediately (blocking, but necessary for media API)
                                    saved_filename = asyncio.run(recorder.download_and_save_from_comfyui(
                                        prompt_id=output_value,
                                        media_type=media_type,
                                        config=output_config_name,
                                        seed=seed
                                    ))

                                if saved_filename:
                                    media_stored = True
                                    logger.info(f"[RECORDER] Media stored successfully in run {run_id}: {saved_filename}")
                                else:
                                    media_stored = False
                                    logger.warning(f"[RECORDER] Failed to store media for run {run_id}")

                            except Exception as e:
                                logger.error(f"[RECORDER] Error downloading/storing media: {e}")
                                import traceback
                                traceback.print_exc()

                            # Log Stage 4 output (using run_id as file_path now)
                            tracker.log_output_image(
                                loop_iteration=i + 1,
                                config_used=output_config_name,
                                file_path=run_id if media_stored else output_result.final_output,
                                model_used=output_result.metadata.get('model_used', 'unknown'),
                                backend_used=output_result.metadata.get('backend', 'comfyui'),
                                metadata=output_result.metadata,
                                execution_time=output_result.execution_time
                            )

                            media_outputs.append({
                                'config': output_config_name,
                                'status': 'success',
                                'run_id': run_id,  # NEW: Unified identifier for media
                                'output': run_id if media_stored else output_result.final_output,  # Use run_id if stored, fallback to raw output
                                'media_type': media_type,
                                'media_stored': media_stored,  # Indicates if media was successfully stored
                                'execution_time': output_result.execution_time,
                                'metadata': output_result.metadata
                            })
                            logger.info(f"[4-STAGE] Stage 4 successful for {output_config_name}: run_id={run_id}, media_stored={media_stored}")
                        else:
                            # Media generation failed
                            media_outputs.append({
                                'config': output_config_name,
                                'status': 'error',
                                'media_type': media_type,  # Add media_type for frontend
                                'error': output_result.error
                            })
                            logger.error(f"[4-STAGE] Stage 4 failed for {output_config_name}: {output_result.error}")

                    except Exception as e:
                        logger.error(f"[4-STAGE] Exception during Stage 4 for {output_config_name}: {e}")
                        media_outputs.append({
                            'config': output_config_name,
                            'status': 'error',
                            'media_type': media_type,  # Add media_type for frontend
                            'error': str(e)
                        })

            # Add media outputs to response
            if len(media_outputs) == 1:
                # Single output: Use old format for backward compatibility
                response_data['media_output'] = media_outputs[0]
            else:
                # Multiple outputs: Use array format
                response_data['media_outputs'] = media_outputs
                response_data['media_output_count'] = len(media_outputs)

        elif not configs_to_execute and default_output and default_output != 'text':
            # No output config found for default_output
            logger.info(f"[AUTO-MEDIA] No Output-Config available for {default_output}/{execution_mode}")
            response_data['media_output'] = {
                'status': 'not_available',
                'message': f'No Output-Config for {default_output}/{execution_mode}'
            }

        # ====================================================================
        # FINALIZE EXECUTION HISTORY
        # ====================================================================
        # Log pipeline completion
        outputs_generated = len(media_outputs) if media_outputs else 0
        tracker.log_pipeline_complete(
            total_duration=result.execution_time if result else 0.0,
            outputs_generated=outputs_generated
        )

        # Persist execution history to storage
        tracker.finalize()
        logger.info(f"[TRACKER] Execution history saved: {tracker.execution_id}")

        # Visual separator for easier run distinction in terminal
        total_time = result.execution_time if result else 0.0
        logger.info("=" * 80)
        logger.info(f"{'RUN COMPLETED':^80}")
        logger.info("=" * 80)
        logger.info(f"  Run ID: {run_id}")
        logger.info(f"  Config: {schema_name}")
        logger.info(f"  Total Time: {total_time:.2f}s")
        logger.info(f"  Outputs: {outputs_generated}")
        logger.info("=" * 80)

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Pipeline-Execution Fehler: {e}")
        import traceback
        traceback.print_exc()

        # Try to finalize tracker even on error (fail-safe)
        try:
            if 'tracker' in locals():
                tracker.log_pipeline_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stage=0
                )
                tracker.finalize()
        except Exception as tracker_error:
            logger.warning(f"[TRACKER] Failed to finalize on error: {tracker_error}")

        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# NOTE: Status endpoint is in pipeline_routes.py, not here
# Use /api/pipeline/{run_id}/status (not /api/schema/pipeline/{run_id}/status)

@schema_bp.route('/pipeline/test', methods=['POST'])  
def test_pipeline():
    """Test-Endpoint für direkte Prompt-Interception"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'error': 'JSON-Request erwartet'}), 400
        
        input_prompt = data.get('input_prompt')
        style_prompt = data.get('style_prompt', '')
        input_context = data.get('input_context', '')
        model = data.get('model', 'local/gemma2:9b')
        
        if not input_prompt:
            return jsonify({'status': 'error', 'error': 'Parameter "input_prompt" erforderlich'}), 400
        
        # Direkte Prompt-Interception (für Tests)
        from schemas.engine.prompt_interception_engine import PromptInterceptionRequest
        engine = PromptInterceptionEngine()
        
        request_obj = PromptInterceptionRequest(
            input_prompt=input_prompt,
            input_context=input_context,
            style_prompt=style_prompt,
            model=model,
            debug=data.get('debug', False)
        )
        
        response = asyncio.run(engine.process_request(request_obj))
        
        if response.success:
            return jsonify({
                'status': 'success',
                'input_prompt': input_prompt,
                'output_str': response.output_str,
                'model_used': response.model_used,
                'metadata': {
                    'output_float': response.output_float,
                    'output_int': response.output_int,
                    'output_binary': response.output_binary
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'error': response.error
            }), 500
            
    except Exception as e:
        logger.error(f"Test-Pipeline Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@schema_bp.route('/schemas', methods=['GET'])
def list_schemas():
    """Verfügbare Schemas auflisten"""
    try:
        init_schema_engine()

        schemas = []
        for schema_name in pipeline_executor.get_available_schemas():
            schema_info = pipeline_executor.get_schema_info(schema_name)
            if schema_info:
                schemas.append(schema_info)

        return jsonify({
            'status': 'success',
            'schemas': schemas
        })

    except Exception as e:
        logger.error(f"Schema-List Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# ============================================================================
# BACKWARD COMPATIBILITY ENDPOINTS (Legacy Frontend Support)
# These endpoints have NO URL prefix and match the old workflow_routes.py API
# ============================================================================
# STATUS: DEPRECATED as of 2025-10-28
# REASON: workflow.js (dropdown system) replaced by workflow-browser.js (cards)
# KEEP: /pipeline_configs_metadata (used by workflow-browser.js)
# REMOVE: /list_workflows, /workflow_metadata (only used by deprecated workflow.js)
# ============================================================================

# DEPRECATED: /list_workflows - Only used by old dropdown system (workflow.js.obsolete)
# @schema_compat_bp.route('/list_workflows', methods=['GET'])
# def list_workflows_compat():
#     """List available Schema-Pipeline configs (replaces workflow_routes.py)"""
#     try:
#         init_schema_engine()
#
#         # Return Schema-Pipelines as dev/config_name format (matches old API)
#         schema_workflows = []
#         for schema_name in pipeline_executor.get_available_schemas():
#             schema_workflows.append(f"dev/{schema_name}")
#
#         logger.info(f"Schema-Pipelines returned: {len(schema_workflows)}")
#
#         return jsonify({"workflows": schema_workflows})
#     except Exception as e:
#         logger.error(f"Error listing workflows: {e}")
#         return jsonify({"error": "Failed to list workflows"}), 500


# DEPRECATED: /workflow_metadata - Only used by old dropdown system (workflow.js.obsolete)
# @schema_compat_bp.route('/workflow_metadata', methods=['GET'])
# def workflow_metadata_compat():
#     """Get Schema-Pipeline metadata (replaces workflow_routes.py)"""
#     try:
#         init_schema_engine()
#
#         metadata = {
#             "categories": {
#                 "dev": {
#                     "de": "Schema-Pipelines (Interception Configs)",
#                     "en": "Schema Pipelines (Interception Configs)"
#                 }
#             },
#             "workflows": {}
#         }
#
#         # Add Schema-Pipeline metadata
#         for schema_name in pipeline_executor.get_available_schemas():
#             schema_info = pipeline_executor.get_schema_info(schema_name)
#             if schema_info:
#                 # Format: dev_config_name (workflow.js expects this format)
#                 workflow_id = f"dev_{schema_name}"
#
#                 config = schema_info.get('config', {})
#                 meta = config.get('meta', {})
#
#                 metadata["workflows"][workflow_id] = {
#                     "category": "dev",
#                     "name": config.get('name', {'de': schema_name, 'en': schema_name}),
#                     "description": config.get('description', {
#                         'de': schema_info.get('description', ''),
#                         'en': schema_info.get('description', '')
#                     }),
#                     "file": f"dev/{schema_name}"
#                 }
#
#         logger.info(f"Schema-Pipeline metadata returned: {len(metadata['workflows'])} configs")
#
#         return jsonify(metadata)
#     except Exception as e:
#         logger.error(f"Error getting workflow metadata: {e}")
#         return jsonify({"error": "Failed to get workflow metadata"}), 500


@schema_compat_bp.route('/pipeline_configs_metadata', methods=['GET'])
def pipeline_configs_metadata_compat():
    """
    Get metadata for all pipeline configs (Expert Mode Karten-Browser)
    Reads directly from config files
    """
    try:
        init_schema_engine()

        # Read metadata directly from config files
        configs_metadata = []
        schemas_path = Path(__file__).parent.parent.parent / "schemas"
        configs_path = schemas_path / "configs"

        if not configs_path.exists():
            return jsonify({"error": "Configs directory not found"}), 404

        # Recursive glob to support subdirectories (interception/, output/, user_configs/)
        for config_file in sorted(configs_path.glob("**/*.json")):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Filter: Only show active Stage 2 (interception) configs
                # Skip: output configs, deactivated configs, user configs, other stages
                relative_path_str = str(config_file.relative_to(configs_path))

                # Skip deactivated configs (in deactivated/ subdirectory)
                if "deactivated" in relative_path_str:
                    continue

                # Skip user configs (in user_configs/ subdirectory)
                if "user_configs" in relative_path_str:
                    continue

                # Only show interception configs (Stage 2)
                stage = config_data.get("meta", {}).get("stage", "")
                if stage != "interception":
                    continue  # Don't show output configs or other stages in legacy frontend

                # Calculate config ID (relative path without .json)
                # Example: interception/dada.json → "dada"
                #          user_configs/doej/test.json → "u_doej_test" (handled by config_loader)
                relative_path = config_file.relative_to(configs_path)
                parts = relative_path.parts

                # Use same naming logic as config_loader.py
                if len(parts) >= 2 and parts[0] == "user_configs":
                    # User config: u_username_filename
                    username = parts[1]
                    stem = config_file.stem
                    config_id = f"u_{username}_{stem}"
                    owner = username  # User-created
                elif parts[0] in ["interception", "output"]:
                    # Main system configs: just the stem
                    config_id = config_file.stem
                    owner = "system"  # System config
                else:
                    # Other system configs: keep path
                    config_id = str(relative_path.with_suffix('')).replace('\\', '/')
                    owner = "system"  # System config

                # Extract metadata fields directly from config
                metadata = {
                    "id": config_id,
                    "name": config_data.get("name", {}),  # Multilingual
                    "description": config_data.get("description", {}),  # Multilingual
                    "category": config_data.get("category", {}),  # Multilingual
                    "pipeline": config_data.get("pipeline", "unknown")
                }

                # Add optional metadata fields if present
                if "display" in config_data:
                    metadata["display"] = config_data["display"]

                if "tags" in config_data:
                    metadata["tags"] = config_data["tags"]

                if "audience" in config_data:
                    metadata["audience"] = config_data["audience"]

                if "media_preferences" in config_data:
                    metadata["media_preferences"] = config_data["media_preferences"]

                # Add meta fields (includes stage, owner, etc.)
                if "meta" in config_data:
                    metadata["meta"] = config_data["meta"]
                else:
                    metadata["meta"] = {}

                # Inject owner if not present
                if "owner" not in metadata["meta"]:
                    metadata["meta"]["owner"] = owner

                configs_metadata.append(metadata)

            except Exception as e:
                logger.error(f"Error reading config {config_file}: {e}")
                continue

        logger.info(f"Loaded metadata for {len(configs_metadata)} pipeline configs")

        return jsonify({"configs": configs_metadata})

    except Exception as e:
        logger.error(f"Error loading pipeline configs metadata: {e}")
        return jsonify({"error": "Failed to load configs metadata"}), 500


@schema_compat_bp.route('/pipeline_configs_with_properties', methods=['GET'])
def pipeline_configs_with_properties():
    """
    Get metadata for all pipeline configs WITH properties for Phase 1 property-based selection.
    Returns configs with properties field + property pairs structure.

    NEW: Phase 1 Property Quadrants implementation (Session 35)
    """
    try:
        init_schema_engine()

        # Feature flag for property symbols (Session 40)
        ENABLE_PROPERTY_SYMBOLS = True  # Set to False to disable symbols

        # Property pairs v2 with symbols and tooltips (Session 40)
        property_pairs_v2 = [
            {
                "id": 1,
                "pair": ["chill", "chaotic"],  # NOTE: Labels use predictable/unpredictable. IDs kept for backward compat (24+ configs)
                "symbols": {"chill": "🎯", "chaotic": "🎲"},
                "labels": {
                    "de": {"chill": "vorhersagbar", "chaotic": "unvorhersagbar"},
                    "en": {"chill": "predictable", "chaotic": "unpredictable"}
                },
                "tooltips": {
                    "de": {
                        "chill": "Output ist erwartbar und steuerbar",
                        "chaotic": "Output ist unvorhersehbar und unberechenbar"
                    },
                    "en": {
                        "chill": "Output is expected and controllable",
                        "chaotic": "Output is unpredictable and unforeseeable"
                    }
                }
            },
            {
                "id": 2,
                "pair": ["narrative", "algorithmic"],
                "symbols": {"narrative": "✍️", "algorithmic": "🔢"},
                "labels": {
                    "de": {"narrative": "semantisch", "algorithmic": "syntaktisch"},
                    "en": {"narrative": "semantic", "algorithmic": "syntactic"}
                },
                "tooltips": {
                    "de": {
                        "narrative": "Schreiben: Bedeutung und Kontext",
                        "algorithmic": "Rechnen: Regeln und Schritte"
                    },
                    "en": {
                        "narrative": "Writing: meaning and context",
                        "algorithmic": "Calculating: rules and steps"
                    }
                }
            },
            {
                "id": 3,
                "pair": ["historical", "contemporary"],
                "symbols": {"historical": "🏛️", "contemporary": "🏙️"},
                "labels": {
                    "de": {"historical": "museal", "contemporary": "lebendig"},
                    "en": {"historical": "museum", "contemporary": "contemporary"}
                },
                "tooltips": {
                    "de": {
                        "historical": "Museumsgebäude (historisch, eingefroren)",
                        "contemporary": "Wolkenkratzer (gegenwärtig, lebendig)"
                    },
                    "en": {
                        "historical": "Museum building (historical, frozen)",
                        "contemporary": "Skyscraper (contemporary, alive)"
                    }
                }
            },
            {
                "id": 4,
                "pair": ["explore", "create"],
                "symbols": {"explore": "🔍", "create": "🎨"},
                "labels": {
                    "de": {"explore": "austesten", "create": "artikulieren"},
                    "en": {"explore": "test AI", "create": "articulate"}
                },
                "tooltips": {
                    "de": {
                        "explore": "KI challengen, kritisch hinterfragen (Detektiv)",
                        "create": "Künstlerisch ausdrücken, gestalten (Künstler)"
                    },
                    "en": {
                        "explore": "Challenge AI, critically question (detective)",
                        "create": "Artistically express, create (artist)"
                    }
                }
            },
            {
                "id": 5,
                "pair": ["playful", "serious"],
                "symbols": {"playful": "🪁", "serious": "🔧"},
                "labels": {
                    "de": {"playful": "verspielt", "serious": "ernst"},
                    "en": {"playful": "playful", "serious": "serious"}
                },
                "tooltips": {
                    "de": {
                        "playful": "Spielerisch, viele Freiheitsgrade (Drachen)",
                        "serious": "Ernst, strukturiert, Genrekonventionen (Werkzeug)"
                    },
                    "en": {
                        "playful": "Playful, many degrees of freedom (kite)",
                        "serious": "Serious, structured, genre conventions (tool)"
                    }
                }
            }
        ]

        # Legacy property pairs (for backward compatibility)
        property_pairs = [
            ["chill", "chaotic"],
            ["narrative", "algorithmic"],
            ["historical", "contemporary"],
            ["explore", "create"],
            ["playful", "serious"]
        ]

        # Read metadata directly from config files
        configs_metadata = []
        schemas_path = Path(__file__).parent.parent.parent / "schemas"
        configs_path = schemas_path / "configs"

        if not configs_path.exists():
            return jsonify({"error": "Configs directory not found"}), 404

        # Excluded directories (deactivated, deprecated, backups, tmp, etc.)
        EXCLUDED_DIRS = {"temporarily_deactivated", "deactivated", "deprecated", "archive", ".obsolete", "tmp", "backup", "backups", "backup_20251114"}

        # Recursive glob to support subdirectories (interception/, output/, user_configs/)
        for config_file in sorted(configs_path.glob("**/*.json")):
            try:
                # Filter: Skip configs in excluded directories
                relative_path = config_file.relative_to(configs_path)
                if any(excluded in relative_path.parts for excluded in EXCLUDED_DIRS):
                    logger.debug(f"Skipping {config_file.name} - in excluded directory")
                    continue

                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Filter: Skip output configs (system-only, not user-facing)
                stage = config_data.get("meta", {}).get("stage", "")
                if stage == "output":
                    continue  # Don't show output configs in frontend

                # Filter: Only include configs with properties (for Phase 1 property selection)
                if "properties" not in config_data:
                    logger.debug(f"Skipping {config_file.name} - no properties field")
                    continue

                # Calculate config ID (relative path without .json)
                parts = relative_path.parts

                # Use same naming logic as config_loader.py
                if len(parts) >= 2 and parts[0] == "user_configs":
                    # User config: u_username_filename
                    username = parts[1]
                    stem = config_file.stem
                    config_id = f"u_{username}_{stem}"
                    owner = username  # User-created
                elif parts[0] in ["interception", "output"]:
                    # Main system configs: just the stem
                    config_id = config_file.stem
                    owner = "system"  # System config
                else:
                    # Other system configs: keep path
                    config_id = str(relative_path.with_suffix('')).replace('\\', '/')
                    owner = "system"  # System config

                # Helper function to create short description
                def make_short_description(long_desc, max_length=220):
                    """
                    Create short description from long one.
                    Extracts complete sentences that fit within max_length.
                    Preserves consistency - doesn't invent new content.
                    Kid-friendly length that provides enough context to understand.

                    Strategy:
                    1. Keep full description if it fits (<= max_length)
                    2. Extract first sentence if it fits
                    3. Extract first 2 sentences if they fit
                    4. Never truncate mid-sentence - use first sentence only
                    """
                    if not long_desc:
                        return long_desc

                    # If full description fits, keep it
                    if len(long_desc) <= max_length:
                        return long_desc

                    # Split into sentences (handle '. ' and '.\n')
                    sentences = long_desc.replace('.\n', '. ').split('. ')

                    # Edge case: no proper sentences (no periods)
                    if len(sentences) == 1:
                        # Truncate at word boundary
                        if len(long_desc) > max_length:
                            truncated = long_desc[:max_length].rsplit(' ', 1)[0]
                            return truncated.strip() + '...'
                        return long_desc

                    # Try first sentence
                    first_sentence = sentences[0] + '.'
                    if len(first_sentence) <= max_length:
                        # Try adding second sentence
                        if len(sentences) >= 2:
                            two_sentences = first_sentence + ' ' + sentences[1] + '.'
                            if len(two_sentences) <= max_length:
                                return two_sentences
                        # Return just first sentence
                        return first_sentence

                    # First sentence too long - truncate at word boundary
                    truncated = long_desc[:max_length].rsplit(' ', 1)[0]
                    return truncated.strip() + '...'

                # Extract metadata fields with properties
                metadata = {
                    "id": config_id,
                    "name": config_data.get("name", {}),  # Multilingual
                    "description": config_data.get("description", {}),  # Multilingual (long version)
                    "category": config_data.get("category", {}),  # Multilingual
                    "pipeline": config_data.get("pipeline", "unknown"),
                    "properties": config_data.get("properties", [])  # NEW: Properties for filtering
                }

                # Add short descriptions for tile display
                long_desc = config_data.get("description", {})
                if isinstance(long_desc, dict):
                    metadata["short_description"] = {
                        lang: make_short_description(text)
                        for lang, text in long_desc.items()
                    }
                else:
                    metadata["short_description"] = make_short_description(long_desc)

                # Add display metadata (icon, color, difficulty, etc.)
                if "display" in config_data:
                    display = config_data["display"]
                    metadata["icon"] = display.get("icon", "🎨")
                    metadata["color"] = display.get("color", "#888888")
                    metadata["difficulty"] = display.get("difficulty", 3)

                    # Phase 1 description (agency-oriented) - NEW
                    if "phase1_description" in display:
                        metadata["phase1_description"] = display["phase1_description"]
                    else:
                        # Fallback to regular description
                        metadata["phase1_description"] = config_data.get("description", {})

                # Add tags
                if "tags" in config_data:
                    metadata["tags"] = config_data["tags"]

                # Add audience metadata
                if "audience" in config_data:
                    metadata["audience"] = config_data["audience"]

                # Add media preferences
                if "media_preferences" in config_data:
                    metadata["media_preferences"] = config_data["media_preferences"]

                # Add owner info
                metadata["owner"] = owner

                configs_metadata.append(metadata)

            except Exception as e:
                logger.error(f"Error reading config {config_file}: {e}")
                continue

        logger.info(f"Loaded {len(configs_metadata)} configs with properties for Phase 1")

        # Return with or without symbols based on feature flag (Session 40)
        if ENABLE_PROPERTY_SYMBOLS:
            return jsonify({
                "configs": configs_metadata,
                "property_pairs": property_pairs_v2,
                "symbols_enabled": True
            })
        else:
            return jsonify({
                "configs": configs_metadata,
                "property_pairs": property_pairs,
                "symbols_enabled": False
            })

    except Exception as e:
        logger.error(f"Error loading configs with properties: {e}")
        return jsonify({"error": "Failed to load configs with properties"}), 500


@schema_compat_bp.route('/api/config/<config_id>/context', methods=['GET'])
def get_config_context(config_id):
    """
    Get the context field for a specific config (Phase 2 - Meta-Prompt Editing)

    Returns the multilingual context field: {en: "...", de: "..."}
    or string if not yet translated.

    NEW: Phase 2 Multilingual Context Editing (Session 36)
    """
    try:
        init_schema_engine()

        # Load config
        config = config_loader.get_config(config_id)

        if not config:
            return jsonify({"error": f"Config not found: {config_id}"}), 404

        # Get context from config
        context = config.context if hasattr(config, 'context') else None

        if context is None:
            return jsonify({"error": f"Config {config_id} has no context field"}), 404

        # Return context (can be string or {en: ..., de: ...})
        return jsonify({
            "config_id": config_id,
            "context": context
        })

    except Exception as e:
        logger.error(f"Error loading context for config {config_id}: {e}")
        return jsonify({"error": f"Failed to load context: {str(e)}"}), 500


@schema_compat_bp.route('/api/config/<config_id>/pipeline', methods=['GET'])
def get_config_pipeline(config_id):
    """
    Get pipeline structure metadata for a config (Phase 2 - Dynamic UI)

    Returns pipeline metadata to determine:
    - How many input bubbles to show (input_requirements)
    - Whether to show context editing bubble (requires_interception_prompt)
    - Pipeline stage and type for UI adaptation

    NEW: Phase 2 Dynamic Pipeline Structure (Session 36)
    """
    try:
        init_schema_engine()

        # Load config
        config = config_loader.get_config(config_id)

        if not config:
            return jsonify({"error": f"Config not found: {config_id}"}), 404

        # Get pipeline metadata
        pipeline = config_loader.pipelines.get(config.pipeline_name)

        if not pipeline:
            return jsonify({"error": f"Pipeline not found: {config.pipeline_name}"}), 404

        # Return pipeline structure metadata
        return jsonify({
            "config_id": config_id,
            "pipeline_name": pipeline.name,
            "pipeline_type": pipeline.pipeline_type,
            "pipeline_stage": pipeline.pipeline_stage,
            "requires_interception_prompt": pipeline.requires_interception_prompt,
            "input_requirements": pipeline.input_requirements or {},
            "description": pipeline.description
        })

    except Exception as e:
        logger.error(f"Error loading pipeline metadata for config {config_id}: {e}")
        return jsonify({"error": f"Failed to load pipeline metadata: {str(e)}"}), 500
