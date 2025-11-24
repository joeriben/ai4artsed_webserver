# LTX-Video Model Setup für AI4ArtsEd

## Status
- ✅ ComfyUI-LTXVideo Extension installiert
- ✅ Backend-Config erstellt (`output_video_ltx.json`)
- ✅ Frontend aktiviert (Phase2 Interface)
- ❌ **Model noch nicht heruntergeladen**

## Model Download

### Option 1: Distilled 13B (EMPFOHLEN für Workshops)
**Schnellstes Model** - Nur 4-8 Steps nötig!

```bash
cd /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/checkpoints/
wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled.safetensors
```

**Specs:**
- Größe: ~26GB
- VRAM: 24GB+ empfohlen
- Generierungszeit: ~4-8 Steps (SEHR SCHNELL!)
- Qualität: Kinoreif

### Option 2: Distilled 13B Quantized (FÜR LIMITIERTES VRAM)
**Für Consumer-GPUs optimiert**

```bash
cd /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/checkpoints/
wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors
```

**Specs:**
- Größe: ~13GB
- VRAM: 16GB (läuft auf RTX 4090!)
- Benötigt: Q8 Kernels Installation (siehe unten)

### Option 3: Standard 2B (LEGACY - nicht empfohlen)
```bash
cd /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/checkpoints/
wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.safetensors
```

## Nach dem Download

### 1. Model-Namen in Config anpassen
Aktuell referenziert die Config: `ltx-video-2b-v0.9.safetensors`

**Für Distilled 13B:**
```bash
# In devserver/schemas/chunks/output_video_ltx.json ändern:
"ckpt_name": "ltxv-13b-0.9.7-distilled.safetensors"
```

**Für Quantized:**
```bash
"ckpt_name": "ltxv-13b-0.9.7-distilled-fp8.safetensors"
```

### 2. (Optional) Q8 Kernels für Quantized Models
Nur nötig für FP8-quantisierte Modelle:

```bash
cd /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI
source ../../venv/bin/activate  # Falls venv verwendet wird
pip install git+https://github.com/Lightricks/LTXVideo-Q8-Kernels.git
```

### 3. Workflow-Anpassungen für Distilled Model
Distilled Models benötigen **weniger Steps**:
- Normale Models: 25 Steps
- Distilled: **4-8 Steps**

In `output_video_ltx.json` anpassen:
```json
"steps": {
  "default": 6,  // statt 25!
  "description": "Distilled model needs only 4-8 steps"
}
```

## Testing

Nach dem Download und Config-Update:

1. Backend neu starten (lädt neue Configs)
2. Phase2 Interface öffnen
3. Video-Kategorie → ⚡ LTX Video auswählen
4. Test-Prompt: "A red car driving through a forest, cinematic camera movement"

## Troubleshooting

### Model lädt nicht
```bash
# Check ob Model existiert:
ls -lh /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/checkpoints/ltxv*

# ComfyUI Logs checken:
tail -f /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/comfyui.log
```

### VRAM-Fehler
→ Verwende quantisierte Version (FP8)
→ Reduziere Resolution: 1216x704 → 768x512

### Langsame Generation
→ Stelle sicher dass Distilled Model verwendet wird
→ Reduziere Steps auf 6

## Links
- [LTX-Video HuggingFace](https://huggingface.co/Lightricks/LTX-Video)
- [ComfyUI-LTXVideo GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo)
- [Q8 Kernels](https://github.com/Lightricks/LTXVideo-Q8-Kernels)
