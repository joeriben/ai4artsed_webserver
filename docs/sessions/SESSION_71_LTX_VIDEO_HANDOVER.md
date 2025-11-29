# Session 71 Handover: LTX-Video Integration

**Date**: 2025-11-25
**Branch**: `develop`
**Commit**: `eeb6176`

---

## Was wurde in dieser Session gemacht?

### 1. Initiale Anfrage
User wollte: "GPT Image 1 Stage4-Config, aber mit OpenAI Sora als Videolösung"

### 2. Problem erkannt
- **OpenAI Sora API existiert nicht öffentlich** (404 Fehler)
- Keine verfügbare REST API für Sora (Stand Nov 2025)
- Nur über ChatGPT-Subscriptions oder Third-Party Aggregatoren zugänglich

### 3. Alternative evaluiert
Recherche nach zugänglichen Video-Modellen:
- ❌ OpenRouter: Keine Video-Generierung
- ❌ Runway, Luma: Separate APIs mit Kosten
- ✅ **LTX-Video (Lightricks)**: Open-source, lokal via ComfyUI

**LTX-Video Vorteile**:
- Open-source (Apache 2.0)
- Läuft lokal über vorhandenes ComfyUI/SwarmUI
- Extension bereits installiert: `ComfyUI-LTXVideo`
- Sehr schnell: 5-15 sec (Distilled: 4-8 Steps!)
- Workshop-geeignet: Consumer GPU friendly (FP8 = 16GB VRAM)

### 4. Implementation durchgeführt

#### Backend
✅ **Neuer Chunk erstellt**: `devserver/schemas/chunks/output_video_ltx.json`
- ComfyUI Workflow JSON mit 9 Nodes:
  - `LTXVCheckpointLoader` (Model)
  - `LTXVImgToVideo` (Settings: 1216x704, 121 frames)
  - `KSampler` (25 steps, CFG 3.0)
  - `CLIPTextEncode` (positive/negative)
  - `VAEDecode`
  - `VHS_VideoCombine` (30fps output)
- Input mappings für alle Parameter
- Output mapping für Video-File

✅ **Config migriert**: `sora_video.json` → `ltx_video.json`
- Backend: `openai` → `comfyui`
- `OUTPUT_CHUNK`: `output_video_sora` → `output_video_ltx`
- Parameters angepasst (WIDTH, HEIGHT, FRAMES, STEPS, CFG, FPS)
- Meta updated (GPU required, VRAM 16GB, duration 5-15 sec)

✅ **Alt-Dateien deprecated**:
- `output_video_sora.json.DEPRECATED`

#### Frontend
✅ **Vue Config updated**: `text_transformation.vue`
- Video-Kategorie aktiviert (war disabled)
- Config-ID: `sora_video` → `ltx_video`
- Label: "LTX Video"
- Icon: ⚡ (statt 🎬)
- Description: "Schnelle lokale Videogenerierung"

#### Dokumentation
✅ **Setup-Guide erstellt**: `docs/LTX_VIDEO_MODEL_SETUP.md`
- 3 Model-Optionen dokumentiert
- Download-Links (HuggingFace)
- Q8 Kernels Installation
- Troubleshooting

---

## Aktueller Status

### Was funktioniert
✅ Backend-Code komplett (Workflow, Config, Mappings)
✅ Frontend aktiviert (UI zeigt LTX Video an)
✅ ComfyUI-LTXVideo Extension bereits installiert
✅ Git committed & dokumentiert

### Was NICHT funktioniert
❌ **LTX-Video Model nicht heruntergeladen**
❌ **Integration nicht getestet** (kann nicht laufen ohne Model)

---

## Tasks für nächste Session

### Task 1: LTX-Video Model Installation (PRIORITÄT 1)

**WICHTIG**: Recherche VORHER wie das für SwarmUI korrekt geht!

#### Recherche-Fragen klären:
1. **Wo speichert SwarmUI Models?**
   - Standard: `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/checkpoints/`
   - Oder separates SwarmUI Models-Directory?
   - Check: SwarmUI Settings/Config für Model-Pfade

