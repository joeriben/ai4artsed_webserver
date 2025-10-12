#!/usr/bin/env python3
"""
Test-Script für Pipeline-Architektur (ohne Schema-Definitionen)
Testet PipelineExecutor-Komponenten und Integration
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Pfad für Schema-Imports anpassen
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.pipeline_executor import PipelineExecutor, PipelineStep, PipelineContext, PipelineStatus
from schemas.engine.backend_router import BackendRouter, BackendRequest, BackendResponse, BackendType
from schemas.engine.chunk_builder import ChunkBuilder
from schemas.engine.schema_registry import SchemaRegistry, SchemaDefinition

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_pipeline_components():
    """Test einzelner Pipeline-Komponenten"""
    print("=" * 60)
    print("AI4ArtsEd Pipeline-Architektur Test")
    print("=" * 60)
    
    schemas_path = Path(__file__).parent / "schemas"
    
    # 1. Einzelkomponenten-Test
    print("\n1. Komponenten-Initialisierung:")
    
    # ChunkBuilder (bereits getestet)
    chunk_builder = ChunkBuilder(schemas_path)
    print(f"   ✓ ChunkBuilder: {len(chunk_builder.templates)} Templates, {len(chunk_builder.configs)} Configs")
    
    # BackendRouter (ohne Legacy-Services)
    backend_router = BackendRouter()
    print(f"   ✓ BackendRouter: {len(backend_router.backends)} Backends verfügbar")
    
    # SchemaRegistry (ohne Workflow-Definitionen)
    schema_registry = SchemaRegistry()
    schema_registry.initialize(schemas_path)
    print(f"   ✓ SchemaRegistry: {len(schema_registry.schemas)} Schemas geladen")
    
    # PipelineExecutor (ohne Legacy-Services)
    pipeline_executor = PipelineExecutor(schemas_path)
    print(f"   ✓ PipelineExecutor: Initialisiert (nicht konfiguriert)")
    
    # 2. Mock-Schema erstellen und testen
    print("\n2. Mock-Schema-Test:")
    
    # Mock Schema-Definition erstellen
    mock_schema = SchemaDefinition(
        name="test_pipeline",
        description="Test Pipeline für Architektur-Validierung",
        chunks=["translate", "manipulate"],
        config_path="translate.standard,manipulate.jugendsprache",
        meta={"test": True}
    )
    
    # Schema manuell registrieren
    schema_registry.register_schema(mock_schema)
    print(f"   ✓ Mock-Schema registriert: {mock_schema.name}")
    
    # 3. Pipeline-Schritte-Planung testen
    print("\n3. Pipeline-Planung:")
    
    steps = pipeline_executor._plan_pipeline_steps(mock_schema)
    print(f"   ✓ {len(steps)} Pipeline-Schritte geplant:")
    for step in steps:
        print(f"     - {step.step_id}: {step.chunk_name} → {step.config_path}")
    
    # 4. Pipeline-Kontext testen
    print("\n4. Pipeline-Kontext:")
    
    context = PipelineContext(
        input_text="Ein Student",
        user_input="Ein Student"
    )
    
    print(f"   ✓ Initial Context: '{context.input_text}'")
    
    # Context-Updates simulieren
    context.add_output("A student")
    context.add_output("Some yute at uni, innit")
    
    print(f"   ✓ Output History: {len(context.previous_outputs)} Outputs")
    print(f"     - Latest: '{context.get_previous_output()}'")
    
    # 5. Chunk-Building für Pipeline testen
    print("\n5. Chunk-Building für Pipeline:")
    
    for step in steps:
        try:
            # Chunk-Context für Schritt
            chunk_context = {
                "input_text": context.input_text,
                "user_input": context.user_input,
                "previous_output": context.get_previous_output(),
                "custom_placeholders": {}
            }
            
            # Chunk erstellen
            chunk_request = chunk_builder.build_chunk(
                chunk_name=step.chunk_name,
                config_path=step.config_path.split(',')[0] if ',' in step.config_path else step.config_path,
                context=chunk_context
            )
            
            print(f"   ✓ {step.chunk_name}: {chunk_request['backend_type']}/{chunk_request['model']}")
            print(f"     Prompt: {len(chunk_request['prompt'])} Zeichen")
            
        except Exception as e:
            print(f"   ✗ {step.chunk_name}: {e}")
    
    # 6. Backend-Request-Format testen
    print("\n6. Backend-Request-Format:")
    
    try:
        # Test Translation-Chunk
        translation_context = {
            "input_text": "Ein Student",
            "user_input": "Ein Student",
            "previous_output": "Ein Student"
        }
        
        chunk_request = chunk_builder.build_chunk(
            "translate",
            "translate.standard",
            translation_context
        )
        
        # Backend-Request erstellen
        backend_request = BackendRequest(
            backend_type=BackendType(chunk_request['backend_type']),
            model=chunk_request['model'],
            prompt=chunk_request['prompt'],
            parameters=chunk_request['parameters']
        )
        
        print(f"   ✓ Backend-Request Format korrekt:")
        print(f"     Type: {backend_request.backend_type}")
        print(f"     Model: {backend_request.model}")
        print(f"     Parameters: {len(backend_request.parameters)} Keys")
        
    except Exception as e:
        print(f"   ✗ Backend-Request Format: {e}")
    
    # 7. Pipeline-Executor Integration
    print("\n7. Pipeline-Executor Integration:")
    
    # Schema-Registry mit PipelineExecutor verknüpfen
    pipeline_executor.schema_registry = schema_registry
    
    available_schemas = pipeline_executor.get_available_schemas()
    print(f"   ✓ Verfügbare Schemas: {available_schemas}")
    
    # Schema-Info abrufen
    schema_info = pipeline_executor.get_schema_info("test_pipeline")
    if schema_info:
        print(f"   ✓ Schema-Info abgerufen: {schema_info['name']}")
        print(f"     Chunks: {schema_info['chunks']}")
    else:
        print("   ✗ Schema-Info nicht verfügbar")
    
    print("\n" + "=" * 60)
    print("Pipeline-Architektur-Test abgeschlossen!")
    print("Bereit für Schema-Definitionen und Legacy-Service-Integration")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline_components()
