# Output-Pipeline Architecture Design
**Date:** 2025-10-26
**Status:** Design finalized, ready for implementation
**Context:** Addressing pipeline inconsistencies and creating backend-transparent media generation

---

## Problem Statement

**Challenge:** How to handle different media types (image, audio, music, video) across different backends (ComfyUI, OpenRouter) with vastly different workflow structures?

**Examples of structural differences:**
- SD3.5 / Flux1: Similar (KSampler → VAEDecode → SaveImage)
- AceStep Music: Different (separate Lyrics+Tags inputs, Music-Generation-Node)
- Stable Audio: Different structure (Audio-Generation-Node, Duration instead of Width/Height)
- QwenImage / OmniGen: Complex (Multi-Input, special Conditioning-Nodes)

**Backend variance:**
- ComfyUI (local): Different workflows per model
- OpenRouter: API calls (completely different structure)
- Future: Additional backends

---

## Design Solution: Input-Type-Based Pipelines

**Core Principle:** Pipelines differentiate by **INPUT STRUCTURE**, not by media type or backend!

### Why Input-Type instead of Media-Type?

**Problem with Media-Type Pipelines:**
```
❌ image_generation pipeline
   - SD3.5: needs 1 text prompt
   - OmniGen: needs 2 text prompts + reference image
   - ControlNet: needs 1 text + 1 control image
   → Can't handle all image generation scenarios!
```

**Solution with Input-Type Pipelines:**
```
✅ single_prompt_generation
   → Can output: Image (SD3.5), Audio (Stable Audio), Music (if single prompt)

✅ dual_prompt_generation
   → Can output: Music (AceStep with Tags+Lyrics)

✅ image_plus_text_generation
   → Can output: Image (Inpainting, img2img, ControlNet)
```

---

## Pipeline Categories

### 1. single_prompt_generation
**Input:** One text prompt
**Output:** Image, Audio, Music, Video (depending on config)

**Data Flow:**
```
Text Prompt → single_prompt_generation Pipeline
  → Backend Router (checks config.backend + config.workflow_template)
  → ComfyUI Workflow OR OpenRouter API
  → Media Output
```

**Used by:**
- SD3.5 Large (image)
- Flux1 (image)
- Stable Audio (audio)
- Future: GPT-5 Image via OpenRouter

---

### 2. dual_prompt_generation
**Input:** Two text prompts (e.g., Tags + Lyrics)
**Output:** Music (AceStep)

**Data Flow:**
```
Prompt 1 (Tags) + Prompt 2 (Lyrics) → dual_prompt_generation Pipeline
  → Backend Router
  → ComfyUI AceStep Workflow
  → Music Output
```

**Config input_mapping:**
```json
{
  "input_mapping": {
    "prompt_1": "tags_node",     // Maps to ComfyUI Node ID for tags
    "prompt_2": "lyrics_node"    // Maps to ComfyUI Node ID for lyrics
  }
}
```

---

### 3. image_plus_text_generation
**Input:** Image + Text prompt
**Output:** Image (modified)

**Examples:**
- Inpainting
- Image-to-Image
- ControlNet
- Style Transfer

**Data Flow:**
```
Input Image + Text Prompt → image_plus_text_generation Pipeline
  → Backend Router
  → ComfyUI Inpainting/img2img Workflow
  → Modified Image Output
```

---

### 4. text_transformation (existing, unchanged)
**Input:** Text
**Output:** Text (optimized/transformed)

**Examples:** All current configs (dada, bauhaus, etc.)

**Data Flow:**
```
User Input → text_transformation Pipeline (simple_manipulation)
  → manipulate Chunk
  → Optimized Text
```

---

## Complete Data Flow Examples

### Example 1: Text → Optimized Text → Image

```
Step 1 (Optional Text Optimization):
  User: "A surreal dream"
  → Config: dada.json (pipeline: simple_manipulation)
  → manipulate Chunk (Dadaism transformation)
  → Output: "Ein surrealistischer Traum in Dadaismus-Ästhetik mit absurden Elementen..."

Step 2 (Media Generation):
  Optimized Text → Config: sd35_standard.json (pipeline: single_prompt_generation)
  → Backend Router → ComfyUI sd35_standard workflow
  → Output: Image (PNG)
```

**Server orchestration:**
```python
# Step 1: Execute text-transformation pipeline
result = executor.execute_pipeline(
    config_name="dada",
    input_text="A surreal dream"
)
optimized_text = result.final_output

# Step 2: Execute output pipeline
image = executor.execute_pipeline(
    config_name="sd35_standard",
    input_text=optimized_text
)
```

---

### Example 2: Direct Text → Image (No optimization)

```
User: "A red apple on a table"
  → Config: sd35_standard.json (pipeline: single_prompt_generation)
  → Backend Router → ComfyUI sd35_standard workflow
  → Output: Image (PNG)
```

