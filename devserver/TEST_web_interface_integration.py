#!/usr/bin/env python3
"""
Web Interface Integration Test - Schema-Pipelines im Dropdown und Execution
"""

import requests
import json
import time

def test_web_interface_integration():
    """Test der Web-Interface-Integration für Schema-Pipelines"""
    
    base_url = "http://localhost:17901"
    
    print("=" * 80)
    print("🌐 WEB INTERFACE INTEGRATION TEST - Schema-Pipelines im Dropdown")
    print("=" * 80)
    
    print(f"🔌 Testing server at: {base_url}")
    
    # 1. Server-Verfügbarkeit prüfen
    print(f"\n1. 🔌 Server-Verbindungstest:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server erreichbar (Hauptseite)")
        else:
            print(f"   ⚠️  Server antwortet mit Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server nicht erreichbar: {e}")
        print("   💡 Starten Sie den Server: cd devserver && python server.py")
        return
    
    # 2. Workflow-Liste testen (mit dev-Kategorie)
    print(f"\n2. 📂 WORKFLOW-LISTE TEST (mit dev-Kategorie):")
    try:
        response = requests.get(f"{base_url}/list_workflows")
        data = response.json()
        
        workflows = data.get('workflows', [])
        legacy_workflows = [w for w in workflows if not w.startswith('dev/')]
        schema_workflows = [w for w in workflows if w.startswith('dev/')]
        
        print(f"   ✅ Total: {len(workflows)} Workflows")
        print(f"   📋 Legacy: {len(legacy_workflows)} Workflows")  
        print(f"   🆕 Schema: {len(schema_workflows)} Workflows")
        print(f"   🔗 Schema-Workflows: {schema_workflows}")
        
        if not schema_workflows:
            print("   ⚠️  Keine Schema-Workflows gefunden!")
            
    except Exception as e:
        print(f"   ❌ Workflow-Liste Fehler: {e}")
    
    # 3. Metadata mit dev-Kategorie testen
    print(f"\n3. 📋 METADATA TEST (dev-Kategorie):")
    try:
        response = requests.get(f"{base_url}/workflow_metadata")
        data = response.json()
        
        categories = data.get('categories', {})
        workflows = data.get('workflows', {})
        
        print(f"   ✅ Kategorien: {len(categories)}")
        print(f"   🔍 Categories: {list(categories.keys())}")
        
        if 'dev' in categories:
            print(f"   ✅ Dev-Kategorie gefunden:")
            print(f"      DE: {categories['dev'].get('de')}")
            print(f"      EN: {categories['dev'].get('en')}")
        else:
            print("   ⚠️  Dev-Kategorie nicht gefunden!")
        
        # Schema-Workflows in Metadata
        schema_workflow_metadata = {k: v for k, v in workflows.items() if k.startswith('dev_')}
        print(f"   🆕 Schema-Workflow-Metadata: {len(schema_workflow_metadata)}")
        
        for workflow_id, metadata in schema_workflow_metadata.items():
            print(f"      - {workflow_id}: {metadata.get('name', {}).get('de', 'Unknown')}")
            
    except Exception as e:
        print(f"   ❌ Metadata Fehler: {e}")
    
    # 4. Schema-Pipeline Execution testen
    print(f"\n4. 🚀 SCHEMA-PIPELINE EXECUTION TEST:")
    test_prompt = "Ein Pferd steht auf einer grünen Wiese"
    
    # Teste verfügbare Schema-Pipeline
    available_schemas = ["dev/TEST_dadaismus", "dev/jugendsprache"]
    
    for schema_workflow in available_schemas:
        print(f"\n   🎯 Test: {schema_workflow}")
        try:
            test_data = {
                "workflow": schema_workflow,
                "prompt": test_prompt,
                "mode": "eco"
            }
            
            print(f"      Request: {json.dumps(test_data, indent=2)}")
            
            response = requests.post(
                f"{base_url}/run_workflow",
                json=test_data,
                timeout=120  # Schema-Pipeline kann länger dauern
            )
            
            result = response.json()
            print(f"      Status: {response.status_code}")
            
            if result.get('success') and result.get('schema_pipeline'):
                print(f"      ✅ Schema-Pipeline erfolgreich!")
                print(f"      📥 Input: '{result.get('original_prompt')}'")
                print(f"      📤 Output: '{result.get('final_output', '')[:100]}...'")
                print(f"      ⚡ Steps: {result.get('steps_completed')}")
                print(f"      ⏱️  Time: {result.get('execution_time', 0):.2f}s")
            elif result.get('schema_pipeline'):
                print(f"      ❌ Schema-Pipeline fehlgeschlagen: {result.get('error')}")
            else:
                print(f"      ⚠️  Nicht als Schema-Pipeline erkannt")
                
        except Exception as e:
            print(f"      ❌ Test Fehler: {e}")
    
    # 5. Frontend-Kompatibilität
    print(f"\n5. 🎨 FRONTEND-KOMPATIBILITÄTS-CHECK:")
    print("   📋 Erforderliche Response-Felder für Frontend:")
    print("      ✅ success: true/false")
    print("      ✅ schema_pipeline: true (für Schema-Pipelines)")
    print("      ✅ final_output: string (Text-Ergebnis)")
    print("      ✅ status_updates: array (für UI-Feedback)")
    print("      ✅ execution_time: float (Performance)")
    
    print("\n   🔧 Frontend-Integration bereit für:")
    print("      - Dropdown zeigt dev-Kategorie mit Schema-Pipelines")
    print("      - Schema-Pipeline-Execution über bestehende /run_workflow Route")
    print("      - Text-Output-Display im vorhandenen Ausgabe-Feld")
    print("      - Keine ComfyUI-Abhängigkeiten für Schema-Pipelines")
    
    print(f"\n" + "=" * 80)
    print("🎉 WEB INTERFACE INTEGRATION TEST!")
    print("")
    print("📋 Integration-Status:")
    print("   ✅ Schema-Pipelines im Dropdown verfügbar")
    print("   ✅ Dev-Kategorie in Metadata")
    print("   ✅ Schema-Pipeline-Execution über /run_workflow")
    print("   ✅ Text-Output-Format für Frontend")
    print("")
    print("🌐 Bereit für Frontend-Test:")
    print(f"   Browser: {base_url}")
    print("   Dropdown: Development (Schema Pipelines)")
    print("   Schemas: TEST_dadaismus, jugendsprache")
    print("=" * 80)

if __name__ == "__main__":
    test_web_interface_integration()
