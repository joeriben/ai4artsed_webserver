"""
Model Availability Service - API-Based Detection

Queries ComfyUI's /object_info endpoint to determine which models are installed.
This is the authoritative source - ComfyUI knows what models it has loaded.

IMPORTANT: This replaces file-based detection which fundamentally cannot work
because ModelPathResolver has incomplete knowledge of model locations.
"""

import aiohttp
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelAvailabilityService:
    """
    Service to check ComfyUI model availability via API.

    Uses ComfyUI's /object_info endpoint to get the authoritative list
    of available models, then compares against config requirements.
    """

    # Cache for ComfyUI model queries (5-minute TTL)
    _cache: Dict[str, Any] = {
        "comfyui_models": None,
        "timestamp": None,
        "ttl_seconds": 300  # 5 minutes
    }

    def __init__(self, comfyui_base_url: Optional[str] = None):
        """
        Initialize the model availability service.

        Args:
            comfyui_base_url: Base URL for ComfyUI API (default: from config.py)
        """
        if comfyui_base_url is None:
            from config import COMFYUI_PORT
            comfyui_base_url = f"http://127.0.0.1:{COMFYUI_PORT}"

        self.comfyui_base_url = comfyui_base_url
        self.config_dir = Path(__file__).parent.parent.parent / "schemas" / "configs" / "output"
        self.chunk_dir = Path(__file__).parent.parent.parent / "schemas" / "chunks"

        logger.info(f"[MODEL_AVAILABILITY] Initialized with ComfyUI at {comfyui_base_url}")

    def _is_cache_valid(self) -> bool:
        """Check if the cached ComfyUI models data is still valid."""
        if not self._cache["timestamp"]:
            return False
        elapsed = time.time() - self._cache["timestamp"]
        return elapsed < self._cache["ttl_seconds"]

    def _get_cache_age(self) -> int:
        """Get the age of the cache in seconds."""
        if not self._cache["timestamp"]:
            return 0
        return int(time.time() - self._cache["timestamp"])

    async def get_comfyui_models(self, force_refresh: bool = False) -> Dict[str, List[str]]:
        """
        Query ComfyUI's /object_info endpoint to get available models.

        Args:
            force_refresh: If True, bypass cache and query fresh

        Returns:
            Dictionary with model lists:
            {
                "checkpoints": ["flux2_dev_fp8mixed.safetensors", ...],
                "unets": ["qwen_image_fp8_e4m3fn.safetensors", ...],
                "vaes": ["flux2-vae.safetensors", ...],
                "clips": ["mistral_3_small_flux2_fp8.safetensors", ...]
            }

        Raises:
            aiohttp.ClientError: If ComfyUI is unreachable or returns error
        """
        # Check cache first
        if not force_refresh and self._is_cache_valid():
            logger.info(f"[MODEL_AVAILABILITY] Using cached ComfyUI models (age: {self._get_cache_age()}s)")
            return self._cache["comfyui_models"]

        logger.info(f"[MODEL_AVAILABILITY] Querying ComfyUI at {self.comfyui_base_url}/object_info")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.comfyui_base_url}/object_info",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise aiohttp.ClientError(
                            f"ComfyUI returned status {response.status}: {error_text}"
                        )

                    data = await response.json()

                    # Extract model lists from loader node definitions
                    models = {
                        "checkpoints": [],
                        "unets": [],
                        "vaes": [],
                        "clips": []
                    }

                    # CheckpointLoaderSimple → ckpt_name
                    if "CheckpointLoaderSimple" in data:
                        ckpt_field = data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"]
                        if isinstance(ckpt_field, list) and len(ckpt_field) > 0:
                            models["checkpoints"] = ckpt_field[0]

                    # UNETLoader → unet_name
                    if "UNETLoader" in data:
                        unet_field = data["UNETLoader"]["input"]["required"]["unet_name"]
                        if isinstance(unet_field, list) and len(unet_field) > 0:
                            models["unets"] = unet_field[0]

                    # VAELoader → vae_name
                    if "VAELoader" in data:
                        vae_field = data["VAELoader"]["input"]["required"]["vae_name"]
                        if isinstance(vae_field, list) and len(vae_field) > 0:
                            models["vaes"] = vae_field[0]

                    # CLIPLoader → clip_name
                    if "CLIPLoader" in data:
                        clip_field = data["CLIPLoader"]["input"]["required"]["clip_name"]
                        if isinstance(clip_field, list) and len(clip_field) > 0:
                            models["clips"] = clip_field[0]

                    logger.info(
                        f"[MODEL_AVAILABILITY] Found {len(models['checkpoints'])} checkpoints, "
                        f"{len(models['unets'])} UNETs, {len(models['vaes'])} VAEs, "
                        f"{len(models['clips'])} CLIPs"
                    )

                    # Update cache
                    self._cache["comfyui_models"] = models
                    self._cache["timestamp"] = time.time()

                    return models

        except aiohttp.ClientError as e:
            logger.error(f"[MODEL_AVAILABILITY] ComfyUI unreachable: {e}")
            raise
        except Exception as e:
            logger.error(f"[MODEL_AVAILABILITY] Error querying ComfyUI: {e}")
            raise

    def _extract_chunk_requirements(self, chunk_path: Path) -> List[Dict[str, str]]:
        """
        Parse a chunk file to extract required models from workflow JSON.

        Args:
            chunk_path: Path to chunk JSON file

        Returns:
            List of required models:
            [
                {"loader_type": "checkpoint", "model_name": "flux2_dev_fp8mixed.safetensors"},
                {"loader_type": "clip", "model_name": "mistral_3_small_flux2_fp8.safetensors"},
                ...
            ]
        """
        try:
            with open(chunk_path, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)

            workflow = chunk_data.get("workflow", {})
            if not workflow:
                logger.warning(f"[MODEL_AVAILABILITY] No workflow found in {chunk_path.name}")
                return []

            requirements = []

            # Iterate through workflow nodes
            for node_id, node_data in workflow.items():
                class_type = node_data.get("class_type")
                inputs = node_data.get("inputs", {})

                # CheckpointLoaderSimple
                if class_type == "CheckpointLoaderSimple":
                    if "ckpt_name" in inputs:
                        requirements.append({
                            "loader_type": "checkpoint",
                            "model_name": inputs["ckpt_name"]
                        })

                # UNETLoader
                elif class_type == "UNETLoader":
                    if "unet_name" in inputs:
                        requirements.append({
                            "loader_type": "unet",
                            "model_name": inputs["unet_name"]
                        })

                # VAELoader
                elif class_type == "VAELoader":
                    if "vae_name" in inputs:
                        requirements.append({
                            "loader_type": "vae",
                            "model_name": inputs["vae_name"]
                        })

                # CLIPLoader
                elif class_type == "CLIPLoader":
                    if "clip_name" in inputs:
                        requirements.append({
                            "loader_type": "clip",
                            "model_name": inputs["clip_name"]
                        })

                # DualCLIPLoader
                elif class_type == "DualCLIPLoader":
                    if "clip_name1" in inputs:
                        requirements.append({
                            "loader_type": "clip",
                            "model_name": inputs["clip_name1"]
                        })
                    if "clip_name2" in inputs:
                        requirements.append({
                            "loader_type": "clip",
                            "model_name": inputs["clip_name2"]
                        })

                # TripleCLIPLoader
                elif class_type == "TripleCLIPLoader":
                    if "clip_name1" in inputs:
                        requirements.append({
                            "loader_type": "clip",
                            "model_name": inputs["clip_name1"]
                        })
                    if "clip_name2" in inputs:
                        requirements.append({
                            "loader_type": "clip",
                            "model_name": inputs["clip_name2"]
                        })
                    if "clip_name3" in inputs:
                        requirements.append({
                            "loader_type": "clip",
                            "model_name": inputs["clip_name3"]
                        })

            return requirements

        except FileNotFoundError:
            logger.error(f"[MODEL_AVAILABILITY] Chunk file not found: {chunk_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"[MODEL_AVAILABILITY] Invalid JSON in {chunk_path.name}: {e}")
            return []
        except Exception as e:
            logger.error(f"[MODEL_AVAILABILITY] Error parsing chunk {chunk_path.name}: {e}")
            return []

    async def check_config_availability(self, config_id: str) -> bool:
        """
        Check if all required models for a config are available.

        Args:
            config_id: Config ID (e.g., "flux2", "sd35_large")

        Returns:
            True if all required models are available, False otherwise
        """
        config_path = self.config_dir / f"{config_id}.json"

        try:
            # Load config
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Skip hidden configs (incomplete stubs)
            if config_data.get("display", {}).get("hidden"):
                return True

            # Check if this is a ComfyUI backend
            backend_type = config_data.get("meta", {}).get("backend_type")
            if backend_type and backend_type != "comfyui":
                # Non-ComfyUI backends (OpenAI, OpenRouter, etc.) are always available
                logger.info(f"[MODEL_AVAILABILITY] {config_id}: Non-ComfyUI backend ({backend_type}), marking available")
                return True

            # Extract OUTPUT_CHUNK reference
            output_chunk = config_data.get("parameters", {}).get("OUTPUT_CHUNK")
            if not output_chunk:
                logger.warning(f"[MODEL_AVAILABILITY] {config_id}: No OUTPUT_CHUNK found")
                return False

            # Load chunk and extract requirements
            chunk_path = self.chunk_dir / f"{output_chunk}.json"
            requirements = self._extract_chunk_requirements(chunk_path)

            if not requirements:
                logger.warning(f"[MODEL_AVAILABILITY] {config_id}: No model requirements found in chunk {output_chunk}")
                # If no requirements, assume available (might be a non-model chunk)
                return True

            # Get available models from ComfyUI
            available_models = await self.get_comfyui_models()

            # Check each requirement
            for req in requirements:
                loader_type = req["loader_type"]
                model_name = req["model_name"]

                # Map loader_type to the correct model list
                if loader_type == "checkpoint":
                    model_list = available_models["checkpoints"]
                elif loader_type == "unet":
                    model_list = available_models["unets"]
                elif loader_type == "vae":
                    model_list = available_models["vaes"]
                elif loader_type == "clip":
                    model_list = available_models["clips"]
                else:
                    logger.warning(f"[MODEL_AVAILABILITY] {config_id}: Unknown loader type '{loader_type}'")
                    continue

                # Check if model exists in ComfyUI's list
                if model_name not in model_list:
                    logger.info(
                        f"[MODEL_AVAILABILITY] {config_id}: Missing {loader_type} model '{model_name}'"
                    )
                    return False

            logger.info(f"[MODEL_AVAILABILITY] {config_id}: All models available")
            return True

        except FileNotFoundError:
            logger.error(f"[MODEL_AVAILABILITY] Config not found: {config_path}")
            return False
        except Exception as e:
            logger.error(f"[MODEL_AVAILABILITY] Error checking {config_id}: {e}")
            return False

    async def check_all_configs(self) -> Dict[str, bool]:
        """
        Check availability for all output configs.

        Returns:
            Dictionary mapping config_id to availability:
            {"flux2": true, "sd35_large": true, "wan22_video": false, ...}
        """
        availability = {}

        if not self.config_dir.exists():
            logger.error(f"[MODEL_AVAILABILITY] Config directory not found: {self.config_dir}")
            return availability

        # List all config files
        config_files = list(self.config_dir.glob("*.json"))
        logger.info(f"[MODEL_AVAILABILITY] Checking {len(config_files)} configs...")

        # Check each config
        for config_file in config_files:
            config_id = config_file.stem
            try:
                is_available = await self.check_config_availability(config_id)
                availability[config_id] = is_available
            except Exception as e:
                logger.error(f"[MODEL_AVAILABILITY] Error checking {config_id}: {e}")
                availability[config_id] = False

        available_count = sum(1 for v in availability.values() if v)
        logger.info(
            f"[MODEL_AVAILABILITY] Result: {available_count}/{len(availability)} configs available"
        )

        return availability
