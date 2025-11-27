# AI4ArtsEd DevServer - Software Versions Reference

Quick reference for all software versions and repository URLs used in AI4ArtsEd DevServer.

## Core Application

### Backend (Python/Flask)
- **Python:** 3.11+ (tested with 3.13)
- **Flask:** 3.0.0
- **Flask-CORS:** 4.0.0
- **waitress:** 2.1.2 (WSGI server)
- **requests:** 2.31.0
- **aiohttp:** 3.13.2
- **python-dotenv:** 1.0.0
- **weasyprint:** 60.2 (PDF export)
- **python-docx:** 1.1.0 (DOCX export)
- **lxml:** 5.1.0 (XML processing)

**Repository:** https://github.com/joerissenbenjamin/ai4artsed_webserver

---

### Frontend (Vue/TypeScript)
- **Vue.js:** 3.5.22 (Composition API)
- **Vite:** 7.1.11 (Build tool)
- **TypeScript:** 5.9.0
- **Pinia:** 3.0.3 (State management)
- **Vue Router:** 4.6.3
- **Vue i18n:** 9.14.5 (Internationalization)
- **Axios:** 1.13.2 (HTTP client)
- **Vitest:** 3.2.4 (Testing)
- **Playwright:** 1.56.1 (E2E testing)

**Location:** `public/ai4artsed-frontend/`

---

## External Services

### Ollama (Local LLM)
- **Version:** Latest stable
- **Installation:** `curl -fsSL https://ollama.com/install.sh | sh`
- **Port:** 11434
- **Website:** https://ollama.com

**Required Models:**
- `gpt-OSS:20b` (~21GB) - Safety checks, translation
- `llama3.2-vision:latest` (~8GB) - Image analysis

---

### SwarmUI (Image/Video Generation)
- **Repository:** https://github.com/mcmonkeyprojects/SwarmUI
- **Version:** Latest from main branch
  - Tested: commit `4c00e2a` (2025-11-22)
- **API Port:** 7801
- **ComfyUI Port:** 7821 (integrated)

**Installation:**
```bash
git clone https://github.com/mcmonkeyprojects/SwarmUI.git
cd SwarmUI
./install-linux.sh
```

---

## ComfyUI Custom Nodes

### 1. ComfyUI-LTXVideo
**Purpose:** Video generation (LTX-Video model support)

- **Repository:** https://github.com/Lightricks/ComfyUI-LTXVideo
- **Version:** Latest from main
- **Required:** Yes (for video output)

**Installation:**
```bash
cd SwarmUI/dlbackend/ComfyUI/custom_nodes
git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git
cd ComfyUI-LTXVideo
pip install -r requirements.txt
```

---

### 2. ai4artsed_comfyui
**Purpose:** Custom pedagogical nodes for AI4ArtsEd workflows

- **Repository:** https://github.com/joeriben/ai4artsed_comfyui_nodes
- **Version:** 0.7
- **License:** EUPL-1.2
- **Author:** Prof. Dr. Benjamin Jörissen
- **Required:** Yes (core functionality)

**Nodes Provided:**
- `ai4artsed_openrouter_key` - Secure API key management
- `ai4artsed_t5_clip_fusion` - Conditioning blending
- `ai4artsed_prompt_interception` - LLM-based prompt transformation
- `ai4artsed_switch_promptsafety` - Safety filters
- `ai4artsed_image_analysis` - Vision LLM analysis
- Additional text/random generators

**Dependencies:**
- `ollama` (Python client)
- `requests`

**Installation:**
```bash
cd SwarmUI/dlbackend/ComfyUI/custom_nodes
git clone https://github.com/joeriben/ai4artsed_comfyui_nodes.git ai4artsed_comfyui
cd ai4artsed_comfyui
pip install -r requirements.txt
```

---

### 3. comfyui-sound-lab
**Purpose:** Audio generation (MusicGen, Stable Audio, AceStep)

- **Repository:** https://github.com/MixLabPro/comfyui-sound-lab
- **Version:** Latest from main
- **Required:** Optional (audio features not fully integrated)

**Nodes Provided:**
- `SaveAudioMP3` - Audio output
- `TextEncodeAceStepAudio` - AceStep text encoding
- `VAEDecodeAudio` - Audio VAE
- `EmptyAceStepLatentAudio` - Latent initialization

**Special Requirements:**
- `flash-attention` (v2.5.2) - May fail on some systems
- `audiotools` with protobuf constraints
- Windows: Requires MSVC + ninja

**Installation:**
```bash
cd SwarmUI/dlbackend/ComfyUI/custom_nodes
git clone https://github.com/MixLabPro/comfyui-sound-lab.git
cd comfyui-sound-lab
pip install -r requirements.txt || echo "Some dependencies optional"
```

---

## AI Models

### Stable Diffusion 3.5 Large
- **Source:** https://huggingface.co/stabilityai/stable-diffusion-3.5-large
- **Model File:** `sd3.5_large.safetensors` (15.9GB)
- **License:** Stability AI Community License

