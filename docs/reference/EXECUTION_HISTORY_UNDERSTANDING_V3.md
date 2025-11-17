# Execution History & Research Data Export - Understanding V3

**Date:** 2025-11-03 Session 17
**Status:** ✅ CORRECT UNDERSTANDING - Based on Legacy System Analysis
**Purpose:** Document what ACTUALLY needs to be tracked for research data export

**Previous Versions:**
- V1: Abandoned (implemented before understanding)
- V2: WRONG - Only focused on Stage 3-4 loop, missed Stage 2 iterations and pedagogical core

---

## 🚨 Critical Misunderstanding in V2

**What V2 Got Wrong:**
- Focused on `output_config_index` for Stage 3-4 loop
- Said: "Stage 2 items (execute once): Interception result"
- Missed: **Stage 2 can have MULTIPLE iterations** (Stille Post = 8 translations!)
- Missed: The pedagogical transformation process IS the research data

**Why This Matters:**
Research data export is about documenting the **pedagogical process**, not just tracking which of 3 images was generated when.

---

## What Legacy System Actually Tracked

### From `/home/joerissen/ai/ai4artsed_webserver_legacy/server/my_app/services/export_manager.py`

```python
# Legacy export structure:
session_data = {
    "user_id": user_id,
    "session_id": session_id,
    "timestamp": timestamp,
    "workflow_name": workflow_name,
    "prompt": prompt_text,
    "translated_prompt": translated_prompt,  # Stage 1 result
    "used_seed": used_seed,                  # For reproducibility
    "safety_level": safety_level,            # Which filter was active
    "outputs": processed_outputs             # Final outputs from ComfyUI nodes
}
```

### What Outputs Contained

```xml
<outputs>
  <output order="1" type="text" node_title="final negative prompt">
    <content>...</content>
  </output>
  <output order="2" type="text" node_title="final positive prompt">
    <content>...</content>
  </output>
  <output order="3" type="image" node_title="Save Image">
    <filename>...</filename>
    <path>...</path>
  </output>
</outputs>
```

**Key Point:** Legacy system captured **ComfyUI node outputs** in execution order, WITH node titles for context.

---

## What Legacy System DIDN'T Track

### Missing Pedagogical Data

1. **Stage 2 Recursive Iterations** (THE CORE PEDAGOGY!)
   - Stille Post: 8 translation iterations
   - Each iteration = one step in the "telephone game"
   - Students need to see: Input → Lang1 → Lang2 → ... → Lang8 → Output
   - **Legacy only saved final result, not the journey**

2. **Stage 1 Intermediate Steps**
   - Translation process
   - Safety check decisions
   - Why something was blocked

3. **Stage 3 Safety Checks**
   - Which outputs were checked
   - What was blocked and why
   - Educational feedback messages

4. **Metadata for Reproducibility**
   - Which models were used (it did actually!)
   - Which backends (Ollama vs OpenRouter)
   - Execution times
   - Temperature/parameters

---

## What DevServer Export Must Track

### Core Principle

**Track the complete pedagogical journey from user input to final output, preserving:**
1. **Order** - Chronological sequence of all events
2. **Type** - What kind of item (translation, transformation, safety check, output)
3. **Context** - Which stage, which iteration, which config
4. **Content** - The actual data (text, image path, metadata such as CFG,Seed, etc.)

### User Quote (Session 17):

> "We have different media types to store: text, image, sound, later: video, potentially others such as 3D-files. These files have a meaningful order at the time of production/inference (translation, security check result, **prompt interception (1, 2, 3, ...),** (Stage3-Check result + media output) (1, 2, 3, ...))"

### What This Means

**"prompt interception (1, 2, 3, ...)"** = Stage 2 iterations
- Stille Post: 8 iterations
- Dada: 1 transformation
- Each needs to be tracked separately

**"(Stage3-Check result + media output) (1, 2, 3, ...)"** = Stage 3-4 loop
- Multiple output configs
- Each has safety check + media generation

---

## Correct Data Model

### ExecutionRecord Structure

```python
@dataclass
class ExecutionRecord:
    """Complete execution history for one pipeline run"""

    # Identity
    execution_id: str           # Unique ID for this execution
    config_name: str           # Which config was used (dada, stillepost, etc.)
    timestamp: datetime        # When execution started

    # User Context
    user_id: str               # For research: group/student ID
    session_id: str            # For grouping multiple executions

    # Execution Metadata
    execution_mode: str        # eco vs fast
    safety_level: str          # kids, youth, off
    used_seed: Optional[int]   # For reproducibility
    total_execution_time: float

    # The Complete History (ordered chronologically)
    items: List[ExecutionItem]
```

### ExecutionItem Structure

