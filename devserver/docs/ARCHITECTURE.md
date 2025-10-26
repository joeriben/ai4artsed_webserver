# DevServer Architecture
**AI4ArtsEd Development Server - Technical Reference**

> **Last Updated:** 2025-10-26
> **Status:** Post-consolidation, Output-Pipeline design finalized
> **Version:** 2.0 (Clean architecture after instruction_types removal and chunk consolidation)

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Three-Layer System](#three-layer-system)
3. [Pipeline Types](#pipeline-types)
4. [Data Flow Patterns](#data-flow-patterns)
5. [Engine Modules](#engine-modules)
6. [Backend Routing](#backend-routing)
7. [Model Selection](#model-selection)
8. [File Structure](#file-structure)
9. [API Routes](#api-routes)
10. [Execution Modes](#execution-modes)
11. [Documentation & Logging Workflow](#documentation--logging-workflow)

---

## Architecture Overview

### Core Principle: Clean Three-Layer Architecture + Input-Type Pipelines

DevServer implements a **template-based pipeline system** with three distinct layers and **input-type-based pipeline routing**:

```
┌─────────────────────────────────────────────────────────┐
│                    Layer 3: CONFIGS                     │
│              (User-Facing Content + Metadata)           │
│  • Display names, descriptions, categories              │
│  • Complete instruction text (context field)            │
│  • Parameters, media preferences, backend selection     │
│  • 34+ configs in schemas/configs/*.json                │
└─────────────────────────────────────────────────────────┘
                            ↓ references
┌─────────────────────────────────────────────────────────┐
│                  Layer 2: PIPELINES                     │
│         (Input-Type-Based Orchestration)                │
│  • Chunk sequences (NO content, only structure)         │
│  • Differentiate by INPUT type (not output/backend)     │
│  • 4 core pipelines in schemas/pipelines/*.json         │
└─────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────┐
│                   Layer 1: CHUNKS                       │
│              (Primitive Operations)                     │
│  • Template strings with {{PLACEHOLDERS}}               │
│  • Backend type (ollama/comfyui/openrouter)             │
│  • Task-type metadata for model selection               │
│  • 3 chunks in schemas/chunks/*.json                    │
└─────────────────────────────────────────────────────────┘
```

**Design Principles:**
1. **No Fourth Layer:** Content belongs in configs, not external registries
2. **Input-Type Pipelines:** Pipelines categorized by what they consume, not what they produce
3. **Backend Transparency:** Same pipeline can use ComfyUI, OpenRouter, or Ollama
4. **Media Transparency:** Same pipeline can generate image, audio, or video
5. **Separation of Concerns:** Text transformation ≠ Media generation

---

## Three-Layer System

### Layer 1: Chunks (Primitives)

**Purpose:** Atomic operations with template-based prompts
**Location:** `schemas/chunks/*.json`
**Count:** 3 core chunks (post-consolidation)

#### Current Chunks

| Chunk Name | Backend | Purpose | Task Type |
|------------|---------|---------|-----------|
| `manipulate` | Ollama | Universal text transformation | `standard` / `advanced` |
| `comfyui_image_generation` | ComfyUI | Image generation (SD3.5, Flux, etc.) | N/A |
| `comfyui_audio_generation` | ComfyUI | Audio/Music generation | N/A |

**Note:** After consolidation, we have ONE text transformation chunk (`manipulate`) instead of multiple redundant chunks (translate, prompt_interception, etc. were deleted).

#### Chunk Structure

```json
{
  "name": "manipulate",
  "description": "Universal text transformation with instruction-based prompting",
  "template": "{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}",
  "backend_type": "ollama",
  "model": "task:standard",  // Task-based model selection
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": false
  },
  "meta": {
    "chunk_type": "manipulation",
    "task_type": "standard",       // Links to model_selector categories
    "output_format": "text",
    "estimated_duration": "medium"
  }
}
```

**Placeholder System:**
- `{{INSTRUCTION}}` - Complete instruction from config.context
- `{{INPUT_TEXT}}` - Original user input (first pipeline step)
- `{{PREVIOUS_OUTPUT}}` - Output from previous chunk (chaining)
- `{{USER_INPUT}}` - Original user input (available in all steps)

**Historical Note:** We removed `{{TASK}}` and `{{CONTEXT}}` placeholders - they were redundant aliases that caused instruction text to appear twice in rendered prompts.

---

### Layer 2: Pipelines (Input-Type Orchestration)

**Purpose:** Define structural flow based on INPUT requirements
**Location:** `schemas/pipelines/*.json`
**Count:** 4 core pipelines

#### Current Pipelines

| Pipeline | Input Type | Output Type | Use Cases |
|----------|------------|-------------|-----------|
| `text_transformation` | 1 text | Text | Dadaism, Bauhaus, translation, etc. (30 configs) |
| `single_prompt_generation` | 1 text | Image/Audio/Video | SD3.5, Flux1, Stable Audio (multiple configs) |
| `dual_prompt_generation` | 2 texts | Music | AceStep (Tags + Lyrics) |
| `image_plus_text_generation` | Image + Text | Image | Inpainting, img2img, ControlNet (future) |

**Key Design:** Pipelines categorized by INPUT structure, not output medium!

#### Pipeline Structure

```json
{
  "name": "text_transformation",
  "description": "Single-step text transformation",
  "chunks": ["manipulate"],
  "required_configs": ["manipulate_config"],
  "config_mappings": {
    "manipulate_config": "{{MANIPULATE_CONFIG}}"
  },
  "meta": {
    "workflow_type": "text_transformation",
    "reusable": true,
    "pre_translation": true,
    "steps": [
      {
        "step": 1,
        "chunk": "manipulate",
        "description": "Text transformation",
        "config_key": "manipulate_config"
      }
    ]
  }
}
```

**Design Principle:** Pipelines define HOW to process (structure), NOT WHAT to process (content).

---

### Layer 3: Configs (Content)

**Purpose:** User-facing configurations with complete instruction content
**Location:** `schemas/configs/*.json`
**Count:** 34+ configs

#### Config Types

**1. Text Transformation Configs (30 configs)**
- Pipeline: `text_transformation`
- Examples: dada.json, bauhaus.json, overdrive.json
- Purpose: Transform/optimize text according to specific approach

**2. Output Generation Configs (4+ configs, expanding)**
- Pipeline: `single_prompt_generation` or `dual_prompt_generation`
- Examples: sd35_standard.json, flux1_dev.json, acestep_standard.json
- Purpose: Generate media from text prompt(s)

#### Config Structure

```json
{
  "pipeline": "text_transformation",

  "name": {
    "en": "Dadaism",
    "de": "Dadaismus"
  },

  "description": {
    "en": "Transform prompts through Dadaist aesthetic",
    "de": "Prompt-Transformation durch dadaistische Ästhetik"
  },

  "category": {
    "en": "Art Movements",
    "de": "Kunstbewegungen"
  },

  "context": "You are an artist working in the spirit of Dadaism. Your task is to...",

  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2048
  },

  "media_preferences": {
    "default_output": "text",
    "supported_types": ["text", "image"]
  },

  "meta": {
    "task_type": "advanced",  // Optional: override chunk's task_type
    "requires_creativity": true,
    "legacy_source": "config.py.DADAISMUS_PROMPT"
  },

  "display": {
    "icon": "🎨",
    "color": "#FF6B6B",
    "category": "art",
    "difficulty": 3,
    "order": 1
  },

  "tags": {
    "en": ["art", "surreal", "avant-garde"],
    "de": ["kunst", "surreal", "avantgarde"]
  },

  "audience": {
    "workshop_suitable": true,
    "min_age": 14,
    "complexity": "intermediate"
  }
}
```

**Key Field - `context`:**
The `context` field contains the **complete instruction text** (formerly called "metaprompt"). This is the actual content that gets injected into chunk templates as `{{INSTRUCTION}}`.

---

## Pipeline Types

### 1. Text Transformation Pipeline

**Purpose:** Transform text according to specific instructions
**Input:** One text prompt
**Output:** Transformed text
**Pipeline:** `text_transformation`

**Data Flow:**
```
User Input → Config (e.g., dada.json)
  → text_transformation Pipeline
    → manipulate Chunk
      → Ollama LLM
        → Optimized Text
```

**Use Cases:**
- Artistic transformations (Dadaism, Bauhaus, Renaissance)
- Translation (with specific cultural preservation)
- Style modifications (Youth Slang, Overdrive, PigLatin)
- Prompt optimization (for downstream media generation)

---

### 2. Single Prompt Generation Pipeline

**Purpose:** Generate media from one text prompt
**Input:** One text prompt
**Output:** Image, Audio, Music, or Video
**Pipeline:** `single_prompt_generation`

**Data Flow:**
```
Text Prompt → Config (e.g., sd35_standard.json)
  → single_prompt_generation Pipeline
    → Backend Router (checks config.backend)
      → ComfyUI Workflow Generator OR OpenRouter API
        → Media Output (Image/Audio/etc.)
```

**Use Cases:**
- Image generation (SD3.5, Flux1, DALL-E)
- Audio generation (Stable Audio)
- Music generation (simple single-prompt models)
- Video generation (future)

**Backend Flexibility:**
- Same pipeline works with ComfyUI (local) or OpenRouter (cloud)
- Config determines backend via `meta.backend` field

---

### 3. Dual Prompt Generation Pipeline

**Purpose:** Generate media from two text prompts
**Input:** Two text prompts (e.g., Tags + Lyrics)
**Output:** Music
**Pipeline:** `dual_prompt_generation`

**Data Flow:**
```
Prompt 1 (Tags) + Prompt 2 (Lyrics) → Config (acestep_standard.json)
  → dual_prompt_generation Pipeline
    → Backend Router
      → ComfyUI AceStep Workflow
        → input_mapping: prompt_1 → tags_node, prompt_2 → lyrics_node
          → Music Output (WAV)
```

**Config input_mapping:**
```json
{
  "input_mapping": {
    "prompt_1": "tags_node",     // Maps to ComfyUI Node ID
    "prompt_2": "lyrics_node"    // Maps to ComfyUI Node ID
  }
}
```

**Use Cases:**
- AceStep music generation (Tags + Lyrics)
- Future: Other multi-input scenarios

---

### 4. Image Plus Text Generation Pipeline

**Purpose:** Generate/modify image using input image + text
**Input:** Image file + Text prompt
**Output:** Modified image
**Pipeline:** `image_plus_text_generation`

**Data Flow:**
```
Input Image + Text Prompt → Config (inpainting_sd35.json)
  → image_plus_text_generation Pipeline
    → Backend Router
      → ComfyUI Inpainting Workflow
        → image → image_node, text → prompt_node
          → Modified Image Output
```

**Use Cases (Future):**
- Inpainting (modify parts of an image)
- Image-to-Image (transform existing image)
- ControlNet (structure-guided generation)
- Style Transfer

**Status:** Pipeline exists, configs not yet implemented

---

## Pipeline → Chunk → Backend Routing

### How Media Generation Works

**Key Concept:** Output-Pipelines (single_prompt_generation, dual_prompt_generation) are **backend-agnostic** and **media-agnostic**. They determine the right execution path based on:

1. **Config metadata** (`media_preferences.default_output`)
2. **Execution mode** (eco vs fast)
3. **Available backends** (local vs remote)

---

### Step-by-Step Routing Logic

#### Example: User generates an image using Dada + SD3.5

**Step 1: Text Transformation (Pre-Pipeline)**
```python
# User selects: Config "Dada" + Input "A red apple"
config = load_config("dada.json")
# → pipeline: "text_transformation"
# → context: "You are an artist working in the spirit of Dadaism..."

result = execute_pipeline(
    pipeline="text_transformation",
    chunks=["manipulate"],
    context="You are an artist working in Dadaism...",
    input_text="A red apple"
)
# → Output: "Ein roter Apfel in dadaistischer Ästhetik mit fragmentierter Form..."
```

**Step 2: Media Generation (Output-Pipeline)**
```python
# User clicks "Generate Image" → Server calls output-pipeline
config = load_config("sd35_standard.json")  # Or user-selected image config
# → pipeline: "single_prompt_generation"
# → media_preferences.default_output: "image"
# → meta.model: "sd3.5_large"
# → parameters: {cfg: 5.5, steps: 20, ...}

# Pipeline determines media_type from config
media_type = config.media_preferences.default_output  # "image"

# Pipeline checks execution mode
execution_mode = get_execution_mode()  # "eco" or "fast" (from frontend or server default)

# Pipeline routes to appropriate chunk
if execution_mode == "eco":
    chunk = select_chunk_for_local_generation(media_type)
    # → For "image": comfyui_image_generation
    # → For "audio": comfyui_audio_generation
    # → For "music": comfyui_music_generation
elif execution_mode == "fast":
    chunk = select_chunk_for_remote_generation(media_type)
    # → For "image": openrouter_image_generation (GPT-5)
    # → For "audio": fallback to local (no remote API yet)
    # → For "music": fallback to local (no remote API yet)

# Execute chunk
result = execute_chunk(
    chunk=chunk,
    input_text="Ein roter Apfel in dadaistischer Ästhetik...",
    config_params=config.parameters
)
# → ComfyUI generates image using SD3.5 Large workflow
# → Returns: prompt_id for polling
```

---

### Chunk Selection Matrix

| Media Type | eco Mode Chunk | fast Mode Chunk | Status |
|------------|----------------|-----------------|--------|
| **image** | `comfyui_image_generation` | `openrouter_image_generation` | eco: ✅, fast: Planned |
| **audio** | `comfyui_audio_generation` | `(fallback to local)` | eco: ✅, fast: Not available |
| **music** | `comfyui_music_generation` | `(fallback to local)` | eco: ✅, fast: Not available |
| **video** | `comfyui_video_generation` | `openai_video_generation` (Sora2) | eco: Planned, fast: Planned |

**Important:** Chunks are **NOT** hardcoded in pipelines. Instead:
- Pipeline reads `config.media_preferences.default_output`
- Pipeline checks `execution_mode` (eco/fast)
- Pipeline dynamically selects appropriate chunk
- Chunk contains either:
  - **Option A:** ComfyUI API JSON workflow (Standard-Template)
  - **Option B:** Python code for API calls (OpenRouter, OpenAI, etc.)

---

### Chunk Naming Convention (Planned Refactoring)

**Current (Backend-Specific):**
- `comfyui_image_generation` ❌ (exposes backend in name)
- `comfyui_audio_generation` ❌
- `comfyui_music_generation` ❌

**Planned (Execution-Mode-Specific):**
- `local_media_generation` ✅ (works with ComfyUI, SwarmUI, or any local backend)
- `remote_media_generation` ✅ (works with OpenRouter, OpenAI, Replicate, etc.)

**Alternative (Media-Type-Specific):**
- `local_image_generation`, `remote_image_generation`
- `local_audio_generation`, `remote_audio_generation`
- `local_music_generation`, `remote_music_generation`
- `local_video_generation`, `remote_video_generation`

**Decision:** TBD - depends on how different media types require different chunk logic

---

### Config → Pipeline → Chunk Example

**Config: stableaudio.json**
```json
{
  "pipeline": "single_prompt_generation",
  "media_preferences": {
    "default_output": "audio",
    "supported_types": ["audio"]
  },
  "meta": {
    "model": "stable_audio_open",
    "duration_seconds": 47
  },
  "parameters": {
    "cfg": 7.0,
    "steps": 100
  }
}
```

**Pipeline: single_prompt_generation.json**
```json
{
  "name": "single_prompt_generation",
  "description": "Single text → Media (image/audio/video)",
  "chunks": ["manipulate", "{{MEDIA_GENERATION_CHUNK}}"],
  "meta": {
    "input_type": "single_text",
    "output_types": ["image", "audio", "music", "video"],
    "backend_agnostic": true
  }
}
```

**Chunk Selection (Runtime):**
```python
# Server determines chunk based on media_type + execution_mode
media_type = config.media_preferences.default_output  # "audio"
execution_mode = "eco"  # From frontend or server default

if execution_mode == "eco":
    chunk_name = f"comfyui_{media_type}_generation"
    # → "comfyui_audio_generation"
else:
    chunk_name = f"openrouter_{media_type}_generation"
    # → "openrouter_audio_generation" (fallback if doesn't exist)
```

**Chunk: comfyui_audio_generation.json**
```json
{
  "name": "comfyui_audio_generation",
  "description": "Audio generation via ComfyUI (Stable Audio Open)",
  "backend_type": "comfyui",
  "workflow_template": "stable_audio_open",
  "input_mapping": {
    "text_prompt": "node_4_text_input"
  },
  "parameters_mapping": {
    "cfg": "node_5_cfg",
    "steps": "node_5_steps",
    "duration_seconds": "node_3_duration"
  },
  "meta": {
    "media_type": "audio",
    "model": "stable_audio_open.safetensors"
  }
}
```

---

### Why This Architecture?

**1. Backend Transparency:**
- Same pipeline `single_prompt_generation` works with any backend
- ComfyUI can be replaced with SwarmUI, Replicate, etc. without changing pipelines

**2. Media Transparency:**
- Pipeline doesn't care if output is image, audio, or video
- Differentiation happens at chunk selection (runtime)

**3. Easy Extension:**
- Add new media type (e.g., "3d_model")? → Create new chunk, no pipeline changes
- Add new backend (e.g., Replicate)? → Create new chunk, no pipeline changes

**4. Pedagogical Flexibility:**
- Teachers can switch between eco (free, slow) and fast (paid, fast) without changing workflows
- Students see same interface regardless of backend

---

## Data Flow Patterns

### Pattern 1: Text-Only Transformation

```
User Input: "A surreal dream"
  ↓
Config: dada.json (pipeline: text_transformation)
  ↓
Pipeline: text_transformation
  ↓
Chunk: manipulate (with Dadaism instruction)
  ↓
Ollama LLM: mistral-nemo (eco mode) or claude-3.5-haiku (fast mode)
  ↓
Output: "Ein surrealistischer Traum in dadaistischer Ästhetik mit absurden juxtapositionen..."
```

---

### Pattern 2: Text → Optimized Text → Image

```
Step 1 (Text Transformation):
  User Input: "A red apple"
    ↓
  Config: dada.json
    ↓
  Output: "Ein roter Apfel in dadaistischer Ästhetik mit fragmentierter Form..."

Step 2 (Media Generation):
  Optimized Text: "Ein roter Apfel in dadaistischer..."
    ↓
  Config: sd35_standard.json (pipeline: single_prompt_generation)
    ↓
  Backend Router: ComfyUI
    ↓
  Workflow: sd35_standard (Dual CLIP: clip_g + t5xxl, CFG:5.5, Steps:20)
    ↓
  Output: Image (PNG)
```

**Server Orchestration:**
```python
# Step 1
result1 = executor.execute_pipeline(
    config_name="dada",
    input_text="A red apple"
)
optimized_text = result1.final_output

# Step 2
result2 = executor.execute_pipeline(
    config_name="sd35_standard",
    input_text=optimized_text
)
image_prompt_id = result2.media_output.prompt_id
```

---

### Pattern 3: Direct Media Generation (No Text Optimization)

```
User Input: "A red apple on a wooden table"
  ↓
Config: sd35_standard.json (pipeline: single_prompt_generation)
  ↓
Backend Router: ComfyUI
  ↓
Workflow: sd35_standard
  ↓
Output: Image (PNG)
```

---

### Pattern 4: Dual Prompt → Music

```
User provides:
  - Tags: "upbeat, electronic, 120bpm"
  - Lyrics: "Dancing through the night, feeling so alive..."
    ↓
Config: acestep_standard.json (pipeline: dual_prompt_generation)
  ↓
Backend Router: ComfyUI
  ↓
Workflow: acestep_music
  ↓
Input Mapping:
  - prompt_1 (Tags) → Node 123 (tags input)
  - prompt_2 (Lyrics) → Node 456 (lyrics input)
  ↓
Output: Music (WAV, 47 seconds)
```

---

## Engine Modules

### Core Engine Architecture

```
schemas/engine/
├── config_loader.py          # Load configs and pipelines
├── chunk_builder.py           # Build chunks with placeholder replacement
├── pipeline_executor.py       # Execute complete pipelines
├── backend_router.py          # Route to appropriate backend
├── model_selector.py          # Task-based model selection
├── comfyui_workflow_generator.py  # Generate ComfyUI workflows
└── prompt_interception_engine.py  # Legacy bridge (deprecated)
```

---

### 1. config_loader.py

**Purpose:** Load and manage configs and pipelines

**Key Classes:**
```python
@dataclass
class Config:
    pipeline: str
    name: dict
    description: dict
    category: dict
    context: str              # Complete instruction text
    parameters: dict
    media_preferences: dict
    meta: dict
    display: dict
    tags: dict
    audience: dict

@dataclass
class Pipeline:
    name: str
    description: str
    chunks: List[str]
    required_configs: List[str]
    config_mappings: dict
    meta: dict

class ConfigLoader:
    def __init__(self, schemas_path: Path):
        self.configs: Dict[str, Config] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        self._load_all()
```

**Key Methods:**
- `get_config(config_name: str) -> Config`
- `get_pipeline(pipeline_name: str) -> Pipeline`
- `list_configs() -> List[str]`
- `get_config_info(config_name: str) -> dict`

---

### 2. chunk_builder.py

**Purpose:** Build chunks with placeholder replacement

**Key Functionality:**
```python
class ChunkBuilder:
    def build_chunk(
        self,
        chunk_name: str,
        resolved_config: ResolvedConfig,
        context: dict
    ) -> ProcessedChunk:
        # 1. Get chunk template
        template = self.templates.get(chunk_name)

        # 2. Build replacement context
        instruction_text = resolved_config.context or ''
        replacement_context = {
            'INSTRUCTION': instruction_text,
            'INSTRUCTIONS': instruction_text,  # Backward compat
            'INPUT_TEXT': context.get('input_text', ''),
            'PREVIOUS_OUTPUT': context.get('previous_output', ''),
            'USER_INPUT': context.get('user_input', ''),
            **context.get('custom_placeholders', {})
        }

        # 3. Replace placeholders
        processed_template = self._replace_placeholders(
            template.template,
            replacement_context
        )

        # 4. Return processed chunk
        return ProcessedChunk(...)
```

**Note:** After consolidation, we removed `TASK` and `CONTEXT` placeholder aliases - they were redundant and caused duplication.

---

### 3. pipeline_executor.py

**Purpose:** Execute complete pipelines by orchestrating chunks

**Key Functionality:**
```python
class PipelineExecutor:
    async def execute_pipeline(
        self,
        config_name: str,
        input_text: str,
        user_input: str = None,
        mode: str = "eco"
    ) -> PipelineResult:
        # 1. Load config and pipeline
        config = self.config_loader.get_config(config_name)
        pipeline = self.config_loader.get_pipeline(config.pipeline)

        # 2. Execute chunks in sequence
        context = {'input_text': input_text, 'user_input': user_input or input_text}
        steps = []

        for i, chunk_name in enumerate(pipeline.chunks):
            # Build chunk
            chunk = self.chunk_builder.build_chunk(chunk_name, config, context)

            # Execute via backend router
            result = await self.backend_router.route(chunk, mode)

            # Update context for next chunk
            context['previous_output'] = result.output
            steps.append(result)

        # 3. Return complete result
        return PipelineResult(
            final_output=context['previous_output'],
            steps=steps,
            execution_time=...,
            metadata=...
        )
```

---

### 4. backend_router.py

**Purpose:** Route chunks to appropriate backends (Ollama, ComfyUI, OpenRouter)

**Key Functionality:**
```python
class BackendRouter:
    async def route(
        self,
        chunk: ProcessedChunk,
        mode: str = "eco"
    ) -> ChunkResult:
        backend_type = chunk.backend_type

        if backend_type == "ollama":
            return await self._route_ollama(chunk, mode)
        elif backend_type == "comfyui":
            return await self._route_comfyui(chunk)
        elif backend_type == "openrouter":
            return await self._route_openrouter(chunk)
        else:
            raise ValueError(f"Unknown backend: {backend_type}")

    async def _route_ollama(self, chunk, mode):
        # Model selection based on task_type
        if chunk.model.startswith('task:'):
            task_name = chunk.model.split(':', 1)[1]
            model = self.model_selector.select_model(task_name, mode)
        else:
            model = chunk.model

        # Execute via Ollama service
        return await ollama_service.generate(model, chunk.prompt, chunk.parameters)
```

**Backend Types:**
- `ollama`: Local LLM server (mistral-nemo, llama3.2, gemma2, etc.)
- `comfyui`: Local ComfyUI server (SD3.5, Flux1, Stable Audio, AceStep)
- `openrouter`: Cloud API (Claude, GPT-4, Gemini, etc.)

---

### 5. model_selector.py

**Purpose:** Task-based model selection (eco vs fast modes)

**Task Categories:**
```python
def _define_task_categories(self) -> Dict[str, Dict[str, str]]:
    return {
        "security": {
            "eco": "local/llama-guard-3-8b",
            "fast": "local/llama-guard-3-8b",  # Always local
            "description": "Content moderation"
        },
        "vision": {
            "eco": "local/llava:13b",
            "fast": "local/llava:13b",  # Always local (DSGVO)
            "description": "Image analysis"
        },
        "translation": {
            "eco": "local/qwen2.5-translator",
            "fast": "openrouter/anthropic/claude-3.5-haiku",
            "description": "Language translation"
        },
        "standard": {
            "eco": "local/mistral-nemo",
            "fast": "openrouter/mistralai/mistral-nemo",
            "description": "General text tasks"
        },
        "advanced": {
            "eco": "local/mistral-small:24b",
            "fast": "openrouter/google/gemini-2.5-pro",
            "description": "Complex reasoning, creativity"
        },
        "data_extraction": {
            "eco": "local/gemma3:4b",
            "fast": "openrouter/google/gemma-3-4b-it",
            "description": "Structured data extraction"
        }
    }
```

**Usage in Chunks:**
```json
{
  "model": "task:translation",  // Uses task-based selection
  "meta": {
    "task_type": "translation"
  }
}
```

**Execution Modes:**
- `eco`: Free local models (slower, privacy-preserving, DSGVO-compliant)
- `fast`: Paid cloud APIs (faster, higher quality, requires API keys)

---

### 6. comfyui_workflow_generator.py

**Purpose:** Generate ComfyUI workflows from templates

**Workflow Templates:**
```python
class ComfyUIWorkflowGenerator:
    def __init__(self, schemas_path: Path):
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        # SD 3.5 Large Standard
        self.templates["sd35_standard"] = WorkflowTemplate(
            name="sd35_standard",
            base_nodes={
                "3": {"inputs": {...}, "class_type": "KSampler"},
                "4": {"inputs": {"ckpt_name": "{{CHECKPOINT}}"}, "class_type": "CheckpointLoaderSimple"},
                "6": {"inputs": {"text": "{{PROMPT}}", "clip": ["43", 0]}, "class_type": "CLIPTextEncode"},
                "43": {"inputs": {"clip_name1": "clip_g.safetensors", "clip_name2": "t5xxl_enconly.safetensors"}, "class_type": "DualCLIPLoader"},
                ...
            },
            parameter_mappings={
                "PROMPT": "{{PROMPT}}",
                "STEPS": 20,
                "CFG": 5.5,
                "CHECKPOINT": "sd3.5_large.safetensors",
                ...
            }
        )

        # Flux1 Dev
        self.templates["flux1_dev"] = WorkflowTemplate(...)

        # AceStep Music
        self.templates["acestep_music"] = WorkflowTemplate(...)

        # Stable Audio
        self.templates["stable_audio_standard"] = WorkflowTemplate(...)

    def generate_workflow(
        self,
        template_name: str,
        schema_output: str,
        parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        template = self.templates.get(template_name)

        # Merge default parameters with overrides
        final_params = {**template.default_params, **parameters}

        # Replace placeholders in workflow
        workflow = self._process_template(template, final_params)

        return workflow
```

**Standard Parameters by Template:**

**SD3.5 Standard:**
- Checkpoint: `sd3.5_large.safetensors`
- CLIP: Dual CLIP (`clip_g.safetensors` + `t5xxl_enconly.safetensors`)
- Steps: 20
- CFG: 5.5
- Sampler: euler
- Scheduler: normal
- Size: 1024x1024

**Flux1 Dev:**
- Checkpoint: `flux1_dev.safetensors`
- Steps: 25
- CFG: 1.0
- Guidance: 3.5
- Size: 1024x1024

**Stable Audio:**
- Duration: 47.0 seconds
- Steps: 150
- CFG: 7.0

---

## Backend Routing

### Backend Types

| Backend | Type | Use Cases | Authentication | DSGVO |
|---------|------|-----------|----------------|-------|
| **Ollama** | Local | Text transformation, translation | None (local) | ✅ Compliant |
| **ComfyUI** | Local | Image/Audio/Music/Video generation | None (local) | ✅ Compliant |
| **OpenRouter** | Cloud | Fast text/image tasks | API Key required | ❌ Non-compliant |
| **OpenAI** | Cloud | GPT-5 Image, Sora2 Video (future) | API Key required | ⚠️ Enterprise only |

---

### Execution Mode System: eco vs fast

The DevServer implements a simple **two-mode execution system** that determines whether tasks run locally or remotely:

| Mode | Priority | Backends | Cost | Speed | DSGVO |
|------|----------|----------|------|-------|-------|
| **eco** | Local resources | Ollama, ComfyUI | Free | Slower | ✅ Compliant |
| **fast** | Cloud APIs | OpenRouter, OpenAI | Paid | Faster | ⚠️ Depends on provider |

**Mode Selection Logic:**
1. **User Switch (Frontend):** User can toggle eco/fast mode in UI
2. **Server Default (server.config.py):** Fallback if no user preference
3. **Config Override (optional):** Specific configs can force eco mode (e.g., DSGVO-sensitive tasks)

---

### Routing Logic Details

#### 1. Text Transformation (LLM Tasks)

**eco mode:**
```python
Backend: Ollama (local)
Models: mistral-nemo, llama3.2, gemma2, qwen2.5-translator
Cost: Free
DSGVO: Compliant (all data stays local)
```

**fast mode:**
```python
Backend: OpenRouter (cloud)
Models: claude-3.5-haiku, gemini-2.5-pro, mistral-nemo (cloud)
Cost: ~$0.10-0.18 per 1M tokens
DSGVO: Non-compliant (data sent to US/UK servers)
```

**Force Local (regardless of mode):**
- task_type: `security` (content moderation must stay local)
- task_type: `vision` (DSGVO requirements for image analysis)

---

#### 2. Media Generation (Image/Audio/Music/Video)

**2a. Image Generation**

**eco mode:**
```python
Backend: ComfyUI (local)
Models:
  - Stable Diffusion 3.5 Large (default)
  - Flux1 Development
  - SD1.5 / SDXL (legacy)
Cost: Free (GPU usage)
Quality: High (full control over parameters)
Speed: ~20-60 seconds per image
DSGVO: Compliant
```

**fast mode:**
```python
Backend: OpenRouter (cloud)
Model: GPT-5 Image (via OpenRouter or direct OpenAI)
Cost: TBD (GPT-5 pricing not yet public)
Quality: TBD
Speed: ~5-15 seconds per image
DSGVO: Non-compliant (OpenRouter) or Enterprise-only (OpenAI direct)

Status: Planned, not yet implemented
```

---

**2b. Audio Generation (Sound Effects, Ambience)**

**eco mode:**
```python
Backend: ComfyUI (local)
Model: Stable Audio Open
Input: Single text prompt (e.g., "ocean waves crashing")
Output: Audio file (47 seconds, WAV)
Cost: Free
DSGVO: Compliant
```

**fast mode:**
```python
Backend: Not yet implemented
Model: TBD (no suitable OpenRouter audio model available)
Status: Placeholder for future implementation

Note: OpenRouter does not currently offer audio generation APIs
```

---

**2c. Music Generation (with Tags + Lyrics)**

**eco mode:**
```python
Backend: ComfyUI (local)
Model: AceStep (ace_step_v1_3.5b.safetensors)
Input:
  - Prompt 1 (Tags): "upbeat, electronic, 120bpm"
  - Prompt 2 (Lyrics): "Dancing through the night..."
Output: Music file (47 seconds, WAV)
Cost: Free
DSGVO: Compliant
```

**fast mode:**
```python
Backend: Not yet implemented
Model: TBD (Suno AI? Udio? via OpenRouter or direct API)
Status: Placeholder for future implementation

Note: Music generation with lyrics is rare in cloud APIs
```

---

**2d. Video Generation (Future)**

**eco mode:**
```python
Backend: ComfyUI (local)
Model: TBD (AnimateDiff? Stable Video Diffusion?)
Cost: Free (but GPU-intensive)
Speed: Very slow (minutes per video)
DSGVO: Compliant
Status: Not yet implemented
```

**fast mode:**
```python
Backend: OpenAI (direct API)
Model: Sora2
Cost: Per-second pricing (e.g., $0.10-0.50 per second of video)
Speed: Fast (seconds to low-resolution, minutes to high-res)
DSGVO: Enterprise-only
Status: Planned, not yet implemented
```

---

### Backend Selection Algorithm

**Step 1: Determine Task Type**
```python
if pipeline == "text_transformation":
    task_category = "LLM"
elif pipeline in ["single_prompt_generation", "dual_prompt_generation"]:
    task_category = "MEDIA_GENERATION"
    media_type = config.media_preferences.default_output  # "image", "audio", "music", "video"
```

**Step 2: Check Execution Mode**
```python
# Priority order:
execution_mode = (
    user_preference_from_frontend  # User toggled eco/fast switch
    or config.meta.get("force_eco")  # Config forces eco mode (DSGVO)
    or server_config.DEFAULT_EXECUTION_MODE  # Server default (usually "eco")
)
```

**Step 3: Route to Backend**
```python
if task_category == "LLM":
    if execution_mode == "eco":
        backend = "ollama"
        model = model_selector.get_local_model(task_type)
    elif execution_mode == "fast":
        if task_type in ["security", "vision"]:
            backend = "ollama"  # Force local for DSGVO
        else:
            backend = "openrouter"
            model = model_selector.get_cloud_model(task_type)

elif task_category == "MEDIA_GENERATION":
    if execution_mode == "eco":
        backend = "comfyui"
        workflow = get_comfyui_workflow(media_type, config.meta.model)
    elif execution_mode == "fast":
        if media_type == "image":
            backend = "openrouter"  # GPT-5 Image
            model = "gpt-5-image"  # Placeholder
        elif media_type in ["audio", "music", "video"]:
            # Fallback to local (no cloud alternative yet)
            backend = "comfyui"
            workflow = get_comfyui_workflow(media_type, config.meta.model)
```

**Step 4: Execute**
```python
result = backend_router.execute(
    backend=backend,
    model=model,
    workflow=workflow,
    input_data=processed_input,
    config_params=config.parameters
)
```

---

### Remote Service Configuration (server.config.py)

The server maintains centralized configuration for remote services:

```python
# server.config.py

# Default execution mode (eco = local, fast = cloud)
DEFAULT_EXECUTION_MODE = "eco"

# Remote service endpoints (used when execution_mode == "fast")
REMOTE_SERVICES = {
    "image": {
        "provider": "openrouter",  # or "openai" for direct GPT-5 access
        "model": "gpt-5-image",  # Placeholder - not yet available
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "fallback_to_local": True  # Use ComfyUI if API fails
    },
    "audio": {
        "provider": None,  # No cloud provider yet
        "fallback_to_local": True
    },
    "music": {
        "provider": None,  # No cloud provider yet (Suno? Udio?)
        "fallback_to_local": True
    },
    "video": {
        "provider": "openai",  # Sora2 via OpenAI direct API
        "model": "sora-2",  # Placeholder
        "api_key": os.getenv("OPENAI_API_KEY"),
        "cost_per_second": 0.20,  # Estimated
        "fallback_to_local": False  # No local video generation yet
    }
}

# LLM Services
LLM_SERVICES = {
    "local": {
        "provider": "ollama",
        "base_url": "http://localhost:11434"
    },
    "cloud": {
        "provider": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1"
    }
}
```

---

### DSGVO Considerations

**Current Status:**
- ✅ **eco mode:** Fully DSGVO-compliant (all data stays local)
- ❌ **fast mode:** Non-compliant (OpenRouter routes through US/UK)

**Planned Solutions:**
1. **Alternative Cloud Provider:** Find EU-based API provider (e.g., Mistral AI direct, DeepL, etc.)
2. **Enterprise OpenAI:** Use OpenAI Enterprise for DSGVO compliance (more expensive)
3. **Workshop Mode:** Force eco mode for educational workshops (config.meta.force_eco = true)

**Current Workaround:**
- Default to eco mode for all educational workshops
- Only allow fast mode for research/development (non-student data)

---

## Model Selection

### Task-Based Selection System

**Purpose:** Select optimal LLM based on task requirements and execution mode

**Implementation:** `schemas/engine/model_selector.py`

### Task Categories

| Task Type | Eco Model | Fast Model | Use Case |
|-----------|-----------|------------|----------|
| **security** | llama-guard-3-8b (local) | llama-guard-3-8b (local) | Content moderation (always local) |
| **vision** | llava:13b (local) | llava:13b (local) | Image analysis (DSGVO) |
| **translation** | qwen2.5-translator (local) | claude-3.5-haiku (cloud) | Language translation |
| **standard** | mistral-nemo (local) | mistral-nemo (cloud) | General text tasks |
| **advanced** | mistral-small:24b (local) | gemini-2.5-pro (cloud) | Complex reasoning |
| **data_extraction** | gemma3:4b (local) | gemma-3-4b-it (cloud) | Structured extraction |

### Usage in Chunks

**Option 1: Task-based selection (recommended):**
```json
{
  "model": "task:translation",
  "meta": {
    "task_type": "translation"
  }
}
```

**Option 2: Direct model specification:**
```json
{
  "model": "mistral-nemo:latest",
  "meta": {
    "task_type": "standard"
  }
}
```

### Execution Mode Behavior

**Eco Mode (default):**
- Uses local Ollama models
- Free, privacy-preserving, DSGVO-compliant
- Slower inference
- No API costs

**Fast Mode:**
- Uses cloud APIs (OpenRouter)
- Paid, requires API key
- Faster inference, higher quality
- For security/vision tasks: Still uses local models (DSGVO)

---

## File Structure

```
devserver/
├── schemas/
│   ├── chunks/
│   │   ├── manipulate.json                    # Universal text transformation
│   │   ├── comfyui_image_generation.json      # Image generation
│   │   └── comfyui_audio_generation.json      # Audio/Music generation
│   │
│   ├── pipelines/
│   │   ├── text_transformation.json           # Text → Text (30 configs)
│   │   ├── single_prompt_generation.json      # Text → Media (SD3.5, Flux1, etc.)
│   │   ├── dual_prompt_generation.json        # 2 Texts → Music (AceStep)
│   │   └── image_plus_text_generation.json    # Image+Text → Image (future)
│   │
│   ├── configs/
│   │   ├── dada.json                          # Text transformation configs
│   │   ├── bauhaus.json
│   │   ├── overdrive.json
│   │   ├── ...                                # (30 total)
│   │   ├── sd35_standard.json                 # Output generation configs
│   │   ├── flux1_dev.json
│   │   ├── acestep_standard.json
│   │   └── stableaudio.json
│   │
│   └── engine/
│       ├── config_loader.py                   # Load configs + pipelines
│       ├── chunk_builder.py                   # Build chunks
│       ├── pipeline_executor.py               # Execute pipelines
│       ├── backend_router.py                  # Route to backends
│       ├── model_selector.py                  # Task-based model selection
│       └── comfyui_workflow_generator.py      # ComfyUI workflows
│
├── my_app/
│   ├── routes/
│   │   └── workflow_routes.py                 # Main API endpoint
│   ├── services/
│   │   ├── ollama_service.py                  # Ollama integration
│   │   ├── comfyui_service.py                 # ComfyUI integration
│   │   └── translator_service.py              # Pre-translation
│   └── utils/
│       └── helpers.py                         # Helper functions
│
├── docs/
│   ├── ARCHITECTURE.md                        # This file
│   ├── OUTPUT_PIPELINE_ARCHITECTURE.md        # Output pipeline design
│   ├── DEVELOPMENT_DECISIONS.md               # Decision log
│   ├── devserver_todos.md                     # Implementation TODOs
│   └── tmp/
│       ├── CHUNK_ANALYSIS.md                  # Chunk analysis
│       ├── PLACEHOLDER_ANALYSIS.md            # Placeholder analysis
│       └── PIPELINE_ANALYSIS.md               # Pipeline analysis
│
├── test_refactored_system.py                  # Architecture tests
├── test_pipeline_execution.py                 # Execution tests
└── config.py                                  # Server configuration
```

---

## API Routes

### Primary Endpoint: `/api/workflow/execute`

**Purpose:** Execute a config-based pipeline

**Request:**
```json
{
  "schema_name": "dada",
  "prompt": "A surreal dream",
  "mode": "eco"  // or "fast"
}
```

**Response:**
```json
{
  "success": true,
  "schema_pipeline": true,
  "schema_name": "dada",
  "final_output": "Ein surrealistischer Traum in dadaistischer Ästhetik...",
  "steps_completed": 1,
  "execution_time": 2.35,
  "original_prompt": "A surreal dream",
  "translated_prompt": "Ein surrealistischer Traum...",
  "backend_info": [
    {
      "step": 1,
      "backend": "ollama",
      "model": "mistral-nemo:latest"
    }
  ]
}
```

**Pre-Translation Logic:**
```python
# Check for #notranslate# marker
if "#notranslate#" in original_prompt:
    translated_prompt = original_prompt.replace("#notranslate#", "")
elif should_translate:
    translated_prompt = await translator_service.translate(original_prompt, "de")
else:
    translated_prompt = original_prompt
```

**Media Generation:**
```python
# After text pipeline, check for media generation
if config.media_preferences.default_output == "image":
    prompt_id = await generate_image_from_text(
        text_prompt=final_output,
        schema_name=schema_name
    )
    response["media"] = {
        "type": "image",
        "prompt_id": prompt_id,
        "url": f"/api/media/image/{prompt_id}"
    }
```

---

### Supporting Endpoints

**Get Available Configs:**
```
GET /api/workflow/schemas
Response: ["dada", "bauhaus", "overdrive", ...]
```

**Get Config Info:**
```
GET /api/workflow/schema/<name>
Response: {name, description, category, display, ...}
```

**Get Media Status:**
```
GET /api/media/status/<prompt_id>
Response: {status: "completed", output_url: "..."}
```

---

## Execution Modes

### Eco Mode (Default)

**Characteristics:**
- Uses local Ollama models
- Free (no API costs)
- Privacy-preserving (DSGVO-compliant)
- Slower inference (~2-5 seconds per request)
- Unlimited usage

**Model Examples:**
- mistral-nemo:latest (12B, general)
- llama3.2:latest (3B, fast)
- gemma2:9b (9B, quality)
- qwen2.5-translator (translation)

**Use Cases:**
- Workshops with students
- Experimentation
- Privacy-sensitive content
- High-volume usage

---

### Fast Mode

**Characteristics:**
- Uses cloud APIs (OpenRouter)
- Paid (API costs per request)
- Faster inference (~0.5-2 seconds)
- Higher quality outputs
- Rate limited by API provider

**Model Examples:**
- claude-3.5-haiku (fast, high quality)
- gemini-2.5-pro (advanced reasoning)
- mistralai/mistral-nemo (balanced)

**Use Cases:**
- Production deployments
- Time-sensitive tasks
- Quality-critical outputs
- Low-volume usage

**Exception:** Security and Vision tasks always use local models (DSGVO compliance)

---

## Testing

### Test Files

**1. test_refactored_system.py**
- Tests architecture components
- Config loading (34 configs)
- Pipeline loading (4 pipelines)
- Backward compatibility
- No execution, just validation

**2. test_pipeline_execution.py**
- Tests actual pipeline execution
- Requires Ollama running
- Tests with real configs (dada, overdrive)
- End-to-end validation

### Running Tests

```bash
# Architecture tests (fast, no dependencies)
python3 test_refactored_system.py

# Execution tests (requires Ollama)
python3 test_pipeline_execution.py
```

### Test Coverage

**Current Coverage:**
- ✅ Config loading (34 configs)
- ✅ Pipeline loading (4 pipelines)
- ✅ Chunk building
- ✅ Placeholder replacement
- ✅ Backend routing
- ✅ Task-based model selection
- ✅ Execution modes (eco/fast)

**TODO:**
- [ ] #notranslate# marker logic
- [ ] Output generation pipelines
- [ ] ComfyUI workflow generation
- [ ] Multi-step text→media chains

---

## Key Design Decisions

### 1. Input-Type-Based Pipelines ✅

**Decision:** Pipelines categorized by INPUT structure, not output medium or backend

**Rationale:**
- Same input structure = same pipeline logic
- Output medium determined by config, not pipeline
- Backend determined by config, not pipeline
- Scalable (easy to add new media types without new pipelines)

**Example:**
- `single_prompt_generation` can output Image (SD3.5), Audio (Stable Audio), or Music
- Pipeline doesn't care about output type

---

### 2. Chunk Consolidation ✅

**Decision:** One universal `manipulate` chunk instead of multiple redundant chunks

**Removed:**
- translate.json (redundant with manipulate + translation context)
- prompt_interception.json (redundant with manipulate + different placeholder names)
- prompt_interception_lyrics.json (broken, invalid structure)
- prompt_interception_tags.json (broken, invalid structure)

**Rationale:**
- Content belongs in configs, not chunk names
- Reduces duplication (instruction appeared twice in rendered prompts)
- Cleaner architecture (3 chunks instead of 7)

---

### 3. Task-Based Model Selection ✅

**Decision:** Chunks declare `task_type`, model_selector.py maps to optimal LLM

**Implementation:**
```json
{
  "model": "task:translation",
  "meta": {"task_type": "translation"}
}
```

**Rationale:**
- Decouple chunk logic from specific model names
- Easy to upgrade models (change model_selector.py, not all chunks)
- Supports eco/fast mode switching
- DSGVO compliance (security/vision always local)

---

### 4. Backend Transparency ✅

**Decision:** Backend determined by config.meta.backend, not by pipeline or chunk

**Rationale:**
- Same pipeline can use ComfyUI (local) or OpenRouter (cloud)
- Easy to add new backends without changing pipelines
- Config controls everything (structure + content + backend)

---

### 5. No Fourth Layer ✅

**Decision:** No external registries or instruction_types system

**Rationale:**
- Instruction text belongs in configs (content layer)
- External indirection creates ambiguity and redundancy
- Three layers sufficient: Chunks (structure) → Pipelines (flow) → Configs (content)

---

## Future Enhancements

### Phase 1: Complete Output-Pipeline System
- [ ] Implement `single_prompt_generation.json` pipeline
- [ ] Implement `dual_prompt_generation.json` pipeline
- [ ] Create standard output configs (sd35_standard, flux1_dev, etc.)
- [ ] Test text→media chains

### Phase 2: Advanced Features
- [ ] `image_plus_text_generation` pipeline implementation
- [ ] Inpainting support
- [ ] ControlNet support
- [ ] Video generation support

### Phase 3: Additional Backends
- [ ] Replicate API integration
- [ ] Stability AI API
- [ ] Direct OpenAI DALL-E integration

### Phase 4: Optimization
- [ ] Batch processing (multiple prompts → multiple images)
- [ ] Streaming output (real-time generation progress)
- [ ] Cost optimization (choose cheapest model for task)
- [ ] Fallback chains (try model A, if fails try model B)

---

## Documentation & Logging Workflow

### Required Documentation Files

DevServer maintains **four types of documentation** to ensure persistent memory across Claude Code sessions:

#### 1. **DEVELOPMENT_LOG.md** - Session Tracking & Cost Accounting
**Purpose:** Linear chronological log of all implementation sessions with cost tracking

**When to update:**
- **Session Start:** Create new session entry with "In Progress" status
- **During Session:** Update "Tasks Completed" in real-time as tasks finish
- **Session End:** Fill in cost data, model usage, and final statistics

**What to track:**
- Session duration (wall time + API time)
- Cost breakdown by model (claude-sonnet, claude-haiku)
- Token usage (input/output/cache read/cache write)
- Tasks completed with ✅
- Code changes (lines added/removed)
- Files created/modified/deleted
- Documentation updates

**Format:**
```markdown
## Session [N]: [YYYY-MM-DD] - [Task Title]
**Duration (Wall):** [Time]
**Duration (API):** [Time]
**Cost:** $[Amount]

### Model Usage
- claude-sonnet: [stats]
- claude-haiku: [stats]

### Tasks Completed
1. ✅ [Task]

### Code Changes
- Lines added: [N]
- Lines removed: [N]
```

**Why:** Cost transparency + ability to analyze development velocity and efficiency

#### 2. **devserver_todos.md** - Task Management
**Purpose:** Current priorities and task status tracking

**When to update:**
- Mark tasks completed with ✅ and timestamp
- Add new tasks discovered during implementation
- Update status: NOT STARTED → IN PROGRESS → COMPLETED
- Reorder priorities when needed

**What to track:**
- Task description
- Status (NOT STARTED/IN PROGRESS/COMPLETED)
- Estimated time
- Priority level
- Dependencies

**Why:** Keeps focus on current priorities, prevents forgetting subtasks

#### 3. **DEVELOPMENT_DECISIONS.md** - Architectural Decisions
**Purpose:** Document WHY decisions were made (not just WHAT)

**When to update:**
- When making architectural decisions
- When choosing between alternatives
- When removing/adding major components
- When changing established patterns

**What to document:**
- Decision made
- Reasoning (technical/pedagogical/architectural)
- Alternatives considered
- Concrete implementation changes
- Files modified
- Future considerations

**Format:**
```markdown
## YYYY-MM-DD: [Decision Title]
### Decision
[What was decided]
### Reasoning
[Why - with user quotes if applicable]
### What Was Done
[Concrete changes]
### Files Modified
[List]
```

**Why:** Prevents re-litigating old decisions, maintains institutional knowledge

#### 4. **ARCHITECTURE.md** - System Structure (this file)
**Purpose:** Technical reference for how system works

**When to update:**
- When adding new architectural patterns
- When changing system structure
- When updating data flow
- When pipeline/chunk/config inventory changes

**What to document:**
- Three-layer architecture
- Pipeline types and purposes
- Data flow patterns
- Module responsibilities
- File structure

**IMPORTANT:** Create backup before major changes:
```bash
cp docs/ARCHITECTURE.md docs/tmp/ARCHITECTURE_$(date +%Y%m%d_%H%M%S).md
```

**Why:** Central reference for understanding system design

### Logging Frequency

**Real-time (as you work):**
- TodoWrite tool updates
- Track file modifications

**Per Task Completion:**
- Update DEVELOPMENT_LOG.md "Tasks Completed" section
- Update devserver_todos.md with ✅

**Per Implementation Decision:**
- Add entry to DEVELOPMENT_DECISIONS.md
- Document WHY, not just WHAT

**Per Session Start:**
- Create new session entry in DEVELOPMENT_LOG.md

**Per Session End:**
- Fill in session cost data
- Update cumulative statistics
- Create git commit with cost info
- Create continuation prompt if needed

### Git Commit Strategy

**When to commit:**
- After completing major architectural change
- After test suite passes
- Before starting new major task
- At session end (with proper documentation)

**Commit message format:**
```
[type]: [Brief description]

[Detailed changes]
- Change 1
- Change 2

Session cost: $XX.XX
Session duration: Xh XXm
Files changed: +XXX -XXX lines

Related docs:
- Updated DEVELOPMENT_DECISIONS.md
- Updated ARCHITECTURE.md
- Updated devserver_todos.md
```

### Session Recovery

**Before context window fills:**
- User signals: "Schreib jetzt alles in .md Dateien"
- Immediately stop current work
- Update DEVELOPMENT_LOG.md with session stats
- Create CONTINUE_SESSION_PROMPT.md in docs/tmp/
- Document current task progress, next priorities, and key context

**Why:** Claude Code sessions have limited context. Documentation provides continuity.

**See:** `docs/DEVELOPMENT_LOG.md` section "Logging Workflow Rules" for complete procedural details

---

## Related Documentation

- **DEVELOPMENT_LOG.md** - Session tracking and cost accounting (NEW!)
- **OUTPUT_PIPELINE_ARCHITECTURE.md** - Detailed output pipeline design
- **DEVELOPMENT_DECISIONS.md** - Chronological decision history
- **devserver_todos.md** - Implementation task list
- **CHUNK_ANALYSIS.md** - Chunk structure analysis (tmp)
- **PLACEHOLDER_ANALYSIS.md** - Placeholder redundancy analysis (tmp)
- **PIPELINE_ANALYSIS.md** - Pipeline inconsistencies analysis (tmp)
- **CONTINUE_SESSION_PROMPT.md** - Session recovery guide (tmp)

---

**Document Version:** 2.0
**Last Updated:** 2025-10-26
**Status:** Post-consolidation, output-pipeline design finalized
**Authors:** Joerissen + Claude collaborative design
