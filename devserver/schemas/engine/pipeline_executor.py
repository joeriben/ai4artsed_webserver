"""
Pipeline-Executor: Zentrale Orchestrierung der Schema-basierten Pipeline
"""
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from pathlib import Path

from .schema_registry import SchemaRegistry, SchemaDefinition
from .chunk_builder import ChunkBuilder
from .backend_router import BackendRouter, BackendRequest, BackendResponse, BackendType

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline-Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class PipelineStep:
    """Einzelner Pipeline-Schritt"""
    step_id: str
    chunk_name: str
    config_path: str
    status: PipelineStatus = PipelineStatus.PENDING
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineContext:
    """Pipeline-Kontext für Datenaustausch zwischen Schritten"""
    input_text: str
    user_input: str
    previous_outputs: List[str] = field(default_factory=list)
    custom_placeholders: Dict[str, Any] = field(default_factory=dict)
    pipeline_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_previous_output(self) -> str:
        """Letzten Pipeline-Output abrufen"""
        return self.previous_outputs[-1] if self.previous_outputs else self.input_text
    
    def add_output(self, output: str) -> None:
        """Pipeline-Output hinzufügen"""
        self.previous_outputs.append(output)

@dataclass
class PipelineResult:
    """Pipeline-Ausführungs-Ergebnis"""
    schema_name: str
    status: PipelineStatus
    steps: List[PipelineStep]
    final_output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class PipelineExecutor:
    """Zentrale Pipeline-Orchestrierung"""
    
    def __init__(self, schemas_path: Path):
        self.schemas_path = schemas_path
        self.schema_registry = SchemaRegistry()
        self.chunk_builder = ChunkBuilder(schemas_path)
        self.backend_router = BackendRouter()
        self._initialized = False
        
    def initialize(self, ollama_service=None, workflow_logic_service=None, comfyui_service=None):
        """Pipeline-Executor mit Legacy-Services initialisieren"""
        # Schema-Registry initialisieren
        self.schema_registry.initialize(self.schemas_path)
        
        # Backend-Router mit Legacy-Services initialisieren
        self.backend_router.initialize(
            ollama_service=ollama_service,
            workflow_logic_service=workflow_logic_service,
            comfyui_service=comfyui_service
        )
        
        self._initialized = True
        logger.info("Pipeline-Executor initialisiert")
    
    async def execute_pipeline(self, schema_name: str, input_text: str, user_input: Optional[str] = None) -> PipelineResult:
        """Komplette Pipeline ausführen"""
        # Auto-Initialisierung wenn noch nicht erfolgt
        if not self._initialized:
            logger.info("Auto-Initialisierung: Schema-Registry wird initialisiert")
            self.schema_registry.initialize(self.schemas_path)
            self._initialized = True
        
        # Schema abrufen
        schema = self.schema_registry.get_schema(schema_name)
        if not schema:
            return PipelineResult(
                schema_name=schema_name,
                status=PipelineStatus.FAILED,
                steps=[],
                error=f"Schema '{schema_name}' nicht gefunden"
            )
        
        # Pipeline-Kontext erstellen
        context = PipelineContext(
            input_text=input_text,
            user_input=user_input or input_text
        )
        
        # Pipeline-Schritte planen
        steps = self._plan_pipeline_steps(schema)
        
        # Pipeline ausführen
        result = await self._execute_pipeline_steps(schema_name, steps, context)
        
        logger.info(f"Pipeline '{schema_name}' abgeschlossen: {result.status}")
        return result
    
    async def stream_pipeline(self, schema_name: str, input_text: str, user_input: Optional[str] = None) -> AsyncGenerator[Tuple[str, Any], None]:
        """Pipeline mit Streaming-Updates ausführen"""
        if not self._initialized:
            yield ("error", "Pipeline-Executor nicht initialisiert")
            return
        
        schema = self.schema_registry.get_schema(schema_name)
        if not schema:
            yield ("error", f"Schema '{schema_name}' nicht gefunden")
            return
        
        context = PipelineContext(
            input_text=input_text,
            user_input=user_input or input_text
        )
        
        steps = self._plan_pipeline_steps(schema)
        
        yield ("pipeline_started", {
            "schema_name": schema_name,
            "total_steps": len(steps),
            "input_text": input_text
        })
        
        # Pipeline-Schritte mit Streaming ausführen
        async for event_type, event_data in self._stream_pipeline_steps(schema_name, steps, context):
            yield (event_type, event_data)
    
    def _plan_pipeline_steps(self, schema: SchemaDefinition) -> List[PipelineStep]:
        """Pipeline-Schritte aus Schema-Definition planen"""
        steps = []
        
        for i, chunk_name in enumerate(schema.chunks):
            # Config-Path aus config_mappings abrufen
            config_path = schema.config_mappings.get(chunk_name, f"{chunk_name}.default")
            
            step = PipelineStep(
                step_id=f"step_{i+1}_{chunk_name}",
                chunk_name=chunk_name,
                config_path=config_path
            )
            steps.append(step)
        
        logger.debug(f"Pipeline geplant: {len(steps)} Schritte für Schema '{schema.name}' (Pipeline-Typ: {schema.pipeline_type})")
        return steps
    
    async def _execute_pipeline_steps(self, schema_name: str, steps: List[PipelineStep], context: PipelineContext) -> PipelineResult:
        """Pipeline-Schritte sequenziell ausführen"""
        import time
        start_time = time.time()
        
        completed_steps = []
        
        for step in steps:
            try:
                # Schritt ausführen
                step.status = PipelineStatus.RUNNING
                output = await self._execute_single_step(step, context)
                
                # Erfolgreicher Schritt
                step.status = PipelineStatus.COMPLETED
                step.output_data = output
                context.add_output(output)
                
                completed_steps.append(step)
                logger.debug(f"Schritt {step.step_id} erfolgreich: {len(output)} Zeichen Output")
                
            except Exception as e:
                # Fehlgeschlagener Schritt
                step.status = PipelineStatus.FAILED
                step.error = str(e)
                completed_steps.append(step)
                
                logger.error(f"Schritt {step.step_id} fehlgeschlagen: {e}")
                
                # Pipeline abbrechen bei Fehler
                return PipelineResult(
                    schema_name=schema_name,
                    status=PipelineStatus.FAILED,
                    steps=completed_steps,
                    error=f"Schritt {step.step_id} fehlgeschlagen: {e}",
                    execution_time=time.time() - start_time
                )
        
        # Pipeline erfolgreich abgeschlossen
        final_output = context.get_previous_output()
        
        return PipelineResult(
            schema_name=schema_name,
            status=PipelineStatus.COMPLETED,
            steps=completed_steps,
            final_output=final_output,
            execution_time=time.time() - start_time,
            metadata={
                "total_steps": len(steps),
                "input_length": len(context.input_text),
                "output_length": len(final_output)
            }
        )
    
    async def _stream_pipeline_steps(self, schema_name: str, steps: List[PipelineStep], context: PipelineContext) -> AsyncGenerator[Tuple[str, Any], None]:
        """Pipeline-Schritte mit Streaming-Updates ausführen"""
        for i, step in enumerate(steps):
            yield ("step_started", {
                "step_id": step.step_id,
                "step_number": i + 1,
                "chunk_name": step.chunk_name,
                "config_path": step.config_path
            })
            
            try:
                step.status = PipelineStatus.RUNNING
                
                # Schritt ausführen
                output = await self._execute_single_step(step, context)
                
                step.status = PipelineStatus.COMPLETED
                step.output_data = output
                context.add_output(output)
                
                yield ("step_completed", {
                    "step_id": step.step_id,
                    "output": output,
                    "output_length": len(output)
                })
                
            except Exception as e:
                step.status = PipelineStatus.FAILED
                step.error = str(e)
                
                yield ("step_failed", {
                    "step_id": step.step_id,
                    "error": str(e)
                })
                
                # Pipeline abbrechen
                yield ("pipeline_failed", {
                    "schema_name": schema_name,
                    "failed_step": step.step_id,
                    "error": str(e)
                })
                return
        
        # Pipeline erfolgreich abgeschlossen
        final_output = context.get_previous_output()
        yield ("pipeline_completed", {
            "schema_name": schema_name,
            "final_output": final_output,
            "total_steps": len(steps)
        })
    
    async def _execute_single_step(self, step: PipelineStep, context: PipelineContext) -> str:
        """Einzelnen Pipeline-Schritt ausführen"""
        # Chunk erstellen
        chunk_context = {
            "input_text": context.input_text,
            "user_input": context.user_input,
            "previous_output": context.get_previous_output(),
            "custom_placeholders": context.custom_placeholders
        }
        
        chunk_request = self.chunk_builder.build_chunk(
            chunk_name=step.chunk_name,
            config_path=step.config_path,
            context=chunk_context
        )
        
        # Backend-Request erstellen
        backend_request = BackendRequest(
            backend_type=BackendType(chunk_request['backend_type']),
            model=chunk_request['model'],
            prompt=chunk_request['prompt'],
            parameters=chunk_request['parameters']
        )
        
        # Backend-Verarbeitung
        response = await self.backend_router.process_request(backend_request)
        
        if isinstance(response, BackendResponse):
            if response.success:
                return response.content
            else:
                raise RuntimeError(f"Backend-Fehler: {response.error}")
        else:
            # AsyncGenerator (Streaming) - für jetzt nicht unterstützt in einzelnen Schritten
            raise RuntimeError("Streaming in Einzelschritten nicht unterstützt")
    
    def get_available_schemas(self) -> List[str]:
        """Liste aller verfügbaren Schemas"""
        return self.schema_registry.list_schemas()
    
    def get_schema_info(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Schema-Informationen abrufen"""
        schema = self.schema_registry.get_schema(schema_name)
        if not schema:
            return None
        
        return {
            "name": schema.name,
            "description": schema.description,
            "pipeline_type": schema.pipeline_type,
            "chunks": schema.chunks,
            "config_mappings": schema.config_mappings,
            "meta": schema.meta
        }

# Singleton-Instanz
executor = PipelineExecutor(Path(__file__).parent.parent)