---

### Example 3: Two Texts → Music

```
User provides:
  - Tags: "upbeat, electronic, 120bpm"
  - Lyrics: "Dancing through the night..."

  → Config: acestep_standard.json (pipeline: dual_prompt_generation)
  → Backend Router → ComfyUI acestep_music workflow
    → input_mapping: tags → Node 123, lyrics → Node 456
  → Output: Music (WAV)
```

---

### Example 4: Image + Text → Modified Image

```
User uploads: portrait.png
User provides: "Add glasses and a hat"

  → Config: inpainting_sd35.json (pipeline: image_plus_text_generation)
  → Backend Router → ComfyUI inpainting workflow
    → Image → Node 789, Text → Node 101
  → Output: Modified Image (PNG)
```

---

## Config Structure for Output-Pipelines

### Standard Output-Config Template

```json
{
  "name": {
    "en": "SD3.5 Large Standard",
    "de": "SD3.5 Large Standard"
  },
  "description": {
    "en": "Stable Diffusion 3.5 Large with Dual CLIP (clip_g + t5xxl)",
    "de": "Stable Diffusion 3.5 Large mit Dual CLIP (clip_g + t5xxl)"
  },
  "category": {
    "en": "Image Generation",
    "de": "Bildgenerierung"
  },

  "pipeline": "single_prompt_generation",

  "workflow_template": "sd35_standard",

  "parameters": {
    "checkpoint": "sd3.5_large.safetensors",
    "clip_g": "clip_g.safetensors",
    "t5xxl": "t5xxl_enconly.safetensors",
    "steps": 20,
    "cfg": 5.5,
    "sampler": "euler",
    "scheduler": "normal",
    "width": 1024,
    "height": 1024,
    "negative_prompt": "watermark, text, bad quality"
  },

  "meta": {
    "backend": "comfyui",
    "output_type": "image",
    "model_family": "sd3.5",
    "purpose": "output_generation"
  },

  "display": {
    "icon": "🎨",
    "color": "#FF6B6B",
    "category": "media_generation",
    "difficulty": 2,
    "order": 10
  }
}
```

---

### Config with Input Mapping (Dual Prompt)

```json
{
  "name": {
    "en": "AceStep Music Standard",
    "de": "AceStep Musik Standard"
  },

  "pipeline": "dual_prompt_generation",

  "workflow_template": "acestep_music",

  "input_mapping": {
    "prompt_1": "tags_node",
    "prompt_2": "lyrics_node"
  },

  "parameters": {
    "steps": 150,
    "cfg": 7.0,
    "duration": 47.0,
    "negative_prompt": "worst quality, bad audio, high harmonic distortion"
  },

  "meta": {
    "backend": "comfyui",
    "output_type": "music",
    "model_family": "acestep",
    "purpose": "output_generation"
  }
}
```

---

## Backend Router Responsibility

**Backend Router decides:**
1. Which workflow generator to use (ComfyUI / OpenRouter / Ollama)
2. How to format the API request
3. How to map config parameters to workflow nodes

```python
# backend_router.py (pseudo-code)

def route_output_generation(config, inputs):
    backend = config.meta.backend
    workflow_template = config.workflow_template

    if backend == "comfyui":
        return generate_comfyui_output(workflow_template, inputs, config.parameters)

    elif backend == "openrouter":
        return generate_openrouter_output(config.model, inputs, config.parameters)

    elif backend == "ollama":
        return generate_ollama_output(config.model, inputs, config.parameters)
```

---

## ComfyUI Workflow Templates

**Location:** `schemas/engine/comfyui_workflow_generator.py` (current)

**Workflow Templates remain in Python** (not JSON), because:
- ComfyUI workflows are 100+ lines of nested JSON
- Need programmatic placeholder replacement
- Python allows better validation and type checking

**But:** Workflows should be modular and clearly documented

**Template Structure:**
```python
class ComfyUIWorkflowGenerator:
    def _load_templates(self):
        # SD3.5 Standard
        self.templates["sd35_standard"] = WorkflowTemplate(
            name="sd35_standard",
            base_nodes={...},  # Complete ComfyUI node structure
            prompt_injection_node="6",  # Which node receives the text prompt
            parameter_mappings={...}    # How config.parameters map to nodes
        )

        # Flux1 Standard
        self.templates["flux1_standard"] = WorkflowTemplate(...)

        # AceStep Music
        self.templates["acestep_music"] = WorkflowTemplate(...)
```

---

## Pipeline File Structure

### Current Pipelines (Post-Consolidation)

```
schemas/pipelines/
  ├── simple_manipulation.json       → Rename to: text_transformation.json
  ├── audio_generation.json          → Merge into: single_prompt_generation.json
  ├── music_generation.json          → Rename to: dual_prompt_generation.json
  ├── image_generation.json          → Merge into: single_prompt_generation.json
  ├── video_generation.json          → DELETE (dummy only)
  └── simple_interception.json       → DELETE (unused, 0 configs)
```

