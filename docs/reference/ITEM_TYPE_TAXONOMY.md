# Item Type Taxonomy - Execution History Data Classification

**Date Created:** 2025-11-03 (Session 18)
**Purpose:** Define all possible item types for execution history tracking
**Status:** ✅ FINALIZED v1.0 - All design decisions made
**Related:** `EXECUTION_HISTORY_UNDERSTANDING_V3.md`, `EXECUTION_TRACKER_ARCHITECTURE.md` (next)

---

## 🚨 CRITICAL DESIGN CONSTRAINT

**The tracker MUST be non-blocking and fail-safe:**

- ✅ Event logging < 1ms per event (in-memory only)
- ✅ No disk I/O during pipeline execution
- ✅ Tracker failures NEVER stall pipeline
- ✅ Persistence happens AFTER pipeline completes (or async)

**Performance Target:**
- Total tracking overhead: < 100ms for entire execution (all stages)
- Pipeline execution time should be identical ±5% with/without tracking

---

## Overview

This document defines the **complete taxonomy** of item types that can be logged during a 4-stage pipeline execution. Each item type represents a specific event or output in the pedagogical journey.

**Design Principles:**
1. **Semantic Naming** - Item types describe WHAT happened, not HOW
2. **Stage-Specific** - Clear mapping to 4-stage architecture
3. **Extensible** - Easy to add new types without breaking existing code
4. **Self-Documenting** - Name alone should explain meaning

---

## Data Model Context

Each `ExecutionItem` has these fields:

