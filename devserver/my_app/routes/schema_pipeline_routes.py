"""
Schema Pipeline Routes - API für Schema-basierte Pipeline-Execution
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import logging
import asyncio
import json

# Schema-Engine importieren
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.prompt_interception_engine import PromptInterceptionEngine
from schemas.engine.stage_orchestrator import (
    execute_stage1_translation,
    execute_stage1_safety,
    execute_stage3_safety,
    build_safety_message
)

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
        # STAGE 1: PRE-INTERCEPTION (Translation + Safety)
        # ====================================================================
        current_input = input_text

        if not is_system_pipeline and not is_output_config:
            logger.info(f"[4-STAGE] Stage 1: Pre-Interception for '{schema_name}'")

            # Stage 1a: Translation
            translated_text = asyncio.run(execute_stage1_translation(
                input_text,
                execution_mode,
                pipeline_executor
            ))
            current_input = translated_text

            # Stage 1b: Safety Check
            is_safe, codes = asyncio.run(execute_stage1_safety(
                translated_text,
                safety_level,
                execution_mode,
                pipeline_executor
            ))

            if not is_safe:
                # Build error message
                error_message = build_safety_message(codes, lang='de')
                logger.warning(f"[4-STAGE] Stage 1 BLOCKED: {codes}")

                return jsonify({
                    'status': 'error',
                    'schema': schema_name,
                    'error': error_message,
                    'metadata': {
                        'stage': 'pre_interception',
                        'safety_codes': codes
                    }
                }), 403

        # ====================================================================
        # STAGE 2: INTERCEPTION (Main Pipeline - DUMB execution)
        # ====================================================================
        logger.info(f"[4-STAGE] Stage 2: Interception (Main Pipeline) for '{schema_name}'")

        result = asyncio.run(pipeline_executor.execute_pipeline(
            config_name=schema_name,
            input_text=current_input,
            user_input=data.get('user_input', input_text),
            execution_mode=execution_mode,
            safety_level=safety_level
        ))

        # Check if pipeline succeeded
        if not result.success:
            return jsonify({
                'status': 'error',
                'schema': schema_name,
                'error': result.error,
                'steps_completed': len([s for s in result.steps if s.status.value == 'completed']),
                'total_steps': len(result.steps)
            }), 500

        # Response für erfolgreiche Pipeline
        response_data = {
            'status': 'success',
            'schema': schema_name,
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

                # ====================================================================
                # STAGE 3: PRE-OUTPUT SAFETY (per output config)
                # ====================================================================
                stage_3_blocked = False

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

                    if not safety_result['safe']:
                        # Stage 3 blocked for this output
                        abort_reason = safety_result.get('abort_reason', 'Content blocked by safety filter')
                        logger.warning(f"[4-STAGE] Stage 3 BLOCKED for {output_config_name}: {abort_reason}")

                        media_outputs.append({
                            'config': output_config_name,
                            'status': 'blocked',
                            'reason': abort_reason,
                            'safety_level': safety_level
                        })
                        stage_3_blocked = True
                        continue  # Skip Stage 4 for this output

                # ====================================================================
                # STAGE 4: OUTPUT (Media Generation)
                # ====================================================================
                if not stage_3_blocked:
                    logger.info(f"[4-STAGE] Stage 4: Executing output config '{output_config_name}'")

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
                            media_outputs.append({
                                'config': output_config_name,
                                'status': 'success',
                                'output': output_result.final_output,  # ComfyUI prompt_id or image URL
                                'execution_time': output_result.execution_time,
                                'metadata': output_result.metadata
                            })
                            logger.info(f"[4-STAGE] Stage 4 successful for {output_config_name}: {output_result.final_output}")
                        else:
                            # Media generation failed
                            media_outputs.append({
                                'config': output_config_name,
                                'status': 'error',
                                'error': output_result.error
                            })
                            logger.error(f"[4-STAGE] Stage 4 failed for {output_config_name}: {output_result.error}")

                    except Exception as e:
                        logger.error(f"[4-STAGE] Exception during Stage 4 for {output_config_name}: {e}")
                        media_outputs.append({
                            'config': output_config_name,
                            'status': 'error',
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

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Pipeline-Execution Fehler: {e}")
        import traceback
        traceback.print_exc()
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