2. **Welches LTX-Model ist optimal?**
   - `ltxv-13b-0.9.7-distilled.safetensors` (26GB, schnellst, 4-8 steps)
   - `ltxv-13b-0.9.7-distilled-fp8.safetensors` (13GB, quantized, RTX 4090)
   - Legacy `ltx-video-2b-v0.9.safetensors` (veraltet, NICHT verwenden)

   **Empfehlung**: Distilled FP8 für Balance Speed/VRAM

3. **Braucht SwarmUI spezielle Model-Registration?**
   - Muss Model in SwarmUI UI registriert werden?
   - Oder reicht ComfyUI checkpoints Directory?
   - Check: SwarmUI Model Management

4. **Q8 Kernels nötig für FP8?**
   - README sagt: "Important: install q8_kernels for quantized"
   - Aber neuere Versionen: "running natively in ComfyUI"
   - Test: Mit und ohne Q8 Kernels probieren

#### Installation Steps (NACH Recherche):

```bash
# 1. Model Download (Beispiel für FP8)
cd /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/checkpoints/
wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors

# 2. (Optional) Q8 Kernels falls nötig
cd /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI
source ../../venv/bin/activate  # Falls venv
pip install git+https://github.com/Lightricks/LTXVideo-Q8-Kernels.git

# 3. Verify installation
ls -lh models/checkpoints/ltxv*
```

#### Config-Update nach Download:

File: `devserver/schemas/chunks/output_video_ltx.json`

```json
{
  "3": {
    "inputs": {
      "ckpt_name": "ltxv-13b-0.9.7-distilled-fp8.safetensors"  // ← Aktuellen Dateinamen eintragen
    },
    "class_type": "LTXVCheckpointLoader"
  }
}
```

**Falls Distilled Model verwendet**:
- Steps reduzieren: `"default": 6` (statt 25)
- In Config und Chunk anpassen

---

### Task 2: DevServer Integration Testing (PRIORITÄT 2)

#### Test-Workflow:
1. **Backend Restart** (lädt neue Configs):
   ```bash
   cd /home/joerissen/ai/ai4artsed_webserver
   ./1_stop_all.sh
   ./3_start_backend_dev.sh
   ```

2. **Config-Loading prüfen**:
   ```bash
   # Check ob ltx_video.json geladen wird
   curl http://localhost:17802/api/schema/configs/output | jq '.[] | select(.id == "ltx_video")'
   ```

3. **Frontend Test** (Phase2 Interface):
   - http://localhost:5173
   - Video-Kategorie auswählen
   - ⚡ LTX Video sollte sichtbar sein

4. **End-to-End Test**:
   ```bash
   curl -X POST http://localhost:17802/api/schema/pipeline/execute \
     -H "Content-Type: application/json" \
     -d '{
       "schema": "dada",
       "input_text": "A red car driving through a forest",
       "output_config": "ltx_video",
       "execution_mode": "eco",
       "safety_level": "youth",
       "user_language": "en"
     }'
   ```

#### Erwartetes Verhalten:
1. Stage 1-3: Text-Processing (wie bei Images)
2. Stage 4: ComfyUI Workflow execution
3. Output: Video file (MP4) in run directory

#### Mögliche Fehler & Fixes:

**Error: "Model not found"**
→ Check `ckpt_name` in chunk matches downloaded file
→ Verify ComfyUI can see the model: SwarmUI UI → Models

**Error: "Node LTXVCheckpointLoader not found"**
→ ComfyUI-LTXVideo extension nicht geladen
→ Restart ComfyUI backend

**Error: "VHS_VideoCombine not found"**
→ Video Helper Suite Extension fehlt
→ Install: `cd custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite`

**Error: "CUDA out of memory"**
→ Resolution reduzieren: 1216x704 → 768x512
→ Oder: FP8 quantized model verwenden

**Generation zu langsam (>60 sec)**
→ Check ob Distilled Model verwendet wird
→ Steps auf 6 reduzieren (nicht 25!)

---

## Architektur-Referenz