```python
@dataclass
class ExecutionItem:
    sequence_number: int              # Global chronological order (1, 2, 3, ...)
    timestamp: datetime               # When this event occurred

    # Stage Context
    stage: int                        # Which stage (1, 2, 3, 4)
    stage_iteration: Optional[int]    # For Stage 2 recursive (1-8 for Stille Post)
    loop_iteration: Optional[int]     # For Stage 3-4 multi-output (1, 2, 3, ...)

    # Classification
    media_type: MediaType             # text | image | audio | music | video | 3d | metadata
    item_type: ItemType               # Semantic type (defined below)

    # Content
    content: Optional[str] = None          # Text content
    file_path: Optional[str] = None        # Media file path

    # Technical Metadata
    config_used: Optional[str] = None      # Which config generated this
    model_used: Optional[str] = None       # Which model (gpt-oss:20b, sd35_large)
    backend_used: Optional[str] = None     # ollama | comfyui | openrouter
    execution_time: Optional[float] = None # Duration in seconds

    # Flexible metadata (for reproducibility)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Key Principle for `metadata` field:**
> "Everything devserver PASSES to a backend should be recorded (for reproducibility)"

The flexible `Dict[str, Any]` structure allows capturing all backend parameters without type constraints. This is critical for qualitative research where **reproducibility > type safety**.

**Examples:**
- Images: `{width: 1024, height: 1024, seed: 42, cfg_scale: 7.0, steps: 20, sampler: "euler_ancestral"}`
- Music: `{duration_seconds: 30.0, tempo_bpm: 120, key: "C major", genre: "ambient"}` (NO dimensions!)
- Video: `{duration_seconds: 5.0, fps: 24, width: 1280, height: 720, codec: "h264"}`

---

## Stage 1: Translation + §86a Safety

**Purpose:** Pre-process user input before interception

### Item Types

#### `USER_INPUT_TEXT`
- **When:** User submits text input
- **Media Type:** `text`
- **Content:** Original user text
- **Metadata:** `{"input_language": "de", "char_count": 24}`
- **Example:** "Eine Blume auf der Wiese"

#### `USER_INPUT_IMAGE`
- **When:** User uploads image input
- **Media Type:** `image`
- **File Path:** Path to uploaded image
- **Metadata:** `{"image_size": "1024x768", "format": "png", "file_size_kb": 245}`
- **Example:** `/uploads/user_abc123_image1.png`
- **Note:** Multiple inputs possible (e.g., 2 images for comparison)

#### `TRANSLATION_RESULT`
- **When:** Text translated to target language
- **Media Type:** `text`
- **Content:** Translated text
- **Model Used:** `gpt-oss:20b` or `openrouter/claude-3.5-haiku` (fast mode)
- **Metadata:** `{"from_lang": "de", "to_lang": "en", "detected_language": "de"}`
- **Example:** "A flower in the meadow"
- **Note:** NOT YET IMPLEMENTED - Multiple texts → multiple translations (keep in loop)

#### `STAGE1_SAFETY_CHECK`
- **When:** Text safety check completed
- **Media Type:** `metadata`
- **Content:** null
- **Model Used:** `gpt-oss:20b` (§86a StGB check)
- **Metadata:** `{"safe": true, "checked_terms": [], "risk_level": "none"}`
- **Example:** Safe content - no blocked terms

#### `STAGE1_SAFETY_CHECK_IMAGE`
- **When:** Image safety check via LLM analysis
- **Media Type:** `metadata`
- **Content:** Analysis result text
- **Model Used:** `llava:13b` or similar vision model
- **Metadata:** `{"safe": true, "analysis": "Contains flower in nature scene", "confidence": 0.95}`
- **Example:** Image analysis confirms safe content
- **Note:** Future implementation for image inputs

#### `STAGE1_BLOCKED`
- **When:** Content blocked by safety check
- **Media Type:** `metadata`
- **Content:** Block reason + educational explanation
- **Metadata:** `{"blocked_reason": "§86a_violation", "blocked_term": "ISIS", "educational_message": "..."}`
- **Example:** "Dein Prompt wurde blockiert. WARUM DIESE REGEL? ..."
- **Note:** Pipeline STOPS here, Stages 2-4 not executed

---

## Stage 2: Interception (CAN BE RECURSIVE!)

**Purpose:** Pedagogical transformation of prompt (Dada, Stille Post, etc.)

**Critical:** Stage 2 can iterate multiple times (Stille Post = 8 translations!)

### Item Types

#### `INTERCEPTION_ITERATION`
- **When:** One iteration of transformation
- **Media Type:** `text` (most common) or `image` (future: image transformation)
- **Content:** Result of this iteration
- **Stage Iteration:** 1, 2, 3, ... (for Stille Post = 1-8)
- **Config Used:** `stillepost` or pipeline name
- **Model Used:** `gpt-oss:20b` or config-specified model
- **Metadata:**
  - For Stille Post: `{"from_lang": "de", "to_lang": "en", "iteration_type": "translation"}`
  - For Dada: `{"transformation_type": "dada_style", "context_used": "..."}`
- **Examples:**
  - Stille Post iteration 1: "A flower in the meadow" (de→en)
  - Stille Post iteration 2: "草地上的花" (en→zh)
  - Dada iteration 1: "Meadow of Forgotten Timepieces (conceptual art description)"

#### `INTERCEPTION_FINAL`
- **When:** Final result after all iterations
- **Media Type:** `text` (or `image` for future image transformations)
- **Content:** Final transformed prompt
- **Stage Iteration:** null (not iteration-specific, this is the RESULT)
- **Config Used:** `dada`, `stillepost`, `bauhaus`, etc.
- **Metadata:** `{"total_iterations": 8, "transformation_type": "stille_post"}`
- **Examples:**
  - Stille Post final: "한 그대 꽃" (after 8 translations)
  - Dada final: "Meadow of Forgotten Timepieces emerging from industrial decay"

---

## Stage 3: Pre-Output Safety (PER OUTPUT CONFIG)

**Purpose:** Age-appropriate content check before media generation

**Critical:** Runs ONCE per output config (loop_iteration tracks which config)

### Item Types

#### `STAGE3_SAFETY_CHECK`
- **When:** Pre-output safety check completed
- **Media Type:** `metadata`
- **Content:** null (or safety check details as text)
- **Loop Iteration:** 1, 2, 3, ... (which output config)
- **Config Used:** `sd35_large`, `gpt5_image`, etc.
- **Model Used:** `llama-guard3:1b` (currently) → will be `gpt-oss:20b` in future
- **Metadata:** `{"safe": true, "safety_level": "kids", "fast_path": true}`
- **Example:** Fast string-match found no blocked terms → PASS

#### `STAGE3_BLOCKED`
- **When:** Output generation blocked (inappropriate for age group)
- **Media Type:** `metadata`
- **Content:** Block reason + fallback strategy
- **Loop Iteration:** 1, 2, 3, ... (which output config)
- **Config Used:** `sd35_large`, etc.
- **Metadata:**
  ```json
  {
    "blocked_reason": "age_inappropriate",
    "safety_level": "kids",
    "blocked_terms": ["violence"],
    "fallback": "text_alternative_provided"
  }
  ```
- **Example:** "Dieses Bild ist für dein Alter nicht geeignet. [Educational explanation]"
- **Note:** Does NOT abort entire pipeline, just this output config

---

## Stage 4: Output Generation (PER OUTPUT CONFIG)

**Purpose:** Generate final media outputs

**Critical:** Runs ONCE per output config (loop_iteration tracks which config)

### Item Types

#### `OUTPUT_IMAGE`
- **When:** Image generated successfully
- **Media Type:** `image`
- **File Path:** Path or URL to generated image
- **Loop Iteration:** 1, 2, 3, ... (which output config)
- **Config Used:** `sd35_large`, `flux1_dev`, `gpt5_image`, etc.
- **Model Used:** `sd35_large`, `flux1-dev-gguf`, `dall-e-3`, etc.
- **Backend Used:** `comfyui` or `openrouter`
- **Metadata:**
  ```json
  {
    "width": 1024,
    "height": 1024,
    "seed": 42,
    "cfg_scale": 7.0,
    "steps": 20,
    "sampler": "euler_ancestral",
    "format": "png"
  }
  ```
- **Example:** `/exports/abc123_image_001.png`

#### `OUTPUT_AUDIO`
- **When:** Audio generated (speech, sound effects)
- **Media Type:** `audio`
- **File Path:** Path to audio file
- **Loop Iteration:** 1, 2, 3, ...
- **Config Used:** `stable_audio`, `elevenlabs_speech`, etc.
- **Model Used:** `stable-audio-open`, `eleven-labs-v2`, etc.
- **Backend Used:** `comfyui` or `openrouter`
- **Metadata:**
  ```json
  {
    "duration_seconds": 10.5,
    "sample_rate": 44100,
    "channels": 2,
    "format": "wav",
    "file_size_kb": 920
  }
  ```
- **Example:** `/exports/abc123_audio_001.wav`

#### `OUTPUT_MUSIC`
- **When:** Music generated (longer form audio)
- **Media Type:** `music` (specialized audio type)
- **File Path:** Path to music file
- **Loop Iteration:** 1, 2, 3, ...
- **Config Used:** `acestep_music`, etc.
- **Model Used:** `AceStep-v1`, `MusicGen`, etc.
- **Backend Used:** `comfyui`
- **Metadata:**
  ```json
  {
    "duration_seconds": 30.0,
    "genre": "ambient",
    "tempo_bpm": 120,
    "key": "C major",
    "format": "mp3"
  }
  ```
- **Example:** `/exports/abc123_music_001.mp3`

#### `OUTPUT_VIDEO`
- **When:** Video generated
- **Media Type:** `video`
- **File Path:** Path to video file
- **Loop Iteration:** 1, 2, 3, ...
- **Config Used:** `runway_gen3`, `luma_dream_machine`, etc.
- **Model Used:** `runway-gen3`, `luma-dream-machine`, etc.
- **Backend Used:** `openrouter` or `comfyui` (future)
- **Metadata:**
  ```json
  {
    "duration_seconds": 5.0,
    "width": 1280,
    "height": 720,
    "fps": 24,
    "format": "mp4",
    "file_size_mb": 12.5
  }
  ```
- **Example:** `/exports/abc123_video_001.mp4`
- **Note:** Not yet implemented

#### `OUTPUT_3D`
- **When:** 3D model generated
- **Media Type:** `3d`
- **File Path:** Path to 3D model file
- **Loop Iteration:** 1, 2, 3, ...
- **Config Used:** `meshy_3d`, etc.
- **Model Used:** `meshy-3`, etc.
- **Backend Used:** `openrouter` (API-based)
- **Metadata:**
  ```json
  {
    "format": "glb",
    "vertices": 50000,
    "polygons": 100000,
    "file_size_mb": 5.2,
    "texture_included": true
  }
  ```
- **Example:** `/exports/abc123_model_001.glb`
- **Note:** Future implementation


---

## System Events

**Purpose:** Track pipeline lifecycle and errors

### Item Types

#### `PIPELINE_START`
- **When:** Pipeline execution begins
- **Media Type:** `metadata`
- **Stage:** 0 (before Stage 1)
- **Content:** null
- **Metadata:**
  ```json
  {
    "config_name": "dada",
    "execution_mode": "eco",
    "safety_level": "kids",
    "user_id": "user_abc123",
    "session_id": "session_xyz789"
  }
  ```

#### `PIPELINE_COMPLETE`
- **When:** Pipeline execution finished successfully
- **Media Type:** `metadata`
- **Stage:** 5 (after Stage 4)
- **Content:** null
- **Metadata:**
  ```json
  {
    "total_duration_seconds": 45.2,
    "total_items_logged": 15,
    "outputs_generated": 2,
    "stages_completed": [1, 2, 3, 4]
  }
  ```

#### `PIPELINE_ERROR`
- **When:** Pipeline execution failed
- **Media Type:** `metadata`
- **Stage:** Current stage when error occurred
- **Content:** Error message + stack trace
- **Metadata:**
  ```json
  {
    "error_type": "ModelNotAvailableError",
    "error_stage": 2,
    "error_message": "Model gpt-oss:20b not loaded in Ollama",
    "recoverable": false
  }
  ```

#### `STAGE_TRANSITION`
- **When:** Moving from one stage to next
- **Media Type:** `metadata`
- **Content:** null
- **Metadata:**
  ```json
  {
    "from_stage": 1,
    "to_stage": 2,
    "transition_time_ms": 5
  }
  ```
- **Note:** Optional - may be too verbose for most use cases

---

## MediaType Enum

```python
class MediaType(str, Enum):
    TEXT = "text"           # Text content (prompts, translations, transformations)
    IMAGE = "image"         # Generated or uploaded images
    AUDIO = "audio"         # Speech, sound effects
    MUSIC = "music"         # Musical compositions (specialized audio)
    VIDEO = "video"         # Video generations
    THREE_D = "3d"          # 3D models
    METADATA = "metadata"   # System events, safety checks (no content/file)
