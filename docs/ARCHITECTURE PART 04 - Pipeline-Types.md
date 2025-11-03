# DevServer Architecture

**Part 4: Pipeline Types**

---


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
**Pipeline:** `single_text_media_generation`

**Data Flow:**
```
Text Prompt → Config (e.g., sd35_large.json)
  → single_text_media_generation Pipeline
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
**Pipeline:** `dual_text_media_generation`

**Data Flow:**
```
Prompt 1 (Tags) + Prompt 2 (Lyrics) → Config (acestep_standard.json)
  → dual_text_media_generation Pipeline
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
**Pipeline:** `image_text_media_generation`

**Data Flow:**
```
Input Image + Text Prompt → Config (inpainting_sd35.json)
  → image_text_media_generation Pipeline
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

