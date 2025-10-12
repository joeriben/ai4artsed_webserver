# ComfyUI Integration Testing Guide

## Test-Übersicht

Es gibt 3 Test-Stufen, die Sie nacheinander ausführen können:

### 1. **Connection Test** (Einfachster Test)
```bash
cd devserver
python TEST_comfyui_simple.py
```

**Was wird getestet:**
- ✅ Auto-Discovery findet ComfyUI
- ✅ Health-Check bestätigt Verbindung
- ✅ Queue-Status abrufbar

**Voraussetzungen:** Nur ComfyUI/SwarmUI muss laufen

---

### 2. **Workflow Generation Test** (Mittlere Stufe)
```bash
cd devserver
python TEST_comfyui_workflow_only.py
```

**Was wird getestet:**
- ✅ Workflow-Generator erstellt SD 3.5 Workflow
- ✅ Workflow wird an ComfyUI gesendet
- ✅ Prompt-ID wird zurückgegeben
- 📄 Workflow-JSON wird gespeichert: `TEST_workflow_output.json`

**Voraussetzungen:** ComfyUI/SwarmUI muss laufen
**KEIN Ollama nötig!** Verwendet direkt einen Test-Prompt.

**Ergebnis:** 
- Workflow in ComfyUI-Queue
- Bild wird in ComfyUI generiert (check SwarmUI/ComfyUI Output)

---

### 3. **Full Pipeline Test** (Kompletter Test)
```bash
cd devserver
python TEST_full_comfyui_pipeline.py
```

**Was wird getestet:**
- ✅ Dadaismus-Transformation mit Ollama
- ✅ Workflow-Generierung
- ✅ ComfyUI-Submission
- ✅ Warten auf Fertigstellung
- ✅ Bild-Download
- 🖼️ Generiertes Bild wird gespeichert: `TEST_generated_image_*.png`

**Voraussetzungen:** 
- ✅ ComfyUI/SwarmUI läuft
- ✅ Ollama läuft (für Dadaismus-Transformation)
- ✅ Mistral-Nemo Modell verfügbar

**Ergebnis:** Komplette Pipeline von deutschem Text → Bild

---

## Port-Auto-Discovery

Der Client erkennt automatisch:
- **8188** - ComfyUI standalone
- **7821** - SwarmUI integrated ComfyUI
- **8189** - ComfyUI alternative
- **7860** - SwarmUI main

**Keine manuelle Konfiguration nötig!**

---

## Troubleshooting

### ComfyUI nicht gefunden
```bash
# Prüfen ob ComfyUI läuft
ps aux | grep -i comfy

# SwarmUI Port prüfen
ps aux | grep -i swarm
```

### Workflow-Submission schlägt fehl
- Prüfen Sie die ComfyUI-Logs
- Stellen Sie sicher, dass SD 3.5 Modell installiert ist
- Checkpoint-Pfad: `OfficialStableDiffusion/sd3.5_large.safetensors`

### Ollama-Verbindung fehlgeschlagen
```bash
# Ollama Status prüfen
ollama list

# Mistral-Nemo installieren (falls nötig)
ollama pull mistral-nemo
```

---

## Erwartete Ausgabe

### ✅ Erfolgreicher Test 2 (Workflow-Only):
```
COMFYUI WORKFLOW GENERATION TEST
======================================================================

Test Prompt: A flying camel over the Black Forest, dadaist art style

Step 1: Generate ComfyUI Workflow
----------------------------------------------------------------------
✓ Workflow generated successfully
  Nodes: 8
  Template: sd35_standard
  Saved to: TEST_workflow_output.json

Step 2: Check ComfyUI Connection
----------------------------------------------------------------------
  URL: http://127.0.0.1:7821
✓ ComfyUI is online

Step 3: Submit Workflow to ComfyUI
----------------------------------------------------------------------
✓ Workflow submitted successfully!
  Prompt ID: abc123...

======================================================================
SUCCESS! Workflow is in ComfyUI queue
======================================================================
```

---

## Nächste Schritte nach erfolgreichen Tests

1. **Web-Interface Integration** - Schema-Pipelines im Frontend
2. **Production Deployment** - Server mit vollständiger Pipeline
3. **Multi-Model Support** - FLUX, andere SD-Versionen

---

## Feedback

Bitte testen Sie die Tests in dieser Reihenfolge:
1. `TEST_comfyui_simple.py` → Connection OK?
2. `TEST_comfyui_workflow_only.py` → Workflow Submission OK?
3. `TEST_full_comfyui_pipeline.py` → Full Pipeline OK?

Bei Problemen: Ausgabe kopieren und analysieren.
