#!/usr/bin/env python3
"""
Test-Script für Template+Config-System
Testet ChunkBuilder-Functionality mit konkreten Beispielen
"""

import sys
import logging
from pathlib import Path

# Pfad für Schema-Imports anpassen
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.chunk_builder import ChunkBuilder

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_chunk_system():
    """Haupt-Test-Funktion für Template+Config-System"""
    print("=" * 60)
    print("AI4ArtsEd Schema-System Test")
    print("=" * 60)
    
    # 1. ChunkBuilder initialisieren
    print("\n1. ChunkBuilder initialisieren...")
    schemas_path = Path(__file__).parent / "schemas"
    chunk_builder = ChunkBuilder(schemas_path)
    
    print(f"   Schemas-Pfad: {schemas_path}")
    print(f"   Templates geladen: {len(chunk_builder.templates)}")
    print(f"   Configs geladen: {len(chunk_builder.configs)}")
    
    # 2. Verfügbare Templates und Configs anzeigen
    print("\n2. Verfügbare Komponenten:")
    print(f"   Templates: {chunk_builder.get_available_templates()}")
    print(f"   Configs: {chunk_builder.get_available_configs()}")
    
    # 3. Template-Placeholder-Erkennung testen
    print("\n3. Template-Placeholder-Analyse:")
    for template_name in chunk_builder.get_available_templates():
        placeholders = chunk_builder.get_template_placeholders(template_name)
        print(f"   {template_name}: {placeholders}")
    
    # 4. Translation-Chunk testen
    print("\n4. Translation-Chunk Test:")
    try:
        context = {
            "input_text": "Ein Student an der Universität",
            "user_input": "Ein Student an der Universität"
        }
        
        chunk_request = chunk_builder.build_chunk(
            chunk_name="translate",
            config_path="translate.standard", 
            context=context
        )
        
        print("   ✓ Translation-Chunk erfolgreich erstellt")
        print(f"   Backend-Type: {chunk_request['backend_type']}")
        print(f"   Model: {chunk_request['model']}")
        print(f"   Prompt-Länge: {len(chunk_request['prompt'])} Zeichen")
        print("   Prompt-Preview:")
        print("   " + "=" * 50)
        print("   " + chunk_request['prompt'][:200] + "...")
        print("   " + "=" * 50)
        
    except Exception as e:
        print(f"   ✗ Translation-Chunk Fehler: {e}")
    
    # 5. Manipulation-Chunk testen
    print("\n5. Manipulation-Chunk Test:")
    try:
        context = {
            "input_text": "Ein Student an der Universität",
            "previous_output": "A student at the university",
            "user_input": "Ein Student an der Universität"
        }
        
        chunk_request = chunk_builder.build_chunk(
            chunk_name="manipulate",
            config_path="manipulate.jugendsprache",
            context=context
        )
        
        print("   ✓ Manipulation-Chunk erfolgreich erstellt")
        print(f"   Backend-Type: {chunk_request['backend_type']}")
        print(f"   Model: {chunk_request['model']}")
        print(f"   Prompt-Länge: {len(chunk_request['prompt'])} Zeichen")
        print("   Prompt-Preview:")
        print("   " + "=" * 50)
        print("   " + chunk_request['prompt'][:200] + "...")
        print("   " + "=" * 50)
        
    except Exception as e:
        print(f"   ✗ Manipulation-Chunk Fehler: {e}")
    
    # 6. Vollständige Pipeline-Simulation
    print("\n6. Pipeline-Simulation (translate→manipulate):")
    try:
        # Schritt 1: Translation
        translation_context = {
            "input_text": "Ein Student",
            "user_input": "Ein Student"
        }
        
        translation_chunk = chunk_builder.build_chunk(
            "translate", 
            "translate.standard", 
            translation_context
        )
        
        # Simulierte Translation-Response
        simulated_translation = "A student"
        print(f"   Schritt 1 (Translation): '{translation_context['input_text']}' → '{simulated_translation}'")
        
        # Schritt 2: Manipulation
        manipulation_context = {
            "input_text": translation_context['input_text'],
            "previous_output": simulated_translation,
            "user_input": translation_context['input_text']
        }
        
        manipulation_chunk = chunk_builder.build_chunk(
            "manipulate",
            "manipulate.jugendsprache",
            manipulation_context
        )
        
        print("   Schritt 2 (Manipulation): Jugendsprache-Transformation bereit")
        print("   ✓ Pipeline-Simulation erfolgreich")
        
    except Exception as e:
        print(f"   ✗ Pipeline-Simulation Fehler: {e}")
    
    # 7. Validierung-Tests
    print("\n7. Validierungs-Tests:")
    
    # Test: Fehlende Template
    try:
        chunk_builder.build_chunk("nonexistent", "translate.standard", {})
        print("   ✗ Fehlende Template-Validation fehlgeschlagen")
    except ValueError as e:
        print("   ✓ Fehlende Template korrekt erkannt")
    
    # Test: Fehlende Config
    try:
        chunk_builder.build_chunk("translate", "nonexistent.config", {})
        print("   ✗ Fehlende Config-Validation fehlgeschlagen")
    except ValueError as e:
        print("   ✓ Fehlende Config korrekt erkannt")
    
    # Test: Validation-Methode
    errors = chunk_builder.validate_chunk_request(
        "translate", 
        "translate.standard", 
        {}  # Leerer Context
    )
    if errors:
        print(f"   ✓ Validation-Fehler erkannt: {errors}")
    else:
        print("   ✓ Validation erfolgreich")
    
    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)

if __name__ == "__main__":
    test_chunk_system()
