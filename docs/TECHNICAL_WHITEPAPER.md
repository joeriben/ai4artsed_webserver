# AI4ArtsEd Technical Whitepaper

**System Architecture and Implementation Guide**

*Version 2.0 - January 2026*

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [The 4-Stage Pipeline](#3-the-4-stage-pipeline)
4. [Three-Layer Configuration System](#4-three-layer-configuration-system)
5. [Frontend (Vue 3)](#5-frontend-vue-3)
6. [Backend (Flask/DevServer)](#6-backend-flaskdevserver)
7. [SwarmUI/ComfyUI Integration](#7-swarmuicomfyui-integration)
8. [LLM Providers](#8-llm-providers)
9. [LoRA Training Studio](#9-lora-training-studio)
10. [API Reference](#10-api-reference)
11. [Deployment](#11-deployment)
12. [Development Guide](#12-development-guide)

---

## 1. System Overview

### What is AI4ArtsEd?

AI4ArtsEd is a pedagogical experimentation platform for critical engagement with generative AI. It separates the creative process into visible, editable steps, making AI transformation transparent.

### Components

- **Frontend**: Vue 3 SPA with TypeScript
- **Backend**: Flask-based orchestration server (DevServer)
- **Generation Backend**: SwarmUI with ComfyUI workflows (separate installation)
- **LLM Layer**: Multi-provider support (Ollama, OpenRouter, Bedrock, Mistral)

### Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| WAS/WIE Separation | User provides idea (WAS) + rules (WIE) separately |
| Visible Processing | 4-stage pipeline with editable breakpoints |
| LLM as Co-Actor | LLM contribution visible, not hidden |
| Original Language | Processing in user's language until final translation |

### Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 3 Frontend                        │
│            (TypeScript, Composition API, i18n)           │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/SSE
┌─────────────────────────▼───────────────────────────────┐
│                  Flask DevServer                         │
│         (Orchestration, Pipeline Execution)              │
└──────────┬──────────────────────────────┬───────────────┘
           │                              │
┌──────────▼──────────┐      ┌───────────▼────────────────┐
│    LLM Providers    │      │   SwarmUI (Port 7801)      │
│  - Ollama (local)   │      │   ┌────────────────────┐   │
│  - OpenRouter       │      │   │     ComfyUI        │   │
│  - AWS Bedrock      │      │   │   (Workflows)      │   │
│  - Mistral          │      │   └────────────────────┘   │
└─────────────────────┘      └────────────────────────────┘
```

---

## 2. Architecture

### Directory Structure

**AI4ArtsEd Development** (`~/ai/ai4artsed_development/`):
```
ai4artsed_development/
├── devserver/                    # Backend
│   ├── my_app/
│   │   ├── routes/              # API endpoints
│   │   │   ├── schema_pipeline_routes.py  # Main orchestration
│   │   │   ├── chat_routes.py             # Träshy chat
│   │   │   ├── training_routes.py         # LoRA training
│   │   │   └── ...
│   │   ├── engine/
│   │   │   └── pipeline_executor.py       # Pipeline execution
│   │   └── services/
│   │       ├── swarmui_manager.py         # Auto-recovery
│   │       └── training_service.py        # LoRA training
│   ├── schemas/
│   │   ├── pipelines/           # Stage 2 pipeline definitions
│   │   ├── chunks/              # Reusable pipeline chunks
│   │   └── configs/
│   │       ├── interception/    # Rule configurations (WIE)
│   │       └── output/          # Output model configs
│   └── config.py                # Centralized configuration
│
├── public/ai4artsed-frontend/   # Frontend
│   ├── src/
│   │   ├── views/               # Page components
│   │   ├── components/          # Reusable components
│   │   └── composables/         # Vue composables
│   └── dist/                    # Built frontend (gitignored)
│
├── docs/                        # Documentation
└── *.sh                         # Startup scripts (1-5)
```

**SwarmUI** (separate installation, `~/ai/SwarmUI/`):
```
SwarmUI/
├── dlbackend/
│   └── ComfyUI/
│       ├── custom_nodes/
│       │   └── ai4artsed_comfyui/    # Custom nodes
│       │       ├── ai4artsed_vector_dimension_eliminator.py
│       │       ├── ai4artsed_t5_clip_fusion.py
│       │       ├── ai4artsed_conditioning_fusion.py
│       │       └── ...
│       └── models/
├── Models/
│   └── Lora/                         # Trained LoRAs go here
└── launch-linux.sh
```

**Important**: SwarmUI is a **separate installation**. Communication via HTTP (Port 7801).

### Core Pattern

**DevServer = Smart Orchestrator | PipelineExecutor = Dumb Engine**

DevServer decides:
- Which stages to execute
- Which LLM for each stage
- Safety level enforcement
- When to translate

PipelineExecutor simply executes what it's told.

---

## 3. The 4-Stage Pipeline

### Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Stage 1   │───▶│   Stage 2   │───▶│   Stage 3   │───▶│   Stage 4   │
│   Safety    │    │ Interception│    │  Translate  │    │ Generation  │
│(orig. lang) │    │+ Optimization│   │  + Safety   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Stage 1: Pre-Interception Safety

**Purpose**: Check user input against §86a safety rules

**Key characteristics**:
- Runs in **original language** (German or English)
- NO translation happens here
- Bilingual safety filter (works in both languages)

**Input**: User's raw idea
**Output**: Safety status (passed/blocked)

**Configurable LLM**: `STAGE1_MODEL` in config.py

### Stage 2: Interception + Optimization

**Purpose**: Transform user idea according to selected rules

**Two-Phase Execution** (Session 65+):

**Phase 1: Interception** (Pedagogical Transformation)
- Combines WAS (idea) with WIE (rules)
- Uses `config.context` (the meta-prompt)
- Model: `STAGE2_INTERCEPTION_MODEL`
- Output: Transformed text in **original language**

**Phase 2: Optimization** (Model-specific, if needed)
- Adapts prompt for target generation model
- Uses `output_config.optimization_instruction`
- **When applied**: SD3.5 (needs keyword style), video, audio, p5.js
- **When skipped**: GPT Image, Gemini, QWEN (have strong language models)

**Result is visible and editable** before proceeding.

### Stage 3: Translation + Pre-Output Safety

**Purpose**: Prepare prompt for generation

1. **Translation**: German → English (generation models need English)
2. **Pre-Output Safety**: Final safety check on translated prompt

**Configurable LLM**: `STAGE3_OPTIMIZATION_MODEL` in config.py

### Stage 4: Media Generation

**Purpose**: Generate final media output

**Input**: English prompt from Stage 3
**Output**: Image, video, audio, or code

**Targets**:
- SwarmUI/ComfyUI (SD3.5, video, audio)
- External APIs (GPT Image, Gemini, QWEN)

---

## 4. Three-Layer Configuration System

### Overview

```
Layer 3: CONFIGS (34+ JSON files)
    "What transformation to apply"
    ↓ references
Layer 2: PIPELINES (4 core definitions)
    "How to orchestrate the transformation"
    ↓ uses
Layer 1: CHUNKS (3 primitives)
    "Atomic operations with templates"
```

### Layer 1: Chunks

**Location**: `devserver/schemas/chunks/`

Atomic operations with template-based prompts:

```json
{
  "name": "manipulate",
  "type": "processing_chunk",
  "template": "{{INSTRUCTION}}\n\nText:\n{{PREVIOUS_OUTPUT}}",
  "backend_type": "ollama",
  "model": "STAGE2_INTERCEPTION_MODEL"
}
```

**Placeholders**:
- `{{INSTRUCTION}}` - From config.context
- `{{INPUT_TEXT}}` - Original user input
- `{{PREVIOUS_OUTPUT}}` - Output from previous chunk

### Layer 2: Pipelines

**Location**: `devserver/schemas/pipelines/`

Define structural flow based on INPUT requirements:

| Pipeline | Input | Description |
|----------|-------|-------------|
| `text_transformation` | 1 text | Standard transformation |
| `image_transformation` | 1 image + text | Image-based transformation |
| `multi_image` | 3 images + text | Multi-image fusion |

```json
{
  "name": "text_transformation",
  "input_requirements": {"texts": 1},
  "chunks": ["manipulate"],
  "meta": {"workflow_type": "standard"}
}
```

### Layer 3: Configs (Interception Rules)

**Location**: `devserver/schemas/configs/interception/`

User-facing configurations with complete instruction content:

```json
{
  "id": "bauhaus",
  "name": {"de": "Bauhaus", "en": "Bauhaus"},
  "description": {"de": "Reduziert auf geometrische Formen..."},
  "context": "Du bist ein Künstler im Geiste des Bauhaus...",
  "category": "art_history",
  "meta": {
    "loras": [{"name": "bauhaus.safetensors", "strength": 0.6}]
  }
}
```

---

## 5. Frontend (Vue 3)

### Lab Paradigm

The frontend orchestrates the pipeline flow using atomic backend services:

```typescript
// Step 1: Run Stage 1+2
const interceptionResult = await fetch('/api/schema/pipeline/stage2', {
  method: 'POST',
  body: JSON.stringify({ schema: 'bauhaus', input_text: userInput })
});

// User can edit the result here...

// Step 2: Run Stage 3+4
const generationResult = await fetch('/api/schema/pipeline/stage3-4', {
  method: 'POST',
  body: JSON.stringify({ prompt: editedPrompt, output_config: 'sd35_large' })
});
```

### Key Views

| View | Route | Purpose |
|------|-------|---------|
| `SelectView.vue` | `/` | Rule selection (start page) |
| `text_transformation.vue` | `/text-transformation` | Text mode |
| `image_transformation.vue` | `/image-transformation` | Image mode |
| `multi_image.vue` | `/multi-image` | Multi-image mode |
| `TrainingView.vue` | `/training` | LoRA training |

### Naming Convention

Vue components for pipelines named EXACTLY after the pipeline:
```
Pipeline: text_transformation → Vue: text_transformation.vue
```

---

## 6. Backend (Flask/DevServer)

### Blueprint Structure

| Blueprint | URL Prefix | Purpose |
|-----------|-----------|---------|
| `schema_bp` | `/api/schema` | Pipeline orchestration |
| `chat_bp` | `/api/chat` | Träshy assistant |
| `media_bp` | `/api/media` | Media delivery |
| `settings_bp` | `/api/settings` | Settings |
| `training_bp` | (root) | LoRA training |

### Centralized Configuration

All models configured in `devserver/config.py`:

```python
STAGE1_MODEL = "llama-guard-3-8b"
STAGE2_INTERCEPTION_MODEL = "mistral-nemo"
STAGE3_OPTIMIZATION_MODEL = "qwen2.5:14b"
```

### Request Queueing

Concurrent LLM requests limited:
```python
_llm_semaphore = threading.Semaphore(3)  # Max 3 concurrent
```

Queue status streamed to frontend (red spinner feedback).

### Safety System

| Level | Age | Description |
|-------|-----|-------------|
| `kids` | 8-12 | Most restricted |
| `youth` | 12-17 | Default |
| `open` | 18+ | Least restricted |

Safety NOT configurable by users. Set by educator.

---

## 7. SwarmUI/ComfyUI Integration

### Architecture

```
DevServer ──HTTP──▶ SwarmUI (7801) ──▶ ComfyUI (7821)
     │                    │
     │              Auto-Recovery
     │                    │
     ▼                    ▼
SwarmUIManager     Health Checks
 (Singleton)       (Dual-port)
```

### Auto-Recovery System

**Pattern**: Lazy Recovery (Start only when needed)

```python
class SwarmUIManager:
    async def ensure_swarmui_available(self):
        if await self.is_healthy():
            return True
        async with self._lock:  # Prevent race conditions
            return await self._start_and_wait()
```

**Health Checks**:
- Port 7801: SwarmUI REST API
- Port 7821: ComfyUI backend

**Timeout**: 120 seconds with 2-second polling

### Custom ComfyUI Nodes

**Location**: `~/ai/SwarmUI/dlbackend/ComfyUI/custom_nodes/ai4artsed_comfyui/`

| Node | Purpose |
|------|---------|
| `ai4artsed_vector_dimension_eliminator.py` | Partial Elimination |
| `ai4artsed_t5_clip_fusion.py` | Surrealizer (dual-encoder) |
| `ai4artsed_conditioning_fusion.py` | Split & Combine |

### Experimental Workflows

| Workflow | Description |
|----------|-------------|
| Surrealizer | Mix CLIP and T5 embeddings |
| Split & Combine | Separate and recombine concepts |
| Partial Elimination | Zero out embedding dimensions |

---

## 8. LLM Providers

### Supported Providers

| Provider | Use Case | Local/Cloud |
|----------|----------|-------------|
| Ollama | Fast, private | Local |
| OpenRouter | Many models | Cloud |
| AWS Bedrock | Enterprise | Cloud |
| Mistral | European | Cloud |

### Configuration

```python
# config.py
OLLAMA_BASE_URL = "http://localhost:11434"
OPENROUTER_API_KEY = "..."  # From .key file
```

---

## 9. LoRA Training Studio

### Overview

Users can train custom LoRA models directly in AI4ArtsEd.

### Training Flow

1. **Upload**: 5-20 training images
2. **Configure**: Name, trigger word, epochs (4-8)
3. **VRAM Check**: Unload SD3.5 if needed (~18GB required)
4. **Training**: Kohya-ss backend with progress streaming
5. **Output**: LoRA in `SwarmUI/Models/Lora/`

### Config-Based LoRA Injection

LoRAs associated with interception configs:

```json
{
  "id": "cooked_negatives",
  "meta": {
    "loras": [
      {"name": "cooked_negatives.safetensors", "strength": 0.6}
    ]
  }
}
```

Automatically injected during Stage 4.

### Best Practices

- **Epoch 4**: Less overfitting, lighter style
- **Epoch 6**: Balanced (default)
- **Strength 0.6**: Good starting point
- Higher strength = more style, less prompt adherence

---

## 10. API Reference

### Pipeline Endpoints (Lab Atomic Services)

| Endpoint | Stages | Purpose |
|----------|--------|---------|
| `POST /api/schema/pipeline/stage2` | 1+2 | Safety + Interception |
| `POST /api/schema/pipeline/stage3-4` | 3+4 | Translate + Generate |
| `POST /api/schema/pipeline/generation` | 4 | Direct generation |
| `POST /api/schema/pipeline/legacy` | 1+4 | Experimental workflows |
| `GET /api/schema/schemas` | - | List configs |

### Stage 2 Request

```json
{
  "schema": "bauhaus",
  "input_text": "Eine Blume auf der Wiese",
  "safety_level": "youth",
  "run_id": "uuid"
}
```

### Stage 3-4 Request

```json
{
  "prompt": "Im Geiste des Bauhauses...",
  "output_config": "sd35_large",
  "safety_level": "youth",
  "run_id": "uuid-from-stage2"
}
```

### Media Endpoints

- `GET /api/media/image/{run_id}`
- `GET /api/media/video/{run_id}`
- `GET /api/media/audio/{run_id}`
- `GET /api/media/p5/{run_id}`

### Chat Endpoint

```json
POST /api/chat
{
  "message": "Was ist Interception?",
  "history": []
}
```

---

## 11. Deployment

### Development

```bash
# Terminal 1: Backend
cd devserver && python run.py  # Port 17802

# Terminal 2: Frontend
cd public/ai4artsed-frontend && npm run dev  # Port 5173

# Terminal 3: SwarmUI (separate directory!)
cd ~/ai/SwarmUI && ./launch-linux.sh --launch_mode none  # Port 7801
```

### Production

```bash
# Build frontend
cd public/ai4artsed-frontend && npm run build

# Start with production port
export PORT=17801
python run.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 17802 | DevServer port |
| `OLLAMA_BASE_URL` | localhost:11434 | Ollama endpoint |
| `SWARMUI_HOST` | localhost | SwarmUI host |
| `SWARMUI_PORT` | 7801 | SwarmUI port |

---

## 12. Development Guide

### Adding a New Interception Config

1. Create JSON in `devserver/schemas/configs/interception/`
2. Include: id, name (de/en), description (de/en), context, category
3. Restart DevServer
4. Appears on start page automatically

### Adding a New Output Model

1. Configure workflow in SwarmUI
2. Create config in `devserver/schemas/configs/output/`
3. Test with various prompts

### Code Style

- Python: Black formatter, type hints
- TypeScript: ESLint, Prettier
- Vue: Composition API, `<script setup>`

### Testing

```bash
cd public/ai4artsed-frontend
npm run type-check  # MANDATORY before commits
```

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **WAS** | User's idea (WHAT to transform) |
| **WIE** | Rules/meta-prompt (HOW to transform) |
| **Interception** | Stage 2 - combining WAS + WIE |
| **Co-Actor** | LLM as visible participant |
| **Breakpoint** | Point where user can edit |
| **Config** | Rule set for transformation |

---

## Appendix B: File Reference

| Need to... | Look in... |
|------------|------------|
| Add a rule | `devserver/schemas/configs/interception/` |
| Add output model | `devserver/schemas/configs/output/` |
| Change LLM | `devserver/config.py` |
| Edit pipeline logic | `my_app/routes/schema_pipeline_routes.py` |
| Add ComfyUI node | `~/ai/SwarmUI/dlbackend/ComfyUI/custom_nodes/ai4artsed_comfyui/` |

---

## Appendix C: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Initial version |
| 2.0 | 2026-01-20 | Complete rewrite: correct stage flow, Lab paradigm, Three-Layer system |

---

*This whitepaper reflects the architecture as of January 2026. For authoritative details, see `docs/ARCHITECTURE PART 01-24.md`.*
