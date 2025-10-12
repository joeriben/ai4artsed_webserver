"""
Flask routes for workflow operations
"""
import logging
import time
from flask import Blueprint, jsonify, request, current_app

from config import (
    ENABLE_VALIDATION_PIPELINE,
    COMFYUI_PREFIX,
    POLLING_TIMEOUT
)
from my_app.services.ollama_service import ollama_service
from my_app.services.comfyui_service import comfyui_service
from my_app.services.workflow_logic_service import workflow_logic_service
from my_app.services.export_manager import export_manager
from my_app.services.inpainting_service import inpainting_service
from my_app.utils.helpers import parse_hidden_commands
from my_app.utils.negative_terms import normalize_negative_terms

logger = logging.getLogger(__name__)

# Create blueprint
workflow_bp = Blueprint('workflow', __name__)


@workflow_bp.route('/list_workflows', methods=['GET'])
def list_workflows():
    """List all available workflows (Legacy + Schema-Pipelines)"""
    try:
        # Legacy-Workflows laden
        legacy_workflows = workflow_logic_service.list_workflows()
        
        # Schema-Pipelines laden (als dev-workflows)
        schema_workflows = []
        try:
            # Schema-Engine importieren
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            
            from schemas.engine.pipeline_executor import PipelineExecutor
            
            schemas_path = Path(__file__).parent.parent.parent / "schemas"
            executor = PipelineExecutor(schemas_path)
            executor.schema_registry.initialize(schemas_path)
            
            # Schema-Pipelines als dev/schema_name format
            for schema_name in executor.get_available_schemas():
                schema_workflows.append(f"dev/{schema_name}")
                
            logger.info(f"Schema-Pipelines geladen: {schema_workflows}")
            
        except Exception as e:
            logger.warning(f"Schema-Pipelines nicht verfügbar: {e}")
        
        # Kombinierte Liste
        all_workflows = legacy_workflows + schema_workflows
        
        return jsonify({"workflows": all_workflows})
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return jsonify({"error": "Failed to list workflows"}), 500


@workflow_bp.route('/workflow_metadata', methods=['GET'])
def workflow_metadata():
    """Get workflow metadata including categories and descriptions (Legacy + Schema)"""
    try:
        # Legacy-Metadata laden
        metadata = workflow_logic_service.get_metadata()
        
        # Schema-Pipeline-Metadata hinzufügen
        try:
            # Schema-Engine importieren
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            
            from schemas.engine.pipeline_executor import PipelineExecutor
            
            schemas_path = Path(__file__).parent.parent.parent / "schemas"
            executor = PipelineExecutor(schemas_path)
            executor.schema_registry.initialize(schemas_path)
            
            # Dev-Kategorie hinzufügen falls noch nicht vorhanden
            if "categories" not in metadata:
                metadata["categories"] = {}
            
            metadata["categories"]["dev"] = {
                "de": "Development (Schema-Pipelines)",
                "en": "Development (Schema Pipelines)"
            }
            
            # Schema-Pipeline-Workflows hinzufügen
            if "workflows" not in metadata:
                metadata["workflows"] = {}
            
            for schema_name in executor.get_available_schemas():
                schema_info = executor.get_schema_info(schema_name)
                if schema_info:
                    # Schema als Workflow-ID mit dev/ prefix
                    workflow_id = f"dev_{schema_name}"
                    
                    metadata["workflows"][workflow_id] = {
                        "category": "dev",
                        "name": {
                            "de": schema_info.get('meta', {}).get('description_de', schema_info['name']),
                            "en": schema_info.get('meta', {}).get('description_en', schema_info['name'])
                        },
                        "description": {
                            "de": f"Schema-Pipeline: {schema_info['description']} (Pipeline-Typ: {schema_info.get('pipeline_type', 'unknown')})",
                            "en": f"Schema Pipeline: {schema_info['description']} (Pipeline Type: {schema_info.get('pipeline_type', 'unknown')})"
                        },
                        "file": f"dev/{schema_name}"
                    }
            
            logger.info(f"Schema-Pipeline-Metadata hinzugefügt: {len(executor.get_available_schemas())} Schemas")
            
        except Exception as e:
            logger.warning(f"Schema-Pipeline-Metadata nicht verfügbar: {e}")
        
        return jsonify(metadata)
    except Exception as e:
        logger.error(f"Error getting workflow metadata: {e}")
        return jsonify({"error": "Failed to get workflow metadata"}), 500


