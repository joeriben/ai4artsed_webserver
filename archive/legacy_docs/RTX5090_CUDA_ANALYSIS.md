# RTX 5090 CUDA Setup für LORA Training

## Problem
- RTX 5090: CUDA Compute Capability SM_120 (Blackwell Architecture)
- PyTorch 2.6.0: Unterstützt nur bis SM_90
- PyTorch 2.9.0 dev: Unterstützt SM_120 ✓

## Lösung
ComfyUI nutzt bereits PyTorch 2.9.0.dev20250807+cu128 → **funktioniert**

Für LoRA Training: PyTorch Nightly mit CUDA 12.4+ erforderlich

## Installation
```bash
cd /home/joerissen/ai/kohya_ss
source venv311/bin/activate
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124
```

## Status
- **ComfyUI:** ✓ Bereit (kann LoRAs laden und verwenden)
- **kohya_ss:** ✗ PyTorch zu alt (SM_120 nicht unterstützt)
