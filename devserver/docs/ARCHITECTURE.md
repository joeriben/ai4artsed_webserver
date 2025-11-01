# DevServer Architecture
**AI4ArtsEd Development Server - Complete Technical Reference**

> **Last Updated:** 2025-11-01
> **Status:** AUTHORITATIVE - 4-Stage Orchestration Architecture Documented
> **Version:** 3.0 (4-Stage Flow + Components Reference - Fully Consolidated)

---

## Table of Contents

### Part I: Orchestration (How It Works)
1. [4-Stage Orchestration Flow](#1-4-stage-orchestration-flow) ⭐ **START HERE**

### Part II: Components (What The Parts Are)
2. [Architecture Overview](#2-architecture-overview)
3. [Three-Layer System](#3-three-layer-system)
4. [Pipeline Types](#4-pipeline-types)
5. [Data Flow Patterns](#5-data-flow-patterns)
6. [Engine Modules](#6-engine-modules)
7. [Backend Routing](#7-backend-routing)
8. [Model Selection](#8-model-selection)
9. [File Structure](#9-file-structure)
10. [API Routes](#10-api-routes)
11. [Frontend Architecture](#11-frontend-architecture)
12. [Execution Modes](#12-execution-modes)
13. [Documentation & Logging Workflow](#13-documentation--logging-workflow)

---

# PART I: ORCHESTRATION

---

## 1. 4-Stage Orchestration Flow

**⭐ AUTHORITATIVE SECTION - Read this first before implementing any flow logic**

**Version:** 2.0 (2025-11-01)
**Source:** Consolidated from 4_STAGE_ARCHITECTURE.md

### 1.1 Executive Summary

**DevServer orchestrates a 4-stage flow where:**
- **Stage 1** runs once per user input (based on input type, not pipeline declaration)
- **Stage 2** executes the main pipeline (can be complex: loops, branches, multiple outputs)
- **Stage 3-4** run once PER OUTPUT REQUEST from Stage 2 (not once per pipeline)

**Key Principle:** Pipelines are DUMB (declare inputs/outputs), DevServer is SMART (knows safety rules).

### 1.2 Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ DevServer (schema_pipeline_routes.py)                          │
│ ROLE: Smart Orchestrator - Knows 4-Stage Flow & Safety Rules   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STAGE 1: Pre-Interception (Input Preparation)                  │
│ ════════════════════════════════════════════════════════════   │
│   DevServer reads: pipeline.input_requirements                 │
│   - texts: N  → Run translation + text_safety for each         │
│   - images: M → Run image_safety for each                      │
│                                                                 │
│   Example: {"texts": 2, "images": 1}                           │
│   → translation(text1), text_safety(text1)                     │
│   → translation(text2), text_safety(text2)                     │
│   → image_safety(image1)                                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STAGE 2: Interception (Main Pipeline - Can Be Complex)         │
│ ════════════════════════════════════════════════════════════   │
│   PipelineExecutor.execute_pipeline(config, inputs)            │
│   - DUMB: Just executes chunks                                 │
│   - NO pre-processing, NO safety checks                        │
│   - CAN: loop, branch, request multiple outputs               │
│                                                                 │
│   Pipeline returns: PipelineResult {                           │
│     final_output: "transformed text",                          │
│     output_requests: [                                         │
│       {type: "image", prompt: "...", params: {...}},          │
│       {type: "audio", prompt: "...", params: {...}}           │
│     ]                                                          │
│   }                                                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STAGE 3-4: For EACH output_request from Stage 2                │
│ ════════════════════════════════════════════════════════════   │
│   FOR EACH request in pipeline_result.output_requests:         │
│                                                                 │
│     STAGE 3: Pre-Output Safety                                 │
│       - Hybrid: Fast string-match → LLM if needed             │
│       - Check: request.prompt against safety_level            │
│       - If blocked: Skip Stage 4, return text alternative     │
│                                                                 │
│     STAGE 4: Media Generation                                  │
│       - Execute output config (e.g., gpt5_image)              │
│       - Generate media                                         │
│       - Return media reference (prompt_id, URL, etc.)         │
│                                                                 │
│   Collect all generated media + metadata                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Separation of Concerns

#### What Pipelines Declare (DUMB)

**Pipeline configs declare ONLY input/output structure:**

```json
{
  "name": "complex_interception",
  "input_requirements": {
    "texts": 2,           // "I need 2 text inputs"
    "images": 1           // "I need 1 image input"
  },
  "chunks": ["manipulate", "translate", ...],
  "control_flow": "iterative",
  "meta": {
    "max_iterations": 8,
    "supports_multiple_outputs": true
  }
}
```

**Pipelines DO NOT declare:**
- ❌ Safety requirements (DevServer knows this)
- ❌ Translation needs (DevServer knows: text → translate)
- ❌ Pre-processing steps (DevServer orchestrates Stage 1)
- ❌ When to run safety checks (DevServer orchestrates Stage 3)

#### What DevServer Knows (SMART)

**DevServer has hardcoded safety rules:**

```python
# schema_pipeline_routes.py

STAGE1_RULES = {
    "text": ["translation", "text_safety_stage1"],
    "image": ["image_safety_stage1"],
    "audio": ["audio_safety_stage1"]  # Future
}

STAGE3_RULES = {
    "image": "text_safety_check_{safety_level}",  # kids/youth/off
    "audio": "audio_safety_check_{safety_level}",  # Future
    "video": "video_safety_check_{safety_level}"   # Future
}
```

**Why non-redundant?**
- If pipeline says `"texts": 2`, DevServer runs Stage 1 safety for BOTH texts
- No duplication in pipeline configs
- Change safety rules in ONE place (DevServer)
- Prevents inconsistencies

### 1.4 Stage-by-Stage Flow

[See above, 1.2 Core Architecture and IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md]

### 1.5 Complex Pipeline Examples

#### Example 1: Simple Text Transformation + Image

**User Input:** "EIne Blume auf der Wiese"
**Config:** overdrive.json
**Execution Mode:** fast
**Safety Level:** kids

**Flow:**
```
┌─ STAGE 1 (Run ONCE) ─────────────────────────────────────────┐
│ Input: "EIne Blume auf der Wiese"                            │
│ → Translation: "One flower on the meadow"                    │
│ → Stage 1 Safety: PASSED (fast-path, no unsafe terms)       │
└──────────────────────────────────────────────────────────────┘

┌─ STAGE 2 (Main Pipeline) ────────────────────────────────────┐
│ Pipeline: overdrive (text_transformation)                    │
│ Input: "One flower on the meadow"                            │
│ → manipulate chunk with overdrive context                    │
│ Output: "In the vast, undulating sea of emerald..."         │
│                                                              │
│ Output Requests: [                                           │
│   {type: "image", prompt: "In the vast, undulating..."}     │
│ ]                                                            │
└──────────────────────────────────────────────────────────────┘

┌─ STAGE 3-4 (Run ONCE per output request) ───────────────────┐
│ Request #1: image                                            │
│                                                              │
│ STAGE 3: Pre-Output Safety                                  │
│   Prompt: "In the vast, undulating..."                      │
│   → Fast-path check: No unsafe terms → PASSED (0.1ms)       │
│                                                              │
│ STAGE 4: Media Generation                                   │
│   Lookup: image/fast → gpt5_image                           │
│   → execute_pipeline('gpt5_image', prompt) [NO STAGE 1-3!]  │
│   → Returns: prompt_id "abc123"                             │
└──────────────────────────────────────────────────────────────┘
```

**Current Bug (What Happens Now):**
```
✅ Stage 1 runs once → Good
✅ Stage 2 runs once → Good
✅ Stage 3 runs once → Good
❌ Stage 4 calls execute_pipeline('gpt5_image', ...)
   → execute_pipeline() runs Stage 1-3 AGAIN! → BAD
   → Translation runs on already-English text
   → Safety runs twice
   → Wasted time + API calls
```

#### Example 3: Multi-Output (Model Comparison)

**Scenario:** Generate same prompt with multiple models for comparison

**Config:** `image_comparison.json`
```json
{
  "pipeline": "text_transformation",
  "context": "Pass through unchanged",
  "media_preferences": {
    "output_configs": ["sd35_large", "gpt5_image"]
  }
}
```

**Flow:**
```
Input: "Eine Blume auf der Wiese"
  ↓
Stage 1: translation + text_safety (once)
  → "A flower on the meadow" + PASSED
  ↓
Stage 2: text_transformation (once)
  → "A flower on the meadow" (pass-through)
  ↓
Stage 3-4 Loop: FOR EACH output_config
  ├─ Iteration 1: sd35_large
  │  ├─ Stage 3: Pre-Output Safety ✅
  │  └─ Stage 4: ComfyUI workflow → image_1.png
  └─ Iteration 2: gpt5_image
     ├─ Stage 3: Pre-Output Safety ✅
     └─ Stage 4: OpenRouter API → image_2.png

Response: {
  "media_outputs": [
    {"config": "sd35_large", "output": "prompt_id_1"},
    {"config": "gpt5_image", "output": "base64_data"}
  ]
}
```

**Key Points:**
✅ Stage 1 runs once (not 2x) - no redundant translation
✅ Stage 2 runs once (not 2x) - no redundant pipeline
✅ Stage 3-4 loop per output - each gets independent safety check
✅ Efficient: Only outputs require duplication, not inputs

**Use Cases:**
- Model comparison (SD3.5 vs GPT-5)
- Multi-format output (image + audio)
- Multi-resolution output (1024px + 2048px)

**Implementation:** See `schema_pipeline_routes.py` Stage 3-4 Loop

#### Example 4: Recursive Pipeline (Stille Post)

**Scenario:** 8-iteration translation loop (Chinese Whispers)

**Config:** `stillepost.json`
```json
{
  "pipeline": "text_transformation_recursive",
  "parameters": {
    "iterations": 8,
    "use_random_languages": true,
    "final_language": "en"
  }
}
```

**Flow:**
```
Input: "Eine Blume auf der Wiese"
  ↓
Stage 1: translation + text_safety (once)
  → "A flower on the meadow" + PASSED
  ↓
Stage 2: text_transformation_recursive (once, loops internally)
  Iteration 1: translate to Hindi
  Iteration 2: translate to Polish
  ...
  Iteration 8: translate to English
  → "The Dutch translation of..." (mangled text)
  ↓
Stage 3: Pre-Output Safety ✅
  ↓
Stage 4: Media Generation → image.png
```

**Key Points:**
✅ Stage 1 runs once (not 8x) - Critical test PASSED
✅ Loop runs INSIDE Stage 2 pipeline
✅ Config controls loop behavior (iterations, languages, final_language)
❌ Does NOT call execute_pipeline() recursively (would trigger Stage 1-3 redundancy)

**Pedagogical Goal:**
- Students see prompt degradation over iterations
- "Stille Post" (Chinese Whispers) workflow
- User-editable configs for different iteration counts

**Implementation:** See `pipeline_executor.py` _execute_recursive_pipeline_steps()

### 1.6 Implementation Status

**Current (2025-11-01 Evening):**
- ✅ Stage 1-3 logic in `schema_pipeline_routes.py` - CORRECT (Session 9)
- ✅ PipelineExecutor is DUMB engine - CORRECT (Session 9)
- ✅ Non-redundant safety rules - IMPLEMENTED (Session 9)
- ✅ Recursive Pipeline System - IMPLEMENTED (Session 11 Part 1)
- ✅ Multi-Output Support - IMPLEMENTED (Session 11 Part 2)

**Validation Tests:**
- ✅ Stillepost (8 iterations): Stage 1 ran once (not 8x) - PASSED
- ✅ Image Comparison (2 outputs): Stage 1 ran once (not 2x) - PASSED
- ✅ Simple config (dada): Stage 1-4 all ran once - PASSED
- ✅ Logs confirm clean execution (no redundancy) - PASSED

**Architecture Proven Correct:**
- DevServer = Smart Orchestrator ✅
- PipelineExecutor = Dumb Engine ✅
- Non-Redundant Safety Rules ✅
- Scalable to Complex Flows ✅

**See:**
- `docs/DEVELOPMENT_DECISIONS.md` (2025-11-01 entries) for design rationale
- `docs/DEVELOPMENT_LOG.md` (Session 9, 11) for implementation details
- `schema_pipeline_routes.py` for orchestration code
- `pipeline_executor.py` for execution engine

---

# PART II: COMPONENTS

---

## 2. Architecture Overview

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

#### Chunk Types

**1. Processing Chunks** (Text transformation via LLM)
| Chunk Name | Backend | Purpose | Task Type |
|------------|---------|---------|-----------|
| `manipulate` | Ollama/OpenRouter | Universal text transformation | `standard` / `advanced` |

**2. Output Chunks** (Media generation via ComfyUI)
| Chunk Name | Backend | Purpose | Media Type |
|------------|---------|---------|-----------|
| `output_image_sd35_standard` | ComfyUI | SD3.5 Large image generation | Image |
| `output_audio_stable_audio` | ComfyUI | Stable Audio generation | Audio |
| `output_music_acestep` | ComfyUI | AceStep music (Tags + Lyrics) | Music |

**Note:**
- After consolidation, we have ONE text transformation chunk (`manipulate`) instead of multiple redundant chunks
- Output-Chunks contain complete ComfyUI API workflows embedded in JSON (not generated dynamically)

#### Chunk Structure

**Type 1: Processing Chunk (LLM-based text transformation)**

```json
{
  "name": "manipulate",
  "type": "processing_chunk",
  "description": "Universal text transformation with instruction-based prompting",
  "template": "{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}",
  "backend_type": "ollama",
  "model": "task:standard",
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": false
  },
  "meta": {
    "task_type": "standard",
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

**Type 2: Output Chunk (ComfyUI media generation)**

Output-Chunks contain **complete ComfyUI API workflows** embedded directly in the JSON, along with metadata for input/output mapping.

```json
{
  "name": "output_audio_stable_audio",
  "type": "output_chunk",
  "backend_type": "comfyui",
  "media_type": "audio",
  "description": "Stable Audio Open - 47 second audio generation",

  "workflow": {
    "3": {
      "inputs": {
        "seed": "{{SEED}}",
        "steps": "{{STEPS}}",
        "cfg": "{{CFG}}",
        "sampler_name": "{{SAMPLER}}",
        "scheduler": "{{SCHEDULER}}",
        "denoise": 1,
        "model": ["4", 0],
        "positive": ["6", 0],
        "negative": ["7", 0],
        "latent_image": ["11", 0]
      },
      "class_type": "KSampler",
      "_meta": {"title": "KSampler"}
    },
    "4": {
      "inputs": {
        "ckpt_name": "stable-audio-open-1.0.safetensors"
      },
      "class_type": "CheckpointLoaderSimple",
      "_meta": {"title": "Load Checkpoint"}
    },
    "6": {
      "inputs": {
        "text": "{{PROMPT}}",
        "clip": ["10", 0]
      },
      "class_type": "CLIPTextEncode",
      "_meta": {"title": "CLIP Text Encode (Prompt)"}
    },
    "7": {
      "inputs": {
        "text": "{{NEGATIVE_PROMPT}}",
        "clip": ["10", 0]
      },
      "class_type": "CLIPTextEncode",
      "_meta": {"title": "CLIP Text Encode (Negative)"}
    },
    "10": {
      "inputs": {
        "clip_name": "t5-base.safetensors",
        "type": "stable_audio",
        "device": "default"
      },
      "class_type": "CLIPLoader",
      "_meta": {"title": "Load CLIP"}
    },
    "11": {
      "inputs": {
        "seconds": "{{DURATION}}",
        "batch_size": 1
      },
      "class_type": "EmptyLatentAudio",
      "_meta": {"title": "Empty Latent Audio"}
    },
    "12": {
      "inputs": {
        "samples": ["3", 0],
        "vae": ["4", 2]
      },
      "class_type": "VAEDecodeAudio",
      "_meta": {"title": "VAE Decode Audio"}
    },
    "19": {
      "inputs": {
        "filename_prefix": "audio/ComfyUI",
        "quality": "V0",
        "audioUI": "",
        "audio": ["12", 0]
      },
      "class_type": "SaveAudioMP3",
      "_meta": {"title": "Save Audio (MP3)"}
    }
  },

  "input_mappings": {
    "prompt": {
      "node_id": "6",
      "field": "inputs.text",
      "source": "{{PREVIOUS_OUTPUT}}"
    },
    "negative_prompt": {
      "node_id": "7",
      "field": "inputs.text",
      "default": ""
    },
    "duration": {
      "node_id": "11",
      "field": "inputs.seconds",
      "default": 47.6
    },
    "steps": {
      "node_id": "3",
      "field": "inputs.steps",
      "default": 50
    },
    "cfg": {
      "node_id": "3",
      "field": "inputs.cfg",
      "default": 4.98
    },
    "seed": {
      "node_id": "3",
      "field": "inputs.seed",
      "default": "random"
    }
  },

  "output_mapping": {
    "node_id": "19",
    "output_type": "audio",
    "format": "mp3",
    "field": "filename_prefix"
  },

  "meta": {
    "estimated_duration": "30-60s",
    "requires_gpu": true,
    "model_file": "stable-audio-open-1.0.safetensors",
    "clip_file": "t5-base.safetensors"
  }
}
```

**Key Design Principles:**

1. **Embedded Workflows:** Complete ComfyUI API JSON workflow is stored in the chunk
   - No dynamic generation required
   - No dependency on `comfyui_workflow_generator.py` (deprecated)
   - Server simply fills placeholders and submits to ComfyUI

2. **Input Mappings:** Define where to inject data into the workflow
   - Maps semantic names (`prompt`, `duration`) to specific node fields
   - Supports defaults and placeholder replacement
   - DevServer knows where to put user input/pipeline output

3. **Output Mapping:** Define where to extract generated media
   - Identifies the SaveImage/SaveAudio node
   - Specifies expected format (png, mp3, wav)
   - Enables proper media retrieval after generation

4. **Backend Transparency:** Workflow could theoretically work with any ComfyUI-compatible backend
   - SwarmUI
   - ComfyUI forks
   - Any system that accepts ComfyUI API format

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
  "input_requirements": {
    "texts": 1
  },
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

**Key Field - `input_requirements`:**
Declares what inputs the pipeline expects. DevServer uses this for Stage 1 orchestration:
- `{"texts": 1}` - One text input (most configs: dada, bauhaus, overdrive, etc.)
- `{"texts": 2}` - Two text inputs (music_generation for AceStep: tags + lyrics)
- Future: `{"texts": 1, "images": 1}` for inpainting/img2img pipelines

DevServer reads this field and runs appropriate Stage 1 processing (translation + safety) for each input before executing the main pipeline.

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
    "stage": "interception",     // Required: "pre_interception" | "interception" | "pre_output" | "output"
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

**Key Field - `meta.stage`:**
The `stage` field identifies which stage of the 4-Stage Architecture this config belongs to:
- `"pre_interception"` - Stage 1 configs (translation, safety checks before main pipeline)
- `"interception"` - Stage 2 configs (main transformation: dada, bauhaus, overdrive, etc.)
- `"pre_output"` - Stage 3 configs (safety checks before media generation)
- `"output"` - Stage 4 configs (media generation: sd35_large, gpt5_image, stableaudio, etc.)

This field helps DevServer orchestrate the correct flow and enables future organization (e.g., moving output configs to separate folder).

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
Text Prompt → Config (e.g., sd35_large.json)
  → single_prompt_generation Pipeline
    → Proxy-Chunk (output_image.json)
      → Backend Router (loads OUTPUT_CHUNK from config)
        → Specialized Output-Chunk (output_image_sd35_large.json)
          → ComfyUI API OR OpenRouter API
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

### Output-Config Selection Matrix

Server selects OUTPUT-CONFIGS (not chunks directly) using `output_config_defaults.json`:

| Media Type | eco Mode Config | fast Mode Config | Status |
|------------|-----------------|------------------|--------|
| **image** | `sd35_large` | `flux1_openrouter` | eco: ✅, fast: Planned |
| **audio** | `stable_audio` | `(fallback to eco)` | eco: ✅, fast: Not available |
| **music** | `acestep` | `(fallback to eco)` | eco: ✅, fast: Not available |
| **video** | `animatediff` | `sora2` | eco: Planned, fast: Planned |

**Implementation:** `schemas/output_config_defaults.json`

**Important:** Server selects CONFIGS, configs specify CHUNKS via OUTPUT_CHUNK parameter:
1. Server reads Interception-Config's `media_preferences.default_output` (e.g., "image")
2. Server reads `execution_mode` (eco/fast)
3. Server looks up `output_config_defaults["image"]["eco"]` → "sd35_large"
4. Server executes Output-Pipeline with config "sd35_large"
5. Config has `"OUTPUT_CHUNK": "output_image_sd35_large"`
6. Proxy-Chunk (output_image.json) receives this parameter
7. backend_router loads specialized Output-Chunk
8. Output-Chunk contains complete ComfyUI API workflow

---

### Output-Chunk Naming Convention

Output-Chunks are **highly specialized** for specific backend+model combinations:

**Format:** `output_[media]_[model]_[variant]`

**Examples:**
- ✅ `output_image_sd35_large` - SD3.5 Large via ComfyUI
- ✅ `output_image_gpt5` - GPT-5 Image via OpenRouter
- ✅ `output_audio_stable_audio` - Stable Audio via ComfyUI
- ✅ `output_music_acestep` - AceStep via ComfyUI

**NOT Config-Level Terms:**
- ❌ `output_image_sd35_standard` - "standard" is config concept, not chunk!

**Each Output-Chunk contains:**
- Complete backend-specific workflow (e.g., ComfyUI API JSON)
- input_mappings (where to inject prompts/parameters)
- output_mapping (where to extract generated media)

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
  "chunks": ["output_image"],
  "meta": {
    "input_type": "single_text",
    "output_types": ["image", "audio", "music", "video"],
    "backend_agnostic": true,
    "note": "Uses Proxy-Chunk system - NO manipulate (Output-Pipeline is primitive!)"
  }
}
```

**Key Design: Proxy-Chunk System**

Output-Pipeline uses a **Proxy-Chunk** (`output_image.json`) that delegates to specialized Output-Chunks:

**Proxy-Chunk: output_image.json**
```json
{
  "name": "output_image",
  "type": "processing_chunk",
  "backend_type": "comfyui",
  "template": "",
  "model": "",
  "parameters": {
    "output_chunk": "{{OUTPUT_CHUNK}}",
    "prompt": "{{PREVIOUS_OUTPUT}}",
    "negative_prompt": "{{NEGATIVE_PROMPT}}",
    "width": "{{WIDTH}}",
    "height": "{{HEIGHT}}"
  }
}
```

**Config Selection (Runtime):**
```python
# Server determines OUTPUT-CONFIG based on media_type + execution_mode
# Using output_config_defaults.json

media_type = interception_config.media_preferences.default_output  # "image"
execution_mode = "eco"  # From frontend or server default

# Lookup in output_config_defaults.json
output_config_name = output_config_defaults[media_type][execution_mode]
# → "sd35_large"

# Execute Output-Pipeline with selected config
result = executor.execute_pipeline(
    config_name="sd35_large",  # Output-Config
    input_text=transformed_text
)
```

**Output-Config: sd35_large.json**
```json
{
  "pipeline": "single_prompt_generation",
  "parameters": {
    "OUTPUT_CHUNK": "output_image_sd35_large",  // Specialized chunk
    "WIDTH": 1024,
    "HEIGHT": 1024,
    "STEPS": 25
  }
}
```

**Specialized Output-Chunk: output_image_sd35_large.json**
```json
{
  "name": "output_image_sd35_large",
  "type": "output_chunk",
  "backend_type": "comfyui",
  "media_type": "image",
  "workflow": {
    // Complete ComfyUI API workflow (11 nodes)
    // See Output-Chunk section for full structure
  },
  "input_mappings": {
    "prompt": {"node_id": "10", "field": "inputs.value", ...},
    "negative_prompt": {"node_id": "11", ...}
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

### Pattern 5: Auto-Media Generation (Text Transformation + Auto Output)

**Purpose:** Text transformation configs (like dada.json) can suggest a media type for automatic media generation after text transformation completes.

**Architecture Principle:** **Separation of Concerns**
- Pre-pipeline configs (dada.json) suggest media type via `media_preferences.default_output`
- Pre-pipeline configs DO NOT choose specific models or output configs
- DevServer uses a central `output_config_defaults.json` to map media types to output configs

**Data Flow:**
```
User Input: "A surreal dream"
  ↓
Config: dada.json (pipeline: text_transformation)
  media_preferences.default_output = "image"
  ↓
Pipeline: text_transformation
  ↓
Output: "Ein surrealistischer Traum in dadaistischer Ästhetik..."
  ↓
DevServer Auto-Media Logic:
  1. Read: config.media_preferences.default_output = "image"
  2. Read: execution_mode = "eco"
  3. Lookup: output_config_defaults["image"]["eco"] → "sd35_large"
  4. Execute: single_prompt_generation pipeline with sd35_large config
  ↓
Output: Image (PNG) generated via SD3.5 Large
```

**output_config_defaults.json Structure:**
```json
{
  "image": {
    "eco": "sd35_large",
    "fast": "flux1_openrouter"
  },
  "audio": {
    "eco": "stable_audio",
    "fast": "stable_audio_api"
  },
  "music": {
    "eco": "acestep",
    "fast": null
  },
  "video": {
    "eco": "animatediff",
    "fast": null
  }
}
```

**Why This Architecture:**

1. **Separation of Concerns:** Text manipulation configs don't know about specific models
2. **Centralized Defaults:** One file defines system-wide output defaults
3. **Easy Maintenance:** Change default image model by editing one line
4. **Pedagogically Clear:** Dada says "I produce visual content" not "I use SD3.5 Large"
5. **Execution Mode Aware:** Different defaults for eco (local) vs fast (cloud)

**User Override Options:**

Users can override the auto-media generation:
- `#image#` tag in input → force image generation
- `#audio#` tag → force audio generation
- `#music#` tag → force music generation
- `#video#` tag → force video generation
- No tag + `default_output = "text"` → no auto-media, return text only

**Implementation Location:**
- File: `schemas/output_config_defaults.json`
- Loader: `schemas/engine/output_config_selector.py`
- Usage: `my_app/routes/schema_pipeline_routes.py` (auto-media generation logic)
- API Endpoint: `/api/schema/pipeline/execute`
- Note: Replaced deprecated `workflow_routes.py` as of 2025-10-28

**DevServer Media Awareness:**

DevServer tracks expected output types throughout execution:

```python
# ExecutionContext tracks media generation
class ExecutionContext:
    config_name: str
    execution_mode: str
    expected_media_type: str  # "image", "audio", "music", "video", "text"
    generated_media: List[MediaOutput]  # Collect all media generated
    text_outputs: List[str]  # Track text at each step

@dataclass
class MediaOutput:
    media_type: str  # From Output-Chunk
    prompt_id: str   # ComfyUI queue ID
    output_mapping: dict  # How to extract media
    config_name: str  # Which output config was used
    status: str  # "queued", "generating", "completed", "failed"
```

**Why DevServer Needs Awareness:**
1. **Media Collection** - Track all media in multi-step processes
2. **Presentation Logic** - Format response based on media type
3. **Pipeline Chaining** - Reuse context for additional generations
4. **Error Handling** - Different validation per media type
5. **Frontend Communication** - Tell UI what to expect/display

**Data Flow with Awareness:**
```
1. schema_pipeline_routes.py receives request at /api/schema/pipeline/execute
2. Loads config → reads media_preferences.default_output
3. Executes Interception-Pipeline (text transformation)
4. Auto-Media Detection: checks if media output requested
5. Looks up Output-Config via output_config_defaults.json
6. Loads Output-Config → reads OUTPUT_CHUNK parameter
7. Executes Output-Pipeline with transformed text
8. Loads Output-Chunk → reads media_type field
9. Submits workflow to ComfyUI (or API backend)
10. Returns response with final_output (text) + media_output (prompt_id)
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
├── comfyui_workflow_generator.py  # DEPRECATED - workflows now embedded in chunks
└── prompt_interception_engine.py  # DEPRECATED - replaced by pipeline system
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

**Status:** ⚠️ **DEPRECATED** - Will be removed in future cleanup

**Historical Purpose:** Generated ComfyUI workflows dynamically from Python templates

**Why Deprecated:**
- Output-Chunks now contain complete ComfyUI API workflows embedded in JSON
- No dynamic generation needed - server fills placeholders and submits directly
- Simplifies architecture - workflows are data, not code
- See "Output Chunk" documentation above for new approach

**Migration Path:**
- Extract workflows from `comfyui_workflow_generator.py` templates
- Convert to Output-Chunk JSON format with `input_mappings` and `output_mapping`
- Store in `schemas/chunks/output_*.json`
- Update backend_router to process Output-Chunks instead of calling generator

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
Backend: OpenRouter (cloud) - or configured alternative
Models: claude-3.5-haiku, gemini-2.5-pro, mistral-nemo (cloud)
Cost: ~$0.10-0.18 per 1M tokens
DSGVO: Depends on provider (OpenRouter: non-compliant)

Note: Cloud provider is configured in server.config.py
      Administrator decides which services to use based on DSGVO research
```

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
        # Use cloud service configured in server.config.py
        backend = server_config.LLM_SERVICES["cloud"]["provider"]  # "openrouter"
        model = model_selector.get_cloud_model(task_type)

elif task_category == "MEDIA_GENERATION":
    if execution_mode == "eco":
        backend = "comfyui"
        workflow = get_comfyui_workflow(media_type, config.meta.model)
    elif execution_mode == "fast":
        # Check if remote service is configured for this media type
        remote_service = server_config.REMOTE_SERVICES.get(media_type)

        if remote_service and remote_service["provider"]:
            backend = remote_service["provider"]
            model = remote_service["model"]
        else:
            # Fallback to local if no remote service configured
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
- ❌ **fast mode (OpenRouter):** Non-compliant (data routed through US/UK servers)

**Administrator Responsibilities:**
- Research and select DSGVO-compliant cloud providers for fast mode
- Update `server.config.py` with compliant services
- Potential EU-based alternatives:
  - Mistral AI (direct API, France-based)
  - DeepL (for translation, Germany-based)
  - OpenAI Enterprise (with DSGVO BAA, expensive)
  - Self-hosted Ollama on EU servers (slower than cloud, compliant)

**Implementation Options:**
1. **Default eco mode:** Keep all educational workshops on local processing
2. **Dual configuration:** Separate server.config.py for research vs workshop environments
3. **Config-level override:** Add `meta.force_eco = true` for sensitive workflows

**Current Default:**
- eco mode for all operations
- fast mode available but requires explicit activation + DSGVO review

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
│       └── comfyui_workflow_generator.py      # DEPRECATED (workflows in chunks now)
│
├── my_app/
│   ├── routes/
│   │   ├── schema_pipeline_routes.py          # Main API endpoint (NEW)
│   │   ├── workflow_streaming_routes.py       # SSE streaming endpoints
│   │   ├── export_routes.py                   # Export management
│   │   ├── media_routes.py                    # Media file serving
│   │   └── workflow_routes.py.obsolete        # DEPRECATED (removed 2025-10-28)
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

## Frontend Architecture

### Overview

**Status:** ✅ Complete migration (2025-10-28)
**Architecture:** 100% Backend-abstracted - Frontend NEVER accesses ComfyUI directly

The Frontend implements a clean separation between UI and Backend services, using Backend API exclusively for all operations.

### Core Components

#### 1. Config Browser (`config-browser.js`)

**Purpose:** Card-based visual selection of 37+ configs

```javascript
// Initialization
initConfigBrowser()
  → fetch('/pipeline_configs_metadata')
  → Backend returns: { configs: [...] }
  → Render cards grouped by category
```

**Features:**
- Card-based UI with icon, name, description
- Grouped by category (Bildgenerierung, Textverarbeitung, etc.)
- Visual selection feedback
- Difficulty stars
- Workshop badges

**Data Flow:**
```
User clicks card
  → selectConfig(configId)
  → Store in selectedConfigId
  → Visual feedback (selected class)
```

#### 2. Execution Handler (`execution-handler.js`)

**Purpose:** Backend-abstracted execution + media polling

**Execution Flow:**
```javascript
submitPrompt()
  → Validate: configId + promptText
  → Build payload: { schema, input_text, execution_mode, aspect_ratio }
  → POST /api/schema/pipeline/execute
  → Backend returns: {
      status: "success",
      final_output: "transformed text",
      media_output: {
        output: "prompt_id",
        media_type: "image"
      }
    }
  → Display transformed text
  → Start media polling
```

**Media Polling (NEW Architecture):**
```javascript
pollForMedia(promptId, mediaType)
  → Every 1 second:
    → GET /api/media/info/{promptId}
    → If 404: Continue polling (not ready yet)
    → If 200: Media ready!
      → displayMediaFromBackend(promptId, mediaInfo)
```

**Media Display:**
```javascript
displayImageFromBackend(promptId)
  → Create <img src="/api/media/image/{promptId}">
  → Backend fetches from ComfyUI internally
  → Returns PNG directly
```

#### 3. Application Initialization (`main.js`)

**Purpose:** Bootstrap application with new architecture

```javascript
initializeApp()
  → initSimpleTranslation()
  → loadConfig()
  → initConfigBrowser()  // NEW: Card-based UI
  → setupImageHandlers()
  → initSSEConnection()
```

### API Endpoints Used by Frontend

**Config Selection:**
```
GET /pipeline_configs_metadata
→ Returns: { configs: [{ id, name, description, category, ... }] }
```

**Execution:**
```
POST /api/schema/pipeline/execute
Body: { schema: "dada", input_text: "...", execution_mode: "eco" }
→ Returns: { status, final_output, media_output }
```

**Media Polling:**
```
GET /api/media/info/{prompt_id}
→ If ready: { type: "image", count: 1, files: [...] }
→ If not ready: 404
```

**Media Retrieval:**
```
GET /api/media/image/{prompt_id}
→ Returns: PNG file (binary)

GET /api/media/audio/{prompt_id}
→ Returns: MP3/WAV file (binary)

GET /api/media/video/{prompt_id}
→ Returns: MP4 file (binary) [future]
```

### Benefits of Backend Abstraction

1. **Generator Independence**
   - Frontend doesn't know about ComfyUI
   - Backend can switch to SwarmUI, Replicate, etc. without Frontend changes

2. **Media Type Flexibility**
   - Same polling logic for image, audio, video
   - Media type determined by Config metadata

3. **Clean Error Handling**
   - Backend validates and provides meaningful errors
   - Frontend just displays them

4. **Stateless Frontend**
   - No workflow state management
   - No complex polling logic
   - Simple request/response pattern

### Legacy Components (Obsolete)

These files are marked `.obsolete` and no longer used:

- ❌ `workflow.js.obsolete` - Dropdown-based config selection
- ❌ `workflow-classifier.js.obsolete` - Runtime workflow classification
- ❌ `workflow-browser.js.obsolete` - Incomplete migration attempt
- ❌ `workflow-streaming.js.obsolete` - Legacy API with direct ComfyUI access
- ❌ `dual-input-handler.js.obsolete` - Replaced by execution-handler

### File Structure

```
public_dev/
├── index.html                      # Main UI (no dropdown, only card container)
├── css/
│   ├── workflow-browser.css       # Card-based UI styles
│   └── ...
├── js/
│   ├── main.js                     # Application bootstrap (NEW architecture)
│   ├── config-browser.js           # Card-based config selection (NEW)
│   ├── execution-handler.js        # Backend-abstracted execution (NEW)
│   ├── ui-elements.js              # DOM element references
│   ├── ui-utils.js                 # UI helper functions
│   ├── simple-translation.js       # i18n for static UI
│   ├── image-handler.js            # Image upload handling
│   ├── sse-connection.js           # Real-time queue updates
│   └── *.obsolete                  # Legacy files (deprecated)
```

### Testing Checklist

When testing Frontend changes:

- [ ] Config browser loads 37+ configs
- [ ] Config selection works (visual feedback)
- [ ] Text input + config selection → valid payload
- [ ] POST /api/schema/pipeline/execute succeeds
- [ ] Transformed text displays correctly
- [ ] Media polling via /api/media/info works
- [ ] Image displays via /api/media/image works
- [ ] Audio/music displays correctly (if applicable)
- [ ] Error messages display user-friendly text

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
  - **Status:** NOT IMPLEMENTED (as of 2025-10-28)
  - **Note:** WorkflowClassifier removed - Config metadata will handle validation
  - **See:** DEVELOPMENT_DECISIONS.md (2025-10-28) for Inpainting implementation plan
- [ ] Inpainting support
  - **Note:** Requires image_plus_text_generation pipeline + inpainting config
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
