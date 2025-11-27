# AI4ArtsEd DevServer - Required AI Models

Complete list of all AI models required for AI4ArtsEd DevServer, including download URLs, checksums, and installation paths.

## Table of Contents
1. [Overview](#overview)
2. [Ollama Models](#ollama-models)
3. [Stable Diffusion 3.5](#stable-diffusion-35)
4. [CLIP Text Encoders](#clip-text-encoders)
5. [LTX-Video Model](#ltx-video-model)
6. [T5 Encoder for Video](#t5-encoder-for-video)
7. [Installation Paths Summary](#installation-paths-summary)
8. [Download Scripts](#download-scripts)
9. [Verification](#verification)

---

## Overview

### Total Disk Space Required

| Category | Size | Purpose |
|----------|------|---------|
| **Ollama Models** | ~29GB | Local LLM inference (translation, safety, analysis) |
| **SD3.5 + Encoders** | ~22GB | Image generation |
| **LTX-Video** | ~15GB | Video generation |
| **T5 Encoder (Video)** | ~11GB | Text encoding for video |
| **Total** | **~77GB** | All models combined |

### Download Time Estimates

| Connection Speed | Estimated Time |
|------------------|----------------|
| **1 Gbps** | 10-15 minutes |
| **100 Mbps** | 1.5-2 hours |
| **50 Mbps** | 3-4 hours |
| **10 Mbps** | 15-20 hours |

---

## Ollama Models

Ollama models are downloaded via the `ollama` CLI, not direct download.

### 1. gpt-OSS:20b

**Purpose:** Safety checks, translation, text processing
**Size:** ~21GB
**Model ID:** `gpt-OSS:20b`
**Provider:** Ollama model library

**Download:**
```bash
ollama pull gpt-OSS:20b
```

**Verification:**
```bash
ollama list | grep gpt-OSS
```

**Expected Output:**
```
gpt-OSS:20b    abc123def456    21 GB    2 minutes ago
```

**Used By:**
- Stage 1: Input translation (German → English)
- Stage 3: Safety validation
- Legacy workflows: Prompt interception

---

### 2. llama3.2-vision:latest

**Purpose:** Image analysis and vision tasks
**Size:** ~8GB
**Model ID:** `llama3.2-vision:latest`
**Provider:** Ollama model library (Meta Llama 3.2 Vision)

**Download:**
```bash
ollama pull llama3.2-vision:latest
```

**Verification:**
```bash
ollama list | grep llama3.2-vision
```

**Expected Output:**
```
llama3.2-vision:latest    def789ghi012    8.0 GB    1 minute ago
```

**Used By:**
- Stage 1: Image analysis
- Custom workflows: Visual understanding

---

## Stable Diffusion 3.5

### sd3.5_large.safetensors

**Purpose:** Primary image generation model
**Size:** 15.9GB
**Architecture:** Stable Diffusion 3.5 Large
**Resolution:** Up to 1024x1024 (native 768x768)
**Provider:** Stability AI

**Download URL:**
```
https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors
```

**SHA256 Checksum:**
```
TBD - Verify after download with: sha256sum sd3.5_large.safetensors
```

**Installation Path:**
```
/opt/ai4artsed/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors
```

**Download Command:**
```bash
mkdir -p /opt/ai4artsed/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion
cd /opt/ai4artsed/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion
wget https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors
```

**Faster Download (aria2c):**
```bash
aria2c -x 16 -s 16 https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors
```

**Used By:**
- Stage 4: Image generation (primary output config)
- Output configs: `sd35_large.json`

---

## CLIP Text Encoders

SD3.5 requires two CLIP text encoders for prompt understanding.

### 1. clip_g.safetensors

**Purpose:** CLIP-G text encoder for SD3.5
**Size:** 1.3GB
**Architecture:** OpenAI CLIP-G
**Provider:** Stability AI

**Download URL:**
```
https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/clip_g.safetensors
```

**SHA256 Checksum:**
```
TBD - Verify after download
```

**Installation Path:**
```
/opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/clip/clip_g.safetensors
```

**Download Command:**
```bash
cd /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/clip
wget https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/clip_g.safetensors
```

---

### 2. t5xxl_enconly.safetensors

**Purpose:** T5-XXL text encoder for SD3.5
**Size:** 4.6GB
**Architecture:** Google T5-XXL (encoder only)
**Provider:** Stability AI

**Download URL:**
```
https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/t5xxl_enconly.safetensors
```

**SHA256 Checksum:**
```
TBD - Verify after download
```

**Installation Path:**
```
/opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors
```

**Download Command:**
```bash
cd /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/clip
wget https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/t5xxl_enconly.safetensors
```

---

## LTX-Video Model

### ltxv-13b-0.9.7-distilled-fp8.safetensors

**Purpose:** Video generation (text-to-video, image-to-video)
**Size:** 14.8GB
**Architecture:** LTX-Video 13B (FP8 quantized)
**Resolution:** 768x512 (recommended), up to 1216x704
**FPS:** 24-25 default
**Steps:** 6 (distilled model - very fast)
**Provider:** Lightricks

**Download URL:**
```
https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors
```

**SHA256 Checksum:**
```
TBD - Verify after download
```

**Installation Path:**
```
/opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors
```

**Download Command:**
```bash
cd /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/checkpoints
wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors
```

**Faster Download:**
```bash
aria2c -x 16 -s 16 https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors
```

**Used By:**
- Stage 4: Video generation
- Output configs: `ltx_video.json`

**Generation Time:**
- 5-15 seconds for 25-frame video (768x512)
- RTX 5090: ~8 seconds average
- RTX 4090: ~12 seconds average

---

## T5 Encoder for Video

### t5xxl_fp16.safetensors

**Purpose:** Text encoder for LTX-Video model
**Size:** 10.9GB
**Architecture:** Google T5-XXL (FP16)
**Provider:** mcmonkey (HuggingFace)

**Download URL:**
```
https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/main/t5xxl_fp16.safetensors
```

**SHA256 Checksum:**
```
TBD - Verify after download
```

**Installation Path:**
```
/opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors
```

**Download Command:**
```bash
cd /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/clip
wget https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/main/t5xxl_fp16.safetensors
```

**Note:** This is a different T5 model than `t5xxl_enconly.safetensors` (SD3.5). Both are required.

---

## Installation Paths Summary

### Directory Structure

```
/opt/ai4artsed/SwarmUI/
├── Models/
│   └── Stable-Diffusion/
│       └── OfficialStableDiffusion/
│           └── sd3.5_large.safetensors (16GB)
│
└── dlbackend/ComfyUI/models/
    ├── clip/
    │   ├── clip_g.safetensors (1.3GB)
    │   ├── t5xxl_enconly.safetensors (4.6GB)
    │   └── t5xxl_fp16.safetensors (11GB)
    │
    └── checkpoints/
        ├── ltxv-13b-0.9.7-distilled-fp8.safetensors (15GB)
        └── OfficialStableDiffusion/ (symlink → ../../../Models/Stable-Diffusion/OfficialStableDiffusion)
```

### Required Symlink

```bash
cd /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/checkpoints
ln -s ../../../Models/Stable-Diffusion/OfficialStableDiffusion OfficialStableDiffusion
```

**Purpose:** Allows both SwarmUI and ComfyUI to access SD3.5 model using different path formats.

---

## Download Scripts

### Complete Download Script

Save as `download_models.sh`:

```bash
#!/bin/bash
set -e

BASE_PATH="/opt/ai4artsed/SwarmUI"

echo "=== AI4ArtsEd Model Downloader ==="
echo ""
echo "Total download: ~48GB"
echo "Estimated time: 30-60 minutes (100Mbps)"
echo ""

# Create directories
echo "[1/5] Creating directories..."
mkdir -p ${BASE_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion
mkdir -p ${BASE_PATH}/dlbackend/ComfyUI/models/clip
mkdir -p ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints

# Download SD3.5 Large
echo "[2/5] Downloading SD3.5 Large (16GB)..."
cd ${BASE_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion
if [ ! -f "sd3.5_large.safetensors" ]; then
    wget https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors
else
    echo "✓ Already downloaded"
fi

# Download CLIP encoders
echo "[3/5] Downloading CLIP encoders (6GB)..."
cd ${BASE_PATH}/dlbackend/ComfyUI/models/clip

if [ ! -f "clip_g.safetensors" ]; then
    wget https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/clip_g.safetensors
else
    echo "✓ clip_g already downloaded"
fi

if [ ! -f "t5xxl_enconly.safetensors" ]; then
    wget https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/t5xxl_enconly.safetensors
else
    echo "✓ t5xxl_enconly already downloaded"
fi

if [ ! -f "t5xxl_fp16.safetensors" ]; then
    echo "Downloading t5xxl_fp16.safetensors (11GB)..."
    wget https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/main/t5xxl_fp16.safetensors
else
    echo "✓ t5xxl_fp16 already downloaded"
fi

# Download LTX-Video
echo "[4/5] Downloading LTX-Video (15GB)..."
cd ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints
if [ ! -f "ltxv-13b-0.9.7-distilled-fp8.safetensors" ]; then
    wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors
else
    echo "✓ Already downloaded"
fi

# Create symlink
echo "[5/5] Creating symlink..."
cd ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints
if [ ! -L "OfficialStableDiffusion" ]; then
    ln -s ../../../Models/Stable-Diffusion/OfficialStableDiffusion OfficialStableDiffusion
    echo "✓ Symlink created"
else
    echo "✓ Symlink already exists"
fi

echo ""
echo "=== Download Complete! ==="
echo ""
echo "Verify installation:"
echo "  ls -lh ${BASE_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion/"
echo "  ls -lh ${BASE_PATH}/dlbackend/ComfyUI/models/clip/"
echo "  ls -lh ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints/"
```

**Run:**
```bash
chmod +x download_models.sh
./download_models.sh
```

---

## Verification

### Check All Models Exist

```bash
BASE_PATH="/opt/ai4artsed/SwarmUI"

# SD3.5 Large
ls -lh ${BASE_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors

# CLIP encoders
ls -lh ${BASE_PATH}/dlbackend/ComfyUI/models/clip/clip_g.safetensors
ls -lh ${BASE_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors
ls -lh ${BASE_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors

# LTX-Video
ls -lh ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors

# Symlink
ls -l ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints/OfficialStableDiffusion
```

### Expected Output

```
-rw-r--r-- 1 user user 16G Jan 15 10:30 sd3.5_large.safetensors
-rw-r--r-- 1 user user 1.3G Jan 15 10:45 clip_g.safetensors
-rw-r--r-- 1 user user 4.6G Jan 15 10:50 t5xxl_enconly.safetensors
-rw-r--r-- 1 user user 11G Jan 15 11:05 t5xxl_fp16.safetensors
-rw-r--r-- 1 user user 15G Jan 15 11:25 ltxv-13b-0.9.7-distilled-fp8.safetensors
lrwxrwxrwx 1 user user 68 Jan 15 11:30 OfficialStableDiffusion -> ../../../Models/Stable-Diffusion/OfficialStableDiffusion
```

### Calculate SHA256 Checksums

```bash
# SD3.5
sha256sum ${BASE_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors

# CLIP
sha256sum ${BASE_PATH}/dlbackend/ComfyUI/models/clip/clip_g.safetensors
sha256sum ${BASE_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors
sha256sum ${BASE_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors

# LTX-Video
sha256sum ${BASE_PATH}/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors
```

**Save checksums for verification after reinstallation.**

### Test Model Loading

```bash
# Start SwarmUI
cd /opt/ai4artsed/SwarmUI
./launch-linux.sh

# Watch logs for model loading
# Should see: "Loaded model: sd3.5_large"
# Press Ctrl+C after successful start
```

---

## Optional Models (Not Required)

These models are installed on the current system but not required for AI4ArtsEd:

### FLUX Models
- `flux1-schnell.safetensors` - Fast image generation
- `flux_dev.safetensors` - Development version

**Not configured** in AI4ArtsEd output configs.

### Stable Audio
- `stableaudio/model.safetensors` - Audio generation

**Config disabled** in current version.

### AceStep Audio
- `ace_step_v1_3.5b.safetensors` - Instrumental generation

**Referenced but not downloaded** - optional for future audio features.

---

## Troubleshooting

### Download Fails/Interrupted

**Resume with wget:**
```bash
wget -c [URL]
# -c flag resumes partial downloads
```

**Resume with aria2c:**
```bash
aria2c -c -x 16 -s 16 [URL]
# aria2c automatically resumes
```

### Checksum Mismatch

**Re-download the file:**
```bash
rm [filename]
wget [URL]
sha256sum [filename]
```

### Model Not Found by SwarmUI

**Check symlink:**
```bash
ls -l /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/checkpoints/OfficialStableDiffusion
# Should point to ../../../Models/Stable-Diffusion/OfficialStableDiffusion
```

**Recreate symlink:**
```bash
cd /opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/checkpoints
rm -f OfficialStableDiffusion
ln -s ../../../Models/Stable-Diffusion/OfficialStableDiffusion OfficialStableDiffusion
```

### Out of Disk Space

**Check space:**
```bash
df -h /opt
```

**Clean package caches:**
```bash
# Ubuntu/Debian
sudo apt clean

# Fedora
sudo dnf clean all

# Python pip cache
pip cache purge

# npm cache
npm cache clean --force
```

---

## Required Software Repositories

### SwarmUI + ComfyUI

- **SwarmUI:** https://github.com/mcmonkeyprojects/SwarmUI
  - Version: Latest from main (tested: commit 4c00e2a, 2025-11-22)
  - Includes integrated ComfyUI

### ComfyUI Custom Nodes

- **ComfyUI-LTXVideo:** https://github.com/Lightricks/ComfyUI-LTXVideo
  - Purpose: LTX-Video text-to-video generation
  - Required for video output

- **ai4artsed_comfyui:** https://github.com/joeriben/ai4artsed_comfyui_nodes
  - Purpose: Custom pedagogical nodes (prompt interception, safety filters)
  - Version: 0.7
  - License: EUPL-1.2

- **comfyui-sound-lab:** https://github.com/MixLabPro/comfyui-sound-lab
  - Purpose: Audio generation (AceStep, Stable Audio)
  - Optional for current version

---

## Model Information Sources

- **Stability AI:** https://huggingface.co/stabilityai
- **LTX-Video:** https://huggingface.co/Lightricks/LTX-Video
- **T5 Encoders:** https://huggingface.co/mcmonkey
- **Ollama Models:** https://ollama.com/library

---

## Next Steps

After downloading all models:
- Return to [INSTALLATION.md](INSTALLATION.md) to continue setup
- Configure paths in [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)
