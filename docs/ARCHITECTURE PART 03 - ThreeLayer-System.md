# DevServer Architecture

**Part 3: Three-Layer System**

---


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
| `single_text_media_generation` | 1 text | Image/Audio/Video | SD3.5, Flux1, Stable Audio (multiple configs) |
| `dual_text_media_generation` | 2 texts | Music | AceStep (Tags + Lyrics) |
| `image_text_media_generation` | Image + Text | Image | Inpainting, img2img, ControlNet (future) |

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
- Pipeline: `single_text_media_generation` or `dual_text_media_generation`
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

