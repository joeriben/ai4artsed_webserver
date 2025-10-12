#!/usr/bin/env python3
"""
Full ComfyUI Pipeline End-to-End Test
Testet: Dadaismus-Transformation → ComfyUI Workflow → Bildgenerierung
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from my_app.services.comfyui_client import get_comfyui_client

async def test_full_pipeline():
    """Test: Komplette Pipeline mit echter ComfyUI-Bildgenerierung"""
    print("🎨 FULL COMFYUI PIPELINE TEST")
    print("=" * 70)
    
    test_prompt = "Ein Kamel fliegt über den Schwarzwald"
    print(f"📝 Input: '{test_prompt}'")
    print()
    
    # 1. ComfyUI Health Check
    print("1. 🏥 ComfyUI Health Check:")
    client = get_comfyui_client()
    is_healthy = await client.health_check()
    
    if not is_healthy:
        print("   ❌ ComfyUI nicht erreichbar!")
        print("   Stelle sicher, dass ComfyUI auf http://127.0.0.1:8188 läuft")
        return
    
    print("   ✅ ComfyUI ist online und bereit!")
    print()
    
    # 2. Schema-Pipeline mit Dadaismus-Transformation
    print("2. 🎭 Dadaismus-Transformation:")
    
    schemas_path = Path(__file__).parent / "schemas"
    executor = PipelineExecutor(schemas_path)
    executor.schema_registry.initialize(schemas_path)
    
    # Pipeline ausführen mit wait_for_completion=True
    result = await executor.execute_pipeline(
        schema_name="TEST_dadaismus_image",
        input_text=test_prompt,
        user_input=test_prompt
    )
    
    print(f"   Status: {result.status.value}")
    print()
    
    # 3. Schritte analysieren
    print("3. 📊 Pipeline-Schritte:")
    dadaismus_output = None
    prompt_id = None
    
    for i, step in enumerate(result.steps):
        print(f"   Schritt {i+1}: {step.chunk_name}")
        print(f"   Status: {step.status.value}")
        
        if step.status.value == 'completed' and step.output_data:
            if step.chunk_name == 'prompt_interception':
                dadaismus_output = step.output_data
                print(f"   ✅ Dadaismus: {dadaismus_output[:100]}...")
            elif step.chunk_name == 'comfyui_image_generation':
                # Sollte die prompt_id enthalten
                prompt_id = step.output_data
                print(f"   ✅ Prompt ID: {prompt_id}")
        elif step.error:
            print(f"   ❌ Error: {step.error}")
        print()
    
    # 4. Wenn ComfyUI-Schritt erfolgreich war
    if prompt_id:
        print("4. ⏳ Warte auf Bildgenerierung:")
        print(f"   Monitoring Prompt ID: {prompt_id}")
        
        # Auf Fertigstellung warten
        history = await client.wait_for_completion(prompt_id, timeout=300)
        
        if history:
            print("   ✅ Generierung abgeschlossen!")
            print()
            
            # 5. Bilder extrahieren
            print("5. 🖼️ Generierte Bilder:")
            images = await client.get_generated_images(history)
            
            if images:
                for i, img_info in enumerate(images):
                    print(f"   Bild {i+1}:")
                    print(f"     Dateiname: {img_info['filename']}")
                    print(f"     Node: {img_info['node_id']}")
                    
                    # Bild herunterladen
                    img_data = await client.get_image(
                        img_info['filename'],
                        img_info['subfolder'],
                        img_info['type']
                    )
                    
                    if img_data:
                        # Bild speichern
                        output_file = Path(f"TEST_generated_image_{i+1}.png")
                        with open(output_file, 'wb') as f:
                            f.write(img_data)
                        print(f"     ✅ Gespeichert: {output_file}")
                        print(f"     Größe: {len(img_data)} bytes")
                    print()
                
                print("=" * 70)
                print("🎉 ERFOLG! Komplette Pipeline funktioniert:")
                print("   ✅ Deutsche Eingabe → Dadaismus-Transformation")
                print("   ✅ Workflow-Generierung → ComfyUI-Submission")
                print("   ✅ Bildgenerierung → Download")
                print()
                print(f"   📁 Generierte Bilder: {len(images)}")
                print("   🎨 Pipeline vollständig funktional!")
                
            else:
                print("   ⚠️ Keine Bilder in History gefunden")
        else:
            print("   ❌ Timeout oder Fehler bei Bildgenerierung")
    else:
        print("4. ⚠️ ComfyUI-Schritt hat keine Prompt-ID zurückgegeben")
        print("   Überprüfe Backend-Router-Integration")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
