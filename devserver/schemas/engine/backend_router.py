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
        """Process Output-Chunk: Load workflow, apply mappings, submit to ComfyUI"""
        try:
            # 1. Load Output-Chunk from JSON
            chunk = self._load_output_chunk(chunk_name)
            if not chunk:
                return BackendResponse(
                    success=False,
                    content="",
                    error=f"Output-Chunk '{chunk_name}' not found"
                )

            logger.info(f"Loaded Output-Chunk: {chunk_name} ({chunk.get('media_type', 'unknown')} media)")

            # 2. Clone workflow (don't modify original)
            import copy
            workflow = copy.deepcopy(chunk['workflow'])

            # 3. Apply input_mappings
            input_data = {'prompt': prompt, **parameters}
            workflow = self._apply_input_mappings(workflow, chunk['input_mappings'], input_data)

            logger.debug(f"Applied input_mappings to {len(chunk['input_mappings'])} fields")

            # 4. Get ComfyUI client
            import sys
            from pathlib import Path
            devserver_path = Path(__file__).parent.parent.parent
            if str(devserver_path) not in sys.path:
                sys.path.insert(0, str(devserver_path))
            from my_app.services.comfyui_client import get_comfyui_client

            client = get_comfyui_client()
            is_healthy = await client.health_check()

            if not is_healthy:
                logger.warning("ComfyUI server not reachable")
                return BackendResponse(
                    success=True,
                    content="workflow_prepared",
                    metadata={
                        'chunk_name': chunk_name,
                        'workflow': workflow,
                        'output_mapping': chunk['output_mapping'],
                        'comfyui_available': False,
                        'message': 'Workflow prepared but ComfyUI server not available'
                    }
                )

            # 5. Submit workflow to ComfyUI
            prompt_id = await client.submit_workflow(workflow)

            if not prompt_id:
                return BackendResponse(
                    success=False,
                    content="",
                    error="Failed to submit workflow to ComfyUI"
                )

            logger.info(f"Workflow submitted to ComfyUI: {prompt_id} (chunk: {chunk_name})")

            # 6. Optional: Wait for completion
            if parameters.get('wait_for_completion', False):
                timeout = parameters.get('timeout', 300)
                history = await client.wait_for_completion(prompt_id, timeout=timeout)

                if history:
                    # Extract generated media based on output_mapping
                    media = await self._extract_output_media(client, history, chunk['output_mapping'])
                    return BackendResponse(
                        success=True,
                        content=prompt_id,
                        metadata={
                            'chunk_name': chunk_name,
                            'prompt_id': prompt_id,
                            'completed': True,
                            'media': media,
                            'media_type': chunk.get('media_type'),
                            'output_mapping': chunk['output_mapping'],
                            'comfyui_available': True
                        }
                    )
                else:
                    return BackendResponse(
                        success=False,
                        content=prompt_id,
                        error="Timeout or error waiting for completion",
                        metadata={
                            'chunk_name': chunk_name,
                            'prompt_id': prompt_id,
                            'completed': False,
                            'comfyui_available': True
                        }
                    )
            else:
                # Return immediately with prompt_id
                return BackendResponse(
                    success=True,
                    content=prompt_id,
                    metadata={
                        'chunk_name': chunk_name,
                        'prompt_id': prompt_id,
                        'submitted': True,
                        'output_mapping': chunk['output_mapping'],
                        'media_type': chunk.get('media_type'),
                        'comfyui_available': True,
                        'message': 'Workflow submitted to ComfyUI queue'
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

            # Get API key from .key file
            api_key = self._load_api_key('openrouter_api.key')
            if not api_key:
                logger.error("OpenRouter API key not found. Create 'openrouter_api.key' file in devserver root.")
                return BackendResponse(success=False, error="OpenRouter API key not found. Create 'openrouter_api.key' file in devserver root.")

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

                        # Extract image URL from multimodal chat completion response
                        # For GPT-5 Image: choices[0].message.content is a list with type="image_url"
                        image_url = self._extract_image_from_chat_completion(data, chunk['output_mapping'])

                        if not image_url:
                            logger.error("No image found in API response")
                            return BackendResponse(success=False, content="", error="No image found in response", metadata={})

                        logger.info(f"API generation successful: Generated data URI ({len(image_url)} chars)")

                        return BackendResponse(
                            success=True,
                            content=image_url,
                            metadata={
                                'chunk_name': chunk_name,
                                'media_type': chunk['media_type'],
                                'provider': api_config['provider'],
                                'model': api_config['model'],
                                'image_url': image_url
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

    def _apply_input_mappings(self, workflow: Dict, mappings: Dict[str, Any], input_data: Dict[str, Any]) -> Dict:
        """Apply input_mappings to workflow - inject prompts and parameters"""
        import random

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

        return workflow

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
        """LEGACY: ComfyUI-Request mit deprecated comfyui_workflow_generator"""
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
                from my_app.services.comfyui_client import get_comfyui_client

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

                # 2. ComfyUI Client holen und Health Check
                client = get_comfyui_client()
                is_healthy = await client.health_check()

                if not is_healthy:
                    logger.warning("ComfyUI server not reachable, returning workflow only")
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