```python
@dataclass
class ExecutionItem:
    """Single logged item in execution history"""

    # Identity & Ordering
    sequence_number: int          # Global order (1, 2, 3, ...)
    timestamp: datetime           # When this item was created

    # Stage Context
    stage: int                    # Which stage (1, 2, 3, 4)
    stage_iteration: Optional[int]  # For recursive pipelines (Stille Post iteration 1-8)
    loop_iteration: Optional[int]   # For Stage 3-4 multi-output loop (1, 2, 3, ...)

    # Item Classification
    media_type: MediaType         # text, image, audio, music, video, 3d, metadata
    item_type: ItemType           # Semantic meaning (see taxonomy below)

    # Content
    content: Optional[str] = None          # Text content
    file_path: Optional[str] = None        # Media file path

    # Technical Metadata
    config_used: Optional[str] = None      # Which config generated this
    model_used: Optional[str] = None       # Which model was used
    backend_used: Optional[str] = None     # ollama, comfyui, openrouter
    execution_time: Optional[float] = None # How long this step took

    # Flexible metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Key Design Decisions

1. **`stage_iteration`** - For Stage 2 recursive pipelines
   - Stille Post iteration 1-8
   - Each translation in the chain
   - **This is what V2 completely missed**

2. **`loop_iteration`** - For Stage 3-4 multi-output loop
   - Which output config execution (1, 2, 3)
   - NOT called `output_config_index` because "output" = Stage 4 specifically
   - Used for BOTH Stage 3 (safety check) and Stage 4 (media generation) of same iteration

3. **Both fields are Optional** - Only used when relevant
   - Stage 1: Neither field used
   - Stage 2 (Dada): Neither field used (single execution)
   - Stage 2 (Stille Post): `stage_iteration` = 1-8
   - Stage 3-4: `loop_iteration` = 1, 2, 3, ...

---

## Item Type Taxonomy

### Stage 1 (Translation + §86a Safety)
- `USER_INPUT_TEXT` - Original text from user -> could be 2 or more, depending on pipeline
- `USER_INPUT_IMAGE` - Original image from user -> could be 2 or more, depending on pipeline
- `TRANSLATION_RESULT` - Translated text -> NOT YET IMPLEMENTED: X Texts -> X Translations (keep in server, just make a loop)
- `STAGE1_SAFETY_CHECK` - Safety check result (metadata) -> in case of 1 image: run safety check as image analysis via LLM 
- `STAGE1_BLOCKED` - Content blocked with reason (-> OUTPUT REASON AND DON'T RUN STAGES 2-4)

### Stage 2 (Interception - CAN BE RECURSIVE!)
- `INTERCEPTION_ITERATION` - One iteration of transformation
  - For Dada: Just 1 iteration
  - For Stille Post: 8 iterations (use `stage_iteration` field)
- `INTERCEPTION_FINAL` - Final result after all iterations

### Stage 3 (Pre-Output Safety - PER OUTPUT CONFIG)
- `STAGE3_SAFETY_CHECK` - Safety check for this output config
- `STAGE3_BLOCKED` - This output blocked
- Uses `loop_iteration` to track which output config

### Stage 4 (Output Generation - PER OUTPUT CONFIG)
- `OUTPUT_IMAGE` - Generated image
- `OUTPUT_AUDIO` - Generated audio
- `OUTPUT_MUSIC` - Generated music
- `OUTPUT_VIDEO` - Generated video
- `OUTPUT_3D` - Generated 3D model
- Uses `loop_iteration` to track which output config

### System Events
- `PIPELINE_START` - Pipeline began
- `PIPELINE_COMPLETE` - Pipeline finished
- `PIPELINE_ERROR` - Pipeline failed

---

## Example: Stille Post Execution

```python
ExecutionRecord{
  execution_id: "abc-123",
  config_name: "stillepost",
  execution_mode: "eco",
  safety_level: "kids",

  items: [
    # Stage 1
    {seq: 1, stage: 1, item_type: "user_input_text",
     content: "Eine Blume auf der Wiese"},
    {seq: 2, stage: 1, item_type: "stage1_safety_check",
     metadata: {safe: true}},

    # Stage 2 - 8 ITERATIONS (the pedagogical core!)
    {seq: 3, stage: 2, stage_iteration: 1, item_type: "interception_iteration",
     content: "A flower in the meadow",
     metadata: {from_lang: "de", to_lang: "en"}},
    {seq: 4, stage: 2, stage_iteration: 2, item_type: "interception_iteration",
     content: "草地上的花",
     metadata: {from_lang: "en", to_lang: "zh"}},
    {seq: 5, stage: 2, stage_iteration: 3, item_type: "interception_iteration",
     content: "Une fleur dans le pré",
     metadata: {from_lang: "zh", to_lang: "fr"}},
    # ... iterations 4-7 ...
    {seq: 10, stage: 2, stage_iteration: 8, item_type: "interception_iteration",
     content: "한 그대 꽃",
     metadata: {from_lang: "ar", to_lang: "ko"}},
    {seq: 11, stage: 2, item_type: "interception_final",
     content: "한 그대 꽃"},

    # No Stage 3-4 for text-only output
  ]
}
```

## Example: Dada with Image Comparison

```python
ExecutionRecord{
  execution_id: "def-456",
  config_name: "image_comparison",  # Uses dada transformation + 2 image outputs

  items: [
    # Stage 1
    {seq: 1, stage: 1, item_type: "user_input_text", content: "Eine Blume"},
    {seq: 2, stage: 1, item_type: "translation_result", content: "A flower"},
    {seq: 3, stage: 1, item_type: "stage1_safety_check", metadata: {safe: true}},

    # Stage 2 - Single transformation (Dada)
    {seq: 4, stage: 2, item_type: "interception_final",
     content: "Meadow of Forgotten Timepieces (conceptual art description)"},

    # Stage 3-4 Loop Iteration 1 (sd35_large)
    {seq: 5, stage: 3, loop_iteration: 1, item_type: "stage3_safety_check",
     config_used: "sd35_large", metadata: {safe: true}},
    {seq: 6, stage: 4, loop_iteration: 1, item_type: "output_image",
     config_used: "sd35_large", file_path: "/exports/img1.png"},

    # Stage 3-4 Loop Iteration 2 (gpt5_image)
    {seq: 7, stage: 3, loop_iteration: 2, item_type: "stage3_safety_check",
     config_used: "gpt5_image", metadata: {safe: true}},
    {seq: 8, stage: 4, loop_iteration: 2, item_type: "output_image",
     config_used: "gpt5_image", file_path: "https://cdn.openai.com/..."},
  ]
}
```

---

## Why This is More Complex Than Legacy

### Legacy System (ComfyUI-based):
- ComfyUI workflows had internal nodes
- Export captured node outputs in execution order
- Node titles provided context ("final negative prompt", "Save Image")
- **Limitation:** Only captured ComfyUI outputs, not pipeline internals

### DevServer (4-Stage Architecture):
- 4 distinct stages with different purposes
- Stage 2 can be recursive (8 iterations for Stille Post)
- Stage 3-4 can loop for multiple outputs
- Tracking needed at EVERY stage for pedagogical transparency

**Key Difference:** Legacy tracked ComfyUI's execution graph. DevServer must track the 4-stage pedagogical pipeline.

---

## Frontend Display Capabilities

### Student View (Simple)
```
Show: Only final outputs (Stage 4)
"Image 1"
"Image 2"
```

### Teacher View (Transformation Process)
```
Show: Stage 2 iterations + outputs
"Original: Eine Blume auf der Wiese"
"English: A flower in the meadow"
"Chinese: 草地上的花"
"French: Une fleur dans le pré"
... (show transformation journey)
"Image 1"
```

### Researcher View (Complete Data)
```
Show: Everything
Stage 1:
  - Input: "Eine Blume auf der Wiese"
  - Translation: "A flower in the meadow"
  - Safety: ✓ PASSED

