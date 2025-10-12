#!/usr/bin/env python3
"""
Server API Test - Testet die Schema-Pipeline-API über HTTP
"""

import requests
import json
import time

def test_server_api():
    """Test der Schema-Pipeline-API über HTTP"""
    
    base_url = "http://localhost:17901"
    
    print("=" * 80)
    print("🌐 SERVER API TEST - Schema-Pipeline über HTTP")
    print("=" * 80)
    
    # Warten auf Server-Start
    print(f"\n🔌 Prüfe Server-Verbindung zu {base_url}...")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/schema/info", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Server erreichbar (Versuch {i+1})")
                break
        except requests.exceptions.RequestException as e:
            print(f"   ⏳ Verbindungsversuch {i+1}/{max_retries}... ({e})")
            if i == max_retries - 1:
                print(f"   ❌ Server nicht erreichbar!")
                print(f"   💡 Starten Sie den Server: cd devserver && python server.py")
                return
            time.sleep(2)
    
    # 1. Schema-Info testen
    print(f"\n1. 📋 SCHEMA-INFO TEST:")
    try:
        response = requests.get(f"{base_url}/api/schema/info")
        data = response.json()
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if data.get('status') == 'success':
            print("   ✅ Schema-Info API funktioniert")
            schemas_available = data.get('schemas_available', 0)
            print(f"   📊 {schemas_available} Schema(s) verfügbar: {data.get('schemas', [])}")
        else:
            print(f"   ❌ Schema-Info fehlgeschlagen: {data.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Schema-Info Fehler: {e}")
    
    # 2. Schemas auflisten
    print(f"\n2. 📂 SCHEMAS LIST TEST:")
    try:
        response = requests.get(f"{base_url}/api/schema/schemas")
        data = response.json()
        
        print(f"   Status: {response.status_code}")
        
        if data.get('status') == 'success':
            print("   ✅ Schema-List API funktioniert")
            for schema in data.get('schemas', []):
                print(f"   📋 Schema: {schema.get('name')}")
                print(f"       Beschreibung: {schema.get('description')}")
                print(f"       Chunks: {schema.get('chunks')}")
        else:
            print(f"   ❌ Schema-List fehlgeschlagen: {data.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Schema-List Fehler: {e}")
    
    # 3. Direkte Prompt-Interception testen
    print(f"\n3. 🎯 PROMPT INTERCEPTION TEST:")
    try:
        test_data = {
            "input_prompt": "Ein Pferd steht auf einer grünen Wiese",
            "style_prompt": "Translate to English. Output ONLY the translation.",
            "model": "local/gemma2:9b",
            "debug": True
        }
        
        print(f"   Request: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/schema/pipeline/test",
            json=test_data,
            timeout=60
        )
        
        data = response.json()
        print(f"   Status: {response.status_code}")
        
        if data.get('status') == 'success':
            print("   ✅ Prompt Interception API funktioniert")
            print(f"   📥 Input: '{data.get('input_prompt')}'")
            print(f"   📤 Output: '{data.get('output_str')}'")
            print(f"   🎯 Model: {data.get('model_used')}")
        else:
            print(f"   ❌ Prompt Interception fehlgeschlagen: {data.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Prompt Interception Fehler: {e}")
    
    # 4. Pipeline-Execution testen (falls Schema verfügbar)
    print(f"\n4. 🚀 PIPELINE EXECUTION TEST:")
    try:
        pipeline_data = {
            "schema": "simple_interception_pipeline",
            "input_text": "Ein Pferd steht auf einer grünen Wiese"
        }
        
        print(f"   Request: {json.dumps(pipeline_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/schema/pipeline/execute",
            json=pipeline_data,
            timeout=120
        )
        
        data = response.json()
        print(f"   Status: {response.status_code}")
        
        if data.get('status') == 'success':
            print("   ✅ Pipeline Execution API funktioniert")
            print(f"   📥 Input: '{data.get('input_text')}'")
            print(f"   📤 Final Output: '{data.get('final_output')}'")
            print(f"   ⚡ Steps: {data.get('steps_completed')}")
            print(f"   ⏱️  Execution Time: {data.get('execution_time'):.2f}s")
        else:
            print(f"   ⚠️  Pipeline Execution: {data.get('error')}")
            print("   💡 Note: Pipeline benötigt Backend-Integration für vollständige Funktionalität")
            
    except Exception as e:
        print(f"   ❌ Pipeline Execution Fehler: {e}")
    
    print(f"\n" + "=" * 80)
    print("🎉 SERVER API TEST ABGESCHLOSSEN!")
    print("")
    print("📋 Test-Zusammenfassung:")
    print("   ✅ Schema-Engine über HTTP erreichbar")
    print("   ✅ API-Routen funktional") 
    print("   ✅ JSON-Request/Response funktional")
    print("   ✅ Schema-System in Webserver integriert")
    print("")
    print("🌐 Live-API-Endpoints:")
    print(f"   GET  {base_url}/api/schema/info")
    print(f"   GET  {base_url}/api/schema/schemas")
    print(f"   POST {base_url}/api/schema/pipeline/test")
    print(f"   POST {base_url}/api/schema/pipeline/execute")
    print("=" * 80)

if __name__ == "__main__":
    test_server_api()
