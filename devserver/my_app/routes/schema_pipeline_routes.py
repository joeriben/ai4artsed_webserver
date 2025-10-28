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
    """Schema-Pipeline ausführen mit Auto-Media-Unterstützung"""
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

        if not schema_name or not input_text:
            return jsonify({
                'status': 'error',
                'error': 'Parameter "schema" und "input_text" erforderlich'
            }), 400

        # Schema-Engine initialisieren
        init_schema_engine()

        # Get config to check for media_preferences
        config = pipeline_executor.config_loader.get_config(schema_name)
        if not config:
            return jsonify({
                'status': 'error',
                'error': f'Config "{schema_name}" nicht gefunden'
            }), 404

        logger.info(f"[AUTO-MEDIA] Executing config '{schema_name}' with execution_mode='{execution_mode}'")

        # 1. Execute Interception-Pipeline (or direct Output-Pipeline)
        result = asyncio.run(pipeline_executor.execute_pipeline(
            config_name=schema_name,
            input_text=input_text,
            user_input=data.get('user_input', input_text),
            execution_mode=execution_mode
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

        # 2. Check for Auto-Media: Does config request media output?
        # ResolvedConfig has media_preferences as direct attribute (not in parameters)
        media_preferences = config.media_preferences or {}

        default_output = media_preferences.get('default_output') if media_preferences else None

        if default_output and default_output != 'text':
            logger.info(f"[AUTO-MEDIA] Config requests media output: {default_output}")

            # 3. Lookup Output-Config from defaults
            output_config_name = lookup_output_config(default_output, execution_mode)

            if output_config_name:
                logger.info(f"[AUTO-MEDIA] Starting Output-Pipeline: {output_config_name}")

                # 4. Execute Output-Pipeline with transformed text
                output_result = asyncio.run(pipeline_executor.execute_pipeline(
                    config_name=output_config_name,
                    input_text=result.final_output,  # Use transformed text as input!
                    user_input=result.final_output,
                    execution_mode=execution_mode
                ))

                # Add media output to response
                if output_result.success:
                    response_data['media_output'] = {
                        'config': output_config_name,
                        'media_type': default_output,
                        'output': output_result.final_output,  # ComfyUI prompt_id or image URL
                        'execution_time': output_result.execution_time,
                        'metadata': output_result.metadata
                    }
                    logger.info(f"[AUTO-MEDIA] Media generation successful: {output_result.final_output}")
                else:
                    # Media generation failed, but text generation succeeded
                    response_data['media_output'] = {
                        'status': 'error',
                        'error': output_result.error
                    }
                    logger.error(f"[AUTO-MEDIA] Media generation failed: {output_result.error}")
            else:
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

        for config_file in sorted(configs_path.glob("*.json")):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Extract metadata fields directly from config
                metadata = {
                    "id": config_file.stem,  # Filename without .json
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

                configs_metadata.append(metadata)

            except Exception as e:
                logger.error(f"Error reading config {config_file}: {e}")
                continue

        logger.info(f"Loaded metadata for {len(configs_metadata)} pipeline configs")

        return jsonify({"configs": configs_metadata})

    except Exception as e:
        logger.error(f"Error loading pipeline configs metadata: {e}")
        return jsonify({"error": "Failed to load configs metadata"}), 500