@workflow_bp.route('/workflow_selection_config', methods=['GET'])
def workflow_selection_config():
    """Get current workflow selection configuration"""
    try:
        from config import WORKFLOW_SELECTION, FIXED_WORKFLOW, SYSTEM_WORKFLOW_FOLDERS
        
        return jsonify({
            "mode": WORKFLOW_SELECTION,
            "fixed_workflow": FIXED_WORKFLOW,
            "system_folders": SYSTEM_WORKFLOW_FOLDERS
        })
    except Exception as e:
        logger.error(f"Error getting workflow selection config: {e}")
        return jsonify({"error": "Failed to get workflow selection config"}), 500


@workflow_bp.route('/workflow_has_safety_node/<path:workflow_name>', methods=['GET'])
def workflow_has_safety_node(workflow_name):
    """Check if a workflow contains the safety node"""
    try:
        has_safety_node = workflow_logic_service.check_safety_node(workflow_name)
        return jsonify({"has_safety_node": has_safety_node})
    except Exception as e:
        logger.error(f"Error checking workflow safety node: {e}")
        return jsonify({"error": "Failed to check workflow"}), 500


@workflow_bp.route('/workflow-type/<path:workflow_name>', methods=['GET'])
def workflow_type(workflow_name):
    """Check if a workflow is an inpainting workflow"""
    try:
        is_inpainting = workflow_logic_service.is_inpainting_workflow(workflow_name)
        return jsonify({"isInpainting": is_inpainting})
    except Exception as e:
        logger.error(f"Error checking workflow type: {e}")
        return jsonify({"error": "Failed to check workflow type"}), 500


@workflow_bp.route('/workflow-info/<path:workflow_name>', methods=['GET'])
def workflow_info(workflow_name):
    """Get comprehensive workflow information"""
    try:
        info = workflow_logic_service.get_workflow_info(workflow_name)
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting workflow info: {e}")
        return jsonify({"error": "Failed to get workflow info"}), 500


