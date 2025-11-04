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
from schemas.engine.stage_orchestrator import (
    execute_stage1_translation,
    execute_stage1_safety,
    execute_stage1_gpt_oss_unified,
    execute_stage3_safety,
    build_safety_message
)

# Execution History Tracking (OLD - will be replaced)
from execution_history import ExecutionTracker

# Media Storage Service (OLD - will be replaced)
from my_app.services.media_storage import get_media_storage_service

# NEW: Live Pipeline Recorder (Session 29)
from pipeline_recorder import get_recorder

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

        logger.info("Schema-Engine initialisiert")

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

        if not schema_name or not input_text:
            return jsonify({
                'status': 'error',
                'error': 'Parameter "schema" und "input_text" erforderlich'
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
        # EXECUTION HISTORY TRACKER - Create request-scoped tracker (OLD)
        # ====================================================================
        tracker = ExecutionTracker(
            config_name=schema_name,
            execution_mode=execution_mode,
            safety_level=safety_level,
            user_id='anonymous',  # TODO: Extract from session
            session_id='default'  # TODO: Extract from session
        )

        # Log pipeline start
        tracker.log_pipeline_start(
            input_text=input_text,
            metadata={'request_timestamp': data.get('timestamp')}
        )

        # ====================================================================
        # MEDIA STORAGE - Create atomic run folder (OLD)
        # ====================================================================
        media_storage = get_media_storage_service()
        run_metadata = asyncio.run(media_storage.create_run(
            schema=schema_name,
            execution_mode=execution_mode,
            input_text=input_text,
            transformed_text=None,  # Will be updated after Stage 2
            user_id='anonymous',
            run_id=run_id  # NEW: Pass unified run_id
        ))
        logger.info(f"[MEDIA_STORAGE] Created run {run_id} for {schema_name}")

        # ====================================================================
        # SESSION 29: LIVE PIPELINE RECORDER (NEW)
        # ====================================================================
        # Parallel implementation: Run alongside old systems for testing
        recorder = get_recorder(
            run_id=run_id,  # Use same unified ID
            config_name=schema_name,
            execution_mode=execution_mode,
            safety_level=safety_level,
            user_id='anonymous'
        )
        recorder.set_state(0, "pipeline_starting")
        logger.info(f"[RECORDER] Initialized LivePipelineRecorder for run {run_id}")

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

            # Stage 1: GPT-OSS Unified (Translation + §86a Safety in ONE call)
            is_safe, translated_text, error_message = asyncio.run(execute_stage1_gpt_oss_unified(
                input_text,
                safety_level,
                execution_mode,
                pipeline_executor
            ))
            current_input = translated_text

            if not is_safe:
                logger.warning(f"[4-STAGE] Stage 1 BLOCKED by GPT-OSS §86a")

                # SESSION 29: Save translation (even if blocked)
                recorder.save_entity('translation', translated_text)

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

            # SESSION 29: Save translation and safety results
            recorder.save_entity('translation', translated_text)
            recorder.save_entity('safety', {
                'safe': True,
                'method': 'gpt_oss_unified',
                'codes_checked': ['§86a'],
                'safety_level': safety_level
            })
            logger.info(f"[RECORDER] Saved translation and safety entities")

            # Log translation result (GPT-OSS includes translation)
            tracker.log_translation_result(
                translated_text=translated_text,
                from_lang='de',
                to_lang='en',
                model_used='gpt-oss',
                backend_used='ollama',
                execution_time=0.0  # TODO: Track actual execution time from GPT-OSS unified pipeline
            )

        # ====================================================================
        # STAGE 2: INTERCEPTION (Main Pipeline - DUMB execution)
        # ====================================================================
        logger.info(f"[4-STAGE] Stage 2: Interception (Main Pipeline) for '{schema_name}'")
        tracker.set_stage(2)
        recorder.set_state(2, "interception")

        result = asyncio.run(pipeline_executor.execute_pipeline(
            config_name=schema_name,
            input_text=current_input,
            user_input=data.get('user_input', input_text),
            execution_mode=execution_mode,
            safety_level=safety_level,
            tracker=tracker
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

        # Response für erfolgreiche Pipeline
        response_data = {
            'status': 'success',
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

        # Determine which output configs to use
        if output_configs:
            # Multi-Output: Use explicit output_configs array
            logger.info(f"[MULTI-OUTPUT] Config requests {len(output_configs)} outputs: {output_configs}")
            configs_to_execute = output_configs
        elif default_output and default_output != 'text':
            # Single-Output: Use lookup from default_output
            output_config_name = lookup_output_config(default_output, execution_mode)
            if output_config_name:
                configs_to_execute = [output_config_name]
            else:
                configs_to_execute = []
        else:
            # Text-only output
            configs_to_execute = []

        # Execute Stage 3-4 for each output config
        media_outputs = []

        if configs_to_execute and not is_system_pipeline and not is_output_config:
            logger.info(f"[4-STAGE] Stage 3-4 Loop: Processing {len(configs_to_execute)} output configs")

            for i, output_config_name in enumerate(configs_to_execute):
                logger.info(f"[4-STAGE] Stage 3-4 Loop iteration {i+1}/{len(configs_to_execute)}: {output_config_name}")
                tracker.set_loop_iteration(i + 1)

                # ====================================================================
                # STAGE 3: PRE-OUTPUT SAFETY (per output config)
                # ====================================================================
                stage_3_blocked = False
                tracker.set_stage(3)
                recorder.set_state(3, "pre_output_safety")

                if safety_level != 'off':
                    # Determine media type from output config name
                    # Simple heuristic: if name contains 'image', 'audio', 'video', etc.
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

                # ====================================================================
                # STAGE 4: OUTPUT (Media Generation)
                # ====================================================================
                if not stage_3_blocked:
                    logger.info(f"[4-STAGE] Stage 4: Executing output config '{output_config_name}'")
                    tracker.set_stage(4)
                    recorder.set_state(4, "media_generation")

                    try:
                        # Execute Output-Pipeline with transformed text
                        output_result = asyncio.run(pipeline_executor.execute_pipeline(
                            config_name=output_config_name,
                            input_text=result.final_output,  # Use transformed text as input!
                            user_input=result.final_output,
                            execution_mode=execution_mode
                        ))

                        # Add media output to results
                        if output_result.success:
                            # ====================================================================
                            # MEDIA STORAGE - Download and store media locally
                            # ====================================================================
                            media_stored = False
                            media_output_data = None

                            try:
                                output_value = output_result.final_output

                                # Detect if output is URL or prompt_id
                                if output_value.startswith('http://') or output_value.startswith('https://'):
                                    # API-based generation (GPT-5, Replicate, etc.) - URL
                                    logger.info(f"[MEDIA_STORAGE] Downloading from URL: {output_value}")
                                    media_output_data = asyncio.run(media_storage.add_media_from_url(
                                        run_id=run_id,
                                        url=output_value,
                                        config=output_config_name,
                                        media_type=media_type
                                    ))
                                else:
                                    # ComfyUI generation - prompt_id
                                    logger.info(f"[MEDIA_STORAGE] Downloading from ComfyUI: {output_value}")
                                    media_output_data = asyncio.run(media_storage.add_media_from_comfyui(
                                        run_id=run_id,
                                        prompt_id=output_value,
                                        config=output_config_name,
                                        media_type=media_type
                                    ))

                                if media_output_data:
                                    media_stored = True
                                    logger.info(f"[MEDIA_STORAGE] Media stored successfully in run {run_id}: {media_output_data.filename}")

                                    # SESSION 29: Copy media file to recorder folder
                                    try:
                                        from pathlib import Path
                                        media_source = Path(media_output_data.file_path)
                                        if media_source.exists():
                                            with open(media_source, 'rb') as f:
                                                media_bytes = f.read()
                                            recorder.save_entity(
                                                f'output_{media_type}',
                                                media_bytes,
                                                metadata={
                                                    'config': output_config_name,
                                                    'filename': media_output_data.filename,
                                                    'original_path': str(media_output_data.file_path)
                                                }
                                            )
                                            logger.info(f"[RECORDER] Saved output_{media_type} entity")
                                        else:
                                            logger.warning(f"[RECORDER] Media file not found at {media_source}")
                                    except Exception as copy_error:
                                        logger.error(f"[RECORDER] Failed to copy media to recorder: {copy_error}")

                                else:
                                    logger.warning(f"[MEDIA_STORAGE] Failed to store media for run {run_id}")

                            except Exception as e:
                                logger.error(f"[MEDIA_STORAGE] Error storing media: {e}")
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

                # Filter: Skip output configs (system-only, not user-facing)
                stage = config_data.get("meta", {}).get("stage", "")
                if stage == "output":
                    continue  # Don't show output configs in frontend

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