```

---

## Complete Examples

### Example 1: Stille Post (Text-Only, Recursive Stage 2)

```python
ExecutionRecord{
  execution_id: "exec_abc123",
  config_name: "stillepost",
  execution_mode: "eco",
  safety_level: "kids",

  items: [
    # Stage 0: Pipeline start
    {seq: 1, stage: 0, item_type: "pipeline_start", media_type: "metadata"},

    # Stage 1: Input + Safety
    {seq: 2, stage: 1, item_type: "user_input_text", media_type: "text",
     content: "Eine Blume auf der Wiese"},
    {seq: 3, stage: 1, item_type: "stage1_safety_check", media_type: "metadata",
     metadata: {safe: true}, model_used: "gpt-oss:20b"},

    # Stage 2: 8 ITERATIONS (recursive!)
    {seq: 4, stage: 2, stage_iteration: 1, item_type: "interception_iteration",
     content: "A flower in the meadow", media_type: "text",
     metadata: {from_lang: "de", to_lang: "en"}, model_used: "gpt-oss:20b"},
    {seq: 5, stage: 2, stage_iteration: 2, item_type: "interception_iteration",
     content: "草地上的花", media_type: "text",
     metadata: {from_lang: "en", to_lang: "zh"}},
    {seq: 6, stage: 2, stage_iteration: 3, item_type: "interception_iteration",
     content: "Une fleur dans le pré", media_type: "text",
     metadata: {from_lang: "zh", to_lang: "fr"}},
    # ... iterations 4-7 ...
    {seq: 11, stage: 2, stage_iteration: 8, item_type: "interception_iteration",
     content: "한 그대 꽃", media_type: "text",
     metadata: {from_lang: "ar", to_lang: "ko"}},
    {seq: 12, stage: 2, item_type: "interception_final",
     content: "한 그대 꽃", media_type: "text",
     metadata: {total_iterations: 8}},

    # Stage 3-4: Skipped (text-only output)

    # Stage 5: Pipeline complete
    {seq: 13, stage: 5, item_type: "pipeline_complete", media_type: "metadata",
     metadata: {total_duration_seconds: 8.5}}
  ]
}
```

### Example 2: Dada + Image Comparison (Multi-Output Loop)

```python
ExecutionRecord{
  execution_id: "exec_def456",
  config_name: "image_comparison",  # Uses dada + 2 image outputs
  execution_mode: "eco",
  safety_level: "kids",

  items: [
    # Stage 0: Pipeline start
    {seq: 1, stage: 0, item_type: "pipeline_start"},

    # Stage 1: Input + Translation + Safety
    {seq: 2, stage: 1, item_type: "user_input_text", content: "Eine Blume"},
    {seq: 3, stage: 1, item_type: "translation_result", content: "A flower",
     metadata: {from_lang: "de", to_lang: "en"}},
    {seq: 4, stage: 1, item_type: "stage1_safety_check", metadata: {safe: true}},

    # Stage 2: Single transformation (Dada - not recursive)
    {seq: 5, stage: 2, item_type: "interception_final",
     content: "Meadow of Forgotten Timepieces (conceptual art description)",
     config_used: "dada"},

    # Stage 3-4: Loop Iteration 1 (sd35_large)
    {seq: 6, stage: 3, loop_iteration: 1, item_type: "stage3_safety_check",
     config_used: "sd35_large", metadata: {safe: true}},
    {seq: 7, stage: 4, loop_iteration: 1, item_type: "output_image",
     config_used: "sd35_large", file_path: "/exports/img1.png",
     model_used: "sd35_large", backend_used: "comfyui",
     metadata: {width: 1024, height: 1024, seed: 42}},

    # Stage 3-4: Loop Iteration 2 (gpt5_image)
    {seq: 8, stage: 3, loop_iteration: 2, item_type: "stage3_safety_check",
     config_used: "gpt5_image", metadata: {safe: true}},
    {seq: 9, stage: 4, loop_iteration: 2, item_type: "output_image",
     config_used: "gpt5_image", file_path: "https://cdn.openai.com/...",
     model_used: "dall-e-3", backend_used: "openrouter"},

    # Stage 5: Pipeline complete
    {seq: 10, stage: 5, item_type: "pipeline_complete",
     metadata: {total_duration_seconds: 45.2, outputs_generated: 2}}
  ]
}
```

---

## Future Extensions

### Planned Item Types

#### Stage 1 Extensions
- `USER_INPUT_AUDIO` - Audio input (future: audio-to-text)
- `USER_INPUT_VIDEO` - Video input (future: video analysis)
- `STAGE1_CORRECTION` - Grammar/spelling correction before translation

#### Stage 2 Extensions
- `INTERCEPTION_IMAGE_TRANSFORMATION` - Image-to-image transformation
- `INTERCEPTION_STYLE_TRANSFER` - Style transfer operations
- `INTERCEPTION_NESTED_RECURSION_START` / `_END` - For nested recursive pipelines

#### Stage 4 Extensions
- `OUTPUT_ANIMATION` - Short animations (GIF, animated PNG)
- `OUTPUT_HYBRID` - Combined media (e.g., image + audio narration)

### System Events Extensions
- `BACKEND_SWITCH` - When execution switches backends (e.g., fallback from local to cloud)

---

## Taxonomy Versioning

**Current Version:** 1.0 (2025-11-03)

**Version Strategy:**
- **Major version** (2.0): Breaking changes (renamed item types, removed types)
- **Minor version** (1.1): New item types added (backward compatible)
- **Patch version** (1.0.1): Clarifications, documentation fixes

**Stored in ExecutionRecord:**
```python
@dataclass
class ExecutionRecord:
    taxonomy_version: str = "1.0"  # Which taxonomy version was used