@workflow_bp.route('/validate-prompt', methods=['POST'])
def validate_prompt():
    """Validate and translate a prompt"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({"error": "Kein Prompt angegeben."}), 400
        
        logger.info(f"Validating prompt: {prompt[:50]}...")
        
        # Skip validation if disabled
        if not ENABLE_VALIDATION_PIPELINE:
            return jsonify({
                "success": True,
                "translated_prompt": prompt,
                "cached": False,
                "skipped": True
            })
        
        # Validate and translate
        result = ollama_service.validate_and_translate_prompt(prompt)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error validating prompt: {e}")
        return jsonify({"error": "Validierungsfehler"}), 500


@workflow_bp.route('/run_workflow', methods=['POST'])
def execute_workflow():
    """Execute a workflow with support for three modes: text_only, image_with_text, inpainting"""
    try:
        from config import WORKFLOW_SELECTION, FIXED_WORKFLOW
        
        data = request.json
        workflow_name = data.get('workflow')
        original_prompt = data.get('prompt', '').strip()
        aspect_ratio = data.get('aspectRatio', '1:1')
        mode = data.get('mode', 'eco')
        seed_mode = data.get('seedMode', 'random')
        custom_seed = data.get('customSeed', None)
        safety_level = data.get('safetyLevel', 'off')
        input_negative_terms = normalize_negative_terms(data.get('inputNegativeTerms'))
        
        # Input mode and image data
        image_data = data.get('imageData')
        input_mode = data.get('inputMode', 'text_only')
        skip_translation = data.get('skipTranslation', False)
        
        # Parse hidden commands from the prompt (moved up)
        clean_prompt, hidden_commands = parse_hidden_commands(original_prompt)
        
        # Handle server-level commands
        if hidden_commands.get('notranslate'):
            skip_translation = True
            logger.info("Hidden command #notranslate# detected, skipping translation")
        
        # Check for empty prompt after command removal
        if not clean_prompt:
            return jsonify({"error": "Kein Prompt angegeben (nach Entfernen von Hidden Commands)."}), 400
        
        # CHECK: Schema-Pipeline (dev/) vs Legacy-Workflow
        if workflow_name and workflow_name.startswith("dev/"):
            # Schema-Pipeline ausführen (synchron mit asyncio.run)
            schema_name = workflow_name.replace("dev/", "")
            logger.info(f"Executing Schema-Pipeline: {schema_name}")
            
            try:
                # Schema-Engine importieren
                import sys
                from pathlib import Path
                import asyncio
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                
                from schemas.engine.pipeline_executor import PipelineExecutor
                
                schemas_path = Path(__file__).parent.parent.parent / "schemas"
                executor = PipelineExecutor(schemas_path)
                executor.schema_registry.initialize(schemas_path)
                
                # Schema-Pipeline ausführen (synchron)
                result = asyncio.run(executor.execute_pipeline(
                    schema_name=schema_name,
                    input_text=clean_prompt,
                    user_input=original_prompt
                ))
                
                if result.status.value == 'completed':
                    # Tag-Detection für Media-Typ
                    final_output = result.final_output or ""
                    media_type = "text"  # Default
                    
                    # Check for media tags
                    if "#image#" in final_output:
                        media_type = "image"
                    elif "#music#" in final_output:
                        media_type = "music"
                    elif "#audio#" in final_output:
                        media_type = "audio"
                    elif "#video#" in final_output:
                        media_type = "video"
                    
                    # Check for ComfyUI prompt_id in metadata
                    prompt_id = None
                    for step in result.steps:
                        if step.metadata and 'prompt_id' in step.metadata:
                            prompt_id = step.metadata['prompt_id']
                            break
                    
                    response_data = {
                        "success": True,
                        "schema_pipeline": True,
                        "schema_name": schema_name,
                        "final_output": final_output,
                        "steps_completed": len(result.steps),
                        "execution_time": result.execution_time,
                        "original_prompt": original_prompt,
                        "translated_prompt": final_output,
                        "status_updates": [f"Schema-Pipeline '{schema_name}' erfolgreich ausgeführt"]
                    }
                    
                    # Add media info if ComfyUI generated something
                    if media_type != "text" and prompt_id:
                        response_data["media"] = {
                            "type": media_type,
                            "prompt_id": prompt_id,
                            "url": f"/api/media/{media_type}/{prompt_id}"
                        }
                    
                    return jsonify(response_data)
                else:
                    return jsonify({
                        "error": f"Schema-Pipeline fehlgeschlagen: {result.error}",
                        "schema_pipeline": True,
                        "schema_name": schema_name
                    }), 500
                    
            except Exception as e:
                logger.error(f"Schema-Pipeline Fehler: {e}")
                return jsonify({
                    "error": f"Schema-Pipeline fehlgeschlagen: {str(e)}",
                    "schema_pipeline": True,
                    "schema_name": schema_name
                }), 500
        
        # Backend-side workflow selection based on configuration (Legacy-Workflows)
        if WORKFLOW_SELECTION == "fixed":
            workflow_name = FIXED_WORKFLOW
            logger.info(f"Using fixed workflow: {workflow_name}")
        elif WORKFLOW_SELECTION == "system":
            workflow_name = workflow_logic_service.get_random_workflow_from_folders()
            if not workflow_name:
                return jsonify({"error": "System konnte keinen Workflow auswählen."}), 500
            logger.info(f"System selected workflow: {workflow_name}")
        elif WORKFLOW_SELECTION == "user":
            if workflow_name == "random":
                workflow_name = workflow_logic_service.get_random_workflow_from_folders()
                if not workflow_name:
                    return jsonify({"error": "System konnte keinen zufälligen Workflow auswählen."}), 500
                logger.info(f"User requested random workflow: {workflow_name}")
            elif not workflow_name:
                return jsonify({"error": "Kein Workflow angegeben."}), 400
            # else: workflow_name remains the user-selected workflow
        
        # Parse hidden commands from the prompt
        clean_prompt, hidden_commands = parse_hidden_commands(original_prompt)
        
        # Handle server-level commands
        if hidden_commands.get('notranslate'):
            skip_translation = True
            logger.info("Hidden command #notranslate# detected, skipping translation")
        
        # Check for empty prompt after command removal
        if not clean_prompt:
            return jsonify({"error": "Kein Prompt angegeben (nach Entfernen von Hidden Commands)."}), 400
        
        workflow_prompt = clean_prompt
        logger.info(f"Executing workflow: {workflow_name} in mode: {input_mode}")
        if hidden_commands:
            logger.info(f"Hidden commands found: {hidden_commands}")
        
        # Validate prompt (translation + safety check) if enabled
        if ENABLE_VALIDATION_PIPELINE:
            # For image_with_text mode, skip translation as frontend already translated
            if skip_translation:
                logger.info("Skipping translation as requested by frontend")
                # Still do safety check
                safety_result = ollama_service.check_safety(workflow_prompt)
                if not safety_result["is_safe"]:
                    return jsonify({"error": safety_result.get("reason", "Prompt rejected for safety reasons.")}), 400
            else:
                validation_result = ollama_service.validate_and_translate_prompt(workflow_prompt)
                
                if not validation_result["success"]:
                    # Safety check failed
                    return jsonify({"error": validation_result.get("error", "Prompt-Validierung fehlgeschlagen.")}), 400
                
                # Use translated prompt for workflow execution
                workflow_prompt = validation_result["translated_prompt"]
                logger.info(f"Using validated prompt: {workflow_prompt[:50]}...")
        
        # Prepare workflow with the workflow_prompt and input_negative_terms and hidden commands
        result = workflow_logic_service.prepare_workflow(
            workflow_name, 
            workflow_prompt, 
            aspect_ratio, 
            mode, 
            seed_mode, 
            custom_seed, 
            safety_level, 
            input_negative_terms,
            hidden_commands
        )
        
        if not result["success"]:
            return jsonify({"error": result["error"]}), 400
        
        workflow = result["workflow"]
        status_updates = result.get("status_updates", [])
        used_seed = result.get("used_seed")
        
        # Handle inpainting workflows - inject image data
        if input_mode == 'inpainting' and image_data:
            logger.info("Injecting image into inpainting workflow")
            workflow = inpainting_service.inject_image_to_workflow(workflow, image_data)
            status_updates.append("Bild wurde in Inpainting-Workflow eingefügt.")
        
        # Log workflow if kids safety is enabled (for debugging)
        if safety_level == "kids":
            logger.info("=== Workflow being sent to ComfyUI (kids safety enabled) ===")
            # Log negative prompts to verify they were enhanced
            for node_id, node_data in workflow.items():
                if node_data.get("class_type") == "CLIPTextEncode":
                    # Check if this is connected to a negative input
                    text = node_data.get("inputs", {}).get("text", "")
                    if any(term in text for term in ["violence", "blood", "horror"]):
                        logger.info(f"Node {node_id} negative prompt (first 200 chars): {text[:200]}...")
        
        # Submit to ComfyUI
        prompt_id = comfyui_service.submit_workflow(workflow)
        
        if not prompt_id:
            return jsonify({"error": "ComfyUI hat kein Prompt-ID zurückgegeben."}), 500
        
        # Store pending export info
        current_app.pending_exports[prompt_id] = {
            "workflow_name": workflow_name,
            "prompt": original_prompt,  # Always store the original prompt
            "translated_prompt": workflow_prompt,  # Store the workflow prompt (translated or original)
            "used_seed": used_seed,
            "safety_level": safety_level,
            "timestamp": time.time()
        }
        
        return jsonify({
            "success": True,
            "prompt_id": prompt_id,
            "status_updates": status_updates,
            "translated_prompt": workflow_prompt,  # Return the workflow prompt
            "used_seed": used_seed  # Return the seed that was used
        })
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return jsonify({"error": f"Workflow-Ausführung fehlgeschlagen: {str(e)}"}), 500


@workflow_bp.route('/workflow-status/<prompt_id>', methods=['GET'])
def workflow_status(prompt_id):
    """Check workflow execution status"""
    try:
        # Get history from ComfyUI
        history = comfyui_service.get_history(prompt_id)
        
        if not history or prompt_id not in history:
            return jsonify({"status": "pending"})
        
        session_data = history[prompt_id]
        outputs = session_data.get("outputs", {})
        
        if outputs:
            # Workflow completed
            response = {
                "status": "completed",
                "outputs": outputs
            }
            
            # Trigger auto-export if enabled
            if prompt_id in current_app.pending_exports:
                export_info = current_app.pending_exports[prompt_id]
                logger.info(f"[AUTO-EXPORT DEBUG] Starting auto-export for {prompt_id}")
                logger.info(f"[AUTO-EXPORT DEBUG] Export info: {export_info}")
                try:
                    result = export_manager.auto_export_session(
                        prompt_id,
                        export_info["workflow_name"],
                        export_info["prompt"],  # Original prompt
                        export_info.get("translated_prompt"),  # Keep for documentation
                        export_info.get("used_seed"),
                        export_info.get("safety_level", "off")
                    )
                    logger.info(f"[AUTO-EXPORT DEBUG] Auto-export result: {result}")
                except Exception as e:
                    logger.error(f"[AUTO-EXPORT DEBUG] Auto-export failed with exception: {e}")
                del current_app.pending_exports[prompt_id]
            else:
                logger.warning(f"[AUTO-EXPORT DEBUG] No pending export found for {prompt_id}")
            
            return jsonify(response)
        else:
            return jsonify({"status": "processing"})
            
    except Exception as e:
        logger.error(f"Error checking workflow status: {e}")
        return jsonify({"error": "Status-Abfrage fehlgeschlagen"}), 500


@workflow_bp.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze an image using vision model"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"error": "Kein Bild angegeben."}), 400
        
        logger.info("Analyzing image...")
        
        # Analyze image
        analysis = ollama_service.analyze_image(image_data)
        
        if analysis:
            return jsonify({
                "success": True,
                "analysis": analysis
            })
        else:
            return jsonify({"error": "Bildanalyse fehlgeschlagen."}), 500
            
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return jsonify({"error": "Bildanalyse-Fehler"}), 500


# ComfyUI proxy route
@workflow_bp.route(f'/{COMFYUI_PREFIX}/<path:path>', methods=['GET', 'POST'])
def comfyui_proxy(path):
    """Proxy requests to ComfyUI"""
    try:
        response = comfyui_service.proxy_request(path, request.args)
        
        # Check if this is a history request with results
        if path.startswith('history/') and response.status_code == 200:
            prompt_id = path.split('/')[-1]
            # Check if we have pending export for this prompt_id
            if prompt_id in current_app.pending_exports:
                try:
                    # Parse response to check if workflow is completed
                    import json
                    history_data = json.loads(response.content)
                    
                    # Check if this prompt_id has outputs (meaning it's completed)
                    if prompt_id in history_data and history_data[prompt_id].get('outputs'):
                        logger.info(f"Triggering auto-export for completed workflow {prompt_id}")
                        
                        # Get export info
                        export_info = current_app.pending_exports[prompt_id]
                        
                        # Trigger auto-export
                        export_manager.auto_export_session(
                            prompt_id,
                            export_info["workflow_name"],
                            export_info["prompt"],  # Original prompt
                            export_info.get("translated_prompt"),  # Keep for documentation
                            export_info.get("used_seed"),
                            export_info.get("safety_level", "off")
                        )
                        
                        # Remove from pending exports
                        del current_app.pending_exports[prompt_id]
                        
                except Exception as e:
                    logger.error(f"Error during auto-export: {e}")
        
        return response.content, response.status_code, dict(response.headers)
    except Exception as e:
        logger.error(f"ComfyUI proxy error: {e}")
        return jsonify({"error": "Proxy-Fehler"}), 500
