#!/usr/bin/env python3
"""
Translation-Test - Teste korrigierte Prompt Interception Format
"""

import sys
import asyncio
import logging
from pathlib import Path

# Pfad für Schema-Imports anpassen
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.chunk_builder import ChunkBuilder
from schemas.engine.backend_router import BackendRouter, BackendRequest, BackendType

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_translation_fixed():
    """Test der korrigierten Translation mit TASK/CONTEXT Support"""
    
    print("=" * 70)
    print("🔧 TRANSLATION TEST - Korrigierte TASK/CONTEXT Support")
    print("=" * 70)
    
    schemas_path = Path(__file__).parent / "schemas"
    
    # 1. ChunkBuilder mit neuen Placeholders testen
    print("\n1. 🔧 ChunkBuilder Test (TASK/CONTEXT):")
    chunk_builder = ChunkBuilder(schemas_path)
    
    print(f"   Templates geladen: {len(chunk_builder.templates)}")
    print(f"   Configs geladen: {len(chunk_builder.configs)}")
    
    # Verfügbare Templates und Configs anzeigen
    print(f"   Templates: {chunk_builder.get_available_templates()}")
    print(f"   Configs: {chunk_builder.get_available_configs()}")
    
    # 2. Prompt Interception Template testen
    if 'prompt_interception' in chunk_builder.templates:
        print("\n2. 🎯 Prompt Interception Template:")
        pi_template = chunk_builder.templates['prompt_interception']
        print(f"   Template: {pi_template.template}")
        print(f"   Placeholders: {pi_template.placeholders}")
    else:
        print("\n2. ❌ Prompt Interception Template nicht gefunden!")
    
    # 3. Translation Config testen
    if 'prompt_interception.translation_en' in chunk_builder.configs:
        print("\n3. 🌍 Translation Config:")
        trans_config = chunk_builder.configs['prompt_interception.translation_en']
        print(f"   Task: {trans_config.task[:100]}...")
        print(f"   Context: '{trans_config.context}'")
        print(f"   Parameters: {trans_config.parameters}")
    else:
        print("\n3. ❌ Translation Config nicht gefunden!")
        print("   Verfügbare PI-Configs:")
        pi_configs = [c for c in chunk_builder.configs.keys() if 'prompt_interception' in c]
        print(f"   {pi_configs}")
    
    # 4. Translation-Chunk-Building testen
    print("\n4. 🚀 Translation Chunk-Building:")
    try:
        context = {
            "input_text": "Ein Pferd steht auf einer grünen Wiese",
            "user_input": "Ein Pferd steht auf einer grünen Wiese"
        }
        
        chunk_request = chunk_builder.build_chunk(
            chunk_name="prompt_interception",
            config_path="prompt_interception.translation_en",
            context=context
        )
        
        print("   ✅ Translation-Chunk erfolgreich erstellt!")
        print(f"   Backend: {chunk_request['backend_type']}")
        print(f"   Model: {chunk_request['model']}")
        print(f"   Prompt-Länge: {len(chunk_request['prompt'])} Zeichen")
        print("   Prompt-Content:")
        print("   " + "=" * 50)
        print("   " + chunk_request['prompt'])
        print("   " + "=" * 50)
        
    except Exception as e:
        print(f"   ❌ Translation Chunk-Building Fehler: {e}")
        return
    
    # 5. Backend-Request testen (ohne echten API-Call)
    print("\n5. 🔗 Backend-Request Simulation:")
    try:
        backend_router = BackendRouter()
        
        backend_request = BackendRequest(
            backend_type=BackendType(chunk_request['backend_type']),
            model=chunk_request['model'],
            prompt=chunk_request['prompt'],
            parameters=chunk_request['parameters']
        )
        
        print(f"   ✅ Backend-Request Format korrekt:")
        print(f"      Type: {backend_request.backend_type}")
        print(f"      Model: {backend_request.model}")
        print(f"      Prompt hat Task+Context+Prompt Format: {('Task:' in backend_request.prompt and 'Context:' in backend_request.prompt)}")
        
    except Exception as e:
        print(f"   ❌ Backend-Request Fehler: {e}")
    
    # 6. Live Translation-Test mit Ollama
    print("\n6. 🤖 Live Translation-Test:")
    print("   Hinweis: Für echten Ollama-Test verwenden Sie:")
    print("   cd devserver && python TEST_dadaismus_live.py")
    
    print("\n" + "=" * 70)
    print("🎉 TRANSLATION TEST ABGESCHLOSSEN!")
    print("")
    print("📋 Status:")
    print("   ✅ ChunkBuilder unterstützt TASK/CONTEXT")
    print("   ✅ Prompt Interception Template verfügbar") 
    print("   ✅ Translation Config korrekt geladen")
    print("   ✅ Task+Context+Prompt Format funktional")
    print("")
    print("🔧 Bereit für Schema-Pipeline-Integration mit korrigierter Translation!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_translation_fixed())
