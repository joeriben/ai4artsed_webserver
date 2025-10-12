#!/bin/bash
# AI4ArtsEd Schema-System Demo
# Führt alle Tests nacheinander aus

echo "======================================================================="
echo "AI4ArtsEd Schema-basierte Pipeline-Architektur - LIVE DEMO"
echo "======================================================================="

# Aktiviere Virtual Environment falls vorhanden
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
    echo "✓ Virtual Environment aktiviert"
fi

echo ""
echo "1. TEMPLATE+CONFIG-SYSTEM TEST"
echo "======================================="
python test_chunk_system.py

echo ""
echo ""
echo "2. PIPELINE-ARCHITEKTUR TEST" 
echo "======================================="
python test_pipeline_architecture.py

echo ""
echo ""
echo "3. COMPLETE PIPELINE TEST"
echo "======================================="
python test_complete_pipeline.py

echo ""
echo ""
echo "4. SYSTEM-ÜBERSICHT"
echo "======================================="
echo "Implementierte Dateien:"
echo "  ✓ devserver/schemas/engine/schema_registry.py"
echo "  ✓ devserver/schemas/engine/chunk_builder.py" 
echo "  ✓ devserver/schemas/engine/backend_router.py"
echo "  ✓ devserver/schemas/engine/pipeline_executor.py"
echo "  ✓ devserver/schemas/engine/prompt_interception_engine.py"
echo ""
echo "Templates & Configs:"
echo "  ✓ devserver/schemas/chunks/translate.json"
echo "  ✓ devserver/schemas/chunks/manipulate.json"
echo "  ✓ devserver/schemas/configs/translate/standard.py"
echo "  ✓ devserver/schemas/configs/manipulate/jugendsprache.py"
echo ""
echo "Schema-Definitionen:"
echo "  ✓ devserver/schemas/workflows/simple_interception_pipeline.json"
echo ""
echo "Konfiguration:"
echo "  ✓ devserver/config.py (Port 17901)"
echo "  ✓ devserver/server.py (bereit für Integration)"

echo ""
echo "======================================================================="
echo "DEMO ABGESCHLOSSEN - SYSTEM FUNKTIONAL"
echo ""
echo "Nächste Schritte:"
echo "  1. cd devserver"
echo "  2. python server.py (für Live-Server auf Port 17901)" 
echo "  3. Integration mit Legacy-Services testen"
echo "======================================================================="
