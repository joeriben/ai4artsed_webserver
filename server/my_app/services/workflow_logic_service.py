"""
Service for workflow manipulation and logic
"""
import logging
import json
import random
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from config import (
    LOCAL_WORKFLOWS_DIR,
    OLLAMA_TO_OPENROUTER_MAP,
    OPENROUTER_TO_OLLAMA_MAP,
    ENABLE_VALIDATION_PIPELINE
)
from my_app.utils.helpers import (
    calculate_dimensions,
    parse_model_name
)

logger = logging.getLogger(__name__)


class WorkflowLogicService:
    """Service for handling workflow logic and manipulation"""
    
    def __init__(self):
        self.workflows_dir = LOCAL_WORKFLOWS_DIR
    
    def load_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a workflow file by name
        
        Args:
            workflow_name: Name of the workflow file
            
        Returns:
            Workflow dictionary or None if not found
        """
        # Security check
        if ".." in workflow_name or workflow_name.startswith("/"):
            logger.error(f"Invalid workflow name: {workflow_name}")
            return None
        
        workflow_path = self.workflows_dir / workflow_name
        
        try:
            with open(workflow_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Workflow not found: {workflow_name}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in workflow {workflow_name}: {e}")
            return None
    
    def list_workflows(self) -> list:
        """
        List all available workflow files
        
        Returns:
            List of workflow filenames
        """
        try:
            workflows = sorted([
                f.name for f in self.workflows_dir.glob("*.json")
                if not f.name.startswith(".")
            ])
            return workflows
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    def switch_to_eco_mode(self, workflow: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
        """
        Switch workflow to eco mode (local models)
        
        Args:
            workflow: Workflow definition
            
        Returns:
            Tuple of (modified workflow, status updates)
        """
        status_updates = ["Eco-Modus aktiviert. Alle Modelle werden lokal ausgeführt."]
        
        for node_data in workflow.values():
            if node_data.get("class_type") == "ai4artsed_prompt_interception":
                current_model_full = node_data["inputs"].get("model", "")
                
                if current_model_full.startswith("openrouter/"):
                    openrouter_model_name = current_model_full[11:].split(' ')[0]
                    local_model = OPENROUTER_TO_OLLAMA_MAP.get(openrouter_model_name)
                    
                    if local_model:
                        node_data["inputs"]["model"] = f"local/{local_model}"
                        logger.info(f"Swapped {current_model_full} to {node_data['inputs']['model']}")
                        status_updates.append(
                            f"Cloud-Modell '{openrouter_model_name}' durch lokales Modell '{local_model}' ersetzt."
                        )
                    else:
                        logger.warning(f"No local equivalent found for {current_model_full}")
                        status_updates.append(
                            f"Warnung: Kein lokales Äquivalent für '{openrouter_model_name}' gefunden."
                        )
        
        return workflow, status_updates
    
    def switch_to_fast_mode(self, workflow: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
        """
        Switch workflow to fast mode (cloud models)
        
        Args:
            workflow: Workflow definition
            
        Returns:
            Tuple of (modified workflow, status updates)
        """
        status_updates = ["Schnell-Modus aktiviert. Suche nach Cloud-basierten Modell-Äquivalenten..."]
        
        for node_data in workflow.values():
            if node_data.get("class_type") == "ai4artsed_prompt_interception":
                current_model_full = node_data["inputs"].get("model", "")
                
                if current_model_full.startswith("local/"):
                    local_model_raw = current_model_full[6:]
                    local_model_with_tag = re.split(r'\s*\[', local_model_raw)[0].strip()
                    
                    # Try for exact match first
                    exact_match = (
                        OLLAMA_TO_OPENROUTER_MAP.get(local_model_with_tag) or 
                        OLLAMA_TO_OPENROUTER_MAP.get(local_model_with_tag.split(':')[0])
                    )
                    
                    # Apply intelligent fallback logic
                    req_base, req_size = parse_model_name(local_model_with_tag)
                    
                    if 7 <= req_size <= 32 and "mistral-nemo" in OLLAMA_TO_OPENROUTER_MAP and local_model_with_tag != "mistral-nemo":
                        if exact_match == "mistralai/mistral-small-24b" or not exact_match:
                            openrouter_model = OLLAMA_TO_OPENROUTER_MAP["mistral-nemo"]
                            status_updates.append(
                                f"Using Mistral Nemo (14b) as intelligent fallback for {req_size}b model."
                            )
                        else:
                            openrouter_model = exact_match
                            status_updates.append(f"Using exact match: '{exact_match}'.")
                    elif exact_match:
                        openrouter_model = exact_match
                        status_updates.append(f"Using exact match: '{exact_match}'.")
                    else:
                        # Intelligent fallback
                        openrouter_model = self._find_fallback_model(local_model_with_tag, req_base, req_size)
                        if openrouter_model:
                            status_updates.append(f"Found fallback: '{openrouter_model}'.")
                        else:
                            status_updates.append(f"No fallback found for '{local_model_with_tag}'.")
                    
                    if openrouter_model:
                        node_data["inputs"]["model"] = f"openrouter/{openrouter_model}"
                        logger.info(f"Swapped {current_model_full} to {node_data['inputs']['model']}")
        
        return workflow, status_updates
    
    def _find_fallback_model(self, model_name: str, req_base: str, req_size: int) -> Optional[str]:
        """Find a suitable fallback model for fast mode"""
        # For medium-sized models, prefer Mistral Nemo
        if 7 <= req_size <= 32 and "mistral-nemo" in OLLAMA_TO_OPENROUTER_MAP:
            return OLLAMA_TO_OPENROUTER_MAP["mistral-nemo"]
        
        # Find candidates in the same family
        candidates = []
        for map_key in OLLAMA_TO_OPENROUTER_MAP.keys():
            cand_base, cand_size = parse_model_name(map_key)
            if (req_base.startswith(cand_base) or cand_base.startswith(req_base)) and cand_size >= req_size:
                candidates.append((map_key, cand_size))
        
        if candidates:
            candidates.sort(key=lambda x: x[1])
            return OLLAMA_TO_OPENROUTER_MAP[candidates[0][0]]
        
        # Ultimate fallback
        return OLLAMA_TO_OPENROUTER_MAP.get("mistral-nemo")
    
    def inject_prompt(self, workflow: Dict[str, Any], prompt: str) -> bool:
        """
        Inject a prompt into the workflow
        
        Args:
            workflow: Workflow definition
            prompt: Prompt text to inject
            
        Returns:
            True if injection successful, False otherwise
        """
        for node_data in workflow.values():
            if node_data.get("_meta", {}).get("title") == "ai4artsed_text_prompt":
                target_input = "value" if "value" in node_data["inputs"] else "text"
                if target_input in node_data["inputs"]:
                    node_data["inputs"][target_input] = prompt
                    logger.info("Injected prompt into workflow")
                    return True
        
        logger.warning("Could not find prompt injection node in workflow")
        return False
    
    def update_dimensions(self, workflow: Dict[str, Any], aspect_ratio: str):
        """
        Update image dimensions in workflow based on aspect ratio
        
        Args:
            workflow: Workflow definition
            aspect_ratio: Aspect ratio string (e.g., "16:9")
        """
        dims = calculate_dimensions("1024", aspect_ratio)
        
        for node_data in workflow.values():
            if node_data["class_type"] == "EmptyLatentImage":
                if not isinstance(node_data["inputs"].get("width"), list):
                    node_data["inputs"]["width"] = dims["width"]
                if not isinstance(node_data["inputs"].get("height"), list):
                    node_data["inputs"]["height"] = dims["height"]
    
    def randomize_seeds(self, workflow: Dict[str, Any]):
        """
        Randomize all seed values in the workflow
        
        Args:
            workflow: Workflow definition
        """
        for node_data in workflow.values():
            if "KSampler" in node_data["class_type"] and "seed" in node_data["inputs"]:
                node_data["inputs"]["seed"] = random.randint(0, 2**32 - 1)
    
    def prepare_workflow(self, workflow_name: str, prompt: str, aspect_ratio: str, mode: str) -> Dict[str, Any]:
        """
        Prepare a workflow for execution
        
        Args:
            workflow_name: Name of the workflow
            prompt: Prompt text
            aspect_ratio: Aspect ratio
            mode: Execution mode ('eco' or 'fast')
            
        Returns:
            Dictionary with workflow, status_updates, and success flag
        """
        # Load workflow
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return {"success": False, "error": f"Workflow '{workflow_name}' nicht gefunden."}
        
        status_updates = []
        
        # Apply mode switching
        if mode == 'eco':
            workflow, mode_updates = self.switch_to_eco_mode(workflow)
            status_updates.extend(mode_updates)
        elif mode == 'fast':
            workflow, mode_updates = self.switch_to_fast_mode(workflow)
            status_updates.extend(mode_updates)
        
        # Inject prompt
        if not self.inject_prompt(workflow, prompt):
            return {"success": False, "error": "Workflow hat keinen vorgesehenen Prompt-Eingabeknoten."}
        
        # Update dimensions and randomize seeds
        self.update_dimensions(workflow, aspect_ratio)
        self.randomize_seeds(workflow)
        
        return {
            "success": True,
            "workflow": workflow,
            "status_updates": status_updates
        }


# Create a singleton instance
workflow_logic_service = WorkflowLogicService()
