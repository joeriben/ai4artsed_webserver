# DevServer Architecture
**AI4ArtsEd Development Server - Technical Reference**

> **Status:** Current as of 2025-10-26 (Post instruction_types removal, Post legacy cleanup)
> **Decision Log:** See [docs/DEVELOPMENT_DECISIONS.md](docs/DEVELOPMENT_DECISIONS.md)
> **Audit Report:** See [docs/tmp/ARCHITECTURE_AUDIT.md](docs/tmp/ARCHITECTURE_AUDIT.md) (temporary)

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Three-Layer System](#three-layer-system)
3. [Data Flow](#data-flow)
4. [Engine Modules](#engine-modules)
5. [File Structure](#file-structure)
6. [API Routes](#api-routes)
7. [Execution Modes](#execution-modes)
8. [Testing](#testing)

---

## Architecture Overview

### Core Principle: Clean Three-Layer Architecture

DevServer implements a **template-based pipeline system** with three distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Layer 3: CONFIGS                     │
│              (User-Facing Content + Metadata)           │
│  • Display names, descriptions, categories              │
│  • Complete instruction text (context field)            │
│  • Parameters, media preferences                        │
│  • 34 configs in schemas/configs/*.json                 │
└─────────────────────────────────────────────────────────┘
                            ↓ references
┌─────────────────────────────────────────────────────────┐
│                  Layer 2: PIPELINES                     │
│                (Structural Templates)                   │
│  • Chunk sequences (NO content)                         │
│  • Required fields, defaults                            │
│  • 7 pipelines in schemas/pipelines/*.json              │
└─────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────┐
│                   Layer 1: CHUNKS                       │
│              (Primitive Operations)                     │
│  • Template strings with {{PLACEHOLDERS}}               │
│  • Backend type (ollama/comfyui)                        │
│  • Model specifications                                 │
│  • 7+ chunks in schemas/chunks/*.json                   │
└─────────────────────────────────────────────────────────┘
```

**Key Design Decision:**
NO fourth layer for indirection. Instruction text belongs in configs (content layer), not in external registries.

---

## Three-Layer System

### Layer 1: Chunks (Primitives)

**Purpose:** Atomic operations with template-based prompts
**Location:** `schemas/chunks/*.json`
**Count:** 7+ chunk templates

#### Available Chunks

| Chunk Name | Backend | Purpose |
|------------|---------|---------|
| `manipulate` | Ollama | Text transformation |
| `translate` | Ollama | Translation |
| `prompt_interception` | Ollama | Prompt transformation |
| `prompt_interception_tags` | Ollama | Music tag generation |
| `prompt_interception_lyrics` | Ollama | Music lyrics generation |
| `comfyui_image_generation` | ComfyUI | Image generation |
| `comfyui_audio_generation` | ComfyUI | Audio generation |

#### Chunk Structure

```json
{
  "name": "manipulate",
  "backend_type": "ollama",
  "model": "llama3.2:latest",
  "template": "{{INSTRUCTION}}\n\nUser Input:\n{{INPUT_TEXT}}",
  "parameters": {
    "temperature": 0.8,
    "max_tokens": 1000
  }
}
```

#### Placeholder System

| Placeholder | Source | Purpose |
|-------------|--------|---------|
| `{{INSTRUCTION}}` | `config.context` | Complete instruction text |
| `{{INSTRUCTIONS}}` | `config.context` | Alias for INSTRUCTION |
| `{{TASK}}` | `config.context` | Alias for INSTRUCTION |
| `{{CONTEXT}}` | `config.context` | Alias for INSTRUCTION |
| `{{INPUT_TEXT}}` | User input | Current input text |
| `{{PREVIOUS_OUTPUT}}` | Pipeline state | Output from previous chunk |
| `{{USER_INPUT}}` | User input | Original user input (unchanged) |

**Note:** All instruction-related placeholders resolve to `config.context` - the complete instruction text.

---

### Layer 2: Pipelines (Structure)

**Purpose:** Define chunk sequences (pure structure, NO content)
**Location:** `schemas/pipelines/*.json`
**Count:** 7 pipeline definitions

#### Available Pipelines

| Pipeline | Chunks | Use Case |
|----------|--------|----------|
| `simple_manipulation` | `[manipulate]` | Single-step text transformation |
| `simple_interception` | `[prompt_interception, manipulate]` | Intercept then transform |
| `prompt_interception_single` | `[prompt_interception]` | Interception only |
| `image_generation` | `[prompt_interception, comfyui_image_generation]` | Text → Image |
| `audio_generation` | `[prompt_interception, comfyui_audio_generation]` | Text → Audio |
| `music_generation` | `[prompt_interception_tags, prompt_interception_lyrics, comfyui_music_generation]` | Text → Music (3-step) |
| `video_generation` | `[prompt_interception, comfyui_video_generation]` | Text → Video |

#### Pipeline Structure

```json
{
  "name": "simple_manipulation",
  "description": "Single manipulation step",
  "chunks": ["manipulate"],
  "required_fields": [],
  "defaults": {},
  "meta": {}
}
```

**Design Principle:** Pipelines define HOW to process (structure), NOT WHAT to process (content).

---

### Layer 3: Configs (Content)

**Purpose:** User-facing configurations with complete instruction content
**Location:** `schemas/configs/*.json`
**Count:** 34 configs

#### Config Structure

```json
{
  "name": {
    "en": "Dadaism",
    "de": "Dadaismus"
  },
  "description": {
    "en": "Transform prompts through Dadaist perspective",
    "de": "Transformiert Prompts durch dadaistische Perspektive"
  },
  "category": {
    "en": "Art Movements",
    "de": "Kunstbewegungen"
  },
  "pipeline": "simple_manipulation",
  "context": "You are an artist working in the spirit of Dadaism. Your task is to transform the user's prompt by applying Dadaist principles: absurdity, anti-rationalism, spontaneity...",
  "parameters": {
    "temperature": 0.9
  },
  "media_preferences": {
    "preferred_media": ["image"]
  },
  "meta": {
    "tags": ["art", "experimental"]
  }
}
```

#### Field Reference

| Field | Type | Purpose | Required |
|-------|------|---------|----------|
| `name` | Multilingual Object | Display name | ✅ Yes |
| `description` | Multilingual Object | Description | ✅ Yes |
| `category` | Multilingual Object | UI categorization | ❌ Optional |
| `pipeline` | String | Pipeline reference | ✅ Yes |
| `context` | String | **Complete instruction text** | ✅ Yes |
| `parameters` | Object | LLM parameter overrides | ❌ Optional |
| `media_preferences` | Object | Media type hints | ❌ Optional |
| `meta` | Object | Additional metadata | ❌ Optional |

**Critical Field: `context`**
- Contains the COMPLETE instruction text (former "metaprompt")
- Replaces all `{{INSTRUCTION}}`, `{{TASK}}`, `{{CONTEXT}}` placeholders
- No indirection to external files

**Example Configs:**
- `dada.json` - Dadaist transformation (1287 characters context)
- `overdrive.json` - Exaggeration and amplification
- `translation_en.json` - English translation
- `stableaudio.json` - Audio generation with prompt interception
- `acestep_longnarrativeprompts.json` - Music generation (3-step pipeline)

---

## Data Flow

### Request Flow (Step by Step)

```
1. User Request
   ├─ config_name: "dada"
   ├─ input_text: "a peaceful garden"
   └─ execution_mode: "eco" (local) or "fast" (cloud)
              ↓
2. workflow_routes.py
   └─ Route: POST /execute_pipeline
              ↓
3. pipeline_executor.execute_pipeline(config_name, input_text, execution_mode)
              ↓
4. config_loader.get_config("dada")
   └─ Returns: ResolvedConfig
      ├─ name: "dada"
      ├─ pipeline_name: "simple_manipulation"
      ├─ chunks: ["manipulate"]
      └─ context: "You are an artist working in the spirit of Dadaism..."
              ↓
5. For each chunk in pipeline:

   a) chunk_builder.build_chunk(chunk_name, resolved_config, context)
      └─ Load template: chunks/manipulate.json
      └─ Replace placeholders:
         • {{INSTRUCTION}} ← resolved_config.context
         • {{INPUT_TEXT}} ← context.input_text
         • {{PREVIOUS_OUTPUT}} ← context.previous_output
      └─ Select model based on execution_mode:
         • eco: llama3.2:latest (Ollama)
         • fast: gpt-4o-mini (OpenRouter)
      └─ Build chunk_request with final prompt
              ↓
   b) backend_router.process_request(chunk_request)
      └─ Route to backend:
         • backend_type="ollama" → Ollama service
         • backend_type="comfyui" → ComfyUI service
              ↓
   c) Backend execution (Ollama/ComfyUI/OpenRouter)
              ↓
   d) Return response → Add to context.previous_outputs[]
              ↓
6. Pipeline complete
   └─ Return final_output to user
```

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       User Request                           │
│   config_name="dada", input_text="peaceful garden"          │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                   Config Loader                              │
│  1. Load config: schemas/configs/dada.json                   │
│  2. Load pipeline: schemas/pipelines/simple_manipulation.json│
│  3. Merge → ResolvedConfig                                   │
│     - chunks: ["manipulate"]                                 │
│     - context: "You are an artist..."                        │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                   Chunk Builder                              │
│  1. Load template: schemas/chunks/manipulate.json            │
│  2. Build replacement context:                               │
│     {                                                         │
│       'INSTRUCTION': resolved_config.context,                │
│       'INPUT_TEXT': 'peaceful garden',                       │
│       'PREVIOUS_OUTPUT': ''                                  │
│     }                                                         │
│  3. Replace placeholders in template                         │
│  4. Select model (execution_mode: eco/fast)                  │
│  5. Return chunk_request with final prompt                   │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  Backend Router                              │
│  Route based on backend_type:                                │
│  • ollama    → Ollama Service (local)                        │
│  • comfyui   → ComfyUI Service (local/remote)                │
│  • openrouter → OpenRouter API (cloud)                       │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                Backend Execution                             │
│  Execute model with final prompt                             │
│  Return response                                             │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│              Pipeline Context Update                         │
│  Add output to context.previous_outputs[]                    │
│  If more chunks: repeat from Chunk Builder                   │
│  If done: return final_output                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Engine Modules

### Core Architecture

**Location:** `schemas/engine/`

All modules are **ACTIVE** (no legacy code). Legacy modules have been marked `.OBSOLETE`.

#### 1. config_loader.py

**Purpose:** Load and resolve configs + pipelines

**Dataclasses:**
```python
@dataclass
class Pipeline:
    name: str
    description: str
    chunks: List[str]
    required_fields: List[str]
    defaults: Dict[str, Any]
    meta: Dict[str, Any]

@dataclass
class Config:
    name: str
    pipeline: str
    display_name: Dict[str, str]  # Multilingual
    description: Dict[str, str]   # Multilingual
    category: Optional[Dict[str, str]]
    context: Optional[str]         # Complete instruction text
    parameters: Optional[Dict[str, Any]]
    media_preferences: Optional[Dict[str, Any]]
    meta: Optional[Dict[str, Any]]

@dataclass
class ResolvedConfig:
    """Merged pipeline + config for execution"""
    name: str
    display_name: Dict[str, str]
    description: Dict[str, str]
    pipeline_name: str
    chunks: List[str]              # From pipeline
    context: Optional[str]          # From config
    parameters: Dict[str, Any]      # Merged
    media_preferences: Optional[Dict[str, Any]]
    meta: Dict[str, Any]            # Merged
```

**Key Methods:**
- `initialize(schemas_path)` - Load all configs and pipelines
- `get_config(name)` → `ResolvedConfig` - Get merged config
- `list_configs()` → `List[str]` - List all config names
- `list_pipelines()` → `List[str]` - List all pipeline names

**Singleton:** `config_loader = ConfigLoader()`

---

#### 2. chunk_builder.py

**Purpose:** Build executable chunks from templates + resolved configs

**Key Class:**
```python
class ChunkBuilder:
    def build_chunk(self,
                    chunk_name: str,
                    resolved_config: ResolvedConfig,
                    context: Dict[str, Any],
                    execution_mode: str = 'eco') -> Dict[str, Any]:
        """
        Build chunk with template and resolved config

        Returns:
            chunk_request = {
                'backend_type': 'ollama',
                'model': 'llama3.2:latest',
                'prompt': '<final prompt with replaced placeholders>',
                'parameters': {...},
                'metadata': {...}
            }
        """
```

**Process:**
1. Load chunk template from `schemas/chunks/<chunk_name>.json`
2. Get instruction text from `resolved_config.context`
3. Build replacement context:
   - `INSTRUCTION` ← `resolved_config.context`
   - `INPUT_TEXT` ← `context['input_text']`
   - `PREVIOUS_OUTPUT` ← `context['previous_output']`
4. Replace placeholders in template
5. Select model based on `execution_mode` (via model_selector)
6. Return chunk_request

**Key Change (2025-10-26):**
Now uses `resolved_config.context` directly (no instruction_resolver indirection).

---

#### 3. pipeline_executor.py

**Purpose:** Orchestrate pipeline execution

**Key Classes:**
```python
class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PipelineContext:
    input_text: str
    user_input: str
    previous_outputs: List[str]
    custom_placeholders: Dict[str, Any]
    pipeline_metadata: Dict[str, Any]

@dataclass
class PipelineResult:
    config_name: str
    status: PipelineStatus
    steps: List[PipelineStep]
    final_output: Optional[str]
    error: Optional[str]
    execution_time: Optional[float]
    metadata: Dict[str, Any]
```

**Key Methods:**
- `execute_pipeline(config_name, input_text, execution_mode)` → `PipelineResult`
- `stream_pipeline(...)` → `AsyncGenerator` - Streaming execution
- `get_available_configs()` → `List[str]` - List configs
- `get_config_info(config_name)` → `Dict` - Config metadata

**Singleton:** `executor = PipelineExecutor(schemas_path)`

---

#### 4. backend_router.py

**Purpose:** Route requests to appropriate backends

**Backends:**
- **Ollama** - Local LLM inference (eco mode)
- **ComfyUI** - Image/Audio/Video generation
- **OpenRouter** - Cloud LLM API (fast mode)

**Key Method:**
```python
async def process_request(self, request: BackendRequest) -> BackendResponse:
    """Route to ollama/comfyui/openrouter based on backend_type"""
```

---

#### 5. model_selector.py

**Purpose:** Select models based on execution mode

**Modes:**
- `eco` (local) - Uses Ollama models (llama3.2:latest, qwen2.5:14b, etc.)
- `fast` (cloud) - Uses OpenRouter models (gpt-4o-mini, claude-3.5-haiku, etc.)

**Key Method:**
```python
def select_model_for_mode(template_model: str, execution_mode: str) -> str:
    """Override template model based on execution mode"""
```

**Example:**
- Template: `llama3.2:latest`
- Mode: `eco` → Returns: `llama3.2:latest` (no change)
- Mode: `fast` → Returns: `gpt-4o-mini` (cloud model)

---

#### 6. comfyui_workflow_generator.py

**Purpose:** Generate ComfyUI workflows dynamically

Used for image/audio/video generation chunks.

---

#### 7. prompt_interception_engine.py

**Purpose:** Legacy bridge for prompt interception logic

Maintains compatibility with original prompt interception concept.

---

## File Structure

```
devserver/
├── ARCHITECTURE.md                    # This file
├── DEVSERVER_COMPREHENSIVE_DOCUMENTATION.md  # Pedagogical perspective
│
├── docs/                              # Documentation directory
│   ├── README.md                      # Documentation organization
│   ├── DEVELOPMENT_DECISIONS.md       # Decision log (updated by every task)
│   ├── LEGACY_SERVER_ARCHITECTURE.md  # Legacy system docs
│   ├── DEVSERVER_TODOS.md            # Development roadmap
│   ├── examples/                      # Example docs
│   │   └── API_USAGE_EXAMPLE.md
│   └── tmp/                           # Temporary task docs
│       ├── ARCHITECTURE_AUDIT.md      # Technical audit (this task)
│       ├── REFACTORING_SUMMARY.md
│       └── ...
│
├── schemas/
│   ├── chunks/                        # Layer 1: Primitives (7 files)
│   │   ├── manipulate.json
│   │   ├── translate.json
│   │   ├── prompt_interception.json
│   │   ├── prompt_interception_tags.json
│   │   ├── prompt_interception_lyrics.json
│   │   ├── comfyui_image_generation.json
│   │   └── comfyui_audio_generation.json
│   │
│   ├── pipelines/                     # Layer 2: Structure (7 files)
│   │   ├── simple_manipulation.json
│   │   ├── simple_interception.json
│   │   ├── prompt_interception_single.json
│   │   ├── image_generation.json
│   │   ├── audio_generation.json
│   │   ├── music_generation.json
│   │   └── video_generation.json
│   │
│   ├── configs/                       # Layer 3: Content (34 files) ✅ ACTIVE
│   │   ├── dada.json
│   │   ├── overdrive.json
│   │   ├── translation_en.json
│   │   ├── stableaudio.json
│   │   └── ... (30 more)
│   │
│   ├── configs_old_DELETEME/          # Legacy Python configs (to be deleted)
│   ├── schema_data_LEGACY_TESTS/      # Legacy test configs
│   │
│   ├── engine/                        # Core engine modules
│   │   ├── config_loader.py           # ✅ ACTIVE
│   │   ├── chunk_builder.py           # ✅ ACTIVE
│   │   ├── pipeline_executor.py       # ✅ ACTIVE
│   │   ├── backend_router.py          # ✅ ACTIVE
│   │   ├── model_selector.py          # ✅ ACTIVE
│   │   ├── comfyui_workflow_generator.py  # ✅ ACTIVE
│   │   ├── prompt_interception_engine.py  # ✅ ACTIVE
│   │   ├── __init__.py
│   │   ├── schema_registry.py.OBSOLETE     # ❌ LEGACY
│   │   ├── chunk_builder_old.py.OBSOLETE   # ❌ LEGACY
│   │   ├── pipeline_executor_old.py.OBSOLETE  # ❌ LEGACY
│   │   └── instruction_resolver.py.OBSOLETE   # ❌ LEGACY
│   │
│   ├── instruction_types.json.OBSOLETE # ❌ LEGACY
│   └── __init__.py
│
├── my_app/
│   └── routes/
│       └── workflow_routes.py         # API routes
│
├── test_refactored_system.py         # Component tests ✅
└── test_pipeline_execution.py        # Full execution tests (requires Ollama)
```

---

## API Routes

**File:** `my_app/routes/workflow_routes.py`

### POST /execute_pipeline

Execute a config pipeline.

**Request:**
```json
{
  "config_name": "dada",
  "input_text": "a peaceful garden",
  "execution_mode": "eco"
}
```

**Response:**
```json
{
  "config_name": "dada",
  "status": "completed",
  "final_output": "An absurd garden where plants argue philosophically...",
  "execution_time": 2.5,
  "metadata": {
    "total_steps": 1,
    "pipeline_name": "simple_manipulation"
  }
}
```

---

### GET /pipeline_configs_metadata

Get metadata for all configs (for Expert Mode UI).

**Response:**
```json
{
  "configs": [
    {
      "id": "dada",
      "name": {
        "en": "Dadaism",
        "de": "Dadaismus"
      },
      "description": {
        "en": "Transform prompts through Dadaist perspective"
      },
      "category": {
        "en": "Art Movements"
      },
      "pipeline": "simple_manipulation"
    }
  ],
  "count": 34
}
```

**Note:** `instruction_type` field removed (2025-10-26).

---

## Execution Modes

DevServer supports two execution modes for flexible deployment:

### eco Mode (Default)
- **Backend:** Ollama (local)
- **Models:** llama3.2:latest, qwen2.5:14b, etc.
- **Cost:** Free
- **Speed:** Moderate (depends on local hardware)
- **Privacy:** Full (DS-GVO compliant, no data leaves server)

### fast Mode
- **Backend:** OpenRouter (cloud API)
- **Models:** gpt-4o-mini, claude-3.5-haiku, etc.
- **Cost:** Paid (per token)
- **Speed:** Fast
- **Privacy:** Data sent to external API

**Selection:**
- User specifies `execution_mode` parameter in API request
- `model_selector.py` overrides template models based on mode
- Backend router handles appropriate service

---

## Testing

### test_refactored_system.py

**Purpose:** Component tests (config loader, pipeline executor)

**Tests:**
1. Config Loader - Load 34 configs, resolve pipelines
2. Pipeline Executor - Info methods, metadata

**Run:**
```bash
python3 test_refactored_system.py
```

**Status:** ✅ All tests passing (as of 2025-10-26)

---

### test_pipeline_execution.py

**Purpose:** Full execution tests with actual LLM calls

**Requirements:** Ollama running locally

**Tests:**
- Actual pipeline execution
- Config-specific tests (dada, overdrive, etc.)

---

## Change History

**Major Changes Documented in:** [docs/DEVELOPMENT_DECISIONS.md](docs/DEVELOPMENT_DECISIONS.md)

### 2025-10-26: instruction_types System Removed
- Removed redundant fourth layer (instruction_types.json)
- All configs now use `context` field for instruction text
- See: [DEVELOPMENT_DECISIONS.md](docs/DEVELOPMENT_DECISIONS.md#2025-10-26-removal-of-instruction_types-system)

### 2025-10-26: Legacy Code Cleanup
- Marked all pre-refactoring modules as .OBSOLETE
- Clean engine with only active modules
- See: [DEVELOPMENT_DECISIONS.md](docs/DEVELOPMENT_DECISIONS.md#2025-10-26-removal-of-legacy-devserver-code)

### 2025-10-26: Documentation Reorganization
- Created docs/ structure (permanent, tmp/, examples/)
- Created DEVELOPMENT_DECISIONS.md for decision tracking
- See: [docs/README.md](docs/README.md)

---

## Development Principles

### Immutable Architecture Rules

1. **Three Layers Only** - No fourth layer for indirection
2. **Content in Configs** - Instruction text belongs in config.context, not external files
3. **Structure vs Content** - Pipelines define HOW (structure), Configs define WHAT (content)
4. **Single Source of Truth** - Each data type has one canonical location
5. **No Data Duplication** - Configs stored in files, not in database/registry

### Terminology Guidelines

From [DEVELOPMENT_DECISIONS.md](docs/DEVELOPMENT_DECISIONS.md):
- Avoid terms like "creative" (contradicts theoretical approach)
- Focus: "Haltungen statt Stile" (attitudes not styles)
- No "solutionistic" language

### For Future Tasks

**Every significant architectural change MUST:**
1. Update [docs/DEVELOPMENT_DECISIONS.md](docs/DEVELOPMENT_DECISIONS.md)
2. Update this ARCHITECTURE.md if core architecture changes
3. Run tests to verify changes
4. Create temporary reports in docs/tmp/ if needed

---

**Last Updated:** 2025-10-26
**Next Review:** After pedagogical architecture documentation (DEVSERVER_ARCHITECTURE.md)
**Maintainer:** See commit history
