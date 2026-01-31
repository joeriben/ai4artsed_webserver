# Session 149 Handover: Triton/Diffusers Backend Implementation

## Zusammenfassung

Session 149 implementierte alternative Inference-Backends (Triton, Diffusers) für SwarmUI/ComfyUI-Unabhängigkeit. PyTorch + Blackwell GPU funktioniert, aber der Diffusers-Wrapper hat noch einen Bug.

---

## Was wurde gemacht

### 1. Backend-Infrastruktur (COMMITTED: `7e39253`)

**Neue Dateien:**
- `my_app/services/triton_client.py` - Triton Inference Server Client
- `my_app/services/diffusers_backend.py` - HuggingFace Diffusers Backend (**HAT BUG**)
- `schemas/chunks/output_image_sd35_triton.json` - Triton Output Config
- `schemas/chunks/output_image_sd35_diffusers.json` - Diffusers Output Config

**Geänderte Dateien:**
- `config.py` - TRITON_* und DIFFUSERS_* Konfiguration hinzugefügt
- `schemas/engine/backend_router.py` - Routing für neue Backends

### 2. Triton Setup

**Erledigt:**
- Docker Image: `nvcr.io/nvidia/tritonserver:24.08-py3` ✓
- NVIDIA Container Toolkit installiert ✓
- Model Repository: `~/ai/triton_models/` mit Struktur ✓
- Startup Script: `~/ai/start_triton.sh` ✓

**NICHT erledigt:**
- TensorRT-Konvertierung für SD3.5 scheiterte an dynamischen Shapes
- Triton kann SD3.5 NICHT ausführen ohne funktionierende .plan Dateien

### 3. PyTorch + Blackwell

**FUNKTIONIERT:**
```bash
# PyTorch 2.11.0 mit CUDA 13.0 installiert
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu130
```

**Beweis (direkter Test funktionierte):**
```python
from diffusers import StableDiffusion3Pipeline
pipe = StableDiffusion3Pipeline.from_pretrained('stabilityai/stable-diffusion-3.5-large', torch_dtype=torch.float16)
pipe = pipe.to('cuda')
# Generiert Bild in <1s (5 steps), 28GB VRAM
```

### 4. ONNX Export

**Erledigt:**
- `~/ai/sd35_onnx/transformer.onnx` (16GB)
- `~/ai/sd35_onnx/vae_decoder.onnx` (95MB)
- `~/ai/sd35_onnx/vae_encoder.onnx` (66MB)

---

## Was NICHT funktioniert / TODO

### KRITISCH: diffusers_backend.py Bug

Der Wrapper-Service generiert keine Bilder. Direkter Diffusers-Aufruf funktioniert, aber `DiffusersImageGenerator` Klasse nicht.

**Problem lokalisieren:**
```bash
cd ~/ai/ai4artsed_development/devserver
DIFFUSERS_ENABLED=true python -c "
import asyncio
from my_app.services.diffusers_backend import get_diffusers_backend

async def test():
    backend = get_diffusers_backend()
    # Debug hier...

asyncio.run(test())
"
```

**Vermuteter Bug:** Async/await Handling in `generate_image()` oder `load_model()` - der `run_in_executor` Call blockiert möglicherweise.

### TensorRT Konvertierung

SD3.5 hat dynamische Shapes die TensorRT nicht direkt handeln kann. Benötigt:
1. Feste Shape-Profile (nicht trivial bei SD3.5)
2. Oder: Diffusers+torch.compile als Alternative

---

## Dateien zum Anschauen

| Datei | Zweck |
|-------|-------|
| `my_app/services/diffusers_backend.py` | **BUG FIXEN** |
| `config.py:297-340` | Triton/Diffusers Config |
| `schemas/engine/backend_router.py:480-510` | Routing-Logik |
| `~/ai/convert_sd35_triton.py` | Konvertierungs-Script |
| `~/ai/trt_final_build.log` | TensorRT Fehler-Log |

---

## Nächste Schritte

1. **Bug in diffusers_backend.py fixen**
   - `generate_image()` Methode debuggen
   - Async/Executor Problem lösen

2. **Config aktivieren:**
   ```python
   # In config.py ändern:
   DIFFUSERS_ENABLED = True
   ```

3. **Testen:**
   ```bash
   cd ~/ai/ai4artsed_development/devserver
   python -m pytest tests/ -k diffusers  # Falls Tests existieren
   ```

4. **Optional: Triton für andere Modelle**
   - Flux, SDXL haben evtl. einfachere Shapes

---

## Commits dieser Session

```
7e39253 feat(backend): Add Triton and Diffusers alternative inference backends
e4cf329 feat(edutainment): Add GPU stats visualization and educational facts system
```

---

## Environment Notes

- **GPU:** NVIDIA RTX PRO 6000 Blackwell (98GB VRAM)
- **CUDA:** 13.0
- **PyTorch:** 2.11.0.dev20260130+cu130 (Nightly)
- **Python:** 3.13
- **OS:** Fedora 42
