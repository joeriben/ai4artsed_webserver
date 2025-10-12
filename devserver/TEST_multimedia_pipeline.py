#!/usr/bin/env python3
"""
Multi-Media Pipeline Test
Testet die neu implementierte Multi-Media-Generation
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.pipeline_executor import PipelineExecutor

async def test_image_generation():
    """Test Image Generation Pipeline"""
    print("🎨 MULTI-MEDIA PIPELINE TEST - Image Generation")
    print("=" * 70)
    
    # Pipeline-Executor initialisieren
    schemas_path = Path(__file__).parent / "schemas"
    executor = PipelineExecutor(schemas_path)
    executor.schema_registry.initialize(schemas_path)
    
    # Test-Prompt
    test_prompt = "Ein futuristisches AI-Labor mit glühenden Bildschirmen und Robotern"
    
    print(f"📝 Test-Prompt: '{test_prompt}'")
    print()
    
    # 1. Schema verfügbar?
    available_schemas = executor.get_available_schemas()
    print(f"1. 📋 Verfügbare Schemas: {len(available_schemas)}")
    
    if "TEST_image_generation" in available_schemas:
        print("   ✅ TEST_image_generation Schema gefunden!")
    else:
        print("   ❌ TEST_image_generation Schema NICHT gefunden!")
        print(f"   Verfügbare: {available_schemas}")
        return
    
    # 2. Schema-Info laden
    schema_info = executor.get_schema_info("TEST_image_generation")
    if schema_info:
        print(f"2. 🔧 Schema-Info geladen:")
        print(f"   Pipeline-Typ: {schema_info['pipeline_type']}")
        print(f"   Chunks: {schema_info['chunks']}")
        print(f"   Output-Typ: {schema_info.get('meta', {}).get('output_type', 'unknown')}")
        print()
    
    # 3. Pipeline-Schritte testen (nur Prompt-Optimierung)
    print("3. 🚀 Pipeline-Execution Test:")
    print("   (Nur Prompt-Optimierung, ComfyUI-Schritt wird übersprungen)")
    print()
    
    try:
        # Pipeline ausführen (wird bei ComfyUI-Schritt fehlschlagen, aber Prompt-Optimierung sollte funktionieren)
        result = await executor.execute_pipeline(
            schema_name="TEST_image_generation",
            input_text=test_prompt,
            user_input=test_prompt
        )
        
        print(f"   Status: {result.status.value}")
        print(f"   Schritte abgeschlossen: {len(result.steps)}")
        
        if result.steps:
            for i, step in enumerate(result.steps):
                print(f"   Schritt {i+1}: {step.chunk_name} - {step.status.value}")
                if step.output_data and step.status.value == 'completed':
                    print(f"     ✅ Output: {step.output_data[:100]}...")
                elif step.error:
                    print(f"     ❌ Error: {step.error}")
        
        if result.error:
            print(f"   🔧 Pipeline-Error: {result.error}")
        
        print()
        print("4. 📊 Erwartetes Verhalten:")
        print("   ✅ Prompt-Optimierung sollte funktionieren")
        print("   ❌ ComfyUI-Generation wird fehlschlagen (noch nicht implementiert)")
        print("   🎯 Ziel: Media-Prompt-Optimierung testen")
        
    except Exception as e:
        print(f"   ❌ Pipeline-Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_generation())
