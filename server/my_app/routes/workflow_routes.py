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

logger = logging.getLogger(__name__)

# Create blueprint
workflow_bp = Blueprint('workflow', __name__)


@workflow_bp.route('/list_workflows', methods=['GET'])
def list_workflows():
    """List all available workflows"""
    try:
        workflows = workflow_logic_service.list_workflows()
        return jsonify({"workflows": workflows})
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return jsonify({"error": "Failed to list workflows"}), 500


@workflow_bp.route('/workflow_metadata', methods=['GET'])
def workflow_metadata():
    """Get workflow metadata including categories and descriptions"""
    try:
        metadata = workflow_logic_service.get_metadata()
        return jsonify(metadata)
    except Exception as e:
        logger.error(f"Error getting workflow metadata: {e}")
        return jsonify({"error": "Failed to get workflow metadata"}), 500


@workflow_bp.route('/workflow_has_safety_node/<workflow_name>', methods=['GET'])
def workflow_has_safety_node(workflow_name):
    """Check if a workflow contains the safety node"""
    try:
        has_safety_node = workflow_logic_service.check_safety_node(workflow_name)
        return jsonify({"has_safety_node": has_safety_node})
    except Exception as e:
        logger.error(f"Error checking workflow safety node: {e}")
        return jsonify({"error": "Failed to check workflow"}), 500


@workflow_bp.route('/workflow-type/<workflow_name>', methods=['GET'])
def workflow_type(workflow_name):
    """Check if a workflow is an inpainting workflow"""
    try:
        is_inpainting = workflow_logic_service.is_inpainting_workflow(workflow_name)
        return jsonify({"isInpainting": is_inpainting})
    except Exception as e:
        logger.error(f"Error checking workflow type: {e}")
        return jsonify({"error": "Failed to check workflow type"}), 500


@workflow_bp.route('/workflow-info/<workflow_name>', methods=['GET'])
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
        data = request.json
        workflow_name = data.get('workflow')
        original_prompt = data.get('prompt', '').strip()
        aspect_ratio = data.get('aspectRatio', '1:1')
        mode = data.get('mode', 'eco')
        seed_mode = data.get('seedMode', 'random')
        custom_seed = data.get('customSeed', None)
        safety_level = data.get('safetyLevel', 'off')
        
        # Input mode and image data
        image_data = data.get('imageData')
        input_mode = data.get('inputMode', 'text_only')
        skip_translation = data.get('skipTranslation', False)
        
        if not workflow_name:
            return jsonify({"error": "Kein Workflow angegeben."}), 400
        
        # The frontend already handles the concatenation and sends the final prompt
        # We just need to validate and process it
        if not original_prompt:
            return jsonify({"error": "Kein Prompt angegeben."}), 400
        
        workflow_prompt = original_prompt
        logger.info(f"Executing workflow: {workflow_name} in mode: {input_mode}")
        
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
        
        # Prepare workflow with the workflow_prompt
        result = workflow_logic_service.prepare_workflow(workflow_name, workflow_prompt, aspect_ratio, mode, seed_mode, custom_seed, safety_level)
        
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
                export_manager.auto_export_session(
                    prompt_id,
                    export_info["workflow_name"],
                    export_info["prompt"],
                    export_info.get("translated_prompt"),
                    export_info.get("used_seed"),
                    export_info.get("safety_level", "off")
                )
                del current_app.pending_exports[prompt_id]
            
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
                            export_info["prompt"],
                            export_info.get("translated_prompt"),
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