### New Pipelines (Input-Type Based)

```
schemas/pipelines/
  ├── text_transformation.json             (was: simple_manipulation)
  ├── single_prompt_generation.json        (NEW: merges image + audio + video)
  ├── dual_prompt_generation.json          (was: music_generation, but generalized)
  └── image_plus_text_generation.json      (NEW: for inpainting, img2img)
```

---

## Config Organization

### Directory Structure

```
schemas/configs/
  ├── text_transformation/
  │   ├── dada.json
  │   ├── bauhaus.json
  │   ├── overdrive.json
  │   └── ...
  │
  ├── output_generation/
  │   ├── image/
  │   │   ├── sd35_standard.json
  │   │   ├── flux1_dev.json
  │   │   ├── flux1_schnell.json
  │   │   └── omnigen_standard.json
  │   │
  │   ├── audio/
  │   │   └── stableaudio_standard.json
  │   │
  │   ├── music/
  │   │   └── acestep_standard.json
  │   │
  │   └── video/
  │       └── (future)
```

**Or keep flat structure with meta.purpose:**
```json
{
  "meta": {
    "purpose": "output_generation",  // vs "text_transformation"
    "output_type": "image"
  }
}
```

---

## Implementation Priority

### Phase 1: Core Infrastructure ✅
1. ✅ Consolidate text transformation chunks (manipulate only)
2. ✅ Fix placeholder redundancy
3. ✅ Analyze pipeline structure

### Phase 2: Output-Pipeline Refactoring (NEXT)
1. Create `single_prompt_generation.json` pipeline
2. Create `dual_prompt_generation.json` pipeline
3. Rename `simple_manipulation` → `text_transformation`
4. Delete unused pipelines (simple_interception, video_generation)

### Phase 3: Standard Output-Configs
1. Create `sd35_standard.json` (SD3.5 Large, Dual CLIP, CFG:5.5, Steps:20)
2. Create `flux1_dev.json` (Flux1 Dev, appropriate CLIP, CFG:1.0, Steps:25)
3. Create `flux1_schnell.json` (Flux1 Schnell, fast variant)
4. Create `acestep_standard.json` (AceStep Music with dual prompt)
5. Create `stableaudio_standard.json` (Stable Audio)

### Phase 4: Backend Router Enhancement
1. Implement input-type routing logic
2. Add OpenRouter support for image generation
3. Add Ollama support (if applicable)
4. Error handling and fallbacks

### Phase 5: Testing
1. Test single_prompt_generation with SD3.5
2. Test dual_prompt_generation with AceStep
3. Test text_transformation → single_prompt_generation chain
4. Integration tests with frontend

---

## Decision Points Resolved

### ✅ Pipeline Organization
- **Decision:** Input-Type based (not Media-Type, not Backend-Type)
- **Rationale:** Same input structure = same pipeline, regardless of output medium

### ✅ Workflow Templates Location
- **Decision:** Keep in Python (`comfyui_workflow_generator.py`)
- **Rationale:** Too complex for JSON, need programmatic placeholder replacement

### ✅ Config Structure
- **Decision:** Configs contain `workflow_template` reference + parameters
- **Rationale:** Separation of structure (workflow) and values (parameters)

### ✅ Backend Transparency
- **Decision:** Pipeline doesn't know backend details, Backend Router decides
- **Rationale:** Allows adding new backends without changing pipelines

### ✅ Media Transparency
- **Decision:** Pipeline doesn't enforce output type, Config meta declares it
- **Rationale:** Same pipeline can generate different media types

---

## Open Questions (for future consideration)

1. **Multi-step output pipelines?**
   - Example: Text → Image → Video (img2vid)
   - Current design: Would need separate pipeline calls
   - Future: Could add `multi_step_output_generation` pipeline

2. **Batch processing?**
   - Multiple prompts → Multiple images
   - Not yet designed

3. **Streaming output?**
   - Real-time generation progress
   - Would need ComfyUI websocket integration

---

## Benefits of This Architecture

✅ **Backend Transparency:** Add new backends (OpenRouter, Replicate) without changing pipelines
✅ **Media Transparency:** Same pipeline structure for image/audio/video
✅ **Input Clarity:** Pipeline name tells you what inputs it needs
✅ **Config Flexibility:** Easy to add new models/workflows via config
✅ **Future-Proof:** Can add complex input types (triple_prompt, video_plus_audio) as needed
✅ **Clear Separation:** Text transformation ≠ Media generation
✅ **Backend-Agnostic:** Frontend doesn't need to know ComfyUI vs OpenRouter details

---

**Created:** 2025-10-26
**Status:** Design finalized
**Next:** Implementation Phase 2 (Pipeline refactoring)
**Author:** Claude + Joerissen collaborative design