Stage 2 (Stille Post - 8 iterations):
  1. de→en: "A flower in the meadow"
  2. en→zh: "草地上的花"
  3. zh→fr: "Une fleur dans le pré"
  ... (all 8 iterations)

Stage 3-4 (2 outputs):
  Output 1: sd35_large
    - Safety: ✓ PASSED
    - Image: img1.png
  Output 2: gpt5_image
    - Safety: ✓ PASSED
    - Image: https://...
```

---

## Success Criteria

✅ Tracks ALL pedagogical steps (not just final outputs)
✅ Preserves chronological order across all stages
✅ Handles Stage 2 recursive iterations (Stille Post)
✅ Handles Stage 3-4 multi-output loop
✅ Distinguishes between iteration types (stage_iteration vs loop_iteration)
✅ Provides complete context for each item
✅ Enables flexible frontend display by view level
✅ Research can analyze transformation processes
✅ Non-blocking (tracker failure doesn't break pipeline)
✅ Maintains compatibility with legacy export formats (XML, PDF, DOCX)

---

## Implementation Priority

**Phase 1:** Core data structures (ExecutionItem, ExecutionRecord)
**Phase 2:** Stateful tracker (observer pattern, async events)
**Phase 3:** Integration with actual pipeline execution
**Phase 4:** Export API (XML, PDF, DOCX, JSON for research)

**Critical:** Must track Stage 2 iterations during pipeline execution, not just after completion.

---

**Created:** 2025-11-03 Session 17
**Status:** ✅ CORRECT - Based on legacy system analysis + architectural understanding
**Next:** Create implementation plan with correct field names and data model
