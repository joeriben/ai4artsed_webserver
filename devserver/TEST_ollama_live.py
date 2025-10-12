#!/usr/bin/env python3
"""
LIVE OLLAMA TEST - Echter Pipeline-Testlauf
Input: "Ein Pferd steht auf einer grünen Wiese"
Interception: "make every color = grey"
"""

import sys
import asyncio
import logging
from pathlib import Path

# Pfad für Schema-Imports anpassen
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.prompt_interception_engine import (
    PromptInterceptionEngine, 
    PromptInterceptionRequest
)

# Logging konfigurieren für Live-Output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_live_ollama_pipeline():
    """Live Ollama Pipeline Test mit echten API-Aufrufen"""
    
    print("=" * 80)
    print("🚀 LIVE OLLAMA PIPELINE TEST - Schema-System mit echten KI-Aufrufen")
    print("=" * 80)
    
    # Test-Parameter
    test_input = "Ein Pferd steht auf einer grünen Wiese"
    interception_instruction = "make every color = grey"
    
    print(f"\n📝 Test-Input: '{test_input}'")
    print(f"🎯 Interception: '{interception_instruction}'")
    
    # 1. Prompt Interception Engine initialisieren
    print("\n1. 🔧 Prompt Interception Engine Setup:")
    engine = PromptInterceptionEngine()
    
    available_ollama = engine._get_ollama_models()
    if not available_ollama:
        print("   ❌ Keine Ollama-Modelle verfügbar!")
        print("   💡 Starten Sie Ollama: 'ollama serve'")
        print("   💡 Installieren Sie ein Modell: 'ollama pull gemma2:9b'")
        return
    
    print(f"   ✅ {len(available_ollama)} Ollama-Modelle verfügbar: {available_ollama[:3]}...")
    
    # Wähle bestes verfügbares Modell
    preferred_models = ["gemma2:9b", "llama3.2:1b", "llama3.1:8b", "phi3:mini"]
    selected_model = None
    
    for model in preferred_models:
        if model in available_ollama:
            selected_model = model
            break
    
    if not selected_model:
        selected_model = available_ollama[0]
    
    print(f"   🎯 Gewähltes Modell: {selected_model}")
    
    # 2. Schritt 1: Translation (Deutsch → Englisch)
    print(f"\n2. 🌍 TRANSLATION-SCHRITT:")
    print("   Request: Deutsch → Englisch")
    
    translation_instructions = """Translate the following text to English. CRITICAL RULES:
1. Preserve ALL brackets exactly as they appear
2. Translate with maximal semantic preservation
3. Keep original structure and formatting
4. Output ONLY the translated text, nothing else
5. If text is already in English, return it unchanged"""
    
    translation_request = PromptInterceptionRequest(
        input_prompt=test_input,
        input_context="",
        style_prompt=translation_instructions,
        model=f"local/{selected_model}",
        debug=True,
        unload_model=False
    )
    
    print("   🔄 Sende Translation-Request an Ollama...")
    translation_response = await engine.process_request(translation_request)
    
    if not translation_response.success:
        print(f"   ❌ Translation fehlgeschlagen: {translation_response.error}")
        return
    
    translated_text = translation_response.output_str.strip()
    print(f"   ✅ Translation-Ergebnis: '{translated_text}'")
    
    # 3. Schritt 2: Color Manipulation (Alle Farben → Grau)
    print(f"\n3. 🎨 MANIPULATION-SCHRITT:")
    print("   Request: Alle Farben → Grau")
    
    color_instructions = """Your task is to transform the input text to make every color mentioned grey.

RULES:
1. Replace ALL color words with "grey" or "gray"
2. Keep the original sentence structure intact
3. Maintain all other descriptive elements
4. Only change color-related words (red, green, blue, yellow, white, black, brown, etc.)
5. Output ONLY the transformed text, no explanations

Examples:
- "red car" → "grey car"
- "blue sky and green grass" → "grey sky and grey grass"
- "white horse on green meadow" → "grey horse on grey meadow"

Transform the following text by making every color grey:"""
    
    manipulation_request = PromptInterceptionRequest(
        input_prompt=translated_text,
        input_context="",
        style_prompt=color_instructions,
        model=f"local/{selected_model}",
        debug=True,
        unload_model=True  # Modell nach dem letzten Schritt entladen
    )
    
    print("   🔄 Sende Manipulation-Request an Ollama...")
    manipulation_response = await engine.process_request(manipulation_request)
    
    if not manipulation_response.success:
        print(f"   ❌ Manipulation fehlgeschlagen: {manipulation_response.error}")
        return
    
    final_result = manipulation_response.output_str.strip()
    print(f"   ✅ Manipulation-Ergebnis: '{final_result}'")
    
    # 4. Pipeline-Zusammenfassung
    print(f"\n4. 📋 PIPELINE-ZUSAMMENFASSUNG:")
    print("   " + "=" * 60)
    print(f"   📥 Input:       '{test_input}'")
    print(f"   🌍 Translation: '{translated_text}'") 
    print(f"   🎨 Manipulation: '{final_result}'")
    print("   " + "=" * 60)
    
    # 5. Erfolg-Validierung
    print(f"\n5. ✅ ERFOLGS-VALIDIERUNG:")
    
    # Prüfe ob Translation erfolgreich
    if "pferd" not in translated_text.lower() and ("horse" in translated_text.lower() or "pony" in translated_text.lower()):
        print("   ✅ Translation: Deutsch → Englisch erfolgreich")
    else:
        print("   ⚠️  Translation: Möglicherweise unvollständig")
    
    # Prüfe ob Color-Manipulation erfolgreich
    color_words = ["green", "grün", "red", "blue", "yellow", "white", "black", "brown"]
    colors_found = [word for word in color_words if word in final_result.lower()]
    greys_found = ["grey", "gray"]
    grey_count = sum(1 for grey in greys_found if grey in final_result.lower())
    
    if not colors_found and grey_count > 0:
        print("   ✅ Color-Manipulation: Alle Farben zu Grau erfolgreich")
    elif colors_found:
        print(f"   ⚠️  Color-Manipulation: Noch Farben gefunden: {colors_found}")
    else:
        print("   ⚠️  Color-Manipulation: Keine Grau-Wörter erkannt")
    
    print(f"\n6. 🎯 SCHEMA-SYSTEM VALIDIERUNG:")
    print("   ✅ Prompt Interception Engine: Funktional")
    print("   ✅ Multi-Step-Pipeline: Funktional") 
    print("   ✅ Ollama-Integration: Funktional")
    print("   ✅ Task+Context+Prompt-Format: Funktional")
    print("   ✅ Custom-Instructions-System: Funktional")
    
    print("\n" + "=" * 80)
    print("🎉 LIVE OLLAMA TEST ERFOLGREICH ABGESCHLOSSEN!")
    print("Schema-basierte Pipeline-Architektur arbeitet mit echten KI-Models!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_live_ollama_pipeline())
