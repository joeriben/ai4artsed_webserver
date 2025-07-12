"""
Streaming workflow routes to prevent Cloudflare timeouts
"""
import logging
import json
import time
from flask import Blueprint, jsonify, request, current_app, Response

from config import (
    ENABLE_VALIDATION_PIPELINE,
    COMFYUI_PREFIX,
    POLLING_TIMEOUT
)
from my_app.services.ollama_service import ollama_service
from my_app.services.comfyui_service import comfyui_service
from my_app.services.workflow_logic_service import workflow_logic_service
from my_app.services.export_manager import export_manager
from my_app.services.streaming_response import create_streaming_response

logger = logging.getLogger(__name__)

# Create blueprint
workflow_streaming_bp = Blueprint('workflow_streaming', __name__)


@workflow_streaming_bp.route('/run_workflow_stream', methods=['POST'])
def execute_workflow_stream():
    """Execute a workflow with streaming response to prevent timeouts"""
    
    def execute_workflow_internal():
        """Internal function to execute the workflow"""
        try:
            data = request.json
            workflow_name = data.get('workflow')
            prompt = data.get('prompt', '').strip()
            aspect_ratio = data.get('aspectRatio', '1:1')
            mode = data.get('mode', 'eco')
            seed_mode = data.get('seedMode', 'random')
            custom_seed = data.get('customSeed', None)
            safety_level = data.get('safetyLevel', 'off')
            
            if not workflow_name:
                return {"error": "Kein Workflow angegeben."}
            
            if not prompt:
                return {"error": "Kein Prompt angegeben."}
            
            # Validate prompt if enabled
            if ENABLE_VALIDATION_PIPELINE:
                validation_result = ollama_service.validate_and_translate_prompt(prompt)
                
                if not validation_result["success"]:
                    return {"error": validation_result.get("error", "Prompt-Validierung fehlgeschlagen.")}
                
                prompt = validation_result["translated_prompt"]
            
            # Prepare workflow
            result = workflow_logic_service.prepare_workflow(
                workflow_name, prompt, aspect_ratio, mode, seed_mode, custom_seed, safety_level
            )
            
            if not result["success"]:
                return {"error": result["error"]}
            
            workflow = result["workflow"]
            status_updates = result.get("status_updates", [])
            used_seed = result.get("used_seed")
            
            # Submit to ComfyUI
            prompt_id = comfyui_service.submit_workflow(workflow)
            
            if not prompt_id:
                return {"error": "ComfyUI hat kein Prompt-ID zurückgegeben."}
            
            # Store pending export info
            current_app.pending_exports[prompt_id] = {
                "workflow_name": workflow_name,
                "prompt": prompt,
                "timestamp": time.time()
            }
            
            # Wait for completion with periodic checks
            max_wait_time = 480  # 8 minutes
            check_interval = 5   # Check every 5 seconds
            start_time = time.time()
            
            while (time.time() - start_time) < max_wait_time:
                history = comfyui_service.get_history(prompt_id)
                
                if history and prompt_id in history:
                    session_data = history[prompt_id]
                    outputs = session_data.get("outputs", {})
                    
                    if outputs:
                        # Workflow completed
                        # Trigger auto-export if enabled
                        if prompt_id in current_app.pending_exports:
                            export_info = current_app.pending_exports[prompt_id]
                            export_manager.auto_export_session(
                                prompt_id,
                                export_info["workflow_name"],
                                export_info["prompt"]
                            )
                            del current_app.pending_exports[prompt_id]
                        
                        return {
                            "success": True,
                            "prompt_id": prompt_id,
                            "status": "completed",
                            "outputs": outputs,
                            "status_updates": status_updates,
                            "translated_prompt": prompt,
                            "used_seed": used_seed
                        }
                
                time.sleep(check_interval)
            
            # Timeout reached
            return {
                "error": "Workflow-Timeout erreicht",
                "prompt_id": prompt_id,
                "status": "timeout"
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {"error": f"Workflow-Ausführung fehlgeschlagen: {str(e)}"}
    
    # Create and return streaming response
    return create_streaming_response(execute_workflow_internal)


@workflow_streaming_bp.route('/workflow-status-poll/<prompt_id>', methods=['GET'])
def workflow_status_poll(prompt_id):
    """Fast polling endpoint for workflow status"""
    try:
        # Quick check without blocking
        history = comfyui_service.get_history(prompt_id)
        
        if not history or prompt_id not in history:
            return jsonify({"status": "pending", "timestamp": time.time()})
        
        session_data = history[prompt_id]
        outputs = session_data.get("outputs", {})
        
        if outputs:
            return jsonify({
                "status": "completed",
                "outputs": outputs,
                "timestamp": time.time()
            })
        else:
            return jsonify({"status": "processing", "timestamp": time.time()})
            
    except Exception as e:
        logger.error(f"Error checking workflow status: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500
