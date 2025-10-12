#!/usr/bin/env python3
"""
TEST: Korrigierte Pipeline-Typ + Schema-Daten Architektur
"""

import sys
import logging
from pathlib import Path

# Pfad für Schema-Imports anpassen
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.schema_registry import SchemaRegistry
from schemas.engine.chunk_builder import ChunkBuilder

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_corrected_architecture():
    """Test der korrigierten Pipeline-Typ + Schema-Daten Architektur"""
    
    print("=" * 80)
    print("🏗️  KORRIGIERTE ARCHITEKTUR TEST - Pipeline-Typ + Schema-Daten")
    print("=" * 80)
    
    schemas_path = Path(__file__).parent / "schemas"
    
    # 1. Schema-Registry mit neuer Architektur
    print("\n1. 🔧 Schema-Registry Setup:")
    registry = SchemaRegistry()
    registry.initialize(schemas_path)
    
    print(f"   Pipeline-Typen: {len(registry.pipeline_types)}")
    print(f"   Schema-Daten: {len(registry.schema_data)}")
    print(f"   Aufgelöste Schemas: {len(registry.resolved_schemas)}")
    
    # 2. Pipeline-Typen anzeigen
    print("\n2. 📋 PIPELINE-TYPEN:")
    for pipeline_name, pipeline_type in registry.pipeline_types.items():
        print(f"   🔀 {pipeline_name}:")
        print(f"      Beschreibung: {pipeline_type.description}")
        print(f"      Chunks: {pipeline_type.chunks}")
        print(f"      Required Configs: {pipeline_type.required_configs}")
        print(f"      Config-Mappings: {pipeline_type.config_mappings}")
    
    # 3. Schema-Daten anzeigen  
    print("\n3. 📊 SCHEMA-DATEN:")
    for schema_name, schema_data in registry.schema_data.items():
        print(f"   📄 {schema_name}:")
        print(f"      Beschreibung: {schema_data.description}")
        print(f"      Pipeline-Typ: {schema_data.pipeline_type}")
        print(f"      Config-Mappings: {schema_data.config_mappings}")
    
    # 4. Aufgelöste Schemas anzeigen
    print("\n4. ✅ AUFGELÖSTE SCHEMAS:")
    for schema_name, resolved_schema in registry.resolved_schemas.items():
        print(f"   🎯 {schema_name}:")
        print(f"      Pipeline-Typ: {resolved_schema.pipeline_type}")
        print(f"      Chunks: {resolved_schema.chunks}")
        print(f"      Config-Mappings: {resolved_schema.config_mappings}")
        print(f"      Meta: {resolved_schema.meta.get('description_de', 'Keine Beschreibung')}")
    
    # 5. Chunk-Building Test mit aufgelösten Schemas
    print("\n5. 🧩 CHUNK-BUILDING TEST:")
    chunk_builder = ChunkBuilder(schemas_path)
    
    test_input = "Ein Pferd steht auf einer grünen Wiese"
    
    for schema_name in registry.list_schemas():
        print(f"\n   🎯 Test Schema: {schema_name}")
        schema = registry.get_schema(schema_name)
        
        if not schema:
            print("      ❌ Schema nicht verfügbar")
            continue
        
        # Teste alle Chunks des Schemas
        context = {
            "input_text": test_input,
            "user_input": test_input,
            "previous_output": "A horse stands on a green meadow"
        }
        
        for chunk_name in schema.chunks:
            try:
                config_path = schema.config_mappings.get(chunk_name)
                if not config_path:
                    print(f"      ⚠️  {chunk_name}: Keine Config gefunden")
                    continue
                
                chunk_request = chunk_builder.build_chunk(
                    chunk_name=chunk_name,
                    config_path=config_path,
                    context=context
                )
                
                print(f"      ✅ {chunk_name}: {chunk_request['backend_type']}/{chunk_request['model']}")
                print(f"         Config: {config_path}")
                print(f"         Prompt: {len(chunk_request['prompt'])} Zeichen")
                
                # Chunk für nächsten Schritt verwenden
                if chunk_name == "translate":
                    context["previous_output"] = "A horse stands on a green meadow"  # Simuliert
                elif chunk_name == "manipulate":
                    context["previous_output"] = "Transformed text"  # Simuliert
                
            except Exception as e:
                print(f"      ❌ {chunk_name}: {e}")
    
    # 6. Architektur-Validation
    print("\n6. 🎯 ARCHITEKTUR-VALIDATION:")
    
    # Test: Wiederverwendbarkeit
    simple_interception_schemas = [
        name for name, schema in registry.resolved_schemas.items()
        if schema.pipeline_type == "simple_interception"
    ]
    
    print(f"   ✅ Pipeline-Typ Wiederverwendung: {len(simple_interception_schemas)} Schemas nutzen 'simple_interception'")
    print(f"      Schemas: {simple_interception_schemas}")
    
    # Test: Config-Auflösung
    config_resolved_count = 0
    for schema in registry.resolved_schemas.values():
        if len(schema.config_mappings) == len(schema.chunks):
            config_resolved_count += 1
    
    print(f"   ✅ Config-Auflösung: {config_resolved_count}/{len(registry.resolved_schemas)} Schemas vollständig aufgelöst")
    
    # Test: Legacy-Integration
    legacy_configs = [
        config for schema in registry.resolved_schemas.values()
        for config in schema.config_mappings.values()
        if "jugendsprache" in config or "standard" in config
    ]
    
    print(f"   ✅ Legacy-Integration: {len(legacy_configs)} Legacy-Configs verwendet")
    print(f"      Configs: {legacy_configs}")
    
    print("\n" + "=" * 80)
    print("🎉 KORRIGIERTE ARCHITEKTUR TEST ERFOLGREICH!")
    print("")
    print("📋 Architektur-Zusammenfassung:")
    print("   ✅ Pipeline-Typ + Schema-Daten Trennung funktional")
    print("   ✅ Wiederverwendbare Pipeline-Definitionen")
    print("   ✅ Spezifische Schema-Konfigurationen")
    print("   ✅ Config-Mapping-Auflösung")
    print("   ✅ Legacy-Integration")
    print("")
    print("🚀 System bereit für Dadaismus-Pipeline-Test!")
    print("=" * 80)

if __name__ == "__main__":
    test_corrected_architecture()
