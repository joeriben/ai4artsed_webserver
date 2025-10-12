"""
ComfyUI Workflow Generator
Generiert automatisch ComfyUI-Workflows basierend auf Schema-Pipeline-Outputs
"""
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class WorkflowTemplate:
    """Template für einen ComfyUI-Workflow-Typ"""
    name: str
    base_nodes: Dict[str, Any]
    prompt_injection_node: str
    parameter_mappings: Dict[str, str]

class ComfyUIWorkflowGenerator:
    """Generiert ComfyUI-Workflows aus Schema-Pipeline-Outputs"""
    
    def __init__(self, schemas_path: Path):
        self.schemas_path = schemas_path
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Workflow-Templates laden"""
        # SD 3.5 Template definieren (basierend auf Dadaismus-Workflow)
        self.templates["sd35_standard"] = WorkflowTemplate(
            name="sd35_standard",
            base_nodes={
                "3": {
                    "inputs": {
                        "seed": "{{SEED}}",
                        "steps": "{{STEPS}}",
                        "cfg": "{{CFG}}",
                        "sampler_name": "{{SAMPLER}}",
                        "scheduler": "{{SCHEDULER}}",
                        "denoise": 1,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0]
                    },
                    "class_type": "KSampler",
                    "_meta": {"title": "KSampler"}
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "{{CHECKPOINT}}"
                    },
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "Load Checkpoint"}
                },
                "5": {
                    "inputs": {
                        "width": "{{WIDTH}}",
                        "height": "{{HEIGHT}}",
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage",
                    "_meta": {"title": "Empty Latent Image"}
                },
                "6": {
                    "inputs": {
                        "text": "{{PROMPT}}",
                        "clip": ["43", 0]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "CLIP Text Encode (Positive)"}
                },
                "7": {
                    "inputs": {
                        "text": "{{NEGATIVE_PROMPT}}",
                        "clip": ["43", 0]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "CLIP Text Encode (Negative)"}
                },
                "8": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    },
                    "class_type": "VAEDecode",
                    "_meta": {"title": "VAE Decode"}
                },
                "9": {
                    "inputs": {
                        "filename_prefix": "AI4ArtsEd_Schema",
                        "images": ["8", 0]
                    },
                    "class_type": "SaveImage",
                    "_meta": {"title": "Save Image"}
                },
                "43": {
                    "inputs": {
                        "clip_name1": "clip_g.safetensors",
                        "clip_name2": "t5xxl_enconly.safetensors",
                        "type": "sd3",
                        "device": "default"
                    },
                    "class_type": "DualCLIPLoader",
                    "_meta": {"title": "DualCLIPLoader"}
                }
            },
            prompt_injection_node="6",
            parameter_mappings={
                "prompt": "{{PROMPT}}",
                "negative_prompt": "{{NEGATIVE_PROMPT}}",
                "width": "{{WIDTH}}",
                "height": "{{HEIGHT}}",
                "steps": "{{STEPS}}",
                "cfg": "{{CFG}}",
                "sampler": "{{SAMPLER}}",
                "scheduler": "{{SCHEDULER}}",
                "seed": "{{SEED}}",
                "checkpoint": "{{CHECKPOINT}}"
            }
        )
        
        # Stable Audio Template (ComfyUI Custom Nodes)
        self.templates["stable_audio_standard"] = WorkflowTemplate(
            name="stable_audio_standard",
            base_nodes={
                "93": {
                    "inputs": {
                        "text": "{{NEGATIVE_PROMPT}}",
                        "clip": ["102", 0]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "CLIP Text Encode (Negative)"}
                },
                "94": {
                    "inputs": {
                        "filename_prefix": "AI4ArtsEd_Audio",
                        "quality": "320k",
                        "audioUI": "",
                        "audio": ["100", 0]
                    },
                    "class_type": "SaveAudioMP3",
                    "_meta": {"title": "Save Audio (MP3)"}
                },
                "96": {
                    "inputs": {
                        "ckpt_name": "OfficialStableDiffusion/stableaudio_model.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "Load Checkpoint"}
                },
                "97": {
                    "inputs": {
                        "seconds": "{{DURATION}}",
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentAudio",
                    "_meta": {"title": "EmptyLatentAudio"}
                },
                "98": {
                    "inputs": {
                        "text": "{{PROMPT}}",
                        "clip": ["102", 0]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "CLIP Text Encode (Positive)"}
                },
                "99": {
                    "inputs": {
                        "seconds_start": 0,
                        "seconds_total": "{{DURATION}}",
                        "positive": ["98", 0],
                        "negative": ["93", 0]
                    },
                    "class_type": "ConditioningStableAudio",
                    "_meta": {"title": "ConditioningStableAudio"}
                },
                "100": {
                    "inputs": {
                        "samples": ["101", 0],
                        "vae": ["96", 2]
                    },
                    "class_type": "VAEDecodeAudio",
                    "_meta": {"title": "VAEDecodeAudio"}
                },
                "101": {
                    "inputs": {
                        "seed": "{{SEED}}",
                        "steps": "{{STEPS}}",
                        "cfg": "{{CFG}}",
                        "sampler_name": "euler",
                        "scheduler": "simple",
                        "denoise": 0.9,
                        "model": ["96", 0],
                        "positive": ["99", 0],
                        "negative": ["99", 1],
                        "latent_image": ["97", 0]
                    },
                    "class_type": "KSampler",
                    "_meta": {"title": "KSampler"}
                },
                "102": {
                    "inputs": {
                        "clip_name": "CLIP_stableaudio_model.safetensors",
                        "type": "stable_audio",
                        "device": "default"
                    },
                    "class_type": "CLIPLoader",
                    "_meta": {"title": "Load CLIP"}
                }
            },
            prompt_injection_node="98",
            parameter_mappings={
                "prompt": "{{PROMPT}}",
                "negative_prompt": "{{NEGATIVE_PROMPT}}",
                "duration": "{{DURATION}}",
                "steps": "{{STEPS}}",
                "cfg": "{{CFG}}",
                "seed": "{{SEED}}"
            }
        )
    
    def generate_workflow(
        self,
        template_name: str,
        schema_output: str,
        parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """ComfyUI-Workflow generieren"""
        
        template = self.templates.get(template_name)
        if not template:
            logger.error(f"Template '{template_name}' nicht gefunden")
            return None
        
        # Default-Parameter je nach Template
        if template_name == "stable_audio_standard":
            default_params = {
                "PROMPT": schema_output,
                "NEGATIVE_PROMPT": "worst quality, bad audio, high harmonic distortion",
                "DURATION": 47.0,  # Float (max 47s)
                "STEPS": 150,  # Integer
                "CFG": 7.0,  # Float
                "SEED": self._generate_seed()  # Integer
            }
        else:
            # SD 3.5 Default-Parameter
            default_params = {
                "PROMPT": schema_output,
                "NEGATIVE_PROMPT": "watermark, text, bad quality",
                "WIDTH": 1024,  # Integer
                "HEIGHT": 1024,  # Integer
                "STEPS": 25,  # Integer
                "CFG": 5.5,  # Float
                "SAMPLER": "euler",
                "SCHEDULER": "normal",
                "SEED": self._generate_seed(),  # Integer
                "CHECKPOINT": "OfficialStableDiffusion/sd3.5_large.safetensors"
            }
        
        # Parameter mit übergebenen Werten überschreiben (Typ-Konvertierung)
        final_params = {**default_params}
        for key, value in parameters.items():
            # Typ-Konvertierung für numerische Parameter
            if key in ["WIDTH", "HEIGHT", "STEPS", "SEED"]:
                final_params[key] = int(value) if not isinstance(value, int) else value
            elif key in ["CFG", "DURATION"]:
                final_params[key] = float(value) if not isinstance(value, float) else value
            else:
                final_params[key] = value
        
        # Workflow generieren
        workflow = {}
        for node_id, node_data in template.base_nodes.items():
            workflow[node_id] = self._process_node(node_data, final_params)
        
        logger.info(f"ComfyUI-Workflow '{template_name}' generiert mit {len(workflow)} Nodes")
        return workflow
    
    def _process_node(self, node_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Node-Daten verarbeiten und Platzhalter ersetzen (mit Typ-Erhaltung!)"""
        import copy
        node = copy.deepcopy(node_data)
        
        # Rekursiv durch alle Werte gehen und Platzhalter ersetzen
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                # Check if this is a pure placeholder (entire string)
                for param, value in parameters.items():
                    placeholder = f"{{{{{param}}}}}"
                    if obj == placeholder:
                        # Replace entire value with original type preserved!
                        return value
                    elif placeholder in obj:
                        # Partial replacement - must remain string
                        obj = obj.replace(placeholder, str(value))
                return obj
            else:
                return obj
        
        return replace_placeholders(node)
    
    def _generate_seed(self) -> int:
        """Zufälligen Seed generieren"""
        import random
        return random.randint(1, 2**32 - 1)
    
    def get_available_templates(self) -> List[str]:
        """Verfügbare Templates auflisten"""
        return list(self.templates.keys())

# Singleton-Instanz
workflow_generator = None

def get_workflow_generator(schemas_path: Path) -> ComfyUIWorkflowGenerator:
    """Workflow-Generator Singleton"""
    global workflow_generator
    if workflow_generator is None:
        workflow_generator = ComfyUIWorkflowGenerator(schemas_path)
    return workflow_generator
