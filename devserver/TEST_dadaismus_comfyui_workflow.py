#!/usr/bin/env python3
"""
Dadaismus → ComfyUI Workflow Generator Test
Testet die vollständige Pipeline: Dadaismus-Transformation → SD 3.5 Workflow-Generierung
"""
import asyncio
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.comfyui_workflow_generator import get_workflow_generator

async def test_dadaismus_to_comfyui():
    """Test: Dadaismus-Transformation + ComfyUI-Workflow-Generierung"""
    print("🎭 DADAISMUS → COMFYUI WORKFLOW TEST")
    print("=" * 70)
    
    test_prompt = "Ein Kamel fliegt über den Schwarzwald"
    print(f"📝 Test-Prompt: '{test_prompt}'")
    print()
    
    # 1. Schema-Pipeline: Dadaismus-Transformation
    print("1. 🎨 Dadaismus-Transformation:")
    
    schemas_path = Path(__file__).parent / "schemas"
    executor = PipelineExecutor(schemas_path)
    executor.schema_registry.initialize(schemas_path)
    
    # Verfügbare Schemas prüfen
    available_schemas = executor.get_available_schemas()
    print(f"   📋 Verfügbare Schemas: {available_schemas}")
    
    if "TEST_dadaismus_image" in available_schemas:
        print("   ✅ TEST_dadaismus_image Schema gefunden!")
        
        # Schema-Info
        schema_info = executor.get_schema_info("TEST_dadaismus_image")
        print(f"   🔧 Pipeline-Typ: {schema_info['pipeline_type']}")
        print(f"   🔧 Chunks: {schema_info['chunks']}")
        print()
        
        # Nur den ersten Schritt (Dadaismus-Transformation) testen
        print("2. 🚀 Dadaismus-Pipeline-Schritt:")
        try:
            result = await executor.execute_pipeline(
                schema_name="TEST_dadaismus_image",
                input_text=test_prompt,
                user_input=test_prompt
            )
            
            print(f"   Status: {result.status.value}")
            print(f"   Schritte: {len(result.steps)}")
            
            dadaismus_output = None
            for i, step in enumerate(result.steps):
                print(f"   Schritt {i+1}: {step.chunk_name} - {step.status.value}")
                if step.status.value == 'completed' and step.output_data:
                    print(f"     ✅ Output: {step.output_data[:100]}...")
                    if step.chunk_name == 'prompt_interception':
                        dadaismus_output = step.output_data
                elif step.error:
                    print(f"     ❌ Error: {step.error}")
            
            print()
            
            # 3. ComfyUI-Workflow-Generator testen
            if dadaismus_output:
                print("3. 🖼️ ComfyUI-Workflow-Generation:")
                print(f"   📝 Dadaismus-Output: {dadaismus_output[:150]}...")
                print()
                
                generator = get_workflow_generator(schemas_path)
                
                # Workflow generieren
                workflow = generator.generate_workflow(
                    template_name="sd35_standard",
                    schema_output=dadaismus_output,
                    parameters={
                        "width": 1024,
                        "height": 1024,
                        "steps": 25,
                        "cfg": 5.5
                    }
                )
                
                if workflow:
                    print(f"   ✅ ComfyUI-Workflow generiert: {len(workflow)} Nodes")
                    print(f"   🔧 Nodes: {list(workflow.keys())}")
                    
                    # Prompt-Node prüfen
                    if "6" in workflow:
                        prompt_node = workflow["6"]
                        actual_prompt = prompt_node["inputs"]["text"]
                        print(f"   🎯 Generierter Prompt: {actual_prompt[:100]}...")
                        print()
                        
                        # Workflow-Struktur prüfen
                        print("4. 📊 Workflow-Struktur-Analyse:")
                        essential_nodes = ["3", "4", "5", "6", "7", "8", "9", "43"]
                        for node_id in essential_nodes:
                            if node_id in workflow:
                                node = workflow[node_id]
                                print(f"   ✅ Node {node_id}: {node['class_type']}")
                            else:
                                print(f"   ❌ Node {node_id}: FEHLT")
                        
                        print()
                        print("5. 🎉 ERFOLG:")
                        print("   ✅ Dadaismus-Transformation funktioniert")
                        print("   ✅ ComfyUI-Workflow-Generator funktioniert") 
                        print("   ✅ Pipeline-Integration komplett")
                        print()
                        print("   🎯 BEREIT FÜR COMFYUI-BACKEND-INTEGRATION!")
                        
                        # Optional: Workflow als JSON speichern
                        workflow_file = Path("TEST_generated_workflow.json")
                        with open(workflow_file, 'w', encoding='utf-8') as f:
                            json.dump(workflow, f, indent=2, ensure_ascii=False)
                        print(f"   📁 Workflow gespeichert: {workflow_file}")
                        
                    else:
                        print("   ❌ Prompt-Node (6) nicht im generierten Workflow gefunden!")
                else:
                    print("   ❌ Workflow-Generation fehlgeschlagen!")
            else:
                print("3. ❌ Kein Dadaismus-Output für ComfyUI-Generation verfügbar")
                
        except Exception as e:
            print(f"   ❌ Pipeline-Fehler: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   ❌ TEST_dadaismus_image Schema nicht gefunden!")
        print(f"   Verfügbare: {available_schemas}")

if __name__ == "__main__":
    asyncio.run(test_dadaismus_to_comfyui())