```

**Handling Unknown Types:**
```python
def load_execution_record(record_dict: Dict) -> ExecutionRecord:
    """Load record with graceful handling of unknown item types"""
    taxonomy_version = record_dict.get("taxonomy_version", "1.0")

    for item in record_dict["items"]:
        if item["item_type"] not in KNOWN_ITEM_TYPES_V1:
            logger.warning(f"Unknown item_type: {item['item_type']} (taxonomy v{taxonomy_version})")
            # Still load, just log warning
```

---

## Implementation Notes

### Enum Definition
```python
class ItemType(str, Enum):
    # Stage 1
    USER_INPUT_TEXT = "user_input_text"
    USER_INPUT_IMAGE = "user_input_image"
    TRANSLATION_RESULT = "translation_result"
    STAGE1_SAFETY_CHECK = "stage1_safety_check"
    STAGE1_SAFETY_CHECK_IMAGE = "stage1_safety_check_image"
    STAGE1_BLOCKED = "stage1_blocked"

    # Stage 2
    INTERCEPTION_ITERATION = "interception_iteration"
    INTERCEPTION_FINAL = "interception_final"

    # Stage 3
    STAGE3_SAFETY_CHECK = "stage3_safety_check"
    STAGE3_BLOCKED = "stage3_blocked"

    # Stage 4
    OUTPUT_IMAGE = "output_image"
    OUTPUT_AUDIO = "output_audio"
    OUTPUT_MUSIC = "output_music"
    OUTPUT_VIDEO = "output_video"
    OUTPUT_3D = "output_3d"

    # System
    PIPELINE_START = "pipeline_start"
    PIPELINE_COMPLETE = "pipeline_complete"
    PIPELINE_ERROR = "pipeline_error"
    STAGE_TRANSITION = "stage_transition"