### File-Struktur
```
devserver/schemas/
├── chunks/
│   ├── output_video_ltx.json          ← ComfyUI Workflow + Mappings
│   └── output_video_sora.json.DEPRECATED
├── configs/
│   └── output/
│       ├── ltx_video.json             ← High-level Config
│       └── sora_video.json (deleted)
└── engine/
    ├── backend_router.py              ← Routes zu ComfyUI
    └── pipeline_executor.py           ← Führt Workflow aus

public/ai4artsed-frontend/src/views/
└── text_transformation.vue            ← Frontend Config-Selection
```

### Workflow-Flow
1. **User wählt**: Phase2 UI → Video → ⚡ LTX Video
2. **Config geladen**: `ltx_video.json` → `OUTPUT_CHUNK: "output_video_ltx"`
3. **Chunk geladen**: `output_video_ltx.json` → ComfyUI Workflow JSON
4. **Backend Router**: Sendet Workflow an SwarmUI ComfyUI Backend
5. **ComfyUI**: Führt Workflow aus (Model load, Sample, Decode, Save)
6. **Output**: Video file zurück zu DevServer → Frontend

### Bestehende ComfyUI-Integration
- **Pattern**: Identisch zu SD3.5 Large (`output_image_sd35_large.json`)
- **Backend**: `backend_router.py` hat bereits ComfyUI-Support
- **Communication**: HTTP API zu SwarmUI/ComfyUI
- **Keine Änderungen nötig**: Backend-Code ist generic

---

## Wichtige Hinweise

### DO NOT
- ❌ NICHT "ltx-video-2b-v0.9.safetensors" verwenden (veraltet)
- ❌ NICHT Node-Namen ändern (müssen zu ComfyUI-LTXVideo passen)
- ❌ NICHT Steps >10 bei Distilled Models (ineffizient)

### DO
- ✅ Recherche VORHER: SwarmUI Model-Handling
- ✅ FP8 quantized bevorzugen (schneller, weniger VRAM)
- ✅ Steps auf 6 bei Distilled Models
- ✅ Logs checken: SwarmUI + DevServer Backend

### Debug-Commands
```bash
# SwarmUI Status
ps aux | grep -i swarm

# ComfyUI Backend Logs
tail -f /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/comfyui.log

# DevServer Backend Logs
tail -f /home/joerissen/ai/ai4artsed_webserver/devserver/logs/backend.log

# Check Models in ComfyUI
curl http://localhost:7820/object_info | jq '.LTXVCheckpointLoader'
```

---

## Ressourcen

### Dokumentation
- `docs/LTX_VIDEO_MODEL_SETUP.md` (diese Session)
- `devserver/schemas/chunks/output_video_ltx.json` (Workflow)
- `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/custom_nodes/ComfyUI-LTXVideo/README.md`

### External Links
- [LTX-Video HuggingFace](https://huggingface.co/Lightricks/LTX-Video)
- [ComfyUI-LTXVideo GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo)
- [Q8 Kernels](https://github.com/Lightricks/LTXVideo-Q8-Kernels)
- [SwarmUI Docs](https://swarmui.net/)

### Example Workflows
Check ComfyUI-LTXVideo für Referenz-Workflows:
```bash
ls /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/custom_nodes/ComfyUI-LTXVideo/example_workflows/
```

---

## Success Criteria

Session erfolgreich wenn:
1. ✅ LTX Model heruntergeladen & in ComfyUI verfügbar
2. ✅ Config zeigt korrekten Model-Namen
3. ✅ DevServer Backend startet ohne Fehler
4. ✅ Phase2 UI zeigt "⚡ LTX Video"
5. ✅ Test-Generation produziert Video-File
6. ✅ Video spielt ab (4 sec, 30fps, sinnvoller Content)

---

## Commit Reference
```
feat: Replace Sora with LTX-Video for local video generation
Commit: eeb6176
Branch: develop
Files changed: 21 files, +1585/-99 lines
```

---

**Next Session**: START WITH RESEARCH! → SwarmUI Model Installation Best Practices
