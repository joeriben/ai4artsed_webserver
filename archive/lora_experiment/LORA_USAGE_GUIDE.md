# LoRA Verwendung mit ComfyUI

## System-Status

✅ **ComfyUI läuft** mit PyTorch 2.9.0 dev + CUDA 12.8
✅ **RTX 5090 wird erkannt** (22GB VRAM in Nutzung)
✅ **LoRAs können geladen und verwendet werden**

## LoRA-Verzeichnis

Lege LoRA-Dateien (.safetensors) hier ab:
```
/home/joerissen/ai/SwarmUI/Models/Lora/
```

ODER (für ComfyUI direkt):
```
/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/models/loras/
```

## LoRAs finden und herunterladen

**Civitai:** https://civitai.com/models?types=LORA
**HuggingFace:** https://huggingface.co/models?pipeline_tag=text-to-image&other=lora

Beispiel-Download:
```bash
cd /home/joerissen/ai/SwarmUI/Models/Lora/
wget https://civitai.com/api/download/models/XXXXX -O mein_lora.safetensors
```

## In ComfyUI verwenden

1. ComfyUI aufrufen (läuft bereits auf Port 7860)
2. **Load LoRA** Node hinzufügen
3. LoRA aus Dropdown wählen
4. **LoRA Strength** einstellen (0.5 - 1.0)
5. Mit Model und CLIP verbinden
6. Trigger-Wörter im Prompt nutzen

## Wichtig

- LoRA-Training ist NICHT auf diesem System (RTX 5090 braucht PyTorch Nightly)
- Für Training: Nutze externe Services oder ein anderes System
- Diese Maschine ist **perfekt zum VERWENDEN** von LoRAs

## ComfyUI Status

Prüfe Status:
```bash
ps aux | grep ComfyUI
```

Wenn ComfyUI nicht läuft:
```bash
cd /home/joerissen/ai/SwarmUI
./launch-linux.sh
```

## Fertig!

Das System ist jetzt bereit, LoRAs zu verwenden. Einfach LoRA-Dateien ins Verzeichnis legen und in ComfyUI laden.