### CLIP Text Encoders
- **clip_g.safetensors** (1.3GB)
  - Source: https://huggingface.co/stabilityai/stable-diffusion-3.5-large
- **t5xxl_enconly.safetensors** (4.6GB)
  - Source: https://huggingface.co/stabilityai/stable-diffusion-3.5-large
- **t5xxl_fp16.safetensors** (10.9GB)
  - Source: https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly

### LTX-Video
- **Source:** https://huggingface.co/Lightricks/LTX-Video
- **Model File:** `ltxv-13b-0.9.7-distilled-fp8.safetensors` (14.8GB)
- **Version:** 0.9.7 (distilled, FP8 quantized)
- **License:** Apache 2.0

---

## System Requirements

### Operating System
- **Supported:**
  - Ubuntu 22.04+ (LTS recommended)
  - Fedora 38, 39, 40
  - Arch Linux (rolling)
- **Tested:** Ubuntu 22.04, Fedora 40

### Node.js
- **Required Version:** v20.19.0+ OR v22.12.0+
- **npm:** 9.x or 10.x

### NVIDIA Drivers
- **CUDA Version:** 12.0+ required
- **Driver Version:** 535+ recommended
- **GPU:** RTX 4090/5090 (16GB+ VRAM)

---

## Build Tools

### Python Build Dependencies (Ubuntu/Debian)
```
build-essential
libcairo2-dev
libpango1.0-dev
libjpeg-dev
libgif-dev
libgirepository1.0-dev
```

### Python Build Dependencies (Fedora)
```
gcc
make
cairo-devel
pango-devel
libjpeg-devel
giflib-devel
gobject-introspection-devel
```

---

## Version Verification Commands

```bash
# Python
python3 --version
pip list | grep -E "Flask|waitress|weasyprint"

# Node.js / Frontend
node --version
npm --version
cd public/ai4artsed-frontend && npm list vue vite pinia

# Ollama
ollama --version
ollama list

# SwarmUI
cd /path/to/SwarmUI && git log -1 --format="%h %cd" --date=short

# NVIDIA
nvidia-smi
nvidia-smi | grep "CUDA Version"

# Custom Nodes
ls -la SwarmUI/dlbackend/ComfyUI/custom_nodes/
```

---

## API Services (External)

### OpenRouter
- **Website:** https://openrouter.ai
- **API Docs:** https://openrouter.ai/docs
- **Get API Key:** https://openrouter.ai/keys
- **Cost:** Pay-per-use, ~$0.001-0.01 per request

**Models Used:**
- `anthropic/claude-haiku-4.5` - Fast, cheap ($0.003/1M tokens)
- `anthropic/claude-sonnet-4.5` - High-quality ($0.03/1M tokens)
- `google/gemini-2.5-flash-lite` - Very fast, multimodal
- `mistralai/mistral-nemo` - Alternative fast model

### OpenAI (Optional)
- **Website:** https://platform.openai.com
- **Get API Key:** https://platform.openai.com/api-keys
- **Only needed for:** GPT-Image-1 or DALL-E output configs (not default)

---

## Port Usage

| Port | Service | Purpose |
|------|---------|---------|
| 11434 | Ollama | Local LLM inference |
| 7801 | SwarmUI | Image/video generation API |
| 7821 | ComfyUI | Advanced workflows (integrated with SwarmUI) |
| 17801 | Backend | Flask application (production) |
| 17802 | Backend | Flask application (development) |
| 5173 | Frontend | Vite dev server (development only) |

---

## Update Strategy

### Application Updates
```bash
cd /path/to/ai4artsed_webserver
git pull origin main
./update.sh
```

### Ollama Model Updates
```bash
ollama pull gpt-OSS:20b
ollama pull llama3.2-vision:latest
```

### SwarmUI Updates
```bash
cd /path/to/SwarmUI
git pull origin main
./install-linux.sh  # Re-run installer if dependencies changed
```

### Custom Node Updates
```bash
cd SwarmUI/dlbackend/ComfyUI/custom_nodes/ai4artsed_comfyui
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## License Information

### AI4ArtsEd Components
- **ai4artsed_webserver:** EUPL-1.2
- **ai4artsed_comfyui:** EUPL-1.2

### Third-Party Components
- **SwarmUI:** MIT License
- **ComfyUI:** GPL-3.0
- **Vue.js:** MIT License
- **Flask:** BSD-3-Clause
- **Ollama:** MIT License
- **LTX-Video:** Apache 2.0
- **Stable Diffusion 3.5:** Stability AI Community License

---

## Documentation

- **Installation Guide:** [INSTALLATION.md](INSTALLATION.md)
- **System Requirements:** [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)
- **Model Requirements:** [MODELS_REQUIRED.md](MODELS_REQUIRED.md)
- **Configuration Guide:** [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)

---

**Last Updated:** 2025-01-27
**Documentation Version:** 1.0.1
