"""
Service for workflow manipulation and logic
"""
import logging
import json
import random
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from config import (
    LOCAL_WORKFLOWS_DIR,
    OLLAMA_TO_OPENROUTER_MAP,
    OPENROUTER_TO_OLLAMA_MAP,
    ENABLE_VALIDATION_PIPELINE,
    SAFETY_NEGATIVE_TERMS,
    ENABLE_MODEL_PATH_RESOLUTION,
    MODEL_RESOLUTION_FALLBACK,
    SWARMUI_BASE_PATH,
    COMFYUI_BASE_PATH
)
from my_app.utils.helpers import (
    calculate_dimensions,
    parse_model_name
)
from my_app.services.model_path_resolver import ModelPathResolver

logger = logging.getLogger(__name__)


class WorkflowLogicService:
    """Service for handling workflow logic and manipulation"""
    
    def __init__(self):
        self.workflows_dir = LOCAL_WORKFLOWS_DIR
        self.metadata_path = self.workflows_dir / "metadata.json"
        self.metadata = None
        self._generate_metadata()  # Generate metadata on startup
        self._load_metadata()
        
        # Initialize model path resolver if enabled
        if ENABLE_MODEL_PATH_RESOLUTION:
            self.model_resolver = ModelPathResolver(
                swarmui_base=SWARMUI_BASE_PATH,
                comfyui_base=COMFYUI_BASE_PATH
            )
            logger.info("Model path resolver initialized")
        else:
            self.model_resolver = None
            logger.info("Model path resolution disabled")
    
    def _extract_about_info(self, workflow_data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Extract information from über and about nodes"""
        info = {
            "name": {"de": "", "en": ""},
            "description": {"de": "", "en": ""},
            "longDescription": {"de": "", "en": ""}
        }
        
        # Find über and about nodes
        for node_id, node in workflow_data.items():
            if node.get("_meta", {}).get("title") == "über":
                lines = node.get("inputs", {}).get("value", "").split("\n")
                if len(lines) >= 1:
                    info["name"]["de"] = lines[0]
                if len(lines) >= 2:
                    info["description"]["de"] = lines[1]
                if len(lines) >= 3:
                    info["longDescription"]["de"] = "\n".join(lines[2:])
                    
            elif node.get("_meta", {}).get("title") == "about":
                lines = node.get("inputs", {}).get("value", "").split("\n")
                if len(lines) >= 1:
                    info["name"]["en"] = lines[0]
                if len(lines) >= 2:
                    info["description"]["en"] = lines[1]
                if len(lines) >= 3:
                    info["longDescription"]["en"] = "\n".join(lines[2:])
        
        return info
    
    def _generate_metadata(self):
        """Generate metadata.json from workflow files"""
        try:
            metadata = {"categories": {}, "workflows": {}}
            
            # Define category names
            category_names = {
                "across": {"de": "Medienübergreifend", "en": "Cross-Media"},
                "aesthetics": {"de": "Ästhetik", "en": "Aesthetics"},
                "arts": {"de": "Kunstrichtungen", "en": "Art Movements"},
                "culture": {"de": "Kultur", "en": "Culture"},
                "flow": {"de": "Ablauf", "en": "Flow"},
                "model": {"de": "Modelle", "en": "Models"},
                "semantics": {"de": "Semantik", "en": "Semantics"},
                "sound": {"de": "Klang", "en": "Sound"},
                "vector": {"de": "Vektorräume", "en": "Vector Spaces"}
            }
            
            # Process each category folder
            for category_folder in self.workflows_dir.iterdir():
                if category_folder.is_dir() and category_folder.name in category_names:
                    category = category_folder.name
                    
                    # Add category metadata
                    metadata["categories"][category] = category_names[category]
                    
                    # Process workflow files in this category
                    for workflow_file in category_folder.glob("*.json"):
                        workflow_id = workflow_file.stem
                        
                        try:
                            # Read workflow file
                            with open(workflow_file, 'r', encoding='utf-8') as f:
                                workflow_data = json.load(f)
                            
                            # Extract information from about nodes
                            info = self._extract_about_info(workflow_data)
                            
                            # Add to metadata
                            metadata["workflows"][workflow_id] = {
                                "category": category,
                                "name": info["name"],
                                "description": info["description"],
                                "longDescription": info["longDescription"],
                                "file": f"{category}/{workflow_file.name}"
                            }
                            
                        except Exception as e:
                            logger.error(f"Error processing {workflow_file}: {e}")
            
            # Write metadata.json
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Generated metadata.json with {len(metadata['workflows'])} workflows in {len(metadata['categories'])} categories")
            
        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
    
    def _load_metadata(self):
        """Load workflow metadata from metadata.json"""
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info("Workflow metadata loaded successfully")
            else:
                logger.warning(f"Metadata file not found at {self.metadata_path}")
                self.metadata = {"categories": {}, "workflows": {}, "ui": {}}
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self.metadata = {"categories": {}, "workflows": {}, "ui": {}}
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get workflow metadata"""
        if self.metadata is None:
            self._load_metadata()
        return self.metadata
    
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
        List all available workflow files from subdirectories
        
        Returns:
            List of workflow filenames (including subdirectory paths)
        """
        try:
            workflows = []
            
            # Get all json files from subdirectories
            for json_file in self.workflows_dir.rglob("*.json"):
                # Skip metadata.json and hidden files
                if json_file.name == "metadata.json" or json_file.name.startswith("."):
                    continue
                    
                # Get relative path from workflows directory
                relative_path = json_file.relative_to(self.workflows_dir)
                workflows.append(str(relative_path))
            
            return sorted(workflows)
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    def check_safety_node(self, workflow_name: str) -> bool:
        """
        Check if a workflow contains the safety node
        
        Args:
            workflow_name: Name of the workflow file
            
        Returns:
            True if workflow contains safety node, False otherwise
        """
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return False
        
        # Check if any node has the safety switch class type
        for node_data in workflow.values():
            if node_data.get("class_type") == "ai4artsed_switch_promptsafety":
                return True
        
        return False
    
    def is_inpainting_workflow(self, workflow_name: str) -> bool:
        """
        Check if a workflow is an inpainting/image editing workflow.
        Requires both an appropriate model AND a LoadImage node.
        
        Args:
            workflow_name: Name of the workflow file
            
        Returns:
            True if workflow is for inpainting/image editing, False otherwise
        """
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return False
        
        has_inpainting_model = False
        has_load_image = False
        
        # Check for both conditions
        for node_data in workflow.values():
            class_type = node_data.get("class_type")
            
            # Check for inpainting/image editing models
            if class_type == "CheckpointLoaderSimple":
                ckpt_name = node_data.get("inputs", {}).get("ckpt_name", "").lower()
                if "inpaint" in ckpt_name or "omnigen2" in ckpt_name:
                    has_inpainting_model = True
            elif class_type == "UNETLoader":
                # OmniGen2 uses UNETLoader instead of CheckpointLoaderSimple
                unet_name = node_data.get("inputs", {}).get("unet_name", "").lower()
                if "omnigen2" in unet_name:
                    has_inpainting_model = True
            
            # Check for LoadImage node
            if class_type in ["LoadImage", "LoadImageMask"]:
                has_load_image = True
        
        # Both conditions must be met
        return has_inpainting_model and has_load_image
    
    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get comprehensive workflow information
        
        Args:
            workflow_name: Name of the workflow file
            
        Returns:
            Dict with workflow information
        """
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return {
                "isInpainting": False,
                "hasLoadImageNode": False,
                "requiresBothInputs": False,
                "error": "Workflow not found"
            }
        
        has_inpainting_model = False
        has_load_image = False
        
        # Check for inpainting/image editing models and load image nodes
        for node_data in workflow.values():
            class_type = node_data.get("class_type")
            
            # Check for inpainting/image editing models
            if class_type == "CheckpointLoaderSimple":
                ckpt_name = node_data.get("inputs", {}).get("ckpt_name", "").lower()
                if "inpaint" in ckpt_name or "omnigen2" in ckpt_name:
                    has_inpainting_model = True
            elif class_type == "UNETLoader":
                # OmniGen2 uses UNETLoader instead of CheckpointLoaderSimple
                unet_name = node_data.get("inputs", {}).get("unet_name", "").lower()
                if "omnigen2" in unet_name:
                    has_inpainting_model = True
            
            # Check for load image node
            if class_type in ["LoadImage", "LoadImageMask"]:
                has_load_image = True
        
        # Only consider it an inpainting workflow if BOTH conditions are met
        is_inpainting = has_inpainting_model and has_load_image
        
        return {
            "isInpainting": is_inpainting,
            "hasLoadImageNode": has_load_image,
            "requiresBothInputs": is_inpainting  # Inpainting requires both inputs
        }
    
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
    
    def apply_seed_control(self, workflow: Dict[str, Any], seed_mode: str, custom_seed: Optional[int] = None) -> int:
        """
        Apply seed control to ALL seed-sensitive nodes in the workflow
        Ignores external seed connections and applies the same seed everywhere
        
        Args:
            workflow: Workflow definition
            seed_mode: 'random', 'standard', or 'fixed'
            custom_seed: Custom seed value for 'fixed' mode
            
        Returns:
            The seed value that was used
        """
        # Determine the seed value to use
        if seed_mode == 'standard':
            seed_value = 123456789
        elif seed_mode == 'fixed' and custom_seed is not None:
            seed_value = custom_seed
        else:  # random
            seed_value = random.randint(0, 2**32 - 1)
        
        # List of all sampler node types
        sampler_types = [
            "KSampler", "KSamplerAdvanced", "SamplerCustom",
            "StableAudioSampler", "MusicGenGenerate",
            "AudioScheduledSampler"  # Add more sampler types as needed
        ]
        
        # Apply seed to all sampler nodes
        for node_data in workflow.values():
            # Check if it's a sampler
            if node_data.get("class_type") in sampler_types:
                if "inputs" in node_data and "seed" in node_data["inputs"]:
                    # Override seed, regardless of connections
                    node_data["inputs"]["seed"] = seed_value
                    logger.info(f"Set seed {seed_value} in {node_data.get('class_type')} node")
        
        return seed_value
    
    def apply_safety_level(self, workflow: Dict[str, Any], safety_level: str) -> bool:
        """
        Apply safety level to the workflow if the safety node exists
        
        Args:
            workflow: Workflow definition
            safety_level: Safety level ('off', 'youth', or 'kids')
            
        Returns:
            True if safety node was found and updated, False otherwise
        """
        # Look for the safety switch node
        safety_node_found = False
        
        for node_data in workflow.values():
            if node_data.get("class_type") == "ai4artsed_switch_promptsafety":
                # Found the safety node, update its filter_level
                if "inputs" in node_data:
                    node_data["inputs"]["filter_level"] = safety_level
                    logger.info(f"Applied safety level '{safety_level}' to workflow")
                    safety_node_found = True
        
        if not safety_node_found:
            logger.info("No safety node found in workflow, safety level not applied")
        
        return safety_node_found
    
    def enhance_negative_prompts(self, workflow: Dict[str, Any], safety_level: str) -> int:
        """
        Enhance negative prompts with safety terms based on the safety level
        
        Args:
            workflow: Workflow definition
            safety_level: Safety level ('kids' or 'youth')
            
        Returns:
            Number of negative prompts enhanced
        """
        enhanced_count = 0
        
        logger.info(f"=== Starting {safety_level} safety enhancement ===")
        logger.info(f"Total nodes in workflow: {len(workflow)}")
        
        # First, identify which CLIPTextEncode nodes are connected to negative inputs of KSamplers
        negative_clip_nodes = set()
        
        # List of sampler node types that have negative conditioning
        sampler_types = ["KSampler", "KSamplerAdvanced", "SamplerCustom"]
        
        # Find all sampler nodes and trace their negative inputs
        for node_id, node_data in workflow.items():
            node_type = node_data.get("class_type")
            logger.debug(f"Checking node {node_id}: type={node_type}")
            
            if node_type in sampler_types:
                logger.info(f"Found sampler node {node_id} of type {node_type}")
                # Check if this sampler has a negative input
                inputs = node_data.get("inputs", {})
                logger.debug(f"Sampler inputs: {list(inputs.keys())}")
                
                if "negative" in inputs:
                    negative_input = inputs["negative"]
                    logger.info(f"Sampler node {node_id} has negative input: {negative_input}")
                    
                    # If it's a connection (list with node_id and output_index)
                    if isinstance(negative_input, list) and len(negative_input) >= 2:
                        connected_node_id = str(negative_input[0])
                        negative_clip_nodes.add(connected_node_id)
                        logger.info(f"Added node {connected_node_id} to negative_clip_nodes")
                    else:
                        logger.warning(f"Negative input is not a proper connection: {negative_input}")
        
        logger.info(f"Found {len(negative_clip_nodes)} nodes connected to negative inputs: {negative_clip_nodes}")
        
        # Get the appropriate safety terms based on the safety level
        safety_terms = ", ".join(SAFETY_NEGATIVE_TERMS.get(safety_level, []))
        logger.info(f"Safety terms to add (length: {len(safety_terms)} chars)")
        
        for node_id in negative_clip_nodes:
            if node_id in workflow:
                node_data = workflow[node_id]
                node_type = node_data.get("class_type")
                logger.info(f"Processing negative node {node_id} with class_type: {node_type}")
                
                if node_type == "CLIPTextEncode":
                    current_text = node_data.get("inputs", {}).get("text", "")
                    logger.info(f"Current negative prompt text: '{current_text}'")
                    
                    # Only add safety terms if they're not already present
                    if safety_terms not in current_text:
                        # Append safety terms with proper separation
                        if current_text.strip():
                            new_text = f"{current_text}, {safety_terms}"
                        else:
                            new_text = safety_terms
                        
                        node_data["inputs"]["text"] = new_text
                        logger.info(f"Enhanced negative prompt in node {node_id}")
                        logger.info(f"New text (first 100 chars): '{new_text[:100]}...'")
                        enhanced_count += 1
                    else:
                        logger.info(f"Safety terms already present in node {node_id}")
                else:
                    logger.warning(f"Node {node_id} is not a CLIPTextEncode, it's a {node_type}")
            else:
                logger.error(f"Node {node_id} not found in workflow!")
        
        logger.info(f"=== Enhancement complete. Enhanced {enhanced_count} negative prompts for {safety_level} safety ===")
        return enhanced_count
    
    def _resolve_model_paths(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve model paths in the workflow using the model path resolver
        
        Args:
            workflow: Workflow definition
            
        Returns:
            Modified workflow with resolved model paths
        """
        if not self.model_resolver:
            logger.debug("Model resolver not available, skipping path resolution")
            return workflow
            
        try:
            # Create a deep copy to avoid modifying the original
            import copy
            workflow_copy = copy.deepcopy(workflow)
            resolved_count = 0
            
            # Find all CheckpointLoaderSimple nodes
            for node_id, node_data in workflow_copy.items():
                if node_data.get("class_type") == "CheckpointLoaderSimple":
                    original_name = node_data.get("inputs", {}).get("ckpt_name", "")
                    
                    if original_name:
                        # Skip if it already looks like a path
                        if "/" in original_name or "\\" in original_name:
                            logger.debug(f"Node {node_id}: '{original_name}' already appears to be a path, skipping")
                            continue
                        
                        # Try to resolve the model path
                        resolved_path = self.model_resolver.find_model(original_name)
                        
                        if resolved_path and resolved_path != original_name:
                            node_data["inputs"]["ckpt_name"] = resolved_path
                            logger.info(f"Node {node_id}: Resolved '{original_name}' -> '{resolved_path}'")
                            resolved_count += 1
                        else:
                            logger.warning(f"Node {node_id}: Could not resolve path for '{original_name}'")
            
            if resolved_count > 0:
                logger.info(f"Successfully resolved {resolved_count} model path(s)")
            else:
                logger.info("No model paths needed resolution")
                
            return workflow_copy
            
        except Exception as e:
            logger.error(f"Error resolving model paths: {e}")
            if MODEL_RESOLUTION_FALLBACK:
                logger.info("Using original workflow due to resolution error (fallback mode)")
                return workflow
            else:
                raise
    
    def prepare_workflow(self, workflow_name: str, prompt: str, aspect_ratio: str, mode: str, 
                        seed_mode: str = "random", custom_seed: Optional[int] = None,
                        safety_level: str = "off") -> Dict[str, Any]:
        """
        Prepare a workflow for execution
        
        Args:
            workflow_name: Name of the workflow
            prompt: Prompt text
            aspect_ratio: Aspect ratio
            mode: Execution mode ('eco' or 'fast')
            seed_mode: Seed control mode ('random', 'standard', or 'fixed')
            custom_seed: Custom seed value for 'fixed' mode
            safety_level: Safety level ('off', 'youth', or 'kids')
            
        Returns:
            Dictionary with workflow, status_updates, used_seed, and success flag
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
        
        # Update dimensions and apply seed control
        self.update_dimensions(workflow, aspect_ratio)
        used_seed = self.apply_seed_control(workflow, seed_mode, custom_seed)
        
        # Apply safety level if safety node exists (failsafe)
        safety_applied = self.apply_safety_level(workflow, safety_level)
        if safety_applied and safety_level != "off":
            status_updates.append(f"Sicherheitsstufe '{safety_level}' aktiviert.")
        
        # Enhance negative prompts for safety
        if safety_level in ["kids", "youth"]:
            logger.info(f"{safety_level} safety level selected - enhancing negative prompts")
            enhanced_count = self.enhance_negative_prompts(workflow, safety_level)
            if enhanced_count > 0:
                if safety_level == "kids":
                    status_updates.append(f"Negative Prompts wurden mit Kindersicherheitsbegriffen erweitert ({enhanced_count} Nodes).")
                else:  # youth
                    status_updates.append(f"Negative Prompts wurden mit Jugendschutzbegriffen erweitert ({enhanced_count} Nodes).")
                logger.info(f"Enhanced {enhanced_count} negative prompts for {safety_level} safety")
            else:
                logger.warning(f"{safety_level} safety selected but no negative prompts were enhanced!")
        
        # Resolve model paths if enabled
        if ENABLE_MODEL_PATH_RESOLUTION:
            try:
                workflow = self._resolve_model_paths(workflow)
                logger.info("Model paths resolved successfully")
            except Exception as e:
                logger.warning(f"Model path resolution failed: {e}")
                if not MODEL_RESOLUTION_FALLBACK:
                    return {"success": False, "error": f"Model-Pfad-Auflösung fehlgeschlagen: {str(e)}"}
                # If fallback is enabled, continue with original workflow
                status_updates.append("Warnung: Model-Pfad-Auflösung fehlgeschlagen, verwende Original-Pfade.")
        
        return {
            "success": True,
            "workflow": workflow,
            "status_updates": status_updates,
            "used_seed": used_seed
        }


# Create a singleton instance
workflow_logic_service = WorkflowLogicService()