```

### Validation
```python
def validate_item(item: ExecutionItem):
    """Validate item type matches stage constraints"""

    # Stage 1 items must have stage=1
    if item.item_type.startswith("USER_INPUT") or item.item_type.startswith("TRANSLATION"):
        assert item.stage == 1

    # Stage 2 items must have stage=2
    if item.item_type.startswith("INTERCEPTION"):
        assert item.stage == 2

    # Stage 3 items must have loop_iteration
    if item.item_type.startswith("STAGE3"):
        assert item.loop_iteration is not None

    # Stage 4 outputs must have loop_iteration
    if item.item_type.startswith("OUTPUT") and item.item_type != "OUTPUT_TEXT":
        assert item.loop_iteration is not None
```

---

## Success Criteria

✅ **Complete:** All possible events in 4-stage architecture are covered
✅ **Unambiguous:** Each item type has clear, distinct meaning
✅ **Extensible:** Easy to add new types without breaking existing code
✅ **Versioned:** Taxonomy version tracked for future compatibility
✅ **Validated:** Constraints can be enforced programmatically
✅ **Non-Blocking:** Taxonomy design supports < 1ms event logging

---

## Design Decisions (Session 18)

✅ **Q1: Track `STAGE_TRANSITION`?** → YES
- **Reason:** Required for live UI (box-by-box progress display)
- DevServer knows internally what it's doing, but UI needs these events to show "Stage 1 complete → Moving to Stage 2"
- Adds 3-4 items per execution, but essential for educational transparency

✅ **Q2: Track model loading events?** → NO
- **Reason:** Not relevant for pedagogical research
- Out of scope for our qualitative research goals

✅ **Q3: Include `OUTPUT_TEXT` item type?** → NO
- **Reason:** `INTERCEPTION_FINAL` is sufficient for text-only outputs
- No redundancy needed - the final interception result IS the output

✅ **Q4: Flexible or strict metadata?** → FLEXIBLE
- **Reason:** "Everything devserver PASSES to a backend should be recorded (for reproducibility)"
- Different media types have different parameters:
  - Images: width, height, seed, cfg_scale, steps, sampler
  - Music: duration, tempo, key, genre (NO dimensions!)
  - Video: fps, duration, resolution, codec
- **Reproducibility > Type Safety** (qualitative research, not quantitative)
- Flexible `Dict[str, Any]` allows capturing all backend parameters without constraints

✅ **Q5: Cache tracking?** → NO
- **Reason:** Above scope for our research project
- Performance optimization is secondary to pedagogical transparency

---

**Next Steps:**
1. **Review this taxonomy** - Does it cover all cases?
2. **Create EXECUTION_TRACKER_ARCHITECTURE.md** - How to implement this taxonomy
3. **Create STORAGE_STRATEGY.md** - How to persist these items

---

**Created:** 2025-11-03 Session 18
**Status:** ✅ FINALIZED v1.0 - All design decisions made
**Last Updated:** 2025-11-03 Session 18 (decisions finalized)
**Next:** EXECUTION_TRACKER_ARCHITECTURE.md
