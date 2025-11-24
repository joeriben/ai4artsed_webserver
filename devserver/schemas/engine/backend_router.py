"""
Backend-Router: Multi-Backend-Support für Schema-Pipelines
"""
import logging
from typing import Dict, Any, Optional, AsyncGenerator, Tuple, Union, List
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class BackendType(Enum):
    """Backend-Typen"""
    OLLAMA = "ollama"
    OPENROUTER = "openrouter" 
    COMFYUI = "comfyui"

@dataclass
class BackendRequest:
    """Request für Backend-Verarbeitung"""
    backend_type: BackendType
    model: str
    prompt: str
    parameters: Dict[str, Any]
    stream: bool = False

@dataclass 
class BackendResponse:
    """Response von Backend"""
    success: bool
    content: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BackendRouter:
    """Router für verschiedene KI-Backends"""
    
    def __init__(self):
        self.backends: Dict[BackendType, Any] = {}
        self._initialized = False
    
    def initialize(self, ollama_service=None, workflow_logic_service=None, comfyui_service=None):
        """Router mit Legacy-Services initialisieren"""
        if ollama_service:
            self.backends[BackendType.OLLAMA] = ollama_service
            logger.info("Ollama-Backend registriert")
        
        if comfyui_service:
            self.backends[BackendType.COMFYUI] = comfyui_service
            logger.info("ComfyUI-Backend registriert")
            
        self._initialized = True
        logger.info(f"Backend-Router initialisiert mit {len(self.backends)} Backends")
    
    async def process_request(self, request: BackendRequest) -> Union[BackendResponse, AsyncGenerator[str, None]]:
        """Request an entsprechendes Backend weiterleiten"""
        try:
            # IMPORTANT: Detect actual backend from model prefix, not template backend_type
            # This allows execution_mode to override the template's backend_type
            actual_backend = self._detect_backend_from_model(request.model, request.backend_type)
            
            # Schema-Pipelines: Ollama/OpenRouter über Prompt Interception Engine
            if actual_backend in [BackendType.OLLAMA, BackendType.OPENROUTER]:
                # Create modified request with detected backend for proper routing
                modified_request = BackendRequest(
                    backend_type=actual_backend,
                    model=request.model,
                    prompt=request.prompt,
                    parameters=request.parameters,
                    stream=request.stream
                )
                return await self._process_prompt_interception_request(modified_request)
            elif actual_backend == BackendType.COMFYUI:
                # ComfyUI braucht kein registriertes Backend - verwendet direkt ComfyUI-Client
                return await self._process_comfyui_request(None, request)
            else:
                return BackendResponse(
                    success=False,
                    content="",
                    error=f"Backend-Typ {actual_backend.value} nicht implementiert"
                )
        except Exception as e:
            logger.error(f"Fehler bei Backend-Verarbeitung: {e}")
            return BackendResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    def _detect_backend_from_model(self, model: str, fallback_backend: BackendType) -> BackendType:
        """
        Detect backend from model prefix
        This allows execution_mode to override template's backend_type

        Args:
            model: Model string (may have local/ or openrouter/ prefix)
            fallback_backend: Fallback if no prefix detected

        Returns:
            Detected backend type
        """
        # Empty model or prefix-only (e.g., "local/" with no model name) → use fallback
        # This is important for Proxy-Chunks (output_image) which have empty model
        if not model or model in ["local/", "openrouter/", ""]:
            logger.debug(f"[BACKEND-DETECT] Model '{model}' empty or prefix-only → {fallback_backend.value} (fallback)")
            return fallback_backend

        if model.startswith("openrouter/"):
            logger.debug(f"[BACKEND-DETECT] Model '{model}' → OPENROUTER")
            return BackendType.OPENROUTER
        elif model.startswith("local/"):
            logger.debug(f"[BACKEND-DETECT] Model '{model}' → OLLAMA")
            return BackendType.OLLAMA
        else:
            # No prefix, use fallback
            logger.debug(f"[BACKEND-DETECT] Model '{model}' → {fallback_backend.value} (fallback)")
            return fallback_backend
    
    async def _process_prompt_interception_request(self, request: BackendRequest) -> BackendResponse:
        """Schema-Pipeline-Request über Prompt Interception Engine"""
        try:
            from .prompt_interception_engine import PromptInterceptionEngine, PromptInterceptionRequest
            
            # Parse Template+Config zu Task+Context+Prompt
            input_prompt, input_context, style_prompt = self._parse_template_to_prompt_format(request.prompt)
            
            # Model already has prefix from ModelSelector - use as-is!
            model = request.model
            logger.info(f"[BACKEND] Using model: {model}")
            
            # Prompt Interception Request
            pi_engine = PromptInterceptionEngine()
            pi_request = PromptInterceptionRequest(
                input_prompt=input_prompt,
                input_context=input_context,
                style_prompt=style_prompt,
                model=model,
                debug=request.parameters.get('debug', False),
                unload_model=request.parameters.get('unload_model', False)
            )
            
            # Engine-Request ausführen
            pi_response = await pi_engine.process_request(pi_request)

            if pi_response.success:
                # Use backend from modified_request (already set correctly in process_request)
                # Note: request here is the modified_request which has backend_type=actual_backend
                return BackendResponse(
                    success=True,
                    content=pi_response.output_str,
                    metadata={
                        'model_used': pi_response.model_used,
                        'backend_type': request.backend_type.value
                    }
                )
            else:
                return BackendResponse(
                    success=False,
                    content="",
                    error=pi_response.error
                )
                
        except Exception as e:
            logger.error(f"Prompt Interception Engine Fehler: {e}")
            return BackendResponse(
                success=False,
                content="",
                error=f"Prompt Interception Engine Fehler: {str(e)}"
            )
    
    def _parse_template_to_prompt_format(self, template_result: str) -> tuple[str, str, str]:
        """Parse Template-Result zu Task+Context+Prompt Format"""
        # Template-Result ist bereits fertig aufgebaut aus ChunkBuilder
        # Für Schema-Pipelines: Template enthält INSTRUCTIONS + INPUT_TEXT/PREVIOUS_OUTPUT
        
        # Einfache Heuristik: Teile bei ersten Doppel-Newlines
        parts = template_result.split('\n\n', 2)
        
        if len(parts) >= 3:
            # Task: Instructions, Context: leer, Prompt: Text
            style_prompt = parts[0]
            input_context = ""  
            input_prompt = parts[2] if len(parts) > 2 else parts[1]
        elif len(parts) == 2:
            # Instructions + Text
            style_prompt = parts[0]
            input_context = ""
            input_prompt = parts[1]
        else:
            # Nur Text
            style_prompt = ""
            input_context = ""
            input_prompt = template_result
        
        return input_prompt, input_context, style_prompt
    
    async def _process_ollama_request(self, ollama_service, request: BackendRequest) -> BackendResponse:
        """Ollama-Request verarbeiten - Legacy-Service nutzen"""
        try:
            # Legacy ollama_service.py wiederverwenden
            if hasattr(ollama_service, 'generate_completion'):
                result = await ollama_service.generate_completion(
                    model=request.model,
                    prompt=request.prompt,
                    **request.parameters
                )
            elif hasattr(ollama_service, 'generate'):
                result = await ollama_service.generate(
                    model=request.model,
                    prompt=request.prompt,
                    **request.parameters
                )
            else:
                # Fallback auf direkte API-Calls
                result = await ollama_service.call_api(
                    model=request.model,
                    prompt=request.prompt,
                    **request.parameters
                )
            
            return BackendResponse(
                success=True,
                content=result.get('response', ''),
                metadata=result
            )
            
        except Exception as e:
            logger.error(f"Ollama-Backend-Fehler: {e}")
            return BackendResponse(
                success=False,
                content="",
                error=f"Ollama-Service-Fehler: {str(e)}"
            )
    
    async def _process_direct_request(self, workflow_service, request: BackendRequest) -> BackendResponse:
        """Direct-Request verarbeiten - Legacy workflow_logic_service nutzen"""
        try:
            # Legacy workflow_logic_service.py wiederverwenden
            result = await workflow_service.process_text(
                text=request.prompt,
                parameters=request.parameters
            )
            
            return BackendResponse(
                success=True,
                content=result.get('processed_text', request.prompt),
                metadata=result
            )
            
        except Exception as e:
            logger.error(f"Direct-Backend-Fehler: {e}")
            return BackendResponse(
                success=False,
                content="",
                error=f"Workflow-Service-Fehler: {str(e)}"
            )
    
    async def _process_comfyui_request(self, comfyui_service, request: BackendRequest) -> BackendResponse:
        """ComfyUI-Request verarbeiten mit Output-Chunks oder Legacy-Workflow-Generator"""
        try:
            # Schema-Pipeline-Output ist der optimierte Prompt
            schema_output = request.prompt

            # Check if we have an output_chunk specified
            output_chunk_name = request.parameters.get('output_chunk')

            if output_chunk_name:
                # Load chunk to check type
                chunk = self._load_output_chunk(output_chunk_name)

                if not chunk:
                    return BackendResponse(
                        success=False,
                        content="",
                        error=f"Output-Chunk '{output_chunk_name}' not found"
                    )

                # Route based on chunk type
                if chunk.get('type') == 'api_output_chunk':
                    # API-based generation (OpenRouter, Replicate, etc.)
                    return await self._process_api_output_chunk(output_chunk_name, schema_output, request.parameters, chunk)
                else:
                    # ComfyUI workflow-based generation
                    return await self._process_output_chunk(output_chunk_name, schema_output, request.parameters)
            else:
                # LEGACY PATH: Use deprecated comfyui_workflow_generator
                # This will be removed after all chunks are migrated
                logger.warning("Using deprecated comfyui_workflow_generator - migrate to Output-Chunks!")
                return await self._process_comfyui_legacy(schema_output, request.parameters)

        except Exception as e:
            logger.error(f"ComfyUI-Backend-Fehler: {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"ComfyUI-Service-Fehler: {str(e)}"
            )

    async def _process_output_chunk(self, chunk_name: str, prompt: str, parameters: Dict[str, Any]) -> BackendResponse:
        """Process Output-Chunk: Route based on media type

        - Images: Use SwarmUI /API/GenerateText2Image (simple, fast)
        - Audio/Video: Use custom workflow submission via /ComfyBackendDirect
        """
        try:
            # 1. Load Output-Chunk from JSON
            chunk = self._load_output_chunk(chunk_name)
            if not chunk:
                return BackendResponse(
                    success=False,
                    content="",
                    error=f"Output-Chunk '{chunk_name}' not found"
                )

            media_type = chunk.get('media_type', 'image')
            logger.info(f"Loaded Output-Chunk: {chunk_name} ({media_type} media)")

            # 2. Route based on media type
            if media_type == 'image':
                # Use SwarmUI's simple Text2Image API
                return await self._process_image_chunk_simple(chunk_name, prompt, parameters, chunk)
            else:
                # For audio/video: use custom workflow submission
                return await self._process_workflow_chunk(chunk_name, prompt, parameters, chunk)

        except Exception as e:
            logger.error(f"Error processing Output-Chunk '{chunk_name}': {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"Output-Chunk processing error: {str(e)}"
            )

    async def _process_image_chunk_simple(self, chunk_name: str, prompt: str, parameters: Dict[str, Any], chunk: Dict[str, Any]) -> BackendResponse:
        """Process image chunks using SwarmUI's /API/GenerateText2Image endpoint"""
        try:
            # Extract parameters from input_mappings
            import sys
            from pathlib import Path
            devserver_path = Path(__file__).parent.parent.parent
            if str(devserver_path) not in sys.path:
                sys.path.insert(0, str(devserver_path))

            input_mappings = chunk['input_mappings']
            input_data = {'prompt': prompt, **parameters}

            # Build SwarmUI API parameters (IMAGE-ONLY)
            import random

            # Get model from checkpoint mapping
            model = parameters.get('checkpoint') or input_mappings.get('checkpoint', {}).get('default', 'sd3.5_large')
            # If model has .safetensors extension, keep the full path, otherwise use as-is
            if not model.endswith('.safetensors'):
                model = f"{model}.safetensors"

            # Get prompt (positive)
            positive_prompt = input_data.get('prompt', prompt)

            # Get negative prompt
            negative_prompt = input_data.get('negative_prompt') or input_mappings.get('negative_prompt', {}).get('default', '')

            # Get dimensions (only for image chunks - audio/video don't need dimensions)
            media_type = chunk.get('media_type', 'image')
            if media_type == 'image':
                width = int(input_data.get('width') or input_mappings.get('width', {}).get('default', 1024))
                height = int(input_data.get('height') or input_mappings.get('height', {}).get('default', 1024))
            else:
                # Audio/video chunks don't need dimensions - skip parsing
                width = None
                height = None

            # Get generation parameters
            steps = int(input_data.get('steps') or input_mappings.get('steps', {}).get('default', 25))
            cfg_scale = float(input_data.get('cfg') or input_mappings.get('cfg', {}).get('default', 7.0))

            # Get seed (generate random if needed)
            seed = input_data.get('seed') or input_mappings.get('seed', {}).get('default', 'random')
            if seed == 'random' or seed == -1:
                seed = random.randint(0, 2**32 - 1)
                logger.info(f"Generated random seed: {seed}")
            else:
                seed = int(seed)

            # 3. Get SwarmUI client
            from my_app.services.swarmui_client import get_swarmui_client

            client = get_swarmui_client()
            is_healthy = await client.health_check()

            if not is_healthy:
                logger.warning("SwarmUI server not reachable")
                return BackendResponse(
                    success=False,
                    content="",
                    error="SwarmUI server not available"
                )

            # 4. Generate image using SwarmUI API
            logger.info(f"[SWARMUI] Generating image with model={model}, steps={steps}, size={width}x{height}")
            image_paths = await client.generate_image(
                prompt=positive_prompt,
                model=model,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg_scale=cfg_scale,
                seed=seed
            )

            if not image_paths:
                return BackendResponse(
                    success=False,
                    content="",
                    error="SwarmUI failed to generate image"
                )

            # 5. Return image paths directly (no polling needed!)
            logger.info(f"[SWARMUI] ✓ Generated {len(image_paths)} image(s)")
            logger.info(f"[SWARMUI-DEBUG] image_paths value: {image_paths}")

            return BackendResponse(
                success=True,
                content="swarmui_generated",
                metadata={
                    'chunk_name': chunk_name,
                    'media_type': chunk.get('media_type'),
                    'image_paths': image_paths,
                    'swarmui_available': True,
                    'seed': seed,
                    'model': model,
                    'parameters': {
                        'width': width,
                        'height': height,
                        'steps': steps,
                        'cfg_scale': cfg_scale
                    }
                }
            )

        except Exception as e:
            logger.error(f"Error processing Output-Chunk '{chunk_name}': {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"Output-Chunk processing error: {str(e)}"
            )

    async def _process_workflow_chunk(self, chunk_name: str, prompt: str, parameters: Dict[str, Any], chunk: Dict[str, Any]) -> BackendResponse:
        """Process audio/video chunks using custom ComfyUI workflows via SwarmUI"""
        try:
            # 1. Load workflow from chunk
            workflow = chunk.get('workflow')
            if not workflow:
                return BackendResponse(
                    success=False,
                    content="",
                    error=f"No workflow found in chunk '{chunk_name}'"
                )

            media_type = chunk.get('media_type', 'unknown')
            logger.info(f"[WORKFLOW-CHUNK] Processing {media_type} chunk: {chunk_name}")

            # 2. Detect mapping format and apply input mappings
            input_mappings = chunk.get('input_mappings', {})
            input_data = {'prompt': prompt, **parameters}

            # Check if first mapping has 'node_id' to determine format
            first_mapping = next(iter(input_mappings.values()), {})
            if 'node_id' in first_mapping:
                # Node-based format: use existing _apply_input_mappings()
                logger.info(f"[WORKFLOW-CHUNK] Using node-based mappings")
                workflow, generated_seed = self._apply_input_mappings(workflow, input_mappings, input_data)
            else:
                # Template-based format: do JSON string replacement
                logger.info(f"[WORKFLOW-CHUNK] Using template-based mappings")
                workflow_str = json.dumps(workflow)
                generated_seed = None

                for key, mapping in input_mappings.items():
                    value = input_data.get(key)
                    if value is None:
                        value = mapping.get('default', '')

                    # Special handling for "random" seed
                    if value == "random" and key == "seed":
                        import random
                        value = random.randint(0, 2**32 - 1)
                        generated_seed = value
                        logger.info(f"Generated random seed: {generated_seed}")

                    # Replace template placeholders like {{PROMPT}}
                    placeholder = mapping.get('template', f'{{{{{key.upper()}}}}}')
                    workflow_str = workflow_str.replace(placeholder, str(value))
                    logger.debug(f"Replaced '{placeholder}' with '{str(value)[:50]}...'")

                workflow = json.loads(workflow_str)

            # 3. Get SwarmUI client
            import sys
            from pathlib import Path
            devserver_path = Path(__file__).parent.parent.parent
            if str(devserver_path) not in sys.path:
                sys.path.insert(0, str(devserver_path))

            from my_app.services.swarmui_client import get_swarmui_client

            client = get_swarmui_client()
            is_healthy = await client.health_check()

            if not is_healthy:
                logger.warning("SwarmUI server not reachable")
                return BackendResponse(
                    success=False,
                    content="",
                    error="SwarmUI server not available"
                )

            # 4. Submit workflow via unified swarmui_client
            logger.info(f"[WORKFLOW-CHUNK] Submitting {media_type} workflow to SwarmUI")
            prompt_id = await client.submit_workflow(workflow)

            if not prompt_id:
                return BackendResponse(
                    success=False,
                    content="",
                    error="Failed to submit workflow to SwarmUI"
                )

            logger.info(f"[WORKFLOW-CHUNK] Workflow submitted: {prompt_id}")

            # 5. Wait for completion
            timeout = parameters.get('timeout', 300)
            history = await client.wait_for_completion(prompt_id, timeout=timeout)

            if not history:
                return BackendResponse(
                    success=False,
                    content="",
                    error="Timeout or error waiting for workflow completion"
                )

            logger.info(f"[WORKFLOW-CHUNK] Workflow completed: {prompt_id}")

            # 6. Extract media files from known ComfyUI output directory
            # NOTE: ComfyUI history parsing is unreliable for non-image media
            # Use direct filesystem listing instead
            import os
            import glob

            if media_type == 'audio':
                output_dir = '/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio'
            elif media_type == 'video':
                output_dir = '/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/video'
            else:
                logger.warning(f"Unknown media type '{media_type}', using audio directory")
                output_dir = '/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio'

            # Get most recent file from output directory
            filesystem_path = None
            if os.path.exists(output_dir):
                files = glob.glob(f"{output_dir}/*.{'mp3' if media_type == 'audio' else 'mp4'}")
                if files:
                    most_recent = max(files, key=os.path.getmtime)
                    filesystem_path = most_recent
                    logger.info(f"[WORKFLOW-CHUNK] Found {media_type} file: {filesystem_path}")

            if not filesystem_path:
                logger.error(f"[WORKFLOW-CHUNK] No {media_type} files found in {output_dir}")
                return BackendResponse(
                    success=False,
                    content="",
                    error=f"No {media_type} files found in workflow output"
                )

            # 7. Return filesystem path for direct copy (no downloading needed)
            # The endpoint handler will copy this file directly to exports/json/{run_id}/
            return BackendResponse(
                success=True,
                content="workflow_generated",
                metadata={
                    'chunk_name': chunk_name,
                    'media_type': media_type,
                    'prompt_id': prompt_id,
                    'filesystem_path': filesystem_path,
                    'swarmui_available': True,
                    'seed': generated_seed,
                    'workflow_completed': True
                }
            )

        except Exception as e:
            logger.error(f"Error processing workflow chunk '{chunk_name}': {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"Workflow chunk processing error: {str(e)}"
            )

    async def _process_api_output_chunk(self, chunk_name: str, prompt: str, parameters: Dict[str, Any], chunk: Dict[str, Any]) -> BackendResponse:
        """Process API-based Output-Chunk (OpenRouter, Replicate, etc.)"""
        try:
            logger.info(f"Processing API Output-Chunk: {chunk_name} ({chunk.get('media_type', 'unknown')} media)")

            # Build API request with deep copy to avoid mutation
            import copy
            api_config = chunk['api_config']
            request_body = copy.deepcopy(api_config['request_body'])

            # Apply input mappings
            for param_name, mapping in chunk['input_mappings'].items():
                field_path = mapping['field']
                value = parameters.get(param_name, prompt if param_name == 'prompt' else mapping.get('default'))

                # Set nested value (e.g., "request_body.messages[1].content")
                self._set_nested_value(request_body, field_path.replace('request_body.', ''), value)

            # Get API key from .key file based on provider
            provider = api_config.get('provider', 'openrouter')
            if provider == 'openai':
                key_file = 'openai_api.key'
                key_name = 'OpenAI'
            else:
                key_file = 'openrouter_api.key'
                key_name = 'OpenRouter'

            api_key = self._load_api_key(key_file)
            if not api_key:
                error_msg = f"{key_name} API key not found. Create '{key_file}' file in devserver root."
                logger.error(error_msg)
                return BackendResponse(success=False, error=error_msg)

            # Build headers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai4artsed.com",
                "X-Title": "AI4ArtsEd DevServer"
            }

            # Make API call
            import aiohttp
            async with aiohttp.ClientSession() as session:
                logger.debug(f"POST {api_config['endpoint']} with model {api_config['model']}")
                async with session.post(
                    api_config['endpoint'],
                    json=request_body,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Debug: Log the response structure
                        logger.debug(f"API Response: {json.dumps(data, indent=2)[:500]}...")

                        # Extract image based on output_mapping type
                        output_mapping = chunk.get('output_mapping', {})
                        mapping_type = output_mapping.get('type', 'chat_completion_with_image')

                        if mapping_type == 'images_api_base64':
                            # OpenAI Images API: extract from data[0].b64_json
                            logger.info(f"[API-OUTPUT] Using Images API extraction")
                            image_data = self._extract_image_from_images_api(data, output_mapping)
                        else:
                            # Chat Completions API: extract from choices[0].message
                            logger.info(f"[API-OUTPUT] Using Chat Completions extraction")
                            image_data = self._extract_image_from_chat_completion(data, output_mapping)

                        if not image_data:
                            logger.error("No image found in API response")
                            return BackendResponse(success=False, content="", error="No image found in response", metadata={})

                        logger.info(f"API generation successful: Generated image data ({len(image_data)} chars)")

                        return BackendResponse(
                            success=True,
                            content=image_data,
                            metadata={
                                'chunk_name': chunk_name,
                                'media_type': chunk['media_type'],
                                'provider': api_config['provider'],
                                'model': api_config['model'],
                                'image_data': image_data
                            }
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        return BackendResponse(success=False, content="", error=f"API error: {response.status}")

        except Exception as e:
            logger.error(f"Error processing API Output-Chunk '{chunk_name}': {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"API Output-Chunk processing error: {str(e)}"
            )

    def _extract_image_from_chat_completion(self, data: Dict, output_mapping: Dict) -> Optional[str]:
        """Extract image URL from chat completion response with multimodal content"""
        try:
            message = data['choices'][0]['message']

            # GPT-5 Image: Check message.images array first
            if 'images' in message and isinstance(message['images'], list) and len(message['images']) > 0:
                first_image = message['images'][0]
                if 'image_url' in first_image and 'url' in first_image['image_url']:
                    return first_image['image_url']['url']

            # Fallback: Check message.content for image_url items
            content = message.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'image_url':
                        return item['image_url']['url']

            return None
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract image from response: {e}")
            return None

    def _extract_image_from_images_api(self, data: Dict, output_mapping: Dict) -> Optional[str]:
        """Extract base64 image data from OpenAI Images API response

        Expected format:
        {
            "created": 1234567890,
            "data": [
                {"b64_json": "base64_image_data"}
            ]
        }
        """
        try:
            extract_path = output_mapping.get('extract_path', 'data[0].b64_json')
            logger.info(f"[IMAGES-API] Extracting from path: {extract_path}")

            # Images API standard response
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                first_image = data['data'][0]
                if 'b64_json' in first_image:
                    b64_data = first_image['b64_json']
                    logger.info(f"[IMAGES-API] Successfully extracted base64 data ({len(b64_data)} chars)")
                    return b64_data

            logger.error(f"[IMAGES-API] No base64 data found in response. Keys: {list(data.keys())}")
            return None
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"[IMAGES-API] Failed to extract image from Images API response: {e}")
            return None

    def _set_nested_value(self, obj: Any, path: str, value: Any):
        """Set nested value in dict or list using path notation (e.g., 'messages[1].content')"""
        import re
        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p]  # Remove empty strings

        current = obj
        for i, part in enumerate(parts[:-1]):
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]

        final_key = parts[-1]
        if final_key.isdigit():
            current[int(final_key)] = value
        else:
            current[final_key] = value

    def _load_api_key(self, key_filename: str) -> Optional[str]:
        """Load API key from .key file in devserver root directory"""
        try:
            # Path to devserver root (3 levels up from this file)
            devserver_root = Path(__file__).parent.parent.parent
            key_path = devserver_root / key_filename

            if not key_path.exists():
                logger.warning(f"API key file not found: {key_path}")
                return None

            with open(key_path, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()

            if not api_key:
                logger.warning(f"API key file is empty: {key_path}")
                return None

            logger.info(f"Loaded API key from {key_filename}")
            return api_key

        except Exception as e:
            logger.error(f"Error reading API key file '{key_filename}': {e}")
            return None

    def _load_output_chunk(self, chunk_name: str) -> Optional[Dict[str, Any]]:
        """Load Output-Chunk from schemas/chunks/ directory"""
        try:
            chunk_path = Path(__file__).parent.parent / "chunks" / f"{chunk_name}.json"

            if not chunk_path.exists():
                logger.error(f"Output-Chunk file not found: {chunk_path}")
                return None

            with open(chunk_path, 'r', encoding='utf-8') as f:
                chunk = json.load(f)

            # Validate it's an Output-Chunk (either 'output_chunk' or 'api_output_chunk')
            chunk_type = chunk.get('type')
            if chunk_type not in ['output_chunk', 'api_output_chunk']:
                logger.error(f"Chunk '{chunk_name}' is not an Output-Chunk (type: {chunk_type})")
                return None

            # Validate required fields based on type
            if chunk_type == 'output_chunk':
                required_fields = ['workflow', 'input_mappings', 'output_mapping', 'backend_type']
            elif chunk_type == 'api_output_chunk':
                required_fields = ['api_config', 'input_mappings', 'output_mapping', 'backend_type']

            missing = [f for f in required_fields if f not in chunk]
            if missing:
                logger.error(f"Output-Chunk '{chunk_name}' missing fields: {missing}")
                return None

            return chunk

        except Exception as e:
            logger.error(f"Error loading Output-Chunk '{chunk_name}': {e}")
            return None

    def _apply_input_mappings(self, workflow: Dict, mappings: Dict[str, Any], input_data: Dict[str, Any]) -> Tuple[Dict, Optional[int]]:
        """Apply input_mappings to workflow - inject prompts and parameters

        Returns:
            Tuple[Dict, Optional[int]]: (modified_workflow, generated_seed)
        """
        import random

        generated_seed = None

        for key, mapping in mappings.items():
            # Get value from input_data, or use default, or use source placeholder
            value = input_data.get(key)

            if value is None:
                # Try default value
                value = mapping.get('default')

            if value is None:
                # Try source placeholder (like {{PREVIOUS_OUTPUT}})
                source = mapping.get('source', '')
                if source == '{{PREVIOUS_OUTPUT}}':
                    value = input_data.get('prompt', '')

            # Special handling for "random" seed
            if value == "random" and key == "seed":
                value = random.randint(0, 2**32 - 1)
                generated_seed = value
                logger.info(f"Generated random seed: {generated_seed}")

            # Apply value to workflow
            if value is not None:
                node_id = mapping['node_id']
                field_path = mapping['field'].split('.')

                # Navigate to the nested field (e.g., "inputs.value" -> workflow[node_id]['inputs']['value'])
                target = workflow.get(node_id, {})
                for part in field_path[:-1]:
                    target = target.setdefault(part, {})

                # Set the final value
                target[field_path[-1]] = value

                logger.debug(f"Mapped '{key}' = '{str(value)[:50]}...' to node {node_id}.{mapping['field']}")

        return workflow, generated_seed

    async def _extract_output_media(self, client, history: Dict, output_mapping: Dict) -> List[Dict[str, Any]]:
        """Extract generated media based on output_mapping"""
        try:
            node_id = output_mapping['node_id']
            media_type = output_mapping['output_type']  # 'image', 'audio', 'video'

            # Use appropriate extraction method based on media_type
            if media_type == 'image':
                return await client.get_generated_images(history)
            elif media_type == 'audio':
                return await client.get_generated_audio(history)
            elif media_type == 'video':
                return await client.get_generated_video(history)
            else:
                logger.warning(f"Unknown media type: {media_type}, using generic extraction")
                return await client.get_generated_images(history)

        except Exception as e:
            logger.error(f"Error extracting output media: {e}")
            return []

    async def _process_comfyui_legacy(self, schema_output: str, parameters: Dict[str, Any]) -> BackendResponse:
        """LEGACY: ComfyUI-Request mit deprecated comfyui_workflow_generator

        NOW USES: SwarmUI client's /ComfyBackendDirect passthrough instead of direct port 7821
        """
        try:
            # Workflow-Template aus Parameters extrahieren
            workflow_template = parameters.get('workflow_template', 'sd35_standard')

            # ComfyUI-Workflow-Generator verwenden (DEPRECATED)
            try:
                from .comfyui_workflow_generator import get_workflow_generator
                # Import relativ zum devserver root
                import sys
                from pathlib import Path
                devserver_path = Path(__file__).parent.parent.parent
                if str(devserver_path) not in sys.path:
                    sys.path.insert(0, str(devserver_path))
                from my_app.services.swarmui_client import get_swarmui_client

                # 1. Workflow generieren
                generator = get_workflow_generator(Path(__file__).parent.parent)
                workflow = generator.generate_workflow(
                    template_name=workflow_template,
                    schema_output=schema_output,
                    parameters=parameters
                )

                if not workflow:
                    return BackendResponse(
                        success=False,
                        content="",
                        error=f"Workflow-Template '{workflow_template}' nicht verfügbar"
                    )

                logger.info(f"ComfyUI-Workflow generiert: {len(workflow)} Nodes für Template '{workflow_template}' (DEPRECATED)")

                # 2. SwarmUI Client holen (now handles ComfyUI via /ComfyBackendDirect)
                client = get_swarmui_client()
                is_healthy = await client.health_check()

                if not is_healthy:
                    logger.warning("SwarmUI/ComfyUI server not reachable, returning workflow only")
                    return BackendResponse(
                        success=True,
                        content="workflow_generated_only",
                        metadata={
                            'workflow_generated': True,
                            'template': workflow_template,
                            'workflow': workflow,
                            'comfyui_available': False,
                            'message': 'Workflow generated but ComfyUI server not available'
                        }
                    )

                # 3. Workflow an ComfyUI senden
                prompt_id = await client.submit_workflow(workflow)

                if not prompt_id:
                    return BackendResponse(
                        success=False,
                        content="",
                        error="Failed to submit workflow to ComfyUI"
                    )

                logger.info(f"Workflow submitted to ComfyUI: {prompt_id}")

                # 4. Optional: Auf Fertigstellung warten (wenn wait_for_completion Parameter gesetzt)
                if parameters.get('wait_for_completion', False):
                    timeout = parameters.get('timeout', 300)
                    history = await client.wait_for_completion(prompt_id, timeout=timeout)

                    if history:
                        # Generierte Bilder extrahieren
                        images = await client.get_generated_images(history)
                        return BackendResponse(
                            success=True,
                            content=prompt_id,
                            metadata={
                                'workflow_generated': True,
                                'template': workflow_template,
                                'prompt_id': prompt_id,
                                'completed': True,
                                'images': images,
                                'comfyui_available': True
                            }
                        )
                    else:
                        return BackendResponse(
                            success=False,
                            content=prompt_id,
                            error="Timeout or error waiting for completion",
                            metadata={
                                'workflow_generated': True,
                                'template': workflow_template,
                                'prompt_id': prompt_id,
                                'completed': False,
                                'comfyui_available': True
                            }
                        )
                else:
                    # Sofort zurückkehren mit prompt_id
                    return BackendResponse(
                        success=True,
                        content=prompt_id,
                        metadata={
                            'workflow_generated': True,
                            'template': workflow_template,
                            'prompt_id': prompt_id,
                            'submitted': True,
                            'comfyui_available': True,
                            'message': 'Workflow submitted to ComfyUI queue'
                        }
                    )

            except ImportError as e:
                logger.error(f"ComfyUI modules nicht verfügbar: {e}")
                return BackendResponse(
                    success=False,
                    content="",
                    error="ComfyUI integration not available"
                )

        except Exception as e:
            logger.error(f"ComfyUI-Legacy-Backend-Fehler: {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"ComfyUI-Legacy-Service-Fehler: {str(e)}"
            )
    
    def is_backend_available(self, backend_type: BackendType) -> bool:
        """Prüfen ob Backend verfügbar ist"""
        return backend_type in self.backends
    
    def get_available_backends(self) -> list[BackendType]:
        """Liste aller verfügbaren Backends"""
        return list(self.backends.keys())

# Singleton-Instanz
router = BackendRouter()
