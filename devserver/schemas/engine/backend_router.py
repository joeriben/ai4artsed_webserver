"""
Backend-Router: Multi-Backend-Support für Schema-Pipelines
"""
import logging
from typing import Dict, Any, Optional, AsyncGenerator, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path

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
            # Schema-Pipelines: Ollama/OpenRouter über Prompt Interception Engine
            if request.backend_type in [BackendType.OLLAMA, BackendType.OPENROUTER]:
                return await self._process_prompt_interception_request(request)
            elif request.backend_type == BackendType.COMFYUI:
                # ComfyUI braucht kein registriertes Backend - verwendet direkt ComfyUI-Client
                return await self._process_comfyui_request(None, request)
            else:
                return BackendResponse(
                    success=False,
                    content="",
                    error=f"Backend-Typ {request.backend_type.value} nicht implementiert"
                )
        except Exception as e:
            logger.error(f"Fehler bei Backend-Verarbeitung: {e}")
            return BackendResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def _process_prompt_interception_request(self, request: BackendRequest) -> BackendResponse:
        """Schema-Pipeline-Request über Prompt Interception Engine"""
        try:
            from .prompt_interception_engine import PromptInterceptionEngine, PromptInterceptionRequest
            
            # Parse Template+Config zu Task+Context+Prompt
            input_prompt, input_context, style_prompt = self._parse_template_to_prompt_format(request.prompt)
            
            # Model-String für Prompt Interception Engine
            if request.backend_type == BackendType.OLLAMA:
                model = f"local/{request.model}"
            else:  # OPENROUTER
                model = f"openrouter/{request.model}"
            
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
        """ComfyUI-Request verarbeiten mit automatischer Workflow-Generierung"""
        try:
            # Schema-Pipeline-Output ist der optimierte Prompt
            schema_output = request.prompt
            
            # Workflow-Template aus Parameters extrahieren  
            workflow_template = request.parameters.get('workflow_template', 'sd35_standard')
            
            # ComfyUI-Workflow-Generator verwenden
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
                    parameters=request.parameters
                )
                
                if not workflow:
                    return BackendResponse(
                        success=False, 
                        content="", 
                        error=f"Workflow-Template '{workflow_template}' nicht verfügbar"
                    )
                
                logger.info(f"ComfyUI-Workflow generiert: {len(workflow)} Nodes für Template '{workflow_template}'")
                
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
                if request.parameters.get('wait_for_completion', False):
                    timeout = request.parameters.get('timeout', 300)
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
            logger.error(f"ComfyUI-Backend-Fehler: {e}")
            import traceback
            traceback.print_exc()
            return BackendResponse(
                success=False,
                content="",
                error=f"ComfyUI-Service-Fehler: {str(e)}"
            )
    
    def is_backend_available(self, backend_type: BackendType) -> bool:
        """Prüfen ob Backend verfügbar ist"""
        return backend_type in self.backends
    
    def get_available_backends(self) -> list[BackendType]:
        """Liste aller verfügbaren Backends"""
        return list(self.backends.keys())

# Singleton-Instanz
router = BackendRouter()
